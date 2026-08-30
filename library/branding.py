"""
Branding Profiles
=================
Reusable branding configurations (intros, outros, bumpers).
"""

from scripts.logic.models import Branding

BRANDING_ADULT_SWIM = Branding(
    intro="adult_swim_intro",
    outro="adult_swim_outro",
    bumpers="adult_swim_bumpers",
)

# BRANDING_90S_KIDS was here. It named fox_kids_intro and fox_kids_bumper,
# neither of which is defined in sources.py, and filler/bumpers/fox kids/ is an
# empty tree on disk. Its only consumer was animation.FOX_KIDS_BLOCK, which
# nothing referenced. Both went in the Cartoon Network restructure.

BRANDING_TOONAMI = Branding(
    intro="toonami_intro",
    outro="toonami_outro",
    bumpers="toonami_bumpers",
)

BRANDING_TGIF = Branding(
    bumpers="commercials_90s_spot"
)