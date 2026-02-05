#!/usr/bin/env python3
"""
Test script for Sci-Fi Channel - Appointment TV Verification.
Tests the transition between Active Seasons and Off-Season Fillers.
"""
import sys
import os
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import scifi

def run_test():
    print("Testing Sci-Fi Channel - Appointment TV Logic")
    print("="*60)
    
    # Define realistic durations for the test
    durations = {
        "__auto_lost_s1": 44,
        "__auto_alias_s1": 44,
        "__auto_fringe_s1": 44,
    }
    
    sim = ChannelSimulator(scifi, content_durations=durations)
    
    # Test Dates (Sundays)
    scenarios = [
        ("Fall 2026 (Oct 11)", date(2026, 10, 11), 
         "Lost Active, Alias Filler, Fringe Filler"),
         
        ("Winter 2027 (Jan 10)", date(2027, 1, 10), 
         "Lost Active, Alias Active, Fringe Filler"),
         
        ("Spring 2027 (May 16)", date(2027, 5, 16), 
         "Lost Filler, Alias Active, Fringe Active")
    ]
    
    for name, test_date, expected in scenarios:
        print(f"\n--- {name} ---")
        print(f"Expectation: {expected}")
        
        # Ensure it's a Sunday
        if test_date.weekday() != 6:
            print(f"WARNING: {test_date} is not a Sunday!")
        
        schedule = sim.simulate_day(test_date)
        
        # Filter for Prime Time Block (20:00 - 23:00)
        prime_items = [e for e in schedule if 20 <= e['time'].hour < 23 and e['type'] == 'content']
        
        if not prime_items:
            print("❌ No prime time content found.")
            continue
            
        for item in prime_items:
            time_str = item['time'].strftime('%H:%M')
            content = item['content']
            
            # Add helpful annotations
            note = ""
            if "__auto_lost" in content: note = " <-- ✅ Lost (Active)"
            elif "__auto_alias" in content: note = " <-- ✅ Alias (Active)"
            elif "__auto_fringe" in content: note = " <-- ✅ Fringe (Active)"
            elif "auto_gen_" in content: note = " <-- Filler (Generated)"
            
            print(f"{time_str} | {content}{note}")

    print("\n" + "="*60)

if __name__ == "__main__":
    run_test()