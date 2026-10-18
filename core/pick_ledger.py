# scripts/core/pick_ledger.py
"""
The pick ledger: lets a build that starts mid-day carry on where the last stopped.

ErsatzTV runs a `continue` build from wherever the existing playout ends, which
is almost never midnight, and every build is a fresh process. Everything a
collection remembers about *today* lives in memory -- OrderedCollection's
intraday step, DailyOrderedCollection's index, RandomCollection's unplayed set
and its date-seeded RNG -- so the first pick after a build boundary was the
same as the day's first pick. On the live guide (2026-10-18) that put Ed, Edd n
Eddy at 09:03, 12:21 and 13:07 on one Sunday, and Metalocalypse at 22:06 and
again at 23:18. Every channel was doing it.

The fix keeps the framework's promise -- the same date gives the same
schedule -- by making a resumed build *replay* the earlier part of the day
instead of guessing at it:

- Every collection pick is recorded as (time, collection id).
- A build that starts at T replays, in order, every pick recorded on T's date
  before T. Replaying calls the real `pick()`, so each collection's counter
  and RNG stream land exactly where the earlier process left them.
- Records at or after T are dropped on load: they belong to a playout that a
  reset or a rebuild has since replaced. A reset build starts at 00:00 and so
  replays nothing, which is what makes this self-healing.
- A plain-list block cut off by the boundary resumes its list at the next item
  rather than at the top (see `resume_list_offset`).
- The ledger is written once, when the build finishes. A build that dies --
  timeout, exception -- fails as a whole in ErsatzTV and commits nothing, so
  not writing for it is the consistent outcome.

Picks made while assembling the day (marathon selection) are not recorded:
every process repeats that step at the start of each day, from the same fresh
state, so it reproduces on its own.

Not covered: `DayDirector.pick()`/`pick_weighted()` streams keyed outside a
collection. They are used for one-off choices, not rotations.

Collection ids are the collection's type and content hash, with a `#n` suffix
for the nth instance sharing one (construction order is fixed for a given
channel module). After a deploy that changes a collection, its old records no
longer match any id and are skipped; deploys are followed by a reset anyway.
"""

import json
import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from scripts.settings import LOG_DIR, PICK_LEDGER_ENABLED, PICK_LEDGER_KEEP_DAYS

# Beside the logs: the one directory the framework already writes to.
STATE_DIR = LOG_DIR / "state"

_registry: Dict[str, Any] = {}
_active: Optional["PickLedger"] = None
_enabled: bool = PICK_LEDGER_ENABLED
_state_dir: Any = STATE_DIR


def configure(enabled: bool, state_dir: Any = None) -> None:
    """Switch the ledger on or off for this process (the simulator's default is off)."""
    global _enabled, _state_dir
    _enabled = enabled
    _state_dir = state_dir or STATE_DIR


def register(collection: Any, identity: str) -> str:
    """Give a collection a ledger id, unique within this process."""
    base = f"{type(collection).__name__}:{identity}"
    ledger_id, n = base, 0
    while ledger_id in _registry:
        n += 1
        ledger_id = f"{base}#{n}"
    _registry[ledger_id] = collection
    return ledger_id


def note(ledger_id: str, boss: Any) -> None:
    """Record one collection pick, if a ledger is active and listening."""
    if _active is not None and boss is not None:
        _active.record("c", ledger_id, boss.now)


def note_list_item(block_id: str, invocation_start: datetime, when: datetime) -> None:
    """Record one item played from a plain-list block."""
    if _active is not None:
        _active.record("l", block_id, when, invocation_start.isoformat())


def note_block_entry(block_id: str, when: datetime) -> None:
    """Record that a block started playing."""
    if _active is not None:
        _active.record("b", block_id, when)


def resume_list_offset(block_id: str) -> int:
    """How many list items the interrupted block had already played; 0 if none."""
    if _active is None:
        return 0
    return _active.take_list_offset(block_id)


def replay(boss: Any) -> int:
    """Bring every collection up to where earlier builds left it today."""
    return _active.replay(boss) if _active is not None else 0


@contextmanager
def suspended():
    """Run a step without recording its picks."""
    if _active is None:
        yield
        return
    previous, _active.listening = _active.listening, False
    try:
        yield
    finally:
        _active.listening = previous


def begin(channel: str, start: datetime, logger: Any = None) -> Optional["PickLedger"]:
    """Open the ledger for one build. Returns None when disabled."""
    global _active
    _active = PickLedger(channel, start, logger, _state_dir) if _enabled else None
    if _active is not None:
        _active.load()
    return _active


def finish() -> None:
    """Write the ledger for a build that completed, and close it."""
    global _active
    if _active is not None:
        _active.save()
    _active = None


class PickLedger:
    def __init__(self, channel: str, start: datetime, logger: Any, state_dir: Any):
        self.path = state_dir / f"{channel}.json"
        self.start = start
        self.logger = logger
        self.events: List[list] = []
        self.listening = True
        self._replayed_dates = set()
        self._list_resume: Optional[tuple] = None

    def _warn(self, msg: str) -> None:
        if self.logger is not None:
            self.logger.warn(msg)

    def load(self) -> None:
        try:
            with open(self.path, encoding="utf-8") as f:
                events = json.load(f)
        except FileNotFoundError:
            return
        except (OSError, ValueError) as e:
            self._warn(f"Pick ledger unreadable ({e}); building without it.")
            return
        cutoff = self.start - timedelta(days=PICK_LEDGER_KEEP_DAYS)
        start_iso, cutoff_iso = self.start.isoformat(), cutoff.isoformat()
        # ISO strings from one naive clock sort the same as the times.
        self.events = [e for e in events if cutoff_iso <= e[0] < start_iso]
        self._find_interrupted_list()

    def _find_interrupted_list(self) -> None:
        """If the last block before the boundary was a list, note how far it got."""
        day = self.start.date().isoformat()
        entries = [e for e in self.events if e[1] == "b" and e[0].startswith(day)]
        if not entries:
            return
        _, _, block_id, *_ = entries[-1]
        entered = entries[-1][0]
        played = sum(1 for e in self.events
                     if e[1] == "l" and e[2] == block_id and e[3] == entered)
        if played:
            self._list_resume = (block_id, played)

    def take_list_offset(self, block_id: str) -> int:
        """Hand the offset to the first block after the boundary, if it matches."""
        resume, self._list_resume = self._list_resume, None
        if resume and resume[0] == block_id:
            return resume[1]
        return 0

    def record(self, kind: str, ledger_id: str, when: datetime, extra: Optional[str] = None) -> None:
        if not self.listening:
            return
        event = [when.isoformat(), kind, ledger_id]
        if extra is not None:
            event.append(extra)
        self.events.append(event)

    def replay(self, boss: Any) -> int:
        """Re-run today's earlier picks so every collection resumes in place."""
        day = boss.now.date()
        if day in self._replayed_dates:
            return 0
        self._replayed_dates.add(day)
        prefix = day.isoformat()
        replayed = skipped = 0
        previous, self.listening = self.listening, False
        try:
            for when, kind, ledger_id, *_ in self.events:
                if kind != "c" or not when.startswith(prefix):
                    continue
                collection = _registry.get(ledger_id)
                if collection is None:
                    skipped += 1
                    continue
                collection.pick(boss)
                replayed += 1
        finally:
            self.listening = previous
        if replayed and self.logger is not None:
            self.logger.info(f"Pick ledger: resumed {replayed} picks from earlier today.")
        if skipped:
            self._warn(f"Pick ledger: {skipped} picks name collections that no longer exist.")
        return replayed

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.events, f, separators=(",", ":"))
            os.replace(tmp, self.path)
        except OSError as e:
            self._warn(f"Pick ledger not saved ({e}); the next mid-day build will restart rotations.")
