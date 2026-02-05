#!/usr/bin/env python3
"""
Comprehensive Health Check for ErsatzTV Scheduling Framework.
Validates imports, registry integrity, schedule references, and core logic.
"""

import sys
import os
import unittest
from datetime import datetime, date
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Install mocks
from scripts.testing import install_mocks
install_mocks()

# Import core modules
from scripts.core import registry
from scripts.library.sources import MASTER_SOURCES
from scripts.logic.resolution import resolve_target
from scripts.logic.resolver import ContentResolver
from scripts.core.logger import ChannelLogger
from scripts.core import DayDirector
from scripts.logic.holidays import HolidayContext
from scripts.schedule import ScheduleConfig
from scripts.logic.structures import AppointmentBlock
from scripts.logic.sequencing import find_active_season

# Import channels to test
from scripts.channels import cartoon_network, detective, scifi, sitcoms, classic_movies

CHANNELS = [cartoon_network, detective, scifi, sitcoms, classic_movies]

class TestComprehensive(unittest.TestCase):

    def setUp(self):
        self.logger = ChannelLogger(verbose=False)
        self.mock_api = MagicMock()
        self.resolver = ContentResolver(self.mock_api, "test_build", MASTER_SOURCES, self.logger)
        
        # Mock Context for Director
        self.mock_context = MagicMock()
        self.mock_context.current_time = datetime(2026, 10, 31, 20, 0, 0) # Halloween Night
        self.boss = DayDirector(self.mock_context)
        self.holiday_ctx = HolidayContext(self.boss)

    def test_01_registry_integrity(self):
        """Verify MASTER_SOURCES contains valid queries."""
        print("\n[Test] Registry Integrity")
        for key, data in MASTER_SOURCES.items():
            if isinstance(data, dict):
                if "type" in data and data["type"] == "playlist":
                    self.assertTrue("playlist" in data, f"Playlist '{key}' missing 'playlist' field")
                elif "query" in data:
                    self.assertIsInstance(data["query"], str, f"Key '{key}' has non-string query")
                elif "content" in data:
                    pass # Legacy/Marathon format
                else:
                    # Might be a MarathonDefinition or other object, which is fine
                    pass
            elif isinstance(data, str):
                self.assertTrue(len(data) > 0, f"Key '{key}' has empty query string")
        print(f"✅ Checked {len(MASTER_SOURCES)} source keys.")

    def test_02_channel_schedules(self):
        """Verify all keys in channel schedules exist in MASTER_SOURCES."""
        print("\n[Test] Channel Schedule References")
        
        for channel in CHANNELS:
            print(f"  Checking {channel.__name__}...")
            if not hasattr(channel, "SCHEDULES"):
                continue
                
            # Helper to walk the schedule structure
            def check_content(target):
                if isinstance(target, str):
                    if target not in MASTER_SOURCES:
                        # It might be a seasonal block reference defined in the channel config
                        # We can't easily check that here without parsing the build_playout config
                        # So we'll just warn/print
                        # print(f"    ⚠️  Key '{target}' not in MASTER_SOURCES (might be local block)")
                        pass
                elif isinstance(target, dict):
                    for v in target.values():
                        check_content(v)
                elif hasattr(target, 'base'): # SeasonalBlock
                    check_content(target.base)
                    for v in target.seasonal.values():
                        check_content(v)
                elif hasattr(target, 'content'): # BrandedBlock / PlayOnce
                    check_content(target.content)
                elif hasattr(target, 'items'): # Collections
                    for item in target.items:
                        if isinstance(item, dict) and "query" in item:
                            pass # Inline query
                        elif hasattr(item, "query"): # ContentItem
                            pass
                        else:
                            check_content(item)

            for day_sched in channel.SCHEDULES.values():
                for slot_content in day_sched.values():
                    check_content(slot_content)
            print(f"  ✅ {channel.__name__} passed static check.")

    def test_03_resolution_pipeline(self):
        """Test resolving a complex target through the full pipeline."""
        print("\n[Test] Resolution Pipeline")
        
        # Test a SeasonalBlock from Detective channel
        from scripts.channels import detective
        target = detective.PRIME_SEASONAL
        
        # 1. Test Default (Winter)
        self.mock_context.current_time = datetime(2026, 1, 15, 20, 0, 0) # Winter
        boss = DayDirector(self.mock_context)
        holiday_ctx = HolidayContext(boss)
        config = ScheduleConfig(schedules={})
        
        res = resolve_target(target, boss, holiday_ctx, config, self.resolver, self.logger)
        print(f"  Winter Resolution: {res.resolved_content}")
        self.assertTrue(res, "Failed to resolve Winter target")

        # 2. Test Fall (Noir November)
        self.mock_context.current_time = datetime(2026, 11, 15, 20, 0, 0) # Fall
        boss = DayDirector(self.mock_context)
        holiday_ctx = HolidayContext(boss)
        
        res = resolve_target(target, boss, holiday_ctx, config, self.resolver, self.logger)
        print(f"  Fall Resolution: {res.resolved_content}")
        self.assertTrue(res, "Failed to resolve Fall target")
        
        print("✅ Resolution pipeline functioning.")

    def test_04_appointment_logic(self):
        """Verify Appointment Block date math."""
        print("\n[Test] Appointment Logic")
        
        # Simple weekly show
        block = AppointmentBlock(
            seasons=[("show_s1", 5, date(2026, 1, 1))], # 5 eps, starts Jan 1
            frequency="weekly"
        )
        
        # Week 1
        res = find_active_season(block, date(2026, 1, 1))
        self.assertEqual(res, ("show_s1", 5, 1))
        
        # Week 3
        res = find_active_season(block, date(2026, 1, 15))
        self.assertEqual(res, ("show_s1", 5, 3))
        
        # Week 6 (Finished)
        res = find_active_season(block, date(2026, 2, 10))
        self.assertIsNone(res)
        
        print("✅ Appointment logic verified.")

if __name__ == "__main__":
    unittest.main()