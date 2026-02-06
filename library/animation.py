"""
Animation Content
Collections, Blocks, and Special Programming for Cartoon Network & Adult Swim.
"""

from scripts.logic.structures import RandomCollection, OrderedCollection, MarathonSequence, Block
from scripts.library.queries import show_by_title
from scripts.logic.models import Swap, ContentItem
from scripts.logic.calendar.seasonal import SeasonalBlock
from . import branding

# --- COLLECTIONS ---

# Classic Morning Blocks - OrderedCollection for morning routine
SATURDAY_MORNING = OrderedCollection([
    {"title": "scooby-doo, where are you!"},
    {"title": "looney tunes"},
    {"title": "tom and jerry"},
    {"title": "the flintstones"},
    {"title": "the jetsons"},
    {"title": "popeye"},
    {"title": "yogi bear"},
    {"title": "superman"}
])

CLASSIC_CARTOONS = RandomCollection([
    {"title": "popeye"},
    {"title": "looney tunes"},
    {"title": "tom and jerry"},
    {"title": "the flintstones"},
    {"title": "the jetsons"},
    {"title": "yogi bear"}
])

# Nickelodeon - RandomCollection for variety
NICKTOONS_VAULT = RandomCollection([
    {"title": "aaahh!!! real monsters"},
    {"title": "the wild thornberrys"},
    {"title": "spongebob squarepants"},
    {"title": "invader zim"},
    {"title": "avatar: the last airbender"},
    {"title": "the legend of korra"},
    {"title": "the ren & stimpy show"},
    {"title": "ed, edd n eddy"}
])

FOX_PRIMETIME = OrderedCollection([
    {"title": "the simpsons"},
    {"title": "bob's burgers"},
    {"title": "futurama"},
    {"title": "rick and morty"}
])

# Disney - OrderedCollection for afternoon block progression
DISNEY_AFTERNOON = OrderedCollection([
    {"title": "talespin"},
    {"title": "chip 'n' dale rescue rangers"},
    {"title": "goof troop"},
    {"title": "ducktales"},
    {"title": "darkwing duck"},
    {"title": "kim possible"},
    {"title": "pepper ann"}
])

DISNEY_MORNING = OrderedCollection([
    {"title": "aladdin"},
    {"title": "hercules"},
    {"title": "mighty ducks: the animated series"},
    {"title": "buzz lightyear of star command"},
    {"title": "goof troop"}
])

# Cartoon Network - RandomCollection for variety
CARTOON_NETWORK_CLASSICS = RandomCollection([
    {"title": "courage the cowardly dog"},
    {"title": "daria"},
    {"title": "dexter's laboratory"},
    {"title": "the powerpuff girls"},
    {"title": "gravity falls"},
    {"title": "infinity train"},
    {"title": "johnny bravo"},
    {"title": "the owl house"},
    {"title": "animaniacs"},
    {"title": "pinky and the brain"}
])

# Action & Superhero - OrderedCollection for DC universe progression
ACTION_ANIMATION = OrderedCollection([
    {"title": "batman: the animated series", "order": "Chronological"},
    {"title": "new batman adventures", "order": "Chronological"},
    {"title": "batman beyond", "order": "Chronological"},
    {"title": "justice league", "order": "Chronological"},
    {"title": "superman: the animated series", "order": "Chronological"},
    {"title": "x-men", "query": 'show_title:"x-men" NOT show_tag:"adult"'},
    {"title": "spider-man"}
])

SUPERHERO_HOUR = OrderedCollection([
    {"title": "batman: the animated series"},
    {"title": "superman: the animated series"},
    {"title": "justice league"},
    {"title": "batman beyond"}
])

MARVEL_HOUR = OrderedCollection([
    {"title": "x-men", "query": 'show_title:"x-men" NOT show_tag:"adult"'},
    {"title": "spider-man"},
    {"title": "teenage mutant ninja turtles"},
    {"title": "SWAT Kats", "query": 'show_title:"SWAT Kats*"', "order": "Chronological"}
])

WB_AFTERNOON = OrderedCollection([
    {"title": "animaniacs"},
    {"title": "pinky and the brain"},
    {"title": "tiny toon adventures"},
    {"title": "scooby-doo, where are you!"},
    {"title": "batman: the animated series"},
    {"title": "batman beyond"}
])

STAR_WARS_ANIMATION = RandomCollection([
    {"title": "Clone Wars"},
    {"title": "Clone Wars"}, # Weighted for more play
    {"title": "Rebels"},
    {"title": "Bad Batch"}
])

# Misc Blocks - Plain lists for flexibility
ANIME_BLOCK = OrderedCollection([
    {"title": "pokémon"},
    {"title": "Dragon Ball", "query": 'show_title:"Dragon Ball" AND release_date:[1980-01-01 TO 1989-04-21]'},
    {"title": "Dragon Ball Z", "order": "Chronological"}, # Explicit order
    "anime_action_tv"
])

SYNDICATED_CARTOONS = RandomCollection([
    {"title": "inspector gadget"},
    {"title": "captain planet"},
    {"title": "the magic school bus"},
    {"title": "mister t"},
    {"title": "teenage mutant ninja turtles"},
    {"title": "gargoyles"}
])

# Animation Film
ANIMATION_SHOWCASE = RandomCollection([
    "ghibli_movie", 
    "disney_movie", 
    "pixar_movie", 
    "dreamworks_movie"
])

# DBZ Marathon Collection
DBZ_SAGAS = RandomCollection([
    "dbz_saiyan_saga_tv",
    "dbz_frieza_saga_tv",
    "dbz_cell_games_tv"
])

# Simpsons Marathon Collection
SIMPSONS_MARATHON = "simpsons_random_marathon"

# Cowboy Bebop Complete Run (Sequence)
COWBOY_BEBOP_COMPLETE = MarathonSequence([
    {"title": "Cowboy Bebop Eps 1-22", "query": 'show_title:"Cowboy Bebop" AND season_number:1 AND episode_number:[1 TO 22]', "order": "Chronological", "media_type": "show"},
    {"title": "Cowboy Bebop: The Movie", "query": 'show_title:"cowboy bebop" AND season_number:0 AND episode_number:2', "media_type": "movie"},
    {"title": "Cowboy Bebop Eps 23-26", "query": 'show_title:"Cowboy Bebop" AND season_number:1 AND episode_number:[23 TO 26]', "order": "Chronological", "media_type": "show"}
])

# --- BLOCKS ---

# --- ADULT SWIM PRIME (8pm - 11pm) ---
# Vibe: Comedy, Sitcoms, Story-driven

AS_PRIME_A = Block(
    name="Adult Swim Prime A",
    items=OrderedCollection([
        {"title": "King of the Hill", "query": show_by_title("King of the Hill"), "order": "Shuffle"},
        {"title": "Family Guy", "query": show_by_title("Family Guy"), "order": "Shuffle"},
        {"title": "Rick and Morty", "query": show_by_title("Rick and Morty"), "order": "Chronological"},
        {"title": "Archer", "query": show_by_title("Archer"), "order": "Chronological"},
        {"title": "Home Movies", "query": show_by_title("Home Movies"), "order": "Shuffle"},
        {"title": "Metalocalypse", "query": show_by_title("Metalocalypse"), "order": "Shuffle"},
    ]),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

AS_PRIME_B = Block(
    name="Adult Swim Prime B",
    items=OrderedCollection([
        {"title": "Bob's Burgers", "query": show_by_title("Bob's Burgers"), "order": "Shuffle"},
        {"title": "Futurama", "query": show_by_title("Futurama"), "order": "Shuffle"},
        {"title": "Rick and Morty", "query": show_by_title("Rick and Morty"), "order": "Chronological"},
        {"title": "The Boondocks", "query": show_by_title("The Boondocks"), "order": "Shuffle"},
        {"title": "Home Movies", "query": show_by_title("Home Movies"), "order": "Shuffle"},
        {"title": "Metalocalypse", "query": show_by_title("Metalocalypse"), "order": "Shuffle"},
    ]),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

# --- ADULT SWIM NIGHT (11pm - 2am) ---
# Vibe: Weird, Anime, Experimental

AS_NIGHT_A = Block(
    name="Adult Swim Night A",
    items=OrderedCollection([
        {"title": "Aqua Teen Hunger Force", "query": show_by_title("Aqua Teen Hunger Force"), "order": "Shuffle"},
        {"title": "Harvey Birdman", "query": show_by_title("Harvey Birdman, Attorney at Law"), "order": "Shuffle"},
        {"title": "The Eric Andre Show", "query": show_by_title("The Eric Andre Show"), "order": "Shuffle"},
        {"title": "Cowboy Bebop", "query": show_by_title("Cowboy Bebop"), "order": "Chronological"},
        {"title": "Black Dynamite", "query": show_by_title("Black Dynamite"), "order": "Shuffle"},
        {"title": "12 oz. Mouse", "query": show_by_title("12 oz. Mouse"), "order": "Shuffle"},
    ]),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)

AS_NIGHT_B = Block(
    name="Adult Swim Night B",
    items=OrderedCollection([
        {"title": "Robot Chicken", "query": show_by_title("Robot Chicken"), "order": "Shuffle"},
        {"title": "Sealab 2021", "query": show_by_title("Sealab 2021"), "order": "Shuffle"},
        {"title": "Steve Brule", "query": show_by_title("Check It Out! with Dr. Steve Brule"), "order": "Shuffle"},
        {"title": "Cowboy Bebop", "query": show_by_title("Cowboy Bebop"), "order": "Chronological"},
        {"title": "Frisky Dingo", "query": show_by_title("Frisky Dingo"), "order": "Shuffle"},
        {"title": "12 oz. Mouse", "query": show_by_title("12 oz. Mouse"), "order": "Shuffle"},
    ]),
    intro=branding.BRANDING_ADULT_SWIM.intro,
    bumpers=branding.BRANDING_ADULT_SWIM.bumpers,
    use_epg_group=False
)


TOONAMI_BLOCK = Block(
    name="Toonami",
    items=OrderedCollection([
        {"title": "Sailor Moon", "query": 'show_title:"sailor moon" AND NOT show_title:"sailor moon crystal"', "order": "Shuffle"},
        {"title": "Dragon Ball", "query": 'show_title:"Dragon Ball" AND release_date:[1980-01-01 TO 1989-04-21]', "order": "Chronological"},
        {"title": "Dragon Ball Z", "order": "Chronological"},
        {"title": "Yu Yu Hakusho", "order": "Chronological"},
        {"title": "Rurouni Kenshin", "order": "Chronological"},
        {"title": "Inuyasha", "order": "Chronological"},
        {"title": "Naruto", "order": "Chronological"}
    ]),
    intro=branding.BRANDING_TOONAMI.intro,
    outro=branding.BRANDING_TOONAMI.outro,
    bumpers=branding.BRANDING_TOONAMI.bumpers,
    use_epg_group=False
)

FOX_KIDS_BLOCK = Block(
    name="Fox Kids",
    items=MARVEL_HOUR,
    intro=branding.BRANDING_90S_KIDS.intro,
    outro=branding.BRANDING_90S_KIDS.outro,
    bumpers=branding.BRANDING_90S_KIDS.bumpers,
    use_epg_group=False
)

# --- SEASONAL BLOCKS ---

# Cartoon Network
CN_MORNING_HERO = SeasonalBlock(
    base=SUPERHERO_HOUR,
    seasonal={
        "SPRING": Swap(MARVEL_HOUR)
    }
)

CN_AFTERNOON_BLOCK = SeasonalBlock(
    base=DISNEY_AFTERNOON,
    seasonal={
        "SPRING": Swap(WB_AFTERNOON)
    }
)