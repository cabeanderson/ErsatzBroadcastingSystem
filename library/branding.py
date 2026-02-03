"""
Branding Profiles
=================
Reusable branding configurations (intros, outros, bumpers).
"""

from scripts.logic.models import Branding

BRANDING_ADULT_SWIM = Branding(
    intro="adult_swim_intro",
    bumpers="adult_swim_bumpers",
)

BRANDING_90S_KIDS = Branding(
    intro="fox_kids_intro",
    outro="fox_kids_bumper", # Reusing bumper as outro if specific outro missing
    bumpers="fox_kids_bumper",
)

BRANDING_TOONAMI = Branding(
    intro="toonami_intro",
    outro="toonami_outro",
    bumpers="toonami_bumpers",
)

BRANDING_TGIF = Branding(
    bumpers="commercials_90s_spot"
)