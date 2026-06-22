"""
The Schedule Runner.

Orchestrates the daily execution loop, coordinating the Director (Time),
Resolver (Content), and Engines (Playback) to generate the stream.
"""

from typing import Any
from scripts.core import DayDirector
from scripts.logic.calendar.holidays import HolidayContext
from scripts.logic.resolution.pipeline import resolve_content
from scripts.logic.resolution.playback import hour_in_window
from scripts.logic.resolution.resolver import ContentResolver
from scripts.engines.dispatcher import play_schedule_slot, maintain_playout_invariants
from scripts.library.sources import MASTER_SOURCES
from scripts.logic.calendar.assembly import assemble_day_schedule
from scripts.scheduling.config import ScheduleConfig
from scripts.scheduling.pre_registration import pre_register_all_content
from scripts.engines.blocks import PlayoutSession

class ScheduleRunner:
    """
    The Standard Broadcast Runner.
    Uses time slots, day parts, marathons, and holiday overrides.
    """
    def __init__(self, api: Any, context: Any, build_id: str, config: ScheduleConfig):
        self.api = api
        self.context = context
        self.build_id = build_id
        self.config = config
        self.resolver = ContentResolver(api, build_id, MASTER_SOURCES, config.logger, global_filter=config.global_filter)

    def run(self) -> Any:
        """Main execution loop."""
        try:
            pre_register_all_content(self.resolver, self.config)
        except Exception as e:
            self.config.logger.warn(f"Pre-registration failed: {e}")

        while not self.context.is_done:
            self.boss = DayDirector(self.context)
            self.holiday_ctx = HolidayContext(self.boss)
            start_day = self.context.current_time.day
            last_time = self.context.current_time

            day_schedule, marathon_block, marathon_window = assemble_day_schedule(self.config, self.boss, self.holiday_ctx)

            self.config.logger.info(f"=== {self.boss.now.strftime('%A, %B %d, %Y')} ===")
            self.config.logger.info(f"Season: {self.boss.season_vibe} | Holidays: {', '.join(self.holiday_ctx.active_holidays) or 'None'}")

            session = PlayoutSession(
                api=self.api,
                build_id=self.build_id,
                context=self.context,
                resolver=self.resolver,
                logger=self.config.logger,
                boss=self.boss,
                holiday_ctx=self.holiday_ctx,
                config=self.config
            )

            while self.context.current_time.day == start_day and not self.context.is_done:
                hour = self.context.current_time.hour

                current_slot_tuple = None
                target = None
                
                # 1. Check Marathon Overlay
                if marathon_block and marathon_window and hour_in_window(hour, marathon_window[0], marathon_window[1]):
                    current_slot_tuple = marathon_window
                    target = marathon_block
                else:
                    # 2. Check Regular Schedule
                    for (start, end), entry in sorted(day_schedule.items()):
                        if hour_in_window(hour, start, end):
                            current_slot_tuple = (start, end)
                            target = entry
                            break
                
                # Handle gaps in schedule (default to 1-hour slot for fallback)
                if current_slot_tuple is None:
                    current_slot_tuple = (hour, (hour + 1) % 24)
                    target = self.config.fallback_content

                session.context = self.context
                result = resolve_content(target, self.boss, self.holiday_ctx, self.config, self.resolver, self.config.logger)
                self.context = play_schedule_slot(session, result, current_slot_tuple, day_schedule=day_schedule)
                
                # If we just played the marathon and returned, disable it so we fall back to normal schedule
                if marathon_block and target is marathon_block:
                    self.config.logger.info(f"Marathon '{marathon_block.name}' yielded/finished. Returning to regular schedule.")
                    marathon_block = None

                session.context = self.context
                self.context = maintain_playout_invariants(session, last_time)
                last_time = self.context.current_time

        return self.context