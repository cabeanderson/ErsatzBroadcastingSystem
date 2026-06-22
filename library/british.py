"""
British TV Content
Collections and Blocks for "The Telly" channel.
"""

from scripts.logic.structures import RandomCollection, OrderedCollection, Block
from scripts.library.queries import show_by_title, movie_by_title

# --- FILLERS ---

BRITISH_FILLERS = RandomCollection([
    {"title": "Wallace & Gromit", "query": 'title:"Wallace &"'},
    {"title": "Mr. Bean", "query": show_by_title("Mr. Bean")},
   # {"title": "Shaun the Sheep", "query": show_by_title("Shaun the Sheep")}
])

# --- BLOCKS ---

""" KEEP_CALM_AND_CARRY_ON = Block(
    name="Keep Calm and Carry On",
    items=RandomCollection([
      #  {"title": "Are You Being Served?", "query": show_by_title("Are You Being Served?")},
       # {"title": "Keeping Up Appearances", "query": show_by_title("Keeping Up Appearances")},
      #  {"title": "Fawlty Towers", "query": show_by_title("Fawlty Towers")},
      #  {"title": "Wallace & Gromit", "query": 'title:"Wallace &"'}
        {"title": "Doc Martin", "query": show_by_title("Doc Martin")}
    ]),
) """

KEEP_CALM_COLLECTION = RandomCollection([
        {"title": "Are You Being Served?", "query": show_by_title("Are You Being Served?")},
        {"title": "Keeping Up Appearances", "query": show_by_title("Keeping Up Appearances")},
        {"title": "Fawlty Towers", "query": show_by_title("Fawlty Towers")},
        {"title": "Doc Martin", "query": show_by_title("Doc Martin")}
])

KEEP_CALM = Block(
    name="Keep Calm",
    items=KEEP_CALM_COLLECTION,
)

VILLAGE_MYSTERIES = Block(
    name="Village Mysteries",
    items=RandomCollection([
        {"title": "Miss Marple", "query": show_by_title("Miss Marple")},
        {"title": "Agatha Christie's Marple", "query": show_by_title("Miss Marple")},
        {"title": "Doc Martin", "query": show_by_title("Doc Martin")}
    ]),
)

DETECTIVE_HOUR = Block(
    name="Detective Hour",
    items=RandomCollection([
        {"title": "Agatha Christie's Poirot", "query": show_by_title("Agatha Christie's Poirot")},
        {"title": "Inspector Morse", "query": show_by_title("Inspector Morse")}
    ]),
)

THE_LUNCH_BREAK = Block(
    name="The Lunch Break",
    items=RandomCollection([
        {"title": "The Great British Bake Off", "query": show_by_title("The Great British Bake Off")},
        {"title": "Clarkson's Farm", "query": show_by_title("Clarkson's Farm")},
        {"title": "An Idiot Abroad", "query": show_by_title("An Idiot Abroad")},
       # {"title": "Grand Designs", "query": show_by_title("Grand Designs")},
       # {"title": "Antiques Roadshow", "query": show_by_title("Antiques Roadshow")}
    ]),
)

BRITCOM_AFTERNOON_A = Block(
    name="Britcom Afternoon A",
    items=RandomCollection([
        {"title": "The IT Crowd", "query": show_by_title("The IT Crowd")},
        {"title": "The Office (UK)", "query": 'type:episode AND show_title:"Office" AND show_studio:BBC'},
        {"title": "Gavin & Stacey", "query": show_by_title("Gavin & Stacey")},
        {"title": "Outnumbered", "query": show_by_title("Outnumbered")},
        {"title": "Ted Lasso", "query": show_by_title("Ted Lasso")},
    ]),
)

BRITCOM_AFTERNOON_B = Block(
    name="Britcom Afternoon B",
    items=RandomCollection([
        {"title": "Life's Too Short", "query": show_by_title("Life's Too Short")},
        {"title": "The Ricky Gervais Show", "query": show_by_title("The Ricky Gervais Show")},
        {"title": "Toast of London", "query": show_by_title("Toast of London")},
        {"title": "Coupling", "query": show_by_title("Coupling")},
        {"title": "Derry Girls", "query": show_by_title("Derry Girls")}
    ]),
)

TEATIME_FLAGSHIPS = Block(
    name="Teatime Flagships",
    items=OrderedCollection([
        {"title": "Doctor Who", "query": show_by_title("Doctor Who")},
        {"title": "Top Gear", "query": show_by_title("Top Gear")},
     #   {"title": "Taskmaster", "query": show_by_title("Taskmaster")}
    ]),
)

# --- PRIME TIME BLOCKS ---

PRIME_CRIME_BLOCK = Block(
    name="Prime Suspects",
    items=OrderedCollection([
        {"title": "Agatha Christie's Poirot", "query": show_by_title("Agatha Christie's Poirot"), "order": "Shuffle"},
        {"title": "Miss Marple", "query": show_by_title("Miss Marple"), "order": "Shuffle"},
        {"title": "Inspector Morse", "query": show_by_title("Inspector Morse"), "order": "Shuffle"},
        {"title": "Doc Martin", "query": show_by_title("Doc Martin"), "order": "Shuffle"}
    ]),
)

PRIME_DRAMA_A = Block(
    name="British Drama: Gritty & Dark",
    items=OrderedCollection([
      #  {"title": "Luther", "query": show_by_title("Luther"), "order": "Shuffle"},
        {"title": "Gangs of London", "query": show_by_title("Gangs of London"), "order": "Shuffle"},
        {"title": "Peaky Blinders", "query": show_by_title("Peaky Blinders"), "order": "Shuffle"},
        {"title": "The Terror", "query": show_by_title("The Terror"), "order": "Shuffle"}
    ]),
)

PRIME_DRAMA_B = Block(
    name="British Drama: Prestige & Period",
    items=OrderedCollection([
    #    {"title": "Sherlock", "query": show_by_title("Sherlock"), "order": "Shuffle"},
        {"title": "Sharpe", "query": show_by_title("Sharpe"), "order": "Shuffle"},
        {"title": "The Knick", "query": show_by_title("The Knick"), "order": "Shuffle"},
        {"title": "Years and Years", "query": show_by_title("Years and Years"), "order": "Shuffle"}
    ]),
)

PRIME_COMEDY_BLOCK = Block(
    name="Comedy Night",
    items=OrderedCollection([
        {"title": "Peep Show", "query": show_by_title("Peep Show"), "order": "Shuffle"},
        {"title": "The Office (UK)", "query": 'type:episode AND show_title:"Office" AND show_studio:BBC', "order": "Shuffle"},
        {"title": "The IT Crowd", "query": show_by_title("The IT Crowd"), "order": "Shuffle"},
        {"title": "Keeping Up Appearances", "query": show_by_title("Keeping Up Appearances"), "order": "Shuffle"}
    ]),
)

SATURDAY_MOVIE_NIGHT = Block(
    name="Saturday Night Cinema",
    items=RandomCollection([
        {"title": "James Bond Collection", "query": 'collection:"James Bond"'},
        {"title": "Harry Potter Collection", "query": 'collection:"Harry Potter"'},
        {"title": "British Cinema", "query": "british_movie"},
        {"title": "Cornetto Trilogy", "query": 'title:"Shaun of the Dead" OR title:"Hot Fuzz" OR title:"The World\'s End"'}
    ]),
)

BEST_OF_BRITISH_MOVIES = Block(
    name="Best of British Cinema",
    items=RandomCollection([
#        {"title": "The King's Speech", "query": movie_by_title("The King's Speech")},
        {"title": "1917", "query": movie_by_title("1917")},
        {"title": "Dunkirk", "query": movie_by_title("Dunkirk")},
#        {"title": "Darkest Hour", "query": movie_by_title("Darkest Hour")},
        {"title": "Slumdog Millionaire", "query": movie_by_title("Slumdog Millionaire")},
        {"title": "Trainspotting", "query": movie_by_title("Trainspotting")},
        {"title": "Monty Python and the Holy Grail", "query": movie_by_title("Monty Python and the Holy Grail")},
        {"title": "Life of Brian", "query": movie_by_title("Life of Brian")},
#        {"title": "Atonement", "query": movie_by_title("Atonement")},
#        {"title": "Pride & Prejudice", "query": movie_by_title("Pride & Prejudice")},
    ]),
)

# Nightly Rotations (3 Hours approx)

PUB_LOCK_IN_A = Block(
    name="Pub Lock-In: Modern Satire",
    items=OrderedCollection([
        {"title": "Peep Show", "query": show_by_title("Peep Show"), "order": "Shuffle"},
        {"title": "That Mitchell and Webb Look", "query": show_by_title("That Mitchell and Webb Look"), "order": "Shuffle"},
        {"title": "The Thick of It", "query": show_by_title("The Thick of It"), "order": "Shuffle"},
        {"title": "Fleabag", "query": show_by_title("Fleabag"), "order": "Shuffle"},
        {"title": "Cunk on Earth", "query": 'show_title:"Cunk"', "order": "Shuffle"},
        {"title": "Spaced", "query": show_by_title("Spaced"), "order": "Shuffle"}
    ]),
)

PUB_LOCK_IN_B = Block(
    name="Pub Lock-In: Classics & Cult",
    items=OrderedCollection([
        {"title": "Blackadder", "query": show_by_title("Blackadder"), "order": "Shuffle"},
        {"title": "Monty Python's Flying Circus", "query": show_by_title("Monty Python's Flying Circus"), "order": "Shuffle"},
        {"title": "The Young Ones", "query": show_by_title("The Young Ones"), "order": "Shuffle"},
        {"title": "Fawlty Towers", "query": show_by_title("Fawlty Towers"), "order": "Shuffle"},
        {"title": "Toast of London", "query": show_by_title("Toast of London"), "order": "Shuffle"},
        {"title": "Mandy", "query": show_by_title("Mandy"), "order": "Shuffle"},
      #  {"title": "Mandy", "query": show_by_title("Mandy"), "order": "Shuffle"} # Short ep, play twice
    ]),
)

PUB_LOCK_IN_C = Block(
    name="Pub Lock-In: Dark & Edgy",
    items=OrderedCollection([
        {"title": "Black Mirror", "query": show_by_title("Black Mirror"), "order": "Shuffle"}, # ~60m
        {"title": "I May Destroy You", "query": show_by_title("I May Destroy You"), "order": "Shuffle"}, # ~30m
        {"title": "Father Ted", "query": show_by_title("Father Ted"), "order": "Shuffle"}, # ~30m
        {"title": "The IT Crowd", "query": show_by_title("The IT Crowd"), "order": "Shuffle"}, # ~30m
        {"title": "Derry Girls", "query": show_by_title("Derry Girls"), "order": "Shuffle"} # ~30m
    ]),
)

# --- NEW BLOCKS ---

SUNDAY_SANCTUARY = Block(
    name="Sunday Sanctuary",
    items=RandomCollection([
        {"title": "Planet Earth", "query": show_by_title("Planet Earth")},
        {"title": "Blue Planet", "query": 'show_title:"The Blue Planet" OR show_title:"Blue Planet II"'},
        {"title": "Prehistoric Planet", "query": show_by_title("Prehistoric Planet")},
      #  {"title": "Frozen Planet", "query": show_by_title("Frozen Planet")},
        {"title": "Life", "query": 'type:episode AND show_title:"Life" AND show_studio:BBC', "order": "Shuffle"},
      #  {"title": "Life", "query": show_by_title("Life")},
      #  {"title": "Dynasties", "query": show_by_title("Dynasties")},
    ]),
)

FRIDAY_NIGHT_DINNER = Block(
    name="Friday Night Dinner",
    items=OrderedCollection([
      #  {"title": "Friday Night Dinner", "query": show_by_title("Friday Night Dinner"), "order": "Shuffle"},
      #  {"title": "The Inbetweeners", "query": show_by_title("The Inbetweeners"), "order": "Shuffle"},
        {"title": "Father Ted", "query": show_by_title("Father Ted"), "order": "Shuffle"},
      #  {"title": "Black Books", "query": show_by_title("Black Books"), "order": "Shuffle"},
        {"title": "The IT Crowd", "query": show_by_title("The IT Crowd"), "order": "Shuffle"},
        {"title": "Derry Girls", "query": show_by_title("Derry Girls"), "order": "Shuffle"},
        {"title": "Spaced", "query": show_by_title("Spaced"), "order": "Shuffle"},
    ]),
)

JAMES_BOND_FILMS = RandomCollection([
    {"title": "James Bond Collection", "query": 'collection:"James Bond"'}
])

DOCTOR_WHO_COLLECTION = RandomCollection([
    {"title": "Doctor Who", "query": show_by_title("Doctor Who")},
    {"title": "Doctor Who (Classic)", "query": 'show_title:"Doctor Who" AND release_date:[* TO 1989-12-31]'}
])

BRITISH_CHRISTMAS_COLLECTION = RandomCollection([
    {"title": "The Office Christmas", "query": 'type:episode AND show_title:"Office" AND show_studio:BBC AND (tag:christmas OR plot:christmas)'},
    {"title": "Gavin & Stacey Christmas", "query": 'show_title:"Gavin & Stacey" AND (tag:christmas OR plot:christmas)'},
    {"title": "Doctor Who Christmas", "query": 'show_title:"Doctor Who" AND (tag:christmas OR plot:christmas)'},
  #  {"title": "Downton Abbey Christmas", "query": 'show_title:"Downton Abbey" AND tag:christmas'},
    {"title": "Blackadder Christmas", "query": 'title:"Blackadder\'s Christmas Carol"'},
   # {"title": "Vicar of Dibley Christmas", "query": 'show_title:"The Vicar of Dibley" AND tag:christmas'},
  #  {"title": "Call the Midwife Christmas", "query": 'show_title:"Call the Midwife" AND tag:christmas'},
])