#!/usr/bin/env python3
"""
Test script to verify multi-watermark capabilities.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks

# Install mocks BEFORE importing modules that depend on etv_client
install_mocks()

from scripts.logic.models import BrandedBlock
from scripts.library import collections
from scripts.schedule import run_daily_schedule, ScheduleConfig
from scripts.library.sources import MASTER_SOURCES

# Register test content to avoid "Key not found" errors
MASTER_SOURCES["special_event_movie"] = "type:movie AND tag:special"
MASTER_SOURCES["test_fallback"] = "type:episode AND tag:fallback"

# Define a block with MULTIPLE watermarks
EVENT_BLOCK = BrandedBlock(
    name="Special Event",
    content=collections.RandomCollection(["special_event_movie"]),
    use_epg_group=True
)

SCHEDULES = {
    "WEEKDAY": {
        "prime": EVENT_BLOCK
    }
}

def build_playout(api, context, build_id):
    config = ScheduleConfig(
        schedules=SCHEDULES,
        timeslot_preset="default",
        log_func=lambda x: None, # Silence normal logs
        fallback_content="test_fallback"
    )
    return run_daily_schedule(api, context, build_id, config)

if __name__ == "__main__":
    print("Testing Multi-Watermark Support...")
    
    # Create a dummy module to pass to simulator
    import types
    dummy_channel = types.ModuleType("dummy_channel")
    dummy_channel.build_playout = build_playout
    
    sim = ChannelSimulator(dummy_channel)
    schedule = sim.simulate_day(datetime(2026, 1, 1))
    
    # Print only the meta events to verify
    print("\nLog Output:")
    for entry in schedule:
        if entry['type'] == 'meta' and "WATERMARK" in entry['content']:
            print(f"{entry['time'].strftime('%H:%M')} | {entry['content']}")