"""
Content Collections for Channel Scheduling
===========================================
Curated collections using smart collection classes.
All keys reference MASTER_SOURCES from library/sources.py
"""

from .structures import RandomCollection, OrderedCollection, WeightedCollection, DailyOrderedCollection

# MOVIE COLLECTIONS (Mostly plain lists for flexibility)
# =================================================================

# Historical Cinema
SILENT_CINEMA = RandomCollection(["20s_silent_movie"])
GOLDEN_AGE_CINEMA = RandomCollection(["30s_golden_age_movie", "classic_hollywood_movie"])
NEW_HOLLYWOOD_CINEMA = RandomCollection(["70s_movie", "80s_movie"])
MODERN_BLOCKBUSTERS = RandomCollection(["90s_movie", "00s_movie", "10s_movie", "blockbuster_action_movie"])

# Spotlights
CYBERPUNK_SPOTLIGHT = RandomCollection(["cyberpunk_movie", "classic_scifi_movie"])
TIME_TRAVEL_SPOTLIGHT = RandomCollection(["classic_scifi_movie", "modern_scifi_movie", "80s_movie"])
ALIEN_INVASION_SPOTLIGHT = RandomCollection(["horror_aliens_movie", "classic_scifi_movie"])

# Genre Marquees
WESTERN_MATINEE = RandomCollection(["western_movie"])
MUSICAL_MARQUEE = RandomCollection(["musical_movie"])
WAR_CHRONICLES = RandomCollection(["war_movie"])
ACTION_ADRENALINE = RandomCollection(["80s_action_movie", "90s_action_movie", "blockbuster_action_movie"])
COMEDY_NIGHT = RandomCollection(["80s_comedy_movie", "90s_comedy_movie"])
NOIR_NIGHT = RandomCollection(["classic_noir_movie", "mystery_crime_movie"])
SCI_FI_SHOWCASE = RandomCollection(["classic_scifi_movie", "modern_scifi_movie", "cyberpunk_movie"])

# Animation Film
ANIMATION_SHOWCASE = RandomCollection([
    "ghibli_movie", 
    "disney_movie", 
    "pixar_movie", 
    "dreamworks_movie"
])

# Monster Vault
CREATURE_FEATURE = RandomCollection(["horror_kaiju_movie", "horror_werewolf_movie"])
UNDEAD_CINEMA = RandomCollection(["horror_zombies_movie", "horror_vampire_movie"])
STALKER_CINEMA = RandomCollection(["horror_slasher_movie", "psych_thriller_movie"])
HORROR_VAULT = RandomCollection(["classic_horror_movie", "horror_found_footage_movie", "horror_aliens_movie"])

# Holiday Movies (Plain lists for event programming)
HALLOWEEN_MARATHON_EVENT = RandomCollection([
    "halloween_all_movie",
    "halloween_comedy_movie",
    "halloween_80s_movie",
    "halloween_90s_movie"
])

CHRISTMAS_FESTIVAL_EVENT = RandomCollection([
    "christmas_all_movie",
    "christmas_family_movie",
    "christmas_classic_movie",
    "christmas_80s_movie",
    "christmas_90s_movie"
])

# LIVE-ACTION TV COLLECTIONS
# =================================================================

# Classic TV - OrderedCollection for nostalgic progression
NICK_AT_NITE = OrderedCollection([
    "i_love_lucy_tv",
    "andy_griffith_tv",
    "dick_van_dyke_tv",
    "bewitched_tv",
    "gilligans_island_tv",
    "mary_tyler_moore_tv",
    "bob_newhart_tv",
    "taxi_tv",
    "cheers_tv",
    "wonder_years_tv"
])

SEVENTIES_MORNING = RandomCollection([
    "mary_tyler_moore_tv",
    "bob_newhart_tv",
    "mash_tv",
    "good_times_tv",
    "sanford_and_son_tv"
])

CLASSIC_SITCOMS_60s_70s = RandomCollection([
    "i_love_lucy_tv",
    "andy_griffith_tv",
    "dick_van_dyke_tv",
    "bewitched_tv",
    "gilligans_island_tv",
    "mary_tyler_moore_tv",
    "bob_newhart_tv",
    "mash_tv",
    "good_times_tv",
    "sanford_and_son_tv"
])

# 1990s Programming Blocks - OrderedCollection for branded lineups
TGIF_PRIMETIME = OrderedCollection([
    "sister_sister_tv",
    "mr_cooper_tv",
    "full_house_tv",
    "family_matters_tv",
    "perfect_strangers_tv",
    "dinosaurs_tv"
])

MUST_SEE_TV = OrderedCollection([
    "seinfeld_tv",
    "the_office_tv",
    "parks_and_recreation_tv",
    "30_rock_tv",
    "community_tv"
])

NINETIES_PRIMETIME = RandomCollection([
    "seinfeld_tv",
    "home_improvement_tv",
    "drew_carey_tv",
    "newsradio_tv",
    "3rd_rock_tv",
    "wings_tv",
    "mad_about_you_tv"
])

NINETIES_DAYTIME = RandomCollection([
    "fresh_prince_tv",
    "saved_by_the_bell_tv",
    "sister_sister_tv",
    "moesha_tv",
    "mr_cooper_tv",
    "coach_tv",
    "nanny_tv",
    "married_children_tv"
])

NINETIES_FAMILY = RandomCollection([
    "full_house_tv",
    "family_matters_tv",
    "fresh_prince_tv",
    "home_improvement_tv",
    "dinosaurs_tv"
])

NINETIES_TEEN = RandomCollection([
    "saved_by_the_bell_tv",
    "sister_sister_tv",
    "moesha_tv",
    "mr_cooper_tv",
    "fresh_prince_tv"
])

# Specialty Rotations
WORKPLACE_COMEDIES = RandomCollection([
    "the_office_tv",
    "parks_and_recreation_tv",
    "30_rock_tv",
    "newsradio_tv",
    "taxi_tv",
    "mary_tyler_moore_tv"
])

WORKING_CLASS_SITCOMS = RandomCollection([
    "married_children_tv",
    "good_times_tv",
    "sanford_and_son_tv",
    "home_improvement_tv",
    "drew_carey_tv"
])

QUIRKY_COMEDIES = RandomCollection([
    "3rd_rock_tv",
    "community_tv",
    "30_rock_tv",
    "dinosaurs_tv",
    "taxi_tv"
])

# Search-Based Era Blocks (Plain lists)
VINTAGE_VAULT = RandomCollection(["vintage_tv", "retro_tv"])
GOLDEN_AGE_TV = RandomCollection(["golden_age_tv", "golden_sitcoms_tv"])
MODERN_HD_TV = RandomCollection(["hd_era_tv", "modern_drama_tv", "modern_sitcoms_tv"])

# Holiday TV Episodes (Plain lists for event programming)
THANKSGIVING_COMEDY_EVENT = RandomCollection([
    "thanksgiving_sitcoms_tv",
    "thanksgiving_animated_tv",
    "thanksgiving_90s_tv"
])

HALLOWEEN_TV_EVENT = RandomCollection([
    "halloween_animated_tv",
    "halloween_sitcoms_tv",
    "halloween_drama_tv"
])

CHRISTMAS_TV_EVENT = RandomCollection([
    "christmas_animated_tv",
    "christmas_80s_sitcoms_tv",
    "christmas_90s_sitcoms_tv",
    "christmas_modern_sitcoms_tv"
])

VALENTINES_COMEDY_EVENT = RandomCollection([
    "valentines_tv",
    "valentines_animation_tv"
])

# Selective Halloween Blocks
HALLOWEEN_KIDS_SPOOKFEST = RandomCollection([
    "halloween_animated_tv",
    "scooby_doo_tv"
])

HALLOWEEN_TEEN_FRIGHTS = RandomCollection([
    "gravity_falls_tv",
    "infinity_train_tv",
    "courage_tv"
])

HALLOWEEN_ADULT_SCARES = RandomCollection([
    "metalocalypse_tv",
    "horror_tv"
])

# ANIMATED TV COLLECTIONS
# =================================================================

# Classic Morning Blocks - OrderedCollection for morning routine
SATURDAY_MORNING = OrderedCollection([
    "scooby_doo_tv",
    "looney_tunes_tv",
    "tom_and_jerry_tv",
    "flintstones_tv",
    "jetsons_tv",
    "popeye_tv",
    "yogi_bear_tv",
    "superman_1941_tv"
])

CLASSIC_CARTOONS = RandomCollection([
    "popeye_tv",
    "looney_tunes_tv",
    "tom_and_jerry_tv",
    "flintstones_tv",
    "jetsons_tv",
    "yogi_bear_tv"
])

# Nickelodeon - RandomCollection for variety
NICKTOONS_VAULT = RandomCollection([
    "monsters_tv",
    "thornberrys_tv",
    "spongebob_tv",
    "zim_tv",
    "avatar_tv",
    "korra_tv",
    "ren_stimpy_tv",
    "ed_edd_eddy_tv"
])

# Adult Swim Main - The Hits
ADULT_SWIM_MAIN = OrderedCollection([
    "rick_morty_tv",
    "archer_tv",
    "bobs_burgers_tv",
    "home_movies_tv",
    "boondocks_tv",
    OrderedCollection(["aqua_teen_tv", "robot_chicken_tv"]),
    "birdman_tv",
    "sealab_2021_tv",
    "metalocalypse_tv",
    "cowboy_bebop_tv"
])

TOONAMI_MAIN = OrderedCollection([
    "sailor_moon_tv",
    "dragon_ball_tv",
    "dragon_ball_z_tv",
    "yu_yu_hakusho_tv",
    "rurouni_kenshin_tv"
])

# Adult Animation - RandomCollection for variety
ADULT_SWIM_AFTER_DARK = RandomCollection([
    "archer_tv",
    "boondocks_tv",
    "home_movies_tv",
    "metalocalypse_tv"
])

ADULT_SWIM_WEIRD_CONTENT = RandomCollection([
    "mouse_12oz_tv",
    "dynamite_tv",
    "bojack_tv",
    "frisky_dingo_tv",
    "birdman_tv",
    "robot_chicken_tv",
    "sealab_2021_tv",
    "aqua_teen_tv",
    "eric_andre_tv",
    "steve_brule_tv"
])

FOX_PRIMETIME = OrderedCollection([
    "simpsons_tv",
    "bobs_burgers_tv",
    "futurama_tv",
    "rick_morty_tv"
])

# Disney - OrderedCollection for afternoon block progression
DISNEY_AFTERNOON = OrderedCollection([
    "talespin_tv",
    "chip_dale_tv",
    "goof_troop_tv",
    "ducktales_tv",
    "darkwing_tv",
    "kim_possible_tv",
    "pepper_ann_tv"
])

DISNEY_MORNING = OrderedCollection([
    "aladdin_tv",
    "hercules_tv",
    "mighty_ducks_tv",
    "buzz_lightyear_tv",
    "goof_troop_tv"
])

# Cartoon Network - RandomCollection for variety
CARTOON_NETWORK_CLASSICS = RandomCollection([
    "courage_tv",
    "daria_tv",
    "dexter_tv",
    "powerpuff_tv",
    "gravity_falls_tv",
    "infinity_train_tv",
    "johnny_bravo_tv",
    "owl_house_tv",
    "animaniacs_tv",
    "pinky_brain_tv"
])

# Action & Superhero - OrderedCollection for DC universe progression
ACTION_ANIMATION = OrderedCollection([
    "batman_tas_tv",
    "new_batman_tv",
    "batman_beyond_tv",
    "justice_league_tv",
    "superman_90s_tv",
    "xmen_tv",
    "spiderman_90s_tv"
])

SUPERHERO_HOUR = OrderedCollection([
    "batman_tas_tv",
    "superman_90s_tv",
    "justice_league_tv",
    "batman_beyond_tv"
])

MARVEL_HOUR = OrderedCollection([
    "xmen_tv",
    "spiderman_90s_tv",
    "tmnt_90s_tv",
    "swat_kats_tv",
])

WB_AFTERNOON = OrderedCollection([
    "animaniacs_tv",
    "pinky_brain_tv",
    "tiny_toon_tv",
    "scooby_doo_tv",
    "batman_tas_tv",
    "batman_beyond_tv",
])

STAR_WARS_ANIMATION = RandomCollection([
    "clone_wars_tv",
    "clone_wars_tv",
    "rebels_tv",
    "bad_batch_tv"
])

# Misc Blocks - Plain lists for flexibility
ANIME_BLOCK = OrderedCollection([
    "pokemon_tv", 
    "dragon_ball_tv", 
    "dragon_ball_z_tv", 
    "anime_action_tv"
])

SYNDICATED_CARTOONS = RandomCollection([
    "gadget_tv",
    "captain_planet_tv",
    "magic_school_bus_tv",
    "mister_t_tv",
    "tmnt_90s_tv",
    "gargoyles_tv"
])

# DBZ Marathon Collection
DBZ_SAGAS = RandomCollection([
    "dbz_saiyan_saga_tv",
    "dbz_frieza_saga_tv",
    "dbz_cell_games_tv"
])

# Simpsons Marathon Collection
SIMPSONS_MARATHON = "simpsons_random_marathon"

# DETECTIVE & CRIME COLLECTIONS
# =================================================================

CLASSIC_DETECTIVES = OrderedCollection([
    "classic_mystery_tv",
    "detective_tv",
    "classic_noir_movie"
])

MODERN_CRIME = OrderedCollection([
    "procedural_tv",
    "modern_mystery_tv",
    "legal_drama_tv"
])

BRITISH_CRIME = OrderedCollection([
    "british_mystery_tv",
    "british_drama_tv"
])

TRUE_CRIME_NIGHT = OrderedCollection([
    "true_crime_tv",
    "mystery_crime_movie"
])

LEGAL_BLOCK = RandomCollection([
    "legal_drama_tv"
])

DETECTIVE_USA_BLOCK = RandomCollection([
    "monk_tv", 
    "psych_tv"
])

DETECTIVE_DRAMEDY_BLOCK = RandomCollection([
    "moonlighting_tv", 
    "elsbeth_tv"
])

DETECTIVE_BRITISH_BLOCK = RandomCollection([
    "poirot_tv", 
    "miss_marple_tv",
    "british_mystery_tv"
])

DETECTIVE_LATE_NIGHT = RandomCollection([
    "columbo_tv",
    "classic_mystery_tv",
    "true_crime_tv"
])

COMMERCIAL_BREAK = RandomCollection([
    "commercials_spot"
])

# SCI-FI & FANTASY COLLECTIONS
# =================================================================

SCIFI_CLASSICS_TV = RandomCollection([
    "classic_scifi_tv",
    "syndicated_scifi_tv"
])

MODERN_SCIFI_BLOCK = RandomCollection([
    "modern_scifi_tv",
    "scifi_tv"
])

FANTASY_ADVENTURE = RandomCollection([
    "fantasy_tv",
    "epic_fantasy_tv",
    "scifi_fantasy_tv"
])

PARANORMAL_FILES = RandomCollection([
    "supernatural_tv",
    "thriller_tv",
    "horror_tv"
])

WHEDONVERSE_SAGA = RandomCollection([
    "buffy_chronological_tv",
    "angel_chronological_tv",
    "firefly_chronological_tv"
])

HERCULES_XENA = RandomCollection([
    "hercules_chronological_tv",
    "xena_chronological_tv"
])

SCIFI_MYTHS = RandomCollection([
    "beyond_belief_chronological_tv",
    "mythbusters_chronological_tv"
])

TREK_MORNING = RandomCollection([
    "star_trek_enterprise_chronological_tv",
    "star_trek_tng_chronological_tv"
])

# Sci-Fi Prime Time Lineups
SCIFI_STARTREK = OrderedCollection([
    "star_trek_tng_chronological_tv",
    "star_trek_ds9_chronological_tv",
    "star_trek_voyager_chronological_tv"
])

SCIFI_INVESTIGATION = OrderedCollection([
    "x_files_chronological_tv",
    "fringe_chronological_tv",
    "millennium_chronological_tv"
])

SCIFI_SPACE_OPERA = OrderedCollection([
    "babylon_5_chronological_tv",
    "stargate_chronological_tv",
    "farscape_chronological_tv"
])

SCIFI_MODERN_EPIC = OrderedCollection([
    "battlestar_galactica_chronological_tv",
    "expanse_chronological_tv",
    "for_all_mankind_chronological_tv"
])

SCIFI_GRITTY = OrderedCollection([
    "terminator_scc_chronological_tv",
    "orphan_black_chronological_tv",
    "high_castle_chronological_tv"
])
