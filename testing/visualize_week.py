#!/usr/bin/env python3
"""
Visualize Weekly Schedule
Prints the resolved timeslots and blocks for a given channel over a week.
Useful for verifying schedule structure, seasonal overrides, and marathon triggers.
"""

import sys
import os
import argparse
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Install mocks to avoid etv_client dependency
from scripts.testing.simulator import install_mocks, MockContext
install_mocks()

from scripts.core import DayDirector
from scripts.logic.calendar.holidays import HolidayContext
from scripts.logic.calendar.assembly import assemble_day_schedule
from scripts.scheduling.config import ScheduleConfig
from scripts.logic.structures import Block, Program
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.core.logger import ChannelLogger
from scripts.library.filters import INJECTION_RULES, SEASONAL_TAG_QUERIES

# Import channels
from scripts.channels import cartoon_network, detective, scifi, sitcoms, classic_movies, eighties, british

CHANNELS = {
    "cartoon_network": {"module": cartoon_network, "preset": "default"},
    "detective": {"module": detective, "preset": "default"},
    "scifi": {"module": scifi, "preset": "default"},
    "sitcoms": {"module": sitcoms, "preset": "default"},
    "classic_movies": {"module": classic_movies, "preset": "movies"},
    "eighties": {"module": eighties, "preset": "default"},
    "british": {"module": british, "preset": "default"},
}

def find_variable_name(obj):
    """Attempt to find the variable name for a collection object in loaded modules."""
    # Prioritize library modules
    sorted_modules = sorted(sys.modules.items(), key=lambda x: 0 if "library" in x[0] else 1)
    
    best_name = None
    
    for mod_name, module in sorted_modules:
        if not mod_name.startswith("scripts.") or "testing" in mod_name:
            continue
            
        for var_name, var_val in vars(module).items():
            if var_name.startswith("_"):
                continue
            if var_val is obj:
                if var_name.isupper():
                    return var_name
                if best_name is None:
                    best_name = var_name
    return best_name

def get_content_name(content, boss=None):
    """Extract a readable name from various content objects."""
    if isinstance(content, str):
        return content
    
    if isinstance(content, dict):
        if boss:
            # Resolve conditional dicts (e.g. day-of-week overrides inside a slot)
            for key in content:
                if key != "default" and boss.has(key):
                    return get_content_name(content[key], boss)
            if "default" in content:
                return get_content_name(content["default"], boss)
        return "Conditional (Dict)"

    if isinstance(content, Block):
        return f"Block: {content.name}"
        
    if isinstance(content, Program):
        return f"Program: {content.name}"
        
    if isinstance(content, SeasonalBlock):
        # Resolve the seasonal block to see what would play
        base_name = get_content_name(content.base, boss)
        if boss:
            season = boss.season_vibe
            if season in content.seasonal:
                seasonal_content = content.seasonal[season]
                # Handle Swap/Feather wrappers if present
                if hasattr(seasonal_content, 'content'): 
                    seasonal_content = seasonal_content.content
                
                seasonal_name = get_content_name(seasonal_content, boss)
                return f"Seasonal ({season}): {seasonal_name}"
        return f"Seasonal: {base_name}"
        
    # Handle Collections (RandomCollection, OrderedCollection, etc.)
    if hasattr(content, "items") and isinstance(content.items, list):
        var_name = find_variable_name(content)
        if var_name:
            return var_name
            
        items = content.items
        display_items = []
        for item in items[:3]:
            if isinstance(item, str):
                display_items.append(item)
            elif isinstance(item, dict):
                display_items.append(item.get("title", item.get("name", "Untitled")))
            elif hasattr(item, "name"):
                display_items.append(item.name)
            elif hasattr(item, "title"):
                display_items.append(item.title)
            else:
                display_items.append(str(item))
        
        suffix = ", ..." if len(items) > 3 else ""
        return f"{type(content).__name__} ({len(items)}): {', '.join(display_items)}{suffix}"

    if hasattr(content, "name"):
        return content.name
        
    return str(type(content).__name__)

def visualize_channel(channel_name, start_date):
    if channel_name not in CHANNELS:
        print(f"❌ Unknown channel: {channel_name}")
        print(f"Available channels: {', '.join(CHANNELS.keys())}")
        return

    info = CHANNELS[channel_name]
    module = info["module"]
    preset = info["preset"]
    
    # Reconstruct config from module exports
    schedules = getattr(module, "SCHEDULES", {})
    marathons = getattr(module, "MARATHONS", [])
    holiday_schedules = getattr(module, "HOLIDAY_SCHEDULES", {})
    
    # Create a silent logger
    logger = ChannelLogger(verbose=False)

    config = ScheduleConfig(
        schedules=schedules,
        marathons=marathons,
        holiday_schedules=holiday_schedules,
        timeslot_preset=preset,
        logger=logger
    )

    print(f"\n📅 WEEKLY SCHEDULE VISUALIZATION: {channel_name.upper()}")
    print("=" * 80)

    current_date = start_date
    for _ in range(7):
        # Mock context for the specific day
        mock_context = MockContext(datetime.combine(current_date, datetime.min.time()))
        
        boss = DayDirector(mock_context)
        holiday_ctx = HolidayContext(boss)
        
        # Assemble the schedule for this day
        day_schedule, marathon_block, marathon_window = assemble_day_schedule(config, boss, holiday_ctx)
        
        date_str = current_date.strftime("%A, %B %d")
        print(f"\n{date_str} | Season: {boss.season_vibe}")
        if holiday_ctx.active_holidays:
            print(f"  🎉 Holidays: {', '.join(holiday_ctx.active_holidays)}")
            
        # Check for active injections
        injections = []
        
        # Holiday
        for h, strength in holiday_ctx.envelope.items():
            if strength > 0.0:
                injections.append(f"Holiday: {h} ({strength:.0%})")
        
        # Thematic
        for label, rule_config in INJECTION_RULES.items():
            prob = 0.0
            mode = rule_config.get("mode", "static")
            
            if mode == "ramp":
                signal_name = rule_config.get("signal")
                if signal_name:
                    strength = boss.signal(signal_name)
                    prob = strength * rule_config.get("ratio", 1.0)
            elif mode == "static":
                check_label = rule_config.get("label", label)
                if boss.has(check_label):
                    prob = rule_config.get("ratio", 1.0)
            
            if prob > 0.0:
                injections.append(f"Thematic: {label} ({prob:.0%})")
        
        # Seasonal
        for season_name in SEASONAL_TAG_QUERIES:
            strength = boss.get_season_strength(season_name)
            prob = strength * 0.4
            if prob > 0.0:
                injections.append(f"Seasonal: {season_name} ({prob:.0%})")

        if injections:
            print(f"  💉 Injections: {', '.join(injections)}")

        if marathon_block:
            start, end = marathon_window
            print(f"  🚀 MARATHON OVERRIDE: {marathon_block.name} ({start:02d}:00 - {end:02d}:00)")
            
        print(f"  {'Time':<15} | {'Content'}")
        print(f"  {'-'*15}-+-{'-'*50}")
        
        # Sort slots by start time
        sorted_slots = sorted(day_schedule.items(), key=lambda x: x[0][0])
        
        for (start, end), content in sorted_slots:
            # Handle midnight wrap for display (e.g. 22-26 -> 22:00-02:00)
            end_disp = end % 24
            start_disp = start % 24
            time_str = f"{start_disp:02d}:00 - {end_disp:02d}:00"
            
            # If marathon is active, indicate if this slot is covered
            is_covered = False
            if marathon_block:
                m_start, m_end = marathon_window
                # Simple overlap check
                if start >= m_start and start < m_end:
                    is_covered = True
            
            name = get_content_name(content, boss)
            
            prefix = "  "
            if is_covered:
                prefix = "░░" # Dimmed/Covered
                name = f"(Covered by Marathon) {name}"
                
            print(f"{prefix} {time_str:<15} | {name}")
            
        current_date += timedelta(days=1)
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize weekly schedule timeslots")
    parser.add_argument("channel", nargs="?", default="cartoon_network", help="Channel name (e.g. cartoon_network, scifi)")
    parser.add_argument("--date", help="Start date YYYY-MM-DD", default=None)
    args = parser.parse_args()
    
    start = datetime.now().date()
    if args.date:
        try:
            start = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
        
    visualize_channel(args.channel, start)