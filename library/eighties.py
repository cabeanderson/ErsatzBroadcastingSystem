"""
Totally 80s -- content

The 1980s as broadcast: cartoons at breakfast, a wheel through the daytime, a
named night in prime, and the decade's own late night after it.

Two things constrain everything below.

**The hours contract with Be Kind Rewind.** `library/modern_movies.py` states
it from the other side: the 1980s film shelf is Totally 80s' by day and Be Kind
Rewind's between 22:00 and 06:00. Be Kind Rewind keeps the decade out of its
12:00-18:00 afternoon for exactly this reason, and holds `eighties_cult_movie`
and `80s_pure_movie` in Cult Corner (00:00-02:00) and The Late Show
(22:00-24:00). So this channel's cult shelf sits at noon rather than at
midnight -- the slot a cult movie wants is the one slot it cannot have.

The contract is not quite clean, and it was not clean before this pass either:
Friday and Sunday prime are films and prime runs to 23:00, so 22:00-23:00 on
those two nights has 1980s film on both channels. That hour predates this
design -- prime used to run 17:00-23:00, so it was the same overlapping hour
behind three more hours of lead-in -- and closing it means moving Be Kind
Rewind's Late Show or splitting this channel's prime, neither of which belongs
in an 80s-channel pass. Recorded in KNOWN_ISSUES.md.

**Good Times owns most of the decade's sitcoms at some hour.** Where a show is
shared, it is placed in an hour Good Times is not airing it: Cheers is
Thursday prime here and 23:00-02:00 there; Perfect Strangers is the morning
here and Friday's TGIF there; Family Matters, Married... with Children, Full
House and The Wonder Years all sit in the 17:00-20:00 strip, which Good Times
gives to its 1990s lineup.
"""

from scripts.logic.structures import RandomCollection, OrderedCollection, Block
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.models import Swap

# ==============================================================================
# 1. COLLECTIONS
# ==============================================================================

# --- MORNING ---

# Pee-wee's Playhouse is live action among four cartoons on purpose: it is the
# Saturday-morning register itself, and it was on disk with no registry key at
# all until 2026-09-01.
MORNING_CARTOONS = RandomCollection([
    "eighties_cartoons_heman",
    "eighties_cartoons_transformers",
    "eighties_cartoons_smurfs",
    "eighties_cartoons_thundercats",
    "pee_wee_playhouse_tv",
])

# The fall/winter morning, when the cartoons give way to sitcom reruns.
#
# Full House and Family Matters are deliberately *not* here. Good Times gives
# its weekend 06:00-10:00 to NINETIES_FAMILY, which holds both, so either one
# in this slot is the same title on two channels in the same hour -- the one
# hard rule. They are in the 17:00-20:00 strip instead.
MORNING_SITCOMS = RandomCollection([
    "saved_by_the_bell_tv",
    "perfect_strangers_tv",
    "coach_tv",
])

# --- DAYTIME ---
DAYTIME_GENRE_WHEEL = RandomCollection([
    "eighties_action_tv",      # e.g., The A-Team, MacGyver
    "eighties_drama_tv",       # e.g., Hill Street Blues, St. Elsewhere
    "eighties_daytime_movie"   # A random 80s movie
])

FALL_WINTER_DAYTIME_WHEEL = RandomCollection([
    "eighties_crime_tv",       # e.g., Miami Vice, Magnum P.I.
    "eighties_drama_tv",       # More drama focus
    "eighties_suspense_movie"  # Different movie genre
])

# --- EVENING STRIP (17:00-20:00) ---

# The after-school syndication hour, and the reason prime is three hours rather
# than six. Every title here is shared with Good Times at a different hour; see
# the module docstring.
EVENING_SYNDICATION = RandomCollection([
    "family_matters_tv",
    "married_children_tv",
    "wonder_years_tv",
    "full_house_tv",
])

# The weekend takes a different four, and the reason is a hole on the *other*
# channel: Good Times declares no `evening` in its WEEKEND schedule, so its
# 17:00-20:00 falls through to `fallback_content`, which is
# `sitcoms.LATE_NIGHT_SYNDICATION` -- Cheers, The Wonder Years, Married... with
# Children and Coach. Those four are unreachable here on Saturday and Sunday
# however clear the declared grid looks, and the weekday strip above collided
# with exactly two of them until this split. Murphy Brown and Roseanne are
# claimed by no other channel at any hour; they are Tuesday's prime here, which
# is a different day rather than a second airing.
WEEKEND_EVENING = RandomCollection([
    "family_matters_tv",
    "full_house_tv",
    "murphy_brown_tv",
    "roseanne_tv",
])

# --- PRIME TIME COLLECTIONS ---

# Knight Rider is 86 episodes against The A-Team's 13 and Street Hawk's 15, so
# the two short ones cycle fast -- acceptable for a weekly appointment, which
# sees three items a night, not a strip. Airwolf was the second name here and is
# not on disk; see reference/acquisitions.md.
ACTION_NIGHT_COLLECTION = OrderedCollection([
    "knight_rider_tv",
    "eighties_action_a_team",
    {"title": "Street Hawk", "order": "Chronological"},
])

# Tuesday, and none of the three is claimed by another channel at any hour.
# Roseanne aired Tuesdays on ABC, which is the night it has here.
COMEDY_GOLD_COLLECTION = OrderedCollection([
    "roseanne_tv",
    "murphy_brown_tv",
    "eighties_sitcom_golden_girls",
])

PI_WEDNESDAY_COLLECTION = OrderedCollection([
    "eighties_crime_miami_vice",
    "eighties_crime_magnum_pi",
])

# NBC Thursday, and the two of the four real Must See TV shows that are on
# disk. The Cosby Show and Family Ties are the other two and neither is in the
# library, which is what left this night as Cheers alone for as long as the
# channel has existed.
MUST_SEE_TV_COLLECTION = OrderedCollection([
    "cheers_tv",
    "eighties_sitcom_night_court",
])

# V was the second name here and is not on disk. Quantum Leap is the
# replacement: NBC, 1989, and Other Worlds airs it only 06:00-08:00 on
# Mon/Wed/Fri, so Saturday prime is clear.
SCIFI_SATURDAY_COLLECTION = OrderedCollection([
    "eighties_scifi_star_trek",
    "eighties_scifi_quantum_leap",
])

# --- LATE NIGHT ---

# 23:00-24:00. The decade's late-night register, which the channel had none of:
# acquisitions.md asks for SCTV and Letterman and neither is on disk, but The
# Kids in the Hall (1989) and In Living Color (1990) both are, and both were
# unregistered until 2026-09-01.
# Police Squad! is six episodes, which is too thin to carry a daytime strip and
# exactly right here: a 1982 cult half-hour among two sketch shows, once a night.
SKETCH_HOUR = RandomCollection([
    "kids_in_the_hall_tv",
    "in_living_color_tv",
    "police_squad_tv",
])

LATE_NIGHT_MUSIC = "eighties_music_videos"


# ==============================================================================
# 2. BLOCKS
# ==============================================================================

# 12:00-14:00. The cult shelf, at noon rather than at midnight.
#
# `eighties_cult_movie` is Be Kind Rewind's between 22:00 and 06:00 -- Cult
# Corner and The Late Show both draw it -- so a midnight cult slot here would
# be the same pool on two channels in the same hour. These are the hours Be
# Kind Rewind holds open for this channel by keeping the 1980s out of its own
# 12:00-18:00 afternoon.
CULT_MATINEE_BLOCK = Block(
    name="The Cult Matinee",
    items=["eighties_cult_movie"],
    fill_strategy="bridge",
    strict_window=False,
)

# --- PRIME TIME BLOCKS ---

ACTION_NIGHT_BLOCK = Block(
    name="Action Night",
    items=ACTION_NIGHT_COLLECTION,
    commercial_duration=120,
    commercials="commercials_80s_spot"
)

COMEDY_GOLD_BLOCK = Block(
    name="Comedy Gold",
    items=COMEDY_GOLD_COLLECTION,
)

PI_WEDNESDAY_BLOCK = Block(
    name="P.I. Wednesday",
    items=PI_WEDNESDAY_COLLECTION,
)

MUST_SEE_TV_BLOCK = Block(
    name="Must See TV",
    items=MUST_SEE_TV_COLLECTION,
)

FRIDAY_NIGHT_MOVIES_BLOCK = Block(
    name="Friday Night Movies",
    items=["eighties_blockbuster_movie"],
    intro="movie_intro_bumper",
    fill_strategy="gap" # Leave dead air if movie ends early
)

SCIFI_SATURDAY_BLOCK = Block(
    name="Sci-Fi Saturday",
    items=SCIFI_SATURDAY_COLLECTION,
)

SKETCH_HOUR_BLOCK = Block(
    name="The Sketch Hour",
    items=SKETCH_HOUR,
)

# Prime is 20:00-23:00 only. It used to be handed to both `evening` and `prime`,
# which ran the same Block object over 17:00-23:00 -- six hours of a two-item
# collection, and the reason Monday read as Knight Rider on a loop even before
# Airwolf turned out to be missing. The 17:00-20:00 hours are EVENING_SYNDICATION.
PRIME_TIME_BLOCKS = {
    "MONDAY": ACTION_NIGHT_BLOCK,
    "TUESDAY": COMEDY_GOLD_BLOCK,
    "WEDNESDAY": PI_WEDNESDAY_BLOCK,
    "THURSDAY": MUST_SEE_TV_BLOCK,
    "FRIDAY": FRIDAY_NIGHT_MOVIES_BLOCK,
    "SATURDAY": SCIFI_SATURDAY_BLOCK,
    "SUNDAY": "eighties_drama_movie"
}

# --- SEASONAL BLOCKS ---

# The swap is the school year: cartoons through spring and summer, sitcom
# reruns once the audience is back at school. 06:00-08:00 keeps the cartoons
# either way -- the old block swapped the only cartoon slot on the channel out
# for six months of the year.
SEASONAL_MORNING_BLOCK = SeasonalBlock(
    base=MORNING_CARTOONS, # Spring/Summer default
    seasonal={
        "FALL": Swap(MORNING_SITCOMS),
        "WINTER": Swap(MORNING_SITCOMS)
    }
)

SEASONAL_DAYTIME_BLOCK = SeasonalBlock(
    base=DAYTIME_GENRE_WHEEL, # Spring/Summer default
    seasonal={
        "FALL": Swap(FALL_WINTER_DAYTIME_WHEEL),
        "WINTER": Swap(FALL_WINTER_DAYTIME_WHEEL)
    }
)

# --- DEFAULT ASSIGNMENTS ---
MORNING_BLOCK = SEASONAL_MORNING_BLOCK
DAYTIME_BLOCK = SEASONAL_DAYTIME_BLOCK
LATE_NIGHT_BLOCK = LATE_NIGHT_MUSIC
