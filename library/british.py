"""
British TV and film content -- "Across the Pond" (channel 104).

One BBC/ITV broadcast day. The blocks below are named for what a British
schedule calls the hour they run in, and each one keeps that hour's register:
the vintage half-hours in the small hours, factual over breakfast, the
feature-length mystery through the morning, comedy in the afternoon, Top Gear
at teatime, Doctor Who at seven, drama at eight and the lock-in from eleven.

Two things constrain the pools and are worth knowing before editing:

**Mystery Theatre owns the evening mystery.** `british_mystery_tv` is Poirot,
Marple, Morse and Luther, and Mystery Theatre strips it 17:00-20:00 five nights
a week plus Monday prime, runs `poirot_tv` Saturday 10:00-12:00, `miss_marple_tv`
Saturday 14:00-17:00 and Sunday 10:00-12:00. Sharing those titles is deliberate
(channel-plan.md), but C1 makes the hours a hard rule -- which is why
THE_DAYTIME_MYSTERY runs 09:00-12:00 on weekdays only, why the weekend mornings
are something else entirely, and why Luther sits on Wednesday rather than Monday.

**Channel 4 is half this channel.** `british_comedy_tv` was BBC/ITV only until
this build and could not see Peep Show, Father Ted, The IT Crowd, Spaced, Derry
Girls or Toast of London. It is widened in `sources.py`; the bench under
CLOSEDOWN is the only place it is used broadly, because at 03:00 variety beats
curation.
"""

from scripts.logic.structures import (
    RandomCollection, OrderedCollection, MarathonSequence, Block
)
from scripts.library.queries import (
    show_by_title, movie_by_title, movie_by_title_year
)

# ==============================================================================
# FILLER
# ==============================================================================
#
# 110 British commercials, categorised country/decade/gate/product. They were
# idle until this build: the channel that wants them is this one, and
# `commercials_uk_spot` reaches them without a US channel ever drawing a Dime
# Bar advert. `ENABLE_FILLER` is off globally, so this is a declaration of what
# the channel would run rather than something that fires today.

BRITISH_FILLERS = RandomCollection(["commercials_uk_spot"])

# The Saturday-morning block is Wallace & Gromit and Mr. Bean. Eleven of the 116
# UK spots are beer and spirits, so that block overrides to the family-safe cut.
BRITISH_FILLERS_FAMILY = RandomCollection(["commercials_uk_family_safe_spot"])


# ==============================================================================
# 03:00-06:00 -- CLOSEDOWN
# ==============================================================================
#
# The dead zone, and the only block on the channel that runs a pool key broadly.
# Three named vintage half-hours carry it -- 157 episodes, which is under four
# weeks at 42 half-hours a week and too fast on its own -- with the widened
# `british_comedy_tv` (33 shows, ~995 episodes) as the bench behind them. That
# takes the cycle past twenty weeks. G4's warning is about two curated blocks
# quietly drawing one pool; a deliberate bench at three in the morning is the
# case it does not cover.

KEEP_CALM_COLLECTION = RandomCollection([
    {"title": "Are You Being Served?", "query": show_by_title("Are You Being Served?")},
    {"title": "Keeping Up Appearances", "query": show_by_title("Keeping Up Appearances")},
    {"title": "Gavin & Stacey", "query": show_by_title("Gavin & Stacey")},
    "british_comedy_tv",
])

CLOSEDOWN = Block(
    name="Closedown",
    items=KEEP_CALM_COLLECTION,
)


# ==============================================================================
# 06:00-09:00 -- BREAKFAST
# ==============================================================================
#
# Baking and farming, which is what British daytime actually is. Both are
# hour-ish, so the slot holds three and nothing is stranded (G2). 142 episodes
# against 21 a week is a seven-week cycle.

BREAKFAST = Block(
    name="Breakfast",
    items=RandomCollection([
        {"title": "The Great British Bake Off", "query": show_by_title("The Great British Bake Off")},
        {"title": "Clarkson's Farm", "query": show_by_title("Clarkson's Farm")},
    ]),
)

# Saturday and Sunday mornings. Saturday cannot run the mystery strip -- Mystery
# Theatre has Poirot from ten -- and a children's hour is the right answer
# anyway. Mr. Bean and the Cracking Contraptions are 5-15 minute pieces, so this
# is many short items rather than three long ones, which is what a
# Saturday-morning block should be.
SATURDAY_MORNING = Block(
    name="Saturday Morning",
    items=RandomCollection([
        {"title": "Mr. Bean", "query": show_by_title("Mr. Bean")},
        {"title": "Wallace & Gromit's Cracking Contraptions",
         "query": show_by_title("Wallace & Gromit's Cracking Contraptions")},
    ]),
    filler=BRITISH_FILLERS_FAMILY,
)


# ==============================================================================
# 09:00-12:00 -- THE DAYTIME MYSTERY  (weekdays only)
# ==============================================================================
#
# The ITV3 hour: three feature-length mysteries a morning out of 124 episodes,
# a nine-week cycle. Weekdays only. Mystery Theatre has these titles at
# 17:00-20:00 and on both weekend mornings, and 09:00-12:00 Monday to Friday is
# the window where neither channel is holding them.
#
# Doc Martin used to pad this block and is not a mystery; it moved to the lunch
# hour, where an ITV daytime comedy-drama belongs.

THE_DAYTIME_MYSTERY = Block(
    name="The Daytime Mystery",
    items=RandomCollection([
        {"title": "Agatha Christie's Poirot", "query": show_by_title("Agatha Christie's Poirot")},
        {"title": "Miss Marple", "query": show_by_title("Miss Marple")},
        {"title": "Inspector Morse", "query": show_by_title("Inspector Morse")},
    ]),
)


# ==============================================================================
# 12:00-14:00 -- THE LUNCH BREAK
# ==============================================================================
#
# Travel, talk and the ITV daytime drama. 152 episodes against 21 a week is
# seven weeks. Karl Pilkington appears three ways here and nowhere else on the
# channel, which is the block's actual identity.

THE_LUNCH_BREAK = Block(
    name="The Lunch Break",
    items=RandomCollection([
        {"title": "Doc Martin", "query": show_by_title("Doc Martin")},
        {"title": "An Idiot Abroad", "query": show_by_title("An Idiot Abroad")},
        {"title": "The Moaning of Life", "query": show_by_title("The Moaning of Life")},
        {"title": "The Ricky Gervais Show", "query": show_by_title("The Ricky Gervais Show")},
    ]),
)


# ==============================================================================
# 14:00-17:00 -- BRITCOM AFTERNOON
# ==============================================================================
#
# The modern mainstream half-hours, one block rather than the old A/B pair.
# Splitting them halved a pool that was already only four weeks deep and made
# two blocks out of one; six shows and 241 episodes against 42 a week is six
# weeks, which is the first time this slot has cleared F6.
#
# Ted Lasso is Apple, not a British broadcaster, and is kept as a deliberate
# call -- London setting, British cast, and it reads on air as what this block
# is. It is the only non-UK-commissioned title on the channel.

BRITCOM_AFTERNOON = Block(
    name="Britcom Afternoon",
    items=RandomCollection([
        {"title": "The IT Crowd", "query": show_by_title("The IT Crowd")},
        {"title": "The Office (UK)", "query": 'type:episode AND show_title:"Office" AND show_studio:BBC'},
        {"title": "Derry Girls", "query": show_by_title("Derry Girls")},
        {"title": "Ted Lasso", "query": show_by_title("Ted Lasso")},
        {"title": "Toast of London", "query": show_by_title("Toast of London")},
        {"title": "Life's Too Short", "query": show_by_title("Life's Too Short")},
        {"title": "Coupling", "query": show_by_title("Coupling")},
        {"title": "Outnumbered", "query": show_by_title("Outnumbered")},
    ]),
)


# ==============================================================================
# 17:00-19:00 -- TEATIME
# ==============================================================================
#
# One show, which is the point (G3). 176 episodes of Top Gear is the largest
# single pool on the channel and it is the only thing here that can carry two
# hours a night seven nights a week -- 14 a week, a twelve-week cycle.

# Two shows, not one, and they are the same show: The Grand Tour is the same
# three presenters in the same format, 46 episodes that were on disk and named
# nowhere. Ordered rather than random so the hour still reads as a strip --
# Top Gear leads, and 176 + 46 episodes takes the cycle from twelve weeks to
# fifteen.
TEATIME = Block(
    name="Teatime",
    items=OrderedCollection([
        {"title": "Top Gear", "query": show_by_title("Top Gear"), "order": "Shuffle"},
        {"title": "The Grand Tour", "query": show_by_title("The Grand Tour"), "order": "Shuffle"},
    ]),
)


# ==============================================================================
# 19:00-20:00 -- THE SEVEN O'CLOCK SHOW
# ==============================================================================
#
# Doctor Who, one episode a night, every night. 88 episodes at seven a week is a
# twelve-week cycle, and no other channel on the lineup claims it. An hour on
# its own rather than a share of the teatime block, because a flagship that
# alternates with Top Gear is not a flagship.

THE_SEVEN_OCLOCK_SHOW = Block(
    name="The Seven O'Clock Show",
    items=OrderedCollection([
        {"title": "Doctor Who", "query": show_by_title("Doctor Who"), "order": "Shuffle"},
    ]),
)


# ==============================================================================
# 20:00-23:00 -- PRIME
# ==============================================================================
#
# Five drama nights, a film night and a natural-history night, and no two of
# them draw the same title (G4). The mystery pool is deliberately absent: it
# owns the morning, and putting it here as well would be one pool wearing two
# blocks -- besides handing Mystery Theatre a collision on four nights.

PRIME_MONDAY_GRITTY = Block(
    name="Monday Night Drama",
    items=OrderedCollection([
        {"title": "Peaky Blinders", "query": show_by_title("Peaky Blinders"), "order": "Shuffle"},
        {"title": "Gangs of London", "query": show_by_title("Gangs of London"), "order": "Shuffle"},
    ]),
)

PRIME_TUESDAY_THRILLER = Block(
    name="Tuesday Night Thriller",
    items=OrderedCollection([
        {"title": "Killing Eve", "query": show_by_title("Killing Eve"), "order": "Shuffle"},
        {"title": "The Terror", "query": show_by_title("The Terror"), "order": "Shuffle"},
        {"title": "Years and Years", "query": show_by_title("Years and Years"), "order": "Shuffle"},
    ]),
)

# Luther lives here and not on Monday. Mystery Theatre's Monday prime draws
# `british_mystery_tv`, which contains Luther; Wednesday is Hardboiled over
# there and the title is free.
PRIME_WEDNESDAY_AFTER_DARK = Block(
    name="Wednesday After Dark",
    items=OrderedCollection([
        {"title": "Luther", "query": show_by_title("Luther"), "order": "Shuffle"},
        {"title": "Black Mirror", "query": show_by_title("Black Mirror"), "order": "Shuffle"},
        {"title": "I May Destroy You", "query": show_by_title("I May Destroy You"), "order": "Shuffle"},
    ]),
)

PRIME_THURSDAY_PERIOD = Block(
    name="Thursday Night Period Drama",
    items=OrderedCollection([
        {"title": "Sharpe", "query": show_by_title("Sharpe"), "order": "Shuffle"},
        {"title": "A Young Doctor's Notebook", "query": show_by_title("A Young Doctor's Notebook"), "order": "Shuffle"},
        {"title": "Queer as Folk", "query": show_by_title("Queer as Folk"), "order": "Shuffle"},
    ]),
)

# Friday night sketch. Python, Mitchell and Webb and Serafinowicz are the three
# sketch shows on disk and they were scattered across the afternoon and the
# lock-in, where none of them read as an event. 111 episodes for one night a
# week is eighteen weeks.
PRIME_FRIDAY_SKETCH = Block(
    name="Friday Night Sketch Show",
    items=OrderedCollection([
        {"title": "Monty Python's Flying Circus", "query": show_by_title("Monty Python's Flying Circus"), "order": "Shuffle"},
        {"title": "That Mitchell and Webb Look", "query": show_by_title("That Mitchell and Webb Look"), "order": "Shuffle"},
        {"title": "The Peter Serafinowicz Show", "query": show_by_title("The Peter Serafinowicz Show"), "order": "Shuffle"},
    ]),
)

# Sunday at eight on BBC One, and the least contested hour the channel has --
# nothing else on the lineup runs natural history at all. 59 episodes for one
# night a week is twenty weeks.
PRIME_SUNDAY_NATURAL_HISTORY = Block(
    name="Sunday Night on BBC One",
    items=RandomCollection([
        {"title": "Planet Earth", "query": 'type:episode AND show_title:"Planet Earth"'},
        {"title": "Planet Earth II", "query": show_by_title("Planet Earth II")},
        {"title": "Planet Earth III", "query": show_by_title("Planet Earth III")},
        {"title": "Blue Planet II", "query": show_by_title("Blue Planet II")},
        {"title": "Seven Worlds, One Planet", "query": show_by_title("Seven Worlds, One Planet")},
        {"title": "Prehistoric Planet", "query": show_by_title("Prehistoric Planet")},
        {"title": "Life", "query": 'type:episode AND show_title:"Life" AND show_studio:BBC'},
    ]),
)


# ==============================================================================
# Sunday 09:00-12:00 -- THE OMNIBUS
# ==============================================================================
#
# The week's drama, repeated on a Sunday morning. Every title here has already
# had its own night at eight, which makes this the same escalation the lineup
# already uses when two slots want one pool: not a second helping but a second
# *presentation* (C2, and the weekday/weekend split of G8). At eight it is the
# night's drama; on a Sunday morning it is the omnibus you catch up on.
#
# 228 episodes for three hours once a week is over a year, so nothing here
# competes with the weeknight blocks for pool. It exists because Sunday morning
# was running the Breakfast block a second time -- six unbroken hours of Bake Off
# and Clarkson's Farm, which is the weekday grid printed twice by another name.
#
# Luther is safe here: Mystery Theatre holds `british_mystery_tv` on weekday
# evenings and Monday prime, and its Sunday morning is `miss_marple_tv`.

THE_OMNIBUS = Block(
    name="The Omnibus",
    items=RandomCollection([
        {"title": "Peaky Blinders", "query": show_by_title("Peaky Blinders")},
        {"title": "Gangs of London", "query": show_by_title("Gangs of London")},
        {"title": "Killing Eve", "query": show_by_title("Killing Eve")},
        {"title": "The Terror", "query": show_by_title("The Terror")},
        {"title": "Years and Years", "query": show_by_title("Years and Years")},
        {"title": "Luther", "query": show_by_title("Luther")},
        {"title": "Black Mirror", "query": show_by_title("Black Mirror")},
        {"title": "I May Destroy You", "query": show_by_title("I May Destroy You")},
        {"title": "Sharpe", "query": show_by_title("Sharpe")},
        {"title": "A Young Doctor's Notebook", "query": show_by_title("A Young Doctor's Notebook")},
        {"title": "Queer as Folk", "query": show_by_title("Queer as Folk")},
    ]),
)


# ==============================================================================
# FILM -- Saturday night, and the Sunday matinee
# ==============================================================================
#
# The channel is television with a film shelf, not the other way round (F5):
# roughly 1,600 episodes against 60-odd named British films plus twenty Bond and
# eight Potter. Two film slots a week, ~3 features, which is a twenty-week cycle.
#
# Every film is named. `british_movie` -- the key this block used to draw -- is
# `tag:british OR studio:(BBC|Film4|Working Title|Ealing|Hammer|Warp|DNA)`, and
# the film manifest carries no studio column at all, so the key census can only
# report it as 1,858 films "partial". Nobody can size it offline, it depends on
# studio metadata that may simply be absent in the index, and the Hammer clause
# reaches straight into Nightmare Theatre's shelf. Named titles are checkable by
# `validate_titles`; that key is not, and it is no longer used.
#
# Titles are year-bound where the phrase match is loose (G10).

SATURDAY_NIGHT_CINEMA = Block(
    name="Saturday Night Cinema",
    items=RandomCollection([
        # The Cornetto trilogy. The World's End is filed `World's End, The` on
        # disk, so the old `title:"The World's End"` matched nothing and the
        # trilogy quietly ran as a double bill.
        {"title": "Shaun of the Dead", "query": movie_by_title_year("Shaun of the Dead", 2004)},
        {"title": "Hot Fuzz", "query": movie_by_title_year("Hot Fuzz", 2007)},
        {"title": "The World's End", "query": movie_by_title_year("World's End, The", 2013)},
        # Monty Python. Life of Brian and The Meaning of Life are filed without
        # the apostrophe -- `Monty Pythons ...` -- which is why the old
        # `movie_by_title("Life of Brian")` resolved to nothing.
        {"title": "Monty Python and the Holy Grail", "query": movie_by_title_year("Monty Python and the Holy Grail", 1974)},
        {"title": "Monty Python's Life of Brian", "query": movie_by_title_year("Monty Pythons Life of Brian", 1979)},
        {"title": "Monty Python's The Meaning of Life", "query": movie_by_title_year("Monty Pythons the Meaning of Life", 1983)},
        # Gilliam and the British fantastical
        {"title": "Time Bandits", "query": movie_by_title_year("Time Bandits", 1981)},
        {"title": "Brazil", "query": movie_by_title_year("Brazil", 1985)},
        # Modern British genre
        {"title": "28 Days Later", "query": movie_by_title_year("28 Days Later", 2002)},
        {"title": "Children of Men", "query": movie_by_title_year("Children of Men", 2006)},
        {"title": "V for Vendetta", "query": movie_by_title_year("V for Vendetta", 2005)},
        {"title": "Moon", "query": movie_by_title_year("Moon", 2009)},
        {"title": "Ex Machina", "query": movie_by_title_year("Ex Machina", 2015)},
        {"title": "Dead Man's Shoes", "query": movie_by_title_year("Dead Man's Shoes", 2004)},
        # Crime
        {"title": "Snatch", "query": movie_by_title_year("Snatch", 2000)},
        {"title": "In Bruges", "query": movie_by_title_year("In Bruges", 2008)},
        # Romantic comedy -- the Curtis shelf
        {"title": "Four Weddings and a Funeral", "query": movie_by_title_year("Four Weddings and a Funeral", 1994)},
        {"title": "Notting Hill", "query": movie_by_title_year("Notting Hill", 1999)},
        {"title": "Love Actually", "query": movie_by_title_year("Love Actually", 2003)},
        {"title": "Withnail & I", "query": movie_by_title_year("Withnail & I", 1987)},
    ]),
)

# Sunday 14:00-17:00. Bond on a bank-holiday afternoon is the most British thing
# a schedule can do, and 14:00-17:00 is a genuinely empty film hour on this
# lineup -- unlike 20:00, where four channels start features at once (C7).
THE_SUNDAY_MATINEE = Block(
    name="The Sunday Matinee",
    items=RandomCollection([
        {"title": "James Bond Collection", "query": 'collection:"James Bond"'},
        {"title": "Harry Potter Collection", "query": 'collection:"Harry Potter"'},
        {"title": "Lawrence of Arabia", "query": movie_by_title_year("Lawrence of Arabia", 1962)},
        {"title": "Zulu", "query": movie_by_title_year("Zulu", 1964)},
        {"title": "My Fair Lady", "query": movie_by_title_year("My Fair Lady", 1964)},
        {"title": "Chariots of Fire", "query": movie_by_title_year("Chariots of Fire", 1981)},
        {"title": "Gandhi", "query": movie_by_title_year("Gandhi", 1982)},
        {"title": "1917", "query": movie_by_title_year("1917", 2019)},
        {"title": "Dunkirk", "query": movie_by_title_year("Dunkirk", 2017)},
        {"title": "Atonement", "query": movie_by_title_year("Atonement", 2007)},
        {"title": "Slumdog Millionaire", "query": movie_by_title_year("Slumdog Millionaire", 2008)},
        {"title": "127 Hours", "query": movie_by_title_year("127 Hours", 2010)},
        {"title": "Trainspotting", "query": movie_by_title_year("Trainspotting", 1996)},
        {"title": "The Wind That Shakes the Barley", "query": movie_by_title_year("Wind That Shakes the Barley, The", 2006)},
        {"title": "Chicken Run", "query": movie_by_title_year("Chicken Run", 2000)},
        {"title": "Paddington", "query": movie_by_title_year("Paddington", 2014)},
        {"title": "Paddington 2", "query": movie_by_title_year("Paddington 2", 2017)},
    ]),
)


# ==============================================================================
# 23:00-24:00 and 00:00-03:00 -- THE PUB LOCK-IN
# ==============================================================================
#
# Four hours a night of alternative comedy, split into two slots rather than one
# `night: (23, 2)`. A wrapping slot is entered twice under two different day
# labels, so "Saturday night" resolves to two different nights and an ordered
# collection replays its first items across the boundary (G1). `night` is 23-24
# and `after_hours` is 00-03, each with its own block.
#
# Two variants, not the old three. Three split 380 episodes into a 148-episode
# weekend block that cycled in nine weeks while Python and Mitchell and Webb --
# now the Friday sketch night -- were being spent on it.
#
#   A  Mon / Wed / Fri / Sun   197 eps   32 a week   6 weeks
#   B  Tue / Thu / Sat         184 eps   24 a week   8 weeks

PUB_LOCK_IN_A = Block(
    name="Pub Lock-In: Modern Satire",
    items=OrderedCollection([
        {"title": "Peep Show", "query": show_by_title("Peep Show"), "order": "Shuffle"},
        {"title": "The Thick of It", "query": show_by_title("The Thick of It"), "order": "Shuffle"},
        {"title": "Fleabag", "query": show_by_title("Fleabag"), "order": "Shuffle"},
        {"title": "Spaced", "query": show_by_title("Spaced"), "order": "Shuffle"},
        # `show_title:"Cunk"` matched Cunk on Britain and Cunk on Earth while the
        # item was labelled "Cunk on Earth" -- the validator's one standing
        # finding for four sessions. Both shows are wanted; they are two items now.
        {"title": "Cunk on Earth", "query": show_by_title("Cunk on Earth"), "order": "Shuffle"},
        {"title": "Cunk on Britain", "query": show_by_title("Cunk on Britain"), "order": "Shuffle"},
    ]),
)

PUB_LOCK_IN_B = Block(
    name="Pub Lock-In: Classics & Cult",
    items=OrderedCollection([
        {"title": "Blackadder", "query": show_by_title("Blackadder"), "order": "Shuffle"},
        {"title": "Fawlty Towers", "query": show_by_title("Fawlty Towers"), "order": "Shuffle"},
        {"title": "The Young Ones", "query": show_by_title("The Young Ones"), "order": "Shuffle"},
        {"title": "Father Ted", "query": show_by_title("Father Ted"), "order": "Shuffle"},
        {"title": "Garth Marenghi's Darkplace", "query": show_by_title("Garth Marenghi's Darkplace"), "order": "Shuffle"},
        {"title": "Mandy", "query": show_by_title("Mandy"), "order": "Shuffle"},
        {"title": "Wasted", "query": show_by_title("Wasted"), "order": "Shuffle"},
    ]),
)


# ==============================================================================
# MARATHON SEQUENCES
# ==============================================================================
#
# `find_active_marathon` calls `.pick()` on anything that has one, so a
# RandomCollection handed to a Marathon collapses to a single item: the block
# plays one film and yields the rest of the window back to the ordinary grid.
# Both of this channel's marathons were RandomCollections. They are sequences
# now (G9), and the Bond run is ordered and year-bound (G10) so it plays as a
# run of films rather than a shuffle of everything with "Bond" in the title.

JAMES_BOND_MARATHON = MarathonSequence(items=[
    {"title": "Dr. No", "query": movie_by_title_year("Dr. No", 1962)},
    {"title": "From Russia with Love", "query": movie_by_title_year("From Russia with Love", 1963)},
    {"title": "Goldfinger", "query": movie_by_title_year("Goldfinger", 1964)},
    {"title": "Thunderball", "query": movie_by_title_year("Thunderball", 1965)},
    {"title": "You Only Live Twice", "query": movie_by_title_year("You Only Live Twice", 1967)},
    {"title": "On Her Majesty's Secret Service", "query": movie_by_title_year("On Her Majestys Secret Service", 1969)},
    {"title": "Diamonds Are Forever", "query": movie_by_title_year("Diamonds are Forever", 1971)},
    {"title": "Live and Let Die", "query": movie_by_title_year("Live and Let Die", 1973)},
    {"title": "The Man with the Golden Gun", "query": movie_by_title_year("Man with the Golden Gun, The", 1974)},
    {"title": "The Spy Who Loved Me", "query": movie_by_title_year("Spy Who Loved Me, The", 1977)},
    {"title": "Moonraker", "query": movie_by_title_year("Moonraker", 1979)},
    {"title": "For Your Eyes Only", "query": movie_by_title_year("For Your Eyes Only", 1981)},
    {"title": "Octopussy", "query": movie_by_title_year("Octopussy", 1983)},
    {"title": "A View to a Kill", "query": movie_by_title_year("A View to a Kill", 1985)},
    {"title": "Licence to Kill", "query": movie_by_title_year("Licence to Kill", 1989)},
    {"title": "GoldenEye", "query": movie_by_title_year("Goldeneye", 1995)},
    {"title": "Tomorrow Never Dies", "query": movie_by_title_year("Tomorrow Never Dies", 1997)},
    {"title": "The World Is Not Enough", "query": movie_by_title_year("World Is Not Enough, The", 1999)},
    {"title": "Die Another Day", "query": movie_by_title_year("Die Another Day", 2002)},
    {"title": "Casino Royale", "query": movie_by_title_year("Casino Royale", 2006)},
])

# Doctor Who Day -- 23 November, the anniversary of the 1963 first broadcast.
# This is a holiday *schedule*, not a marathon: `find_active_marathon` returns
# nothing while `is_holiday_season` is true, Thanksgiving's ramp is fourteen
# days, and in most years 23 November falls inside it. A marathon on that date
# could never fire (G9). See `channels/british.py`.
DOCTOR_WHO_DAY_BLOCK = Block(
    name="Doctor Who Day",
    items=OrderedCollection([
        {"title": "Doctor Who", "query": show_by_title("Doctor Who"), "order": "Chronological"},
    ]),
)


# ==============================================================================
# CHRISTMAS
# ==============================================================================
#
# The British Christmas special is the one piece of scheduling this channel
# exists to do, and the pool for it is four items -- three of them tag-dependent
# queries that no offline checker can confirm. So Christmas Day takes the
# specials where they can be found and leaves the rest of the day on the ordinary
# grid rather than on a four-item collection stretched over 24 hours, which is
# what the old holiday schedule did.

BRITISH_CHRISTMAS_COLLECTION = RandomCollection([
    {"title": "The Office Christmas",
     "query": 'type:episode AND show_title:"Office" AND show_studio:BBC AND (tag:christmas OR plot:christmas)'},
    {"title": "Gavin & Stacey Christmas",
     "query": 'show_title:"Gavin & Stacey" AND (tag:christmas OR plot:christmas)'},
    {"title": "Doctor Who Christmas",
     "query": 'show_title:"Doctor Who" AND (tag:christmas OR plot:christmas)'},
    {"title": "Blackadder's Christmas Carol", "query": 'title:"Blackadder\'s Christmas Carol"'},
])

BRITISH_CHRISTMAS = Block(
    name="Christmas Night on BBC One",
    items=BRITISH_CHRISTMAS_COLLECTION,
)
