#!/usr/bin/env python3
"""
Test script for Sitcoms Channel Refactor Verification.
Verifies that TGIF BrandedBlock (with EPG grouping) works correctly.
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import sitcoms

if __name__ == "__main__":
    print("Testing Sitcoms Channel Refactor (TGIF Block)")
    print("="*60)
    
    # Test Date: Friday, July 17, 2026 (Friday is TGIF night)
    test_date = date(2026, 7, 17)
    
    sim = ChannelSimulator(sitcoms)
    schedule = sim.simulate_day(test_date)
    
    print(f"Schedule for {test_date.strftime('%A, %B %d')}:")
    
    # Filter for TGIF block (Prime Time 20:00-23:00 on Fridays)
    tgif_items = [e for e in schedule if 20 <= e['time'].hour < 23]
    
    print("\nTGIF Block (Prime Time 20:00-23:00):")
    for item in tgif_items[:15]:
        content = item['content']
        type_icon = "📺" if item['type'] == 'content' else "⚙️"
        print(f"{item['time'].strftime('%H:%M')} | {type_icon} {content}")
        
    # Verify EPG Grouping
    epg_starts = [e for e in tgif_items if e['type'] == 'meta' and "EPG_GROUP_START" in e['content']]
    
    if epg_starts:
        print(f"\n✅ SUCCESS: Found EPG Group Start: {epg_starts[0]['content']}")
    else:
        print("\n❌ FAILURE: No EPG Group Start found for TGIF block.")

    # Verify Bumpers (TGIF uses 'commercials_90s_spot' as bumpers)
    bumpers = [e for e in tgif_items if e['type'] == 'content' and "commercials_90s_spot" in str(e['content'])]
    if bumpers:
        print(f"✅ SUCCESS: Found {len(bumpers)} TGIF bumpers.")
    else:
        print("⚠️  WARNING: No bumpers found (might be duration/timing related).")

    print("\n" + "="*60)
