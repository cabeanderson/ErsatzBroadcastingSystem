"""
Example Sources Registry
------------------------
This file defines the content queries used by channels/example_channel.py.
Copy this file to library/sources.py to get started.
"""

# Helper to create simple query dicts
def query(q, order="Shuffle"):
    return {"query": q, "order": order}

MASTER_SOURCES = {
    # --- Collections ---
    "collection_80s_cartoons": query('genre:Animation AND year:[1980 TO 1989]'),
    "collection_general_movies": query('type:Movie'),
    "collection_christmas_movies": query('type:Movie AND tag:Christmas'),
    "collection_blockbuster_movies": query('type:Movie AND studio:Blockbuster'),
    "collection_horror_movies": query('type:Movie AND genre:Horror'),
    "collection_scifi_series": query('type:Show AND genre:"Sci-Fi"'),
    "collection_star_wars": query('title:"Star Wars"'),
    "collection_news_and_weather": query('genre:News'),
    "collection_sitcoms": query('genre:Comedy AND type:Episode'),
    "collection_drama_series": query('genre:Drama AND type:Episode'),
    "collection_holiday_specials": query('tag:Holiday AND type:Episode'),
    "collection_adult_swim": query('tag:"Adult Swim"'),
    "collection_infomercials": query('tag:Infomercial'),
    "collection_sports": query('genre:Sports'),
    "collection_action_movies": query('type:Movie AND genre:Action'),
    "collection_classic_cartoons": query('genre:Animation AND year:[1940 TO 1979]'),
    "collection_documentaries": query('genre:Documentary'),
    "collection_prestige_drama": query('genre:Drama AND studio:HBO'),
    "collection_yule_log": query('title:"Yule Log"'),
    "collection_christmas_parade": query('title:"Christmas Parade"'),
    "collection_classic_christmas_movies": query('type:Movie AND tag:Christmas AND year:[1940 TO 1980]'),
    "collection_party_music": query('genre:Music'),
    "collection_winter_bumpers": query('tag:Winter AND type:Other'),
    "collection_music_videos": query('type:MusicVideo'),
    "collection_fallback_loops": query('tag:Loop'),

    # --- Shows (Single Play) ---
    "show_daily_talkshow": query('title:"The Daily Show"'),

    # --- Marathons ---
    "scifi_marathon": query('genre:"Sci-Fi"'),

    # --- Branding / Fillers ---
    # These are usually type:Other or type:Clip in ErsatzTV
    "intro_saturday_morning": query('title:"Sat Morning Intro"'),
    "outro_saturday_morning": query('title:"Sat Morning Outro"'),
    "bumpers_cartoons": query('tag:Bumper AND tag:Cartoon'),
    "commercials_80s": query('tag:Commercial AND year:[1980 TO 1989]'),
    "commercials_spot": query('tag:Commercial'),
    
    # --- Fallbacks ---
    # Used if nothing else matches
    "default": query('type:Movie'),
}
