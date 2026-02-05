"""
Configuration settings for the ErsatzTV Scheduling Framework.
"""
import os
from pathlib import Path

# ==========================================
# PATH CONFIGURATION
# ==========================================

# Base directory of the project (calculated relative to this file)
# scripts/config.py -> scripts/ -> project_root/
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory for logs
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)

# ==========================================
# FRAMEWORK BEHAVIOR
# ==========================================

# Default playback order for collections/searches ("Shuffle" or "Chronological")
DEFAULT_ORDER = "Shuffle"

# Feature Flags
ENABLE_SMART_BUMPERS = True
ENABLE_HOLIDAY_INJECTION = True
ENABLE_SEASONAL_BLOCKS = True

# Logging
LOG_LEVEL = "INFO"
VERBOSE_LOGGING = False

# ==========================================
# LOCAL OVERRIDES
# ==========================================
# Create config_local.py to override settings without committing them
try:
    from .config_local import *
except ImportError:
    pass