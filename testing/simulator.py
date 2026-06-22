# scripts/testing/simulator.py
"""
Simulation harness for testing channel schedules without ErsatzTV.
Mocks the API and provides fast testing with time travel capabilities.
"""

from datetime import datetime, timedelta
from uuid import uuid4
from collections import defaultdict
import sys


class MockContext:
    """Simulates ErsatzTV PlayoutContext."""
    
    def __init__(self, start_time):
        self.current_time = start_time
        self.start_time = start_time
        self.finish_time = start_time + timedelta(days=7)  # Week lookahead
        self.is_done = False
    
    def advance(self, minutes=20):
        """Advance time by specified minutes."""
        self.current_time += timedelta(minutes=minutes)
        if self.current_time >= self.finish_time:
            self.is_done = True


class MockAPI:
    """Simulates ErsatzTV API."""
    
    def __init__(self, context):
        self.context = context
        self.schedule = []  # List of (time, content_key, metadata)
        self.registered_searches = {}
        self.content_durations = {}
        self.missing_content = set()
    
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
        """Mock PlayoutCount - logs content and advances time."""
        content_key = playout_count.content
        
        # Simulate missing content (Circuit Breaker / Fallback test)
        if content_key in self.missing_content:
            self.schedule.append({
                'time': self.context.current_time,
                'content': f"MISSING: {content_key}",
                'type': 'error'
            })
            # Do NOT advance time, simulating failure to play
            return self.context
        
        # Record what's playing
        self.schedule.append({
            'time': self.context.current_time,
            'content': content_key,
            'type': 'content'
        })
        
        # Advance time by content duration
        duration = self.content_durations.get(content_key, self._guess_duration(content_key))
        self.context.advance(duration)
        
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
        """Mock skip_to_item."""
        self.schedule.append({
            'time': self.context.current_time,
            'content': f"SKIP_TO: {control_skip.content} S{control_skip.season}E{control_skip.episode}",
            'type': 'skip'
        })
    
    def wait_until(self, build_id, control_wait):
        """Mock wait_until - jumps time."""
        target_time = control_wait.when
        
        # Parse HH:MM format
        hour, minute = map(int, target_time.split(':'))
        
        # Calculate target datetime
        target = self.context.current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If tomorrow flag or time already passed, go to next day
        if control_wait.tomorrow or target <= self.context.current_time:
            target += timedelta(days=1)
        
        # Log the wait
        self.schedule.append({
            'time': self.context.current_time,
            'content': f"WAIT_UNTIL: {target_time}",
            'type': 'meta'
        })

        # Jump to target time
        self.context.current_time = target
        
        return self.context
    
    def pad_until(self, build_id, playout_pad):
        """Mock pad_until - logs filler and jumps time."""
        # Calculate target time similar to wait_until
        target_time = playout_pad.when
        hour, minute = map(int, target_time.split(':'))
        target = self.context.current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if playout_pad.tomorrow or target <= self.context.current_time:
            target += timedelta(days=1)
            
        self.schedule.append({'time': self.context.current_time, 'content': f"PAD_UNTIL: {playout_pad.content} -> {target_time}", 'type': 'content'})
        self.context.current_time = target
        return self.context

    def get_context(self, build_id):
        """Return current context."""
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
        """Mock skip_items."""
        count = getattr(control, 'count', 1)
        self.schedule.append({
            'time': self.context.current_time,
            'content': f"SKIP_ITEMS: {count}",
            'type': 'meta'
        })


class PlayoutCount:
    """Mock PlayoutCount model."""
    def __init__(self, content, count=1):
        self.content = content
        self.count = count


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

class PlayoutPadUntil:
    """Mock PlayoutPadUntil model."""
    def __init__(self, content, when, tomorrow=False):
        self.content = content
        self.when = when
        self.tomorrow = tomorrow

class ControlStartEpgGroup:
    """Mock ControlStartEpgGroup model."""
    def __init__(self, custom_title=None, description=None, advance=True):
        self.custom_title = custom_title
        self.description = description
        self.advance = advance

class ControlSkipItems:
    """Mock ControlSkipItems model."""
    def __init__(self, count=1):
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
        'ContentSearch': ContentSearch,
        'ContentPlaylist': ContentPlaylist,
        'ControlWaitUntil': ControlWaitUntil,
        'ControlSkipToItem': ControlSkipToItem,
        'ControlStartEpgGroup': ControlStartEpgGroup,
        'PlayoutPadUntil': PlayoutPadUntil,
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
