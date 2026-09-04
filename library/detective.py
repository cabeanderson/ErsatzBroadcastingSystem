"""
Detective Channel Content
Collections, Blocks, and Special Programming.
"""

from scripts.logic.structures import RandomCollection, OrderedCollection, DailyOrderedCollection, Block
from scripts.library.queries import show_by_title
from scripts.logic.factories import annual_show

# --- BLOCKS ---

CLASSIC_DETECTIVES = Block(
    name="Classic Detectives",
    items=OrderedCollection([
        "classic_mystery_tv",
        "detective_tv"
        # `classic_noir_movie` removed: 13 Golden Age films, and Classic Cinema
        # builds its whole noir identity on them.
    ])
)

MODERN_CRIME = Block(
    name="Modern Crime",
    items=OrderedCollection([
        "the_shield_tv",
        "procedural_tv",      # 4 shows -- `tag:procedural` is thinner than it reads
        "modern_mystery_tv"   # 62 shows; `legal_drama_tv` was 4 and is dropped
    ])
)

# 08:00-10:00 weekdays, and nowhere else on the grid. This used to hold the
# afternoon as well -- five hours a weekday, 4.5 h/day averaged, 18% of the
# channel on two shows. Two hours is one Monk and one Psych a day, which is
# what the block is for; the afternoon it vacated is THE_PROCEDURAL_WALL.
DETECTIVE_USA_BLOCK = Block(
    name="USA Network Block",
    items=OrderedCollection([
        {"title": "monk"},
        {"title": "psych"}
    ])
)

# 14:00-17:00 weekdays. The drop-in-anywhere hour this channel exists to run
# and did not have: three episodic procedurals, ~43 minutes each, three of
# them into a three-hour slot. All three were on disk with no registry key.
THE_PROCEDURAL_WALL = Block(
    name="The Procedural Wall",
    items=OrderedCollection([
        "nine_one_one_tv",
        "greys_anatomy_tv",
        "chicago_med_tv",
    ])
)

DETECTIVE_BRITISH_BLOCK = Block(
    name="British Mystery",
    items=RandomCollection([
        {"title": "agatha christie's poirot"},
        {"title": "miss marple"},
        "british_mystery_tv"
    ])
)

DETECTIVE_LATE_NIGHT = Block(
    name="Detective Late Night",
    items=RandomCollection([
        {"title": "columbo"},
        {"title": "poker face"},
        {"title": "bored to death"},
        {"title": "remington steele"},
        # 268 episodes, previously on no channel. It replaces `true_crime_tv`,
        # which was genre:documentary AND genre:crime -- one show, six episodes,
        # carrying 47 hours a month across the three slots this block fills.
        {"title": "Alfred Hitchcock Presents", "query": show_by_title("Alfred Hitchcock Presents"), "order": "Shuffle"},
        "classic_mystery_tv"
    ])
)

# Named for the NBC wheel, but every item was a television series, which is most
# of why this channel ran at 2% film against a library of 365 mystery and crime
# features. The television wheel keeps its rotation under an honest name; the
# movie wheel below is the one that shows films.
WHODUNIT_WHEEL = Block(
    name="Whodunit Wheel",
    items=OrderedCollection([
        {"title": "Columbo", "query": show_by_title("Columbo"), "order": "Shuffle"},
        {"title": "Poirot", "query": show_by_title("Agatha Christie's Poirot"), "order": "Shuffle"},
        {"title": "Miss Marple", "query": show_by_title("Miss Marple"), "order": "Shuffle"},
        {"title": "Murder, She Wrote", "query": show_by_title("Murder, She Wrote"), "order": "Shuffle"},
    ])
)

# Era-split from Classic Cinema rather than shared. Both channels want crime
# film, and Classic Cinema runs NOIR_NIGHT overnight on the same two keys this
# used to hold -- so raising this channel's film share from 2% to 21% put the
# identical pool on both at 00:00. Classic Cinema keeps the pre-1970 titles and
# the Golden Age noirs; this takes the 330 films from 1970 on.
MYSTERY_MOVIE_WHEEL = Block(
    name="Mystery Movie Wheel",
    items=RandomCollection([
        "modern_crime_movie"     # 330 films, 1970+
    ])
)

# The comma matters: the folder is `Magnum, P.I.`, and Friday's block asked for
# "Magnum P.I." for as long as it has existed.
#
# Miami Vice was the second item and is gone as of 2026-09-02. Two reasons, and
# the first is the channel's own identity: every other title in this hour is a
# case show, and `reference/library-tv.tsv` agrees -- Magnum, Moonlighting and
# Remington Steele all carry a Mystery genre tag, Miami Vice is `Crime; Drama`
# and nothing else. It is a vice-squad mood piece, not a whodunit.
#
# The second is a live collision, logged in KNOWN_ISSUES.md: this block is
# `midday`, which is 10:00-12:00, and Totally 80s' fall/winter daytime wheel
# draws `eighties_crime_tv` over the same two hours -- a genre pool that returns
# Miami Vice. `collision_report` could not see it because that channel reaches
# the show through a pool and this one named it by title. Totally 80s has the
# stronger claim either way: it names Miami Vice by key as a Wednesday prime
# appointment, and the decade is that channel's whole subject.
#
# Remington Steele takes the slot: 96 episodes, 1982, tagged Mystery, and on no
# other channel. It already airs here at overnight/early and Friday prime, so
# 10:00-12:00 is its own hour and clashes with nothing.
RETRO_PI_STRIP = Block(
    name="Retro P.I.",
    items=OrderedCollection([
        {"title": "Magnum, P.I.", "query": show_by_title("Magnum, P.I."), "order": "Shuffle"},
        {"title": "Remington Steele", "query": show_by_title("Remington Steele"), "order": "Shuffle"},
    ])
)

# Episodic modern procedurals. Mr. Robot and The Americans are the other large
# unused shows in this genre and are deliberately absent -- both are serialized
# past the point where a shuffled strip makes sense.
MODERN_CASEBOOK = Block(
    name="Modern Casebook",
    items=OrderedCollection([
        # Bounded by year: a phrase match on "House" also returns House of the
        # Dragon and House Of Cosbys.
        {"title": "House",
         "query": 'type:episode AND show_title:"House" AND release_date:[2004-01-01 TO 2004-12-31]',
         "order": "Shuffle"},
        {"title": "Burn Notice", "query": show_by_title("Burn Notice"), "order": "Shuffle"},
        {"title": "Veronica Mars", "query": show_by_title("Veronica Mars"), "order": "Shuffle"},
    ])
)

NOIR_NOVEMBER_COLLECTION = Block(
    name="Noir November",
    items=RandomCollection([
        {"title": "True Detective", "query": show_by_title("True Detective"), "order": "Chronological"},
        {"title": "Bosch", "query": show_by_title("Bosch"), "order": "Chronological"},
        {"title": "Mindhunter", "query": show_by_title("Mindhunter"), "order": "Chronological"},
        {"title": "Dark Winds", "query": show_by_title("Dark Winds"), "order": "Chronological"},
        {"title": "Homicide: Life on the Street", "query": show_by_title("Homicide: Life on the Street"), "order": "Shuffle"},
        {"title": "Millennium", "query": show_by_title("Millennium"), "order": "Shuffle"},
    ])
)

# --- BLOCKS ---

DETECTIVE_MONDAY_BRITISH = Block(
    name="British Parlour Mystery",
    items=OrderedCollection([
        {"title": "Agatha Christie's Poirot", "query": show_by_title("Agatha Christie's Poirot"), "order": "Shuffle"},
        {"title": "Miss Marple", "query": show_by_title("Miss Marple"), "order": "Shuffle"},
        {"title": "Agatha Christie's Poirot", "query": show_by_title("Agatha Christie's Poirot"), "order": "Shuffle"}, # Encore
    ]),
    use_epg_group=False
)

DETECTIVE_TUESDAY_BLUESKY = Block(
    name="Blue Sky Dramedy",
    items=OrderedCollection([
        {"title": "Monk", "query": show_by_title("Monk"), "order": "Shuffle"},
        {"title": "Psych", "query": show_by_title("Psych"), "order": "Shuffle"},
        {"title": "Elsbeth", "query": show_by_title("Elsbeth"), "order": "Shuffle"},
    ]),
    use_epg_group=False
)

DETECTIVE_WEDNESDAY_HARDBOILED = Block(
    name="Hardboiled Crime",
    items=OrderedCollection([
        # 336 episodes, the deepest show on the channel, and the register this
        # night is named for. Shuffled: it is serialized, but the cases are not.
        {"title": "The Shield", "query": show_by_title("The Shield"), "order": "Shuffle"},
        {"title": "Bosch", "query": show_by_title("Bosch"), "order": "Chronological"},
        {"title": "Homicide: Life on the Street", "query": show_by_title("Homicide: Life on the Street"), "order": "Shuffle"},
        {"title": "Mindhunter", "query": show_by_title("Mindhunter"), "order": "Chronological"},
    ]),
    use_epg_group=False
)

DETECTIVE_THURSDAY_WHODUNIT = Block(
    name="The Whodunit Club",
    items=OrderedCollection([
        {"title": "Murder, She Wrote", "query": show_by_title("Murder, She Wrote"), "order": "Shuffle"},
        {"title": "Poker Face", "query": show_by_title("Poker Face"), "order": "Shuffle"},
        {"title": "Bored to Death", "query": show_by_title("Bored to Death"), "order": "Shuffle"},
    ]),
    use_epg_group=False
)

DETECTIVE_FRIDAY_RETRO = Block(
    name="Retro P.I. Night",
    items=OrderedCollection([
        {"title": "Magnum, P.I.", "query": show_by_title("Magnum, P.I."), "order": "Shuffle"},
        {"title": "Moonlighting", "query": show_by_title("Moonlighting"), "order": "Shuffle"},
        {"title": "Remington Steele", "query": show_by_title("Remington Steele"), "order": "Shuffle"},
    ]),
    use_epg_group=False
)

TRUE_DETECTIVE_BLOCK = annual_show(
    show_title="True Detective",
    episodes_per_season=[8, 8, 8, 6],
    premiere_year=2026,
    premiere_season=("FALL", "SUNDAY"),
    frequency=["SUNDAY"],
    reruns="modern_crime_movie",  # Fallback if season ends early
    loop=True
)

FARGO_BLOCK = annual_show(
    show_title="Fargo",
    episodes_per_season=[10, 10, 10, 11, 10],
    premiere_year=2026,
    premiere_season=("WINTER", "SUNDAY"),
    frequency=["SUNDAY"],
    reruns="modern_crime_movie",
    loop=True
)

# SUNDAY PRESTIGE NIGHT
# 1. Millennium (Anchor)
# 2. Anthology Slot (True Detective in Fall, Fargo in Winter, Movies otherwise)
# 3. Movie Filler
SUNDAY_PRESTIGE_BLOCK = Block(
    name="Sunday Prestige Mystery",
    items=DailyOrderedCollection([
        TRUE_DETECTIVE_BLOCK,
        FARGO_BLOCK,
        {"title": "Millennium", "query": show_by_title("Millennium"), "order": "Chronological"}
    ])
)