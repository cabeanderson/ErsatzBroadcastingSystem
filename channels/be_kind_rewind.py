"""
Be Kind Rewind - the video store, 1980 to now

The lineup's general movie channel, and the last of the film channels to be
built. Cabes Classic Cinema takes everything before 1980; this takes everything
after, which is 1,530 live-action films and a 122-day cycle. Between them the
two cover the whole library and **no title can appear on both**.

The organizing axis is the **week**, because the pool is too big and too
cross-genre for anything else. Nightmare Theatre organizes by the clock and
High Noon around a television spine; a viewer should be able to tell what day
it is here from what is on:

    Mon  Comedy Night          Tue  The Director's Chair
    Wed  Recent                Thu  Star of the Month
    Fri  NEW RELEASES          Sat  Blockbuster Night
    Sun  The Sunday Feature

and the day around it:

    00-02  Cult Corner         the back wall of the store
    02-06  The Overnight Bin   the whole shelf, plus the 1980s
    06-09  The Morning Matinee family and PG
    09-12  The Back Catalogue  comedy and romance
    12-15  Decade Afternoon    a decade a month
    15-18  The Afternoon Double genre x decade
    18-22  PRIME               see above
    22-24  The Late Show       thrillers, the harder shelf

**Prime starts at 18:00, and that is a measured decision rather than a taste
one.** Simulating all eleven channels over a fortnight and bucketing film
minutes by hour of day showed 18:00-20:00 is the emptiest film hour on the
lineup -- Nightmare Theatre, High Noon and Other Worlds are all running
television, and only Totally 80s has any film there at all. From 20:00 four
channels start features at once. Opening prime two hours early means this
channel's viewer is already inside a film when the rest of the lineup begins.

## How it stays clear of its neighbours

Nothing here is exclusive; the rule is that the same title must not air on two
channels in the same hour. Each border is kept a different way:

- **Totally 80s** owns the 1980s as a theme and runs film 10:00-23:00. This
  channel's 1980s shelf is scheduled 22:00-06:00 -- Cult Corner and The
  Overnight Bin -- and the decade is deliberately absent from the afternoon
  rotations. An hours rule, not an eviction.
- **Nightmare Theatre** draws every era of horror and runs seventeen hours of
  film a day, so there is no hour to hide in. `NO_HORROR` is on the wide keys.
- **High Noon** draws every era of western and runs film 20:00-24:00, this
  channel's prime. `NO_WESTERN` is on the wide keys. Both exclusions cost 225
  films out of 1,530.
- **Other Worlds** and **Mystery Theatre** keep science fiction and modern
  crime outright, but both run mostly television in these hours -- 9 and 17
  film-minutes a day respectively at 20:00-22:00. Shared, and left shared.
  `modern_thriller_movie` carries the full set of exclusions so the one key
  that could quietly re-open all three borders does not.
"""

from etv_client.models import ControlWaitUntil
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.logic import triggers
from scripts.logic.models import Marathon
from scripts.library import modern_movies
from scripts.logic.factories import monthly_rotation
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================
#
# Eight slots. None shorter than two hours, because the mean running time here
# is 115 minutes and a shorter daypart cuts a feature in half -- the reason the
# "movies" preset's four six-hour blocks were not simply reused, and the reason
# the default two-hour map is wrong for any film channel. No slot wraps
# midnight.

REWIND_TIMESLOTS = {
    "night":     (0, 2),     # Cult Corner
    "overnight": (2, 6),     # The Overnight Bin
    "early":     (6, 9),     # The Morning Matinee
    "morning":   (9, 12),    # The Back Catalogue
    "afternoon": (12, 15),   # Decade Afternoon
    "matinee":   (15, 18),   # The Afternoon Double
    "prime":     (18, 22),   # the appointment
    "late":      (22, 24),   # The Late Show
}

# ==============================================================================
# 2. MARATHONS
# ==============================================================================

MARATHONS = [
    # Whenever the 13th is a Friday the new-release wall gives way. Composed
    # from the weekday label and `day_of_month` the same way Nightmare
    # Theatre's is -- there is no FRIDAY_THE_13TH label in `core/registry.py`.
    Marathon(
        name="Friday the 13th Rentals",
        trigger=triggers.all_of(
            triggers.has_label("FRIDAY"),
            triggers.day_of_month(13),
        ),
        collection=modern_movies.CULT_CORNER,
        hours=(22, 24),
        priority=2
    ),
]

# ==============================================================================
# 3. BLOCK DEFINITIONS
# ==============================================================================

# Tuesday and Thursday are the spotlights, rotated monthly. Eight directors and
# four stars means the director cycles twice a year and the star three times.
#
# `monthly_rotation` returns a month-keyed dict, which the resolution pipeline
# already understands -- the same mechanic Nick and Disney use, and the reason
# this needs no new resolution logic.
DIRECTORS_CHAIR = monthly_rotation(modern_movies.DIRECTORS_CHAIR)
STAR_OF_THE_MONTH = monthly_rotation(modern_movies.STAR_OF_THE_MONTH)

# The decade rotations. A month per decade, so the afternoon has a character
# that lasts long enough to be noticed rather than shuffling every day.
DECADE_AFTERNOON = monthly_rotation(modern_movies.DECADE_AFTERNOON)
AFTERNOON_DOUBLE = monthly_rotation(modern_movies.AFTERNOON_DOUBLE)

# Prime, gated by the weekday label rather than by an appointment's own
# `frequency` -- `frequency` paces an episode index, it does not stop content
# airing on other days, which is the trap every channel on this lineup has hit.
PRIME_BLOCK = {
    "MONDAY":    modern_movies.COMEDY_NIGHT,
    "TUESDAY":   DIRECTORS_CHAIR,
    "WEDNESDAY": modern_movies.RECENT_MIDWEEK,
    "THURSDAY":  STAR_OF_THE_MONTH,
    "FRIDAY":    modern_movies.NEW_RELEASES,
    "SATURDAY":  modern_movies.SATURDAY_PRIME,
    "SUNDAY":    modern_movies.SUNDAY_FEATURE,
    "default":   modern_movies.THE_OVERNIGHT_BIN,
}

# ==============================================================================
# 4. HOLIDAY SCHEDULES
# ==============================================================================

HALLOWEEN_SCHEDULE = {
    "prime": modern_movies.HALLOWEEN_EVENT,
    "late":  modern_movies.HALLOWEEN_EVENT,
}

CHRISTMAS_SCHEDULE = {
    "afternoon": modern_movies.CHRISTMAS_EVENT,
    "matinee":   modern_movies.CHRISTMAS_EVENT,
    # The one night the channel drops its week and runs a fixed bill.
    "prime":     modern_movies.CHRISTMAS_EVE_FEATURE,
    "late":      modern_movies.CHRISTMAS_EVENT,
}

# ==============================================================================
# 5. SCHEDULE DEFINITIONS
# ==============================================================================

# One daily grid. The week's identity lives in PRIME_BLOCK rather than in
# separate WEEKDAY / SATURDAY / SUNDAY maps, because only prime changes by day
# -- with two exceptions, both on the weekend morning.
DAILY = {
    "night":     modern_movies.CULT_CORNER,
    "overnight": modern_movies.THE_OVERNIGHT_BIN,
    "early":     modern_movies.MORNING_MATINEE,
    "morning":   modern_movies.THE_BACK_CATALOGUE,
    "afternoon": DECADE_AFTERNOON,
    "matinee":   AFTERNOON_DOUBLE,
    "prime":     PRIME_BLOCK,
    "late":      modern_movies.THE_LATE_SHOW,
}

SCHEDULES = {
    "WEEKDAY": DAILY,
    # Saturday morning is the matinee stretched over both morning slots -- the
    # video store's Saturday, and the one concession to the family shelf
    # outside breakfast.
    "SATURDAY": {**DAILY, "morning": modern_movies.MORNING_MATINEE},
    "SUNDAY": DAILY,
}

# ==============================================================================
# 6. ERSATZTV INTEGRATION
# ==============================================================================

def define_content(api, context, build_id):
    pass

def reset_playout(api, context, build_id):
    return api.wait_until(build_id, ControlWaitUntil(
        when="00:00",
        tomorrow=False,
        rewind_on_reset=True
    ))

def build_playout(api, context, build_id):
    config = ScheduleConfig(
        schedules=SCHEDULES,
        marathons=MARATHONS,
        holiday_schedules={
            "HALLOWEEN": HALLOWEEN_SCHEDULE,
            "CHRISTMAS": CHRISTMAS_SCHEDULE,
        },
        block_profiles={},
        timeslot_preset=REWIND_TIMESLOTS,
        logger=ChannelLogger(prefix="[REWIND]"),
        # The wide modern shelf. 1,307 films, so a stall anywhere on the grid
        # drops into something the channel would plausibly have aired anyway.
        fallback_content="modern_cinema_movie",
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True
    )
    return run_daily_schedule(api, context, build_id, config)
