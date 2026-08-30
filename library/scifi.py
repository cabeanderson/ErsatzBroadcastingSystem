"""
Sci-Fi Channel Content
Collections, Blocks, and Special Programming.
"""

from datetime import date
from scripts.logic.structures import RandomCollection, OrderedCollection, Block, Program
from scripts.logic.factories import annual_show

# --- COLLECTIONS ---

MODERN_SCIFI_BLOCK = RandomCollection([
    "modern_scifi_tv",
    "scifi_tv"
])

# The overnight and early-morning pool. `classic_scifi_tv` alone is 8 shows for
# 28 hours a week, so the vintage titles are named directly and the era key rides
# along rather than carrying the whole block.
SCIFI_VAULT = RandomCollection([
    {"title": "The Twilight Zone", "order": "Shuffle"},
    # Year-bounded: `show_title:"Star Trek"` is a phrase match, so it also
    # returns The Next Generation, Deep Space Nine and the rest, which makes the
    # vault a second Trek playlist. This is the 1966 original only.
    {"title": "Star Trek",
     "query": 'show_title:"Star Trek" AND release_date:[1966-01-01 TO 1966-12-31]',
     "order": "Chronological"},
    {"title": "Street Hawk", "order": "Chronological"},
    {"title": "The Hitchhiker's Guide to the Galaxy", "order": "Chronological"},
    "classic_scifi_tv",
    "syndicated_scifi_tv"
])

# Ordered because both are strictly episodic 80s action -- there is no serial to
# preserve, but a stable rotation reads as a scheduled strip rather than a shuffle.
SCIFI_RETRO_ACTION = OrderedCollection([
    {"title": "Knight Rider", "order": "Chronological"},
    {"title": "Quantum Leap", "order": "Chronological"}
])

# Short-run cult science fiction. Firefly is the piece of the old Whedonverse
# block that belongs on a science fiction channel; Buffy and Angel went to
# library/fantasy.py with the rest of the fantasy programming.
SCIFI_CULT = OrderedCollection([
    {"title": "Firefly", "order": "Chronological"},
    {"title": "Dollhouse", "order": "Chronological"},
    {"title": "Dark Angel", "order": "Chronological"}
])

# Horror television, not science fiction. Off Other Worlds and waiting for
# Nightmare Theatre; kept here rather than deleted because the block works and
# only its home is wrong. `thriller_tv` needs narrowing before it is scheduled
# again -- genre:thriller reaches Columbo and Remington Steele.
PARANORMAL_FILES = RandomCollection([
    "supernatural_tv",
    "thriller_tv",
    "horror_tv"
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
    {"title": "fringe", "order": "Chronological"}
    # Millennium left for Mystery Theatre. It carries a Science Fiction tag but
    # there is no science in it -- it is a serial-killer profiler that drifts
    # into the occult.
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
        annual_show(
            show_title="Lost",
            episodes_per_season=[25, 24, 23, 14, 17, 18],
            premiere_year=2026,
            premiere_season=("FALL", "SUNDAY"),
            frequency=["SUNDAY"],
            reruns=LOST_FILLERS,
            loop=True
        ),
        # 9:00pm Slot
        annual_show(
            show_title="Alias",
            episodes_per_season=[22, 22, 22, 22, 17],
            premiere_year=2026,
            premiere_season=("WINTER", "SUNDAY"),
            frequency=["SUNDAY"],
            reruns=ALIAS_FILLERS,
            loop=True
        ),
        # 10:00pm Slot
        annual_show(
            show_title="Fringe",
            episodes_per_season=[20, 23, 22, 22, 13],
            premiere_year=2027,
            premiere_season=("SPRING", "SUNDAY"),
            frequency=["SUNDAY"],
            reruns=FRINGE_FILLERS,
            loop=True
        )
    ]
)