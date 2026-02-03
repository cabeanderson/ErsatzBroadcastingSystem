#!/usr/bin/env python3
"""
Test script for Cartoon Network Refactor Verification.
Verifies that BrandedBlocks (Adult Swim) function correctly with the new ResolutionResult pipeline.
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import cartoon_network
from scripts.logic.models import BrandedBlock

if __name__ == "__main__":
    print("Testing Cartoon Network Refactor (BrandedBlock Resolution)")
    print("="*60)
    
    # Test Date: A standard weekday (Adult Swim runs at night)
    test_date = date(2026, 7, 15)
    
    sim = ChannelSimulator(cartoon_network)
    schedule = sim.simulate_day(test_date)
    
    print(f"Schedule for {test_date.strftime('%A, %B %d')}:")
    
    # Filter for Adult Swim block (Prime Time 20:00-23:00 on Weekdays)
    as_items = [e for e in schedule if 20 <= e['time'].hour < 23]
    
    print("\nAdult Swim Block (Prime Time 20:00-23:00):")
    for item in as_items[:10]:
        content = item['content']
        type_icon = "📺" if item['type'] == 'content' else "⚙️"
        print(f"{item['time'].strftime('%H:%M')} | {type_icon} {content}")
        
    # Verify we see content
    content_count = len([e for e in as_items if e['type'] == 'content'])
    
    # Check for intro (Adult Swim block has intro "adult_swim_intro")
    has_intro = any("adult_swim_intro" in str(e['content']) for e in as_items)
    
    if content_count > 0:
        print(f"\n✅ SUCCESS: Found {content_count} items in Adult Swim block.")
        if has_intro:
             print("✅ SUCCESS: Found Adult Swim intro.")
        else:
             print("⚠️  WARNING: Adult Swim intro not found (might be missing in mocks/registry).")
    else:
        print("\n❌ FAILURE: No content found in Adult Swim block.")

    print("\n" + "="*60)
