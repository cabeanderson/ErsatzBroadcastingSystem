#!/usr/bin/env python3
"""
Test script for CommercialBreak Logic.
Verifies that CommercialBreak wrappers work in schedule slots and collections.
"""
import sys
import os
from datetime import date, datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.logic.models import CommercialBreak
from scripts.library import structures
from scripts.schedule import run_daily_schedule, ScheduleConfig
from scripts.library.sources import MASTER_SOURCES

# Register test content
MASTER_SOURCES["test_show"] = "type:episode AND tag:test"
MASTER_SOURCES["commercials_spot"] = "type:other_video"

# Define a collection with interleaved ads
TEST_COLLECTION = structures.OrderedCollection([
    "test_show",
    CommercialBreak(duration_seconds=1800, content="commercials_spot"), # 30 min break for visibility
    "test_show"
])

# Define schedule
SCHEDULES = {
    "WEEKDAY": {
        "morning": CommercialBreak(duration_seconds=3600, content="commercials_spot"), # 1 hour of ads
        "noon": TEST_COLLECTION
    }
}

def build_playout(api, context, build_id):
    config = ScheduleConfig(
        schedules=SCHEDULES,
        timeslot_preset="default",
        logger=None, # Silence logs
        fallback_content="test_show"
    )
    return run_daily_schedule(api, context, build_id, config)

if __name__ == "__main__":
    print("Testing CommercialBreak Logic")
    print("="*60)
    
    # Create dummy module
    import types
    dummy_channel = types.ModuleType("dummy_channel")
    dummy_channel.build_playout = build_playout
    
    sim = ChannelSimulator(dummy_channel)
    schedule = sim.simulate_day(date(2026, 1, 1))
    
    print("\nSchedule Output:")
    for item in schedule:
        if 8 <= item['time'].hour < 14: # Morning (8-10) and Noon (12-14)
            if item['type'] == 'content':
                if "PAD_UNTIL" in item['content']:
                    print(f"{item['time'].strftime('%H:%M')} | ☕ {item['content']}")
                else:
                    print(f"{item['time'].strftime('%H:%M')} | 📺 {item['content']}")
            elif item['type'] == 'meta':
                 print(f"{item['time'].strftime('%H:%M')} | ⚙️  {item['content']}")

    # Verification
    # Morning (8:00) should be a solid block of ads
    morning_ads = [e for e in schedule if 8 <= e['time'].hour < 9 and "PAD_UNTIL" in str(e.get('content', ''))]
    
    # Noon (12:00) should be Show -> Ads -> Show
    noon_items = [e for e in schedule if 12 <= e['time'].hour < 14 and e['type'] == 'content']
    
    if morning_ads:
        print("\n✅ SUCCESS: Found Morning CommercialBreak (Schedule Slot).")
    else:
        print("\n❌ FAILURE: Morning CommercialBreak missing.")
        
    if len(noon_items) >= 3 and "PAD_UNTIL" in str(noon_items[1]['content']):
        print("✅ SUCCESS: Found Interleaved CommercialBreak (Collection).")
    else:
        print("❌ FAILURE: Interleaved CommercialBreak missing or incorrect order.")

    print("="*60)