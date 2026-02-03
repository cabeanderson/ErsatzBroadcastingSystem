#!/usr/bin/env python3
# scripts/testing/test_scifi.py

from datetime import date, datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, test_channel, install_mocks

# Install mocks first
install_mocks()
from scripts.channels import scifi

if __name__ == "__main__":
    print("Testing Sci-Fi Channel")
    print("="*80)
    
    # Test Weekday A (Monday) - Should show Modern Sci-Fi in Midday and Star Trek Playlist in Prime
    print("\n1. Testing Weekday A (Monday, July 13, 2026) [Expect Star Trek Playlist]:")
    test_channel(scifi, date(2026, 7, 13))
    
    # Test Weekday B (Tuesday) - Should show Fantasy in Midday/Prime
    print("\n2. Testing Weekday B (Tuesday, July 14, 2026):")
    test_channel(scifi, date(2026, 7, 14))

    # Test Saturday - Should show Creature Features and Superheroes
    print("\n3. Testing Saturday (July 18, 2026):")
    test_channel(scifi, date(2026, 7, 18))