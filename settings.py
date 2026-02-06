"""
Configuration settings for the ErsatzTV Scheduling Framework.
"""
import os
from pathlib import Path
from datetime import date

# ==========================================
# PATH CONFIGURATION
# ==========================================

# Base directory of the project (calculated relative to this file)
# scripts/settings.py -> scripts/ -> project_root/
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory for logs
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)

# ==========================================
# FRAMEWORK BEHAVIOR
# ==========================================

# Default playback order for collections/searches
# Used by logic/queries.py playback_order() function
DEFAULT_ORDER = "Shuffle"  # "Shuffle" or "Chronological"

# Program & Block Defaults
DEFAULT_FILL_STRATEGY = "yield"
DEFAULT_APPOINTMENT_START_DATE = date(2026, 1, 1)
DEFAULT_BLOCK_EPG_GROUPING = False
DEFAULT_COMMERCIAL_DURATION = 0 # seconds
DEFAULT_COMMERCIAL_CONTENT = "commercials_spot"
DEFAULT_CIRCUIT_BREAKER_SKIP = 30 # Minutes to skip if playback stalls

# Feature Flags
ENABLE_SMART_BUMPERS = False
ENABLE_HOLIDAY_INJECTION = False
ENABLE_SEASONAL_INJECTION = False # This flag controls auto-tagging
ENABLE_THEMATIC_INJECTION = False
ENABLE_COMMERCIALS = False
ENABLE_FILLER = False
ENABLE_BUMPERS = False
ENABLE_MARATHONS = False

# Logging
LOG_LEVEL = "INFO"
VERBOSE_LOGGING = False