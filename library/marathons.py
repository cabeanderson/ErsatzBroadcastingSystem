"""
Marathon definitions for the content library.
"""

from .builders import show_by_title

MARATHONS = {
    "dbz_saiyan_saga_tv": {
        "title": "Dragon Ball Z Marathon: Saiyan Saga",
        "description": "Goku races back to Earth to face the invading Saiyan warriors Nappa and Vegeta.",
        "query": f'{show_by_title("Dragon Ball Z")} AND season_number:1 AND episode_number:[21 TO 36]',
        "order": "Chronological",
        "start_hour": 14
    },
    "dbz_frieza_saga_tv": {
        "title": "Dragon Ball Z Marathon: Frieza Saga",
        "description": "The Z Fighters travel to Namek to find the Dragon Balls, but the tyrant Frieza stands in their way.",
        "query": f'{show_by_title("Dragon Ball Z")} AND season_number:3 AND episode_number:[1 TO 33]',
        "order": "Chronological",
        "start_hour": 8
    },
    "dbz_cell_games_tv": {
        "title": "Dragon Ball Z Marathon: Cell Games",
        "description": "The ultimate android Cell challenges Earth's heroes to a tournament for the fate of the planet.",
        "query": f'{show_by_title("Dragon Ball Z")} AND season_number:6 AND episode_number:[10 TO 29]',
        "order": "Chronological",
        "start_hour": 12
    },

    "monk_trudy_arc_tv": {
        "title": "Monk Marathon, The Trudy Investigation",
        "description": "Monk investigates the cause of his wifes murder and find out who planted the car bomb that killed her.",
        "query": f'{show_by_title("Monk")} AND tag:"main plot"',
        "order": "Chronological",
        "start_hour": 10,
        "start_season": 1,
        "start_episode": 2,
        "episode_count": 16
    },

    "simpsons_random_marathon": {
        "title": "The Simpsons Marathon",
        "description": "MARATHON: Golden Age. A random journey through the classic years of Springfield.",
        "query": show_by_title("The Simpsons"),
        "order": "Chronological",
        "start_mode": "random",
        "start_season": [3, 9],
        "start_hour": 16
    },

    "cowboy_bebop_complete": {
        # "title": "Cowboy Bebop: The Complete Series",
        # "description": "The complete jazz-fueled journey of the Bebop crew, concluding with the movie.",
        "query": show_by_title("Cowboy Bebop"),
        "order": "Chronological",
        "start_hour": 10
    },
}