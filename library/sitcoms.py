"""
Good Times -- the studio audience
=================================

**Identity.** Multi-camera network sitcom, 1951-1999. If it has a laugh track
and it aired on CBS, NBC, ABC or FOX, it is here. That is a *form*, not a date
range (F4): the multi-camera studio-audience sitcom really does end around
2000, when Malcolm in the Middle and The Office replaced it with single-camera.
Everything on the far side of that break -- the single-camera network sitcom,
cable, streaming, sketch and alt comedy -- belongs to Corncob TV.

**Axis (F3): the week is the networks; the day is that network's history.**

Each day of the week belongs to one network and walks its roster across the
clock. The placement is by *fit*, not by date -- CBS Monday opens with The Nanny
(1993) at eight in the morning and closes with Murphy Brown, while its 06:00
sign-on is Dick Van Dyke (1961). Era floats freely, which it can precisely
because the laugh-track line was drawn: every show left on this channel works at
any hour, so nothing has to be fenced into a daypart.

    MONDAY     CBS      the vault day      -- CBS Monday, 1993
    TUESDAY    NBC                         -- NBC Tuesday, 1997
    WEDNESDAY  ABC                         -- ABC Wednesday, 1995
    THURSDAY   NBC                         -- Must See TV
    FRIDAY     ABC                         -- TGIF
    SATURDAY   CBS                         -- The Greatest Night (1973)
    SUNDAY     FOX + the fourth networks   -- Fox Sunday

Roster by network: ABC 18 shows, NBC 15, CBS 11, FOX/UPN/WB 5. Two days each
for the big three and one for FOX, which puts every network on a 16-20 week
cycle -- comfortably past the three-week floor in F6.

**The books.** Three daytime strips a day -- morning, midday, afternoon -- carry
a season-keyed book, so the channel reshuffles its daytime four times a year the
way a real station does while prime, evening and the overnight stay the spine.
Winter leans cosy (Andy Griffith, Bob Newhart, Northern Exposure, Golden Girls),
spring leans bright (Bewitched, Jeannie, Sabrina, Mork), summer leans young
(Saved by the Bell, Sister Sister, Fresh Prince, Full House), fall is the
marquee. Sunday carries no book: five shows would give four names to the same
five titles. See reference/acquisitions.md.

--------------------------------------------------------------------------
THE HOURS RULES (C1/C2 -- every one of these is a title another channel is
airing at that hour, not a matter of taste)
--------------------------------------------------------------------------

Nick at Nite, split at midnight. The documented rule reads "nothing shared
between 21:00 and 02:00", which is stricter than Nick's own grid: `nite` is
21:00-24:00 and holds the pre-1970 seven, `after_hours` is 00:00-02:00 and holds
the 70s shift. Blocking each title only for the hours Nick actually airs it is
what C1 literally asks, and it is what frees Saturday prime below.

  21:00-24:00 (so: prime 20-23 and late 23-24)
      Dick Van Dyke · Andy Griffith · Bewitched · I Dream of Jeannie
      The Addams Family · Gilligan's Island
  00:00-02:00 (so: after_hours)
      Mary Tyler Moore · Bob Newhart · Taxi · M*A*S*H · Sanford and Son
      Good Times · Soap · Mork & Mindy · Smothers Brothers

Totally 80s. Its evening splits Mon-Fri from Sat-Sun and the two arms hold
different titles, so the rule is not "these six, every day" -- Married... with
Children is free at the weekend and Murphy Brown and Roseanne are free on a
weekday. Sunday's 17:00 strip and Monday's prime both depend on that.

  Mon-Fri 17:00-20:00       Family Matters · Married... with Children
                            The Wonder Years · Full House
  Sat-Sun 17:00-20:00       Family Matters · Full House · Murphy Brown
                            · Roseanne
  08:00-10:00, FALL/WINTER  Saved by the Bell · Perfect Strangers · Coach
  Tuesday 20:00-23:00       Roseanne · Murphy Brown · The Golden Girls
  Thursday 20:00-23:00      Cheers · Night Court
  23:00-24:00               In Living Color

**Lucy TV is out of scope, settled by the operator 2026-09-08.** It runs
I Love Lucy and nothing else, as background television, and it **claims
nothing**. Every other channel schedules as though it did not exist. This
replaces the old framing, which treated it as a claimant and therefore needed
C5 to license a "three-channel exemption" for I Love Lucy -- an exemption that
existed only because a non-claimant had been counted as one.

What is left is an ordinary hours rule, not an exception. I Love Lucy is on
this channel and on Nick at Nite, and the only constraint that binds is Nick's,
above: out of 21:00-24:00, which prime and late respect. It signs the channel
on at 06:00 on both CBS days, and 06:00 is nowhere near Nick.

**All three Lucille Ball series are here as of 2026-09-08**, where the old
policy reserved two of them for a channel that was never going to air them:

* **I Love Lucy** (180 eps, 26.3m) -- the sign-on, both CBS days. This is the
  multi-camera studio-audience channel and this is the show that invented the
  form.
* **The Lucy Show** (156 eps, 25.6m) -- CBS 1962, so it joins the CBS bench on
  Monday and Saturday like any other half-hour on the roster.
* **The Lucy-Desi Comedy Hour** (13 eps, **50.7m**) -- the only hour-long show
  on the channel. Too short to strip (G6) and the wrong shape for a half-hour
  slot (G2), so it takes Saturday's two-hour noon exactly: two episodes, one
  day a week, a 45-day cycle.

Thursday is the one to notice. Totally 80s runs Cheers and Night Court as *its*
Must See Thursday; Good Times runs the 1990s Must See Thursday on the same
night. Same night's identity, two eras, no shared title.
"""

from scripts.logic.structures import RandomCollection, OrderedCollection, Block, Program
from scripts.library.queries import show_by_title
from . import branding

# ==============================================================================
# 1. THE ROSTER, BY NETWORK
# ==============================================================================
#
# Documentation first and content second: these are what each network-day draws
# from, and having them written down is what makes the hours rules above
# checkable by eye. Nothing schedules them, which is why they are underscored:
# collision_report's `library_collections()` treats every public uppercase list
# in the library as a schedulable collection, and a roster read that way makes
# every pair of shows on one network report as SAME COLLECTION.

_CBS_ROSTER = [
    "i_love_lucy_tv", "lucy_show_tv", "lucy_desi_tv",
    "andy_griffith_tv", "dick_van_dyke_tv", "gilligans_island_tv",
    "smothers_brothers_tv", "mary_tyler_moore_tv", "mash_tv", "bob_newhart_tv",
    "good_times_tv", "murphy_brown_tv", "northern_exposure_tv", "nanny_tv",
]

_NBC_ROSTER = [
    "jeannie_tv", "sanford_and_son_tv", "cheers_tv", "night_court_tv",
    "golden_girls_tv", "saved_by_the_bell_tv", "seinfeld_tv", "fresh_prince_tv",
    "wings_tv", "mad_about_you_tv", "frasier_tv", "newsradio_tv", "3rd_rock_tv",
    "just_shoot_me_tv", "will_and_grace_tv",
]

_ABC_ROSTER = [
    "bewitched_tv", "addams_family_tv", "soap_tv", "mork_mindy_tv", "taxi_tv",
    "perfect_strangers_tv", "full_house_tv", "roseanne_tv", "wonder_years_tv",
    "coach_tv", "family_matters_tv", "dinosaurs_tv", "home_improvement_tv",
    "mr_cooper_tv", "sister_sister_tv", "drew_carey_tv", "sabrina_tv",
    "spin_city_tv",
]

# FOX proper is three shows. Sunday is "FOX and the fourth networks" so that the
# day has five: Moesha was UPN and Sister, Sister spent its back half on The WB,
# which is the same upstart-network story the day is about.
_FOURTH_NETWORK_ROSTER = [
    "married_children_tv", "in_living_color_tv", "martin_tv", "moesha_tv",
    "sister_sister_tv",
]

# The channel fallback. Every title here is clear of Nick at Nite and Totally
# 80s at *every* hour of the day, which is the only safe property for content
# that fires on a stall and cannot know what time it is. Lucy TV used to be in
# that sentence and is not a claimant (see the docstring), so it no longer
# constrains anything here.
CHANNEL_FALLBACK = RandomCollection([
    "seinfeld_tv", "frasier_tv", "wings_tv", "mad_about_you_tv", "newsradio_tv",
    "3rd_rock_tv", "just_shoot_me_tv", "will_and_grace_tv", "nanny_tv",
    "drew_carey_tv", "home_improvement_tv", "spin_city_tv", "sabrina_tv",
    "mr_cooper_tv", "sister_sister_tv", "northern_exposure_tv",
])


# ==============================================================================
# 2. MONDAY -- CBS, the vault day
# ==============================================================================

MON_AFTER_HOURS = OrderedCollection(["nanny_tv", "murphy_brown_tv"])
MON_OVERNIGHT = RandomCollection([
    "i_love_lucy_tv", "lucy_show_tv", "gilligans_island_tv", "andy_griffith_tv",
    "dick_van_dyke_tv",
])
# The channel signs on with the show that invented it. 06:00 is nowhere near
# Nick at Nite's 21:00-24:00, so this is an hours rule and not an exception --
# see the docstring.
MON_EARLY = OrderedCollection(["i_love_lucy_tv", "dick_van_dyke_tv", "andy_griffith_tv"])

MON_MORNING = {
    "FALL":   OrderedCollection(["nanny_tv", "murphy_brown_tv"]),
    "WINTER": OrderedCollection(["northern_exposure_tv", "bob_newhart_tv"]),
    "SPRING": OrderedCollection(["gilligans_island_tv", "nanny_tv"]),
    "SUMMER": OrderedCollection(["good_times_tv", "gilligans_island_tv"]),
}
MON_MIDDAY = {
    "FALL":   OrderedCollection(["good_times_tv", "bob_newhart_tv"]),
    "WINTER": OrderedCollection(["bob_newhart_tv", "mary_tyler_moore_tv"]),
    # The Lucy Show rather than I Love Lucy, deliberately: the two Ball series
    # are never in the same arm, so the channel reads as having a Lucy on
    # somewhere rather than as running Lucy twice (G4, inside one day).
    "SPRING": OrderedCollection(["lucy_show_tv", "murphy_brown_tv"]),
    "SUMMER": OrderedCollection(["gilligans_island_tv", "good_times_tv"]),
}
MON_AFTERNOON = {
    "FALL":   RandomCollection(["andy_griffith_tv", "good_times_tv", "nanny_tv"]),
    "WINTER": RandomCollection(["andy_griffith_tv", "bob_newhart_tv", "northern_exposure_tv"]),
    "SPRING": RandomCollection(["gilligans_island_tv", "dick_van_dyke_tv", "nanny_tv"]),
    "SUMMER": RandomCollection(["gilligans_island_tv", "good_times_tv", "nanny_tv"]),
}

MON_EVENING = OrderedCollection(["mary_tyler_moore_tv", "bob_newhart_tv"])

# CBS Monday, 1993 -- the night Murphy Brown actually held down.
MON_PRIME = Block(
    name="CBS Monday",
    items=OrderedCollection([
        "murphy_brown_tv",
        "northern_exposure_tv",
        "nanny_tv",
    ]),
    use_epg_group=False,
)


# ==============================================================================
# 3. TUESDAY -- NBC
# ==============================================================================

TUE_AFTER_HOURS = OrderedCollection(["just_shoot_me_tv", "newsradio_tv"])
TUE_OVERNIGHT = OrderedCollection(["jeannie_tv", "sanford_and_son_tv"])
TUE_EARLY = OrderedCollection(["wings_tv", "mad_about_you_tv"])

# Saved by the Bell is Totally 80s' 08:00-10:00 in fall and winter, so it takes
# the summer arm of this book and the midday strip the rest of the year.
TUE_MORNING = {
    "FALL":   OrderedCollection(["3rd_rock_tv", "just_shoot_me_tv"]),
    "WINTER": OrderedCollection(["frasier_tv", "wings_tv"]),
    "SPRING": OrderedCollection(["jeannie_tv", "mad_about_you_tv"]),
    "SUMMER": OrderedCollection(["saved_by_the_bell_tv", "fresh_prince_tv"]),
}
TUE_MIDDAY = {
    "FALL":   OrderedCollection(["fresh_prince_tv", "saved_by_the_bell_tv"]),
    "WINTER": OrderedCollection(["golden_girls_tv", "night_court_tv"]),
    "SPRING": OrderedCollection(["jeannie_tv", "wings_tv"]),
    "SUMMER": OrderedCollection(["fresh_prince_tv", "saved_by_the_bell_tv"]),
}
TUE_AFTERNOON = {
    "FALL":   RandomCollection(["saved_by_the_bell_tv", "fresh_prince_tv", "mad_about_you_tv"]),
    "WINTER": RandomCollection(["night_court_tv", "golden_girls_tv", "wings_tv"]),
    "SPRING": RandomCollection(["jeannie_tv", "fresh_prince_tv", "newsradio_tv"]),
    "SUMMER": RandomCollection(["saved_by_the_bell_tv", "fresh_prince_tv", "jeannie_tv"]),
}

TUE_EVENING = OrderedCollection(["seinfeld_tv", "frasier_tv"])

# The literal NBC Tuesday lineup of 1997, all four of them on disk:
# Mad About You, NewsRadio, Frasier, Just Shoot Me!
TUE_PRIME = Block(
    name="NBC Tuesday",
    items=OrderedCollection([
        "mad_about_you_tv",
        "newsradio_tv",
        "frasier_tv",
        "just_shoot_me_tv",
    ]),
    use_epg_group=False,
)


# ==============================================================================
# 4. WEDNESDAY -- ABC
# ==============================================================================

WED_AFTER_HOURS = OrderedCollection(["drew_carey_tv", "spin_city_tv"])
WED_OVERNIGHT = OrderedCollection(["bewitched_tv", "addams_family_tv"])
WED_EARLY = OrderedCollection(["sabrina_tv", "sister_sister_tv"])

WED_MORNING = {
    "FALL":   OrderedCollection(["spin_city_tv", "drew_carey_tv"]),
    "WINTER": OrderedCollection(["home_improvement_tv", "drew_carey_tv"]),
    "SPRING": OrderedCollection(["bewitched_tv", "sabrina_tv"]),
    "SUMMER": OrderedCollection(["perfect_strangers_tv", "sister_sister_tv"]),
}
WED_MIDDAY = {
    "FALL":   OrderedCollection(["mr_cooper_tv", "dinosaurs_tv"]),
    "WINTER": OrderedCollection(["dinosaurs_tv", "coach_tv"]),
    "SPRING": OrderedCollection(["bewitched_tv", "mork_mindy_tv"]),
    "SUMMER": OrderedCollection(["sister_sister_tv", "sabrina_tv"]),
}
# Full House and Family Matters are Totally 80s' 17:00-20:00 strip and nothing
# else; the afternoon is open and it is where TGIF's own shows belong anyway.
WED_AFTERNOON = {
    "FALL":   RandomCollection(["full_house_tv", "family_matters_tv", "sister_sister_tv"]),
    "WINTER": RandomCollection(["full_house_tv", "perfect_strangers_tv", "dinosaurs_tv"]),
    "SPRING": RandomCollection(["bewitched_tv", "sabrina_tv", "mork_mindy_tv"]),
    "SUMMER": RandomCollection(["sister_sister_tv", "full_house_tv", "wonder_years_tv"]),
}

WED_EVENING = RandomCollection(["home_improvement_tv", "coach_tv", "mr_cooper_tv"])

WED_PRIME = Block(
    name="ABC Wednesday",
    items=OrderedCollection([
        "drew_carey_tv",
        "roseanne_tv",
        "coach_tv",
    ]),
    use_epg_group=False,
)

WED_LATE = OrderedCollection(["soap_tv", "mork_mindy_tv"])


# ==============================================================================
# 5. THURSDAY -- NBC, Must See TV
# ==============================================================================

THU_AFTER_HOURS = OrderedCollection(["frasier_tv", "mad_about_you_tv"])
THU_OVERNIGHT = OrderedCollection(["jeannie_tv", "night_court_tv"])
THU_EARLY = OrderedCollection(["newsradio_tv", "wings_tv"])

THU_MORNING = {
    "FALL":   OrderedCollection(["will_and_grace_tv", "frasier_tv"]),
    "WINTER": OrderedCollection(["golden_girls_tv", "frasier_tv"]),
    "SPRING": OrderedCollection(["jeannie_tv", "3rd_rock_tv"]),
    "SUMMER": OrderedCollection(["saved_by_the_bell_tv", "will_and_grace_tv"]),
}
THU_MIDDAY = {
    "FALL":   OrderedCollection(["golden_girls_tv", "night_court_tv"]),
    "WINTER": OrderedCollection(["cheers_tv", "golden_girls_tv"]),
    "SPRING": OrderedCollection(["wings_tv", "mad_about_you_tv"]),
    "SUMMER": OrderedCollection(["fresh_prince_tv", "saved_by_the_bell_tv"]),
}
THU_AFTERNOON = {
    "FALL":   RandomCollection(["saved_by_the_bell_tv", "fresh_prince_tv", "will_and_grace_tv"]),
    "WINTER": RandomCollection(["golden_girls_tv", "night_court_tv", "frasier_tv"]),
    "SPRING": RandomCollection(["jeannie_tv", "wings_tv", "3rd_rock_tv"]),
    "SUMMER": RandomCollection(["saved_by_the_bell_tv", "fresh_prince_tv", "seinfeld_tv"]),
}

THU_EVENING = OrderedCollection(["seinfeld_tv", "wings_tv"])

# NBC Thursday, 1995. Friends is not on disk; the other three of the four are,
# and Will & Grace inherits the 21:00 half-hour it went on to hold.
# Cheers and Night Court are deliberately absent: they are Totally 80s' Thursday
# prime, and this is the same night one era later.
THU_PRIME = Block(
    name="Must See TV",
    items=OrderedCollection([
        "seinfeld_tv",
        "mad_about_you_tv",
        "frasier_tv",
        "will_and_grace_tv",
    ]),
    use_epg_group=False,
)

# ==============================================================================
# 6. FRIDAY -- ABC, TGIF
# ==============================================================================
#
# The one night on the channel that has a *season*. Everything else here is a
# strip -- the same shape every week, with the daytime books reshuffling four
# times a year. TGIF instead runs a broadcast year: shows premiere, run week by
# week, break for the holidays, come back, and go into repeats.
#
# **The epoch.** Schedule year 2026 is broadcast season 1989-90 -- TGIF's first
# night was 22 September 1989 -- so every show's seasons are placed at their
# real broadcast year plus `TGIF_EPOCH`. That is the whole trick, and it needs
# no machinery: `states.resolve_season_date` turns a `(year, season)` pair into
# an absolute calendar date, so `premiere_year` is a hard anchor and relative
# alignment between shows is arithmetic. Perfect Strangers S7 is on the air the
# year Mr. Cooper premieres because that is when it happened.
#
#     sched  broadcast   20:00           20:30           21:00         21:30
#     2026   1989-90     Full House S3   Fam Matters S1  Perf Str S5   --
#     2027   1990-91     Full House S4   Fam Matters S2  Perf Str S6   Dinosaurs S1
#     2028   1991-92     Full House S5   Fam Matters S3  Perf Str S7   Dinosaurs S2
#     2029   1992-93     Full House S6   Fam Matters S4  Mr Cooper S1  Dinosaurs S3
#     2030   1993-94     Full House S7   Fam Matters S5  Mr Cooper S2  Sister Sis S1
#     2031   1994-95     Full House S8   Fam Matters S6  Mr Cooper S3  Sister Sis S2
#     2032   1995-96     --              Fam Matters S7  Mr Cooper S4  Sister Sis S3
#     2033   1996-97     Sabrina S1      Fam Matters S8  Mr Cooper S5  Sister Sis S4
#     2034   1997-98     Sabrina S2      Fam Matters S9  --            Sister Sis S5
#     2035   1998-99     Sabrina S3      --              --            Sister Sis S6
#     2036   1999-00     Sabrina S4      --              --            --
#
# **Four chairs, not four shows.** A chair is one `Program` whose season list
# walks *across* shows, which is how the real 21:00 half-hour worked: Mr. Cooper
# took the slot Perfect Strangers vacated, and Sister, Sister took Dinosaurs'.
# `annual_show()` cannot express that -- it numbers seasons from 1 and maps
# season `i` to `premiere_year + i`, so it can neither start a show mid-run nor
# hand a slot over -- so `_chair` below builds the same `Program` shape by hand.
# The query it writes per season is character-for-character what
# `factories._get_content_key` writes, so nothing about resolution changes.
#
# **Every chair carries a bed (C-rung: an off-season appointment must not
# stall).** `blocks._resolve_and_prepare_program_content` returns nothing for a
# Program whose season window is closed and whose `content` is None; the block
# loop then sees time unmoved and `playout.circuit_breaker` fires, spending the
# half-hour on `fallback_content` and logging a warning. So `content=TGIF_BENCH`
# on all four. It is deliberately the *same object* on each: `RandomCollection`
# clears its no-repeat state once per day, so four chairs drawing one bench
# cannot serve the same title twice in a night (G4).
#
# **Two seasons are held back from the chairs on purpose.** Perfect Strangers S8
# (6 episodes) and Dinosaurs S4 (14) were both burned off over the summer rather
# than aired in season, so they are the SUMMER_RERUNS arm below instead of the
# tail of a chair. That is both the faithful reading and the reason the chairs
# hand over cleanly -- without it Perfect Strangers and Mr. Cooper would both
# want 2029.
#
# **What does not air on the first pass.** Full House S1-S2 and Perfect
# Strangers S1-S4 sit at schedule years 2022-2025, which are in the past: 117
# episodes that `unaired_check` will flag and that will not air until the chair
# loops (chair A in 2037, chair C in 2034). That is expected, not a defect --
# the alternative is truncating the lists, which would strand them permanently.
#
# **Where this stops being true.** Each chair loops on its own span, so from
# 2037 they drift out of step with each other and the table above stops holding.
# Keeping it aligned forever needs an explicit cycle length on the appointment
# resolver (`_apply_schedule_looping`); see KNOWN_ISSUES.md. Ten years of
# correct history was judged worth more than the machinery to extend it.
#
# **Hours rules.** All seven titles are clear at 20:00-23:00. Nick at Nite holds
# none of them at any hour. Totally 80s holds Full House and Family Matters at
# 08:00-10:00 and 17:00-20:00 and Perfect Strangers at 08:00-10:00 -- every one
# of those claims ends at or before 20:00, which is where this block starts.

FRI_AFTER_HOURS = OrderedCollection(["spin_city_tv", "drew_carey_tv"])
FRI_OVERNIGHT = OrderedCollection(["bewitched_tv", "addams_family_tv"])
FRI_EARLY = OrderedCollection(["dinosaurs_tv", "mr_cooper_tv"])

FRI_MORNING = {
    "FALL":   OrderedCollection(["drew_carey_tv", "spin_city_tv"]),
    "WINTER": OrderedCollection(["home_improvement_tv", "spin_city_tv"]),
    "SPRING": OrderedCollection(["bewitched_tv", "dinosaurs_tv"]),
    "SUMMER": OrderedCollection(["sister_sister_tv", "perfect_strangers_tv"]),
}
FRI_MIDDAY = {
    "FALL":   OrderedCollection(["sister_sister_tv", "mr_cooper_tv"]),
    "WINTER": OrderedCollection(["mr_cooper_tv", "dinosaurs_tv"]),
    "SPRING": OrderedCollection(["sabrina_tv", "mork_mindy_tv"]),
    "SUMMER": OrderedCollection(["sister_sister_tv", "full_house_tv"]),
}
FRI_AFTERNOON = {
    "FALL":   RandomCollection(["full_house_tv", "family_matters_tv", "mr_cooper_tv"]),
    "WINTER": RandomCollection(["perfect_strangers_tv", "coach_tv", "dinosaurs_tv"]),
    "SPRING": RandomCollection(["sabrina_tv", "bewitched_tv", "sister_sister_tv"]),
    "SUMMER": RandomCollection(["full_house_tv", "sister_sister_tv", "wonder_years_tv"]),
}

# Sabrina came out of `after_hours`, `early` and `evening` in the TGIF pass. It
# was in eleven places across the lineup and five of Friday's ten slots, one of
# them the 17:00-20:00 strip immediately before prime; it now holds the 20:00
# chair from 2033 and keeps Wednesday, which is its ABC day.
FRI_EVENING = RandomCollection(["drew_carey_tv", "home_improvement_tv", "spin_city_tv"])


# --- the TGIF broadcast year --------------------------------------------------

# Schedule year - broadcast year. 2026 == 1989-90, TGIF's first season.
TGIF_EPOCH = 37

_FRI_FALL = ("FALL", "FRIDAY")
_FRI_SPRING = ("SPRING", "FRIDAY")


# The three shows that arrived at midseason. Their first season -- and only
# their first -- opens at the SPRING ramp rather than the FALL one, which is
# where it really opened: Perfect Strangers March 1986, Dinosaurs April 1991,
# Sister, Sister April 1994. Their short first orders (6, 5 and 12 episodes)
# are the evidence; no other show in the seven has a first season under 22.
_SPRING_PREMIERES = {"perfect_strangers", "dinosaurs", "sister_sister"}


def _seasons(title, stem, entries):
    """Season triples for one show's run inside a chair.

    `entries` are `(season_number, episode_count, broadcast_year)` -- the real
    year the season *opened*, so a spring premiere carries the year its
    broadcast season began (Dinosaurs S1 aired April 1991 and is 1990). Returns
    the `(key, count, (year, season_spec))` triples the appointment resolver
    wants, plus the queries to pre-register.
    """
    triples, queries = [], {}
    for number, count, broadcast_year in entries:
        key = f"__tgif_{stem}_s{number}"
        queries[key] = f'{show_by_title(title)} AND season_number:{number}'
        spec = _FRI_SPRING if number == 1 and stem in _SPRING_PREMIERES else _FRI_FALL
        triples.append((key, count, (broadcast_year + TGIF_EPOCH, spec)))
    return triples, queries




def _chair(name, runs, restart, bed):
    """One half-hour of TGIF, across every show that ever held it."""
    triples, queries = [], {}
    for title, stem, entries in runs:
        t, q = _seasons(title, stem, entries)
        triples.extend(t)
        queries.update(q)
    return Program(
        name=name,
        content=bed,
        scheduling={
            "seasons": triples,
            "frequency": ["FRIDAY"],
            "episodes_per_slot": 1,
            "loop": True,
            "loop_restart_season": restart,
            "generated_queries": queries,
        },
    )


# **Each chair reruns its own shows, and nothing else.** The first version put
# one shared `TGIF_BENCH` under all four, which measured badly: 69% of nights
# aired the same title twice in prime, because the bench could hand back the
# show that had just aired as an appointment. The four chairs own *disjoint*
# sets, so a per-chair bed makes that structurally impossible -- and it gives
# each half-hour an identity that holds all year. Nine o'clock is Perfect
# Strangers or Mr. Cooper whether it is a new episode or a repeat, which is
# what a slot on a real station felt like. This is the per-show shelf pattern
# from `library/scifi.py`; the shared bench was a mistake.
TGIF_BED_2000 = OrderedCollection(["full_house_tv", "sabrina_tv"])
TGIF_BED_2030 = OrderedCollection(["family_matters_tv"])
TGIF_BED_2100 = OrderedCollection(["perfect_strangers_tv", "mr_cooper_tv"])
TGIF_BED_2130 = OrderedCollection(["dinosaurs_tv", "sister_sister_tv"])

# The 22:00 tail's pool, and the block's last-resort filler. Still all seven --
# the tail is explicitly the hour where the night stops being appointments and
# becomes the shelf.
TGIF_BENCH = RandomCollection([
    "full_house_tv", "family_matters_tv", "perfect_strangers_tv",
    "mr_cooper_tv", "sister_sister_tv", "dinosaurs_tv", "sabrina_tv",
])

TGIF_CHAIR_2000 = _chair("TGIF 8:00", [
    ("Full House", "full_house", [
        (1, 22, 1987), (2, 22, 1988), (3, 24, 1989), (4, 26, 1990),
        (5, 26, 1991), (6, 24, 1992), (7, 24, 1993), (8, 24, 1994),
    ]),
    # ABC years only. Sabrina's last three seasons were The WB, which is not
    # this night and not this channel's ABC day.
    ("Sabrina, the Teenage Witch", "sabrina", [
        (1, 24, 1996), (2, 26, 1997), (3, 25, 1998), (4, 22, 1999),
    ]),
], restart="FALL", bed=TGIF_BED_2000)

TGIF_CHAIR_2030 = _chair("TGIF 8:30", [
    ("Family Matters", "family_matters", [
        (1, 22, 1989), (2, 25, 1990), (3, 25, 1991), (4, 24, 1992),
        (5, 24, 1993), (6, 25, 1994), (7, 24, 1995), (8, 24, 1996),
        (9, 22, 1997),
    ]),
], restart="FALL", bed=TGIF_BED_2030)

# The handover chair. Mr. Cooper really did take the 9:00 half-hour Perfect
# Strangers vacated, and S8 -- burned off in the summer of 1993 -- is what makes
# the handover land clean instead of both shows wanting 2029.
TGIF_CHAIR_2100 = _chair("TGIF 9:00", [
    ("Perfect Strangers", "perfect_strangers", [
        (1, 6, 1985), (2, 22, 1986), (3, 23, 1987), (4, 22, 1988),
        (5, 24, 1989), (6, 24, 1990), (7, 24, 1991),
    ]),
    ("Hangin' with Mr. Cooper", "mr_cooper", [
        (1, 22, 1992), (2, 22, 1993), (3, 22, 1994), (4, 22, 1995),
        (5, 13, 1996),
    ]),
], restart="SPRING", bed=TGIF_BED_2100)

# The fourth-show chair -- the slot TGIF rotated hardest. Dinosaurs S4 is held
# back for the same reason as Perfect Strangers S8: it was burned off over the
# summer of 1994, and holding it back is what lets Sister, Sister open in 2030.
TGIF_CHAIR_2130 = _chair("TGIF 9:30", [
    ("Dinosaurs", "dinosaurs", [
        (1, 5, 1990), (2, 24, 1991), (3, 22, 1992),
    ]),
    ("Sister, Sister", "sister_sister", [
        (1, 12, 1993), (2, 19, 1994), (3, 22, 1995), (4, 22, 1996),
        (5, 22, 1997), (6, 22, 1998),
    ]),
], restart="SPRING", bed=TGIF_BED_2130)

TGIF_CHAIRS = [
    TGIF_CHAIR_2000, TGIF_CHAIR_2030, TGIF_CHAIR_2100, TGIF_CHAIR_2130,
]

# --- the 22:00 hour ------------------------------------------------------------
#
# **The tail is not TGIF, and that is the point.** TGIF was 20:00-22:00; ten
# o'clock on ABC was the grown-up hour. Making the tail the channel's other
# 90s ABC shows does three things at once: it gives 22:00 an identity of its
# own, it means the night has eight distinct titles instead of six, and it
# **structurally removes the duplicate problem** -- every one of the seven TGIF
# shows belongs to a chair, so any tail drawn from them repeats a chair. That
# measured at 69-71% of nights airing a title twice, and per-chair beds alone
# did not touch it, because the tail was the duplicator all along.
#
# Hours rules: Bewitched and The Addams Family are Nick at Nite's 21:00-24:00
# and are deliberately absent. Roseanne is Totally 80s' *Tuesday* prime and
# Wonder Years its weekday 17:00-20:00, so neither is free here. What is left
# is the four below, all clear at 22:00 on a Friday.
TGIF_TEN_OCLOCK = RandomCollection([
    "home_improvement_tv", "coach_tv", "drew_carey_tv", "spin_city_tv",
])

# The night that built the block, for the two nights that celebrate it.
TGIF_TAIL_PREMIERE = OrderedCollection(["full_house_tv", "family_matters_tv"])

# Dinosaurs is the odd one out tonally and the most event-shaped thing on the
# shelf, which is what a sweeps stunt wants.
TGIF_TAIL_STUNT = OrderedCollection(["dinosaurs_tv"])

TGIF_TAIL_HOLIDAY = RandomCollection([
    "christmas_80s_sitcoms_tv", "christmas_90s_sitcoms_tv",
])

# The two seasons held back from the chairs, aired when they really aired.
# Queried inline rather than through a registry key because they exist only
# here (G8: a content key carries its own playback order, and these want
# chronological).
TGIF_TAIL_BURNOFF = OrderedCollection([
    {"title": "Perfect Strangers",
     "query": f'{show_by_title("Perfect Strangers")} AND season_number:8',
     "order": "Chronological"},
    {"title": "Dinosaurs",
     "query": f'{show_by_title("Dinosaurs")} AND season_number:4',
     "order": "Chronological"},
])

# The bench, kept only as the block's last-resort filler.
TGIF_BENCH = RandomCollection([
    "full_house_tv", "family_matters_tv", "perfect_strangers_tv",
    "mr_cooper_tv", "sister_sister_tv", "dinosaurs_tv", "sabrina_tv",
])


def _tgif_night(name, tail):
    """One arm of the broadcast year: four chairs, then four tail half-hours.

    `tail` is a **list of four entries**, one per 22:00 half-hour, not one
    object repeated. Repeating it was worth 56% of nights airing a title twice:
    the summer arm is two burn-off seasons and the sweeps arm is one show, so
    four picks from either had to collide. Arms with less than four half-hours
    of signature content top up from `TGIF_TEN_OCLOCK`.

    **Every arm carries the chairs; only the tail changes.** The first draft of
    this went dark for HIATUS and SUMMER_RERUNS on the reading that the dead
    fortnight and the summer hold no appointment -- and that silently destroyed
    86 episodes between 2026 and 2036. `resolve_scheduled_content` is driven by
    the calendar, not by what aired: a season window that opens in September
    counts every Friday inside it whether the block asked for an episode or
    not, so two dark Fridays in December are two episodes the viewer never
    sees, every year, with nothing in the logs. The chairs stay in, the label
    layer dresses the 22:00 hour, and the two clocks stay uncoupled -- which is
    what this design claimed to be doing in the first place.

    `items` is a list rather than a collection so the block *exhausts*:
    `blocks._get_next_block_item` indexes a list by position and returns None
    past the end, where a collection keeps handing items back and wraps. That
    wrap is the defect KNOWN_ISSUES.md records against the old Must See
    Thursday, and it was live here -- six shuffled titles in a three-hour slot
    had room for a seventh pick.

    **Eight items, and why the grid does not land on the half hour.** Episodes
    run 21.3-24.0 minutes (measured off disk, median 22.6). A half-hour grid
    needs the balance in advertising -- about seven minutes a show, which is
    what a 1990 network half-hour really carried. The operator's call was one
    or two spots between shows and no more: *enjoyment over accuracy*. That is
    a deliberate trade, and the consequence is arithmetic -- eight shows at
    ~23 minutes plus 35-second breaks fills 20:00 to roughly 23:05, so the
    night runs on its own clock rather than the station's. What it buys is
    the slot being **97% programming** instead of 77%, with no dead air and
    no arbitrary repeat: the 13% pad and the 9% overflow both go to shows.
    """
    return Block(
        name=name,
        items=[*TGIF_CHAIRS, *tail],
        bumpers=branding.BRANDING_TGIF.bumpers,
        use_epg_group=False,
        # Two spots between shows. `Block.commercials` is declared but never
        # read -- `_handle_program_commercials` passes `program.commercials` --
        # so the pool comes from the channel's `commercial_content`.
        enable_commercials=True,
        commercial_duration=35,
        fill_strategy="fill",
        filler=TGIF_BENCH,
    )


# Resolution takes the first key the day carries (pipeline._unwrap_nested_
# structure), so the additive labels have to be written above the season they
# sit inside: a Friday in November carries FALL_SEASON, SWEEPS and SWEEPS_NOV
# together. The five season labels are a strict partition, so nothing can fall
# through; `default` is belt-and-braces.
FRI_PRIME = {
    # Premiere and finale night lead with the two shows that built the block.
    # They are chairs A and B, so those two nights a year do air a title twice
    # -- deliberately: "the night TGIF built" wants more of it, not less.
    "PREMIERE_WEEK": _tgif_night("TGIF Premiere Night",
                                 [TGIF_TAIL_PREMIERE, TGIF_TAIL_PREMIERE,
                                  TGIF_TEN_OCLOCK, TGIF_TEN_OCLOCK]),
    "SWEEPS_NOV":    _tgif_night("TGIF -- November Sweeps",
                                 [TGIF_TAIL_STUNT, TGIF_TEN_OCLOCK,
                                  TGIF_TEN_OCLOCK, TGIF_TEN_OCLOCK]),
    "SWEEPS_FEB":    _tgif_night("TGIF -- February Sweeps",
                                 [TGIF_TAIL_STUNT, TGIF_TEN_OCLOCK,
                                  TGIF_TEN_OCLOCK, TGIF_TEN_OCLOCK]),
    "SWEEPS_MAY":    _tgif_night("TGIF -- May Sweeps",
                                 [TGIF_TAIL_STUNT, TGIF_TEN_OCLOCK,
                                  TGIF_TEN_OCLOCK, TGIF_TEN_OCLOCK]),
    "FINALE_WEEK":   _tgif_night("TGIF Finale Night",
                                 [TGIF_TAIL_PREMIERE, TGIF_TAIL_PREMIERE,
                                  TGIF_TEN_OCLOCK, TGIF_TEN_OCLOCK]),
    # The holiday keys are episode *pools*, not single shows, so four draws are
    # four different Christmas episodes.
    "HIATUS":        _tgif_night("TGIF Holiday Break",
                                 [TGIF_TAIL_HOLIDAY] * 4),
    "FALL_SEASON":   _tgif_night("TGIF", [TGIF_TEN_OCLOCK] * 4),
    "MIDSEASON":     _tgif_night("TGIF", [TGIF_TEN_OCLOCK] * 4),
    "SUMMER_RERUNS": _tgif_night("TGIF Summer",
                                 [TGIF_TAIL_BURNOFF, TGIF_TAIL_BURNOFF,
                                  TGIF_TEN_OCLOCK, TGIF_TEN_OCLOCK]),
    "default":       _tgif_night("TGIF", [TGIF_TEN_OCLOCK] * 4),
}

FRI_LATE = OrderedCollection(["soap_tv", "taxi_tv"])
# ==============================================================================
# 7. SATURDAY -- CBS, The Greatest Night
# ==============================================================================

SAT_AFTER_HOURS = OrderedCollection(["nanny_tv", "northern_exposure_tv"])
SAT_OVERNIGHT = OrderedCollection([
    "gilligans_island_tv", "lucy_show_tv", "andy_griffith_tv",
])
SAT_EARLY = OrderedCollection(["i_love_lucy_tv", "dick_van_dyke_tv", "gilligans_island_tv"])

SAT_MORNING = {
    "FALL":   OrderedCollection(["nanny_tv", "northern_exposure_tv"]),
    "WINTER": OrderedCollection(["northern_exposure_tv", "bob_newhart_tv"]),
    "SPRING": OrderedCollection(["dick_van_dyke_tv", "gilligans_island_tv"]),
    "SUMMER": OrderedCollection(["gilligans_island_tv", "good_times_tv"]),
}
SAT_MIDDAY = {
    "FALL":   OrderedCollection(["good_times_tv", "murphy_brown_tv"]),
    "WINTER": OrderedCollection(["bob_newhart_tv", "mary_tyler_moore_tv"]),
    "SPRING": OrderedCollection(["i_love_lucy_tv", "andy_griffith_tv"]),
    "SUMMER": OrderedCollection(["good_times_tv", "nanny_tv"]),
}
SAT_AFTERNOON = {
    "FALL":   RandomCollection(["andy_griffith_tv", "lucy_show_tv", "good_times_tv"]),
    "WINTER": RandomCollection(["andy_griffith_tv", "northern_exposure_tv", "bob_newhart_tv"]),
    "SPRING": RandomCollection(["dick_van_dyke_tv", "gilligans_island_tv", "nanny_tv"]),
    "SUMMER": RandomCollection(["gilligans_island_tv", "lucy_show_tv", "nanny_tv"]),
}

SAT_EVENING = OrderedCollection(["dick_van_dyke_tv", "good_times_tv"])

# CBS Saturday, 1973 -- All in the Family, M*A*S*H, Mary Tyler Moore, Bob
# Newhart, Carol Burnett. Three of the five are on disk and they are the three
# in the middle. Reachable at 20:00-23:00 only because Nick at Nite runs the 70s
# shift at 00:00-02:00 and not at 21:00; see the hours rules in the docstring.
# The two missing names are the top of reference/acquisitions.md.
SAT_PRIME = Block(
    name="The Greatest Night",
    items=OrderedCollection([
        "mash_tv",
        "mary_tyler_moore_tv",
        "bob_newhart_tv",
    ]),
    use_epg_group=False,
)


# ==============================================================================
# 8. SUNDAY -- FOX and the fourth networks
# ==============================================================================
#
# Five shows and no seasonal book: four arms would be four names for the same
# five titles. It is a deliberately small, loud day -- which is what FOX Sunday
# was -- and the shelf it wants is in reference/acquisitions.md.

SUN_AFTER_HOURS = OrderedCollection(["martin_tv", "in_living_color_tv"])
SUN_OVERNIGHT = OrderedCollection(["married_children_tv", "martin_tv"])
SUN_EARLY = OrderedCollection(["sister_sister_tv", "moesha_tv"])
SUN_MORNING = OrderedCollection(["moesha_tv", "sister_sister_tv"])
SUN_MIDDAY = OrderedCollection(["moesha_tv", "sister_sister_tv"])
SUN_AFTERNOON = RandomCollection([
    "sister_sister_tv", "moesha_tv", "married_children_tv",
])
# Married... with Children is Totally 80s' *weekday* 17:00-20:00 strip; its
# weekend evening is a different four, so Sunday at seven is clear.
SUN_EVENING = OrderedCollection(["married_children_tv", "martin_tv"])

SUN_PRIME = Block(
    name="Fox Sunday",
    items=OrderedCollection([
        "married_children_tv",
        "in_living_color_tv",
        "martin_tv",
    ]),
    use_epg_group=False,
)

# In Living Color is Totally 80s' 23:00-24:00 Sketch Hour, so the late shift
# here takes Martin and the sketch show waits until after midnight.
SUN_LATE = "martin_tv"


# ==============================================================================
# 9. THE NOON HOUR
# ==============================================================================
#
# One show per day, no collection (G3): the hour reads as "M*A*S*H is on at
# noon" rather than "sitcoms are on". Each day's anchor comes from that day's
# network, so the strip turns over with the wheel.

# Saturday is the one hour-long entry, and the slot is why. `noon` is two hours;
# every other day fills it with four half-hours, and Saturday fills it with two
# 50-minute Comedy Hours -- the same 100 minutes, so the shape of the slot does
# not change. It is the only place on the channel an hour-long fits without
# stranding a half-hour strip's tail (G2), and at two episodes a week those 13
# run a 45-day cycle, which is what G6 asks of a pool too short to strip.
NOON_HOUR = {
    "MONDAY":    "mash_tv",
    "TUESDAY":   "wings_tv",
    "WEDNESDAY": "taxi_tv",
    "THURSDAY":  "cheers_tv",
    "FRIDAY":    "perfect_strangers_tv",
    "SATURDAY":  "lucy_desi_tv",
    "SUNDAY":    "martin_tv",
}


# ==============================================================================
# 10. THE LATE SHIFT (23:00-24:00)
# ==============================================================================
#
# One hour, and the only slot on the channel that has to dodge both Nick at
# Nite's 21:00-24:00 block and Totally 80s' Sketch Hour. The Smothers Brothers
# is a 60-minute variety hour, which is exactly one late shift, and Nick runs it
# at 00:00-02:00 -- so it can hold two nights a week and still cycle 67 episodes
# over eight months.

LATE_SHIFT = {
    "MONDAY":    "smothers_brothers_tv",
    "TUESDAY":   "night_court_tv",
    "WEDNESDAY": WED_LATE,
    "THURSDAY":  "3rd_rock_tv",
    "FRIDAY":    FRI_LATE,
    "SATURDAY":  "smothers_brothers_tv",
    "SUNDAY":    SUN_LATE,
}


# ==============================================================================
# 11. HOLIDAY EVENTS
# ==============================================================================
#
# The channel's own, rather than `common.HALLOWEEN_TV_EVENT` and
# `common.CHRISTMAS_TV_EVENT`: both of those lead with `*_animated_tv`, and a
# laugh-track channel that spends Halloween on cartoons is running another
# channel's holiday. These are episode-level keys -- the Halloween and Christmas
# episodes of the sitcoms already on the air here.

HALLOWEEN_EVENT = RandomCollection([
    "halloween_sitcoms_tv",
])

THANKSGIVING_EVENT = RandomCollection([
    "thanksgiving_sitcoms_tv",
    "thanksgiving_90s_tv",
])

CHRISTMAS_EVENT = RandomCollection([
    "christmas_80s_sitcoms_tv",
    "christmas_90s_sitcoms_tv",
])
