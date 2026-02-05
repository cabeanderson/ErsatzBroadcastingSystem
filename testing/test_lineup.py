# scripts/testing/test_lineup.py
import sys
import os
import unittest
from datetime import datetime, date
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Install mocks for etv_client to prevent ImportErrors during testing
from scripts.testing import install_mocks
install_mocks()

from scripts.logic.structures import AppointmentLineup, AppointmentSlot, AppointmentBlock
from scripts.logic.resolution import resolve_target
from scripts.core.logger import ChannelLogger

class TestAppointmentLineup(unittest.TestCase):
    def setUp(self):
        self.logger = ChannelLogger(verbose=False)
        self.mock_boss = MagicMock()
        self.mock_boss.now = datetime(2026, 1, 1, 20, 0, 0)
        
        # Mock resolver
        self.mock_resolver = MagicMock()
        self.mock_resolver.resolve.side_effect = lambda x: x # Pass through
        
        # Mock config
        self.mock_config = MagicMock()
        self.mock_config.seasonal_blocks = {}
        self.mock_config.global_holiday_overrides = {}
        self.mock_config.fallback_content = "fallback"
        
        # Mock holiday context
        self.mock_holiday_ctx = MagicMock()
        self.mock_holiday_ctx.is_active.return_value = False
        self.mock_holiday_ctx.envelope = {}

    def test_lineup_is_returned_as_wrapper(self):
        """
        Test that resolve_target correctly identifies an AppointmentLineup
        and returns it as a wrapper for the scheduler to handle.
        """
        anchor_block = AppointmentBlock(seasons=[], loop=False)
        slot1 = AppointmentSlot(anchor=anchor_block, fillers="filler1")
        lineup = AppointmentLineup(slots=[slot1])
        
        # Resolve the lineup object
        result = resolve_target(lineup, self.mock_boss, self.mock_holiday_ctx, self.mock_config, self.mock_resolver, self.logger)
        
        # The resolver should not try to look inside the lineup.
        # It should return the lineup object itself in the 'wrapper' field.
        self.assertIsNone(result.key)
        self.assertIsInstance(result.wrapper, AppointmentLineup)
        self.assertEqual(result.wrapper, lineup)
        self.assertEqual(result.source, "schedule")

if __name__ == '__main__':
    unittest.main()