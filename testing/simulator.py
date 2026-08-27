# scripts/testing/simulator.py
"""
Simulation harness for testing channel schedules without ErsatzTV.
Mocks the API and provides fast testing with time travel capabilities.
"""

from datetime import datetime, timedelta
from uuid import uuid4
from collections import defaultdict
import sys


# ErsatzTV's PlayoutDaysToBuild config element, which defaults to 2:
#   int daysToBuild = await GetDaysToBuild(...);   // IfNoneAsync(2)
#   DateTimeOffset finish = start.AddDays(daysToBuild);
# Simulating a longer window than production actually builds hides overruns,
# so the default here matches ErsatzTV rather than being generous.
DEFAULT_DAYS_TO_BUILD = 2


class MockContext:
    """Simulates ErsatzTV PlayoutContext."""

    def __init__(self, start_time, days_to_build=DEFAULT_DAYS_TO_BUILD):
        self.current_time = start_time
        self.start_time = start_time
        self.finish_time = start_time + timedelta(days=days_to_build)
        self.is_done = False

    def advance(self, minutes=20):
        """Advance time by specified minutes."""
        self.current_time += timedelta(minutes=minutes)
        if self.current_time >= self.finish_time:
            self.is_done = True

    def set_time(self, dt):
        """Move the clock to an absolute time (may move backward on rewind)."""
        self.current_time = dt
        self.is_done = self.current_time >= self.finish_time


class MockAPI:
    """Simulates ErsatzTV API."""
    
    # Number of items a content key is assumed to hold when the test does not
    # say. Used by add_all / peek_next and to wrap the per-key cursor.
    DEFAULT_ITEM_COUNT = 24

    def __init__(self, context, mode="continue"):
        self.context = context
        self.schedule = []  # List of (time, content_key, metadata)
        self.registered_searches = {}
        self.content_durations = {}
        self.missing_content = set()
        # Playout build mode ("reset" or "continue"). wait_until's rewind branch
        # only applies during a reset build.
        self.mode = mode
        # ErsatzTV keeps one enumerator per content key alive for the whole
        # build (SchedulingEngine._enumerators), so the cursor advances across
        # separate calls and skip_* reposition it. Model that here.
        self.cursors = defaultdict(int)
        self.content_counts = {}
        # Every API method is one HTTP round trip against a 30s build timeout
        # (PlayoutScriptedScheduleTimeoutSeconds). Counting them makes the cost
        # of chatty scheduling visible in tests.
        self.call_count = 0

    def _count_call(self):
        self.call_count += 1

    def _item_count(self, content_key):
        return self.content_counts.get(content_key, self.DEFAULT_ITEM_COUNT)

    def _record(self, content, kind='content', **extra):
        entry = {'time': self.context.current_time, 'content': content, 'type': kind}
        entry.update(extra)
        self.schedule.append(entry)
        return entry

    def _play_one(self, content_key):
        """Append a single item from content_key's enumerator and advance time.

        Returns False when the key is missing (time does not advance).
        """
        if content_key in self.missing_content:
            self._record(f"MISSING: {content_key}", kind='error')
            return False

        index = self.cursors[content_key]
        duration = self.content_durations.get(content_key, self._guess_duration(content_key))
        self._record(content_key, item_index=index, duration=duration)
        # Advance this key's enumerator, wrapping like a looping collection.
        self.cursors[content_key] = (index + 1) % max(1, self._item_count(content_key))
        self.context.advance(duration)
        return True

    def _parse_time_of_day(self, when):
        """Resolve an 'HH:MM' string against the current date."""
        hour, minute = map(int, when.split(':'))
        return self.context.current_time.replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )

    def _fill_until(self, content_key, target, label):
        """Add whole items while they fit before target (stop_before_end=True)."""
        if target <= self.context.current_time:
            # Matches AddDurationInternal with a non-positive span: nothing is
            # scheduled, silently.
            self._record(f"{label}: {content_key} -> no-op (target not in future)", kind='meta')
            return self.context

        while self.context.current_time < target and not self.context.is_done:
            duration = self.content_durations.get(content_key, self._guess_duration(content_key))
            if self.context.current_time + timedelta(minutes=duration) > target:
                break
            if not self._play_one(content_key):
                break
        return self.context


    @staticmethod
    def _guess_duration(content_key):
        """Guess duration from content key."""
        if not isinstance(content_key, str):
            return 20
            
        key_lower = content_key.lower()
        
        # Movies
        if 'movie' in key_lower or 'film' in key_lower:
            return 120  # 2 hours
        
        # Hour-long shows
        if 'drama' in key_lower or 'procedural' in key_lower or 'star_trek' in key_lower:
            return 60
        
        # Half-hour shows
        if 'sitcom' in key_lower or 'cartoon' in key_lower or 'tv' in key_lower:
            return 30
        
        # Shorts/filler
        if 'short' in key_lower or 'filler' in key_lower or 'bumper' in key_lower or 'commercial' in key_lower:
            return 5
        
        # Default
        return 20
    
    def add_count(self, build_id, playout_count):
        """Mock PlayoutCount - appends `count` items and advances time.

        Mirrors SchedulingEngine.AddCountInternal, which loops `count` times
        pulling from the key's persistent enumerator. Critically, it applies no
        time bound whatsoever: a large count runs past the build window, and
        bounding is entirely the caller's job.
        """
        self._count_call()
        content_key = playout_count.content
        count = getattr(playout_count, 'count', 1) or 1

        for _ in range(count):
            if not self._play_one(content_key):
                # Missing content never advances time; the real engine logs
                # "Skipping invalid content" once and adds nothing at all.
                break

        return self.context

    def add_all(self, build_id, content_all):
        """Mock ContentAll - appends every item in the collection."""
        self._count_call()
        return self.add_count(
            build_id,
            PlayoutCount(content=content_all.content, count=self._item_count(content_all.content)),
        )

    def add_duration(self, build_id, playout_duration):
        """Mock PlayoutDuration - appends items for a wall-clock duration."""
        self._count_call()
        minutes = _parse_duration_minutes(playout_duration.duration)
        if minutes is None:
            self._record(f"ADD_DURATION: invalid duration {playout_duration.duration!r}", kind='meta')
            return self.context

        target = self.context.current_time + timedelta(minutes=minutes)
        stop_before_end = getattr(playout_duration, 'stop_before_end', True)

        if not stop_before_end:
            # Content is allowed to run over the requested span.
            while self.context.current_time < target and not self.context.is_done:
                if not self._play_one(playout_duration.content):
                    break
            return self.context

        self._fill_until(playout_duration.content, target, "ADD_DURATION")

        fallback = getattr(playout_duration, 'fallback', None)
        if fallback and self.context.current_time < target:
            self._fill_until(fallback, target, "ADD_DURATION_FALLBACK")

        if getattr(playout_duration, 'offline_tail', False):
            self.context.set_time(target)
        return self.context


    def add_search(self, build_id, content_search):
        """Mock search registration."""
        self.registered_searches[content_search.key] = {
            'query': content_search.query,
            'order': content_search.order
        }

    def add_playlist(self, build_id, content_playlist):
        """Mock playlist registration."""
        self.registered_searches[content_playlist.key] = {
            'type': 'playlist',
            'playlist': content_playlist.playlist,
            'group': content_playlist.playlist_group
        }
    
    def skip_to_item(self, build_id, control_skip):
        """Mock skip_to_item - repositions the key's persistent cursor.

        This is a positioning operation, not a per-play modifier: issuing it
        before every single-item add pins the cursor and replays one item
        forever. Position once, then pull.
        """
        self._count_call()
        self.cursors[control_skip.content] = max(0, control_skip.episode - 1)
        self._record(
            f"SKIP_TO: {control_skip.content} S{control_skip.season}E{control_skip.episode}",
            kind='skip',
        )

    def wait_until(self, build_id, control_wait):
        """Mock wait_until - inserts unscheduled time up to a time of day.

        Mirrors SchedulingEngine.WaitUntil. Note there is no "already passed, so
        roll to tomorrow" convenience: when the target has passed and `tomorrow`
        is false, the clock does not move at all (except the reset-mode rewind).
        """
        self._count_call()
        target = self._parse_time_of_day(control_wait.when)
        rewind = getattr(control_wait, 'rewind_on_reset', False)

        if self.context.current_time > target:
            if control_wait.tomorrow:
                target += timedelta(days=1)
            elif rewind and self.mode == "reset":
                pass  # rewind backward to today's target
            else:
                self._record(
                    f"WAIT_UNTIL: {control_wait.when} -> no-op (already passed, tomorrow=False)",
                    kind='meta',
                )
                return self.context

        self._record(f"WAIT_UNTIL: {control_wait.when}", kind='meta')
        self.context.set_time(target)
        return self.context

    def wait_until_exact(self, build_id, control_wait):
        """Mock wait_until_exact - unscheduled time up to an absolute datetime."""
        self._count_call()
        target = control_wait.when
        rewind = getattr(control_wait, 'rewind_on_reset', False)

        if self.context.current_time > target and not (rewind and self.mode == "reset"):
            self._record(f"WAIT_UNTIL_EXACT: {target:%Y-%m-%d %H:%M} -> no-op (already passed)", kind='meta')
            return self.context

        self._record(f"WAIT_UNTIL_EXACT: {target:%Y-%m-%d %H:%M}", kind='meta')
        self.context.set_time(target)
        return self.context

    def pad_until(self, build_id, playout_pad):
        """Mock pad_until - fills with content up to a time of day.

        Mirrors SchedulingEngine.PadUntil: `when` is a time of day only. When
        the clock is already past it and `tomorrow` is false, targetTime is left
        at CurrentTime and NOTHING is scheduled -- silently, with no error. That
        is the documented contract ("no content will be scheduled by this
        request") and the cause of the historical "pad under-filled" reports.
        """
        self._count_call()
        target = self._parse_time_of_day(playout_pad.when)

        if self.context.current_time > target:
            if playout_pad.tomorrow:
                target += timedelta(days=1)
            else:
                self._record(
                    f"PAD_UNTIL: {playout_pad.content} -> no-op "
                    f"(already past {playout_pad.when}, tomorrow=False)",
                    kind='meta',
                )
                return self.context

        return self._fill_until(playout_pad.content, target, "PAD_UNTIL")

    def pad_until_exact(self, build_id, playout_pad):
        """Mock pad_until_exact - fills with content up to an absolute datetime.

        No time-of-day reconstruction, so none of the `tomorrow` or DST
        ambiguity that affects pad_until.
        """
        self._count_call()
        return self._fill_until(playout_pad.content, playout_pad.when, "PAD_UNTIL_EXACT")

    def pad_to_next(self, build_id, playout_pad):
        """Mock pad_to_next - fills to the next N-minute boundary."""
        self._count_call()
        minutes = max(1, getattr(playout_pad, 'minutes', 30))
        now = self.context.current_time
        elapsed = now.hour * 60 + now.minute
        next_boundary = ((elapsed // minutes) + 1) * minutes
        target = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=next_boundary)
        return self._fill_until(playout_pad.content, target, "PAD_TO_NEXT")

    def peek_next(self, build_id, content):
        """Mock peek_next - duration of the next item, without consuming it."""
        self._count_call()
        minutes = self.content_durations.get(content, self._guess_duration(content))
        return PeekItemDuration(content=content, milliseconds=minutes * 60 * 1000)

    def get_context(self, build_id):
        """Return current context."""
        self._count_call()
        return self.context

    def start_epg_group(self, build_id, control_group):
        """Mock start_epg_group."""
        desc = f" - {control_group.description}" if control_group.description else ""
        self.schedule.append({
            'time': self.context.current_time,
            'content': f"EPG_GROUP_START: {control_group.custom_title}{desc}",
            'type': 'meta'
        })

    def stop_epg_group(self, build_id):
        """Mock stop_epg_group."""
        self.schedule.append({
            'time': self.context.current_time,
            'content': "EPG_GROUP_STOP",
            'type': 'meta'
        })

    def skip_items(self, build_id, control):
        """Mock skip_items - advances the key's cursor without scheduling."""
        self._count_call()
        count = getattr(control, 'count', 1)
        content = getattr(control, 'content', None)
        if content:
            self.cursors[content] = (
                self.cursors[content] + count
            ) % max(1, self._item_count(content))
        self._record(f"SKIP_ITEMS: {content} x{count}", kind='meta')


def _parse_duration_minutes(duration):
    """Parse a duration accepted by add_duration into whole minutes.

    Accepts a timedelta, a number of minutes, or an 'HH:MM' / 'HH:MM:SS' string.
    """
    if isinstance(duration, timedelta):
        return duration.total_seconds() / 60
    if isinstance(duration, (int, float)):
        return float(duration)
    if isinstance(duration, str):
        try:
            parts = [float(p) for p in duration.split(':')]
        except ValueError:
            return None
        if len(parts) == 3:
            return parts[0] * 60 + parts[1] + parts[2] / 60
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        if len(parts) == 1:
            return parts[0]
    return None


class PlayoutCount:
    """Mock PlayoutCount model."""
    def __init__(self, content, count=1, filler_kind=None, custom_title=None,
                 disable_watermarks=False):
        self.content = content
        self.count = count
        self.filler_kind = filler_kind
        self.custom_title = custom_title
        self.disable_watermarks = disable_watermarks


class ContentAll:
    """Mock ContentAll model."""
    def __init__(self, content, filler_kind=None, custom_title=None,
                 disable_watermarks=False):
        self.content = content
        self.filler_kind = filler_kind
        self.custom_title = custom_title
        self.disable_watermarks = disable_watermarks


class PlayoutDuration:
    """Mock PlayoutDuration model."""
    def __init__(self, content, duration, fallback=None, trim=False,
                 discard_attempts=0, stop_before_end=True, offline_tail=False,
                 filler_kind=None, custom_title=None, disable_watermarks=False):
        self.content = content
        self.duration = duration
        self.fallback = fallback
        self.trim = trim
        self.discard_attempts = discard_attempts
        self.stop_before_end = stop_before_end
        self.offline_tail = offline_tail
        self.filler_kind = filler_kind
        self.custom_title = custom_title
        self.disable_watermarks = disable_watermarks


class PeekItemDuration:
    """Mock PeekItemDuration model."""
    def __init__(self, content, milliseconds):
        self.content = content
        self.milliseconds = milliseconds


class ContentSearch:
    """Mock ContentSearch model."""
    def __init__(self, key, query, order="Shuffle"):
        self.key = key
        self.query = query
        self.order = order

class ContentPlaylist:
    """Mock ContentPlaylist model."""
    def __init__(self, key, playlist, playlist_group):
        self.key = key
        self.playlist = playlist
        self.playlist_group = playlist_group

class ControlSkipToItem:
    """Mock ControlSkipToItem model."""
    def __init__(self, content, season, episode):
        self.content = content
        self.season = season
        self.episode = episode


class ControlWaitUntil:
    """Mock ControlWaitUntil model."""
    def __init__(self, when, tomorrow=False, rewind_on_reset=False):
        self.when = when
        self.tomorrow = tomorrow
        self.rewind_on_reset = rewind_on_reset

class ControlWaitUntilExact:
    """Mock ControlWaitUntilExact model. `when` is a datetime."""
    def __init__(self, when, rewind_on_reset=False):
        self.when = when
        self.rewind_on_reset = rewind_on_reset


class PlayoutPadUntil:
    """Mock PlayoutPadUntil model."""
    def __init__(self, content, when, tomorrow=False, fallback=None, trim=False,
                 discard_attempts=0, stop_before_end=True, offline_tail=False):
        self.content = content
        self.when = when
        self.tomorrow = tomorrow
        self.fallback = fallback
        self.trim = trim
        self.discard_attempts = discard_attempts
        self.stop_before_end = stop_before_end
        self.offline_tail = offline_tail


class PlayoutPadUntilExact:
    """Mock PlayoutPadUntilExact model. `when` is a datetime."""
    def __init__(self, content, when, fallback=None, trim=False,
                 discard_attempts=0, stop_before_end=True, offline_tail=False):
        self.content = content
        self.when = when
        self.fallback = fallback
        self.trim = trim
        self.discard_attempts = discard_attempts
        self.stop_before_end = stop_before_end
        self.offline_tail = offline_tail


class PlayoutPadToNext:
    """Mock PlayoutPadToNext model."""
    def __init__(self, content, minutes, fallback=None, trim=False,
                 discard_attempts=0, stop_before_end=True, offline_tail=False):
        self.content = content
        self.minutes = minutes
        self.fallback = fallback
        self.trim = trim
        self.discard_attempts = discard_attempts
        self.stop_before_end = stop_before_end
        self.offline_tail = offline_tail

class ControlStartEpgGroup:
    """Mock ControlStartEpgGroup model."""
    def __init__(self, custom_title=None, description=None, advance=True):
        self.custom_title = custom_title
        self.description = description
        self.advance = advance

class ControlSkipItems:
    """Mock ControlSkipItems model."""
    def __init__(self, content=None, count=1):
        self.content = content
        self.count = count


def install_mocks():
    """
    Make a mock ``etv_client.models`` importable for offline simulation/tests.

    Safe to call anywhere, any number of times. It is invoked automatically when
    ``scripts.testing`` is imported, so channel modules (which do
    ``from etv_client.models import ...`` at import time) load on a dev machine
    without the real client and regardless of import order.

    The real client always wins: if ``etv_client`` is installed (e.g. inside the
    ErsatzTV container) this is a no-op, so it can never silently shadow a real
    deployment.
    """
    if 'etv_client.models' in sys.modules:
        return

    # Never shadow a real, installed client (the ErsatzTV scripting runtime).
    try:
        import etv_client.models  # noqa: F401
        return
    except ImportError:
        pass

    ModuleType = type(sys)
    package = sys.modules.get('etv_client') or ModuleType('etv_client')
    models = ModuleType('etv_client.models')
    for name, cls in {
        'PlayoutCount': PlayoutCount,
        'ContentAll': ContentAll,
        'ContentSearch': ContentSearch,
        'ContentPlaylist': ContentPlaylist,
        'ControlWaitUntil': ControlWaitUntil,
        'ControlWaitUntilExact': ControlWaitUntilExact,
        'ControlSkipToItem': ControlSkipToItem,
        'ControlStartEpgGroup': ControlStartEpgGroup,
        'PlayoutDuration': PlayoutDuration,
        'PlayoutPadUntil': PlayoutPadUntil,
        'PlayoutPadUntilExact': PlayoutPadUntilExact,
        'PlayoutPadToNext': PlayoutPadToNext,
        'PeekItemDuration': PeekItemDuration,
        'ControlSkipItems': ControlSkipItems,
    }.items():
        setattr(models, name, cls)

    package.models = models
    sys.modules['etv_client'] = package
    sys.modules['etv_client.models'] = models

class ChannelSimulator:
    """Main simulator for testing channels."""
    
    def __init__(self, channel_module, content_durations=None, missing_content=None):
        """
        Args:
            channel_module: The channel module to test (e.g., cartoon_network)
            content_durations: Optional dict of content_key -> minutes
            missing_content: Optional set of keys to simulate as missing
        """
        self.channel = channel_module
        self.content_durations = content_durations or {}
        self.missing_content = missing_content or set()
    
    def simulate_day(self, start_date, hours=24):
        """
        Simulate a single day of programming.
        
        Args:
            start_date: datetime object for start
            hours: Number of hours to simulate (default 24)
        
        Returns:
            Schedule list
        """
        if isinstance(start_date, datetime):
            start_time = start_date
        else:
            start_time = datetime.combine(start_date, datetime.min.time())
        
        # Create mock context
        context = MockContext(start_time)
        context.finish_time = start_time + timedelta(hours=hours)
        
        # Create mock API
        api = MockAPI(context)
        
        # Set custom durations
        api.content_durations.update(self.content_durations)
        api.missing_content.update(self.missing_content)
        
        # Inject mock models into etv_client
        install_mocks()
        
        # Run channel
        build_id = uuid4()
        
        try:
            self.channel.build_playout(api, context, build_id)
        except Exception as e:
            print(f"ERROR during simulation: {e}")
            import traceback
            traceback.print_exc()
        
        return api.schedule
    
    def simulate_week(self, start_date):
        """Simulate a full week."""
        schedules = {}
        current = start_date if isinstance(start_date, datetime) else datetime.combine(start_date, datetime.min.time())
        
        for day in range(7):
            day_start = current + timedelta(days=day)
            schedules[day_start.strftime('%A, %B %d')] = self.simulate_day(day_start)
        
        return schedules
    
    def print_schedule(self, schedule, show_skips=False, show_context=True):
        """Print a readable schedule."""
        print("\n" + "="*80)
        print("CHANNEL SCHEDULE")
        print("="*80)
        
        current_day = None
        
        for entry in schedule:
            time = entry['time']
            content = entry['content']
            entry_type = entry['type']
            
            # Print day header
            day = time.strftime('%A, %B %d, %Y')
            if day != current_day:
                print(f"\n{'='*80}")
                print(f"{day}")
                
                # Add context info
                if show_context:
                    from scripts.core import DayDirector
                    from scripts.logic.calendar.holidays import HolidayContext
                    
                    mock_ctx = type('obj', (object,), {
                        'current_time': time,
                        'is_done': False
                    })()
                    
                    boss = DayDirector(mock_ctx)
                    holiday_ctx = HolidayContext(boss)
                    
                    print(f"Season: {boss.season_vibe}")
                    if holiday_ctx.active_holidays:
                        print(f"Holidays: {', '.join(holiday_ctx.active_holidays)}")
                
                print(f"{'='*80}")
                current_day = day
            
            # Print entry
            time_str = time.strftime('%H:%M')
            
            if entry_type == 'skip' and show_skips:
                print(f"{time_str} | 🔧 {content}")
            elif entry_type == 'content':
                print(f"{time_str} | 📺 {content}")
            elif entry_type == 'error':
                print(f"{time_str} | ❌ {content}")
            elif entry_type == 'meta':
                print(f"{time_str} | ⚙️  {content}")
        
        print("\n" + "="*80)
    
    def print_week_summary(self, schedules):
        """Print summary of week's programming."""
        print("\n" + "="*80)
        print("WEEK SUMMARY")
        print("="*80)
        
        for day_name, schedule in schedules.items():
            content_count = len([e for e in schedule if e['type'] == 'content'])
            print(f"\n{day_name}: {content_count} items scheduled")
            
            # Show first few items
            for entry in schedule[:5]:
                if entry['type'] == 'content':
                    time_str = entry['time'].strftime('%H:%M')
                    print(f"  {time_str} | {entry['content']}")
            
            if content_count > 5:
                print(f"  ... and {content_count - 5} more")
        
        print("\n" + "="*80)

    def validate_schedule(self, schedule):
        """Check for common scheduling issues."""
        issues = []
        
        # Check for gaps
        for i in range(len(schedule) - 1):
            current_end = schedule[i]['time']
            next_start = schedule[i + 1]['time']
            
            # Skip validation if not content
            if schedule[i]['type'] != 'content':
                continue

            # Get duration
            content_key = schedule[i]['content']
            # We need access to the API instance used to create this schedule to get exact durations,
            # but since we don't have it here, we'll use the guesser again or assume 20.
            # For validation purposes, we'll instantiate a temporary MockAPI just for the guesser logic
            # or better, just replicate the guess logic or assume standard blocks.
            # Actually, let's just use the guesser logic directly since it's stateless.
            duration = MockAPI._guess_duration(content_key)
            
            expected_end = current_end + timedelta(minutes=duration)
            
            gap = (next_start - expected_end).total_seconds() / 60
            
            if gap > 5:  # More than 5 minutes
                issues.append({
                    'type': 'gap',
                    'time': current_end,
                    'duration': gap,
                    'message': f"Gap of {gap:.0f} minutes at {current_end.strftime('%H:%M')}"
                })
            
            if gap < -1:  # Overlap (allow 1 min tolerance)
                issues.append({
                    'type': 'overlap',
                    'time': current_end,
                    'duration': abs(gap),
                    'message': f"Overlap of {abs(gap):.0f} minutes at {current_end.strftime('%H:%M')}"
                })
        
        if not issues:
            print("✅ No scheduling issues found!")
        else:
            print(f"\n⚠️  Found {len(issues)} scheduling issues:")
            for issue in issues:
                print(f"  {issue['message']}")
        
        return issues

    def analyze_schedule(self, schedule):
        """Generate statistics about the schedule."""
        from collections import Counter
        
        content_items = [e['content'] for e in schedule if e['type'] == 'content']
        content_counts = Counter(content_items)
        
        total_items = len(content_items)
        unique_items = len(content_counts)
        
        print("\n" + "="*80)
        print("SCHEDULE STATISTICS")
        print("="*80)
        print(f"Total items scheduled: {total_items}")
        print(f"Unique content keys: {unique_items}")
        if unique_items > 0:
            print(f"Average plays per item: {total_items / unique_items:.1f}")
        
        print("\nTop 10 Most Played:")
        for content, count in content_counts.most_common(10):
            print(f"  {count}x - {content}")
        
        print("="*80)

    def compare_days(self, date1, date2):
        """Compare schedules for two different days."""
        schedule1 = self.simulate_day(date1)
        schedule2 = self.simulate_day(date2)
        
        print("\n" + "="*80)
        print(f"COMPARING {date1.strftime('%A, %B %d')} vs {date2.strftime('%A, %B %d')}")
        print("="*80)
        
        # Find differences
        # This is a simple diff, assumes schedules are roughly aligned
        limit = min(len(schedule1), len(schedule2))
        diff_count = 0
        
        for i in range(limit):
            entry1 = schedule1[i]
            entry2 = schedule2[i]
            
            if entry1['type'] == 'content' and entry2['type'] == 'content':
                if entry1['content'] != entry2['content']:
                    time = entry1['time'].strftime('%H:%M')
                    print(f"{time}:")
                    print(f"  {date1.strftime('%b %d')}: {entry1['content']}")
                    print(f"  {date2.strftime('%b %d')}: {entry2['content']}")
                    print()
                    diff_count += 1
        
        if diff_count == 0:
            print("No content differences found.")
        else:
            print(f"Found {diff_count} differences.")


# Convenience function
def test_channel(channel_module, test_date=None, duration_hours=24):
    """
    Quick test a channel for a specific date.
    
    Args:
        channel_module: Channel to test
        test_date: datetime or date object (default: today)
        duration_hours: Hours to simulate (default: 24)
    
    Example:
        from scripts.testing.simulator import test_channel
        from scripts.channels import cartoon_network
        from datetime import date
        
        # Test Halloween
        test_channel(cartoon_network, date(2026, 10, 31))
    """
    if test_date is None:
        test_date = datetime.now()
    
    sim = ChannelSimulator(channel_module)
    schedule = sim.simulate_day(test_date, hours=duration_hours)
    sim.print_schedule(schedule)
    sim.validate_schedule(schedule)
    sim.analyze_schedule(schedule)
    
    return schedule
