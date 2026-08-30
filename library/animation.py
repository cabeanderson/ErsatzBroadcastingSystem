"""
Cartoon Network Content
=======================
Three networks sharing one dial position, dayparted so each owns the hours it
actually held: the vault at breakfast and lunch, Cartoon Network's own shows
through the middle of the day, Toonami after school, and Adult Swim from 20:00
straight through to 06:00.

The old grid handed 27 hours a week to Disney and 13 to Nickelodeon while the
block called "Cartoon Network Classics" was half MTV and Kids' WB. Both of
those channels are now built and own that content outright, so everything
borrowed has gone back and the hours have been given to the 460+ episodes of
CN originals and the eight owned anime series that had never aired. See
reference/cartoon-network-review.md for the audit this was built from.

Two structural rules:

**Adult Swim runs last, not first.** 20:00-23:00 is the Williams Street
originals, 23:00-02:00 the Midnight Run of anime, and 02:00-06:00 the
acquisitions -- King of the Hill, Family Guy, Futurama -- which is the order
the real thing ran in and the reverse of what this channel used to do.

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
    RandomCollection, OrderedCollection, DailyOrderedCollection,
    MarathonSequence, Block, Program
)
from scripts.logic.factories import annual_show
from scripts.logic.models import Swap, ContentItem
from scripts.logic.calendar.seasonal import SeasonalBlock
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


# ==============================================================================
# 1. THE VAULT (06:00-08:00 daily, 12:00-14:00 weekdays, Sunday midday)
# ==============================================================================

# The theatrical shorts and the Hanna-Barbera library. This used to hold
# 02:00-06:00, which was the single largest historical inversion in the grid --
# 28 hours a week of Yogi Bear in the slot Adult Swim actually occupied. It
# keeps the same number of hours; they are now the ones a vault belongs in.
THE_VAULT = Block(
    name="The Vault",
    items=RandomCollection([
        {"title": "Looney Tunes"},
        {"title": "Tom and Jerry"},
        {"title": "Popeye the Sailor"},
        {"title": "The Flintstones"},
        {"title": "The Jetsons"},
        {"title": "Yogi Bear"},
        {"title": "Hong Kong Phooey"},
    ]),
    use_epg_group=False
)

# 08:00-10:00 Saturday. The one block in the old grid that was already right.
# "Superman" by key, not title: the 1941 Fleischer shorts are nine minutes
# each and a different show from Superman: The Animated Series, which airs in
# Action Hour six hours later.
SATURDAY_MORNING = Block(
    name="Saturday Morning Cartoons",
    items=OrderedCollection([
        {"title": "Scooby-Doo, Where Are You!"},
        {"title": "Looney Tunes"},
        {"title": "Tom and Jerry"},
        {"title": "The Flintstones"},
        {"title": "The Jetsons"},
        {"title": "Popeye the Sailor"},
        {"title": "Yogi Bear"},
        "superman_fleischer_tv",
    ]),
    use_epg_group=False
)

# 08:00-10:00 Sunday. Three Scooby series, 104 episodes, which is enough to be
# its own thing rather than a guest in the vault.
THE_SCOOBY_BLOCK = Block(
    name="The Scooby Block",
    items=RandomCollection([
        {"title": "Scooby-Doo, Where Are You!"},
        {"title": "The Scooby-Doo Show"},
        {"title": "What's New Scooby-Doo"},
    ]),
    use_epg_group=False
)

# ==============================================================================
# 2. CARTOON NETWORK'S OWN SHOWS
# ==============================================================================

# 08:00-10:00 weekdays, 10:00-12:00 Saturday, 17:00-20:00 Sunday.
#
# The actual Cartoon Cartoons, which is what the block that used to carry this
# name was not: it held Daria (MTV), Animaniacs and Pinky and the Brain (Kids'
# WB) and Gravity Falls and The Owl House (Disney), and CN's own originals held
# five hours of the week. Ed, Edd n Eddy joins them here -- CN's longest-running
# original, previously filed inside the Nicktoons Vault.
CARTOON_CARTOONS = Block(
    name="Cartoon Cartoons",
    items=RandomCollection([
        {"title": "Dexter's Laboratory"},
        {"title": "The Powerpuff Girls"},
        {"title": "Johnny Bravo"},
        {"title": "Ed, Edd n Eddy"},
        {"title": "Courage the Cowardly Dog"},
    ]),
    use_epg_group=False
)

# 10:00-12:00 weekdays, 14:00-17:00 Sunday. 564 episodes that had never aired.
#
# Two departures from the review's list. Primal is TV-MA and aired on Adult
# Swim, not on daytime CN -- it is in the Midnight Run instead. Infinity Train
# (2019) moves the other way, out of Cartoon Cartoons: it is a modern show and
# was never part of that 1996-2003 brand. Steven Universe is one entry rather
# than two because the title also matches Steven Universe Future.
CN_MODERN = Block(
    name="Cartoon Network",
    items=RandomCollection([
        {"title": "Adventure Time"},
        {"title": "Steven Universe"},
        {"title": "Samurai Jack"},
        {"title": "Over the Garden Wall"},
        {"title": "Infinity Train"},
    ]),
    use_epg_group=False
)

# 17:00-20:00 Friday, in place of Toonami. The Friday-night premiere block,
# ordered rather than shuffled, because the point of it was that it was an
# event with a running order.
CARTOON_CARTOON_FRIDAY = Block(
    name="Cartoon Cartoon Fridays",
    items=OrderedCollection([
        {"title": "Dexter's Laboratory"},
        {"title": "The Powerpuff Girls"},
        {"title": "Johnny Bravo"},
        {"title": "Ed, Edd n Eddy"},
        {"title": "Courage the Cowardly Dog"},
        {"title": "Adventure Time"},
        {"title": "Steven Universe"},
    ]),
    use_epg_group=False
)

# ==============================================================================
# 3. SYNDICATION AND ACTION
# ==============================================================================

# 12:00-14:00 Saturday. The period-correct syndication package -- 900+ episodes
# that were sitting in the library behind a block (`SYNDICATED_CARTOONS`) that
# nothing referenced. Gargoyles is not here; it went back to Disney.
SYNDICATION_HOUR = Block(
    name="Syndication Hour",
    items=RandomCollection([
        {"title": "ThunderCats"},
        {"title": "He-Man and the Masters of the Universe"},
        {"title": "The Transformers"},
        {"title": "Teenage Mutant Ninja Turtles"},
        {"title": "Beast Wars Transformers"},
        {"title": "Inspector Gadget"},
        {"title": "Captain Planet and the Planeteers"},
        {"title": "The Tick"},
        {"title": "Street Sharks"},
        {"title": "Mister T"},
    ]),
    use_epg_group=False
)

# 14:00-17:00 weekdays and Saturday, the ramp into Toonami. This is the old
# SUPERHERO_HOUR, MARVEL_HOUR and the never-referenced ACTION_ANIMATION folded
# into one block and moved out of the 08:00 slot, where a superhero hour was
# competing with the cartoons for the morning.
ACTION_HOUR = Block(
    name="Action Hour",
    items=OrderedCollection([
        {"title": "Batman: The Animated Series", "order": "Chronological"},
        {"title": "The New Batman Adventures", "order": "Chronological"},
        {"title": "Superman: The Animated Series", "order": "Chronological"},
        {"title": "Justice League", "order": "Chronological"},
        {"title": "Batman Beyond", "order": "Chronological"},
        "xmen_animated_tv",
        {"title": "Spider-Man"},
        # The library title is "SWAT Kats The Radical Squadron"; the phrase
        # matches its prefix. `type:episode` was missing here and the query
        # was returning show containers alongside episodes.
        {"title": "SWAT Kats",
         "query": 'type:episode AND show_title:"SWAT Kats*"',
         "order": "Chronological"},
    ]),
    use_epg_group=False
)

# The spring variant, kept from the old grid: the same slot leans Marvel and
# the Turtles for the season. SeasonalBlock ramps rather than hard-swaps, so it
# fades in over the spring and peaks mid-March to mid-April.
MARVEL_HOUR = Block(
    name="Marvel Action Hour",
    items=OrderedCollection([
        "xmen_animated_tv",
        {"title": "Spider-Man"},
        {"title": "Teenage Mutant Ninja Turtles"},
        # The library title is "SWAT Kats The Radical Squadron"; the phrase
        # matches its prefix. `type:episode` was missing here and the query
        # was returning show containers alongside episodes.
        {"title": "SWAT Kats",
         "query": 'type:episode AND show_title:"SWAT Kats*"',
         "order": "Chronological"},
    ]),
    use_epg_group=False
)

# ==============================================================================
# 4. CARTOON THEATRE (12:00-14:00 Sunday)
# ==============================================================================

# One film, from the pool that is actually CN-shaped. The old Sunday gave 11
# hours a week to ANIMATION_SHOWCASE -- Ghibli, Pixar, DreamWorks and Disney
# features, none of which ever aired on Cartoon Network -- while the films that
# did were never scheduled.
#
# Akira and Ghost in the Shell are the two the review listed that are not here:
# both are R-rated and this is a Sunday lunchtime slot. They run in the Saturday
# overnight Toonami block instead.
CARTOON_THEATRE = Block(
    name="Cartoon Theatre",
    items=RandomCollection([
        {"title": "Batman: Mask of the Phantasm",
         "query": 'type:movie AND title:"Batman Mask of the Phantasm"',
         "media_type": "movie"},
        {"title": "The Iron Giant",
         "query": 'type:movie AND title:"The Iron Giant"',
         "media_type": "movie"},
        {"title": "The Transformers: The Movie",
         "query": 'type:movie AND title:"Transformers - The Movie"',
         "media_type": "movie"},
        {"title": "Titan A.E.",
         "query": 'type:movie AND title:"Titan A.E."',
         "media_type": "movie"},
        {"title": "Who Framed Roger Rabbit",
         "query": 'type:movie AND title:"Who Framed Roger Rabbit"',
         "media_type": "movie"},
        {"title": "Steven Universe: The Movie",
         "query": 'type:movie AND title:"Steven Universe The Movie"',
         "media_type": "movie"},
        {"title": "Dragon Ball Z: Battle of Gods",
         "query": 'type:movie AND title:"Dragon Ball Z - Battle of Gods"',
         "media_type": "movie"},
    ]),
    use_epg_group=False
)

# ==============================================================================
# 5. TOONAMI
# ==============================================================================

# 17:00-20:00 weekdays. The best block on the old channel and the one thing the
# restructure leaves alone, except that every show now carries its own bumper
# set instead of all of them sharing a 21-file generic pool.
#
# The `annual_show()` start dates are Contiguous Mode: each show walks its run
# one episode per weekday from the date given, so the block is a real strip
# rather than a shuffle. The start dates are anchors: they were calculated to
# put each show at a particular episode on 2026-03-17, and the four-day week
# below has moved where that lands. Recalculate if you want a specific episode
# on a specific day; nothing else depends on them.
#
# `loop_restart_season=False` and `reruns=` are new, and between them they close
# the strip's two dead stretches. `annual_show()` defaults `loop_restart_season`
# to the season half of `premiere_season`, which is "FALL" even in Contiguous
# Mode where no premiere season was given -- so a strip that finished its run
# in June sat dark until mid-September. False loops it straight over instead.
# The rerun bed then covers whatever is left, since a Program that resolves to
# nothing does not just go quiet: the block skips it, time does not advance,
# and the slot falls through to the circuit breaker.
TOONAMI_BLOCK = Block(
    name="Toonami",
    items=OrderedCollection([
        # Shuffle content doesn't need a start point
        {"title": "Sailor Moon", "query": 'show_title:"sailor moon" AND NOT show_title:"sailor moon crystal"', "order": "Shuffle"},

        # Monday to Thursday, not Monday to Friday: Friday evening is Cartoon
        # Cartoon Fridays now. `frequency` paces the episode index, so leaving
        # FRIDAY in it advanced the strip five slots a week while airing four,
        # quietly dropping an episode of every show every week.
        # Start Date: Today (Mar 17, 2026) -> S01E01
        annual_show(
            show_title="Dragon Ball",
            episodes_per_season=[28, 15, 14, 13, 13, 14, 13, 13, 30],
            start_date=date(2026, 3, 17),
            frequency=["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"],
            reruns="toonami_vault_tv",
            loop=True,
            loop_restart_season=False
        ),
        # Start Date: ~66 days ago to account for weekends -> S02E08 (Total Ep 47)
        _with_bumpers(annual_show(
            show_title="Dragon Ball Z",
            episodes_per_season=[39, 35, 33, 32, 26, 29, 25, 25, 47],
            start_date=date(2025, 12, 9), # Adjusted for weekdays
            frequency=["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"],
            reruns="toonami_vault_tv",
            loop=True,
            loop_restart_season=False
        ), "toonami_dragon_ball_z_bumpers"),
        # Start Date: ~9 days ago -> S01E08
        _with_bumpers(annual_show(
            show_title="Yu Yu Hakusho",
            episodes_per_season=[25, 41, 28, 18],
            start_date=date(2026, 3, 6), # Adjusted for weekdays
            frequency=["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"],
            reruns="toonami_vault_tv",
            loop=True,
            loop_restart_season=False
        ), "toonami_yu_yu_hakusho_bumpers"),
        # Start Date: ~37 days ago -> S02E01 (Total Ep 28)
        annual_show(
            show_title="Rurouni Kenshin",
            episodes_per_season=[27, 35, 33],
            start_date=date(2026, 1, 29), # Adjusted for weekdays
            frequency=["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"],
            reruns="toonami_vault_tv",
            loop=True,
            loop_restart_season=False
        ),
        # Start Date: ~25 days ago -> S01E20
        _with_bumpers(annual_show(
            show_title="Inuyasha",
            episodes_per_season=[27, 27, 27, 27, 27, 27, 7],
            start_date=date(2026, 2, 12), # Adjusted for weekdays
            frequency=["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"],
            reruns="toonami_vault_tv",
            loop=True,
            loop_restart_season=False
        ), "toonami_inuyasha_bumpers"),
        # Start Date: ~12 days ago -> S01E10
        _with_bumpers(annual_show(
            show_title="Naruto",
            episodes_per_season=[35, 48, 48, 48, 41],
            start_date=date(2026, 3, 3), # Adjusted for weekdays
            frequency=["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"],
            reruns="toonami_vault_tv",
            loop=True,
            loop_restart_season=False
        ), "toonami_naruto_bumpers"),
    ]),
    intro=branding.BRANDING_TOONAMI.intro,
    outro=branding.BRANDING_TOONAMI.outro,
    bumpers=branding.BRANDING_TOONAMI.bumpers,
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

# 17:00-20:00 Saturday. DailyOrderedCollection resets to index 0 each day, so
# DAIMA holds 17:00 every Saturday and the premiere lands at the same time each
# week -- the one thing an appointment cannot do is move around.
#
# Eight items at roughly 24 minutes covers the three hours without the
# collection wrapping, which matters here: a wrap would resolve the appointment
# a second time and re-air the premiere in the same evening.
TOONAMI_SATURDAY = Block(
    name="Toonami",
    items=DailyOrderedCollection([
        DRAGON_BALL_DAIMA,
        _with_bumpers({"title": "One Piece"}, "toonami_one_piece_bumpers"),
        _with_bumpers({"title": "Fullmetal Alchemist Brotherhood"},
                      "toonami_fullmetal_alchemist_brotherhood_bumpers"),
        _with_bumpers({"title": "Naruto"}, "toonami_naruto_bumpers"),
        _with_bumpers({"title": "Samurai Jack"}, "toonami_samurai_jack_bumpers"),
        {"title": "Justice League"},
        {"title": "Batman Beyond"},
        _with_bumpers({"title": "Dragon Ball Z"}, "toonami_dragon_ball_z_bumpers"),
    ]),
    intro=branding.BRANDING_TOONAMI.intro,
    outro=branding.BRANDING_TOONAMI.outro,
    bumpers=branding.BRANDING_TOONAMI.bumpers,
    use_epg_group=False
)

# 20:00-23:00 Saturday. The second half of Toonami Saturday, and a separate
# block rather than three more hours of the one above: continuing that
# collection would wrap it back to the DAIMA appointment. Same EPG name, so the
# guide reads as one six-hour Toonami.
TOONAMI_SATURDAY_VAULT = Block(
    name="Toonami",
    items=RandomCollection([
        _with_bumpers({"title": "Samurai Jack"}, "toonami_samurai_jack_bumpers"),
        _with_bumpers({"title": "Dragon Ball Z"}, "toonami_dragon_ball_z_bumpers"),
        _with_bumpers({"title": "Yu Yu Hakusho"}, "toonami_yu_yu_hakusho_bumpers"),
        _with_bumpers({"title": "Inuyasha"}, "toonami_inuyasha_bumpers"),
        _with_bumpers({"title": "One Piece"}, "toonami_one_piece_bumpers"),
        {"title": "Rurouni Kenshin"},
        {"title": "Justice League"},
        {"title": "Batman Beyond"},
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
        _with_bumpers({"title": "One Piece"}, "toonami_one_piece_bumpers"),
        _with_bumpers({"title": "Naruto"}, "toonami_naruto_bumpers"),
        _with_bumpers({"title": "Inuyasha"}, "toonami_inuyasha_bumpers"),
        _with_bumpers({"title": "Dragon Ball Z"}, "toonami_dragon_ball_z_bumpers"),
        _with_bumpers({"title": "Yu Yu Hakusho"}, "toonami_yu_yu_hakusho_bumpers"),
        {"title": "Rurouni Kenshin"},
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
# 6. ADULT SWIM (20:00 - 06:00)
# ==============================================================================

# 20:00-23:00 Mon/Wed/Fri. Williams Street, 2001-2005 -- the shows Adult Swim
# was actually built out of, five of which had never aired on this channel.
# Space Ghost Coast to Coast (81 episodes) is the one the whole block came
# from and was entirely absent.
AS_ORIGINALS_A = Block(
    name="Adult Swim",
    items=OrderedCollection([
        _with_bumpers({"title": "Space Ghost Coast to Coast", "order": "Shuffle"},
                      "adult_swim_space_ghost_coast_to_coast_bumpers"),
        _with_bumpers({"title": "The Brak Show", "order": "Shuffle"},
                      "adult_swim_the_brak_show_bumpers"),
        _with_bumpers({"title": "Aqua Teen Hunger Force", "order": "Shuffle"},
                      "adult_swim_aqua_teen_hunger_force_bumpers"),
        _with_bumpers({"title": "Sealab 2021", "order": "Shuffle"},
                      "adult_swim_sealab_2021_bumpers"),
        _with_bumpers({"title": "Harvey Birdman, Attorney at Law", "order": "Shuffle"},
                      "adult_swim_harvey_birdman_attorney_at_law_bumpers"),
        {"title": "Home Movies", "order": "Shuffle"},
        {"title": "12 oz. Mouse", "order": "Shuffle"},
    ]),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    outro=branding.BRANDING_ADULT_SWIM.outro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

# 20:00-23:00 Tue/Thu/Sat, and 23:00-02:00 Sunday. The 2005-onward originals.
# The Venture Bros. (81 episodes) is the other flagship that was absent.
AS_ORIGINALS_B = Block(
    name="Adult Swim",
    items=OrderedCollection([
        _with_bumpers({"title": "The Venture Bros.", "order": "Shuffle"},
                      "adult_swim_the_venture_bros_bumpers"),
        _with_bumpers({"title": "Robot Chicken", "order": "Shuffle"},
                      "adult_swim_robot_chicken_bumpers"),
        _with_bumpers({"title": "Metalocalypse", "order": "Shuffle"},
                      "adult_swim_metalocalypse_bumpers"),
        _with_bumpers({"title": "The Boondocks", "order": "Shuffle"},
                      "adult_swim_the_boondocks_bumpers"),
        _with_bumpers({"title": "Rick and Morty", "order": "Chronological"},
                      "adult_swim_rick_and_morty_bumpers"),
        _with_bumpers({"title": "The Eric Andre Show", "order": "Shuffle"},
                      "adult_swim_the_eric_andre_show_bumpers"),
        _with_bumpers({"title": "Check It Out! with Dr. Steve Brule", "order": "Shuffle"},
                      "adult_swim_check_it_out_with_dr_steve_brule_bumpers"),
        {"title": "Frisky Dingo", "order": "Shuffle"},
        {"title": "Black Dynamite", "order": "Shuffle"},
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

# 23:00-24:00. The anchor hour: two items, the same two every night, which is
# what makes it an hour you can tune into rather than a pool.
#
# The block exists in two forms because `frequency` does not gate the airing.
# `_find_active_episode` returns the current episode for *any* date inside the
# season window -- the frequency only paces how fast the episode index moves --
# so an appointment sitting in a block that runs seven nights a week airs the
# same episode all seven of them. Disney's Saturday events avoid this by living
# in a Saturday-only slot; the same trick here is a Friday-only variant. See
# reference/next-session.md on the Good Times version of this bug.
_MIDNIGHT_RUN_TAIL = [
    _with_bumpers({"title": "Cowboy Bebop", "order": "Chronological"},
                  "toonami_cowboy_bebop_bumpers"),
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
# single block spanning 23:00-02:00 would play its first two items twice.
# The four shows most people mean by "Adult Swim anime" are Bebop, Champloo,
# FLCL and Space Dandy. One of the four used to air on this channel.
MIDNIGHT_RUN_LATE = Block(
    name="Adult Swim: The Midnight Run",
    items=RandomCollection([
        {"title": "Samurai Champloo", "order": "Chronological"},
        _with_bumpers({"title": "FLCL", "order": "Chronological"}, "toonami_flcl_bumpers"),
        _with_bumpers({"title": "Neon Genesis Evangelion", "order": "Chronological"},
                      "toonami_neon_genesis_evangelion_bumpers"),
        _with_bumpers({"title": "Fullmetal Alchemist Brotherhood", "order": "Chronological"},
                      "toonami_fullmetal_alchemist_brotherhood_bumpers"),
        {"title": "Death Note", "order": "Chronological"},
        _with_bumpers({"title": "Space Dandy", "order": "Shuffle"},
                      "toonami_space_dandy_bumpers"),
        {"title": "Primal", "order": "Chronological"},
    ]),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

# 02:00-06:00, every night but Saturday. The acquisitions, which is where they
# historically sat -- the old grid had them at 20:00 as the marquee and the
# Williams Street originals behind them at 23:00, which is backwards.
AS_LATE = Block(
    name="Adult Swim",
    items=RandomCollection([
        _with_bumpers({"title": "King of the Hill", "order": "Shuffle"},
                      "adult_swim_king_of_the_hill_bumpers"),
        _with_bumpers({"title": "Family Guy", "order": "Shuffle"},
                      "adult_swim_family_guy_bumpers"),
        _with_bumpers({"title": "Futurama", "order": "Shuffle"},
                      "adult_swim_futurama_bumpers"),
        {"title": "American Dad!", "order": "Shuffle"},
        {"title": "Bob's Burgers", "order": "Shuffle"},
        {"title": "Archer", "order": "Chronological"},
    ]),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

# ==============================================================================
# 7. FOX PRIMETIME (20:00-23:00 Sunday)
# ==============================================================================

# The one non-CN, non-Adult-Swim block on the channel, kept because Sunday
# night animation is its own institution. Rick and Morty came out (Adult Swim's,
# and it airs in AS_ORIGINALS_B); King of the Hill and American Dad went in,
# which is what the block is actually about.
FOX_PRIMETIME = Block(
    name="FOX Primetime",
    items=OrderedCollection([
        {"title": "The Simpsons"},
        {"title": "King of the Hill"},
        {"title": "Bob's Burgers"},
        {"title": "Futurama"},
        {"title": "American Dad!"},
    ]),
    use_epg_group=False
)

# ==============================================================================
# 8. SEASONAL VARIANTS
# ==============================================================================

# Summer is the season this channel is remembered for, and the old grid had no
# summer treatment at all -- spring was the only season with a variant defined.
# Through June to August the CN originals take 08:00-14:00 on weekdays and the
# vault gives up its lunchtime slot. SeasonalBlock ramps, so it fades in over
# May and peaks mid-June to mid-July rather than switching on June 1st.
CN_MIDDAY_BLOCK = SeasonalBlock(
    base=CN_MODERN,
    seasonal={
        "SUMMER": Swap(CARTOON_CARTOONS)
    }
)

CN_NOON_BLOCK = SeasonalBlock(
    base=THE_VAULT,
    seasonal={
        "SUMMER": Swap(CN_MODERN)
    }
)

# Spring leans Marvel, as it did before the restructure -- the swap has just
# moved from the 08:00 superhero hour to the 14:00 action hour along with the
# content.
CN_AFTERNOON_BLOCK = SeasonalBlock(
    base=ACTION_HOUR,
    seasonal={
        "SPRING": Swap(MARVEL_HOUR)
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
