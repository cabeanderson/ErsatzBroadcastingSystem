#!/usr/bin/env python3
"""
Integration tests for the holiday injection system.
Verifies that holiday overrides and fallback logic function correctly
using the simulator harness.
"""

from datetime import date
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import cartoon_network
from scripts.library import collections

def test_thanksgiving_injection():
    print("\n" + "="*80)
    print("TEST 1: Thanksgiving Day Injection (Nov 26, 2026)")
    print("Expectation: Shows should have '_auto_thanksgiving' suffix")
    print("="*80)
    
    # Thanksgiving 2026 is Nov 26
    sim = ChannelSimulator(cartoon_network)
    schedule = sim.simulate_day(date(2026, 11, 26), hours=24)
    
    # Filter for Adult Swim block (Prime Time) to see Bob's Burgers/Rick & Morty
    prime_schedule = [
        e for e in schedule 
        if e['type'] == 'content' and 20 <= e['time'].hour < 23
    ]
    
    print("\nPrime Time Schedule (Sample):")
    for entry in prime_schedule[:10]:
        print(f"{entry['time'].strftime('%H:%M')} | {entry['content']}")
        
    # Verification
    injected_count = len([e for e in prime_schedule if "_auto_thanksgiving" in e['content']])
    print(f"\n✅ Found {injected_count} injected Thanksgiving items in prime time.")


def test_fallback_logic():
    print("\n" + "="*80)
    print("TEST 2: Fallback Logic (Missing Holiday Content)")
    print("Expectation: Should try holiday version, fail, then play normal version")
    print("="*80)
    
    # Reset collection state to ensure Bob's Burgers plays (it's 4th in the list)
    # Since Test 1 ran, the index is advanced; we need to reset it.
    if hasattr(collections.ADULT_SWIM_MAIN, 'index'):
        collections.ADULT_SWIM_MAIN.index = 0

    # We will pretend Bob's Burgers has NO Thanksgiving episodes
    # The resolver creates this key: bobs_burgers_tv_auto_thanksgiving
    missing_keys = {"bobs_burgers_tv_auto_thanksgiving"}
    
    sim = ChannelSimulator(cartoon_network, missing_content=missing_keys)
    schedule = sim.simulate_day(date(2026, 11, 26), hours=24)
    
    # Look for the fallback sequence in the logs
    print("\nScanning schedule for fallback sequence...")
    
    found_fallback = False
    for i, entry in enumerate(schedule):
        if entry['type'] == 'error' and entry['content'] == "MISSING: bobs_burgers_tv_auto_thanksgiving":
            # Check if next item is the normal version
            if i + 1 < len(schedule):
                next_entry = schedule[i+1]
                if next_entry['content'] == "bobs_burgers_tv":
                    print(f"✅ SUCCESS at {entry['time'].strftime('%H:%M')}:")
                    print(f"   1. Tried: {entry['content']}")
                    print(f"   2. Fallback: {next_entry['content']}")
                    found_fallback = True
                    break
    
    if not found_fallback:
        print("❌ Failed to find fallback sequence.")

if __name__ == "__main__":
    test_thanksgiving_injection()
    test_fallback_logic()
