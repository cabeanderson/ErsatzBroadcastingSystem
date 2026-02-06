"""
Test Channel for verifying ErsatzTV behavior.
"""
from etv_client.models import ControlWaitUntil
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.core.logger import ChannelLogger

# ==============================================================================
# SCHEDULE DEFINITIONS
# ==============================================================================

SCHEDULES = {
    "WEEKDAY": {
        "morning": "test_monk_morning", # 08:00 - 10:00
        "evening": "test_monk_evening", # 17:00 - 20:00
    },
    "WEEKEND": {
        "morning": "test_monk_morning",
        "evening": "test_monk_evening",
    }
}

# ==============================================================================
# ERSATZTV INTEGRATION
# ==============================================================================

def define_content(api, context, build_id):
    pass

def reset_playout(api, context, build_id):
    return api.wait_until(build_id, ControlWaitUntil(when="00:00", tomorrow=False, rewind_on_reset=True))

def build_playout(api, context, build_id):
    config = ScheduleConfig(
        schedules=SCHEDULES,
        timeslot_preset="default",
        logger=ChannelLogger(prefix="[TEST]"),
        fallback_content=None
    )
    return run_daily_schedule(api, context, build_id, config)