"""
Nightmare Theatre Content - Horror

The inverse of High Noon, and it has to be.

High Noon is a television channel with a film shelf: 946 episodes of black-and-
white network western carry fifteen hours a day and 46 films fill the rest.
Horror in this library is the other way round -- 242 films against roughly 370
usable episodes -- so Nightmare Theatre is a film channel with a television
spine. Seventeen hours of feature, seven of TV.

There is no classic horror television here at all. Nothing before 1989, and the
one 1989 show is Tales from the Crypt, which the library tags Comedy, Crime,
Mystery and Science Fiction and never Horror. The strip that would be the
obvious spine -- a black-and-white anthology in the Twilight Zone position --
does not exist and cannot be built. Two shows are strip-safe:

- **Tales from the Crypt** -- 93 episodes, 7 seasons, half-hours, an anthology
  with a host. The single best asset on the channel and the closest thing it
  has to an identity in television form. Reached by title only.
- **Poltergeist: The Legacy** -- 87 episodes, 4 seasons, hour-long, episodic,
  strictly tune-in.

That is 180 episodes. At an hour of Crypt and two of Legacy a night both cycle
in a little over six weeks, which is the budget the grid was built around; any
more airtime and they burn through in a fortnight.

Everything else that survives is serialized and can only be an appointment.

Three shows carrying a Horror genre tag are deliberately absent, because other
channels anchor on them: **The X-Files** and **Beyond Belief: Fact or Fiction**
(Other Worlds) and **Millennium** (Mystery Theatre). `horror_tv` reaches all
three, which is why nothing here uses it -- see the note on `horror_tv` and
the exclusion clause on `classic_horror_tv` in `sources.py`.

Episode counts are counted off disk. `reference/library-tv.tsv` overstates
Lovecraft Country by 15 (25 against 10 real) and Darkplace by 7 (13 against 6),
the same `extras/` overcount that inflated Justified and Deadwood.
"""

from scripts.logic.structures import (
    RandomCollection, OrderedCollection, DailyOrderedCollection, Block,
    MarathonSequence
)
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.models import Feather
from scripts.library.queries import show_by_title, movie_by_title
from scripts.logic.factories import annual_show

# ==============================================================================
# THE FILM -- 242 features, and the reason the grid looks the way it does
# ==============================================================================
#
# The channel's organizing axis is the clock, not the era: it gets darker as
# the night goes on. Morning is monster movies, midday draws the whole shelf,
# the name block at 22:00 is the 1980s, and the hard modern material is walled
# off in the hours after it. A horror channel that runs a slasher at nine in
# the morning has no idea what it is.
#
# Airtime was budgeted against pool size so nothing cycles faster than about
# three weeks: classic 39 films / 3h a day, eighties 50 / 2h, modern 102 / 6h,
# the whole shelf 191 / 5h.

# 06:00-09:00. The softest horror in the library and the only daylight the
# channel gets: Godzilla, King Kong, The Blob, giant bugs, wolfmen. A blend
# rather than a straight era key because the tag pools underneath it are small
# -- kaiju and werewolf are a handful of films each -- and `classic_horror_movie`
# is what keeps the block from repeating inside a week.
CREATURE_FEATURE = RandomCollection([
    "horror_kaiju_movie",
    "horror_werewolf_movie",
    "horror_aliens_movie",
    "classic_horror_movie",
])

# 09:00-12:00. The pre-1980 shelf on its own -- Nosferatu, Frankenstein, Freaks,
# Psycho, The Birds, Night of the Living Dead, Rosemary's Baby, The Exorcist,
# The Wicker Man, Texas Chain Saw, Jaws, Suspiria, Halloween, Alien. 39 films
# across three hours a day is a three-week cycle, which is as thin as this
# channel lets a pool run.
THE_VAULT = RandomCollection(["classic_horror_movie"])

# 12:00-17:00, the widest block on the channel and the one place every era runs
# against each other on purpose -- 1931 Frankenstein into 2018 Hereditary. The
# seasonal keys only Feather on top; the base is the whole shelf so five hours
# is never thin. FALL is horror's own season and gets the heavier ratio.
# The seasonal arms are era lifts, not holiday ones. `halloween_all_movie` was
# here at 0.6 and it was wrong twice over: FALL is the meteorological season, so
# a Halloween pool ran the whole of September and November as well as October,
# and `enable_holiday_injection` was already ramping the same tag from 41% to
# 86% across late October on its own. The injection is date-proximity weighted
# and owns Halloween; the Feathers just tilt the era.
MATINEE_OF_THE_DAMNED = SeasonalBlock(
    base="horror_movie",
    seasonal={
        "FALL":   Feather("eighties_horror_movie", 0.4),
        "WINTER": Feather("classic_horror_movie", 0.4),
        "SUMMER": Feather("horror_kaiju_movie", 0.3),
    },
    auto_tag=True
)

# 22:00-24:00. The name block, and the channel's centre of gravity: 50 films,
# the largest single era in the library and the decade horror was a video shelf
# -- The Thing, The Shining, Evil Dead, A Nightmare on Elm Street, The Fly,
# Poltergeist, Aliens, Videodrome. Two hours a night, seven nights, six-week
# cycle.
NIGHTMARE_THEATRE_FEATURE = RandomCollection(["eighties_horror_movie"])

# 00:00-02:00. Where the channel stops being hospitable. Found footage and
# slashers exist on the grid only here and in the summer Feather above.
THE_WITCHING_HOUR = RandomCollection([
    "modern_horror_movie",
    "horror_found_footage_movie",
    "horror_slasher_movie",
])

# 02:00-06:00. The dead zone jukebox -- everything modern, shuffled, no
# structure. Same role as High Noon's The Long Ride.
INSOMNIA_THEATRE = RandomCollection([
    "modern_horror_movie",
    "horror_zombies_movie",
    "horror_vampire_movie",
])

# Saturday 22:00-02:00, the double feature. The 51 horror-comedies every other
# key on this channel excludes: An American Werewolf in London, Re-Animator,
# Return of the Living Dead, Fright Night, Gremlins, Creepshow, Evil Dead II,
# Shaun of the Dead, Rocky Horror. A midnight-movie crowd is a different room
# from a Tuesday at ten, and this is the only slot that admits it.
MIDNIGHT_MOVIE = RandomCollection(["horror_comedy_movie"])

# ==============================================================================
# THE SPINE -- the two shows that can strip
# ==============================================================================

# 19:00-20:00, the lead-in to prime, which is where a half-hour anthology with a
# host belongs and where this one actually aired. Two episodes a night, 93 of
# them, so the wheel comes round about every six and a half weeks.
#
# Reached by title because the library tags it Comedy, Crime, Mystery and
# Science Fiction -- no horror key on the channel can see it. Shuffle rather
# than Chronological: it is an anthology, there is nothing to preserve, and
# tune-in is the entire format.
TALES_FROM_THE_CRYPT = Block(
    name="Tales from the Crypt",
    items=OrderedCollection([
        {"title": "Tales from the Crypt",
         "query": show_by_title("Tales from the Crypt"),
         "order": "Shuffle"},
    ])
)

# 17:00-19:00. Two hour-longs, 87 episodes, episodic supernatural procedural --
# the only other show here that survives a stranger dropping in mid-run.
# Nightmare Cafe rides along rather than stripping: six episodes cannot carry a
# slot, but in the wheel it surfaces every couple of weeks and stays a find.
#
# The named Poltergeist entry appears once and `classic_horror_tv` carries the
# rest of the wheel. That key is the same three shows -- Poltergeist, Nightmare
# Cafe and Darkplace -- so the block leans on the era pool rather than on a
# repeated bare title used as a weight, and Darkplace gets a second home
# outside Saturday's comedy hour.
THE_LEGACY = Block(
    name="The Legacy",
    items=RandomCollection([
        {"title": "Poltergeist: The Legacy",
         "query": show_by_title("Poltergeist: The Legacy"),
         "order": "Shuffle"},
        "classic_horror_tv",
        {"title": "Nightmare Cafe",
         "query": show_by_title("Nightmare Cafe"),
         "order": "Chronological"},
    ])
)

# Sunday 17:00-19:00 instead of The Legacy. Animated horror is invisible to
# every key on this channel -- `show_source` excludes genre:animation outright --
# so these three reach air only by being named. Love, Death & Robots is a true
# anthology and drops in cleanly; the other two are serialized and get
# Chronological order.
#
# Primal is not here. It is a Tartakovsky Adult Swim original and Cartoon
# Network airs it in the Midnight Run, which is the stronger claim -- the CN
# restructure was built around raising exactly that number. The collision
# report caught it as a shared key on the first run after this channel existed.
THE_ANIMATED_HOUR = Block(
    name="After Hours Animation",
    items=RandomCollection([
        {"title": "Love, Death & Robots",
         "query": show_by_title("Love, Death & Robots"), "order": "Shuffle"},
        {"title": "Castlevania",
         "query": show_by_title("Castlevania"), "order": "Chronological"},
        {"title": "Pet Shop of Horrors",
         "query": show_by_title("Pet Shop of Horrors"), "order": "Chronological"},
    ])
)

# Saturday 19:00-20:00 in place of the Crypt. The comedies, kept together and
# kept off the weeknight strip -- What We Do in the Shadows and Santa Clarita
# Diet are sitcoms with blood in them and reading them as horror is what makes
# a genre channel feel confused. Paired with the horror-comedy double feature
# that follows at 22:00, Saturday becomes the channel's funny night on purpose.
LATE_SHIFT_COMEDY = Block(
    name="The Late Shift",
    items=RandomCollection([
        {"title": "What We Do in the Shadows",
         "query": show_by_title("What We Do in the Shadows"), "order": "Shuffle"},
        {"title": "Santa Clarita Diet",
         "query": show_by_title("Santa Clarita Diet"), "order": "Chronological"},
        {"title": "Garth Marenghi's Darkplace",
         "query": show_by_title("Garth Marenghi's Darkplace"), "order": "Chronological"},
        {"title": "Wednesday",
         "query": show_by_title("Wednesday"), "order": "Chronological"},
    ])
)

# ==============================================================================
# THE APPOINTMENTS -- six serialized shows, six nights, one season a year
# ==============================================================================
#
# Same construction as High Noon, and for the same reason: nobody drops into
# Hannibal season two. `frequency` paces an appointment, it does not gate it --
# `_find_active_episode` returns the current episode for any date inside the
# season window -- so each of these survives only because PRIME_BLOCK in the
# channel is a weekday dict and the slot does the gating. See KNOWN_ISSUES.md.
#
# Premieres are staggered across all four seasons so the channel always has one
# or two first-run nights and never six. `modern_horror_movie` is the bed under
# every one of them: 102 films, and a prime that falls through to a horror
# feature is still the channel.

HANNIBAL = annual_show(
    show_title="Hannibal",
    episodes_per_season=[13, 13, 13],
    premiere_year=2026,
    premiere_season=("FALL", "MONDAY"),
    frequency=["MONDAY"],
    reruns="modern_horror_movie",
    episodes_per_slot=2,
    loop=True
)

EVIL = annual_show(
    show_title="Evil",
    episodes_per_season=[13, 13, 10, 14],
    premiere_year=2026,
    premiere_season=("WINTER", "TUESDAY"),
    frequency=["TUESDAY"],
    reruns="modern_horror_movie",
    episodes_per_slot=2,
    loop=True
)

FROM = annual_show(
    show_title="FROM",
    episodes_per_season=[10, 10, 10],
    premiere_year=2026,
    premiere_season=("SPRING", "WEDNESDAY"),
    frequency=["WEDNESDAY"],
    reruns="modern_horror_movie",
    episodes_per_slot=2,
    loop=True
)

YELLOWJACKETS = annual_show(
    show_title="Yellowjackets",
    episodes_per_season=[10, 9, 10],
    premiere_year=2026,
    premiere_season=("SUMMER", "THURSDAY"),
    frequency=["THURSDAY"],
    reruns="modern_horror_movie",
    episodes_per_slot=2,
    loop=True
)

# Friday on purpose. It is the loudest show on the channel and it leads into the
# horror-comedy weekend.
ASH_VS_EVIL_DEAD = annual_show(
    show_title="Ash vs Evil Dead",
    episodes_per_season=[10, 10, 10],
    premiere_year=2026,
    premiere_season=("FALL", "FRIDAY"),
    frequency=["FRIDAY"],
    reruns="modern_horror_movie",
    episodes_per_slot=2,
    loop=True
)

# The Sunday prestige hour. Season 2 is 22 episodes against season 1's 8, which
# is the real broadcast shape and not a counting error.
TWIN_PEAKS = annual_show(
    show_title="Twin Peaks",
    episodes_per_season=[8, 22, 18],
    premiere_year=2026,
    premiere_season=("WINTER", "SUNDAY"),
    frequency=["SUNDAY"],
    reruns="modern_horror_movie",
    episodes_per_slot=2,
    loop=True
)

# One appointment per night, wrapped so the slot has a name in the guide either
# way. DailyOrderedCollection rather than OrderedCollection: it resets to index
# 0 each day, so the appointment is always first in its two hours and premieres
# land at 20:00 every week.
def _appointment(name, program):
    return Block(
        name=name,
        items=DailyOrderedCollection([program, "modern_horror_movie"]),
        fill_strategy="yield"
    )

MONDAY_NIGHT    = _appointment("Hannibal", HANNIBAL)
TUESDAY_NIGHT   = _appointment("Evil", EVIL)
WEDNESDAY_NIGHT = _appointment("FROM", FROM)
THURSDAY_NIGHT  = _appointment("Yellowjackets", YELLOWJACKETS)
FRIDAY_NIGHT    = _appointment("Ash vs Evil Dead", ASH_VS_EVIL_DEAD)
SUNDAY_NIGHT    = _appointment("Twin Peaks", TWIN_PEAKS)

# Saturday has no weekly appointment in the six-night rotation. It gets the
# three short prestige runs instead -- and they are annual shows like the rest,
# not a plain playlist.
#
# The first version of this block was an OrderedCollection of the three shows
# straight into Saturday prime. Between them they have 23 episodes and Saturday
# prime is 104 hours a year, so the simulator played the same 23 episodes
# thirteen times over -- The Walking Dead every single Saturday, forever. A
# limited series re-run weekly stops being an event.
#
# Windows are staggered so only one is ever live and the other 40-odd Saturdays
# fall through to the film bed, exactly as the weeknight appointments do.
# Midnight Mass premieres in autumn on purpose: seven episodes of Catholic
# horror landing next to Halloween is the best-scheduled thing on the channel.

MIDNIGHT_MASS = annual_show(
    show_title="Midnight Mass",
    episodes_per_season=[7],
    premiere_year=2026,
    premiere_season=("FALL", "SATURDAY"),
    frequency=["SATURDAY"],
    reruns="modern_horror_movie",
    episodes_per_slot=2,
    loop=True
)

LOVECRAFT_COUNTRY = annual_show(
    show_title="Lovecraft Country",
    episodes_per_season=[10],
    premiere_year=2026,
    premiere_season=("SUMMER", "SATURDAY"),
    frequency=["SATURDAY"],
    reruns="modern_horror_movie",
    episodes_per_slot=2,
    loop=True
)

# Season one is all that is on disk -- six episodes, which is the original
# 2010 run and a complete season, not a gap.
THE_WALKING_DEAD = annual_show(
    show_title="The Walking Dead",
    episodes_per_season=[6],
    premiere_year=2026,
    premiere_season=("SPRING", "SATURDAY"),
    frequency=["SATURDAY"],
    reruns="modern_horror_movie",
    episodes_per_slot=2,
    loop=True
)

# Keyed by season, not stacked in a collection -- the same idiom PRIME_BLOCK
# uses for weekdays, because season names are day labels too and the resolver
# matches them the same way.
#
# Two earlier shapes both failed, and the reason is worth keeping. An
# OrderedCollection of the three shows straight into the slot replayed their 23
# episodes thirteen times a year. Stacking the three Programs in a
# DailyOrderedCollection with a film key behind them looked right and was
# worse: `annual_show(reruns=...)` hangs the bed on the Program, so the first
# entry resolved every week and the other two never aired at all; dropping
# `reruns` did not help either, because a Program that resolves to nothing
# yields the *whole slot* rather than passing the turn to the next item, so the
# trailing key was unreachable both ways. A label-keyed dict resolves exactly
# one branch per night and sidesteps the question.
#
# Winter has no limited series and gets the horror-comedy double feature that
# already owns Saturday's 22:00 -- a four-hour Saturday night rather than two.
SATURDAY_LIMITED_SERIES = {
    "SPRING": _appointment("The Walking Dead", THE_WALKING_DEAD),
    "SUMMER": _appointment("Lovecraft Country", LOVECRAFT_COUNTRY),
    "FALL":   _appointment("Midnight Mass", MIDNIGHT_MASS),
    "default": MIDNIGHT_MOVIE,
}

# ==============================================================================
# EVENTS
# ==============================================================================

# October 31. The channel's own day, and the one date it abandons the clock
# discipline entirely -- horror from noon to close, with the Halloween-tagged
# shelf blended over the top. A RandomCollection is right here and only here:
# a holiday *schedule* re-picks per slot, so four keys give the day four
# different draws. A marathon does not -- see DEVILS_NIGHT below.
#
# Classic Cinema keeps its own Halloween prime; that event is built from
# `tag:halloween`, a different axis from `genre:horror`, so the two do not draw
# the same films by construction.
HALLOWEEN_MARATHON = RandomCollection([
    "halloween_all_movie",
    "halloween_80s_movie",
    "halloween_90s_movie",
    "horror_movie",
])

# ------------------------------------------------------------------------------
# Every title below is year-bounded, because `movie_by_title` builds a phrase
# match: `title:"Halloween"` also returns Halloween II, III, 4 and The Halloween
# Tree, and `title:"Friday the 13th"` returns all eight sequels plus the 2009
# remake. An unbounded franchise title turns an ordered marathon into a shuffle
# of the whole series. Same fix `library/scifi.py` uses to keep Star Trek 1966
# from dragging in The Next Generation.
#
# Marathons are MarathonSequences, not collections, and the difference matters.
#
# `find_active_marathon` calls `.pick()` on anything that has one, so a
# RandomCollection or an OrderedCollection handed to a Marathon collapses to a
# single item: the block plays one film, yields, and the rest of the window
# falls back to the ordinary grid. Only a MarathonSequence survives as a
# sequence -- `_convert_marathon_to_block` reads its `.items` and builds one
# Program per entry. A six-hour window wants four features listed out.
# ------------------------------------------------------------------------------

# Halloween night, 20:00-24:00, via the holiday schedule rather than via a
# Marathon -- `find_active_marathon` returns nothing while
# `holiday_ctx.is_holiday_season` is true, and Halloween is precisely such a
# season, so a marathon triggered on 30 or 31 October can never fire. Holidays
# outrank marathons by design. The holiday *schedule* is the mechanism that
# works on those dates.
#
# DailyOrderedCollection, not OrderedCollection: the plain one is date-anchored
# and walks its start position around the list, which on Halloween 2026 opened
# the night on Halloween 4. This one resets to index 0 each day, so prime takes
# the 1978 original and late takes Halloween II -- the two that fit four hours
# at 91 and 92 minutes. Same reason the appointments below use it.
#
# III and 4 stay on the list behind them. Halloween III has no Myers in it and
# is the famous odd one out; it stays because the run is the franchise, not the
# character, and skipping it is the kind of tidying that makes a schedule feel
# curated by a robot.
HALLOWEEN_NIGHT_FEATURE = DailyOrderedCollection([
    {"title": "Halloween",
     "query": movie_by_title("Halloween") + " AND release_date:[1978-01-01 TO 1978-12-31]",
     "order": "Chronological"},
    {"title": "Halloween II",
     "query": movie_by_title("Halloween II") + " AND release_date:[1981-01-01 TO 1981-12-31]",
     "order": "Chronological"},
    {"title": "Halloween III: Season of the Witch",
     "query": movie_by_title("Halloween III - Season of the Witch") + " AND release_date:[1982-01-01 TO 1982-12-31]",
     "order": "Chronological"},
    {"title": "Halloween 4: The Return of Michael Myers",
     "query": movie_by_title("Halloween 4 - The Return of Michael Myers") + " AND release_date:[1988-01-01 TO 1988-12-31]",
     "order": "Chronological"},
])

# Whenever the 13th lands on a Friday, 18:00-24:00. Chronological because the
# numbering is the joke: 95 + 87 + 95 + 91 minutes, 6h08, the same fit as
# Devil's Night. Parts V-VIII and the 2009 remake are on disk and stay in the
# ordinary slasher pool.
FRIDAY_THE_13TH = MarathonSequence([
    {"title": "Friday the 13th",
     "query": movie_by_title("Friday the 13th") + " AND release_date:[1980-01-01 TO 1980-12-31]",
     "media_type": "movie"},
    {"title": "Friday the 13th Part 2",
     "query": movie_by_title("Friday the 13th Part 2") + " AND release_date:[1981-01-01 TO 1981-12-31]",
     "media_type": "movie"},
    {"title": "Friday the 13th Part III",
     "query": movie_by_title("Friday the 13th Part III") + " AND release_date:[1982-01-01 TO 1982-12-31]",
     "media_type": "movie"},
    {"title": "Friday the 13th: The Final Chapter",
     "query": movie_by_title("Friday the 13th - The Final Chapter") + " AND release_date:[1984-01-01 TO 1984-12-31]",
     "media_type": "movie"},
])

# December 5, 20:00-24:00. The library's entire Christmas-horror shelf is three
# films and all three are comedies, so this is a Krampusnacht played for
# laughs -- 98 + 106 + 106 minutes against a four-hour window, which the third
# film overruns into The Witching Hour rather than being cut.
#
# The seasonal ramp is separate and already handled: INJECTION_RULES["CHRISTMAS"]
# carries a Horror override of `tag:Krampus OR tag:Christmas Horror`, so
# December tilts on its own without a block here.
KRAMPUSNACHT = MarathonSequence([
    {"title": "Krampus",
     "query": movie_by_title("Krampus") + " AND release_date:[2015-01-01 TO 2015-12-31]",
     "media_type": "movie"},
    {"title": "Gremlins",
     "query": movie_by_title("Gremlins") + " AND release_date:[1984-01-01 TO 1984-12-31]",
     "media_type": "movie"},
    {"title": "Gremlins 2: The New Batch",
     "query": movie_by_title("Gremlins 2 - The New Batch") + " AND release_date:[1990-01-01 TO 1990-12-31]",
     "media_type": "movie"},
])

# Halloween night television, in the Crypt's own hour.
CRYPT_MARATHON = OrderedCollection([
    {"title": "Tales from the Crypt",
     "query": show_by_title("Tales from the Crypt"),
     "order": "Shuffle"},
])
