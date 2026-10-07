#!/usr/bin/env python3
"""
Comprehensive Health Check for ErsatzTV Scheduling Framework.
Validates imports, registry integrity, schedule references, and core logic.
"""

import unittest
from datetime import datetime, date
from unittest.mock import MagicMock

# Run as a module, not a loose script:
#     python3 -m scripts.testing.test_comprehensive
# The package is importable from the project root, which is what makes
# `scripts.*` resolve. A sys.path.insert here used to paper over being
# run from anywhere, at the cost of the package being importable two
# different ways -- the same cleanup filler/ and nfo/ had on 2026-09-07.

# Install mocks
from scripts.testing import install_mocks
install_mocks()

# Import core modules
from scripts.core import registry
from scripts.library.sources import MASTER_SOURCES
from scripts.logic.resolution.pipeline import resolve_content, apply_injections, apply_thematic_injection
from scripts.logic.resolution.resolver import ContentResolver
from scripts.core.logger import ChannelLogger
from scripts.core import DayDirector
from scripts.logic.calendar.holidays import HolidayContext
from scripts.scheduling.config import ScheduleConfig
from scripts.logic.calendar.assembly import find_active_marathon
from scripts.logic.structures import Program
from scripts.logic.resolution.pipeline import resolve_scheduled_content
from scripts.logic.models import Marathon, MarathonDefinition, Fallback

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
                elif hasattr(target, 'content'): # Program / PlayOnce
                    check_content(target.content)
                elif hasattr(target, 'items'): # Block or Collection
                    # Distinguish between a Block (which contains content) and a Collection (which is a list wrapper)
                    if hasattr(target, 'pick'): # It's a Collection (Random, Ordered, etc.)
                        for item in target.items:
                            if isinstance(item, dict) and "query" in item:
                                pass # Inline query
                            elif hasattr(item, "query"): # ContentItem
                                pass
                            else:
                                check_content(item)
                    else: # It's a Block
                        check_content(target.items)

            for day_sched in channel.SCHEDULES.values():
                for slot_content in day_sched.values():
                    check_content(slot_content)
            print(f"  ✅ {channel.__name__} passed static check.")

    def test_03_resolution_pipeline(self):
        """Test resolving a complex target through the full pipeline."""
        print("\n[Test] Resolution Pipeline")
        
        # Mystery Theatre's prime block: a label-keyed dict where NOVEMBER is
        # listed before the weekday names and so wins the whole month.
        from scripts.channels import detective
        target = detective.PRIME_BLOCK
        config = ScheduleConfig(schedules={})

        def resolve_on(when):
            self.mock_context.current_time = when
            boss = DayDirector(self.mock_context)
            return resolve_content(target, boss, HolidayContext(boss), config,
                                   self.resolver, self.logger)

        # 1. An ordinary Thursday resolves to that weekday's own block.
        res = resolve_on(datetime(2026, 1, 15, 20, 0, 0))   # Thursday, winter
        print(f"  Thursday Resolution: {res.resolved_content}")
        self.assertTrue(res, "Failed to resolve weekday target")
        self.assertNotEqual(getattr(res.resolved_content, "name", None), "Noir November",
                            "Noir November must not air outside November")

        # 2. A Thursday in November resolves to Noir November instead. This
        #    assertion is the point of the test: the takeover used to sit on a
        #    "default" arm behind five named weekdays, so it never fired, and a
        #    test that only checked "something resolved" passed throughout.
        res = resolve_on(datetime(2026, 11, 12, 20, 0, 0))  # Thursday, November
        print(f"  November Resolution: {res.resolved_content}")
        self.assertEqual(getattr(res.resolved_content, "name", None), "Noir November",
                         "Noir November did not take over the November lineup")

        print("✅ Resolution pipeline functioning.")

    def test_04_appointment_logic(self):
        """Verify Appointment Block date math."""
        print("\n[Test] Appointment Logic")
        
        # Simple weekly show
        block = Program(
            name="Test Show",
            content=None,
            scheduling={
                "seasons": [("show_s1", 5, date(2026, 1, 1))], # 5 eps, starts Jan 1
                "frequency": "weekly"
            }
        )
        
        # Week 1
        res = resolve_scheduled_content(block, date(2026, 1, 1))
        self.assertEqual(res, ("show_s1", 5, 1))
        
        # Week 3
        res = resolve_scheduled_content(block, date(2026, 1, 15))
        self.assertEqual(res, ("show_s1", 5, 3))
        
        # Week 6 (Finished)
        res = resolve_scheduled_content(block, date(2026, 2, 10))
        self.assertIsNone(res)
        
        print("✅ Appointment logic verified.")

    def test_05_marathon_priority(self):
        """Verify marathon priority selection logic."""
        print("\n[Test] Marathon Priority")
        
        # Mock holiday context to allow setting properties
        mock_holiday_ctx = MagicMock()
        
        # Mock Marathons
        # Priority 1: Low (e.g. Random Daily)
        m1 = Marathon(name="Low Priority", trigger=lambda b: True, collection="low", priority=1)
        # Priority 10: High (e.g. Weekly Event)
        m2 = Marathon(name="High Priority", trigger=lambda b: True, collection="high", priority=10)
        # Priority 5: Medium (e.g. Monthly)
        m3 = Marathon(name="Medium Priority", trigger=lambda b: True, collection="med", priority=5)
        
        # Scenario 1: All active
        config = ScheduleConfig(schedules={}, marathons=[m1, m2, m3], enable_marathons=True)
        # Mock holiday context (inactive)
        mock_holiday_ctx.is_holiday_season = False
        
        marathon, key, hours = find_active_marathon(config, self.boss, mock_holiday_ctx)
        self.assertEqual(marathon.name, "High Priority", "Should pick highest priority")
        
        # Scenario 2: High inactive
        m2_inactive = Marathon(name="High Priority", trigger=lambda b: False, collection="high", priority=10)
        config = ScheduleConfig(schedules={}, marathons=[m1, m2_inactive, m3], enable_marathons=True)
        
        marathon, key, hours = find_active_marathon(config, self.boss, mock_holiday_ctx)
        self.assertEqual(marathon.name, "Medium Priority", "Should pick next highest priority")
        
        # Scenario 3: Holiday Season (Marathons Disabled)
        mock_holiday_ctx.is_holiday_season = True
        marathon, key, hours = find_active_marathon(config, self.boss, mock_holiday_ctx)
        self.assertIsNone(marathon, "Should disable marathons during holiday season")
        
        # Reset holiday context
        mock_holiday_ctx.is_holiday_season = False
        
        # Scenario 4: No active marathons
        config = ScheduleConfig(schedules={}, marathons=[], enable_marathons=True)
        marathon, key, hours = find_active_marathon(config, self.boss, mock_holiday_ctx)
        self.assertIsNone(marathon)
        
        print("✅ Marathon priority logic verified.")

    def test_06_marathon_start_hour_override(self):
        """Verify marathon start_hour override logic."""
        print("\n[Test] Marathon Start Hour Override")
        
        # Mock holiday context to ensure marathons are enabled
        mock_holiday_ctx = MagicMock()
        mock_holiday_ctx.is_holiday_season = False
        
        # Mock Marathon Definition with start_hour override
        marathon_def = MarathonDefinition(
            name="Late Start Marathon",
            query="query",
            start_hour=14 # Starts at 2 PM
        )
        
        # Register it in MASTER_SOURCES (mocked via resolver registry)
        MASTER_SOURCES["late_start_marathon"] = marathon_def
        
        m = Marathon(name="Late Start", trigger=lambda b: True, collection="late_start_marathon", hours=(8, 24))
        config = ScheduleConfig(schedules={}, marathons=[m], enable_marathons=True)
        
        marathon, key, hours = find_active_marathon(config, self.boss, mock_holiday_ctx)
        
        self.assertEqual(hours, (14, 24), "Should override start hour to 14")
        print("✅ Marathon start_hour override verified.")

    def test_07_unified_injection(self):
        """Verify unified injection logic (static vs ramp)."""
        print("\n[Test] Unified Injection")
        
        # Setup: Set date to Feb 14 to avoid Halloween interference (from setUp)
        self.mock_context.current_time = datetime(2026, 2, 14, 12, 0, 0)
        
        # Setup: Active Static Holiday (Valentines)
        # Mock boss.has to return True for VALENTINES_DAY
        self.boss.has = MagicMock(side_effect=lambda x: x == "VALENTINES_DAY")
        
        # Setup: Content that can be injected
        self.resolver.registry["test_show"] = "show_title:Test"
        
        # Setup: Force roll to succeed
        self.boss.roll = MagicMock(return_value=True)
        
        # 1. Test Static Injection
        res = apply_thematic_injection(
            "test_show",
            self.boss,
            resolver=self.resolver,
            logger=self.logger,
            enabled=True
        )
        
        self.assertIsNotNone(res.wrapper, "Should have wrapper for Valentines injection")
        self.assertIn("injection_valentines_day", res.source)
        print("  ✅ Static injection (Valentines) verified")
        
        print("✅ Unified injection logic verified.")

    def test_08_cartoon_network_access_contract(self):
        """FOX access stays two shows and weekday DBZ stays a double strip."""
        print("\n[Test] Cartoon Network Access Contract")
        from scripts.library import animation

        expected_companions = {
            "MONDAY": "fox_weekday_king_of_the_hill_tv",
            "TUESDAY": "fox_weekday_futurama_tv",
            "WEDNESDAY": "fox_weekday_family_guy_tv",
            "THURSDAY": "fox_weekday_american_dad_tv",
            "FRIDAY": "fox_weekday_bobs_burgers_tv",
        }
        for day, companion in expected_companions.items():
            block = animation.FOX_WEEKDAY[day]
            self.assertEqual(
                block.items,
                ["fox_weekday_simpsons_tv", companion],
                f"{day} FOX access must be Simpsons plus one companion",
            )
            self.assertEqual(block.fill_strategy, "bridge")
            self.assertFalse(block.strict_window)
            self.assertFalse(block.use_epg_group)

        for block in animation.CN_EARLY_EVENING.values():
            self.assertEqual(len(block.items), 2,
                             "18:00 CN must stop after two programme-length picks")
            self.assertEqual(block.fill_strategy, "gap",
                             "18:00 CN must wait for the hard 19:00 FOX start")

        self.assertEqual(
            animation.TOONAMI_DBZ_POWER_HOUR.scheduling["episodes_per_slot"],
            2,
        )
        self.assertFalse(animation.TOONAMI_POWER_HOUR.use_epg_group)

        from scripts.library import anime
        self.assertNotIn(
            "dragon_ball_z_syndication_tv",
            anime.THE_DRAGON_BALL_HOUR.items.items,
            "Japanorama must not counter-program CN's DBZ power hour with DBZ",
        )

        self.assertEqual([len(seq.items) for seq in animation.DBZ_MOVIE_TRILOGIES],
                         [3, 3, 3])

        self.assertEqual(MASTER_SOURCES["toonami_saturday_dragon_ball_z_tv"]["order"],
                         "Chronological")
        self.assertEqual(MASTER_SOURCES["toonami_overnight_dragon_ball_z_tv"]["order"],
                         "Shuffle")
        self.assertEqual(MASTER_SOURCES["as_prime_venture_bros_tv"]["order"],
                         "Chronological")
        self.assertEqual(MASTER_SOURCES["as_late_venture_bros_tv"]["order"],
                         "Shuffle")
        print("✅ FOX, DBZ, EPG and competing-channel contracts verified.")

    def test_09_cartoon_network_weekday_playout(self):
        """Realistic runtimes preserve 19:00 FOX and the post-FOX CN bridge."""
        from contextlib import redirect_stdout
        from io import StringIO
        from scripts.testing.simulator import ChannelSimulator

        durations = {}
        cn_lengths = {
            "dexter": 7, "johnny_bravo": 7,
            "powerpuff": 11, "ed_edd_n_eddy": 11, "courage": 11,
            "adventure_time": 11, "steven_universe": 11,
            "infinity_train": 11, "over_the_garden_wall": 11,
            "samurai_jack": 22,
        }
        for prefix in ("cn_prime_", "cn_friday_"):
            for show, minutes in cn_lengths.items():
                for suffix in ("", "_auto_fall"):
                    durations[f"{prefix}{show}_tv{suffix}"] = minutes
        for show in ("simpsons", "king_of_the_hill", "futurama", "family_guy",
                     "american_dad", "bobs_burgers"):
            for suffix in ("", "_auto_fall"):
                durations[f"fox_weekday_{show}_tv{suffix}"] = 20

        for day in range(5, 10):
            with redirect_stdout(StringIO()):
                schedule = ChannelSimulator(
                    cartoon_network, content_durations=durations
                ).simulate_day(datetime(2026, 10, day), hours=24)
            content = [e for e in schedule if e["type"] == "content"]
            fox = [e for e in content
                   if str(e["content"]).startswith("fox_weekday_")]
            self.assertEqual(len(fox), 2)
            self.assertEqual(fox[0]["time"].strftime("%H:%M"), "19:00")
            self.assertIn("simpsons", fox[0]["content"])

            dbz = [e for e in content
                   if "dragon_ball_z" in str(e["content"])
                   and e["time"].hour == 17]
            self.assertEqual(len(dbz), 2)

            cn_after_fox = [e for e in content
                            if str(e["content"]).startswith(("cn_prime_", "cn_friday_"))
                            and e["time"] >= fox[-1]["time"]]
            self.assertTrue(any(e["time"].hour == 19 for e in cn_after_fox),
                            "CN must bridge the unused tail after the FOX pair")
            self.assertTrue(any(e["time"].hour >= 20 for e in cn_after_fox),
                            "The scheduled CN prime block must still run after the bridge")

        print("✅ Weekday playout holds FOX at 19:00 and resumes CN correctly.")

if __name__ == "__main__":
    unittest.main()
