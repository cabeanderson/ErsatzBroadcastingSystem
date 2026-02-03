#!/usr/bin/env python3
# scripts/testing/test_cartoon.py

from datetime import date, datetime
import sys
import os

# Add parent directory to path so we can import scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, test_channel, install_mocks

# Install mocks BEFORE importing channels to avoid ImportError on etv_client
install_mocks()
from scripts.channels import cartoon_network

if __name__ == "__main__":
    print("Testing Cartoon Network Channel")
    print("="*80)
    
    # Test Standard Day (July 15)
    print("\n1. Testing Standard Day (July 15):")
    test_channel(cartoon_network, date(2026, 7, 15))
    
    # Test Halloween (Oct 31) - Should be 100% Halloween
    print("\n2. Testing Halloween (Oct 31):")
    test_channel(cartoon_network, date(2026, 10, 31))
    
    # Test Christmas Ramp (Dec 15) - Should be mixed (~30-60% Christmas)
    print("\n3. Testing Christmas Ramp (Dec 15):")
    test_channel(cartoon_network, date(2026, 12, 15))

    # Test Christmas Day (Dec 25) - Should be 100% Christmas
    print("\n4. Testing Christmas Day (Dec 25):")
    test_channel(cartoon_network, date(2026, 12, 25))
    
    # Test Christmas Hangover (Dec 26) - Should be mixed (~70-80% Christmas)
    print("\n5. Testing Christmas Hangover (Dec 26):")
    test_channel(cartoon_network, date(2026, 12, 26))
