#!/usr/bin/env python3
"""
Test script for Appointment Block Seasonal Restart logic.
Verifies that a show waits for its restart season after finishing a loop.
"""
import sys
import os
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Install mocks
from scripts.testing import install_mocks
install_mocks()

from scripts.logic.structures import Program
from scripts.logic.sequencing import resolve_scheduled_content

# Mock registry for seasonal ramps
MOCK_SEASONAL_RAMPS = {
    "FALL": {"peak_start": (9, 1)},
    "WINTER": {"peak_start": (12, 1)},
    "SPRING": {"peak_start": (3, 1)},
    "SUMMER": {"peak_start": (6, 1)},
}

class TestAppointmentRestart(unittest.TestCase):
    
    def setUp(self):
        # Patch registry in sequencing module
        self.patcher = patch('scripts.logic.sequencing.registry')
        self.mock_registry = self.patcher.start()
        self.mock_registry.SEASONAL_RAMPS = MOCK_SEASONAL_RAMPS

    def tearDown(self):
        self.patcher.stop()

    def test_seasonal_restart_gap(self):
        """Test that a show waits for the restart season after finishing."""
        print("\nTesting Seasonal Restart Gap...")
        
        # Scenario: Show runs for 2 weeks in Spring 2026.
        # It should finish mid-March and NOT restart until Fall 2026.
        block = Program(
            name="Test Show",
            content=None,
            scheduling={
                "seasons": [("show_s1", 2, date(2026, 3, 1))], # 2 episodes = 2 weeks
                "loop": True,
                "loop_restart_season": "FALL" # Restart on Sept 1
            }
        )
        
        # 1. During the run (March 8) -> Active
        active = resolve_scheduled_content(block, date(2026, 3, 8))
        self.assertIsNotNone(active, "Show should be active during run")
        print(f"✅ During run (Mar 8): Active (Ep {active[2]})")

        # 2. After run, before restart (June 1) -> Inactive (Gap)
        inactive = resolve_scheduled_content(block, date(2026, 6, 1))
        self.assertIsNone(inactive, "Show should be inactive during summer gap")
        print(f"✅ During gap (Jun 1): Inactive (Waiting for Fall)")

        # 3. At restart date (Sept 1) -> Active (Loop Restart)
        restart = resolve_scheduled_content(block, date(2026, 9, 1))
        self.assertIsNotNone(restart, "Show should restart in Fall")
        self.assertEqual(restart[2], 1, "Should restart at Episode 1")
        print(f"✅ At restart (Sep 1): Active (Ep {restart[2]})")

    def test_lost_full_run_restart(self):
        """Test a multi-season show (like Lost) restarting S1 after the final season."""
        print("\nTesting Lost Full Run Restart...")
        
        # Scenario: Lost has 2 seasons.
        # S1 starts Fall 2026 (2 eps)
        # S2 starts Fall 2027 (2 eps)
        # Should finish Oct 2027.
        # Should restart S1 in Fall 2028.
        
        block = Program(
            name="Lost",
            content=None,
            scheduling={
                "seasons": [
                    ("lost_s1", 2, date(2026, 9, 1)),
                    ("lost_s2", 2, date(2027, 9, 1))
                ],
                "loop": True,
                "loop_restart_season": "FALL"
            }
        )
        
        # 1. Check end of final season (Sept 15, 2027) -> Active S2
        # S2 starts Sept 1. Ep 1: Sept 1-7. Ep 2: Sept 8-14.
        # Sept 15 is after S2 ends.
        
        # 2. Check gap year (Spring 2028) -> Inactive
        inactive = resolve_scheduled_content(block, date(2028, 3, 1))
        self.assertIsNone(inactive, "Should be inactive in gap year before restart")
        
        # 3. Check restart (Sept 1, 2028) -> Active S1
        restart = resolve_scheduled_content(block, date(2028, 9, 1))
        self.assertIsNotNone(restart, "Should restart S1 in Fall 2028")
        self.assertEqual(restart[0], "lost_s1", "Should be Season 1")
        self.assertEqual(restart[2], 1, "Should be Episode 1")
        print(f"✅ Full run restart (Sep 1, 2028): {restart[0]} Ep {restart[2]}")

if __name__ == "__main__":
    unittest.main()