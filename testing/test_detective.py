#!/usr/bin/env python3
# scripts/testing/test_detective.py

from datetime import date, datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, test_channel, install_mocks

# Install mocks first
install_mocks()
from scripts.channels import detective

if __name__ == "__main__":
    print("Testing Detective Channel")
    print("="*80)
    
    # Test a Weekday (Should be Monk/Psych heavy)
    print("\n1. Testing Weekday (Wednesday):")
    test_channel(detective, date(2026, 7, 15))
    
    # Test a Weekend (Should be British/Classic heavy)
    print("\n2. Testing Weekend (Saturday):")
    test_channel(detective, date(2026, 7, 18))