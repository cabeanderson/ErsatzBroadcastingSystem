"""
Fantasy Content
Collections for fantasy film and television.

There is no fantasy channel yet. These collections exist because the library has
the content for one -- 238 live-action fantasy films and 40 live-action shows on
disk (media/ANALYSIS.md) -- and because Other Worlds is science fiction only, so
the fantasy programming it used to carry needs somewhere to live rather than
being deleted along with its slot.
"""

from scripts.logic.structures import RandomCollection, OrderedCollection

# --- TELEVISION ---

# Moved off Other Worlds when that channel narrowed to science fiction. Both are
# tagged Fantasy in the library and neither has any science in it.
HERCULES_XENA = RandomCollection([
    {"title": "Hercules: The Legendary Journeys", "order": "Chronological"},
    {"title": "Xena: Warrior Princess", "order": "Chronological"}
])

# Buffy is tagged `Action; Comedy; Drama` in this library -- no Fantasy tag at
# all -- so it is unreachable by any genre key and has to be named directly.
# Firefly stayed behind on Other Worlds; it is the one science fiction show of
# the three.
BUFFYVERSE = OrderedCollection([
    {"title": "Buffy the Vampire Slayer", "order": "Chronological"},
    {"title": "Angel", "order": "Chronological"}
])

FANTASY_ADVENTURE = RandomCollection([
    "fantasy_tv",
    "epic_fantasy_tv",
    "scifi_fantasy_tv"
])

FANTASY_CLASSICS_TV = RandomCollection([
    "classic_fantasy_tv",
    "fantasy_pure_tv"
])

FANTASY_MODERN_TV = RandomCollection([
    "modern_fantasy_tv",
    "fantasy_tv"
])

FANTASY_ANIMATION_TV = RandomCollection([
    "animated_fantasy_tv"
])

# --- FILM ---

FANTASY_MATINEE = RandomCollection([
    "fairytale_movie",
    "fantasy_adventure_movie"
])

FANTASY_FEATURE = RandomCollection([
    "fantasy_pure_movie",
    "epic_fantasy_movie"
])

FANTASY_COMEDY_NIGHT = RandomCollection([
    "fantasy_comedy_movie"
])

# Where fantasy and horror overlap -- 54 films. Nightmare Theatre has a claim on
# these too; whoever gets them, they should not be on both.
DARK_FANTASY = RandomCollection([
    "dark_fantasy_movie",
    "dark_fantasy_tv"
])

FANTASY_ERA_VAULT = RandomCollection([
    "classic_fantasy_movie",
    "80s_fantasy_movie",
    "90s_fantasy_movie"
])
