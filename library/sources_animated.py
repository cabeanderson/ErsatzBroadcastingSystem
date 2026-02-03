"""
Animated TV source definitions.
"""
from .builders import (
    show_source, show_by_title, playback_order,
    ANIME, SHOW, NO_SITCOM,
    NINETIES, TV_CLASSIC
)

ANIMATED_LIBRARY = {
    # --- BROAD TOOLS ---
    "animated_sitcoms_tv": show_source(tags="tag:sitcom", animated=True),
    "adult_animation_tv": show_source(tags="tag:sitcom", rating="(content_rating:TV-MA OR content_rating:TV-14)", animated=True),
    "family_animation_tv": show_source(tags="tag:sitcom", rating="(content_rating:TV-G OR content_rating:TV-PG OR content_rating:TV-Y7)", animated=True),
    "anime_tv": f"{SHOW} AND {ANIME}",
    "anime_action_tv": f"{SHOW} AND {ANIME} AND genre:action",
    "animated_action_tv": show_source(genre="action", animated=True, extra=NO_SITCOM),
    "animated_90s_tv": show_source(era=NINETIES, animated=True),
    "animated_classic_tv": show_source(era=TV_CLASSIC, animated=True),
    "superhero_animated_tv": show_source(tags="(tag:superhero OR tag:marvel OR tag:dc)", animated=True),

    # --- RETRO / CLASSIC ---
    "popeye_tv": show_by_title("popeye"),
    "looney_tunes_tv": show_by_title("looney tunes"),
    "tom_and_jerry_tv": show_by_title("tom and jerry"),
    "flintstones_tv": show_by_title("the flintstones"),
    "jetsons_tv": show_by_title("the jetsons"),
    "scooby_doo_tv": show_by_title("scooby-doo, where are you!"),
    "superman_1941_tv": show_by_title("superman"),
    "yogi_bear_tv": show_by_title("yogi bear"),
    
    # --- 80s / 90s SYNDICATED ---
    "gadget_tv": show_by_title("inspector gadget"),
    "captain_planet_tv": show_by_title("captain planet"),
    "magic_school_bus_tv": show_by_title("the magic school bus"),
    "mister_t_tv": show_by_title("mister t"),
    "tmnt_90s_tv": show_by_title("teenage mutant ninja turtles"),
    "swat_kats_tv": 'show_title:"swat kats*"',
    "gargoyles_tv": show_by_title("gargoyles"),

    # --- NICKTOONS ---
    "monsters_tv": show_by_title("aaahh!!! real monsters"),
    "thornberrys_tv": show_by_title("the wild thornberrys"),
    "spongebob_tv": show_by_title("spongebob squarepants"),
    "zim_tv": show_by_title("invader zim"),
    "avatar_tv": show_by_title("avatar: the last airbender"),
    "korra_tv": show_by_title("the legend of korra"),
    "ren_stimpy_tv": show_by_title("the ren & stimpy show"),
    "ed_edd_eddy_tv": show_by_title("ed, edd n eddy"),

    # --- ADULT SWIM / MATURE ---
    "mouse_12oz_tv": show_by_title("12 oz. mouse"),
    "archer_tv": show_by_title("archer"),
    "dynamite_tv": show_by_title("black dynamite"),
    "boondocks_tv": show_by_title("the boondocks"),
    "bojack_tv": show_by_title("bojack horseman"),
    "rick_morty_tv": show_by_title("rick and morty"),
    "frisky_dingo_tv": show_by_title("frisky dingo"),
    "birdman_tv": show_by_title("harvey birdman, attorney at law"),
    "home_movies_tv": show_by_title("home movies"),
    "metalocalypse_tv": show_by_title("metalocalypse"),
    "robot_chicken_tv": show_by_title("robot chicken"),
    "sealab_2021_tv": show_by_title("sealab 2021"),
    "aqua_teen_tv": show_by_title("aqua teen hunger force"),

    # --- FOX / NETWORK ANIMATION ---
    "bobs_burgers_tv": show_by_title("bob's burgers"),
    "simpsons_tv": show_by_title("the simpsons"),
    "family_guy_tv": show_by_title("family guy"),
    "futurama_tv": show_by_title("futurama"),
    "great_north_tv": show_by_title("the great north"),

    # --- CARTOON NETWORK / DISNEY ---
    "courage_tv": show_by_title("courage the cowardly dog"),
    "daria_tv": show_by_title("daria"),
    "dexter_tv": show_by_title("dexter's laboratory"),
    "powerpuff_tv": show_by_title("the powerpuff girls"),
    "adventure_time_tv": show_by_title("adventure time"),
    "gravity_falls_tv": show_by_title("gravity falls"),
    "infinity_train_tv": show_by_title("infinity train"),
    "johnny_bravo_tv": show_by_title("johnny bravo"),
    "owl_house_tv": show_by_title("the owl house"),
    "animaniacs_tv": show_by_title("animaniacs"),
    "pinky_brain_tv": show_by_title("pinky and the brain"),
    "tiny_toon_tv": show_by_title("tiny toon adventures"),

    # --- STAR WARS ---
    "clone_wars_tv": show_by_title("Clone Wars"),
    "rebels_tv": show_by_title("Rebels"),
    "bad_batch_tv": show_by_title("Bad Batch"),
    "jedi_tales_tv": show_by_title("Tales of the Jedi"),
    "empire_tales_tv": show_by_title("Tales of the Empire"),
    "underworld_tales_tv": show_by_title("Tales of the Underworld"),

    # --- DISNEY ---
    "aladdin_tv": show_by_title("aladdin"),
    "hercules_tv": show_by_title("hercules"),
    "talespin_tv": show_by_title("talespin"),
    "chip_dale_tv": show_by_title("chip 'n' dale rescue rangers"),
    "goof_troop_tv": show_by_title("goof troop"),
    "ducktales_tv": show_by_title("ducktales"),
    "darkwing_tv": show_by_title("darkwing duck"),
    "buzz_lightyear_tv": show_by_title("buzz lightyear of star command"),
    "kim_possible_tv": show_by_title("kim possible"),
    "mighty_ducks_tv": show_by_title("mighty ducks: the animated series"),
    "pepper_ann_tv": show_by_title("pepper ann"),

    # --- DC / MARVEL ANIMATION ---
    "batman_tas_tv": show_by_title("batman: the animated series"),
    "new_batman_tv": show_by_title("new batman adventures"),
    "batman_beyond_tv": show_by_title("batman beyond"),
    "justice_league_tv": show_by_title("justice league"),
    "superman_90s_tv": show_by_title("superman: the animated series"),
    "xmen_tv": 'show_title:"x-men" NOT show_tag:"adult"',
    "spiderman_90s_tv": show_by_title("spider-man"),

    # --- ANIME SERIES ---
    "pokemon_tv": show_by_title("pokémon"),
    "dragon_ball_tv": 'show_title:"Dragon Ball" AND release_date:[1980-01-01 TO 1989-04-21]',
    "dragon_ball_z_tv": playback_order(show_by_title("Dragon Ball Z"), force="Chronological"),
    "dragon_ball_super_tv": 'show_title:"Dragon Ball Super"',
    "dragon_ball_daima_tv": 'show_title:"Dragon Ball Daima"',
    "cowboy_bebop_tv": show_by_title("cowboy bebop"),
    "sailor_moon_tv": 'show_title:"sailor moon" AND NOT show_title:"sailor moon crystal"',
    "yu_yu_hakusho_tv": show_by_title("Yu Yu Hakusho"),
    "rurouni_kenshin_tv": show_by_title("Rurouni Kenshin")
}