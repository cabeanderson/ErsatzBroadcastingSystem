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
from scripts.logic.models import Swap, Fallback

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

# The weekend takes a different four. It was written to work around a hole on
# the *other* channel -- Good Times declared no `evening` at the weekend, so its
# 17:00-20:00 fell through to a fallback holding Cheers, The Wonder Years,
# Married... with Children and Coach. That hole was closed in the Good Times
# rebuild (2026-09-01): all seven days now declare all ten slots.
#
# The split is kept, and is now load-bearing in the other direction. Good Times
# reads these two arms as *different* rules -- Married... with Children is clear
# at the weekend and takes its Sunday 17:00 strip, while Murphy Brown and
# Roseanne are clear on a weekday and take its Monday and Wednesday primes.
# Changing either arm moves a title on that channel.
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
    "golden_girls_tv",
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
    "night_court_tv",
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

# 04:00-06:00. The videos, and only two hours of them.
#
# This key held 00:00-06:00 until 2026-09-02 and matched *nothing*: it was
# `type:"music_video" AND year:[1980 TO 1989]` against a music video library
# with no year metadata on any of its 303 files, so the channel simply went dark
# from midnight to six. The library was reorganised that day -- every file now
# carries a Kodi .nfo with a real <year>, and the folder above each one is the
# artist rather than a genre bucket -- and the honest size of the pool is 35
# videos over 1975-1989, about 152 minutes. Two hours is what that fills without
# repeating; six was never available.
#
# !! The key still selects nothing (verified 2026-09-07 on a reset playout --
# Totally 80s airs no music videos at all). The slot is carried by the block's
# fallback, which is why the guide looks continuous. Reorganising the library
# fixed the metadata and did not fix the query. See KNOWN_ISSUES, 2026-09-07.
LATE_NIGHT_MUSIC = "eighties_music_videos"

# 00:00-04:00. The four hours the video block gave back.
#
# Action and drama reruns are what an 80s independent actually ran overnight,
# and both keys belong to this channel alone -- `eighties_crime_tv` is
# deliberately absent because Mystery Theatre draws it too (KNOWN_ISSUES), and
# `in_living_color_tv` because Good Times holds it.
LATE_NIGHT_TV = RandomCollection([
    "eighties_action_tv",
    "eighties_drama_tv",
])


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
    # `gap` here was the last deliberate dead air in the lineup, and the only
    # `fill_strategy="gap"` anywhere in it: prime is 20:00-23:00 and a
    # blockbuster is under two hours, so every Friday ended with roughly an hour
    # of unscheduled time. It survived the 2026-09-02 playout reset because it
    # was never stale config -- it was the design. Bridging hands the tail to
    # The Sketch Hour, which is the 23:00 slot anyway, so Friday simply gets to
    # its sketch comedy early.
    fill_strategy="bridge"
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

# 04:00-06:00. `yield`, not `bridge`, and the difference is measurable: bridging
# leaves two minutes of dead air at 05:58 every single day. A music video is
# three to five minutes, `pad_until_exact` places only whole items, and the
# bridge's trailing fill falls through to a bare wait when nothing fits -- so
# the tail the bridge is meant to close is exactly the tail it cannot. Yielding
# hands 05:58 to the Runner, which starts the cartoons early instead.
#
# `Fallback`, because a two-hour slot whose only content is a single query is
# exactly as reliable as that query -- and this one was empty for months without
# anything noticing. `play_with_fallback` switches on *time not advancing*, which
# is precisely what an ErsatzTV search matching nothing produces, so the block
# degrades to late-night television instead of going dark. Verified by
# simulating the key as missing: 120 minutes of dead air a day becomes none.
#
# The secondary is a bare key and must stay one. `play_with_fallback` hands it
# straight to `play_item`, which does not resolve wrappers -- a Collection here
# is stringified into "<RandomCollection object at 0x...>", matches nothing, and
# still reports success. That is the same trap `dispatcher.resolve_fallback_key`
# documents for `fallback_content`, and it is silent in exactly the way this
# whole defect was.
VIDEO_JUKEBOX_BLOCK = Block(
    name="The Video Jukebox",
    items=[Fallback(primary=LATE_NIGHT_MUSIC, secondary="eighties_action_tv")],
)

LATE_NIGHT_TV_BLOCK = Block(
    name="After Hours",
    items=LATE_NIGHT_TV,
    fill_strategy="bridge",
)

