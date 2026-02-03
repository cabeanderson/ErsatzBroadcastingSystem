#!/usr/bin/env python3
"""
Test script for Circuit Breaker Logic.
Verifies that the scheduler recovers from stalled playback using fallback content or time skips.
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import detective

def test_fallback_recovery():
    print("\n" + "="*80)
    print("TEST 1: Circuit Breaker Recovery via Fallback")
    print("Scenario: Main content is missing, Fallback content works.")
    print("="*80)
    
    # Detective channel has fallback_content="procedural_tv"
    # Weekday Morning (08:00) plays DETECTIVE_USA_BLOCK (monk_tv, psych_tv)
    
    # We simulate that 'monk_tv' is broken/missing
    missing = {"monk_tv"}
    
    sim = ChannelSimulator(detective, missing_content=missing)
    # Simulate just the morning block
    schedule = sim.simulate_day(date(2026, 7, 15), hours=12)
    
    # Filter for morning block (08:00-12:00)
    morning_items = [e for e in schedule if 8 <= e['time'].hour < 12]
    
    print("\nMorning Schedule:")
    for item in morning_items:
        if item['type'] == 'error':
            print(f"{item['time'].strftime('%H:%M')} | ❌ {item['content']}")
        elif item['type'] == 'meta':
            print(f"{item['time'].strftime('%H:%M')} | 🔧 {item['content']}")
        else:
            print(f"{item['time'].strftime('%H:%M')} | 📺 {item['content']}")

    # Verification
    # 1. Should see error for monk_tv
    # 2. Should see procedural_tv (fallback) playing immediately after
    
    errors = [e for e in morning_items if e['type'] == 'error' and "monk_tv" in e['content']]
    fallbacks = [e for e in morning_items if e['type'] == 'content' and "procedural_tv" in e['content']]
    
    if errors and fallbacks:
        print("\n✅ SUCCESS: Circuit breaker caught stalled 'monk_tv' and played 'procedural_tv'.")
    else:
        print("\n❌ FAILURE: Fallback logic did not trigger as expected.")


def test_hard_skip():
    print("\n" + "="*80)
    print("TEST 2: Circuit Breaker Hard Time Skip")
    print("Scenario: Main content AND Fallback content are missing.")
    print("="*80)
    
    # Simulate both main content and fallback being broken
    missing = {"monk_tv", "procedural_tv"}
    
    sim = ChannelSimulator(detective, missing_content=missing)
    schedule = sim.simulate_day(date(2026, 7, 15), hours=12)
    
    morning_items = [e for e in schedule if 8 <= e['time'].hour < 12]
    
    print("\nMorning Schedule:")
    for item in morning_items:
        if item['type'] == 'error':
            print(f"{item['time'].strftime('%H:%M')} | ❌ {item['content']}")
        elif item['type'] == 'meta':
            print(f"{item['time'].strftime('%H:%M')} | 🔧 {item['content']}")
        else:
            print(f"{item['time'].strftime('%H:%M')} | 📺 {item['content']}")

    # Verification: Look for WAIT_UNTIL meta event
    skips = [e for e in morning_items if e['type'] == 'meta' and "WAIT_UNTIL" in e['content']]
    
    if skips:
        print(f"\n✅ SUCCESS: Found {len(skips)} hard time skips (WAIT_UNTIL).")
    else:
        print("\n❌ FAILURE: Did not detect hard time skip.")

if __name__ == "__main__":
    test_fallback_recovery()
    test_hard_skip()