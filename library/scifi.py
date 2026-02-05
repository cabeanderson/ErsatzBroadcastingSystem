"""
Sci-Fi Channel Content
Collections, Blocks, and Special Programming.
"""

from datetime import date
from scripts.logic.structures import RandomCollection, OrderedCollection, Block, Program
from scripts.logic.factories import annual_show

# --- COLLECTIONS ---

SCIFI_CLASSICS_TV = RandomCollection([
    "classic_scifi_tv",
    "syndicated_scifi_tv"
])

MODERN_SCIFI_BLOCK = RandomCollection([
    "modern_scifi_tv",
    "scifi_tv"
])

FANTASY_ADVENTURE = RandomCollection([
    "fantasy_tv",
    "epic_fantasy_tv",
    "scifi_fantasy_tv"
])

PARANORMAL_FILES = RandomCollection([
    "supernatural_tv",
    "thriller_tv",
    "horror_tv"
])

WHEDONVERSE_SAGA = RandomCollection([
    {"title": "Buffy", "order": "Chronological"},
    {"title": "Angel", "order": "Chronological"},
    {"title": "Firefly", "order": "Chronological"}
])

HERCULES_XENA = RandomCollection([
    {"title": "Hercules: The Legendary Journeys", "order": "Chronological"},
    {"title": "Xena: Warrior Princess", "order": "Chronological"}
])

SCIFI_MYTHS = RandomCollection([
    {"title": "Beyond Belief: Fact or Fiction", "query": 'show_title:"beyond belief*"', "order": "Shuffle"},
    {"title": "Mythbusters", "order": "Chronological"}
])

TREK_MORNING = RandomCollection([
    {"title": "Star Trek: Enterprise", "order": "Chronological"},
    {"title": "Star Trek: The Next Generation", "order": "Chronological"}
])

# Sci-Fi Prime Time Lineups
SCIFI_STARTREK = OrderedCollection([
    {"title": "Star Trek: The Next Generation", "order": "Chronological"},
    {"title": "Star Trek: Deep Space Nine", "order": "Chronological"},
    {"title": "Star Trek: Voyager", "order": "Chronological"}
])

SCIFI_INVESTIGATION = OrderedCollection([
    {"title": "the x-files", "order": "Chronological"},
    {"title": "fringe", "order": "Chronological"},
    {"title": "millennium", "order": "Chronological"}
])

SCIFI_SPACE_OPERA = OrderedCollection([
    {"title": "babylon 5", "order": "Chronological"},
    {"title": "Stargate SG-1", "query": 'show_title:"Stargate SG-1"', "order": "Chronological"},
    {"title": "farscape", "order": "Chronological"}
])

SCIFI_MODERN_EPIC = OrderedCollection([
    {"title": "battlestar galactica", "order": "Chronological"},
    {"title": "the expanse", "order": "Chronological"},
    {"title": "for all mankind", "order": "Chronological"}
])

SCIFI_GRITTY = OrderedCollection([
    {"title": "terminator: the sarah connor chronicles", "order": "Chronological"},
    {"title": "orphan black", "order": "Chronological"},
    {"title": "the man in the high castle", "order": "Chronological"}
])

# --- APPOINTMENT TV BLOCKS ---

# --- Fillers ---
LOST_FILLERS = OrderedCollection([
    {"title": "Devs", "order": "Chronological"},
    {"title": "The OA", "order": "Chronological"},
    {"title": "Black Mirror", "order": "Chronological"}
])

ALIAS_FILLERS = OrderedCollection([
    {"title": "Terminator: The Sarah Connor Chronicles", "order": "Chronological"},
    {"title": "Dark Angel", "order": "Chronological"}
])

FRINGE_FILLERS = OrderedCollection([
    {"title": "Firefly", "order": "Chronological"},
    {"title": "Cleopatra 2525", "order": "Chronological"}
])

# --- Sunday Night Appointment Lineup ---

SCIFI_SUNDAY_BLOCK = Block(
    name="Sci-Fi Sunday Night",
    items=[
        # 8:00pm Slot
        annual_show(show_title="Lost", seasons=6, episodes_per_season=[25, 24, 23, 14, 17, 18], premiere_year=2026, premiere_season="FALL", reruns=LOST_FILLERS, loop=True),
        # 9:00pm Slot
        annual_show(show_title="Alias", seasons=5, episodes_per_season=[22, 22, 22, 22, 17], premiere_year=2026, premiere_season="WINTER", reruns=ALIAS_FILLERS, loop=True),
        # 10:00pm Slot
        annual_show(show_title="Fringe", seasons=5, episodes_per_season=[20, 23, 22, 22, 13], premiere_year=2027, premiere_season="SPRING", reruns=FRINGE_FILLERS, loop=True)
    ]
)