# scripts/testing/test_appointment_loop.py
import sys
import os
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Install mocks for etv_client to prevent ImportErrors during testing
from scripts.testing import install_mocks
install_mocks()

from scripts.logic.structures import AppointmentBlock
from scripts.logic.sequencing import find_active_season

# Mock registry for seasonal ramps
MOCK_SEASONAL_RAMPS = {
    "FALL": {"peak_start": (9, 1)},
    "WINTER": {"peak_start": (12, 1)},
    "SPRING": {"peak_start": (3, 1)},
    "SUMMER": {"peak_start": (6, 1)},
}

class TestAppointmentLoop(unittest.TestCase):
    
    def setUp(self):
        # Patch registry in sequential module
        self.patcher = patch('scripts.engines.sequential.registry')
        self.mock_registry = self.patcher.start()
        self.mock_registry.SEASONAL_RAMPS = MOCK_SEASONAL_RAMPS

    def tearDown(self):
        self.patcher.stop()

    def test_immediate_loop(self):
        """Test loop=True without restart season (immediate restart)."""
        # Show runs for 2 weeks (2 episodes)
        # Start: Jan 1, 2026
        # End: Jan 15, 2026
        block = AppointmentBlock(
            seasons=[("show_s1", 2, date(2026, 1, 1))],
            loop=True,
            loop_restart_season=None
        )
        
        # During run
        self.assertIsNotNone(find_active_season(block, date(2026, 1, 1)))
        self.assertIsNotNone(find_active_season(block, date(2026, 1, 8)))
        
        # Immediately after run (Jan 15) -> Should loop to start
        # Cycle length = 14 days
        # Jan 15 is 14 days after Jan 1. 14 % 14 = 0. Should map to Jan 1.
        result = find_active_season(block, date(2026, 1, 15))
        self.assertIsNotNone(result)
        self.assertEqual(result[2], 1) # Episode 1

    def test_seasonal_loop_wait(self):
        """Test loop=True with loop_restart_season='FALL'."""
        # Show runs for 2 weeks in Spring
        # Start: Mar 1, 2026
        # End: Mar 15, 2026
        # Restart: Sept 1, 2026 (FALL)
        block = AppointmentBlock(
            seasons=[("show_s1", 2, date(2026, 3, 1))],
            loop=True,
            loop_restart_season="FALL"
        )
        
        # During run
        self.assertIsNotNone(find_active_season(block, date(2026, 3, 1)))
        
        # After run, before restart (Summer) -> Should be None (Off-season)
        self.assertIsNone(find_active_season(block, date(2026, 6, 1)))
        
        # At restart (Sept 1) -> Should be Episode 1
        result = find_active_season(block, date(2026, 9, 1))
        self.assertIsNotNone(result)
        self.assertEqual(result[2], 1)

    def test_seasonal_loop_cycle(self):
        """Test multiple cycles of seasonal loop."""
        # Start: Sept 1, 2026
        # Duration: 2 weeks
        # End: Sept 15, 2026
        # Restart: Sept 1, 2027 (Next FALL)
        block = AppointmentBlock(
            seasons=[("show_s1", 2, date(2026, 9, 1))],
            loop=True,
            loop_restart_season="FALL"
        )
        
        # Year 1 (2026) - Active
        self.assertIsNotNone(find_active_season(block, date(2026, 9, 1)))
        
        # Year 1 (2026) - Finished (Oct)
        self.assertIsNone(find_active_season(block, date(2026, 10, 1)))
        
        # Year 2 (2027) - Active again
        result = find_active_season(block, date(2027, 9, 1))
        self.assertIsNotNone(result)
        self.assertEqual(result[2], 1)

if __name__ == '__main__':
    unittest.main()