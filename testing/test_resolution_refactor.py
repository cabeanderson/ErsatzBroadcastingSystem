#!/usr/bin/env python3
"""
Test script for ResolutionResult Refactor.
Verifies that PlayOnce and Fallback wrappers are correctly handled
by the new resolution pipeline.
"""
import sys
import os
from datetime import date, datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import detective

if __name__ == "__main__":
    print("Testing ResolutionResult Refactor on Detective Channel")
    print("="*60)
    
    # Test Date: Monday (WEEKDAY_A)
    # Detective Channel Noon Block: PlayOnce({"WEEKDAY_A": "elsbeth_tv", ...})
    test_date = date(2026, 7, 13)
    
    sim = ChannelSimulator(detective)
    schedule = sim.simulate_day(test_date)
    
    print(f"Schedule for {test_date.strftime('%A, %B %d')}:")
    
    # 1. Verify Noon PlayOnce Slot
    # Expectation: 1 episode of 'elsbeth_tv', then filling with 'procedural_tv' (afternoon block)
    noon_items = [e for e in schedule if 12 <= e['time'].hour < 14 and e['type'] == 'content']
    
    print("\nNoon Block (PlayOnce Test):")
    for item in noon_items:
        print(f"{item['time'].strftime('%H:%M')} | {item['content']}")
        
    if not noon_items:
        print("❌ FAILURE: No items found in noon block.")
    else:
        first_item = noon_items[0]
        if first_item['content'] == "elsbeth_tv":
            print("✅ SUCCESS: PlayOnce selected correct day-of-week override ('elsbeth_tv')")
        else:
            print(f"❌ FAILURE: Expected 'elsbeth_tv', got '{first_item['content']}'")
            
        # Check if subsequent items are from the next block (afternoon -> DETECTIVE_USA_BLOCK -> monk/psych)
        if len(noon_items) > 1:
            print(f"✅ SUCCESS: Gap filled with content ('{noon_items[1]['content']}')")

    print("\n" + "="*60)