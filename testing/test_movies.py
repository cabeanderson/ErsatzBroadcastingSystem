#!/usr/bin/env python3
# scripts/testing/test_movies.py

from datetime import date, datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, test_channel, install_mocks

# Install mocks first
install_mocks()
from scripts.channels import classic_movies

if __name__ == "__main__":
    print("Testing Classic Movies Channel")
    print("="*80)
    
    # Test Winter (Jan 15) - Should show Winter Classics in Afternoon (feathered) and Golden Age in Prime (Hard Swap)
    print("\n1. Testing Winter Day (Jan 15):")
    schedule = test_channel(classic_movies, date(2026, 1, 15))
    
    # Count winter movies in afternoon (12-18)
    winter_count = 0
    total_count = 0
    for entry in schedule:
        if 12 <= entry['time'].hour < 18 and entry['type'] == 'content':
            total_count += 1
            if "winter" in entry['content']:
                winter_count += 1
    print(f"\nWinter Content Ratio in Afternoon: {winter_count}/{total_count} ({winter_count/total_count:.2%})")
    
    # Test Summer (July 15) - Should show Summer Classics in Afternoon (feathered) and Blockbusters in Prime (Hard Swap)
    print("\n2. Testing Summer Day (July 15):")
    test_channel(classic_movies, date(2026, 7, 15))

    # Test Christmas in July (July 25) - Marathon Trigger
    print("\n3. Testing Christmas in July Marathon (July 25):")
    test_channel(classic_movies, date(2026, 7, 25))

    # Test Halloween (Oct 31) - Holiday Schedule Override
    print("\n4. Testing Halloween (Oct 31):")
    test_channel(classic_movies, date(2026, 10, 31))

    # Test Comparison Feature
    print("\n5. Comparing Winter vs Summer (Jan 15 vs July 15):")
    sim = ChannelSimulator(classic_movies)
    sim.compare_days(date(2026, 1, 15), date(2026, 7, 15))