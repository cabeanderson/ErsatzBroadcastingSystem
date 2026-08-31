"""
Be Kind Rewind Content - the video store, 1980 to now

The largest pool on the lineup by a wide margin: 1,530 live-action films from
1980 on, which is a 122-day cycle at twenty-four hours a day. Cabes Classic
Cinema lives on 328 and High Noon on 46.

That size is the whole reason this channel can do something none of the others
can. Nightmare Theatre organizes by the clock because it has one genre; High
Noon organizes around a television spine because it has 946 episodes and 46
films. Be Kind Rewind has no single genre and no spine, so it organizes by the
**week** -- Friday is new releases, Saturday is the blockbuster, Sunday is the
drama, the small hours are the cult shelf. A viewer should be able to tell what
day it is from what is on.

It is a video store rather than a cinema. The shelves are the sub-genres, the
decade rotation is the back catalogue, and the Friday night wall is the only
thing on the lineup that promises something *recent*.

**Nothing here is exclusive.** An earlier plan proposed fencing 2018-and-later
off for this channel so the lineup could keep "zero shared film pools"; that
constraint was retired before it was built. Totally 80s keeps the whole of the
1980s, Other Worlds keeps science fiction, Mystery Theatre keeps modern crime
and Nightmare Theatre keeps horror, and this channel overlaps every one of
them. The rule is only that the same title must not air on two channels in the
same hour, and that is a grid problem -- see `channels/be_kind_rewind.py` for
the hours each neighbour occupies and which shelf answers it.

Two exclusions are made at the key rather than by hours, because Nightmare
Theatre and High Noon both draw *every* era of their genre and both run film in
this channel's prime: `NO_HORROR` and `NO_WESTERN` are on the wide keys. Every
other border is kept by the clock.
"""

from scripts.logic.structures import (
    RandomCollection, DailyOrderedCollection, MarathonSequence
)
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.models import Swap, Feather
from scripts.library.queries import movie_by_title_year


def _film(title, year):
    """A named, year-bounded film, in the {title, query} shape collections take."""
    return {"title": title, "query": movie_by_title_year(title, year)}


# ==============================================================================
# THE SHELVES -- one per slot
# ==============================================================================

# 00:00-02:00. Cult Corner. The video store's back wall: the oddities, the
# midnight movies, the films that found their audience on tape rather than in
# a cinema. `eighties_cult_movie` had been in the registry and on no channel.
CULT_CORNER = RandomCollection([
    "eighties_cult_movie",
    "modern_thriller_movie",
])
# The 1980s shelf is deliberately *not* here, though this is a night slot and
# the decade otherwise lives in the night slots. Mystery Theatre runs crime
# film 23:00-02:00 and nothing else, so 00:00-02:00 is the one nocturnal hour
# on this channel that is not free: `80s_pure_movie` against
# `modern_crime_movie` was eleven same-title airings a fortnight, the largest
# collision this channel introduced. The decade sits in The Overnight Bin
# (02:00-06:00, when Mystery Theatre has gone dark) and The Late Show instead.
#
# Which is the hours rule working at the granularity it is supposed to work at:
# not "this channel may not have the 1980s", but "not in these two hours".

# 02:00-06:00. The Overnight Bin -- the whole modern shelf, shuffled, no theme.
#
# This is also where the 1980s live on this channel. Totally 80s runs film from
# 10:00 to 23:00 and is dark from 23:00 to 10:00, so the decade the two
# channels genuinely share is scheduled here and in Cult Corner above, in hours
# the other channel is not broadcasting film at all. That is the hours rule
# doing the work an eviction would otherwise have done.
THE_OVERNIGHT_BIN = RandomCollection([
    "modern_cinema_movie",
    "80s_pure_movie",
    "90s_pure_movie",
])

# 06:00-09:00. The Morning Matinee. Family and PG -- the one part of the day
# the channel is safe for anyone. Disney and Cartoon Network both run animation
# in these hours and this key excludes it by construction (`movie_source`
# drops `genre:animation` unless asked), so the overlap is live-action family
# film against cartoons, which is not the same shelf.
MORNING_MATINEE = RandomCollection([
    "modern_family_movie",
    "family_pg_movie",
])

# 09:00-12:00. The Back Catalogue. Comedy and romance -- daytime television's
# actual register, and the two biggest genres in the library after drama.
THE_BACK_CATALOGUE = RandomCollection([
    "modern_comedy_movie",
    "modern_romance_movie",
])

# 12:00-15:00 and 15:00-18:00. The decade rotation, which is the back half of
# the video-store idea: a shelf per decade, rotated monthly rather than mixed,
# so the afternoon has a character that lasts long enough to notice.
#
# The 1980s are deliberately absent from both -- these hours are exactly when
# Totally 80s runs its own daytime and weekend film.
DECADE_AFTERNOON = ["90s_pure_movie", "00s_pure_movie", "10s_pure_movie", "20s_pure_movie"]

# The afternoon double, second half. Genre x decade rather than raw decade, so
# the two halves of the afternoon do not read as the same block twice.
AFTERNOON_DOUBLE = [
    "90s_action_movie", "00s_action_movie", "10s_action_movie",
    "90s_comedy_movie", "00s_comedy_movie", "10s_comedy_movie",
    "90s_drama_movie", "00s_drama_movie", "10s_drama_movie",
]

# 22:00-24:00. The Late Show. Where the channel gets sharper -- thrillers and
# the harder end of the action shelf, after the family and the appointment
# have both had their hours.
THE_LATE_SHOW = RandomCollection([
    "modern_thriller_movie",
    "modern_action_movie",
    "eighties_cult_movie",
    "80s_pure_movie",
])

# ==============================================================================
# PRIME -- 18:00-22:00, one identity per night
# ==============================================================================
#
# Prime starts at 18:00 rather than 20:00 on purpose. Simulating every channel
# over a fortnight and bucketing film by hour showed 18:00-20:00 is the
# clearest film real estate on the lineup: Nightmare Theatre, High Noon and
# Other Worlds are all running television then, and only Totally 80s has any
# film there at all. By 20:00, when four other channels start features, this
# channel's viewer is already an hour into one.

# FRIDAY. The appointment, and the channel's whole argument. 105 films from
# 2022 on, two features a Friday, which is a little over a year before a repeat.
# Nothing else on the lineup promises anything recent.
NEW_RELEASES = RandomCollection(["new_release_movie"])

# SATURDAY. Blockbuster night -- the franchise shelf and the action spine.
BLOCKBUSTER_NIGHT = RandomCollection([
    "blockbuster_action_movie",
    "modern_adventure_movie",
    "modern_action_movie",
])

# SUNDAY. The drama, which is what Sunday night is for everywhere else and is
# the one register the rest of this channel's week does not cover.
SUNDAY_FEATURE = RandomCollection([
    "modern_drama_movie",
    "90s_drama_movie",
])

# MONDAY. Comedy night.
COMEDY_NIGHT = RandomCollection([
    "modern_comedy_movie",
    "90s_comedy_movie",
    "00s_comedy_movie",
])

# WEDNESDAY. Recent, but not brand new -- the 2018+ shelf, which keeps a
# current film in prime midweek without spending the Friday pool.
RECENT_MIDWEEK = RandomCollection(["recent_movie"])

# ==============================================================================
# SPOTLIGHTS -- Tuesday is the director, Thursday is the star
# ==============================================================================
#
# The one thing a 1,530-film pool buys that no other channel on the lineup can
# afford. Every title below was checked against `reference/library-movies.tsv`
# and is year-bounded: `movie_by_title` is a phrase match, so a bare
# title:"Gladiator" also returns Gladiator II and title:"Predator" returns
# Predator 2.
#
# These are title lists rather than `director:` or `actor:` queries because
# nothing in this repo uses those fields, ERSATZTV_API.md does not document
# them, and whether the index carries them cannot be checked from the
# workstation. A list of titles known to be on disk cannot be wrong in the same
# way. If the fields do turn out to work, these become one-line queries.

SPIELBERG = RandomCollection([_film(t, y) for t, y in [
    ("E.T. The Extra-Terrestrial", 1982), ("Indiana Jones and the Temple of Doom", 1984),
    ("Empire of the Sun", 1987), ("Indiana Jones and the Last Crusade", 1989),
    ("Hook", 1991), ("Jurassic Park", 1993), ("Schindler's List", 1993),
    ("Saving Private Ryan", 1998), ("A.I. Artificial Intelligence", 2001),
    ("Minority Report", 2002), ("Catch Me If You Can", 2002), ("Ready Player One", 2018),
]])

COEN_BROTHERS = RandomCollection([_film(t, y) for t, y in [
    ("Blood Simple", 1984), ("Raising Arizona", 1987), ("Miller's Crossing", 1990),
    ("Barton Fink", 1991), ("Fargo", 1996), ("No Country for Old Men", 2007),
    ("Burn After Reading", 2008), ("A Serious Man", 2009), ("True Grit", 2010),
    ("Inside Llewyn Davis", 2013), ("Hail, Caesar!", 2016),
]])

TARANTINO = RandomCollection([_film(t, y) for t, y in [
    ("Reservoir Dogs", 1992), ("Pulp Fiction", 1994), ("Jackie Brown", 1997),
    ("Inglourious Basterds", 2009), ("Django Unchained", 2012),
    ("Once Upon a Time in Hollywood", 2019),
]])

SCORSESE = RandomCollection([_film(t, y) for t, y in [
    ("Raging Bull", 1980), ("Goodfellas", 1990), ("Cape Fear", 1991),
    ("Casino", 1995), ("Gangs of New York", 2002), ("Shutter Island", 2010),
    ("Hugo", 2011), ("Silence", 2016), ("Killers of the Flower Moon", 2023),
]])

RIDLEY_SCOTT = RandomCollection([_film(t, y) for t, y in [
    ("Blade Runner", 1982), ("Legend", 1985), ("Thelma & Louise", 1991),
    ("Gladiator", 2000), ("Black Hawk Down", 2001), ("Matchstick Men", 2003),
    ("Kingdom of Heaven", 2005), ("American Gangster", 2007), ("Prometheus", 2012),
]])

NOLAN = RandomCollection([_film(t, y) for t, y in [
    ("Memento", 2000), ("Insomnia", 2002), ("Batman Begins", 2005),
    ("Inception", 2010), ("Interstellar", 2014), ("Dunkirk", 2017),
    ("Tenet", 2020), ("Oppenheimer", 2023),
]])

FINCHER = RandomCollection([_film(t, y) for t, y in [
    ("Se7en", 1995), ("Fight Club", 1999), ("Panic Room", 2002),
    ("Zodiac", 2007), ("Gone Girl", 2014),
]])

# John Carpenter's post-1980 run. Halloween and Assault on Precinct 13 are on
# disk but pre-1980 and horror -- Nightmare Theatre's, not this channel's.
CARPENTER = RandomCollection([_film(t, y) for t, y in [
    ("Escape from New York", 1981), ("Christine", 1983), ("Starman", 1984),
    ("Big Trouble in Little China", 1986), ("They Live", 1988),
    ("In the Mouth of Madness", 1995),
]])

DIRECTORS_CHAIR = [
    SPIELBERG, COEN_BROTHERS, TARANTINO, SCORSESE,
    RIDLEY_SCOTT, NOLAN, FINCHER, CARPENTER,
]

SCHWARZENEGGER = RandomCollection([_film(t, y) for t, y in [
    ("Conan the Barbarian", 1982), ("Commando", 1985), ("Predator", 1987),
    ("Twins", 1988), ("Total Recall", 1990), ("Kindergarten Cop", 1990),
    ("Last Action Hero", 1993), ("True Lies", 1994), ("Jingle All the Way", 1996),
]])

BILL_MURRAY = RandomCollection([_film(t, y) for t, y in [
    ("Caddyshack", 1980), ("Ghostbusters", 1984), ("Scrooged", 1988),
    ("Ghostbusters II", 1989), ("Groundhog Day", 1993), ("Ed Wood", 1994),
    ("Rushmore", 1998), ("Lost in Translation", 2003), ("Zombieland", 2009),
]])

SIGOURNEY_WEAVER = RandomCollection([_film(t, y) for t, y in [
    ("Ghostbusters", 1984), ("Aliens", 1986), ("Working Girl", 1988),
    ("Ghostbusters II", 1989), ("Alien Resurrection", 1997),
    ("Galaxy Quest", 1999), ("Avatar", 2009),
]])

DENZEL_WASHINGTON = RandomCollection([_film(t, y) for t, y in [
    ("Glory", 1989), ("Malcolm X", 1992), ("Philadelphia", 1993),
    ("Training Day", 2001), ("Inside Man", 2006), ("American Gangster", 2007),
]])

STAR_OF_THE_MONTH = [
    SCHWARZENEGGER, BILL_MURRAY, SIGOURNEY_WEAVER, DENZEL_WASHINGTON,
]

# ==============================================================================
# BLOCKS -- seasonal treatments
# ==============================================================================

# Summer is blockbuster season and autumn is thriller season. This is the swap
# Cabes Classic Cinema used to run on `MODERN_BLOCKBUSTERS` every summer, on
# the channel it always belonged to.
SATURDAY_PRIME = SeasonalBlock(
    base=BLOCKBUSTER_NIGHT,
    seasonal={
        "SUMMER": Feather("blockbuster_action_movie", 0.5),
        "FALL":   Feather("modern_thriller_movie", 0.4),
    },
    auto_tag=True
)

# ==============================================================================
# HOLIDAY EVENTS
# ==============================================================================

HALLOWEEN_EVENT = RandomCollection([
    "halloween_modern_movie",
    "halloween_90s_movie",
    "halloween_comedy_movie",
])

CHRISTMAS_EVENT = RandomCollection([
    "christmas_modern_movie",
    "christmas_90s_movie",
    "christmas_80s_movie",
    "christmas_family_movie",
])

# Christmas Eve, 18:00-24:00. Die Hard is on disk and this is the argument the
# channel is built to have.
CHRISTMAS_EVE_FEATURE = DailyOrderedCollection([
    _film("Die Hard", 1988),
    _film("Gremlins", 1984),
])
