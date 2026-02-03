#!/usr/bin/env python3
"""
Test script for Lost Appointment TV logic.
Verifies that Lost plays correctly across seasons (Appointment vs Default).
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.library.sources import MASTER_SOURCES

# Register mock keys to avoid warnings and ensure duration guessing works
for i in range(1, 7):
    MASTER_SOURCES[f"lost_s{i}"] = f"type:episode AND tag:lost_s{i}"

MASTER_SOURCES["lost_chronological_tv"] = "type:episode AND tag:lost_all"
MASTER_SOURCES["alias_chronological_tv"] = "type:episode AND tag:alias"
MASTER_SOURCES["fringe_chronological_tv"] = "type:episode AND tag:fringe"

from scripts.channels import scifi

def test_lost_schedule():
    print("Testing Lost Appointment Schedule (Sci-Fi Channel)")
    print("="*60)
    
    sim = ChannelSimulator(scifi)
    
    # 1. Fall 2026 - Season 1 should be active
    # Fall usually starts around Sept 22. Let's pick Oct 4, 2026 (Sunday).
    date_s1 = date(2026, 10, 4)
    print(f"\n1. Testing Fall 2026 (Season 1 Active) - {date_s1}")
    schedule_s1 = sim.simulate_day(date_s1)
    
    # Filter for Prime Time (20:00)
    prime_items = [e for e in schedule_s1 if 20 <= e['time'].hour < 23 and e['type'] == 'content']
    
    if not prime_items:
        print("❌ FAILURE: No content in prime time.")
    else:
        # First item should be Lost S1
        first = prime_items[0]['content']
        print(f"   Played: {first}")
        if first == "lost_s1":
            print("   ✅ Correct: Playing Season 1")
        else:
            print(f"   ❌ Incorrect: Expected 'lost_s1', got '{first}'")

    # 2. Summer 2027 - Off-season (Default)
    # Season 1 (25 eps) ends approx March 2027. July 2027 should be off-season.
    date_off = date(2027, 7, 11) # Sunday
    print(f"\n2. Testing Summer 2027 (Off-Season) - {date_off}")
    schedule_off = sim.simulate_day(date_off)
    
    prime_items_off = [e for e in schedule_off if 20 <= e['time'].hour < 23 and e['type'] == 'content']
    
    if not prime_items_off:
        print("❌ FAILURE: No content in prime time.")
    else:
        # First item should be Default (lost_chronological_tv)
        first = prime_items_off[0]['content']
        print(f"   Played: {first}")
        if first == "lost_chronological_tv":
            print("   ✅ Correct: Playing Default (Reruns)")
        else:
            print(f"   ❌ Incorrect: Expected 'lost_chronological_tv', got '{first}'")

    # 3. Fall 2027 - Season 2 should be active
    date_s2 = date(2027, 10, 3) # Sunday
    print(f"\n3. Testing Fall 2027 (Season 2 Active) - {date_s2}")
    schedule_s2 = sim.simulate_day(date_s2)
    
    prime_items_s2 = [e for e in schedule_s2 if 20 <= e['time'].hour < 23 and e['type'] == 'content']
    
    if not prime_items_s2:
        print("❌ FAILURE: No content in prime time.")
    else:
        # First item should be Lost S2
        first = prime_items_s2[0]['content']
        print(f"   Played: {first}")
        if first == "lost_s2":
            print("   ✅ Correct: Playing Season 2")
        else:
            print(f"   ❌ Incorrect: Expected 'lost_s2', got '{first}'")

    print("\n" + "="*60)

if __name__ == "__main__":
    test_lost_schedule()