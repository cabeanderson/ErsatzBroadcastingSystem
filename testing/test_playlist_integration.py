#!/usr/bin/env python3
"""
Test script for Playlist Integration.
Verifies that the Star Trek playlist is scheduled correctly on Mondays.
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import scifi

if __name__ == "__main__":
    print("Testing Playlist Integration on Sci-Fi Channel")
    print("="*60)
    
    # Monday, July 13, 2026
    test_date = date(2026, 7, 13)
    
    sim = ChannelSimulator(scifi)
    schedule = sim.simulate_day(test_date)
    
    print(f"Schedule for {test_date.strftime('%A, %B %d')}:")
    
    # Filter for Prime Time (20:00 - 23:00)
    prime_items = [e for e in schedule if 20 <= e['time'].hour < 23 and e['type'] == 'content']
    
    found = False
    for item in prime_items:
        print(f"{item['time'].strftime('%H:%M')} | {item['content']}")
        if item['content'] == "star_trek_all_playlist":
            found = True
            
    print("-" * 40)
    if found:
        print("✅ SUCCESS: 'star_trek_all_playlist' found in Prime Time.")
    else:
        print("❌ FAILURE: Playlist not found.")