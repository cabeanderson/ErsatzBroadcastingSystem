# scripts/library/filters.py
"""
Reusable filter constants for building Lucene queries.
This includes eras, seasonal tags, and exclusion logic.
"""

# --- LOGIC FILTERS ---
NO_SITCOM = "NOT tag:sitcom"
NO_FANTASY = "NOT genre:fantasy"
NO_SCIFI = 'NOT genre:"science fiction"'
NO_COMEDY = "NOT genre:comedy"
NO_BBC = "NOT studio:bbc"
NO_HORROR = "NOT genre:horror"
NO_WESTERN = "NOT genre:western"
SHORT = "minutes:[* TO 40]"

# --- MOVIE ERAS ---
SILENT_ERA = "release_date:[* TO 1929-12-31]"
GOLDEN_AGE = "release_date:[1930-01-01 TO 1949-12-31]"
CLASSIC_ERA = "release_date:[1950-01-01 TO 1969-12-31]"
SEVENTIES = "release_date:[1970-01-01 TO 1979-12-31]"
EIGHTIES = "release_date:[1980-01-01 TO 1989-12-31]"
NINETIES = "release_date:[1990-01-01 TO 1999-12-31]"
Y2K_ERA = "release_date:[2000-01-01 TO 2009-12-31]"
TENS = "release_date:[2010-01-01 TO 2019-12-31]"
TWENTIES = "release_date:[2020-01-01 TO 2029-12-31]"
STREAMING_ERA = "release_date:[2010-01-01 TO *]"
# The line Classic Cinema and Mystery Theatre split the crime shelf along:
# 74 films before it, 291 after. Both channels want crime film and neither can
# have the whole 365 without airing the other's overnight.
PRE_EIGHTIES_ERA = "release_date:[* TO 1979-12-31]"
MODERN_FILM_ERA = "release_date:[1980-01-01 TO *]"

# --- TV ERAS ---
TV_VINTAGE = "release_date:[* TO 1975-12-31]"
TV_CLASSIC = "release_date:[1976-01-01 TO 1989-12-31]"
TV_GOLDEN_AGE = "release_date:[1985-01-01 TO 2009-12-31]"
TV_HD = "release_date:[2010-01-01 TO *]"

# --- SITCOM VIBES ---
SITCOM_80S_VIBE = "release_date:[1979-01-01 TO 1989-12-31]"
SITCOM_90S_VIBE = "release_date:[1988-01-01 TO 1999-12-31]"

# --- DECADE RANGES ---
SIXTIES = "release_date:[1960-01-01 TO 1969-12-31]"

# --- SEASONAL TAGS ---
WINTER_TAGS = "(tag:snow OR tag:ice OR tag:blizzard OR tag:cold OR tag:winter OR tag:mountain OR tag:arctic OR tag:alaska OR tag:antarctica OR tag:glacier OR tag:ski OR tag:cabin OR tag:fireplace OR tag:storm OR tag:isolation OR tag:survival OR tag:holiday OR tag:christmas OR tag:newyear)"
FALL_TAGS = "(tag:rain OR tag:fog OR tag:overcast OR tag:autumn OR tag:fall OR tag:leaves OR tag:harvest OR tag:small-town OR tag:noir OR tag:detective OR tag:mystery OR tag:thriller OR tag:psychological OR tag:gothic OR tag:halloween OR tag:witch OR tag:ghost OR tag:haunted OR tag:school OR tag:college OR tag:campus)"
SPRING_TAGS = "(tag:spring OR tag:flowers OR tag:bloom OR tag:garden OR tag:nature OR tag:hiking OR tag:exploration OR tag:travel OR tag:roadtrip OR tag:romance OR tag:dating OR tag:wedding OR tag:coming-of-age OR tag:youth OR tag:festival OR tag:fair OR tag:farm OR tag:countryside OR tag:animals)"
SUMMER_TAGS = "(tag:summer OR tag:beach OR tag:ocean OR tag:lake OR tag:island OR tag:vacation OR tag:resort OR tag:cruise OR tag:camp OR tag:camping OR tag:amusement-park OR tag:festival OR tag:concert OR tag:roadtrip OR tag:sports OR tag:surf OR tag:pool OR tag:heat OR tag:desert OR tag:jungle OR tag:tropical OR tag:teen OR tag:party)"

SEASONAL_TAG_QUERIES = {
    "WINTER": WINTER_TAGS, "FALL": FALL_TAGS, "SPRING": SPRING_TAGS, "SUMMER": SUMMER_TAGS
}

# --- THEMATIC TAGS ---
# Unified Injection Rules
# Supports: Ramps, Static Days, Vetos, and Context Overrides
INJECTION_RULES = {
    "CHRISTMAS": {
        "mode": "ramp",
        "signal": "CHRISTMAS",
        "ratio": 1.0,
        "query": "tag:Christmas",
        "overrides": {
            "Horror": "tag:Krampus OR tag:Christmas Horror",
            "Action": "tag:Christmas AND genre:Action"
        },
        "veto": ["Documentary", "News", "War"]
    },
    "HALLOWEEN": {
        "mode": "ramp",
        "signal": "HALLOWEEN",
        "query": "(tag:halloween OR plot:halloween)",
        "ratio": 0.8,
        "veto": ["Preschool"]
    },
    "THANKSGIVING": {
        "mode": "ramp",
        "signal": "THANKSGIVING",
        "query": "tag:Thanksgiving",
        "ratio": 0.8
    },
    "VALENTINES_DAY": {
        "mode": "static",
        "label": "VALENTINES_DAY",
        "query": '(tag:valentines OR tag:"Valentines Day")',
        "ratio": 1.0,
        "veto": ["Horror", "Crime", "War"]
    },
    "NOVEMBER": {"mode": "static", "label": "NOVEMBER", "query": "(tag:noir OR plot:noir)", "ratio": 0.4},
    "ST_PATRICKS_DAY": {"mode": "static", "label": "ST_PATRICKS_DAY", "query": 'tag:"St Patricks Day"', "ratio": 0.8},
    "NEW_YEARS_EVE": {"mode": "static", "label": "NEW_YEARS_EVE", "query": 'tag:"New Years"', "ratio": 1.0},
    "NEW_YEARS_DAY": {"mode": "static", "label": "NEW_YEARS_DAY", "query": 'tag:"New Years"', "ratio": 0.8},
    "EASTER": {"mode": "static", "label": "EASTER", "query": "tag:Easter", "ratio": 0.8},
    "JULY_4": {"mode": "static", "label": "JULY_4", "query": 'tag:"July 4th"', "ratio": 1.0}
}