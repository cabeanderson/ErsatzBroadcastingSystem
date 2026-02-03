"""
Live-action TV source definitions.
"""
from .builders import (
    show_source, show_by_title, playback_order, playlist_ref,
    TV_CLASSIC, TV_GOLDEN_AGE, TV_HD, TV_VINTAGE,
    NO_FANTASY, NO_SITCOM, NO_BBC, NO_SCIFI,
    SIXTIES, SEVENTIES, EIGHTIES, NINETIES, Y2K_ERA, TENS,
    SITCOM_80S_VIBE, SITCOM_90S_VIBE, STREAMING_ERA
)

TV_REGISTRY = {
    # ============================================================================
    # GENERAL SEARCHES - GENRE & ERA BASED
    # ============================================================================
    
    # --- SCI-FI ---
    "classic_scifi_tv": show_source(genre='"science fiction"', era=TV_CLASSIC, extra=f"{NO_FANTASY} AND {NO_SITCOM}"),
    "syndicated_scifi_tv": show_source(genre='"science fiction"', era=TV_GOLDEN_AGE, extra=f"{NO_FANTASY} AND {NO_SITCOM}"),
    "golden_scifi_tv": show_source(genre='"science fiction"', era=TV_GOLDEN_AGE, extra=f"{NO_FANTASY} AND {NO_SITCOM}"),
    "modern_scifi_tv": show_source(genre='"science fiction"', era=TV_HD, extra=f"{NO_FANTASY} AND {NO_SITCOM}"),
    "scifi_tv": show_source(genre='"science fiction"', extra=f"{NO_FANTASY} AND {NO_SITCOM}"),
    "scifi_fantasy_tv": show_source(genre='"science fiction"', extra=f"genre:fantasy AND {NO_SITCOM}"),
    "space_opera_tv": show_source(genre='"science fiction"', extra=NO_SITCOM),
    
    # --- FANTASY ---
    "fantasy_pure_tv": show_source(genre="fantasy", extra=f"{NO_SCIFI} AND {NO_SITCOM}"),
    "fantasy_tv": show_source(genre="fantasy", extra=NO_SITCOM),
    "epic_fantasy_tv": show_source(genre="fantasy", tags="(tag:epic OR tag:sword)", extra=NO_SITCOM),
    
    # --- SITCOMS BY ERA ---
    "60s_sitcoms_tv": show_source(tags="tag:sitcom", era=SIXTIES, extra=NO_BBC),
    "70s_sitcoms_tv": show_source(tags="tag:sitcom", era=SEVENTIES, extra=NO_BBC),
    "80s_sitcoms_tv": show_source(tags="tag:sitcom", era=SITCOM_80S_VIBE, extra=NO_BBC),
    "90s_sitcoms_tv": show_source(tags="tag:sitcom", era=SITCOM_90S_VIBE, extra=NO_BBC),
    "00s_sitcoms_tv": show_source(tags="tag:sitcom", era=Y2K_ERA, extra=NO_BBC),
    "10s_sitcoms_tv": show_source(tags="tag:sitcom", era=TENS, extra=NO_BBC),
    "golden_sitcoms_tv": show_source(tags="tag:sitcom", era=TV_GOLDEN_AGE),
    "classic_sitcoms_tv": show_source(tags="tag:sitcom", era=TV_CLASSIC),
    "modern_sitcoms_tv": show_source(tags="tag:sitcom", era=TV_HD),
    
    # --- ACTION & DRAMA BY ERA ---
    "60s_action_tv": show_source(genre="action", era=SIXTIES),
    "80s_action_tv": show_source(genre="action", era=EIGHTIES),
    "90s_action_tv": show_source(genre="action", era=NINETIES),
    "classic_action_tv": show_source(genre="action", era=TV_CLASSIC),
    "syndicated_action_tv": show_source(genre="action", era=TV_GOLDEN_AGE),
    "modern_action_tv": show_source(genre="action", era=TV_HD),
    
    "80s_drama_tv": show_source(genre="drama", era=EIGHTIES, extra=NO_SITCOM),
    "90s_drama_tv": show_source(genre="drama", era=NINETIES, extra=NO_SITCOM),
    "00s_drama_tv": show_source(genre="drama", era=Y2K_ERA, extra=NO_SITCOM),
    "golden_drama_tv": show_source(genre="drama", era=TV_GOLDEN_AGE, extra=NO_SITCOM),
    "modern_drama_tv": show_source(genre="drama", era=TV_HD, extra=NO_SITCOM),
    "prestige_drama_tv": show_source(genre="drama", studio="(HBO OR AMC OR Showtime OR FX)", extra=NO_SITCOM),
    
    # --- COMEDY & MYSTERY ---
    "classic_comedy_tv": show_source(genre="comedy", era=TV_CLASSIC),
    "modern_comedy_tv": show_source(genre="comedy", era=TV_HD),
    "sketch_comedy_tv": show_source(tags="tag:sketch"),
    "procedural_tv": show_source(genre="(mystery OR crime)", tags="tag:procedural"),
    "detective_tv": show_source(genre="(mystery OR crime)", tags="(tag:detective OR tag:investigator)"),
    "classic_mystery_tv": show_source(genre="(mystery OR crime)", era=TV_CLASSIC),
    "modern_mystery_tv": show_source(genre="(mystery OR crime)", era=TV_HD),
    "true_crime_tv": show_source(genre="documentary", extra="genre:crime"),
    
    # --- WESTERN, HORROR, THRILLER ---
    "classic_western_tv": show_source(genre="western", era=TV_CLASSIC),
    "modern_western_tv": show_source(genre="western", era=STREAMING_ERA),
    "western_tv": show_source(genre="western"),
    "horror_tv": show_source(genre="horror"),
    "classic_horror_tv": show_source(genre="horror", era=TV_CLASSIC),
    "modern_horror_tv": show_source(genre="horror", era=TV_HD),
    "thriller_tv": show_source(genre="thriller"),
    "supernatural_tv": show_source(genre="(supernatural OR tag:paranormal)"),
    
    # --- NETWORK SPECIFIC ---
    "hbo_drama_tv": show_source(genre="drama", studio="HBO", extra=NO_SITCOM),
    "hbo_comedy_tv": show_source(genre="comedy", studio="HBO"),
    "showtime_drama_tv": show_source(genre="drama", studio="Showtime", extra=NO_SITCOM),
    "amc_drama_tv": show_source(genre="drama", studio="AMC", extra=NO_SITCOM),
    "fx_drama_tv": show_source(genre="drama", studio="FX", extra=NO_SITCOM),
    "nbc_sitcoms_tv": show_source(tags="tag:sitcom", studio="NBC"),
    "cbs_sitcoms_tv": show_source(tags="tag:sitcom", studio="CBS"),
    "abc_sitcoms_tv": show_source(tags="tag:sitcom", studio="ABC"),
    "fox_sitcoms_tv": show_source(tags="tag:sitcom", studio="Fox"),
    
    # --- INTERNATIONAL & SPECIALTY ---
    "british_comedy_tv": show_source(genre="comedy", studio="(bbc OR itv)", tags="(tag:sitcom OR genre:comedy)"),
    "british_mystery_tv": show_source(genre="mystery", studio="(bbc OR itv)"),
    "british_drama_tv": show_source(genre="drama", studio="(bbc OR itv)"),
    "bbc_classics_tv": show_source(studio="bbc", era=TV_CLASSIC),
    "family_tv": show_source(rating="(content_rating:TV-G OR content_rating:TV-PG)"),
    "mature_tv": show_source(rating="(content_rating:TV-MA OR content_rating:TV-14)"),
    "kids_tv": show_source(rating="(content_rating:TV-Y OR content_rating:TV-Y7)"),
    "unscripted_alt_tv": show_source(genre="(documentary OR tag:alternative)", extra="(title:*Wilson* OR title:*Nathan*)"),
    "reality_classic_tv": show_source(genre="reality", era=TV_GOLDEN_AGE),
    "reality_competition_tv": show_source(genre="reality", tags="tag:competition"),
    "documentary_tv": show_source(genre="documentary"),
    "talk_show_tv": show_source(tags="(tag:talk-show OR tag:late-night)"),
    "legal_drama_tv": show_source(genre="drama", tags="(tag:legal OR tag:courtroom)", extra=NO_SITCOM),
    "medical_drama_tv": show_source(genre="drama", tags="(tag:medical OR tag:hospital)", extra=NO_SITCOM),
    "military_tv": show_source(tags="(tag:military OR tag:war)"),
    "sports_drama_tv": show_source(genre="drama", tags="tag:sports", extra=NO_SITCOM),
    "teen_drama_tv": show_source(genre="drama", tags="(tag:teen OR tag:high-school)", extra=NO_SITCOM),
    "workplace_comedy_tv": show_source(tags="tag:sitcom", extra="tag:workplace"),
    "family_drama_tv": show_source(genre="drama", tags="tag:family", extra=NO_SITCOM),
    
    # --- ERA CATCH-ALLS ---
    "vintage_tv": show_source(era=TV_VINTAGE),
    "retro_tv": show_source(era=TV_CLASSIC),
    "golden_age_tv": show_source(era=TV_GOLDEN_AGE),
    "hd_era_tv": show_source(era=TV_HD),
    
    
    # ============================================================================
    # INDIVIDUAL SHOWS - ORGANIZED BY GENRE & ERA
    # ============================================================================
    
    # --- SITCOMS ---
    
    # Classic Era (1950s-1970s)
    "i_love_lucy_tv": show_by_title("i love lucy"),
    "andy_griffith_tv": show_by_title("the andy griffith show"),
    "dick_van_dyke_tv": show_by_title("the dick van dyke show"),
    "bewitched_tv": show_by_title("bewitched"),
    "gilligans_island_tv": show_by_title("gilligan's island"),
    "mary_tyler_moore_tv": show_by_title("the mary tyler moore show"),
    "bob_newhart_tv": show_by_title("the bob newhart show"),
    "mash_tv": show_by_title("m*a*s*h"),
    "good_times_tv": show_by_title("good times"),
    "sanford_and_son_tv": show_by_title("sanford and son"),
    
    # 1980s
    "taxi_tv": show_by_title("taxi"),
    "cheers_tv": show_by_title("cheers"),
    "wonder_years_tv": show_by_title("the wonder years"),
    "family_matters_tv": show_by_title("family matters"),
    "perfect_strangers_tv": show_by_title("perfect strangers"),
    "full_house_tv": show_by_title("full house"),
    "coach_tv": show_by_title("coach"),
    
    # 1990s
    "seinfeld_tv": show_by_title("seinfeld"),
    "fresh_prince_tv": show_by_title("the fresh prince of bel-air"),
    "saved_by_the_bell_tv": show_by_title("saved by the bell"),
    "sister_sister_tv": show_by_title("sister, sister"),
    "moesha_tv": show_by_title("moesha"),
    "mr_cooper_tv": show_by_title("hangin' with mr. cooper"),
    "home_improvement_tv": show_by_title("home improvement"),
    "drew_carey_tv": show_by_title("the drew carey show"),
    "newsradio_tv": show_by_title("newsradio"),
    "3rd_rock_tv": show_by_title("3rd rock from the sun"),
    "wings_tv": show_by_title("wings"),
    "mad_about_you_tv": show_by_title("mad about you"),
    "nanny_tv": show_by_title("the nanny"),
    "married_children_tv": show_by_title("married... with children"),
    "dinosaurs_tv": show_by_title("dinosaurs"),
    
    # 2000s+
    "the_office_tv": show_by_title("the office"),
    "parks_and_recreation_tv": show_by_title("parks and recreation"),
    "30_rock_tv": show_by_title("30 rock"),
    "community_tv": show_by_title("community"),
    
    
    # --- SCI-FI SHOWS ---
    
    # Star Trek Franchise
    "star_trek_tos_chronological_tv": playback_order(show_by_title("star trek"), force="Chronological"),
    "star_trek_tng_chronological_tv": playback_order(show_by_title("star trek: the next generation"), force="Chronological"),
    "star_trek_ds9_chronological_tv": playback_order(show_by_title("star trek: deep space nine"), force="Chronological"),
    "star_trek_voyager_chronological_tv": playback_order(show_by_title("star trek: voyager"), force="Chronological"),
    "star_trek_enterprise_chronological_tv": playback_order(show_by_title("enterprise"), force="Chronological"),
    "star_trek_all_playlist": playlist_ref("ALL", "Star Trek"),
    
    # Stargate Franchise
    "stargate_chronological_tv": playback_order('show_title:"stargate"', force="Chronological"),
    
    # Space Opera
    "alias_chronological_tv": playback_order(show_by_title("Alias"), force="Chronological"),
    "babylon_5_chronological_tv": playback_order(show_by_title("babylon 5"), force="Chronological"),
    "battlestar_galactica_chronological_tv": playback_order(show_by_title("battlestar galactica"), force="Chronological"),
    "expanse_chronological_tv": playback_order(show_by_title("the expanse"), force="Chronological"),
    "farscape_chronological_tv": playback_order(show_by_title("farscape"), force="Chronological"),
    "firefly_chronological_tv": playback_order(show_by_title("Firefly"), force="Chronological"),
    "orville_tv": show_by_title("The Orville"),
    
    # Other Sci-Fi
    "dark_angel_chronological_tv": playback_order(show_by_title("Dark Angel"), force="Chronological"),
    "devs_chronological_tv": playback_order(show_by_title("Devs"), force="Chronological"),
    "for_all_mankind_chronological_tv": playback_order(show_by_title("for all mankind"), force="Chronological"),
    "fringe_chronological_tv": playback_order(show_by_title("fringe"), force="Chronological"),
    "high_castle_chronological_tv": playback_order(show_by_title("the man in the high castle"), force="Chronological"),
    "lost_chronological_tv": playback_order(show_by_title("Lost"), force="Chronological"),
    "lost_s1": 'show_title:"Lost" AND season_number:1',
    "lost_s2": 'show_title:"Lost" AND season_number:2',
    "lost_s3": 'show_title:"Lost" AND season_number:3',
    "lost_s4": 'show_title:"Lost" AND season_number:4',
    "lost_s5": 'show_title:"Lost" AND season_number:5',
    "lost_s6": 'show_title:"Lost" AND season_number:6',
    "orphan_black_chronological_tv": playback_order(show_by_title("orphan black"), force="Chronological"),
    "terminator_scc_chronological_tv": playback_order(show_by_title("terminator: the sarah connor chronicles"), force="Chronological"),
    "the_oa_chronological_tv": playback_order(show_by_title("The OA"), force="Chronological"),
    "quantum_leap_chronological_tv": playback_order(show_by_title("Quantum Leap"), force="Chronological"),
    "knight_rider_tv": show_by_title("Knight Rider"),
    
    # Sci-Fi Adjacent / Speculative
    "black_mirror_chronological_tv": playback_order(show_by_title("Black Mirror"), force="Chronological"),
    "twilight_zone_chronological_tv": playback_order(show_by_title("Twilight Zone"), force="Chronological"),
    
    # X-Files & Supernatural Investigation
    "x_files_tv": show_by_title("the x-files"),
    "x_files_chronological_tv": playback_order(show_by_title("the x-files"), force="Chronological"),
    "millennium_chronological_tv": playback_order(show_by_title("millennium"), force="Chronological"),
    "twin_peaks_chronological_tv": playback_order(show_by_title("Twin Peaks"), force="Chronological"),
    
    # Prestige Crime (Sequential)
    "true_detective_s1": 'show_title:"True Detective" AND season_number:1',
    "fargo_s1": 'show_title:"Fargo" AND season_number:1',
    
    # Mutants & Superheroes
    "mutant_x_chronological_tv": playback_order(show_by_title("Mutant X"), force="Chronological"),
    
    
    # --- FANTASY SHOWS ---
    
    # Sword & Sorcery
    "hercules_chronological_tv": playback_order(show_by_title("Hercules: The Legendary Journeys"), force="Chronological"),
    "xena_chronological_tv": playback_order(show_by_title("Xena: Warrior Princess"), force="Chronological"),
    "cleopetra_2525_chronological_tv": playback_order(show_by_title("Cleopetra 2525"), force="Chronological"),
    
    # Time Travel / British Sci-Fi Fantasy
    "dr_who_tv": playback_order(show_by_title("Dr Who")),
    "dr_who_chronological_tv": playback_order(show_by_title("Dr Who"), force="Chronological"),
    
    # Vampires & Supernatural
    "buffy_chronological_tv": playback_order(show_by_title("Buffy"), force="Chronological"),
    "angel_chronological_tv": playback_order(show_by_title("Angel"), force="Chronological"),
    
    
    # --- DETECTIVE / MYSTERY SHOWS ---
    
    # Classic Detectives
    "columbo_tv": show_by_title("columbo"),
    "sherlock_holmes_tv": show_by_title("the adventures of sherlock holmes"),
    "poirot_tv": show_by_title("agatha christie's poirot"),
    "miss_marple_tv": show_by_title("miss marple"),
    
    # Modern Detectives
    "monk_tv": show_by_title("monk"),
    "monk_chronological_tv": playback_order(show_by_title("monk"), force="Chronological"),
    "psych_tv": show_by_title("psych"),
    "elsbeth_tv": show_by_title("elsbeth"),
    
    # Detective Comedy/Drama
    "moonlighting_tv": show_by_title("moonlighting"),
    
    
    # --- COMEDY / SKETCH / ALTERNATIVE ---
    
    # Adult Swim
    "eric_andre_tv": show_by_title("the eric andre show"),
    "steve_brule_tv": show_by_title("check it out! with dr. steve brule"),
    
    
    # --- DOCUMENTARY / EDUCATIONAL ---
    
    "mythbusters_chronological_tv": playback_order(show_by_title("Mythbusters"), force="Chronological"),
    
    
    # --- ANTHOLOGY / SPECULATIVE FICTION ---
    
    "beyond_belief_chronological_tv": playback_order('show_title:"beyond belief*"', force="Chronological"),
}