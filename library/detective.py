"""
Detective Channel Content
Collections, Blocks, and Special Programming.
"""

from scripts.logic.structures import RandomCollection, OrderedCollection, DailyOrderedCollection, Block
from scripts.logic.queries import show_by_title
from scripts.logic.factories import annual_show

# --- COLLECTIONS ---

CLASSIC_DETECTIVES = OrderedCollection([
    "classic_mystery_tv",
    "detective_tv",
    "classic_noir_movie"
])

MODERN_CRIME = OrderedCollection([
    "procedural_tv",
    "modern_mystery_tv",
    "legal_drama_tv"
])

BRITISH_CRIME = OrderedCollection([
    "british_mystery_tv",
    "british_drama_tv"
])

TRUE_CRIME_NIGHT = OrderedCollection([
    "true_crime_tv",
    "mystery_crime_movie"
])

LEGAL_BLOCK = RandomCollection([
    "legal_drama_tv"
])

DETECTIVE_USA_BLOCK = RandomCollection([
    {"title": "monk"},
    {"title": "psych"}
])

DETECTIVE_BRITISH_BLOCK = RandomCollection([
    {"title": "agatha christie's poirot"},
    {"title": "miss marple"},
    "british_mystery_tv"
])

DETECTIVE_LATE_NIGHT = RandomCollection([
    {"title": "columbo"},
    {"title": "poker face"},
    {"title": "bored to death"},
    {"title": "remington steele"},
    "classic_mystery_tv",
    "true_crime_tv"
])

MYSTERY_MOVIE_WHEEL = OrderedCollection([
    {"title": "Columbo", "query": show_by_title("Columbo"), "order": "Shuffle"},
    {"title": "Poirot", "query": show_by_title("Agatha Christie's Poirot"), "order": "Shuffle"},
    {"title": "Miss Marple", "query": show_by_title("Miss Marple"), "order": "Shuffle"},
    {"title": "Murder, She Wrote", "query": show_by_title("Murder, She Wrote"), "order": "Shuffle"},
])

NOIR_NOVEMBER_COLLECTION = RandomCollection([
    {"title": "True Detective", "query": show_by_title("True Detective"), "order": "Chronological"},
    {"title": "Bosch", "query": show_by_title("Bosch"), "order": "Chronological"},
    {"title": "Mindhunter", "query": show_by_title("Mindhunter"), "order": "Chronological"},
    {"title": "Dark Winds", "query": show_by_title("Dark Winds"), "order": "Chronological"},
    {"title": "Homicide: Life on the Street", "query": show_by_title("Homicide: Life on the Street"), "order": "Shuffle"},
    {"title": "Millennium", "query": show_by_title("Millennium"), "order": "Shuffle"},
])

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
        {"title": "Magnum P.I.", "query": show_by_title("Magnum P.I."), "order": "Shuffle"},
        {"title": "Moonlighting", "query": show_by_title("Moonlighting"), "order": "Shuffle"},
        {"title": "Remington Steele", "query": show_by_title("Remington Steele"), "order": "Shuffle"},
    ]),
    use_epg_group=False
)

TRUE_DETECTIVE_BLOCK = annual_show(
    show_title="True Detective",
    seasons=4,
    episodes_per_season=[8, 8, 8, 6],
    premiere_year=2026,
    premiere_season="FALL",
    reruns="mystery_crime_movie", # Fallback if season ends early
    loop=True
)

FARGO_BLOCK = annual_show(
    show_title="Fargo",
    seasons=5,
    episodes_per_season=[10, 10, 10, 11, 10],
    premiere_year=2026,
    premiere_season="WINTER",
    reruns="mystery_crime_movie",
    loop=True
)

# SUNDAY PRESTIGE NIGHT
# 1. Millennium (Anchor)
# 2. Anthology Slot (True Detective in Fall, Fargo in Winter, Movies otherwise)
# 3. Movie Filler
SUNDAY_PRESTIGE_BLOCK = DailyOrderedCollection([
    TRUE_DETECTIVE_BLOCK,
    FARGO_BLOCK,
    {"title": "Millennium", "query": show_by_title("Millennium"), "order": "Chronological"}
])