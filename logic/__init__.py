"""
Main scheduling logic - the "Brain" of the system.
"""

from .calendar.holidays import with_holidays
from .models import Marathon, Branding, Fallback, Swap, Feather, CommercialBreak
from .resolution.resolver import ContentResolver

__all__ = ['with_holidays', 'Marathon', 'Branding', 'Fallback', 'Swap', 'Feather', 'CommercialBreak', 'ContentResolver']