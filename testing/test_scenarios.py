#!/usr/bin/env python3
"""
Scenario-based tests for ErsatzTV Scheduling Framework.
Covers Smoke Tests, Edge Cases, and Feature Toggles.
"""

import sys
import os
import unittest
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Install mocks
from scripts.testing import install_mocks
install_mocks()

from scripts.core import registry
from scripts.logic.resolution.pipeline import resolve_content, apply_injections
from scripts.logic.resolution.resolver import ContentResolver
from scripts.core.logger import ChannelLogger
from scripts.core import DayDirector
from scripts.logic.calendar.holidays import HolidayContext, get_holiday_target
from scripts.scheduling.config import ScheduleConfig
from scripts.logic.structures import Program, Block, DailyOrderedCollection, RandomCollection
from scripts.logic.models import Fallback
from scripts.logic.resolution.config_utils import resolve_feature
from scripts.logic.resolution.playback import hour_in_window, calculate_boundary_dt
from scripts.playout import play_with_fallback
from scripts.logic.calendar import assemble_day_schedule

class TestScenarios(unittest.TestCase):

    def setUp(self):
        self.logger = ChannelLogger(verbose=False)
        self.mock_api = MagicMock()
        self.resolver = ContentResolver(self.mock_api, "test_build", {}, self.logger)
        self.mock_context = MagicMock()
        self.mock_context.current_time = datetime(2026, 1, 1, 12, 0, 0)
        self.boss = DayDirector(self.mock_context)
        self.holiday_ctx = HolidayContext(self.boss)

    # --- SMOKE TESTS ---

    def test_smoke_simple_channel_run(self):
        """Smoke: Simple channel runs without errors (resolution level)."""
        print("\n[Smoke] Simple Channel Resolution")
        schedule = {"prime": "test_content"}
        config = ScheduleConfig(schedules={"WEEKDAY": schedule})
        
        # Simulate assembly
        day_sched = assemble_day_schedule(config, self.boss, self.holiday_ctx)
        
        # Check that content exists (keys are now tuples like (20, 23))
        self.assertIn("test_content", day_sched.values())
        print("✅ Simple schedule assembled")

    def test_smoke_holiday_activation(self):
        """Smoke: Holiday schedules activate."""
        print("\n[Smoke] Holiday Activation")
        # Mock Halloween
        self.holiday_ctx.envelope = {"halloween": 1.0}
        
        target = {
            "default": "regular_content",
            "halloween": "spooky_content"
        }
        
        res = get_holiday_target(self.holiday_ctx, target)
        self.assertEqual(res, "spooky_content")
        print("✅ Holiday target selected")

    # --- EDGE CASES ---

    def test_edge_midnight_crossing(self):
        """Edge: Midnight crossings (23:00 -> 01:00 slots)."""
        print("\n[Edge] Midnight Crossings")
        # Window: 22:00 to 02:00
        start, end = 22, 2
        
        self.assertTrue(hour_in_window(22, start, end), "22:00 should be in window")
        self.assertTrue(hour_in_window(23, start, end), "23:00 should be in window")
        self.assertTrue(hour_in_window(0, start, end), "00:00 should be in window")
        self.assertTrue(hour_in_window(1, start, end), "01:00 should be in window")
        self.assertFalse(hour_in_window(2, start, end), "02:00 should NOT be in window")
        self.assertFalse(hour_in_window(21, start, end), "21:00 should NOT be in window")
        
        # Boundary Calculation
        self.mock_context.current_time = datetime(2026, 1, 1, 23, 0, 0)
        boundary = calculate_boundary_dt(self.mock_context, start, end)
        expected = datetime(2026, 1, 2, 2, 0, 0)
        self.assertEqual(boundary, expected, "Boundary should be tomorrow at 2am")
        print("✅ Midnight logic verified")

    def test_edge_day_boundary_reset(self):
        """Edge: Day boundaries (new day resets DailyOrderedCollection)."""
        print("\n[Edge] Day Boundary Reset")
        collection = DailyOrderedCollection(["item1", "item2", "item3"])
        
        # Day 1
        self.mock_context.current_time = datetime(2026, 1, 1, 10, 0)
        self.assertEqual(collection.pick(self.boss), "item1")
        self.assertEqual(collection.pick(self.boss), "item2")
        
        # Day 2 (Should reset to item1)
        self.mock_context.current_time = datetime(2026, 1, 2, 10, 0)
        self.assertEqual(collection.pick(self.boss), "item1")
        print("✅ Daily collection reset verified")

    def test_edge_empty_collection(self):
        """Edge: Empty collections/blocks."""
        print("\n[Edge] Empty Collection")
        # RandomCollection with empty list
        col = RandomCollection([])
        
        # Should handle empty list gracefully or fail predictably
        try:
            col.pick(self.boss)
            failed = False
        except (IndexError, ValueError):
            failed = True
            
        # Test resolution of None
        res = resolve_content(None, self.boss, self.holiday_ctx, ScheduleConfig(schedules={}), self.resolver, self.logger)
        self.assertIsNone(res.resolved_content)
        print("✅ Empty/None resolution handled")

    def test_edge_multiple_holidays(self):
        """Edge: Multiple simultaneous holidays."""
        print("\n[Edge] Multiple Holidays Priority")
        # Both Halloween and Christmas active
        self.holiday_ctx.envelope = {"halloween": 1.0, "christmas": 1.0}
        
        target = {
            "default": "regular",
            "halloween": "spooky",
            "christmas": "festive"
        }
        
        # Christmas should win based on get_holiday_target implementation
        res = get_holiday_target(self.holiday_ctx, target)
        self.assertEqual(res, "festive")
        print("✅ Priority respected (Christmas > Halloween)")

    def test_edge_fallback_logic(self):
        """Edge: Missing content fallback."""
        print("\n[Edge] Fallback Logic")
        
        # Mock context
        ctx_stalled = MagicMock()
        ctx_stalled.current_time = datetime(2026, 1, 1, 12, 0)
        
        ctx_success = MagicMock()
        ctx_success.current_time = datetime(2026, 1, 1, 12, 30)
        
        with patch('scripts.playout.play_item') as mock_play:
            # Side effect: First call returns stalled, second returns success
            mock_play.side_effect = [ctx_stalled, ctx_success]
            
            fallback = Fallback(primary="primary", secondary="secondary")
            
            # Run
            res_ctx = play_with_fallback(self.mock_api, "build", fallback, self.logger, context=ctx_stalled)
            
            # Verify
            self.assertEqual(mock_play.call_count, 2)
            self.assertEqual(res_ctx.current_time, datetime(2026, 1, 1, 12, 30))
            print("✅ Fallback triggered successfully")

    # --- FEATURE TOGGLES ---

    def test_toggle_hierarchy(self):
        """Feature: Hierarchy (Channel > Block > Program)."""
        print("\n[Feature] Toggle Hierarchy")
        
        # 1. Channel enables, Program disables
        res = resolve_feature(False, None, True)
        self.assertFalse(res)
        
        # 2. Channel enables, Block disables, Program None
        res = resolve_feature(None, False, True)
        self.assertFalse(res)
        
        # 3. Channel disables, Program enables
        res = resolve_feature(True, None, False)
        self.assertTrue(res)
        
        print("✅ Feature flag hierarchy verified")

    def test_toggle_appointment_injection(self):
        """Feature: Appointment TV auto-disables injections."""
        print("\n[Feature] Appointment TV Injection Protection")
        
        # Setup: Active Holiday
        self.holiday_ctx.envelope = {"halloween": 1.0}
        self.boss.roll = MagicMock(return_value=True) # Force injection roll
        
        # Setup: Content
        self.resolver.registry["show_ep1"] = "show_title:Test"
        
        # 1. Regular Program (Should inject)
        prog_regular = Program(name="Regular", content="show_ep1")
        config = ScheduleConfig(schedules={}, enable_holiday_injection=True)
        
        res_reg = apply_injections(
            "show_ep1",
            program=prog_regular,
            config=config,
            resolver=self.resolver,
            boss=self.boss,
            holiday_ctx=self.holiday_ctx,
            logger=self.logger,
            source="test"
        )
        self.assertIsNotNone(res_reg.wrapper, "Regular program should get injection")
        
        # 2. Appointment Program (Should NOT inject)
        prog_appt = Program(
            name="Appointment", 
            content="show_ep1",
            scheduling={"frequency": "weekly"} # Marks as appointment
        )
        
        res_appt = apply_injections(
            "show_ep1",
            program=prog_appt,
            config=config,
            resolver=self.resolver,
            boss=self.boss,
            holiday_ctx=self.holiday_ctx,
            logger=self.logger,
            source="test"
        )
        self.assertIsNone(res_appt.wrapper, "Appointment program should block injection")
        
        # 3. Appointment Program with Explicit Enable (Should inject)
        prog_appt_explicit = Program(
            name="Appointment Explicit", 
            content="show_ep1",
            scheduling={"frequency": "weekly"},
            enable_holiday_injection=True # Override
        )
        
        res_explicit = apply_injections(
            "show_ep1",
            program=prog_appt_explicit,
            config=config,
            resolver=self.resolver,
            boss=self.boss,
            holiday_ctx=self.holiday_ctx,
            logger=self.logger,
            source="test"
        )
        self.assertIsNotNone(res_explicit.wrapper, "Explicit enable should allow injection")
        
        print("✅ Appointment TV injection protection verified")

if __name__ == "__main__":
    unittest.main()
