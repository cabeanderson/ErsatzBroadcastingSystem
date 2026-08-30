"""
Nickelodeon Content
===================
Two channels on one dial position: Nicktoons and the WB animation bench by
day, Nick at Nite from 21:00 to 02:00.

Nick's own eight animated shows cannot carry a full day on their own. The WB
trio (Animaniacs 197, Pinky 95, Tiny Toons 98) and the educational set are the
bench that keeps them from being ground down, and `monthly_rotation()` is what
puts that bench on the air -- the midday and afternoon strips each cycle four
pools, a month at a time, offset from each other so they never show the same
pool on the same day.

Avatar and Korra are the only serialized shows here, so they get the
weekday/weekend split: chronological Monday to Friday, shuffled at the weekend.
That is first-run and reruns, from one library.

Sharing rule: every title in the Nick at Nite blocks is also on Good Times
(scripts/channels/sitcoms.py), which airs them mornings and daytime and stays
clear of 21:00-02:00. See reference/channel-plan.md.
"""

from scripts.logic.structures import RandomCollection, OrderedCollection, Block
from scripts.logic.factories import monthly_rotation

# ==============================================================================
# 1. DAYTIME POOLS
# ==============================================================================

NICKTOONS_CLASSIC = Block(
    name="Nicktoons Classic",
    items=RandomCollection([
        {"title": "The Ren & Stimpy Show"},
        {"title": "Rocko's Modern Life"},
        {"title": "Aaahh!!! Real Monsters"},
        {"title": "The Wild Thornberrys"},
    ])
)

NICKTOONS_MODERN = Block(
    name="Nicktoons",
    items=RandomCollection([
        {"title": "SpongeBob SquarePants"},
        {"title": "Invader ZIM"},
        {"title": "Rocko's Modern Life"},
        {"title": "The Wild Thornberrys"},
    ])
)

# The bench. Tonally closer to Ren & Stimpy than to Disney Afternoon, which is
# why these three sit here rather than on the Disney channel.
WB_ANIMATION = Block(
    name="The WB Bench",
    items=RandomCollection([
        {"title": "Animaniacs"},
        {"title": "Pinky and the Brain"},
        {"title": "Tiny Toon Adventures"},
    ])
)

NICK_EDUCATIONAL = Block(
    name="Nick Learns",
    items=RandomCollection([
        {"title": "The Magic School Bus"},
        {"title": "Where on Earth is Carmen Sandiego"},
        {"title": "Schoolhouse Rock!"},
    ])
)

NICK_TEEN = Block(
    name="Teen Nick",
    items=RandomCollection([
        {"title": "Daria"},
        {"title": "Clarissa Explains It All"},
        {"title": "Invader ZIM"},
    ])
)

# ==============================================================================
# 2. THE MONTHLY BENCH
# ==============================================================================

# Four pools, one per month, cycling three times a year each. Four strips start
# the cycle at four different months, which exactly covers the cycle: on any
# given day the overnight, morning, midday and afternoon are showing four
# different pools, and next month they have all moved on one.
DAYTIME_POOLS = [
    NICKTOONS_CLASSIC,
    WB_ANIMATION,
    NICKTOONS_MODERN,
    NICK_EDUCATIONAL,
]

MIDDAY_BENCH = monthly_rotation(DAYTIME_POOLS)
AFTERNOON_BENCH = monthly_rotation(DAYTIME_POOLS, start_month=3)
OVERNIGHT_BENCH = monthly_rotation(DAYTIME_POOLS, start_month=2)
MORNING_BENCH = monthly_rotation(DAYTIME_POOLS, start_month=4)

# ==============================================================================
# 3. THE AVATAR STRIP
# ==============================================================================

# Two keys per show rather than one item played at two orders: an ErsatzTV
# content key carries its playback order, and a single key would be pinned to
# whichever order registered first in the build.
AVATAR_FIRST_RUN = Block(
    name="The Avatar Hour",
    items=OrderedCollection([
        "avatar_chronological_tv",
        "korra_chronological_tv",
    ])
)

AVATAR_RERUNS = Block(
    name="The Avatar Hour",
    items=OrderedCollection([
        "avatar_shuffle_tv",
        "korra_shuffle_tv",
    ])
)

# New episodes on weekdays, reruns at the weekend.
AVATAR_STRIP = {
    "WEEKDAY": AVATAR_FIRST_RUN,
    "default": AVATAR_RERUNS,
}

# ==============================================================================
# 4. NICK AT NITE (21:00 - 02:00)
# ==============================================================================

# 21:00-24:00 -- the marquee hours, everything pre-1970.
NICK_AT_NITE = Block(
    name="Nick at Nite",
    items=OrderedCollection([
        {"title": "I Love Lucy"},
        {"title": "The Dick Van Dyke Show"},
        {"title": "The Andy Griffith Show"},
        {"title": "Bewitched"},
        {"title": "I Dream of Jeannie"},
        {"title": "The Addams Family"},
        {"title": "Gilligan's Island"},
    ]),
    use_epg_group=False
)

# 00:00-02:00 -- the 70s shift. Sharper, later, and the half of the lineup
# Good Times gives up in exchange for keeping them in daylight.
NICK_AT_NITE_AFTER_HOURS = Block(
    name="Nick at Nite: After Hours",
    items=OrderedCollection([
        {"title": "The Mary Tyler Moore Show"},
        {"title": "The Bob Newhart Show"},
        {"title": "Taxi"},
        # The one title referenced by key: "M*A*S*H" tokenises to m/a/s/h and
        # will never match the library's "MASH", so the query lives in sources.
        "mash_tv",
        {"title": "Sanford and Son"},
        {"title": "Good Times"},
        {"title": "Soap"},
        {"title": "Mork & Mindy"},
        {"title": "The Smothers Brothers Comedy Hour"},
    ]),
    use_epg_group=False
)

# ==============================================================================
# 5. SNICK (Saturday, 19:00 - 21:00)
# ==============================================================================

# The one appointment on the channel that is not Nick at Nite: the Saturday
# night block, older-skewing than daytime and live-action-led.
SNICK = Block(
    name="SNICK",
    items=OrderedCollection([
        {"title": "Clarissa Explains It All"},
        {"title": "The Ren & Stimpy Show"},
        {"title": "Rocko's Modern Life"},
        {"title": "Daria"},
    ]),
    use_epg_group=False
)
