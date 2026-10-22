"""
Cartoon Network Content
=======================
Four identities sharing one dial position: the vault at breakfast, Cartoon
Network's own shows through the day, Toonami after school, a compact FOX access
hour and Sunday night, then Adult Swim from 22:00 through the small hours.

The old grid handed 27 hours a week to Disney and 13 to Nickelodeon while the
block called "Cartoon Network Classics" was half MTV and Kids' WB. Both of
those channels are now built and own that content outright, so everything
borrowed has gone back and the hours have been given to the 460+ episodes of
CN originals and the eight owned anime series that had never aired. See
reference/cartoon-network-review.md for the audit this was built from.

Two structural rules:

**Adult Swim runs last, not first.** The Williams Street originals begin at
22:00, followed by the Midnight Run and the 02:00-06:00 acquisitions. FOX's
Simpsons-led access strip and CN prime now have room ahead of it.

**Per-show bumpers are wired by hand.** `dispatcher.play_smart_bumper` would
find them from the scheduled title on its own, but it requires a `bumpers` tag
and the trees on disk are tagged `bumps`/`shows`, so it never fires. The
~940 Toonami and 5,316 Adult Swim files are reachable only through the
explicit per-show keys in sources.py, and an item that wants its own set has
to be a Program -- ContentItem has no bumpers field. `_with_bumpers` is that
wrapper. See reference/bumper-inventory.md.

Sharing rules: nothing on this channel is shared. Disney took back
DISNEY_MORNING, DISNEY_AFTERNOON, Gargoyles and Star Wars Day; Nick took back
the Nicktoons Vault, Daria, Animaniacs and Pinky and the Brain. Ed, Edd n Eddy
came the other way -- it is a Cartoon Cartoon and was filed under Nicktoons.
The one remaining daytime gap is branding: `filler/bumpers/cartoon network/
general/` is empty, so the channel has no daytime interstitials at all rather
than borrowing Adult Swim's. See reference/channel-plan.md.
"""

from datetime import date
from scripts.logic.structures import (
    RandomCollection, OrderedCollection, DailyOrderedCollection, WeightedCollection,
    CalendarDeck, MarathonSequence, Block, Program
)
from scripts.logic.factories import annual_show
from scripts.logic.models import Swap, ContentItem
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.library.queries import episodes_without_specials, movie_by_title_year
from . import branding


def _with_bumpers(item, bumper_key):
    """
    Attach a per-show bumper set to a block item.

    ContentItem carries no bumpers field and the resolution hierarchy is
    Program > Block > Channel, so anything that wants its own interstitials
    has to be a Program. Accepts an existing Program (the `annual_show()`
    strips) or a title dict, and returns a Program either way.
    """
    if isinstance(item, Program):
        item.bumpers = bumper_key
        return item
    if isinstance(item, dict):
        item = ContentItem(**item)
    return Program(
        # Not getattr(item, "title", ...): str has a .title *method*, so a bare
        # content key resolved to the bound method rather than the fallback and
        # named the Program "<built-in method title of str object at 0x...>".
        name=item.title if isinstance(item, ContentItem) else str(item),
        content=item,
        bumpers=bumper_key
    )


def _half_hour(item, segments, bumper_key=None):
    """
    One pick that fills a half-hour: `segments` episodes of the same show, back
    to back.

    Most of the daytime library is split into segments rather than half-hours --
    Dexter's Laboratory, Johnny Bravo and the theatrical shorts run about seven
    minutes, Powerpuff Girls, Ed Edd n Eddy, Courage, Adventure Time and Steven
    Universe about eleven (median runtimes probed off disk, 2026-09-27). One
    pick of a seven-minute show is a sixth of the pick a Flintstones episode
    is, so a two-hour block of five of them needed sixteen picks and went round
    its list three times. Grouped, the same block needs six or seven.

    Two segments at most (operator, 2026-10-18): three of the same show back to
    back reads as a repeat, not a half-hour. A seven-minute show's pick is now
    about fourteen minutes.
    """
    if isinstance(item, dict):
        item = ContentItem(**item)
    return Program(
        name=item.title if isinstance(item, ContentItem) else str(item),
        content=item,
        bumpers=bumper_key,
        play_count=segments,
    )


def _episodes(title, order=None):
    """A title-only item without season 0, where the specials and TV movies are."""
    item = {"title": title, "query": episodes_without_specials(title)}
    if order:
        item["order"] = order
    return item


# Block sizing, for every block below: a pick is 14-25 minutes, so an hour is
# about three or four picks, two hours six or seven, three hours nine. A block holds at
# least that many shows, so each one airs once per block and the list only goes
# round again -- back to the top -- when the slot has time left over. Rotations
# are OrderedCollection: the start moves one show a day, and a block used twice
# in one day carries on where the first airing stopped.

# ==============================================================================
# 1. THE VAULT AND THE WEEKEND MORNINGS
# ==============================================================================

# 06:00-08:00 weekdays and Sunday. The theatrical shorts and the Hanna-Barbera
# library. This used to hold 02:00-06:00, which was the single largest historical
# inversion in the grid -- 28 hours a week of Yogi Bear in the slot Adult Swim
# actually occupied.
#
# Popeye is not here any more. The vault ran it at 06:00 and again at 12:00
# every weekday, one seven-minute short per pick, and 46 shorts were going
# round every two and a half weeks. It is a weekend show now: one half-hour on
# Saturday and one on Sunday, about eight weeks per cycle.
THE_VAULT = Block(
    name="The Vault",
    items=OrderedCollection([
        _half_hour(_episodes("Looney Tunes"), 2),
        _episodes("The Flintstones"),
        _half_hour(_episodes("Tom and Jerry"), 2),
        _episodes("The Jetsons"),
        _half_hour(_episodes("Yogi Bear"), 2),
        _half_hour(_episodes("Hong Kong Phooey"), 2),
    ]),
    use_epg_group=False
)

# 06:00-08:00 Saturday, a fixed running order. DailyOrderedCollection restarts
# at the top every Saturday, so Looney Tunes is always at six and Scooby-Doo is
# always around seven, the way a Saturday lineup actually worked.
#
# "Superman" by key, not title: the 1941 Fleischer shorts are nine minutes each
# and a different show from Superman: The Animated Series, which airs in Action
# Hour the same afternoon.
SATURDAY_MORNING = Block(
    name="Saturday Morning Cartoons",
    items=DailyOrderedCollection([
        _half_hour(_episodes("Looney Tunes"), 2),
        _episodes("The Flintstones"),
        _half_hour(_episodes("Popeye the Sailor"), 2),
        _episodes("Scooby-Doo, Where Are You!", "Chronological"),
        _half_hour(_episodes("Tom and Jerry"), 2),
        _half_hour("superman_fleischer_tv", 2),
    ]),
    use_epg_group=False
)

# 08:00-09:00 Sunday. One of three finite two-show bills rotates by date, and
# when it finishes the 09:00 Cartoon Cartoons hour starts early. A bill is
# 31-47 minutes, and waiting for 09:00 was up to half an hour of dead air.
SUNDAY_MORNING = OrderedCollection([
    Block(
        name="Sunday Morning Cartoons",
        items=["cn_sunday_scooby_where_tv", _half_hour("cn_sunday_popeye_tv", 2)],
        fill_strategy="bridge",
        use_epg_group=False,
    ),
    Block(
        name="Sunday Morning Cartoons",
        items=["cn_sunday_scooby_show_tv", _half_hour("cn_sunday_superman_tv", 2)],
        fill_strategy="bridge",
        use_epg_group=False,
    ),
    Block(
        name="Sunday Morning Cartoons",
        items=["cn_sunday_whats_new_scooby_tv", "cn_sunday_flintstones_tv"],
        fill_strategy="bridge",
        use_epg_group=False,
    ),
])

# 14:00-15:00 weekdays. The three Scooby series fill the last hour before
# Toonami, one of each -- 120 episodes at five a week.
THE_SCOOBY_BLOCK = Block(
    name="The Scooby Block",
    items=OrderedCollection([
        _episodes("Scooby-Doo, Where Are You!", "Chronological"),
        _episodes("The Scooby-Doo Show", "Chronological"),
        _episodes("What's New Scooby-Doo", "Chronological"),
    ]),
    use_epg_group=False
)

# ==============================================================================
# 2. CARTOON NETWORK'S OWN SHOWS
# ==============================================================================

# 08:00-10:00 weekdays and Saturday; 09:00 Sunday, returning again at noon.
#
# The actual Cartoon Cartoons, which is what the block that used to carry this
# name was not: it held Daria (MTV), Animaniacs and Pinky and the Brain (Kids'
# WB) and Gravity Falls and The Owl House (Disney), and CN's own originals held
# five hours of the week. Ed, Edd n Eddy joins them here -- CN's longest-running
# original, previously filed inside the Nicktoons Vault.
#
# Five shows in two hours means the sixth half-hour, when there is one, goes
# back to the top. The brand had more (Cow and Chicken, I Am Weasel, Sheep in
# the Big City) but none of them are on disk.
CARTOON_CARTOONS = Block(
    name="Cartoon Cartoons",
    items=OrderedCollection([
        _half_hour("cn_daytime_dexter_tv", 2),
        _half_hour("cn_daytime_powerpuff_tv", 2),
        _half_hour("cn_daytime_johnny_bravo_tv", 2),
        _half_hour("cn_daytime_ed_edd_n_eddy_tv", 2),
        _half_hour("cn_daytime_courage_tv", 2),
    ]),
    use_epg_group=False
)

# Saturday and Sunday advance independently from the weekday strip. The two
# blocks intentionally share this object so a Saturday/Sunday weekend behaves
# like one small run rather than restarting each morning.
CARTOON_CARTOONS_WEEKEND = Block(
    name="Cartoon Cartoons",
    items=OrderedCollection([
        _half_hour("cn_weekend_dexter_tv", 2),
        _half_hour("cn_weekend_powerpuff_tv", 2),
        _half_hour("cn_weekend_johnny_bravo_tv", 2),
        _half_hour("cn_weekend_ed_edd_n_eddy_tv", 2),
        _half_hour("cn_weekend_courage_tv", 2),
    ]),
    use_epg_group=False
)

# 14:00-15:00 Sunday.
#
# Primal is TV-MA and aired on Adult Swim, not on daytime CN, so it is in the
# Midnight Run instead. Infinity Train (2019) is a modern show and was never
# part of the 1996-2003 Cartoon Cartoons brand. Steven Universe is one entry
# rather than two because the title also matches Steven Universe Future.
_ADVENTURE_TIME = _half_hour("cn_weekend_adventure_time_tv", 2)
_STEVEN_UNIVERSE = _half_hour("cn_weekend_steven_universe_tv", 2)
_INFINITY_TRAIN = _half_hour("cn_weekend_infinity_train_tv", 2)

CN_MODERN = Block(
    name="Cartoon Network",
    items=OrderedCollection([
        _ADVENTURE_TIME,
        _STEVEN_UNIVERSE,
        "cn_weekend_samurai_jack_tv",
        _INFINITY_TRAIN,
    ]),
    use_epg_group=False
)

# 10:00-12:00 Saturday. The modern shows, plus Over the Garden Wall, which is
# ten episodes and too short for a daily rotation. Here it gets roughly one
# Saturday half-hour a week, in order, so the miniseries plays through about
# once every couple of months.
CN_SATURDAY = Block(
    name="Cartoon Network",
    items=OrderedCollection([
        _ADVENTURE_TIME,
        _STEVEN_UNIVERSE,
        "cn_weekend_samurai_jack_tv",
        _INFINITY_TRAIN,
        _half_hour("cn_weekend_over_the_garden_wall_tv", 2),
    ]),
    use_epg_group=False
)

# Weekday prime after the FOX access pair, and 10:00-12:00 in summer. Every CN
# original appears in one old/new rotation. The 18:00 hour draws from the same
# rotation, so the evening is one run of ten shows: nothing comes back until the
# other nine have aired.
_CN_PRIME_ROTATION = OrderedCollection([
    _half_hour("cn_prime_dexter_tv", 2),
    _half_hour("cn_prime_adventure_time_tv", 2),
    _half_hour("cn_prime_powerpuff_tv", 2),
    _half_hour("cn_prime_steven_universe_tv", 2),
    _half_hour("cn_prime_johnny_bravo_tv", 2),
    "cn_prime_samurai_jack_tv",
    _half_hour("cn_prime_ed_edd_n_eddy_tv", 2),
    _half_hour("cn_prime_infinity_train_tv", 2),
    _half_hour("cn_prime_courage_tv", 2),
    _half_hour("cn_prime_over_the_garden_wall_tv", 2),
])

CN_PRIME = Block(
    name="Cartoon Network",
    items=_CN_PRIME_ROTATION,
    use_epg_group=False
)

# 18:00-19:00 weekdays, ahead of the FOX pair. This was five fixed pairs, one
# per weekday, drawn from the same shows as prime but outside its rotation:
# Monday's pair was Dexter and Adventure Time, and prime then opened wherever
# its own rotation stood, so Adventure Time aired at 18:21 and again at 19:45
# with two shows between. Sharing the rotation closes that. The last pick may
# run past 19:00 and the FOX pair starts when it ends: a few minutes late is
# fine, dead air is not (operator, 2026-10-18).

CN_EARLY_EVENING = Block(
    name="Cartoon Network",
    items=_CN_PRIME_ROTATION,
    fill_strategy="gap",
    use_epg_group=False,
)

# 18:00-19:00 Friday. Cartoon Cartoon Fridays follows at 20:00 with Dexter,
# Powerpuff, Johnny Bravo, Ed, Courage and Samurai Jack, so the hour ahead of
# it takes the four prime shows CCF never airs. The prime rotation would have
# put Powerpuff at 18:46 and again in CCF at 20:02.
CN_FRIDAY_EARLY_EVENING = Block(
    name="Cartoon Network",
    items=OrderedCollection([
        _half_hour("cn_prime_adventure_time_tv", 2),
        _half_hour("cn_prime_steven_universe_tv", 2),
        _half_hour("cn_prime_infinity_train_tv", 2),
        _half_hour("cn_prime_over_the_garden_wall_tv", 2),
    ]),
    fill_strategy="gap",
    use_epg_group=False,
)

# 20:00-22:00 Friday. A fixed
# running order, because the point of it was that it was an event. This used
# to be seven OrderedCollection items, and seven items against a seven-day
# rotation start on the same show every Friday: Adventure Time and Steven
# Universe, the two at the tail, never aired. Six now, all of them reachable.
CARTOON_CARTOON_FRIDAY = Block(
    name="Cartoon Cartoon Fridays",
    items=DailyOrderedCollection([
        _half_hour("cn_prime_dexter_tv", 2),
        _half_hour("cn_prime_powerpuff_tv", 2),
        _half_hour("cn_prime_johnny_bravo_tv", 2),
        _half_hour("cn_prime_ed_edd_n_eddy_tv", 2),
        _half_hour("cn_prime_courage_tv", 2),
        "cn_prime_samurai_jack_tv",
    ]),
    use_epg_group=False
)

# ==============================================================================
# 3. SYNDICATION AND ACTION
# ==============================================================================

# 10:00-12:00 weekdays, 12:00-14:00 Saturday, 14:00-16:00 Sunday. The
# period-correct syndication package, eight shows, so no airing repeats one. Gargoyles is not here; it went back to
# Disney. ThunderCats left for Toonami's closing filler on 2026-10-18 -- it
# opened the first Toonami in 1997, and one channel airing it twice a day was
# one too many.
#
# Never before 10:00: He-Man, The Transformers and ThunderCats are also Totally
# 80s' morning cartoons, 06:00-10:00.
#
# Teenage Mutant Ninja Turtles is only in the spring Marvel hour; see there.
SYNDICATION_HOUR = Block(
    name="Syndication Hour",
    items=OrderedCollection([
        _episodes("He-Man and the Masters of the Universe", "Chronological"),
        _episodes("The Transformers", "Chronological"),
        _episodes("Beast Wars Transformers", "Chronological"),
        _episodes("Inspector Gadget", "Chronological"),
        _episodes("Captain Planet and the Planeteers", "Chronological"),
        # The 1994 animated series. The bare title also matches the 2001 and
        # 2017 live-action shows.
        {"title": "The Tick",
         "query": 'type:episode AND show_title:"The Tick"'
                  ' AND release_date:[1994-01-01 TO 1997-12-31]'},
        _episodes("Street Sharks", "Chronological"),
        _episodes("Mister T", "Chronological"),
    ]),
    use_epg_group=False
)

# The DC animated universe, in order. Weekdays 14:00-16:00, the hour Cartoon
# Network ran its action shows ahead of Toonami (operator, 2026-10-18). Five
# shows across two hours is six picks, so the sixth goes back to the first with
# four between.
_DC_SHOWS = [
    _episodes("Batman: The Animated Series", "Chronological"),
    _episodes("The New Batman Adventures", "Chronological"),
    _episodes("Superman: The Animated Series", "Chronological"),
    _episodes("Justice League", "Chronological"),
    "cn_batman_beyond_tv",
]

# Marvel and SWAT Kats. Weekdays 12:00-13:00: three shows of about 22 minutes
# each, so the hour is one of each, the last running a few minutes past 13:00.
_MARVEL_SHOWS = [
    "xmen_animated_tv",
    _episodes("Spider-Man"),
    # The library title is "SWAT Kats The Radical Squadron"; the phrase
    # matches its prefix. `type:episode` was missing here and the query
    # was returning show containers alongside episodes.
    {"title": "SWAT Kats",
     "query": 'type:episode AND show_title:"SWAT Kats*"',
     "order": "Chronological"},
]

DC_ACTION_HOUR = Block(
    name="Action Hour",
    items=OrderedCollection(_DC_SHOWS),
    use_epg_group=False
)

MARVEL_HOUR = Block(
    name="Marvel Action Hour",
    items=OrderedCollection(_MARVEL_SHOWS),
    use_epg_group=False
)

# The spring variant of the weekday noon hour, kept from the old grid: the
# Turtles join for the season. SeasonalBlock ramps rather than hard-swaps, so
# it fades in over the spring and peaks mid-March to mid-April.
#
# Teenage Mutant Ninja Turtles is only here. Be Kind Rewind and Sci-Fi both
# carry the 1990 film, and a daily airing met it on 13 days in 30; once a week
# on Saturday it had met it twice.
MARVEL_SPRING_HOUR = Block(
    name="Marvel Action Hour",
    items=OrderedCollection([
        *_MARVEL_SHOWS,
        _episodes("Teenage Mutant Ninja Turtles"),
    ]),
    use_epg_group=False
)

# The weekend's Action Hour is all eight, DC and Marvel together, 14:00-18:00
# Saturday and 16:00-19:00 Sunday. Eight shows is about three hours, so
# Saturday's fourth hour goes back to the top with seven between. Same shows,
# same feeds as the weekdays, so the weekend carries on where Friday stopped.
ACTION_HOUR = Block(
    name="Action Hour",
    items=OrderedCollection([*_DC_SHOWS, *_MARVEL_SHOWS]),
    use_epg_group=False
)

# ==============================================================================
# 4. CARTOON THEATRE (10:00-13:00 Sunday, and the odd Saturday afternoon)
# ==============================================================================

def _film(title, year):
    """One feature, by the title in its NFO and its release year."""
    return {"title": title, "query": movie_by_title_year(title, year), "media_type": "movie"}


def _tv_movie(title, show, episode):
    """A show's own film, which the library files as a season-0 episode.

    Season 0 is left out of every rotation (`episodes_without_specials`), so a
    show's movie airs only where it is named, as here.
    """
    return {
        "title": title,
        "query": f'type:episode AND show_title:"{show}" AND season_number:0'
                 f' AND episode_number:{episode}',
        "media_type": "movie",
    }


# The Sunday double feature's pool. It started as the seven films Cartoon
# Network actually ran; it is now the animated features no other channel
# claims (reference/repeat-plan.md, "The film roster"): Disney and Pixar are
# the Disney channel's, Japanese features Japanorama's, and Ghibli -- cleared
# for this channel -- belongs on a Saturday, because Japanorama gives Ghibli
# all of Sunday evening.
#
# Left out: Akira and Ghost in the Shell (R; they run in the Saturday overnight
# Toonami block), Isle of Dogs (PG-13), and the Christmas films (Klaus and the
# rest air at Christmas only). Fifty-eight films at two a Sunday is a
# twenty-nine-week cycle.
#
# Dragon Ball Z: Battle of Gods was a season-0 episode query and never played:
# the film is in the movie library, not the show's specials.
CARTOON_THEATRE_FILMS = [
    # What Cartoon Network ran, and its own.
    _film("Batman: Mask of the Phantasm", 1993),
    _film("The Iron Giant", 1999),
    _film("The Transformers: The Movie", 1986),
    _film("Titan A.E.", 2000),
    _film("Who Framed Roger Rabbit", 1988),
    _film("Steven Universe: The Movie", 2019),
    _film("Dragon Ball Z: Battle of Gods", 2013),
    _film("Dragon Ball Super: Broly", 2018),
    _film("The Day the Earth Blew Up: A Looney Tunes Movie", 2024),
    _film("The Lego Movie", 2014),
    _film("The Lego Batman Movie", 2017),
    _film("Happy Feet", 2006),
    _film("Happy Feet Two", 2011),
    # Hanna-Barbera, Rankin/Bass, Don Bluth and the other classics.
    _film("Charlotte's Web", 1973),
    _film("Once Upon A Forest", 1993),
    _film("The Hobbit", 1977),
    _film("Yellow Submarine", 1968),
    _film("Watership Down", 1978),
    _film("The Secret of NIMH", 1982),
    _film("An American Tail", 1986),
    _film("An American Tail: Fievel Goes West", 1991),
    _film("The Land Before Time", 1988),
    _film("All Dogs Go to Heaven", 1989),
    _film("The Brave Little Toaster", 1987),
    _film("FernGully The Last Rainforest", 1992),
    _film("The Pagemaster", 1994),
    # DreamWorks and the other studios.
    _film("Antz", 1998),
    _film("The Prince of Egypt", 1998),
    _film("The Road to El Dorado", 2000),
    _film("Chicken Run", 2000),
    _film("Shrek", 2001),
    _film("Ice Age", 2002),
    _film("Madagascar", 2005),
    _film("Kung Fu Panda", 2008),
    _film("Kung Fu Panda 2", 2011),
    _film("Kung Fu Panda 3", 2016),
    _film("Cloudy with a Chance of Meatballs", 2009),
    _film("How to Train Your Dragon", 2010),
    _film("Megamind", 2010),
    _film("Rise of the Guardians", 2012),
    _film("Spider-Man: Into the Spider-Verse", 2018),
    _film("Spider-Man: Across the Spider-Verse", 2023),
    _film("The Mitchells vs. the Machines", 2021),
    _film("The Sea Beast", 2022),
    _film("Teenage Mutant Ninja Turtles: Mutant Mayhem", 2023),
    _film("The Super Mario Bros. Movie", 2023),
    _film("The Wild Robot", 2024),
    _film("Transformers One", 2024),
    _film("KPop Demon Hunters", 2025),
    # Stop-motion and the small studios.
    _film("Wallace and Gromit in The Curse of the Were Rabbit", 2005),
    _film("Wallace & Gromit: Vengeance Most Fowl", 2024),
    _film("Coraline", 2009),
    _film("Fantastic Mr. Fox", 2009),
    _film("Guillermo del Toro's Pinocchio", 2022),
    _film("The Secret of Kells", 2009),
    _film("Song of the Sea", 2014),
    _film("Wolfwalkers", 2020),
    _film("Flow", 2024),
]

# The shows' own films, for the Saturday afternoon movie: TV movies air on
# purpose or not at all (operator, 2026-10-18). Episode numbers are the
# library's season-0 numbering. Not here: A Flintstones Christmas Carol
# (Christmas), Futurama's four films (FOX's shelf), and Ed, Edd n Eddy's Big
# Picture Show, which the library files as an extra rather than an episode.
CARTOON_THEATRE_TV_MOVIES = [
    _tv_movie("The Man Called Flintstone", "The Flintstones", 2),
    _tv_movie("The Jetsons Meet the Flintstones", "The Flintstones", 10),
    _tv_movie("I Yabba-Dabba Do!", "The Flintstones", 11),
    _tv_movie("Hollyrock-a-Bye Baby", "The Flintstones", 12),
    _tv_movie("The Flintstones On the Rocks", "The Flintstones", 17),
    _tv_movie("Rockin' with Judy Jetson", "The Jetsons", 2),
    _tv_movie("Jetsons: The Movie", "The Jetsons", 3),
    _tv_movie("Batman Beyond: Return of the Joker", "Batman Beyond", 1),
    _tv_movie("The Powerpuff Girls Movie", "The Powerpuff Girls", 4),
    _tv_movie("Johnny Bravo Goes to Bollywood", "Johnny Bravo", 20),
    _tv_movie("Dragon Ball Z: Broly - The Legendary Super Saiyan", "Dragon Ball Z", 8),
    _tv_movie("Dragon Ball Z: The Tree of Might", "Dragon Ball Z", 3),
    _tv_movie("Yu Yu Hakusho: Poltergeist Report", "Yu Yu Hakusho", 2),
    _tv_movie("Rurouni Kenshin: Requiem for the Ishin Patriots", "Rurouni Kenshin", 1),
    _tv_movie("InuYasha: Affections Touching Across Time", "InuYasha", 1),
    _tv_movie("Naruto the Movie: Ninja Clash in the Land of Snow", "Naruto", 4),
]


def _cartoon_theatre(films):
    """One film, then shorts to the end of the slot.

    The items used to be the film collection itself, which handed back a
    second feature whenever the first ended early -- Titan A.E. at 12:18 and
    Steven Universe: The Movie at 13:56, running to 15:20 and taking the next
    hour with it. A one-item list exhausts after the film, and `fill` pads the
    remainder.
    """
    return Block(
        name="Cartoon Theatre",
        items=[films],
        fill_strategy="fill",
        filler=RandomCollection([
            _episodes("Looney Tunes"),
            _episodes("Tom and Jerry"),
        ]),
        use_epg_group=False
    )


# Sunday 10:00 and 12:00, a double feature dealt from one deck: every film airs
# once before any airs twice, and the two halves of a Sunday are always
# different films. The second runs past 13:00 into the modern-shows hour.
CARTOON_THEATRE = _cartoon_theatre(CalendarDeck(CARTOON_THEATRE_FILMS, per_week=2, deal=0))
CARTOON_THEATRE_SECOND = _cartoon_theatre(CalendarDeck(CARTOON_THEATRE_FILMS, per_week=2, deal=1))

# The Saturday afternoon movie: a show's own film, dealt weekly.
CARTOON_THEATRE_TV = _cartoon_theatre(CalendarDeck(CARTOON_THEATRE_TV_MOVIES))

# On roughly one Saturday in twenty, a TV movie replaces Action Hour's last two
# hours. The movie block pads the rest of the window with shorts, so resolving
# the schedule again cannot sneak Action Hour back in afterward.
WEEKEND_ACTION_OR_MOVIE = WeightedCollection([
    (ACTION_HOUR, 0.95),
    (CARTOON_THEATRE_TV, 0.05),
])

# ==============================================================================
# 5. TOONAMI
# ==============================================================================

# 16:00-18:00 weekdays, where Toonami began in 1997. Dragon Ball opens and
# Dragon Ball Z follows with two consecutive episodes -- the old 17:00 power
# hour, folded in. Then one show from a rotation of five, and a closing filler
# show for whatever time is left.
#
# The filler used to be `toonami_bumpers` padded to the hour, which on a short
# day was eighteen minutes of back-to-back promos. Now the block's last item is
# a whole episode of ThunderCats or Pokémon, alternating by day, and only the
# minute or two after it falls to the bumpers.
#
# Every show carries its own bumper set instead of all of them sharing a
# 21-file generic pool.
#
# The `annual_show()` start dates are Contiguous Mode: each show walks its run
# one episode per weekday from the date given, so the block is a real strip
# rather than a shuffle. The start dates are anchors: they were calculated to
# put each show at a particular episode on a particular day. Recalculate if you
# want a specific episode on a specific day; nothing else depends on them.
#
# `loop_restart_season=False` and `reruns=` close the strip's two dead
# stretches. `annual_show()` defaults `loop_restart_season` to the season half
# of `premiere_season`, which is "FALL" even in Contiguous Mode where no
# premiere season was given -- so a strip that finished its run in June sat
# dark until mid-September. False loops it straight over instead. The rerun bed
# then covers whatever is left, since a Program that resolves to nothing does
# not just go quiet: the block skips it, time does not advance, and the slot
# falls through to the circuit breaker.
_WEEKDAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]

# Per-season registry keys, not show_title="Dragon Ball": that phrase also
# matches Z, GT, Super and DAIMA, and the strip was airing GT. Season counts
# are the library's six.
#
# Episode 6 on Friday 2026-10-23 (operator, 2026-10-22), which puts episode 1
# on Friday 10-16. Episode 5 had aired three days running by then, from the
# loop-phase bug fixed in `_apply_schedule_looping`; the strip picks up from
# there instead of starting over. The finale airs Tuesday 2027-05-18, the
# rerun bed takes Wednesday and Thursday, and episode 1 returns on Friday.
TOONAMI_DRAGON_BALL = annual_show(
    content_pattern="toonami_dragon_ball_s{n}_tv",
    episodes_per_season=[13, 15, 40, 33, 31, 21],
    start_date=date(2026, 10, 16), frequency=_WEEKDAYS,
    reruns="toonami_vault_tv", loop=True, loop_restart_season=False)

# Two consecutive episodes every weekday, from episode one on Monday
# 2026-10-19 (operator, 2026-10-18). Toonami Saturday has its own Dragon Ball Z
# run, which opens on the Android saga, so the two are about 120 episodes
# apart. Season counts are the library's (seasons 8 and 9 are 34 and 38 on
# disk; this said 25 and 47, which skipped nine episodes and asked for nine
# that are not there). A simulation of any date before the start gets the
# shuffled overnight run instead of an empty slot.
TOONAMI_DBZ = _with_bumpers(annual_show(
    show_title="Dragon Ball Z",
    episodes_per_season=[39, 35, 33, 32, 26, 29, 25, 34, 38],
    start_date=date(2026, 10, 19), frequency=_WEEKDAYS,
    reruns="toonami_overnight_dragon_ball_z_tv",
    episodes_per_slot=2, loop=True, loop_restart_season=False
), "toonami_dragon_ball_z_bumpers")

# One a day, in turn, each on its weekday feed from episode one. Toonami
# Saturday has its own feeds of the same shows, started well into each. Plain keys,
# not `_with_bumpers` Programs: a collection that is one item of a list block
# is resolved as content, and a Program picked that way is skipped as
# unplayable and stalls the slot into the circuit breaker. These shows get the
# block's Toonami bumpers instead of their own sets.
TOONAMI_ROTATION = OrderedCollection([
    "toonami_weekday_sailor_moon_tv",
    "toonami_weekday_yu_yu_hakusho_tv",
    "toonami_weekday_rurouni_kenshin_tv",
    "toonami_weekday_inuyasha_tv",
    "toonami_weekday_naruto_tv",
])

# ThunderCats one day, Pokémon the next.
TOONAMI_FILLER_SHOWS = OrderedCollection([
    "toonami_thundercats_tv",
    "toonami_pokemon_tv",
])

TOONAMI = Block(
    name="Toonami",
    items=[
        TOONAMI_DRAGON_BALL,
        TOONAMI_DBZ,
        TOONAMI_ROTATION,
        TOONAMI_FILLER_SHOWS,
    ],
    intro=branding.BRANDING_TOONAMI.intro,
    outro=branding.BRANDING_TOONAMI.outro,
    bumpers=branding.BRANDING_TOONAMI.bumpers,
    fill_strategy="fill",
    filler="toonami_bumpers",
    use_epg_group=False
)

# --- The Saturday appointment -----------------------------------------------
#
# Dragon Ball DAIMA, 20 episodes, one a Saturday. Too short to strip and the
# only first-run anime the library has that nobody else is scheduling, which is
# exactly what appointment TV is for. Dragon Ball Super is the rerun bed for
# the other 32 Saturdays of the year.
DRAGON_BALL_DAIMA = _with_bumpers(annual_show(
    show_title="Dragon Ball DAIMA",
    episodes_per_season=[20],
    premiere_year=2026,
    premiere_season=("FALL", "SATURDAY"),
    frequency=["SATURDAY"],
    reruns="dragon_ball_super_tv",
    loop=True
), "toonami_dragon_ball_z_bumpers")  # no DAIMA set on disk; DBZ's is the nearest

# 18:00-20:00 Saturday. DailyOrderedCollection resets to index 0 each day, so
# DAIMA holds 18:00 every Saturday and the premiere lands at the same time each
# week -- the one thing an appointment cannot do is move around.
#
# Six items so the collection cannot wrap, which matters here: a wrap resolves
# the appointment a second time and re-airs the premiere in the same evening.
# Five is two hours on paper and was not enough in practice -- the fifth ended
# at 19:58, and a pick that starts before the boundary still plays, so DAIMA
# went out again at 19:58. Yu Yu Hakusho is the guard. It was eight items across
# 17:00-20:00 until the weekday grid moved Toonami to 15:00 and this slot
# boundary to 18:00.
TOONAMI_SATURDAY = Block(
    name="Toonami",
    items=DailyOrderedCollection([
        DRAGON_BALL_DAIMA,
        _with_bumpers("toonami_saturday_dragon_ball_z_tv", "toonami_dragon_ball_z_bumpers"),
        _with_bumpers("toonami_saturday_one_piece_tv", "toonami_one_piece_bumpers"),
        _with_bumpers("toonami_saturday_naruto_tv", "toonami_naruto_bumpers"),
        _with_bumpers("toonami_saturday_fullmetal_alchemist_brotherhood_tv",
                      "toonami_fullmetal_alchemist_brotherhood_bumpers"),
        _with_bumpers("toonami_saturday_yu_yu_hakusho_tv", "toonami_yu_yu_hakusho_bumpers"),
    ]),
    intro=branding.BRANDING_TOONAMI.intro,
    outro=branding.BRANDING_TOONAMI.outro,
    bumpers=branding.BRANDING_TOONAMI.bumpers,
    use_epg_group=False
)

# 20:00-23:00 Saturday. The second half of Toonami Saturday, and a separate
# block rather than three more hours of the one above: continuing that
# collection would wrap it back to the DAIMA appointment. Same EPG name, so the
# guide reads as one five-hour Toonami.
#
# No show from the first two hours. Dragon Ball Z, One Piece and Justice League
# used to be in both halves, so the same evening could air them twice. Six
# shows against about seven picks: the seventh goes back to the top. Batman
# Beyond is the one non-anime that stays; Justice League is in Action Hour three
# hours earlier.
TOONAMI_SATURDAY_VAULT = Block(
    name="Toonami",
    items=OrderedCollection([
        _with_bumpers("cn_weekend_samurai_jack_tv", "toonami_samurai_jack_bumpers"),
        "toonami_saturday_sailor_moon_tv",
        _with_bumpers("toonami_saturday_inuyasha_tv", "toonami_inuyasha_bumpers"),
        "toonami_saturday_batman_beyond_tv",
        "toonami_saturday_rurouni_kenshin_tv",
        "toonami_saturday_dragon_ball_tv",
    ]),
    intro=branding.BRANDING_TOONAMI.intro,
    bumpers=branding.BRANDING_TOONAMI.bumpers,
    use_epg_group=False
)

# 02:00-06:00 Saturday, in place of Adult Swim's acquisitions. The overnight
# rerun of the weekday strip, which is what the Midnight Run name meant on
# Toonami -- the long shows, at the hour there is room for them.
TOONAMI_MIDNIGHT_RUN = Block(
    name="Toonami: The Midnight Run",
    items=RandomCollection([
        _with_bumpers("toonami_overnight_one_piece_tv", "toonami_one_piece_bumpers"),
        _with_bumpers("toonami_overnight_naruto_tv", "toonami_naruto_bumpers"),
        _with_bumpers("toonami_overnight_inuyasha_tv", "toonami_inuyasha_bumpers"),
        _with_bumpers("toonami_overnight_dragon_ball_z_tv", "toonami_dragon_ball_z_bumpers"),
        _with_bumpers("toonami_overnight_yu_yu_hakusho_tv", "toonami_yu_yu_hakusho_bumpers"),
        "toonami_overnight_rurouni_kenshin_tv",
        _with_bumpers("attack_on_titan_tv", "toonami_attack_on_titan_bumpers"),
        # The two films the Cartoon Theatre could not take: both are R-rated,
        # both have Toonami bumper sets on disk (Akira 18, Ghost in the Shell
        # 53), and a four-hour overnight slot is the one place a feature fits.
        _with_bumpers({"title": "Akira", "query": 'type:movie AND title:"Akira"',
                       "media_type": "movie"}, "toonami_akira_bumpers"),
        _with_bumpers({"title": "Ghost in the Shell",
                       "query": 'type:movie AND title:"Ghost in the Shell"',
                       "media_type": "movie"}, "toonami_ghost_in_the_shell_bumpers"),
    ]),
    intro=branding.BRANDING_TOONAMI.intro,
    bumpers=branding.BRANDING_TOONAMI.bumpers,
    use_epg_group=False
)

# ==============================================================================
# 6. ADULT SWIM (22:00 - 06:00)
# ==============================================================================

# 22:00-24:00 Mon/Wed/Fri, and 00:00-02:00 Monday. Williams Street, 2001-2005 --
# the shows Adult Swim was actually built out of, five of which had never aired
# on this channel. Space Ghost Coast to Coast (81 episodes) is the one the whole
# block came from and was entirely absent.
#
# Everything but Home Movies is an eleven-minute show, and one episode per pick
# went round the list twice a night. Two per pick is the half-hour they aired
# as, and seven half-hours against eight picks means one wrap at most.
AS_ORIGINALS_A = Block(
    name="Adult Swim",
    items=OrderedCollection([
        _half_hour("as_prime_space_ghost_tv", 2,
                   "adult_swim_space_ghost_coast_to_coast_bumpers"),
        _half_hour("as_prime_brak_show_tv", 2,
                   "adult_swim_the_brak_show_bumpers"),
        _half_hour("as_prime_aqua_teen_tv", 2,
                   "adult_swim_aqua_teen_hunger_force_bumpers"),
        _half_hour("as_prime_sealab_tv", 2,
                   "adult_swim_sealab_2021_bumpers"),
        _half_hour("as_prime_harvey_birdman_tv", 2,
                   "adult_swim_harvey_birdman_attorney_at_law_bumpers"),
        "as_prime_home_movies_tv",
        _half_hour("as_prime_twelve_oz_mouse_tv", 2),
    ]),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    outro=branding.BRANDING_ADULT_SWIM.outro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

# 22:00-24:00 Tue/Thu and Sunday. The 2005-onward originals.
# The Venture Bros. (81 episodes) is the other flagship that was absent. Nine
# half-hours, the eleven-minute shows paired as above.
AS_ORIGINALS_B = Block(
    name="Adult Swim",
    items=OrderedCollection([
        _with_bumpers("as_prime_venture_bros_tv",
                      "adult_swim_the_venture_bros_bumpers"),
        _half_hour("as_prime_robot_chicken_tv", 2,
                   "adult_swim_robot_chicken_bumpers"),
        _half_hour("as_prime_metalocalypse_tv", 2,
                   "adult_swim_metalocalypse_bumpers"),
        _with_bumpers("as_prime_boondocks_tv",
                      "adult_swim_the_boondocks_bumpers"),
        _with_bumpers("as_prime_rick_and_morty_tv",
                      "adult_swim_rick_and_morty_bumpers"),
        _half_hour("as_prime_eric_andre_tv", 2,
                   "adult_swim_the_eric_andre_show_bumpers"),
        _half_hour("as_prime_steve_brule_tv", 2,
                   "adult_swim_check_it_out_with_dr_steve_brule_bumpers"),
        _half_hour("as_prime_frisky_dingo_tv", 2),
        "as_prime_black_dynamite_tv",
    ]),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    outro=branding.BRANDING_ADULT_SWIM.outro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

# --- The Midnight Run (23:00 - 02:00) ---------------------------------------

# Attack on Titan Junior High, 12 episodes, one a Friday. The other appointment
# the coverage audit had been holding: too short to strip, and a parody that
# only works if you have seen the show it is parodying -- which is the block's
# own anchor, and its rerun bed for the other 40 weeks.
ATTACK_ON_TITAN_JUNIOR_HIGH = _with_bumpers(annual_show(
    show_title="Attack on Titan Junior High",
    episodes_per_season=[12],
    premiere_year=2026,
    premiere_season=("SUMMER", "FRIDAY"),
    frequency=["FRIDAY"],
    reruns="attack_on_titan_tv",
    loop=True
), "toonami_attack_on_titan_bumpers")

# 23:00-24:00. The anchor hour: the same three every night, which is what makes
# it an hour you can tune into rather than a pool. It was two, and two
# 24-minute episodes leave a third pick at about 23:50 -- which wrapped to
# Attack on Titan again, every night. Space Dandy is the third: episodic,
# shuffled, and taken out of the 00:00 run so it cannot air in both.
#
# The block exists in two forms because `frequency` does not gate the airing.
# `_find_active_episode` returns the current episode for *any* date inside the
# season window -- the frequency only paces how fast the episode index moves --
# so an appointment sitting in a block that runs seven nights a week airs the
# same episode all seven of them. Disney's Saturday events avoid this by living
# in a Saturday-only slot; the same trick here is a Friday-only variant. See
# reference/next-session.md on the Good Times version of this bug.
_MIDNIGHT_RUN_TAIL = [
    _with_bumpers(_episodes("Cowboy Bebop", "Chronological"),
                  "toonami_cowboy_bebop_bumpers"),
    _with_bumpers(_episodes("Space Dandy", "Shuffle"),
                  "toonami_space_dandy_bumpers"),
]

MIDNIGHT_RUN = Block(
    name="Adult Swim: The Midnight Run",
    items=DailyOrderedCollection(
        [_with_bumpers("attack_on_titan_tv", "toonami_attack_on_titan_bumpers")]
        + _MIDNIGHT_RUN_TAIL
    ),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

# Friday only. Same hour, with the premiere in the anchor slot instead of the
# rerun bed, so Junior High goes out at 23:00 on a Friday and nowhere else.
MIDNIGHT_RUN_PREMIERE = Block(
    name="Adult Swim: The Midnight Run",
    items=DailyOrderedCollection([ATTACK_ON_TITAN_JUNIOR_HIGH] + _MIDNIGHT_RUN_TAIL),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

# 00:00-02:00. The rest of the run, and its own block rather than two more
# hours of the one above: DailyOrderedCollection resets at midnight, so a
# single block spanning 23:00-02:00 would play its first items twice.
# The four shows most people mean by "Adult Swim anime" are Bebop, Champloo,
# FLCL and Space Dandy. One of the four used to air on this channel; Bebop and
# Space Dandy are in the 23:00 hour, Champloo and FLCL here.
MIDNIGHT_RUN_LATE = Block(
    name="Adult Swim: The Midnight Run",
    items=RandomCollection([
        _episodes("Samurai Champloo", "Chronological"),
        _with_bumpers(_episodes("FLCL", "Chronological"), "toonami_flcl_bumpers"),
        _with_bumpers(_episodes("Neon Genesis Evangelion", "Chronological"),
                      "toonami_neon_genesis_evangelion_bumpers"),
        _with_bumpers(_episodes("Fullmetal Alchemist Brotherhood", "Chronological"),
                      "toonami_fullmetal_alchemist_brotherhood_bumpers"),
        _episodes("Death Note", "Chronological"),
        _episodes("Primal", "Chronological"),
    ]),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

# 02:00-06:00, every night but Saturday. The acquisitions, which is where they
# historically sat -- the old grid had them at 20:00 as the marquee and the
# Williams Street originals behind them at 23:00, which is backwards.
#
# Six shows could not fill four hours without airing each of them twice. The
# overnight is also where Adult Swim reran its own half-hour originals, so four
# of those join the six acquisitions: ten shows against about ten picks. Named
# `as_late_*` feeds keep this shuffled rerun wheel independent from chronological
# prime and FOX access. Black Dynamite is left out because Be Kind Rewind carries
# the 2009 film, and the overnight is when it airs.
AS_LATE = Block(
    name="Adult Swim",
    items=OrderedCollection([
        _with_bumpers("as_late_king_of_the_hill_tv",
                      "adult_swim_king_of_the_hill_bumpers"),
        _with_bumpers("as_late_venture_bros_tv",
                      "adult_swim_the_venture_bros_bumpers"),
        _with_bumpers("as_late_family_guy_tv",
                      "adult_swim_family_guy_bumpers"),
        "as_late_home_movies_tv",
        _with_bumpers("as_late_futurama_tv",
                      "adult_swim_futurama_bumpers"),
        _with_bumpers("as_late_boondocks_tv",
                      "adult_swim_the_boondocks_bumpers"),
        "as_late_american_dad_tv",
        "as_late_bobs_burgers_tv",
        _half_hour("as_late_robot_chicken_tv", 2,
                   "adult_swim_robot_chicken_bumpers"),
        "as_late_archer_tv",
    ]),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

# ==============================================================================
# 7. FOX PRIMETIME
# ==============================================================================

def _fox_access(companion, filler="fox_weekday_futurama_tv"):
    """Simpsons and one companion, then a FOX filler show if 19:00 has room.

    The filler starts only before 20:00, so it plays when the pair finishes
    early and is skipped when a late 18:00 hour has pushed the pair back. It
    used to be Cartoon Network prime bridged in to the top of the hour; a FOX
    show keeps the hour FOX's (operator, 2026-10-18). Starting a few minutes
    late is fine, dead air is not, so nothing here waits for a clock time: if
    the filler ends before 20:00, prime is bridged in for the rest.
    """
    return Block(
        name="FOX Primetime",
        items=["fox_weekday_simpsons_tv", companion, filler],
        fill_strategy="bridge",
        use_epg_group=False,
    )


# Futurama fills, except on Tuesday, where it is the companion: King of the
# Hill fills instead of a second Futurama in a row.
FOX_WEEKDAY = {
    "MONDAY": _fox_access("fox_weekday_king_of_the_hill_tv"),
    "TUESDAY": _fox_access("fox_weekday_futurama_tv", filler="fox_weekday_king_of_the_hill_tv"),
    "WEDNESDAY": _fox_access("fox_weekday_family_guy_tv"),
    "THURSDAY": _fox_access("fox_weekday_american_dad_tv"),
    "FRIDAY": _fox_access("fox_weekday_bobs_burgers_tv"),
}

# Nine twenty-minute playout episodes cover the Sunday window without wrapping.
# Simpsons opens and the three original FOX-era anchors each get one rerun;
# every pull advances its Sunday-only feed.
FOX_PRIMETIME = Block(
    name="FOX Primetime",
    items=DailyOrderedCollection([
        "fox_sunday_simpsons_tv",
        "fox_sunday_king_of_the_hill_tv",
        "fox_sunday_family_guy_tv",
        "fox_sunday_bobs_burgers_tv",
        "fox_sunday_futurama_tv",
        "fox_sunday_american_dad_tv",
        "fox_sunday_simpsons_tv",
        "fox_sunday_family_guy_tv",
        "fox_sunday_king_of_the_hill_tv",
    ]),
    use_epg_group=False
)

# ==============================================================================
# 8. SEASONAL VARIANTS
# ==============================================================================

# Summer is the season this channel is remembered for. Through June to August
# the CN originals take the weekday 10:00-12:00 slot from the syndication
# package, so school-holiday mornings run Cartoon Cartoons at 08:00 straight
# into the full CN rotation. SeasonalBlock ramps, so it fades in over May and
# peaks mid-June to mid-July rather than switching on June 1st.
#
# The old summer swap gave the same two-hour slots to CARTOON_CARTOONS and
# CN_MODERN a second time, which was the same five shows at 08:00 and 10:00.
# CN_PRIME has ten shows and returns in the evening on its own named feeds.
CN_MIDDAY_BLOCK = SeasonalBlock(
    base=SYNDICATION_HOUR,
    seasonal={
        "SUMMER": Swap(CN_PRIME)
    }
)

# Weekdays at noon. Spring adds the Turtles, as it has since before the
# restructure.
CN_NOON_BLOCK = SeasonalBlock(
    base=MARVEL_HOUR,
    seasonal={
        "SPRING": Swap(MARVEL_SPRING_HOUR)
    }
)

# ==============================================================================
# 9. MARATHON COLLECTIONS
# ==============================================================================

DBZ_SAGAS = RandomCollection([
    "dbz_saiyan_saga_tv",
    "dbz_frieza_saga_tv",
    "dbz_cell_games_tv"
])

# Cowboy Bebop's complete run with the film in its right place between
# episodes 22 and 23.
COWBOY_BEBOP_COMPLETE = MarathonSequence([
    {"title": "Cowboy Bebop Eps 1-22", "query": 'show_title:"Cowboy Bebop" AND season_number:1 AND episode_number:[1 TO 22]', "order": "Chronological", "media_type": "show"},
    {"title": "Cowboy Bebop: The Movie", "query": 'show_title:"cowboy bebop" AND season_number:0 AND episode_number:2', "media_type": "movie"},
    {"title": "Cowboy Bebop Eps 23-26", "query": 'show_title:"Cowboy Bebop" AND season_number:1 AND episode_number:[23 TO 26]', "order": "Chronological", "media_type": "show"}
])

# Thanksgiving and New Year's Eve. Both were real Toonami traditions.
TOONAMI_MARATHON = RandomCollection([
    {"title": "Dragon Ball Z", "order": "Chronological"},
    {"title": "Naruto", "order": "Chronological"},
    {"title": "One Piece", "order": "Chronological"},
    {"title": "Yu Yu Hakusho", "order": "Chronological"},
    {"title": "Samurai Jack", "order": "Chronological"},
])

# The first Saturday of the month, in the daytime hours. The Simpsons marathon
# that used to hold 16:00-22:00 is gone: The Simpsons is Fox and never aired on
# Cartoon Network, so a six-hour takeover was the wrong flag on this channel.
CN_MARATHON = RandomCollection([
    {"title": "Adventure Time", "order": "Chronological"},
    {"title": "Steven Universe", "order": "Chronological"},
    {"title": "Ed, Edd n Eddy", "order": "Chronological"},
    {"title": "Dexter's Laboratory", "order": "Chronological"},
    {"title": "The Powerpuff Girls", "order": "Chronological"},
])


def _dbz_movie(title):
    # The library stores all of the original films as Dragon Ball Z season 0
    # episodes, not movie entities. Title phrases keep the curated trilogies
    # stable even if special episode numbers are later renumbered.
    return {
        "title": title,
        "query": f'type:episode AND show_title:"Dragon Ball Z" AND season_number:0 AND title:"{title}"',
        "order": "Chronological",
        # It is indexed as an episode but behaves as a finite feature inside
        # marathon assembly; this flag makes the engine play exactly one.
        "media_type": "movie",
    }


# A rare event chooses one related three-film bill and preserves its order.
DBZ_MOVIE_TRILOGIES = [
    MarathonSequence([
        _dbz_movie("Dead Zone"),
        _dbz_movie("The World's Strongest"),
        _dbz_movie("The Tree of Might"),
    ]),
    MarathonSequence([
        _dbz_movie("Lord Slug"),
        _dbz_movie("Cooler's Revenge"),
        _dbz_movie("The Return of Cooler"),
    ]),
    MarathonSequence([
        _dbz_movie("Broly: The Legendary Super Saiyan"),
        _dbz_movie("Broly: Second Coming"),
        _dbz_movie("Bio-Broly"),
    ]),
]

# ==============================================================================
# 10. HOLIDAY COLLECTIONS
# ==============================================================================

# `common.HALLOWEEN_TEEN_FRIGHTS` leads with Gravity Falls, which is Disney's.
# CN's teen-hours Halloween is built from CN's own two Halloween shows.
CN_HALLOWEEN = RandomCollection([
    "courage_tv",
    "infinity_train_tv",
    "halloween_animated_tv",
])
