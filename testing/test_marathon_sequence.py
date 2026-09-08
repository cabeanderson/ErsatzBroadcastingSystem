#!/usr/bin/env python3
"""
Test script for Marathon Sequence logic.
Verifies that a mixed-media marathon (Show -> Movie -> Show) plays correctly.
"""
from datetime import datetime, timedelta

# Run as a module, not a loose script:
#     python3 -m scripts.testing.test_marathon_sequence
# The package is importable from the project root, which is what makes
# `scripts.*` resolve. A sys.path.insert here used to paper over being
# run from anywhere, at the cost of the package being importable two
# different ways -- the same cleanup filler/ and nfo/ had on 2026-09-07.

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import cartoon_network
from scripts.logic.triggers import has_label
from scripts.logic.models import Marathon
from scripts.library import animation

def run_test():
    print("Testing Marathon Sequence (Cowboy Bebop)")
    print("="*60)
    
    # Force the marathon to trigger by overriding the trigger
    # We find the Cowboy Bebop marathon and replace its trigger
    for m in cartoon_network.MARATHONS:
        if m.name == "Cowboy Bebop":
            print("Found Cowboy Bebop marathon, forcing trigger...")
            m.trigger = lambda boss: True
            # Ensure collection is the sequence (it should be from the file update)
            m.collection = animation.COWBOY_BEBOP_COMPLETE
            break
            
    # Start date (arbitrary)
    start_date = datetime(2026, 5, 10, 8, 0, 0) # 8 AM
    
    # Define durations
    durations = {
        "auto_gen_cowboy_bebop_eps_1_22": 24, # 24 min per ep
        "auto_gen_cowboy_bebop__the_movie": 120, # 2 hours
        "auto_gen_cowboy_bebop_eps_23_26": 24
    }
    
    sim = ChannelSimulator(cartoon_network, content_durations=durations)
    
    # Simulate one day
    schedule = sim.simulate_day(start_date)
    
    # Filter for Marathon Time (10:00 - 24:00)
    marathon_items = [e for e in schedule if 10 <= e['time'].hour < 24 and e['type'] == 'content']
    
    if not marathon_items:
        print("❌ No marathon content found.")
    else:
        print(f"Found {len(marathon_items)} marathon items.")
        
        last_content = None
        transitions = 0
        # Print transitions in the marathon
        for item in marathon_items:
            if item['content'] != last_content:
                print(f"{item['time'].strftime('%H:%M')} | Now Playing: {item['content']}")
                last_content = item['content']
                transitions += 1
        
        print(f"\nDetected {transitions} content blocks in the sequence.")

if __name__ == "__main__":
    run_test()