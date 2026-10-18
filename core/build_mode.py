# scripts/core/build_mode.py
"""
Whether this build is a playout reset.

ErsatzTV runs a channel script with a mode, `reset` or `continue`, and calls
the channel's `reset_playout` hook only for a reset. The mode never reaches
`build_playout`, so a channel's `reset_playout` records it here and the
resolver asks.

It matters for feed start points. ErsatzTV keeps each content key's position
from one build to the next and rewinds every key to its first item on a reset.
A feed with a start point (`playback_order(..., start=(season, episode))`) is
positioned there once, on the reset build, and from then on carries on like any
other feed. Positioning it on a continue build would pin it to that episode.

Keyed by build id, so a process that runs several builds (the simulator) does
not carry one build's reset into the next.
"""

from typing import Any, Set

_RESET_BUILDS: Set[str] = set()


def mark_reset(build_id: Any) -> None:
    """Record that this build is a playout reset. Called from `reset_playout`."""
    _RESET_BUILDS.add(str(build_id))


def is_reset(build_id: Any) -> bool:
    return str(build_id) in _RESET_BUILDS
