"""
Marathon definitions for the content library.
"""

from scripts.logic.factories import themed_marathon

MARATHONS = {
    "dbz_saiyan_saga_tv": themed_marathon(
        show_title="Dragon Ball Z",
        title="Dragon Ball Z Marathon: Saiyan Saga",
        description="Goku races back to Earth to face the invading Saiyan warriors Nappa and Vegeta.",
        season=1,
        episode_range="[21 TO 36]",
        start_hour=14
    ),
    "dbz_frieza_saga_tv": themed_marathon(
        show_title="Dragon Ball Z",
        title="Dragon Ball Z Marathon: Frieza Saga",
        description="The Z Fighters travel to Namek to find the Dragon Balls, but the tyrant Frieza stands in their way.",
        season=3,
        episode_range="[1 TO 33]",
        start_hour=8
    ),
    "dbz_cell_games_tv": themed_marathon(
        show_title="Dragon Ball Z",
        title="Dragon Ball Z Marathon: Cell Games",
        description="The ultimate android Cell challenges Earth's heroes to a tournament for the fate of the planet.",
        season=6,
        episode_range="[10 TO 29]",
        start_hour=12
    ),

    "monk_trudy_arc_tv": themed_marathon(
        show_title="Monk",
        title="Monk Marathon, The Trudy Investigation",
        description="Monk investigates the cause of his wifes murder and find out who planted the car bomb that killed her.",
        theme_tag="main plot",
        start_hour=10,
        start_season=1,
        start_episode=2,
        episode_count=16
    ),

    "simpsons_random_marathon": themed_marathon(
        show_title="The Simpsons",
        title="The Simpsons Marathon",
        description="MARATHON: Golden Age. A random journey through the classic years of Springfield.",
        start_mode="random",
        start_season=[3, 9],
        start_hour=16
    ),

    "cowboy_bebop_complete": themed_marathon(
        show_title="Cowboy Bebop",
        start_hour=10
    ),
}