#!/usr/bin/env python3
"""
Test script for Cartoon Network Christmas Injection.
Verifies that holiday logic injects themed episodes in the week leading up to Christmas.
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import cartoon_network

if __name__ == "__main__":
    # Use Dec 5th: Strong enough for injection (>1%), weak enough to avoid 100% schedule takeover
    test_date = date(2026, 12, 5) 
    print(f"Testing Cartoon Network - Early December ({test_date})")
    print("Checking for Holiday Injection...")
    print("="*60)
    
    sim = ChannelSimulator(cartoon_network)
    schedule = sim.simulate_day(test_date)
    
    # 1. Check for specific Adult Swim shows (if block wasn't swapped)
    as_shows = ["bobs_burgers", "rick_morty", "archer", "birdman"]
    found_shows = [e for e in schedule if e['type'] == 'content' and 
                  any(s in str(e['content']) for s in as_shows)]
    
    # 2. Check for ANY injection
    injected_items = [e for e in schedule if e['type'] == 'content' and "_auto_christmas" in str(e['content'])]
    
    if injected_items:
        print(f"✅ Found {len(injected_items)} items with Christmas injection:")
        for entry in injected_items[:5]: # Show first 5
            print(f"   {entry['time'].strftime('%H:%M')} | {entry['content']}")
        if len(injected_items) > 5:
            print(f"   ... and {len(injected_items)-5} more")
    else:
        print("❌ No Christmas injection found.")

    print("-" * 40)

    if not found_shows:
        print("⚠️  Adult Swim block was likely swapped for Holiday Movies (Normal behavior for December)")
    else:
        print(f"✅ Found {len(found_shows)} Adult Swim items.")

    print("="*60)