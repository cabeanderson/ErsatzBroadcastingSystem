"""
Configuration settings for the ErsatzTV Scheduling Framework.
"""
from pathlib import Path
from datetime import date

# ==========================================
# PATH CONFIGURATION
# ==========================================

# Base directory of the project (calculated relative to this file)
# scripts/settings.py -> scripts/ -> project_root/
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory for logs.
#
# Not created here. `import scripts.settings` sits under every module in the
# framework, so making a directory at import time meant merely importing the
# package wrote to disk -- and raised on a read-only filesystem, where nothing
# was going to log anyway. `core.logger` creates it when it actually opens a
# log file, inside the try/except that already handles a log path it cannot use.
LOG_DIR = BASE_DIR / "logs"

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
# Smart (per-show) bumpers. Three modes, resolvable per program, block and
# channel by logic/resolution/config_utils.resolve_smart_bumpers -- the same
# Program > Block > Channel > Global cascade filler and commercials already use.
#
#   "none"  never look up a per-show bumper; generic pools only.
#   "some"  try the per-show bumper, fall back to the generic pool. The mix.
#   "all"   per-show bumpers only; a show with none gets no bumper rather than
#           a generic one. For a channel whose branding is entirely per-show.
#
# This replaced a module-level ENABLE_SMART_BUMPERS bool that dispatcher read
# directly, which meant the choice was lineup-wide: every channel or none.
SMART_BUMPERS = "none"

# Break composition. A break carries at most this many bumpers, and never two
# in a row -- a bumper always touches a show on one side and is separated from
# any other bumper by content or commercials. Enforced by dispatcher.BreakState,
# not by call sites, so the invariant holds no matter which path emits branding.
MAX_BUMPERS_PER_BREAK = 2
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

# Each run starts a fresh log file; the previous LOG_BACKUP_RUNS runs are kept
# alongside it as .1, .2, ... Without this the handler appends forever -- eleven
# stacked runs is what turned pond.log into 88MB and made one build's output
# impossible to read in isolation.
LOG_BACKUP_RUNS = 3

# The seasonal tag injector builds OR-chains a few hundred characters long, and
# logs one per injection. At INFO the line is summarised; set this True to log
# the full query (it costs about 20MB per channel per run).
LOG_FULL_TAG_QUERIES = False