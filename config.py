"""
Deployment configuration — every host path and network address in one place.

Nothing here is specific to one installation. Each value has a default that is
correct for the normal case (the framework running inside the ErsatzTV
container, where the media library is mounted at `/media`), and each can be
overridden by an environment variable when it is not.

    MEDIA_ROOT        ETV_MEDIA_ROOT     /media
    ERSATZTV_URL      ETV_URL            http://127.0.0.1:8409

The offline tooling in `scripts/filler`, `scripts/nfo` and `scripts/testing`
runs on a workstation rather than in the container, so it sees the library at
a different path than the scheduler does. That is the whole reason this file
exists: point `ETV_MEDIA_ROOT` at wherever the library actually is and every
tool follows, instead of each script carrying its own absolute path.

Copy `env.example` to `.env`, edit it, and source it before running the
offline tools:

    cp env.example .env && $EDITOR .env
    set -a && . ./.env && set +a

`.env` is gitignored. This file is not — it is the example, and it should stay
free of any one machine's paths.
"""
import os
import sys
from pathlib import Path


def _path(env, default):
    """Read a path from the environment, falling back to `default`."""
    return Path(os.environ.get(env) or default).expanduser()


def _text(env, default):
    """Read a string from the environment, falling back to `default`."""
    return os.environ.get(env) or default


# ==========================================
# MEDIA LIBRARY
# ==========================================
# `/media` is where ErsatzTV sees the library inside the container. On a
# workstation set ETV_MEDIA_ROOT to the host path — the tools mount the same
# tree at a different place, and only this variable needs to know that.

MEDIA_ROOT = _path("ETV_MEDIA_ROOT", "/media")

MOVIES_ROOT = _path("ETV_MOVIES_ROOT", MEDIA_ROOT / "movies")
TV_ROOT = _path("ETV_TV_ROOT", MEDIA_ROOT / "tv")
FILLER_ROOT = _path("ETV_FILLER_ROOT", MEDIA_ROOT / "filler")
STAGING_ROOT = _path("ETV_STAGING_ROOT", MEDIA_ROOT / ".staging")

# Filler subtrees. Derived, not separately configurable — the taxonomy under
# the filler root is the framework's own and is documented in
# reference/filler-taxonomy.md.
COMMERCIALS_ROOT = FILLER_ROOT / "commercials"
COMMERCIALS_US = COMMERCIALS_ROOT / "us"
COMMERCIALS_UK = COMMERCIALS_ROOT / "uk"
BUMPERS_ROOT = FILLER_ROOT / "bumpers"
PROMOS_ROOT = FILLER_ROOT / "promos"
INTERSTITIALS_ROOT = FILLER_ROOT / "interstitials"

# Staging subtrees. Working space for acquisition and splitting; nothing here
# is indexed by ErsatzTV, which is why it lives under a dotted directory.
STAGE_US_COMMERCIALS = STAGING_ROOT / "us_commercials"
STAGE_CTVC = STAGING_ROOT / "ctvc"
STAGE_DOWNLOADS = STAGING_ROOT / "downloads"
REEL_CUT_CACHE = STAGING_ROOT / ".reelcuts"


# ==========================================
# ERSATZTV SERVER
# ==========================================
# Only the offline tools reach the server over HTTP — the scheduler itself
# runs inside it and talks to the API directly. Set ETV_URL, or set host and
# port separately if that reads better in your shell profile.

ERSATZTV_HOST = _text("ETV_HOST", "127.0.0.1")
ERSATZTV_PORT = _text("ETV_PORT", "8409")
ERSATZTV_URL = _text("ETV_URL", f"http://{ERSATZTV_HOST}:{ERSATZTV_PORT}")

XMLTV_URL = f"{ERSATZTV_URL}/iptv/xmltv.xml"
M3U_URL = f"{ERSATZTV_URL}/iptv/channels.m3u"


# ==========================================
# EXTERNAL TOOLS
# ==========================================
# The filler pipeline shells out to ffmpeg. Override if they are not on PATH.

FFMPEG = _text("ETV_FFMPEG", "ffmpeg")
FFPROBE = _text("ETV_FFPROBE", "ffprobe")

# The interpreter used for worker subprocesses. Defaults to the one running
# now, which is correct inside a virtualenv and needs no configuration.
PYTHON_BIN = _text("ETV_PYTHON", sys.executable)
