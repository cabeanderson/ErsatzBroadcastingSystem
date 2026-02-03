#!/usr/bin/env python3
"""
Test script for PlayOnce Fallback Logic.
Verifies that PlayOnce slots correctly handle holiday injections (Fallback objects).
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import detective

if __name__ == "__main__":
    print("Testing PlayOnce Fallback Logic (Holiday Injection)")
    print("="*60)
    
    # Test Date: Thanksgiving (Thursday, Nov 26, 2026)
    # Detective Channel Noon Block (Thu = WEEKDAY_B): PlayOnce("moonlighting_tv")
    test_date = date(2026, 11, 26)
    
    # We simulate that the holiday version is MISSING to test the fallback mechanism
    # The injection logic will create: moonlighting_tv_auto_thanksgiving
    missing_content = {"moonlighting_tv_auto_thanksgiving"}
    
    sim = ChannelSimulator(detective, missing_content=missing_content)
    schedule = sim.simulate_day(test_date)
    
    print(f"Schedule for {test_date.strftime('%A, %B %d')}:")
    
    # Filter for Noon Block
    noon_items = [e for e in schedule if 12 <= e['time'].hour < 14]
    
    print("\nNoon Block (PlayOnce):")
    for item in noon_items:
        if item['type'] == 'error':
            print(f"{item['time'].strftime('%H:%M')} | ❌ {item['content']}")
        else:
            print(f"{item['time'].strftime('%H:%M')} | 📺 {item['content']}")
            
    # Verification
    # We expect:
    # 12:00 | MISSING: moonlighting_tv_auto_thanksgiving
    # 12:00 | moonlighting_tv
    
    errors = [e for e in noon_items if e['type'] == 'error' and "moonlighting_tv_auto_thanksgiving" in e['content']]
    success = [e for e in noon_items if e['type'] == 'content' and "moonlighting_tv" == e['content']]
    
    if errors and success:
        print("\n✅ SUCCESS: Attempted holiday version, failed, then played normal version.")
    elif success and not errors:
        print("\n⚠️  WARNING: Played normal version but didn't see failure for holiday version (Injection might not have happened).")
    else:
        print("\n❌ FAILURE: Did not play fallback content correctly.")

    print("\n" + "="*60)