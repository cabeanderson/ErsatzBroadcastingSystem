"""
Be Kind Rewind Content - the video store, 1980 to now

The largest pool on the lineup by a wide margin: 1,530 live-action films from
1980 on, which is a 122-day cycle at twenty-four hours a day. Cabes Classic
Cinema lives on 328 and High Noon on 46.

That size is the whole reason this channel can do something none of the others
can. Nightmare Theatre organizes by the clock because it has one genre; High
Noon organizes around a television spine because it has 946 episodes and 46
films. Be Kind Rewind has no single genre and no spine, so it organizes by the
**week** -- Friday is new releases, Saturday is the blockbuster, Sunday is the
drama, the small hours are the cult shelf. A viewer should be able to tell what
day it is from what is on.

It is a video store rather than a cinema. The shelves are the sub-genres, the
decade rotation is the back catalogue, and the Friday night wall is the only
thing on the lineup that promises something *recent*.

**Nothing here is exclusive.** An earlier plan proposed fencing 2018-and-later
off for this channel so the lineup could keep "zero shared film pools"; that
constraint was retired before it was built. Totally 80s keeps the whole of the
1980s, Other Worlds keeps science fiction, Mystery Theatre keeps modern crime
and Nightmare Theatre keeps horror, and this channel overlaps every one of
them. The rule is only that the same title must not air on two channels in the
same hour, and that is a grid problem -- see `channels/be_kind_rewind.py` for
the hours each neighbour occupies and which shelf answers it.

Two exclusions are made at the key rather than by hours, because Nightmare
Theatre and High Noon both draw *every* era of their genre and both run film in
this channel's prime: `NO_HORROR` and `NO_WESTERN` are on the wide keys. Every
other border is kept by the clock.
"""

import re

from scripts.logic.structures import (
    RandomCollection, DailyOrderedCollection, MarathonSequence
)
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.models import Swap, Feather
from scripts.library.queries import movie_by_title_year


# The library sorts a leading article to the end of a film's title, so The Big
# Lebowski is on disk as "Big Lebowski, The" and a query has to ask for it that
# way. A listing does not: `library/british.py` writes the two forms out by
# hand for every such title, which is the same split done once here.
_SORTED_ARTICLE = re.compile(r"^(.*), (The|A|An)$")


def _film(title, year):
    """A named, year-bounded film, in the {title, query} shape collections take.

    `title` is the manifest's form -- the one the query must match. The
    listing name is derived from it, so a spotlight reads "The Big Lebowski"
    in the guide while still finding "Big Lebowski, The" on disk.
    """
    match = _SORTED_ARTICLE.match(title)
    listing = f"{match.group(2)} {match.group(1)}" if match else title
    return {"title": listing, "query": movie_by_title_year(title, year)}


# ==============================================================================
# THE SHELVES -- one per slot
# ==============================================================================

# 00:00-02:00. Cult Corner. The video store's back wall: the oddities, the
# midnight movies, the films that found their audience on tape rather than in
# a cinema. `eighties_cult_movie` had been in the registry and on no channel.
CULT_CORNER = RandomCollection([
    "eighties_cult_movie",
    "modern_thriller_movie",
])
# The 1980s shelf is deliberately *not* here, though this is a night slot and
# the decade otherwise lives in the night slots. Mystery Theatre runs crime
# film 23:00-02:00 and nothing else, so 00:00-02:00 is the one nocturnal hour
# on this channel that is not free: `80s_pure_movie` against
# `modern_crime_movie` was eleven same-title airings a fortnight, the largest
# collision this channel introduced. The decade sits in The Overnight Bin
# (02:00-06:00, when Mystery Theatre has gone dark) and The Late Show instead.
#
# Which is the hours rule working at the granularity it is supposed to work at:
# not "this channel may not have the 1980s", but "not in these two hours".

# 02:00-06:00. The Overnight Bin -- the whole modern shelf, shuffled, no theme.
#
# This is also where the 1980s live on this channel. Totally 80s runs film from
# 10:00 to 23:00 and is dark from 23:00 to 10:00, so the decade the two
# channels genuinely share is scheduled here and in Cult Corner above, in hours
# the other channel is not broadcasting film at all. That is the hours rule
# doing the work an eviction would otherwise have done.
THE_OVERNIGHT_BIN = RandomCollection([
    "modern_cinema_movie",
    "80s_pure_movie",
    "90s_pure_movie",
])

# 06:00-09:00. The Morning Matinee. Family and PG -- the one part of the day
# the channel is safe for anyone. Disney and Cartoon Network both run animation
# in these hours and this key excludes it by construction (`movie_source`
# drops `genre:animation` unless asked), so the overlap is live-action family
# film against cartoons, which is not the same shelf.
MORNING_MATINEE = RandomCollection([
    "modern_family_movie",
    "family_pg_movie",
])

# 09:00-12:00. The Back Catalogue. Comedy and romance -- daytime television's
# actual register, and the two biggest genres in the library after drama.
THE_BACK_CATALOGUE = RandomCollection([
    "modern_comedy_movie",
    "modern_romance_movie",
])

# 12:00-15:00 and 15:00-18:00. The decade rotation, which is the back half of
# the video-store idea: a shelf per decade, rotated monthly rather than mixed,
# so the afternoon has a character that lasts long enough to notice.
#
# The 1980s are deliberately absent from both -- these hours are exactly when
# Totally 80s runs its own daytime and weekend film.
DECADE_AFTERNOON = ["90s_pure_movie", "00s_pure_movie", "10s_pure_movie", "20s_pure_movie"]

# The afternoon double, second half. Genre x decade rather than raw decade, so
# the two halves of the afternoon do not read as the same block twice.
AFTERNOON_DOUBLE = [
    "90s_action_movie", "00s_action_movie", "10s_action_movie",
    "90s_comedy_movie", "00s_comedy_movie", "10s_comedy_movie",
    "90s_drama_movie", "00s_drama_movie", "10s_drama_movie",
]

# 22:00-24:00. The Late Show. Where the channel gets sharper -- thrillers and
# the harder end of the action shelf, after the family and the appointment
# have both had their hours.
THE_LATE_SHOW = RandomCollection([
    "modern_thriller_movie",
    "modern_action_movie",
    "eighties_cult_movie",
    "80s_pure_movie",
])

# ==============================================================================
# PRIME -- 18:00-22:00, one identity per night
# ==============================================================================
#
# Prime starts at 18:00 rather than 20:00 on purpose. Simulating every channel
# over a fortnight and bucketing film by hour showed 18:00-20:00 is the
# clearest film real estate on the lineup: Nightmare Theatre, High Noon and
# Other Worlds are all running television then, and only Totally 80s has any
# film there at all. By 20:00, when four other channels start features, this
# channel's viewer is already an hour into one.

# FRIDAY. The appointment, and the channel's whole argument. 105 films from
# 2022 on, two features a Friday, which is a little over a year before a repeat.
# Nothing else on the lineup promises anything recent.
NEW_RELEASES = RandomCollection(["new_release_movie"])

# SATURDAY. Blockbuster night -- the franchise shelf and the action spine.
BLOCKBUSTER_NIGHT = RandomCollection([
    "blockbuster_action_movie",
    "modern_adventure_movie",
    "modern_action_movie",
])

# SUNDAY. The drama, which is what Sunday night is for everywhere else and is
# the one register the rest of this channel's week does not cover.
SUNDAY_FEATURE = RandomCollection([
    "modern_drama_movie",
    "90s_drama_movie",
])

# MONDAY. Comedy night.
COMEDY_NIGHT = RandomCollection([
    "modern_comedy_movie",
    "90s_comedy_movie",
    "00s_comedy_movie",
])

# WEDNESDAY. Recent, but not brand new -- the 2018+ shelf, which keeps a
# current film in prime midweek without spending the Friday pool.
RECENT_MIDWEEK = RandomCollection(["recent_movie"])

# ==============================================================================
# SPOTLIGHTS -- Tuesday is the director, Thursday is the star
# ==============================================================================
#
# The one thing a 1,530-film pool buys that no other channel on the lineup can
# afford. Every title below was checked against `reference/library-movies.tsv`
# and is year-bounded: `movie_by_title` is a phrase match, so a bare
# title:"Gladiator" also returns Gladiator II and title:"Predator" returns
# Predator 2.
#
# These are title lists rather than `director:` or `actor:` queries because
# nothing in this repo uses those fields, ERSATZTV_API.md does not document
# them, and whether the index carries them cannot be checked from the
# workstation. A list of titles known to be on disk cannot be wrong in the same
# way. If the fields do turn out to work, these become one-line queries.
#
# **Both cycles are three years long, 36 spotlights each, and that length is
# the point.** They were eight directors and four stars, which `monthly_rotation`
# turned into a director every six months and a star every quarter -- the whole
# spotlight idea collapsing into a rotation you could feel repeating inside one
# year. Twelve was the hard ceiling: a month-keyed dict has twelve slots, and a
# thirteenth entry was accepted and silently never aired. `multiyear_rotation`
# and the YEAR_OF_* labels lift it, so these are sized to the library instead
# of to the mechanism.
#
# The three years are curated rather than arbitrary -- each is a shelf of the
# store, so a year has a character the way a night of the week does. A viewer
# who watches all three sees 36 directors and 36 stars and no repeat.
#
# Sizing: Tuesday and Thursday prime is 18:00-22:00, two features, about 4.3
# times a month -- so a spotlight wants nine films to fill its month without
# repeating one. The stars average ten and clear it. The directors average
# eight and the smallest is five, so the thinner director months play a
# favourite twice. That is a month-long season of one filmmaker, not a defect,
# and it is what the library actually holds: no director below has films on
# disk that were left out.

# --- THE MARQUEE -- the names on the box, the ones a video store puts at eye level

SPIELBERG = RandomCollection([_film(t, y) for t, y in [
    ("E.T. The Extra-Terrestrial", 1982),
    ("Indiana Jones and the Temple of Doom", 1984), ("Empire of the Sun", 1987),
    ("Indiana Jones and the Last Crusade", 1989), ("Hook", 1991),
    ("Jurassic Park", 1993), ("Schindler's List", 1993), ("Saving Private Ryan", 1998),
    ("A.I. Artificial Intelligence", 2001), ("Minority Report", 2002),
    ("Catch Me If You Can", 2002), ("Ready Player One", 2018),
]])

SCORSESE = RandomCollection([_film(t, y) for t, y in [
    ("Raging Bull", 1980), ("Last Temptation of Christ, The", 1988),
    ("Goodfellas", 1990), ("Cape Fear", 1991), ("Age of Innocence, The", 1993),
    ("Casino", 1995), ("Gangs of New York", 2002), ("Departed, The", 2006),
    ("Shutter Island", 2010), ("Hugo", 2011), ("Wolf of Wall Street, The", 2013),
    ("Silence", 2016), ("Irishman, The", 2019), ("Killers of the Flower Moon", 2023),
]])

COEN_BROTHERS = RandomCollection([_film(t, y) for t, y in [
    ("Blood Simple", 1984), ("Raising Arizona", 1987), ("Miller's Crossing", 1990),
    ("Barton Fink", 1991), ("Fargo", 1996), ("Big Lebowski, The", 1998),
    ("O Brother, Where Art Thou", 2000), ("Man Who Wasn't There, The", 2001),
    ("No Country for Old Men", 2007), ("Burn After Reading", 2008),
    ("A Serious Man", 2009), ("True Grit", 2010), ("Inside Llewyn Davis", 2013),
    ("Hail, Caesar!", 2016),
]])

TARANTINO = RandomCollection([_film(t, y) for t, y in [
    ("Reservoir Dogs", 1992), ("Pulp Fiction", 1994), ("Jackie Brown", 1997),
    ("Kill Bill Vol. 1", 2003), ("Kill Bill - Vol. 2", 2004),
    ("Grindhouse - Death Proof", 2007), ("Inglourious Basterds", 2009),
    ("Django Unchained", 2012), ("Hateful Eight, The", 2015),
    ("Once Upon a Time in Hollywood", 2019),
]])

NOLAN = RandomCollection([_film(t, y) for t, y in [
    ("Memento", 2000), ("Insomnia", 2002), ("Batman Begins", 2005),
    ("Prestige, The", 2006), ("Dark Knight, The", 2008), ("Inception", 2010),
    ("Dark Knight Rises, The", 2012), ("Interstellar", 2014), ("Dunkirk", 2017),
    ("Tenet", 2020), ("Oppenheimer", 2023),
]])

CAMERON = RandomCollection([_film(t, y) for t, y in [
    ("Terminator, The", 1984), ("Aliens", 1986), ("Abyss, The", 1989),
    ("Terminator 2 - Judgment Day", 1991), ("True Lies", 1994), ("Titanic", 1997),
    ("Avatar", 2009), ("Avatar - The Way of Water", 2022),
]])

ZEMECKIS = RandomCollection([_film(t, y) for t, y in [
    ("Romancing the Stone", 1984), ("Back to the Future", 1985),
    ("Who Framed Roger Rabbit", 1988), ("Back to the Future Part II", 1989),
    ("Back to the Future Part III", 1990), ("Death Becomes Her", 1992),
    ("Forrest Gump", 1994), ("Contact", 1997), ("Cast Away", 2000),
]])

RIDLEY_SCOTT = RandomCollection([_film(t, y) for t, y in [
    ("Blade Runner", 1982), ("Legend", 1985), ("Thelma & Louise", 1991),
    ("Gladiator", 2000), ("Black Hawk Down", 2001), ("Matchstick Men", 2003),
    ("Kingdom of Heaven", 2005), ("American Gangster", 2007), ("Prometheus", 2012),
    ("Gladiator II", 2024),
]])

FINCHER = RandomCollection([_film(t, y) for t, y in [
    ("Se7en", 1995), ("Game, The", 1997), ("Fight Club", 1999), ("Panic Room", 2002),
    ("Zodiac", 2007), ("Girl with the Dragon Tattoo, The", 2011), ("Gone Girl", 2014),
]])

WES_ANDERSON = RandomCollection([_film(t, y) for t, y in [
    ("Bottle Rocket", 1996), ("Rushmore", 1998), ("Royal Tenenbaums, The", 2001),
    ("Life Aquatic with Steve Zissou, The", 2004), ("Hotel Chevalier", 2007),
    ("Darjeeling Limited, The", 2007), ("Moonrise Kingdom", 2012),
    ("Grand Budapest Hotel, The", 2014), ("Isle of Dogs", 2018),
    ("French Dispatch, The", 2021), ("Asteroid City", 2023),
    ("Phoenician Scheme, The", 2025),
]])

PETER_JACKSON = RandomCollection([_film(t, y) for t, y in [
    ("Meet the Feebles", 1989), ("Heavenly Creatures", 1994),
    ("Frighteners, The", 1996),
    ("Lord of the Rings The Fellowship of the Ring The", 2001),
    ("Lord of the Rings The Two Towers The", 2002),
    ("Lord of the Rings The Return of the King The", 2003), ("King Kong", 2005),
    ("Hobbit - An Unexpected Journey, The", 2012),
    ("Hobbit - The Desolation of Smaug, The", 2013),
    ("Hobbit - The Battle of the Five Armies, The", 2014),
    ("They Shall Not Grow Old", 2018),
]])

VILLENEUVE = RandomCollection([_film(t, y) for t, y in [
    ("Incendies", 2010), ("Prisoners", 2013), ("Enemy", 2014), ("Sicario", 2015),
    ("Arrival", 2016), ("Blade Runner 2049", 2017), ("Dune", 2021),
    ("Dune - Part Two", 2024),
]])

# --- THE GENRE SHELF -- the 80s and 90s house directors -- the reason the shelves were full

CARPENTER = RandomCollection([_film(t, y) for t, y in [
    ("Escape from New York", 1981), ("Christine", 1983), ("Starman", 1984),
    ("Big Trouble in Little China", 1986), ("They Live", 1988),
    ("In the Mouth of Madness", 1995),
]])

JOHN_HUGHES = RandomCollection([_film(t, y) for t, y in [
    ("Sixteen Candles", 1984), ("Breakfast Club, The", 1985), ("Weird Science", 1985),
    ("Ferris Bueller's Day Off", 1986), ("Pretty in Pink", 1986),
    ("Planes, Trains and Automobiles", 1987), ("Uncle Buck", 1989),
    ("Home Alone", 1990), ("Career Opportunities", 1991),
]])

TIM_BURTON = RandomCollection([_film(t, y) for t, y in [
    ("Beetlejuice", 1988), ("Batman", 1989), ("Edward Scissorhands", 1990),
    ("Batman Returns", 1992), ("Ed Wood", 1994), ("Mars Attacks!", 1996),
    ("Big Fish", 2003),
]])

JOHN_LANDIS = RandomCollection([_film(t, y) for t, y in [
    ("Blues Brothers, The", 1980), ("An American Werewolf in London", 1981),
    ("Trading Places", 1983), ("Three Amigos!", 1986), ("Coming to America", 1988),
]])

JOE_DANTE = RandomCollection([_film(t, y) for t, y in [
    ("Gremlins", 1984), ("Burbs, The", 1989), ("Gremlins 2 - The New Batch", 1990),
    ("Matinee", 1993), ("Small Soldiers", 1998),
]])

VERHOEVEN = RandomCollection([_film(t, y) for t, y in [
    ("RoboCop", 1987), ("Total Recall", 1990), ("Basic Instinct", 1992),
    ("Showgirls", 1995), ("Starship Troopers", 1997),
]])

RICHARD_DONNER = RandomCollection([_film(t, y) for t, y in [
    ("Goonies, The", 1985), ("Lethal Weapon", 1987), ("Scrooged", 1988),
    ("Lethal Weapon 2", 1989), ("Lethal Weapon 3", 1992), ("Maverick", 1994),
    ("Lethal Weapon 4", 1998),
]])

MCTIERNAN = RandomCollection([_film(t, y) for t, y in [
    ("Predator", 1987), ("Die Hard", 1988), ("Hunt for Red October, The", 1990),
    ("Last Action Hero", 1993), ("Die Hard with a Vengeance", 1995),
    ("Thomas Crown Affair, The", 1999),
]])

SAM_RAIMI = RandomCollection([_film(t, y) for t, y in [
    ("Darkman", 1990), ("Army of Darkness", 1992), ("Simple Plan, A", 1998),
    ("Spider-Man", 2002), ("Spider-Man 2", 2004), ("Spider-Man 3", 2007),
]])

BARRY_SONNENFELD = RandomCollection([_film(t, y) for t, y in [
    ("Addams Family, The", 1991), ("Addams Family Values", 1993), ("Get Shorty", 1995),
    ("Men in Black", 1997), ("Men in Black II", 2002), ("Men in Black 3", 2012),
]])

ROB_REINER = RandomCollection([_film(t, y) for t, y in [
    ("This Is Spinal Tap", 1984), ("Stand by Me", 1986), ("Princess Bride, The", 1987),
    ("When Harry Met Sally...", 1989), ("Misery", 1990), ("Few Good Men, A", 1992),
    ("American President, The", 1995),
]])

ROBERT_RODRIGUEZ = RandomCollection([_film(t, y) for t, y in [
    ("El Mariachi", 1992), ("Desperado", 1995), ("From Dusk Till Dawn", 1996),
    ("Once Upon a Time in Mexico", 2003), ("Sin City", 2005), ("Planet Terror", 2007),
    ("Alita - Battle Angel", 2019),
]])

# --- THE BACK ROOM -- the auteur and world-cinema shelf, the one nobody browsed by accident

LYNCH = RandomCollection([_film(t, y) for t, y in [
    ("Elephant Man, The", 1980), ("Blue Velvet", 1986), ("Wild at Heart", 1990),
    ("Twin Peaks - Fire Walk with Me", 1992), ("Lost Highway", 1997),
    ("Straight Story, The", 1999), ("Mulholland Drive", 2001), ("Inland Empire", 2006),
]])

CRONENBERG = RandomCollection([_film(t, y) for t, y in [
    ("Scanners", 1981), ("Videodrome", 1983), ("Naked Lunch", 1991), ("Crash", 1996),
    ("A History of Violence", 2005), ("Eastern Promises", 2007),
]])

PT_ANDERSON = RandomCollection([_film(t, y) for t, y in [
    ("Boogie Nights", 1997), ("Magnolia", 1999), ("Punch-Drunk Love", 2002),
    ("There Will Be Blood", 2007), ("Master, The", 2012), ("Inherent Vice", 2014),
    ("Phantom Thread", 2017), ("One Battle After Another", 2025),
]])

DEL_TORO = RandomCollection([_film(t, y) for t, y in [
    ("Cronos", 1993), ("Devil's Backbone, The", 2001), ("Blade II", 2002),
    ("Hellboy", 2004), ("Pan's Labyrinth", 2006),
    ("Hellboy II - The Golden Army", 2008), ("Crimson Peak", 2015),
    ("Shape of Water, The", 2017), ("Nightmare Alley", 2021),
]])

CUARON = RandomCollection([_film(t, y) for t, y in [
    ("A Little Princess", 1995), ("Y Tu Mama Tambien", 2001),
    ("Harry Potter and the Prisoner of Azkaban", 2004), ("Children of Men", 2006),
    ("Gravity", 2013), ("Roma", 2018),
]])

BONG_JOON_HO = RandomCollection([_film(t, y) for t, y in [
    ("Memories of Murder", 2003), ("Snowpiercer", 2013), ("Okja", 2017),
    ("Parasite", 2019), ("Mickey 17", 2025),
]])

LINKLATER = RandomCollection([_film(t, y) for t, y in [
    ("Dazed and Confused", 1993), ("Before Sunrise", 1995), ("Waking Life", 2001),
    ("School of Rock", 2003), ("Before Sunset", 2004), ("Before Midnight", 2013),
    ("Boyhood", 2014),
]])

SPIKE_LEE = RandomCollection([_film(t, y) for t, y in [
    ("Do the Right Thing", 1989), ("Malcolm X", 1992), ("25th Hour", 2002),
    ("Inside Man", 2006), ("BlacKkKlansman", 2018),
]])

MICHAEL_MANN = RandomCollection([_film(t, y) for t, y in [
    ("Manhunter", 1986), ("Last of the Mohicans, The", 1992), ("Heat", 1995),
    ("Collateral", 2004), ("Public Enemies", 2009),
]])

TERRY_GILLIAM = RandomCollection([_film(t, y) for t, y in [
    ("Time Bandits", 1981), ("Brazil", 1985),
    ("Adventures of Baron Munchausen, The", 1988), ("12 Monkeys", 1995),
    ("Fear and Loathing in Las Vegas", 1998),
]])

SODERBERGH = RandomCollection([_film(t, y) for t, y in [
    ("Out of Sight", 1998), ("Erin Brockovich", 2000), ("Oceans Eleven", 2001),
    ("Oceans Twelve", 2004), ("Oceans Thirteen", 2007), ("Contagion", 2011),
    ("Logan Lucky", 2017),
]])

DANNY_BOYLE = RandomCollection([_film(t, y) for t, y in [
    ("Trainspotting", 1996), ("Beach, The", 2000), ("28 Days Later", 2002),
    ("Sunshine", 2007), ("Slumdog Millionaire", 2008), ("127 Hours", 2010),
    ("Yesterday", 2019),
]])

# The director cycle, three years long, in the order the years run.
DIRECTORS_CHAIR = [
    # THE MARQUEE
    SPIELBERG, SCORSESE, COEN_BROTHERS, TARANTINO, NOLAN, CAMERON, ZEMECKIS,
    RIDLEY_SCOTT, FINCHER, WES_ANDERSON, PETER_JACKSON, VILLENEUVE,
    # THE GENRE SHELF
    CARPENTER, JOHN_HUGHES, TIM_BURTON, JOHN_LANDIS, JOE_DANTE, VERHOEVEN,
    RICHARD_DONNER, MCTIERNAN, SAM_RAIMI, BARRY_SONNENFELD, ROB_REINER,
    ROBERT_RODRIGUEZ,
    # THE BACK ROOM
    LYNCH, CRONENBERG, PT_ANDERSON, DEL_TORO, CUARON, BONG_JOON_HO, LINKLATER,
    SPIKE_LEE, MICHAEL_MANN, TERRY_GILLIAM, SODERBERGH, DANNY_BOYLE,
]

# --- THE LEADS -- the ones who opened a film on their name alone

TOM_HANKS = RandomCollection([_film(t, y) for t, y in [
    ("Splash", 1984), ("Big", 1988), ("Turner & Hooch", 1989),
    ("Joe Versus the Volcano", 1990), ("A League of Their Own", 1992),
    ("Sleepless in Seattle", 1993), ("Philadelphia", 1993), ("Forrest Gump", 1994),
    ("Apollo 13", 1995), ("That Thing You Do", 1996), ("Saving Private Ryan", 1998),
    ("Cast Away", 2000), ("Road to Perdition", 2002), ("Catch Me If You Can", 2002),
    ("Captain Phillips", 2013),
]])

HARRISON_FORD = RandomCollection([_film(t, y) for t, y in [
    ("Star Wars - Episode V - Empire Strikes Back", 1980),
    ("Indiana Jones and the Raiders of the Lost Ark", 1981), ("Blade Runner", 1982),
    ("Indiana Jones and the Temple of Doom", 1984),
    ("Indiana Jones and the Last Crusade", 1989), ("Patriot Games", 1992),
    ("Fugitive, The", 1993), ("Clear and Present Danger", 1994),
    ("Air Force One", 1997), ("Star Wars - The Force Awakens", 2015),
    ("Blade Runner 2049", 2017),
]])

BRUCE_WILLIS = RandomCollection([_film(t, y) for t, y in [
    ("Die Hard", 1988), ("Die Hard 2", 1990), ("Hudson Hawk", 1991),
    ("Last Boy Scout, The", 1991), ("Death Becomes Her", 1992), ("Pulp Fiction", 1994),
    ("Die Hard with a Vengeance", 1995), ("12 Monkeys", 1995),
    ("Fifth Element, The", 1997), ("Armageddon", 1998), ("Sixth Sense, The", 1999),
    ("Unbreakable", 2000), ("Sin City", 2005), ("RED", 2010), ("Looper", 2012),
]])

TOM_CRUISE = RandomCollection([_film(t, y) for t, y in [
    ("Risky Business", 1983), ("Top Gun", 1986), ("Rain Man", 1988),
    ("Days of Thunder", 1990), ("Few Good Men, A", 1992),
    ("Mission - Impossible", 1996), ("Jerry Maguire", 1996), ("Eyes Wide Shut", 1999),
    ("Magnolia", 1999), ("Minority Report", 2002), ("Collateral", 2004),
    ("Edge of Tomorrow", 2014), ("American Made", 2017), ("Top Gun Maverick", 2022),
]])

DENZEL_WASHINGTON = RandomCollection([_film(t, y) for t, y in [
    ("Glory", 1989), ("Malcolm X", 1992), ("Philadelphia", 1993),
    ("Training Day", 2001), ("Inside Man", 2006), ("American Gangster", 2007),
    ("Gladiator II", 2024),
]])

JULIA_ROBERTS = RandomCollection([_film(t, y) for t, y in [
    ("Steel Magnolias", 1989), ("Sleeping with the Enemy", 1991), ("Hook", 1991),
    ("My Best Friend's Wedding", 1997), ("Notting Hill", 1999),
    ("Erin Brockovich", 2000), ("Oceans Eleven", 2001), ("Oceans Twelve", 2004),
    ("Oceans Thirteen", 2007),
]])

MORGAN_FREEMAN = RandomCollection([_film(t, y) for t, y in [
    ("Glory", 1989), ("Unforgiven", 1992), ("Shawshank Redemption, The", 1994),
    ("Se7en", 1995), ("Outbreak", 1995), ("Deep Impact", 1998), ("Batman Begins", 2005),
    ("Dark Knight, The", 2008), ("RED", 2010), ("RED 2", 2013),
]])

SAMUEL_L_JACKSON = RandomCollection([_film(t, y) for t, y in [
    ("Do the Right Thing", 1989), ("Juice", 1992), ("Jurassic Park", 1993),
    ("Pulp Fiction", 1994), ("Die Hard with a Vengeance", 1995),
    ("Time to Kill, A", 1996), ("Jackie Brown", 1997),
    ("Star Wars - Episode I - The Phantom Menace", 1999), ("Unbreakable", 2000),
    ("Snakes on a Plane", 2006), ("Django Unchained", 2012), ("Avengers, The", 2012),
]])

KEANU_REEVES = RandomCollection([_film(t, y) for t, y in [
    ("Bill & Ted's Excellent Adventure", 1989), ("Bill & Ted's Bogus Journey", 1991),
    ("Speed", 1994), ("Johnny Mnemonic", 1995), ("Devil's Advocate, The", 1997),
    ("Matrix, The", 1999), ("Matrix Reloaded, The", 2003),
    ("Matrix Revolutions, The", 2003), ("John Wick", 2014),
    ("John Wick - Chapter 2", 2017), ("John Wick - Chapter 3 - Parabellum", 2019),
    ("Bill & Ted Face the Music", 2020), ("Matrix Resurrections, The", 2021),
    ("John Wick 4", 2023),
]])

SIGOURNEY_WEAVER = RandomCollection([_film(t, y) for t, y in [
    ("Ghostbusters", 1984), ("Aliens", 1986), ("Working Girl", 1988),
    ("Ghostbusters II", 1989), ("Alien³", 1992), ("Alien Resurrection", 1997),
    ("Galaxy Quest", 1999), ("Avatar", 2009),
]])

ROBERT_DE_NIRO = RandomCollection([_film(t, y) for t, y in [
    ("Raging Bull", 1980), ("Once Upon a Time in America", 1984), ("Brazil", 1985),
    ("Untouchables, The", 1987), ("Goodfellas", 1990), ("Cape Fear", 1991),
    ("Bronx Tale, A", 1993), ("Casino", 1995), ("Heat", 1995), ("Jackie Brown", 1997),
    ("Meet the Parents", 2000), ("Irishman, The", 2019),
    ("Killers of the Flower Moon", 2023),
]])

BRAD_PITT = RandomCollection([_film(t, y) for t, y in [
    ("Thelma & Louise", 1991), ("True Romance", 1993),
    ("Interview with the Vampire", 1994), ("Se7en", 1995), ("12 Monkeys", 1995),
    ("Fight Club", 1999), ("Snatch", 2000), ("Oceans Eleven", 2001),
    ("Assassination of Jesse James by the Coward Robert Ford, The", 2007),
    ("Burn After Reading", 2008), ("Inglourious Basterds", 2009), ("Moneyball", 2011),
    ("Killing Them Softly", 2012), ("Bullet Train", 2022), ("Wolfs", 2024),
]])

# --- THE COMEDY AND ACTION WALLS -- the two shelves a rental shop actually lived on

BILL_MURRAY = RandomCollection([_film(t, y) for t, y in [
    ("Caddyshack", 1980), ("Ghostbusters", 1984), ("Scrooged", 1988),
    ("Ghostbusters II", 1989), ("Groundhog Day", 1993), ("Ed Wood", 1994),
    ("Rushmore", 1998), ("Lost in Translation", 2003),
    ("Life Aquatic with Steve Zissou, The", 2004), ("Zombieland", 2009),
    ("Grand Budapest Hotel, The", 2014),
]])

EDDIE_MURPHY = RandomCollection([_film(t, y) for t, y in [
    ("48 Hrs.", 1982), ("Eddie Murphy - Delirious", 1983), ("Beverly Hills Cop", 1984),
    ("Beverly Hills Cop II", 1987), ("Eddie Murphy Raw", 1987),
    ("Coming to America", 1988), ("Beverly Hills Cop III", 1994),
    ("Nutty Professor, The", 1996), ("Bowfinger", 1999),
    ("Beverly Hills Cop - Axel F", 2024),
]])

JIM_CARREY = RandomCollection([_film(t, y) for t, y in [
    ("Ace Ventura - Pet Detective", 1994), ("Mask, The", 1994),
    ("Dumb and Dummer", 1994), ("Ace Ventura - When Nature Calls", 1995),
    ("Liar Liar", 1997), ("Truman Show, The", 1998), ("Man on the Moon", 1999),
    ("Me Myself and Irene", 2000), ("How the Grinch Stole Christmas", 2000),
    ("Eternal Sunshine of the Spotless Mind", 2004),
]])

ROBIN_WILLIAMS = RandomCollection([_film(t, y) for t, y in [
    ("Good Morning, Vietnam", 1987), ("Dead Poets Society", 1989), ("Hook", 1991),
    ("Mrs. Doubtfire", 1993), ("Jumanji", 1995), ("Good Will Hunting", 1997),
    ("Flubber", 1997), ("What Dreams May Come", 1998), ("Death to Smoochy", 2002),
    ("Man of the Year", 2006),
]])

STEVE_MARTIN = RandomCollection([_film(t, y) for t, y in [
    ("Three Amigos!", 1986), ("Planes, Trains and Automobiles", 1987),
    ("Parenthood", 1989), ("L.A. Story", 1991), ("Father of the Bride", 1991),
    ("Leap of Faith", 1992), ("Bowfinger", 1999),
]])

JOHN_CANDY = RandomCollection([_film(t, y) for t, y in [
    ("Splash", 1984), ("Planes, Trains and Automobiles", 1987),
    ("Great Outdoors, The", 1988), ("Uncle Buck", 1989), ("Home Alone", 1990),
    ("Cool Runnings", 1993), ("Canadian Bacon", 1995),
]])

SCHWARZENEGGER = RandomCollection([_film(t, y) for t, y in [
    ("Conan the Barbarian", 1982), ("Commando", 1985), ("Predator", 1987),
    ("Twins", 1988), ("Total Recall", 1990), ("Kindergarten Cop", 1990),
    ("Terminator 2 - Judgment Day", 1991), ("Last Action Hero", 1993),
    ("True Lies", 1994), ("Jingle All the Way", 1996),
]])

SYLVESTER_STALLONE = RandomCollection([_film(t, y) for t, y in [
    ("Rambo First Blood", 1982), ("Rocky III", 1982),
    ("Rambo - First Blood Part II", 1985), ("Rocky IV", 1985), ("Cobra", 1986),
    ("Rambo III", 1988), ("Rocky V", 1990), ("Cliffhanger", 1993),
    ("Demolition Man", 1993), ("Cop Land", 1997), ("Creed", 2015), ("Creed II", 2018),
    ("Suicide Squad, The", 2021), ("Creed III", 2023),
]])

MEL_GIBSON = RandomCollection([_film(t, y) for t, y in [
    ("Mad Max 2", 1981), ("Mad Max Beyond Thunderdome", 1985), ("Lethal Weapon", 1987),
    ("Lethal Weapon 2", 1989), ("Lethal Weapon 3", 1992), ("Maverick", 1994),
    ("Braveheart", 1995), ("Lethal Weapon 4", 1998), ("Signs", 2002),
]])

JACKIE_CHAN = RandomCollection([_film(t, y) for t, y in [
    ("Wheels on Meals", 1984), ("Police Story", 1985), ("Police Story 2", 1988),
    ("Police Story 3 - Supercop", 1992), ("Rumble in the Bronx", 1995),
    ("Rush Hour", 1998), ("Shanghai Noon", 2000), ("Rush Hour 2", 2001),
    ("Shanghai Knights", 2003),
]])

WESLEY_SNIPES = RandomCollection([_film(t, y) for t, y in [
    ("White Men Can't Jump", 1992), ("Passenger 57", 1992), ("Demolition Man", 1993),
    ("Blade", 1998), ("Blade II", 2002), ("Blade - Trinity", 2004),
    ("Deadpool & Wolverine", 2024),
]])

MICHAEL_KEATON = RandomCollection([_film(t, y) for t, y in [
    ("Beetlejuice", 1988), ("Batman", 1989), ("Batman Returns", 1992),
    ("Multiplicity", 1996), ("Jackie Brown", 1997),
    ("Birdman or (The Unexpected Virtue of Ignorance)", 2014), ("Founder, The", 2016),
    ("Spider-Man - Homecoming", 2017),
]])

# --- THE CHARACTER SHELF -- the faces you rented for, whoever was billed above them

NICOLAS_CAGE = RandomCollection([_film(t, y) for t, y in [
    ("Raising Arizona", 1987), ("Vampire's Kiss", 1988), ("Wild at Heart", 1990),
    ("Rock, The", 1996), ("Con Air", 1997), ("Face Off", 1997),
    ("Gone in Sixty Seconds", 2000), ("Adaptation.", 2002), ("National Treasure", 2004),
    ("National Treasure - Book of Secrets", 2007), ("Mandy", 2018),
    ("Unbearable Weight of Massive Talent, The", 2022),
]])

JOE_PESCI = RandomCollection([_film(t, y) for t, y in [
    ("Raging Bull", 1980), ("Lethal Weapon 2", 1989), ("Goodfellas", 1990),
    ("Home Alone", 1990), ("Lethal Weapon 3", 1992), ("My Cousin Vinny", 1992),
    ("Home Alone 2 - Lost in New York", 1992), ("Casino", 1995),
    ("Lethal Weapon 4", 1998), ("Irishman, The", 2019),
]])

AL_PACINO = RandomCollection([_film(t, y) for t, y in [
    ("Scarface", 1983), ("Scent of a Woman", 1992), ("Heat", 1995),
    ("Devil's Advocate, The", 1997), ("Any Given Sunday", 1999),
    ("Irishman, The", 2019), ("Once Upon a Time in Hollywood", 2019),
]])

WINONA_RYDER = RandomCollection([_film(t, y) for t, y in [
    ("Beetlejuice", 1988), ("Heathers", 1988), ("Edward Scissorhands", 1990),
    ("Mermaids", 1990), ("Bram Stoker's Dracula", 1992),
    ("Age of Innocence, The", 1993), ("Alien Resurrection", 1997),
]])

JOHNNY_DEPP = RandomCollection([_film(t, y) for t, y in [
    ("Cry-Baby", 1990), ("Edward Scissorhands", 1990), ("Ed Wood", 1994),
    ("Fear and Loathing in Las Vegas", 1998), ("Blow", 2001),
    ("Pirates of the Caribbean - The Curse of the Black Pearl", 2003),
    ("Once Upon a Time in Mexico", 2003),
    ("Pirates of the Caribbean - Dead Man's Chest", 2006),
    ("Pirates of the Caribbean - At World's End", 2007), ("Public Enemies", 2009),
]])

FRANCES_MCDORMAND = RandomCollection([_film(t, y) for t, y in [
    ("Blood Simple", 1984), ("Raising Arizona", 1987), ("Mississippi Burning", 1988),
    ("Fargo", 1996), ("Almost Famous", 2000), ("Burn After Reading", 2008),
    ("Three Billboards Outside Ebbing, Missouri", 2017),
]])

JEFF_GOLDBLUM = RandomCollection([_film(t, y) for t, y in [
    ("Earth Girls Are Easy", 1988), ("Jurassic Park", 1993), ("Independence Day", 1996),
    ("Lost World - Jurassic Park, The", 1997), ("Grand Budapest Hotel, The", 2014),
    ("Independence Day - Resurgence", 2016), ("Thor Ragnarok", 2017),
]])

KURT_RUSSELL = RandomCollection([_film(t, y) for t, y in [
    ("Escape from New York", 1981), ("Big Trouble in Little China", 1986),
    ("Tombstone", 1993), ("Stargate", 1994), ("Grindhouse - Death Proof", 2007),
    ("Guardians of the Galaxy Vol. 2", 2017), ("Once Upon a Time in Hollywood", 2019),
]])

CHRISTIAN_BALE = RandomCollection([_film(t, y) for t, y in [
    ("Empire of the Sun", 1987), ("American Psycho", 2000), ("Batman Begins", 2005),
    ("Rescue Dawn", 2007), ("Prestige, The", 2006), ("Dark Knight, The", 2008),
    ("Dark Knight Rises, The", 2012), ("Vice", 2018), ("Ford v Ferrari", 2019),
    ("Thor Love and Thunder", 2022),
]])

LEONARDO_DICAPRIO = RandomCollection([_film(t, y) for t, y in [
    ("Titanic", 1997), ("Beach, The", 2000), ("Catch Me If You Can", 2002),
    ("Gangs of New York", 2002), ("Departed, The", 2006), ("Shutter Island", 2010),
    ("Inception", 2010), ("Django Unchained", 2012), ("Wolf of Wall Street, The", 2013),
    ("Revenant, The", 2015), ("Once Upon a Time in Hollywood", 2019),
    ("Killers of the Flower Moon", 2023),
]])

SCARLETT_JOHANSSON = RandomCollection([_film(t, y) for t, y in [
    ("Lost in Translation", 2003), ("Prestige, The", 2006), ("Avengers, The", 2012),
    ("Her", 2013), ("Jojo Rabbit", 2019), ("Marriage Story", 2019),
    ("Black Widow", 2021), ("Asteroid City", 2023),
]])

TILDA_SWINTON = RandomCollection([_film(t, y) for t, y in [
    ("Michael Clayton", 2007), ("Snowpiercer", 2013),
    ("Grand Budapest Hotel, The", 2014), ("Okja", 2017), ("Suspiria", 2018),
    ("French Dispatch, The", 2021), ("Asteroid City", 2023),
]])

# The star cycle, three years long, in the order the years run.
STAR_OF_THE_MONTH = [
    # THE LEADS
    TOM_HANKS, HARRISON_FORD, BRUCE_WILLIS, TOM_CRUISE, DENZEL_WASHINGTON,
    JULIA_ROBERTS, MORGAN_FREEMAN, SAMUEL_L_JACKSON, KEANU_REEVES, SIGOURNEY_WEAVER,
    ROBERT_DE_NIRO, BRAD_PITT,
    # THE COMEDY AND ACTION WALLS
    BILL_MURRAY, EDDIE_MURPHY, JIM_CARREY, ROBIN_WILLIAMS, STEVE_MARTIN, JOHN_CANDY,
    SCHWARZENEGGER, SYLVESTER_STALLONE, MEL_GIBSON, JACKIE_CHAN, WESLEY_SNIPES,
    MICHAEL_KEATON,
    # THE CHARACTER SHELF
    NICOLAS_CAGE, JOE_PESCI, AL_PACINO, WINONA_RYDER, JOHNNY_DEPP, FRANCES_MCDORMAND,
    JEFF_GOLDBLUM, KURT_RUSSELL, CHRISTIAN_BALE, LEONARDO_DICAPRIO, SCARLETT_JOHANSSON,
    TILDA_SWINTON,
]

# ==============================================================================
# BLOCKS -- seasonal treatments
# ==============================================================================

# Summer is blockbuster season and autumn is thriller season. This is the swap
# Cabes Classic Cinema used to run on `MODERN_BLOCKBUSTERS` every summer, on
# the channel it always belonged to.
SATURDAY_PRIME = SeasonalBlock(
    base=BLOCKBUSTER_NIGHT,
    seasonal={
        "SUMMER": Feather("blockbuster_action_movie", 0.5),
        "FALL":   Feather("modern_thriller_movie", 0.4),
    },
    auto_tag=True
)

# ==============================================================================
# HOLIDAY EVENTS
# ==============================================================================

HALLOWEEN_EVENT = RandomCollection([
    "halloween_modern_movie",
    "halloween_90s_movie",
    "halloween_comedy_movie",
])

CHRISTMAS_EVENT = RandomCollection([
    "christmas_modern_movie",
    "christmas_90s_movie",
    "christmas_80s_movie",
    "christmas_family_movie",
])

# Christmas Eve, 18:00-24:00. Die Hard is on disk and this is the argument the
# channel is built to have.
CHRISTMAS_EVE_FEATURE = DailyOrderedCollection([
    _film("Die Hard", 1988),
    _film("Gremlins", 1984),
])
