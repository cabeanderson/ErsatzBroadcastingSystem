"""
Cabes Classic Cinema - Hollywood before the blockbuster, 1920-1979

The channel had been edited five times and never designed. Modern film went
first, then science fiction to Other Worlds, westerns to High Noon, horror to
Nightmare Theatre, and the crime shelf was cut in half for Mystery Theatre.
Each edit was correct on its own and none of them ever said what was left.

This says it: **Classic Cinema is everything before 1980.** 328 live-action
films, a 25-day cycle at twenty-four hours a day.

The line matters more than the number. It is the same boundary Be Kind Rewind
starts at, so between them the two film channels cover the whole library and
**no title can ever appear on both** -- the cleanest relationship two channels
on this lineup have. It is also the line `classic_crime_movie` and
`modern_crime_movie` were already split along for Mystery Theatre, so nothing
had to be re-cut to draw it.

What it cost: the 1980s. `80s_pure_movie` was this channel's weekday prime and
a byte-identical copy of Totally 80s' `eighties_daytime_movie` /
`eighties_weekend_movie` -- 229 films drawn by two channels in the same
18:00-23:00 hours, the likeliest same-title collision on the lineup and the
open question `movies.py` used to defer to "the full grid pass". The decade is
Totally 80s' theme now, and Be Kind Rewind's oldest shelf.

The grid walks forward through film history as the day goes on -- silents at
breakfast, the Golden Age at mid-morning, CinemaScope in the afternoon, New
Hollywood at night -- and resets into noir after midnight. That is the channel's
whole organizing idea, and it is why it carries its own timeslot map rather
than the four six-hour blocks of the "movies" preset, which is what let it go
shapeless in the first place.
"""

from scripts.logic.structures import RandomCollection, WeightedCollection
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.library.queries import movie_by_title_year
from scripts.logic.models import Swap, Feather

# ==============================================================================
# COLLECTIONS -- one per hour of the day
# ==============================================================================

# 00:00-03:00. Noir Alley. `classic_noir_movie` alone is thirteen films, so the
# block leans on the wider pre-1980 crime shelf and lets noir concentrate it.
#
# Mystery Theatre runs `modern_crime_movie` in the same hours and the collision
# report flags the pair as SAME GENRE every night. It is not a same-title risk
# and does not need fixing: the two keys were split at 1980 precisely so neither
# channel can draw the other's film. A viewer flipping between them sees crime
# twice, which is the cost of two channels that both have a claim on it.
NOIR_ALLEY = RandomCollection(["classic_noir_movie", "classic_crime_movie"])

# 03:00-06:00. The Small Hours -- the whole pre-1980 shelf, shuffled, no theme.
# Every channel on the lineup needs one slot that is just the library; this is
# the equivalent of High Noon's The Long Ride and Nightmare Theatre's Insomnia.
THE_SMALL_HOURS = RandomCollection(["classic_cinema_movie"])

# 06:00-09:00. First Reel -- silents over early sound.
#
# Weighted, not random, and this is the one block on the channel that had to be.
# There are **thirteen** silent features on disk against 36 in the Golden Age
# key, and an even split put a silent film on at breakfast every other day: the
# first cut of this grid aired the same thirteen titles 379 times in a year,
# once every nine days each. Weighting them to a quarter of the block gives
# each about twelve airings a year, which is roughly a month apart and is what
# a scarce, distinctive pool should feel like.
#
# WeightedCollection had been in `logic/structures.py` since the beginning and
# no channel had ever used it. This is its first consumer.
SILENT_CINEMA = WeightedCollection([
    ("20s_silent_movie", 0.25),
    ("golden_age_pure_movie", 0.75),
])

# 09:00-12:00. The studio system, 1930-69 -- where the morning hands over to
# the afternoon's era.
#
# It draws the Golden Age *and* the classic era on purpose. An earlier cut had
# this block and First Reel above drawing the same two keys in a different
# order, which is six hours a day against a 49-film pool -- a repeat inside a
# fortnight, and invisible until the airings were counted per key rather than
# per block. Two blocks are only two blocks if they draw different things.
GOLDEN_AGE_CINEMA = RandomCollection([
    "golden_age_pure_movie",
    "classic_hollywood_pure_movie",
])

# 12:00-17:00. The Matinee -- 1950-69, the channel's widest block and its
# centre of gravity. 99 films across five hours.
MATINEE = RandomCollection(["classic_hollywood_pure_movie"])

# 17:00-20:00. The Big Picture. The prestige hours before prime, on the
# widescreen material -- Lawrence of Arabia, The Great Escape, Bridge on the
# River Kwai -- with the war and musical shelves blended in. This is the
# clearest film real estate on the whole lineup: at 18:00-20:00 Nightmare
# Theatre, High Noon and Other Worlds are all running television.
# Weighted for the same reason First Reel is: the pre-1980 musical shelf is
# **six films**. An even three-way split gave those six a third of a nightly
# three-hour block -- 90 airings a year, fifteen apiece. At a tenth they land
# about once a month, which is what a musical on a classic channel should be.
#
# Six is also the finding worth keeping: `MUSICAL_MARQUEE` used to be handed
# this slot on the unbounded `musical_movie` key, which reaches every era. It
# looked like a 24-film pool and it was six films and eighteen of Be Kind
# Rewind's.
THE_BIG_PICTURE = WeightedCollection([
    ("classic_epic_movie", 0.55),
    ("classic_war_movie", 0.35),
    ("classic_musical_movie", 0.10),
])

# 20:00-24:00. New Hollywood, and the only slot on the channel that is a single
# decade. 114 films across four hours a night is a seven-week cycle.
#
# Westerns are excluded at the key rather than shared: High Noon runs film
# 20:00-24:00 too, and these are exactly the years -- Butch Cassidy, The Wild
# Bunch, Jeremiah Johnson -- where the two channels would otherwise collide on
# a title. Horror was already out for Nightmare Theatre.
NEW_HOLLYWOOD = RandomCollection(["70s_prestige_movie"])

def _film(title, year):
    """A named, year-bounded film, in the {title, query} shape collections take."""
    return {"title": title, "query": movie_by_title_year(title, year)}


# ==============================================================================
# SPOTLIGHTS -- the occasional highlight, built from titles that are on disk
# ==============================================================================
#
# Genre and era keys give the channel its shape; a spotlight gives it an event.
# These are title lists rather than `director:` queries on purpose -- nothing in
# the repo uses a director or actor field, ERSATZTV_API.md does not document
# one, and it cannot be verified from the workstation. Every title below was
# checked against `reference/library-movies.tsv`.

# Twelve Hitchcocks on disk and every one of them pre-1980, which makes him this
# channel's director outright -- Be Kind Rewind cannot reach a single one.
# Psycho is year-bounded because a bare title:"Psycho" also returns American
# Psycho and Seven Psychopaths; the rest are bounded for consistency.
HITCHCOCK_SPOTLIGHT = RandomCollection([_film(t, y) for t, y in [
    ("Rebecca", 1940), ("Shadow of a Doubt", 1943), ("Notorious", 1946),
    ("Rope", 1948), ("Strangers on a Train", 1951), ("Dial M for Murder", 1954),
    ("Rear Window", 1954), ("To Catch a Thief", 1955), ("Vertigo", 1958),
    ("North by Northwest", 1959), ("Psycho", 1960), ("Frenzy", 1972),
]])

# Four of the six Kubricks on disk are pre-1980. Full Metal Jacket and Eyes Wide
# Shut are Be Kind Rewind's -- the one director the era line genuinely splits,
# which is what a line drawn through a career looks like and is not a defect.
KUBRICK_SPOTLIGHT = RandomCollection([_film(t, y) for t, y in [
    ("Paths of Glory", 1957), ("Spartacus", 1960),
    ("Dr. Strangelove", 1964), ("Barry Lyndon", 1975),
]])

DIRECTORS_CHAIR = {
    "HITCHCOCK": HITCHCOCK_SPOTLIGHT,
    "KUBRICK": KUBRICK_SPOTLIGHT,
}

# ==============================================================================
# BLOCKS -- seasonal treatments
# ==============================================================================

# The Matinee is where the four `classic_hollywood_*_movies` seasonal keys
# actually earn their place. They only Feather on top; the base is the era
# itself so five hours is never thin.
MATINEE_BLOCK = SeasonalBlock(
    base="classic_hollywood_pure_movie",
    seasonal={
        "WINTER": Feather("classic_hollywood_winter_movies", 0.5),
        "SPRING": Feather("classic_hollywood_spring_movies", 0.5),
        "SUMMER": Feather("classic_hollywood_summer_movies", 0.5),
        "FALL":   Feather("classic_hollywood_fall_movies", 0.5),
    },
    auto_tag=True
)

# Prime. Autumn hands the 1970s over to noir -- the one season swap the channel
# keeps, and the only one that ever suited it. The old SUMMER swap to modern
# blockbusters is long gone; that pool founded Be Kind Rewind.
PRIME_BLOCK = SeasonalBlock(
    base=NEW_HOLLYWOOD,
    seasonal={
        "FALL": Swap(NOIR_ALLEY),
        "WINTER": Feather("classic_hollywood_winter_movies", 0.4),
    },
    auto_tag=True
)

# Weekend prime. Deliberately not the weekday block: Sunday night on a classic
# channel should be the big canvas, not another 1970s feature.
WEEKEND_MARQUEE = RandomCollection([
    "classic_epic_movie",
    "classic_war_movie",
    "classic_musical_movie",
    "70s_prestige_movie",
])

# ==============================================================================
# HOLIDAY EVENTS
# ==============================================================================

HALLOWEEN_MARATHON_EVENT = RandomCollection([
    "halloween_classic_movie",
    "halloween_all_movie",
])

CHRISTMAS_FESTIVAL_EVENT = RandomCollection([
    "christmas_classic_movie",
    "christmas_all_movie",
    "christmas_family_movie",
])
