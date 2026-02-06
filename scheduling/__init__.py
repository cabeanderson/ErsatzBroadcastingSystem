"""
Scheduling subsystem.
"""

from .config import ScheduleConfig
from .runner import ScheduleRunner

def run_daily_schedule(api, context, build_id, config):
    """Entry point for standard broadcast scheduling."""
    runner = ScheduleRunner(api, context, build_id, config)
    return runner.run()