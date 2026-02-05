#!/usr/bin/env python3
"""
Test script for Sitcoms Channel - Christmas Schedule.
Verifies the refined holiday programming logic.
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import sitcoms

def run_test():
    print("Testing Sitcoms Channel - Christmas Schedule")
    print("="*60)
    
    # Simulate Christmas Day (Peak Holiday)
    test_date = datetime(2026, 12, 25, 6, 0, 0)
    
    sim = ChannelSimulator(sitcoms)
    schedule = sim.simulate_day(test_date)
    
    sim.print_schedule(schedule)
    
    # Verification Logic
    print("\nVerifying Slots:")
    
    def verify_slot(slot_name, start, end, expected_substrings):
        print(f"  Checking {slot_name} ({start:02d}:00-{end:02d}:00)...")
        items = [e for e in schedule if start <= e['time'].hour < end and e['type'] == 'content']
        if not items:
            print(f"    ❌ No content found.")
            return
            
        found = False
        sample = items[0]['content']
        for item in items:
            content = item['content']
            if any(sub in content for sub in expected_substrings):
                found = True
                break
        
        if found:
            print(f"    ✅ Found expected content (e.g. {sample})")
        else:
            print(f"    ❌ Expected one of {expected_substrings}, got {sample}")

    # Midday (10-12): CHRISTMAS_TV_EVENT
    verify_slot("Midday", 10, 12, ["christmas_animated_tv", "christmas_80s_sitcoms_tv", "christmas_90s_sitcoms_tv", "christmas_modern_sitcoms_tv"])
    
    # Afternoon (14-17): CHRISTMAS_AFTERNOON_MOVIES
    verify_slot("Afternoon", 14, 17, ["christmas_80s_movie", "christmas_90s_movie"])
    
    # Prime (20-23): CHRISTMAS_TV_EVENT
    verify_slot("Prime", 20, 23, ["christmas_animated_tv", "christmas_80s_sitcoms_tv", "christmas_90s_sitcoms_tv", "christmas_modern_sitcoms_tv"])
    
    # Night (23-02): christmas_classic_movie
    verify_slot("Night", 23, 24, ["christmas_classic_movie"])

if __name__ == "__main__":
    run_test()