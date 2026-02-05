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