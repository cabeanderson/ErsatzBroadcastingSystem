#!/usr/bin/env python3
"""
Unit tests for data structures and engine helpers.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Install mocks
from scripts.testing import install_mocks
install_mocks()

from scripts.engines.blocks import _play_bumper
from scripts.core.logger import ChannelLogger
from scripts.logic.structures import Program

class TestEngineHelpers(unittest.TestCase):
    
    def setUp(self):
        self.logger = ChannelLogger(verbose=False)
        self.mock_api = MagicMock()
        self.mock_resolver = MagicMock()
        self.mock_boss = MagicMock()
        self.mock_context = MagicMock()
        
        # Setup context
        self.mock_context.current_time = 100
        
        # Setup resolver registry
        self.mock_resolver.registry = {"generic_bumper": "query"}
        self.mock_resolver.resolve.return_value = "resolved_generic_bumper"

    @patch('scripts.engines.blocks.play_smart_bumper')
    @patch('scripts.engines.blocks.play_item')
    @patch('scripts.engines.blocks._get_content_title')
    def test_play_bumper_priority(self, mock_get_title, mock_play_item, mock_play_smart):
        """Test that smart bumpers are prioritized over generic ones."""
        
        # Scenario 1: Smart bumper succeeds
        # ------------------------------------------------
        mock_get_title.return_value = "My Show"
        # play_smart_bumper returns (context, success_bool)
        mock_play_smart.return_value = (self.mock_context, True)
        
        _play_bumper(
            self.mock_api, "build_id", self.mock_context, 
            bumper_key="generic_bumper", 
            content_key="show_key", 
            resolver=self.mock_resolver, 
            logger=self.logger, 
            boss=self.mock_boss
        )
        
        # Verify smart bumper was called
        mock_play_smart.assert_called()
        # Verify generic bumper was NOT resolved or played
        self.mock_resolver.resolve.assert_not_called()
        
        # Scenario 2: Smart bumper fails (returns False)
        # ------------------------------------------------
        mock_play_smart.reset_mock()
        mock_play_smart.return_value = (self.mock_context, False)
        
        _play_bumper(
            self.mock_api, "build_id", self.mock_context, 
            bumper_key="generic_bumper", 
            content_key="show_key", 
            resolver=self.mock_resolver, 
            logger=self.logger, 
            boss=self.mock_boss
        )
        
        # Verify generic bumper WAS resolved and played
        self.mock_resolver.resolve.assert_called_with("generic_bumper", self.mock_boss)
        mock_play_item.assert_called_with(self.mock_api, "build_id", "resolved_generic_bumper", self.logger)

class TestDataStructures(unittest.TestCase):
    def test_program_validation(self):
        """Test Program validation logic."""
        # Valid case
        p = Program(name="Valid", content="foo", fill_strategy="yield")
        self.assertEqual(p.fill_strategy, "yield")

        # Invalid fill_strategy
        with self.assertRaises(ValueError) as cm:
            Program(name="Invalid", content="foo", fill_strategy="invalid_strategy")
        self.assertIn("Invalid fill_strategy", str(cm.exception))

        # fill_strategy="fill" without filler
        with self.assertRaises(ValueError) as cm:
            Program(name="NoFiller", content="foo", fill_strategy="fill")
        self.assertIn("requires 'filler'", str(cm.exception))

        # Missing content AND scheduling
        with self.assertRaises(ValueError) as cm:
            Program(name="Empty", content=None, scheduling=None)
        self.assertIn("Must have either 'content' or 'scheduling'", str(cm.exception))

if __name__ == "__main__":
    unittest.main()