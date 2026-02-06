"""
Calendar logic: Time, Holidays, Seasons, and Triggers.
"""
from .holidays import with_holidays, HolidayContext
from .seasonal import SeasonalBlock
from .assembly import assemble_day_schedule
from .timeslots import expand_timeslots, get_timeslot_map