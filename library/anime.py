"""
Japanorama -- the Japanese broadcast day
========================================

**Identity (F2).** A Japanese network's whole day, not an after-school block.
Cartoon Network already runs the best three hours of anime on the lineup;
Toonami is a *block*, and a block is a different promise from a channel. This
one signs on in the morning and gets to 深夜アニメ -- deep-night anime -- by
23:00, which is a shape Toonami cannot have because it does not own a clock.

Stated positively, so it is not defined by what Toonami is not (F4): everything
here belongs to a schedule that runs from breakfast to the small hours, and the
back half of that schedule is the part American television never imported.

**Axis (F3): the clock, as a broadcast day.**

    02-06  The Rebroadcast   the vault, which is what the small hours are for
    06-08  Morning Cast      iyashikei -- camping, cooking, climbing
    08-12  The Kids' Hours   Pokémon, Dragon Ball, Sailor Moon -- syndication
    12-15  The Syndication Hour   One Piece, Naruto, InuYasha, Kenshin
    15-17  The Dragon Ball Hour   Z, GT and Super, in the after-school slot
    17-19  Teatime           the channel's own shows, and only its own
    19-21  Japanorama Theatre     the feature
    21-23  the named night   one strip a night
    23-24  Deep Night        深夜アニメ begins
    00-02  Deep Night        and runs to two

**TV-led with a real film shelf (F5).** 587 episodes nobody else names, plus
2,450 more shared with Toonami under the hours rule below, against 43 features.
That makes it television with a nightly feature rather than film with a bed --
the High Noon shape, not the Nightmare Theatre one. The feature still gets two
hours every night because 43 films at seven a week is a six-week cycle, which is
comfortably inside F6, and because the Ghibli shelf is the single best thing on
the channel.

**Every block sized against F6** -- nothing cycles faster than three weeks:

    Morning Cast   119 eps / 14 h wk   3.4 weeks
    Kids' Hours    490 eps / 28 h wk   7 weeks
    Syndication  1,095 eps / 21 h wk   21 weeks
    Dragon Ball    500 eps / 14 h wk   14 weeks
    Teatime        176 eps / 14 h wk   5 weeks
    Theatre         43 films / 7 wk    6 weeks
    Deep Night      86 eps + 11 films  2.6 weeks, with the vault behind it

--------------------------------------------------------------------------
THE HOURS RULE
--------------------------------------------------------------------------

One channel overlaps this one and it overlaps it heavily: **Cartoon Network's
Toonami and Adult Swim** hold the entire shonen canon -- One Piece, Naruto,
Dragon Ball Z, InuYasha, Sailor Moon, Yu Yu Hakusho, Rurouni Kenshin, Attack on
Titan, Fullmetal Alchemist: Brotherhood, Death Note, Evangelion, Cowboy Bebop.
Between them that is about 2,450 episodes, four times everything else this
channel has. Ceding them would leave Japanorama at 587 episodes and a fortnight's
cycle; taking them without a rule would break C1 on a dozen titles a night.

So: the **C2 rung-1 and rung-2 fix together** -- a different presentation, kept
apart by an hours rule written at the resolution Cartoon Network's grid actually
has. Toonami runs these shows as a first-run strip, chronological, after school.
Japanorama runs them as **daytime syndication**: shuffled, drop in anywhere. The
`_syndication_tv` keys in `sources.py` carry `Shuffle` where Toonami's carry
`Chronological`, so the split is enforced at the key level and not by this grid
remembering to behave (C3).

Cartoon Network airs anime in exactly four windows:

    17:00-20:00  Mon-Fri    Toonami
    17:00-23:00  Saturday   Toonami Saturday, and its vault
    23:00-02:00  nightly    the Midnight Run  (Attack on Titan is the anchor)
    02:00-06:00  Sat night  Toonami: The Midnight Run

Which leaves 06:00-17:00 every day, and 20:00-23:00 on the six nights that are
not Saturday. **Every shared title on this channel is scheduled inside that
window and nowhere else**, which is why the syndication keys appear only in
`MORNING_CAST` through `THE_DRAGON_BALL_HOUR` (06:00-17:00) and in `SHONEN_NIGHT`
(Friday 21:00-23:00).

Three consequences worth writing down, because each one moved a decision:

* **Teatime (17:00-19:00) is inside Toonami's window**, so it draws no shared
  title at all -- Assassination Classroom, Ranking of Kings, Girls und Panzer,
  One-Punch Man and DAN DA DAN, every one of them Japanorama's alone.
* **Attack on Titan is not on this channel.** It is the daily anchor of Cartoon
  Network's Midnight Run at 23:00, so an episode of it anywhere near this
  channel's 23:00 is a coin-flip collision rather than a rule. Friday's shonen
  night takes Fullmetal Alchemist: Brotherhood and Death Note instead, which sit
  in CN's 00:00-02:00 `MIDNIGHT_RUN_LATE` and cannot reach 21:00-23:00.
* **Akira and Ghost in the Shell** carry Toonami bumper sets and play on that
  same Midnight Run. `anime_canon_movie` holds them and is scheduled at
  19:00-21:00 only.

The one thing the rule does not cover is Cartoon Network's date-anchored
marathons -- July 4th Dragon Ball Z, Memorial Day Cowboy Bebop, Thanksgiving and
New Year's Toonami -- which take whole days. Those are four days a year against
a shuffled daytime pool of 490 to 1,095 episodes; the exposure is real and it is
small, and it is recorded here rather than engineered around.

**Nothing was taken from Cartoon Network to build this channel.** Its grid is
unchanged and its `animation.py` keys are untouched.
"""

from scripts.logic.structures import (
    Block, RandomCollection, OrderedCollection, DailyOrderedCollection,
    MarathonSequence,
)
from scripts.logic.factories import annual_show
from scripts.library.queries import movie_by_title_year

# ==============================================================================
# 1. MORNING -- 06:00-08:00
# ==============================================================================

# Iyashikei, which is a genre in Japan and nowhere else: shows in which nothing
# much happens on purpose. Four of them, 119 episodes, and they are the reason
# the channel can open at six in the morning with something other than a rerun.
#
# Encouragement of Climb is here as seasons 2-4 only. Its first season is
# twelve 3.5-minute shorts and belongs to the filler key, not to a strip -- the
# G2 split, applied inside a single show rather than between two.
MORNING_CAST = Block(
    name="Morning Cast",
    items=RandomCollection([
        "laid_back_camp_tv",
        "yama_no_susume_tv",
        "campfire_cooking_tv",
        "okitsura_tv",
    ]),
)

# ==============================================================================
# 2. THE KIDS' HOURS -- 08:00-12:00
# ==============================================================================

# The first of the four syndication blocks, and the softest. Pokémon has been
# unscheduled on this lineup for as long as the lineup has existed -- the
# lineup audit lists its 82 episodes as the largest unhomed animated show --
# and Toonami took it in the 2026-09-03 pass as the fourth show on its anime
# bench. It runs there after school and here in the morning.
#
# Sailor Moon Crystal is the 2014 remake and a separate 41-episode key: the
# phrase `show_title:"Sailor Moon"` returns it too, which is the G10 trap
# animation.py already carries the exclusion for.
THE_KIDS_HOURS = Block(
    name="The Kids' Hours",
    items=RandomCollection([
        "pokemon_syndication_tv",
        "dragon_ball_syndication_tv",
        "sailor_moon_syndication_tv",
        "sailor_moon_crystal_tv",
    ]),
)

# ==============================================================================
# 3. THE SYNDICATION HOUR -- 12:00-15:00
# ==============================================================================

# The long shows, in the middle of the day, shuffled. 1,095 episodes is a
# twenty-one week cycle at three hours a day, which is the slowest wheel on the
# channel and deliberately so: this is the block a viewer is most likely to
# land on cold, and One Piece at episode 300 has to be enjoyable without the
# 299 before it. Shuffle is not a compromise here, it is the format.
THE_SYNDICATION_HOUR = Block(
    name="The Syndication Hour",
    items=RandomCollection([
        "one_piece_syndication_tv",
        "naruto_syndication_tv",
        "inuyasha_syndication_tv",
        "rurouni_kenshin_syndication_tv",
    ]),
)

# ==============================================================================
# 4. THE DRAGON BALL HOUR -- 15:00-17:00
# ==============================================================================

# One franchise, two hours, every afternoon -- G3's "a strip that means
# something is worth more than a strip with more variety in it", taken as far
# as it goes. Z, GT and Super are 500 episodes between them and the hour reads
# as *Dragon Ball is on at three* rather than *anime is on*.
#
# GT is the only one of the three no other channel touches. It is also the one
# nobody defends, which is exactly why it belongs in a strip and not in prime.
THE_DRAGON_BALL_HOUR = Block(
    name="The Dragon Ball Hour",
    items=RandomCollection([
        "dragon_ball_z_syndication_tv",
        "dragon_ball_gt_tv",
        "dragon_ball_super_syndication_tv",
    ]),
)

# ==============================================================================
# 5. TEATIME -- 17:00-19:00
# ==============================================================================

# Cartoon Network's Toonami is on the air 17:00-20:00, so this block draws no
# shared title -- see the hours rule in the module docstring. Five shows that
# are Japanorama's alone, all of them episodic enough to tune into cold.
TEATIME = Block(
    name="Teatime",
    items=RandomCollection([
        "assassination_classroom_tv",
        "ranking_of_kings_tv",
        "girls_und_panzer_tv",
        "one_punch_man_tv",
        "dandadan_tv",
    ]),
)

# ==============================================================================
# 6. JAPANORAMA THEATRE -- 19:00-21:00
# ==============================================================================

# 43 features. The whole shelf on weeknights, the canon on Saturday, Ghibli all
# of Sunday.
#
# 19:00 rather than 20:00 is measured, not chosen: C7 recorded 18:00-20:00 as
# the emptiest film hour on the lineup and four channels starting features at
# once from 20:00. Be Kind Rewind already opens at 18:00, so 19:00 is the last
# uncontested start left.
JAPANORAMA_THEATRE = Block(
    name="Japanorama Theatre",
    items=RandomCollection([
        "ghibli_movie",
        "anime_arthouse_movie",
        "anime_modern_movie",
        "evangelion_movie",
        "dragon_ball_movie",
    ]),
)

# Saturday. The canon and the franchise pictures -- the loud half of the shelf,
# on the night for it. `anime_canon_movie` is Akira, Ghost in the Shell, Dirty
# Pair and the 1986 Transformers; the first two are also on Cartoon Network's
# Midnight Run at 23:00-02:00, which this slot ends two hours clear of.
SATURDAY_THEATRE = Block(
    name="Japanorama Theatre",
    items=RandomCollection([
        "anime_canon_movie",
        "dragon_ball_movie",
        "anime_arthouse_movie",
    ]),
)

# Sunday belongs to Ghibli, all 23 films of it, and it is the one block on the
# channel with a single key in it. Twenty-three films at two a Sunday is a
# three-month cycle -- slow enough that Totoro in the evening stays an event.
GHIBLI_SUNDAY = Block(
    name="Ghibli Sunday",
    items=OrderedCollection(["ghibli_movie"]),
)

# ==============================================================================
# 7. THE NAMED NIGHTS -- 21:00-23:00
# ==============================================================================

# One strip a night, gated by the weekday arm of the schedule rather than by an
# appointment's own `frequency` -- `frequency` paces an episode index, it does
# not stop a show airing on other days (G5).
#
# None of these is an `annual_show`, so none of them can hit the replay trap
# that took Must See Thursday off Good Times: they are plain collections of
# content keys, which advance an episode rather than pinning one.

# Monday and Tuesday are the two long modern runs, chronological, because they
# are the two shows on the channel that reward being followed.
#
# One key each, wrapped in an OrderedCollection rather than handed to `items`
# bare. `_get_next_block_item` takes a collection (anything with `.pick`) or a
# list and returns None for anything else, so `items="frieren_chronological_tv"`
# plays nothing, the block reports 0 items and the slot stalls into the circuit
# breaker. A one-item list would resolve once and then exhaust two hours short;
# a one-item collection keeps handing the same key back, which is what a strip
# is. `example_channel.py` documents the bare-string form -- it has never worked.
FRIEREN_NIGHT = Block(
    name="Frieren", items=OrderedCollection(["frieren_chronological_tv"]))
VINLAND_NIGHT = Block(
    name="Vinland Saga", items=OrderedCollection(["vinland_saga_chronological_tv"]))

# Wednesday is the music night. Shinichirō Watanabe's two jazz shows, which are
# the only pair on the channel that share an author and a subject.
MUSIC_NIGHT = Block(
    name="The Music Night",
    items=RandomCollection(["carole_and_tuesday_tv", "kids_on_the_slope_tv"]),
)

# Thursday is the quiet night: two shows built out of self-contained episodes
# about someone arriving somewhere, which is as close to an anthology as this
# library gets.
QUIET_NIGHT = Block(
    name="The Quiet Night",
    items=RandomCollection(["violet_evergarden_tv", "kinos_journey_tv"]),
)

# Friday is the one night a shared title appears outside daytime, and it is
# inside the rule: Cartoon Network runs Fullmetal Alchemist: Brotherhood and
# Death Note in `MIDNIGHT_RUN_LATE` at 00:00-02:00, three hours after this
# block ends. Attack on Titan is deliberately absent -- it anchors CN's 23:00
# Midnight Run every night of the week, and 21:00-23:00 abuts that too closely
# for a rule to hold it.
SHONEN_NIGHT = Block(
    name="Shonen Friday",
    items=RandomCollection([
        "fullmetal_alchemist_brotherhood_tv",
        "death_note_tv",
    ]),
)

# Sunday is the rerun half of Monday and Tuesday: the same two shows, shuffled,
# under their second registration. New episodes on weeknights, reruns at the
# weekend -- two keys per show, because a key carries its playback order (G8).
SUNDAY_REPLAY = Block(
    name="The Sunday Replay",
    items=RandomCollection(["frieren_tv", "vinland_saga_tv"]),
)

# ------------------------------------------------------------------------------
# Saturday: the limited series
# ------------------------------------------------------------------------------
#
# Three runs too short to strip, one to a season of the year (G6). Episode
# counts are off the disk, not off `library-tv.tsv` -- the manifest counts
# `extras/` folders and reads Macross Plus as 13 episodes when the OVA is four
# (V4). A window opened over episodes that resolve to nothing stalls the block.
#
# Keyed by season rather than stacked in a collection, which is the shape
# Nightmare Theatre arrived at after two failures: `annual_show(reruns=...)`
# hangs the bed on the Program, so the first entry of a stack resolves every
# week and the rest never air, and a Program that resolves to nothing yields
# the whole slot rather than passing the turn along. A label-keyed dict
# resolves exactly one branch a night and the question does not arise.

BLUE_EYE_SAMURAI = annual_show(
    show_title="Blue Eye Samurai",
    episodes_per_season=[8],
    premiere_year=2026,
    premiere_season=("WINTER", "SATURDAY"),
    frequency=["SATURDAY"],
    reruns="ghibli_movie",
    episodes_per_slot=2,      # 48-minute episodes: two fill the slot exactly
    loop=True,
)

MACROSS_PLUS = annual_show(
    show_title="Macross Plus",
    episodes_per_season=[4],
    premiere_year=2026,
    premiere_season=("SPRING", "SATURDAY"),
    frequency=["SATURDAY"],
    reruns="ghibli_movie",
    episodes_per_slot=2,      # 39-minute OVA episodes
    loop=True,
)

TATAMI_TIME_MACHINE_BLUES = annual_show(
    show_title="The Tatami Time Machine Blues",
    episodes_per_season=[6],
    premiere_year=2026,
    premiere_season=("SUMMER", "SATURDAY"),
    frequency=["SATURDAY"],
    reruns="ghibli_movie",
    episodes_per_slot=3,      # 32 minutes each
    loop=True,
)


def _appointment(name, program):
    """One appointment plus its bed, with the appointment always first.

    DailyOrderedCollection rather than OrderedCollection: it resets to index 0
    each day, so the premiere lands at 21:00 every week instead of drifting.
    """
    return Block(
        name=name,
        items=DailyOrderedCollection([program, "ghibli_movie"]),
        fill_strategy="yield",
    )


# Autumn has no limited series and falls through to the feature shelf, the same
# way Nightmare Theatre's winter falls through to its double bill.
SATURDAY_LIMITED_SERIES = {
    "WINTER": _appointment("Blue Eye Samurai", BLUE_EYE_SAMURAI),
    "SPRING": _appointment("Macross Plus", MACROSS_PLUS),
    "SUMMER": _appointment("The Tatami Time Machine Blues", TATAMI_TIME_MACHINE_BLUES),
    "default": SATURDAY_THEATRE,
}

# ==============================================================================
# 8. DEEP NIGHT -- 23:00-02:00
# ==============================================================================

# 深夜アニメ. The block the channel exists for, and the half of the medium a
# three-hour after-school strip structurally cannot carry: Yuasa's two Tatami
# shows, Watanabe's Terror in Resonance, Edgerunners, and the only live-action
# series on the channel.
#
# Midnight Diner is 40 episodes across its 2009 run and Tokyo Stories, and it is
# here for the literal reason -- it is a show about a restaurant that opens at
# midnight, and it aired in this slot in Japan.
DEEP_NIGHT = Block(
    name="Deep Night",
    items=RandomCollection([
        "tatami_galaxy_tv",
        "terror_in_resonance_tv",
        "cyberpunk_edgerunners_tv",
        "scott_pilgrim_takes_off_tv",
        "midnight_diner_tv",
    ]),
)

# 00:00-02:00, and its own block rather than three hours of the one above:
# a collection spanning 23:00-02:00 crosses the midnight reset and replays its
# first items on the far side (G1). This half leans on the film shelf, which is
# what gives the small hours a different texture from the hour before them.
#
# `anime_canon_movie` is *not* here. Akira and Ghost in the Shell are on Cartoon
# Network's Midnight Run at exactly these hours.
DEEP_NIGHT_LATE = Block(
    name="Deep Night",
    items=RandomCollection([
        "anime_arthouse_movie",
        "evangelion_movie",
        "tatami_galaxy_tv",
        "midnight_diner_tv",
    ]),
)

# ==============================================================================
# 9. THE REBROADCAST -- 02:00-06:00
# ==============================================================================

# Four hours of vault, which is what Japanese overnight television actually is:
# the day again, cheaper.
#
# **Owned content only, and this is the one place the hours rule nearly went
# wrong.** The obvious bed for the small hours is the day's own syndication
# wheel -- One Piece, Naruto, InuYasha, Dragon Ball Z -- and the first version
# of this block was exactly that. Cartoon Network runs *Toonami: The Midnight
# Run* at 02:00-06:00 on Saturday nights, out of a chronological collection of
# Dragon Ball Z, Naruto, One Piece and Yu Yu Hakusho. A three-year simulation
# put all four of them in this slot on Sundays: four titles against four
# titles, once a week, every week.
#
# It did not show up as a grid mistake because the grid was right -- the
# docstring's window is 06:00-17:00 and this slot is outside it. It showed up
# because the *bed* was built from the wrong half of the library, which is C3's
# point exactly: a convention that lives in a grid survives until something
# reaches past the grid for a fallback.
THE_REBROADCAST = RandomCollection([
    "laid_back_camp_tv",
    "yama_no_susume_tv",
    "assassination_classroom_tv",
    "girls_und_panzer_tv",
    "one_punch_man_tv",
    "ranking_of_kings_tv",
    "dandadan_tv",
    "dragon_ball_gt_tv",
    "tatami_galaxy_tv",
])

# Midnight Diner is deliberately absent too, for a different reason. Be Kind
# Rewind's film pools contain the two Midnight Diner *features*, and 26 of its
# keys can reach them; simulated over 60 days it airs one at 02:00-10:00 and in
# the early evening. This channel plays the *series*, which is a different work
# with the same title -- and C1 is about the title. The overlap measured to
# exactly two hours, 02:00 and 04:00, and both of them are this vault: Deep
# Night runs 23:00-02:00 and never meets Be Kind Rewind at all. Taking the show
# out of the vault closes it completely and costs nothing, because 23:00 is
# where a show about a diner that opens at midnight belonged anyway (C6 -- the
# fix was measured, not asserted).

# Deliberately absent: the six shows that carry a named night. Frieren, Vinland
# Saga, Carole & Tuesday, Kids on the Slope, Violet Evergarden and Kino's
# Journey are the only appointments this channel has, and a show that also
# turns up in the vault at four in the morning every day is not an appointment
# any more -- it is just on. Sunday's replay is the one rerun they get, and it
# is a scheduled block with a name rather than a bed.

# ==============================================================================
# 10. THE CALENDAR
# ==============================================================================

# Golden Week -- 29 April to 3 May, four public holidays inside seven days and
# the week Japanese television clears its schedule. Ghibli in order of release,
# which is the one time of year the shelf runs as a history rather than a
# shuffle.
#
# It stops on 3 May and not 5 May, which is the real end of Golden Week, because
# 4 May is Star Wars Day in `core/registry.py` and `find_active_marathon`
# returns nothing while a holiday season is live (G9). A marathon that spans the
# 4th would go dark in the middle of itself.
GOLDEN_WEEK = MarathonSequence([
    {"title": "Nausicaä of the Valley of the Wind",
     "query": movie_by_title_year("Nausicaä of the Valley of the Wind", 1984)},
    {"title": "Castle in the Sky", "query": movie_by_title_year("Castle in the Sky", 1986)},
    {"title": "My Neighbor Totoro", "query": movie_by_title_year("My Neighbor Totoro", 1988)},
    {"title": "Kiki's Delivery Service",
     "query": movie_by_title_year("Kiki's Delivery Service", 1989)},
    {"title": "Porco Rosso", "query": movie_by_title_year("Porco Rosso", 1992)},
    {"title": "Princess Mononoke", "query": movie_by_title_year("Princess Mononoke", 1997)},
    {"title": "Spirited Away", "query": movie_by_title_year("Spirited Away", 2001)},
    {"title": "Howl's Moving Castle", "query": movie_by_title_year("Howl's Moving Castle", 2004)},
])

# Obon, 13-16 August: the days the dead come home. Grave of the Fireflies is the
# film Japan actually shows in this week, and the other three are the shelf's
# other ghost stories.
#
# Every title is year-bounded. `movie_by_title` builds a phrase match, and
# `title:"Metropolis"` returning Fritz Lang's 1927 silent as well as Rintaro's
# 2001 film is the reason the film keys in sources.py carry a genre guard --
# the same trap, one layer up (G10).
OBON = MarathonSequence([
    {"title": "Grave of the Fireflies",
     "query": movie_by_title_year("Grave of the Fireflies", 1988)},
    {"title": "Only Yesterday", "query": movie_by_title_year("Only Yesterday", 1991)},
    {"title": "Pom Poko", "query": movie_by_title_year("Pom Poko", 1994)},
    {"title": "The Tale of the Princess Kaguya",
     "query": movie_by_title_year("Tale of The Princess Kaguya, The", 2013)},
])

# 31 December. Ōmisoka is a night in, and the one night of the year this
# channel stops being a broadcast day and becomes a marathon of its own best
# thing. A holiday *schedule* rather than a marathon, because New Year's Eve is
# a registry holiday and a marathon cannot fire inside a holiday season (G9).
OMISOKA_SCHEDULE = {
    "teatime":    GHIBLI_SUNDAY,
    "feature":    GHIBLI_SUNDAY,
    "prime":      GHIBLI_SUNDAY,
    "late":       DEEP_NIGHT,
    "deep_night": DEEP_NIGHT_LATE,
}
