# scripts/testing/test_refactor.py
import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Install mocks for etv_client to prevent ImportErrors during testing
from scripts.testing import install_mocks
install_mocks()

def test_imports():
    print("--- Testing Imports ---")
    modules = [
        "scripts.core.director",
        "scripts.library.queries",
        "scripts.logic.structures",
        "scripts.logic.resolution.resolver",
        "scripts.logic.resolution.pipeline",
        "scripts.logic.factories",
        "scripts.library.sources",
        "scripts.library.common",
        "scripts.library.detective",
        "scripts.library.scifi",
        "scripts.library.sitcoms",
        "scripts.library.movies",
        "scripts.library.animation",
        "scripts.channels.detective",
        "scripts.channels.scifi",
        "scripts.channels.sitcoms",
        "scripts.channels.cartoon_network",
        "scripts.channels.classic_movies",
        "scripts.settings",
        "scripts.scheduling",
        "scripts.scheduling.config",
        "scripts.scheduling.runner",
        "scripts.scheduling.pre_registration"
    ]
    
    for m in modules:
        try:
            __import__(m)
            print(f"✅ {m}")
        except Exception as e:
            print(f"❌ {m} FAILED: {e}")
            traceback.print_exc()
            return False
    return True

def test_resolution():
    print("\n--- Testing Resolution (Detective) ---")
    try:
        from scripts.channels.detective import SCHEDULES
        from scripts.library.sources import MASTER_SOURCES
        from scripts.logic.resolution.resolver import ContentResolver
        from scripts.core.logger import ChannelLogger
        from scripts.core import DayDirector
        from scripts.logic.calendar.holidays import HolidayContext
        from scripts.scheduling.config import ScheduleConfig
        from scripts.logic.resolution.pipeline import resolve_content
        
        # Mock API
        class MockApi:
            def add_search(self, *args, **kwargs): pass
            def add_playlist(self, *args, **kwargs): pass
            def add_count(self, *args, **kwargs): pass
        
        # Mock Context
        class MockContext:
            def __init__(self):
                from datetime import datetime
                self.current_time = datetime(2026, 10, 20, 20, 0, 0) # Tuesday Evening
                self.is_done = False
        
        logger = ChannelLogger(verbose=True)
        resolver = ContentResolver(MockApi(), "test_build", MASTER_SOURCES, logger)
        
        # Test resolving a specific block from Detective
        print("Resolving Detective Prime Block...")
        target = SCHEDULES["WEEKDAY"]["prime"]
        
        # We need to simulate the schedule loop logic briefly to resolve the target
        boss = DayDirector(MockContext())
        holiday_ctx = HolidayContext(boss)
        config = ScheduleConfig(schedules=SCHEDULES)
        
        # Resolve the prime block (which is a dict in detective.py)
        # "prime": PRIME_BLOCK
        # PRIME_BLOCK is a dict with "TUESDAY": ...
        
        result = resolve_content(target, boss, holiday_ctx, config, resolver, logger)
        print(f"Resolved Result: {result}")
        
        if result.wrapper:
            print(f"Wrapper: {type(result.wrapper)}")
            if hasattr(result.wrapper, 'content'):
                 # Resolve inner content of BrandedBlock
                 inner = resolve_content(result.wrapper.content, boss, holiday_ctx, config, resolver, logger)
                 print(f"Inner Content: {inner.resolved_content}")

        print("✅ Resolution Test Passed")
        return True
        
    except Exception as e:
        print(f"❌ Resolution Test FAILED: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_imports() and test_resolution():
        print("\n🎉 All Tests Passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests Failed!")
        sys.exit(1)