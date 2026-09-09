#!/usr/bin/env python3
"""
Scenario-based tests for ErsatzTV Scheduling Framework.
Covers Smoke Tests, Edge Cases, and Feature Toggles.
"""

import io
import contextlib
import unittest
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch

# Run as a module, not a loose script:
#     python3 -m scripts.testing.test_scenarios
# The package is importable from the project root, which is what makes
# `scripts.*` resolve. A sys.path.insert here used to paper over being
# run from anywhere, at the cost of the package being importable two
# different ways -- the same cleanup filler/ and nfo/ had on 2026-09-07.

# Install mocks
from scripts.testing import install_mocks
install_mocks()

from scripts.core import registry
from scripts.logic.resolution.pipeline import resolve_content, apply_injections
from scripts.logic.resolution.resolver import ContentResolver
from scripts.core.logger import ChannelLogger
from scripts.core import DayDirector
from scripts.logic.calendar.holidays import HolidayContext, get_holiday_target
from scripts.scheduling.config import ScheduleConfig
from scripts.logic.structures import Program, Block, DailyOrderedCollection, RandomCollection, OrderedCollection
from scripts.logic.models import Fallback
from scripts.logic.resolution.config_utils import resolve_feature
from scripts.logic.resolution.playback import hour_in_window, calculate_boundary_dt
from scripts.playout import play_with_fallback
from scripts.logic.calendar import assemble_day_schedule
from scripts.testing.simulator import MockAPI, MockContext
from etv_client.models import (
    PlayoutCount, PlayoutPadUntil, PlayoutPadUntilExact,
    ControlWaitUntil, ControlSkipToItem,
)

class TestScenarios(unittest.TestCase):

    def setUp(self):
        self.logger = ChannelLogger(verbose=False)
        self.mock_api = MagicMock()
        self.resolver = ContentResolver(self.mock_api, "test_build", {}, self.logger)
        self.mock_context = MagicMock()
        self.mock_context.current_time = datetime(2026, 1, 1, 12, 0, 0)
        self.boss = DayDirector(self.mock_context)
        self.holiday_ctx = HolidayContext(self.boss)

    # --- SMOKE TESTS ---

    def test_smoke_simple_channel_run(self):
        """Smoke: Simple channel runs without errors (resolution level)."""
        print("\n[Smoke] Simple Channel Resolution")
        schedule = {"prime": "test_content"}
        config = ScheduleConfig(schedules={"WEEKDAY": schedule})
        
        # Simulate assembly (returns (day_schedule, marathon_block, marathon_window))
        day_sched, _, _ = assemble_day_schedule(config, self.boss, self.holiday_ctx)

        # Check that content exists (keys are now tuples like (20, 23))
        self.assertIn("test_content", day_sched.values())
        print("✅ Simple schedule assembled")

    def test_smoke_holiday_activation(self):
        """Smoke: Holiday schedules activate."""
        print("\n[Smoke] Holiday Activation")
        # Mock Halloween
        self.holiday_ctx.envelope = {"halloween": 1.0}
        
        target = {
            "default": "regular_content",
            "halloween": "spooky_content"
        }
        
        res = get_holiday_target(self.holiday_ctx, target)
        self.assertEqual(res, "spooky_content")
        print("✅ Holiday target selected")

    # --- EDGE CASES ---

    def test_edge_midnight_crossing(self):
        """Edge: Midnight crossings (23:00 -> 01:00 slots)."""
        print("\n[Edge] Midnight Crossings")
        # Window: 22:00 to 02:00
        start, end = 22, 2
        
        self.assertTrue(hour_in_window(22, start, end), "22:00 should be in window")
        self.assertTrue(hour_in_window(23, start, end), "23:00 should be in window")
        self.assertTrue(hour_in_window(0, start, end), "00:00 should be in window")
        self.assertTrue(hour_in_window(1, start, end), "01:00 should be in window")
        self.assertFalse(hour_in_window(2, start, end), "02:00 should NOT be in window")
        self.assertFalse(hour_in_window(21, start, end), "21:00 should NOT be in window")
        
        # Boundary Calculation
        self.mock_context.current_time = datetime(2026, 1, 1, 23, 0, 0)
        boundary = calculate_boundary_dt(self.mock_context, start, end)
        expected = datetime(2026, 1, 2, 2, 0, 0)
        self.assertEqual(boundary, expected, "Boundary should be tomorrow at 2am")
        print("✅ Midnight logic verified")

    def test_edge_day_boundary_reset(self):
        """Edge: Day boundaries (new day resets DailyOrderedCollection)."""
        print("\n[Edge] Day Boundary Reset")
        collection = DailyOrderedCollection(["item1", "item2", "item3"])
        
        # Day 1
        self.mock_context.current_time = datetime(2026, 1, 1, 10, 0)
        self.assertEqual(collection.pick(self.boss), "item1")
        self.assertEqual(collection.pick(self.boss), "item2")
        
        # Day 2 (Should reset to item1)
        self.mock_context.current_time = datetime(2026, 1, 2, 10, 0)
        self.assertEqual(collection.pick(self.boss), "item1")
        print("✅ Daily collection reset verified")

    def test_edge_empty_collection(self):
        """Edge: Empty collections/blocks."""
        print("\n[Edge] Empty Collection")
        # RandomCollection with empty list
        col = RandomCollection([])
        
        # Should handle empty list gracefully or fail predictably
        try:
            col.pick(self.boss)
            failed = False
        except (IndexError, ValueError):
            failed = True
            
        # Test resolution of None
        res = resolve_content(None, self.boss, self.holiday_ctx, ScheduleConfig(schedules={}), self.resolver, self.logger)
        self.assertIsNone(res.resolved_content)
        print("✅ Empty/None resolution handled")

    def test_edge_multiple_holidays(self):
        """Edge: Multiple simultaneous holidays."""
        print("\n[Edge] Multiple Holidays Priority")
        # Both Halloween and Christmas active
        self.holiday_ctx.envelope = {"halloween": 1.0, "christmas": 1.0}
        
        target = {
            "default": "regular",
            "halloween": "spooky",
            "christmas": "festive"
        }
        
        # Christmas should win based on get_holiday_target implementation
        res = get_holiday_target(self.holiday_ctx, target)
        self.assertEqual(res, "festive")
        print("✅ Priority respected (Christmas > Halloween)")

    def test_edge_fallback_logic(self):
        """Edge: Missing content fallback."""
        print("\n[Edge] Fallback Logic")
        
        # Mock context
        ctx_stalled = MagicMock()
        ctx_stalled.current_time = datetime(2026, 1, 1, 12, 0)
        
        ctx_success = MagicMock()
        ctx_success.current_time = datetime(2026, 1, 1, 12, 30)
        
        with patch('scripts.playout.play_item') as mock_play:
            # Side effect: First call returns stalled, second returns success
            mock_play.side_effect = [ctx_stalled, ctx_success]
            
            fallback = Fallback(primary="primary", secondary="secondary")
            
            # Run
            res_ctx = play_with_fallback(self.mock_api, "build", fallback, self.logger, context=ctx_stalled)
            
            # Verify
            self.assertEqual(mock_play.call_count, 2)
            self.assertEqual(res_ctx.current_time, datetime(2026, 1, 1, 12, 30))
            print("✅ Fallback triggered successfully")

    # --- FEATURE TOGGLES ---

    def test_toggle_hierarchy(self):
        """Feature: Hierarchy (Channel > Block > Program)."""
        print("\n[Feature] Toggle Hierarchy")
        
        # 1. Channel enables, Program disables
        res = resolve_feature(False, None, True)
        self.assertFalse(res)
        
        # 2. Channel enables, Block disables, Program None
        res = resolve_feature(None, False, True)
        self.assertFalse(res)
        
        # 3. Channel disables, Program enables
        res = resolve_feature(True, None, False)
        self.assertTrue(res)
        
        print("✅ Feature flag hierarchy verified")

    def test_toggle_appointment_injection(self):
        """Feature: Appointment TV auto-disables injections."""
        print("\n[Feature] Appointment TV Injection Protection")
        
        # Setup: Active Holiday
        self.mock_context.current_time = datetime(2026, 10, 31, 12, 0, 0)
        self.boss.roll = MagicMock(return_value=True) # Force injection roll
        
        # Setup: Content
        self.resolver.registry["show_ep1"] = "show_title:Test"
        
        # 1. Regular Program (Should inject)
        prog_regular = Program(name="Regular", content="show_ep1")
        config = ScheduleConfig(schedules={}, enable_holiday_injection=True)
        
        res_reg = apply_injections(
            "show_ep1",
            program=prog_regular,
            config=config,
            resolver=self.resolver,
            boss=self.boss,
            holiday_ctx=self.holiday_ctx,
            logger=self.logger,
            source="test"
        )
        self.assertIsNotNone(res_reg.wrapper, "Regular program should get injection")
        
        # 2. Appointment Program (Should NOT inject)
        prog_appt = Program(
            name="Appointment", 
            content="show_ep1",
            scheduling={"frequency": "weekly"} # Marks as appointment
        )
        
        res_appt = apply_injections(
            "show_ep1",
            program=prog_appt,
            config=config,
            resolver=self.resolver,
            boss=self.boss,
            holiday_ctx=self.holiday_ctx,
            logger=self.logger,
            source="test"
        )
        self.assertIsNone(res_appt.wrapper, "Appointment program should block injection")
        
        # 3. Appointment Program with Explicit Enable (Should inject)
        prog_appt_explicit = Program(
            name="Appointment Explicit", 
            content="show_ep1",
            scheduling={"frequency": "weekly"},
            enable_holiday_injection=True # Override
        )
        
        res_explicit = apply_injections(
            "show_ep1",
            program=prog_appt_explicit,
            config=config,
            resolver=self.resolver,
            boss=self.boss,
            holiday_ctx=self.holiday_ctx,
            logger=self.logger,
            source="test"
        )
        self.assertIsNotNone(res_explicit.wrapper, "Explicit enable should allow injection")

        print("✅ Appointment TV injection protection verified")


class TestApiContract(unittest.TestCase):
    """Guards the ErsatzTV API semantics documented in ERSATZTV_API.md.

    These assert against the mock, so they are only as good as the mock's
    fidelity to SchedulingEngine.cs -- that is the point. Each one previously
    passed vacuously because the mock did not model the behaviour at all.
    """

    def _api(self, start=datetime(2026, 4, 30, 12, 0), mode="continue"):
        ctx = MockContext(start)
        return MockAPI(ctx, mode=mode), ctx

    def test_add_count_appends_every_item(self):
        """add_count(N) appends N items -- it is not a single-item call."""
        api, ctx = self._api()
        api.content_durations["show"] = 30
        api.add_count("b", PlayoutCount(content="show", count=4))

        played = [e for e in api.schedule if e['type'] == 'content']
        self.assertEqual(len(played), 4, "add_count must append `count` items")
        self.assertEqual(ctx.current_time, datetime(2026, 4, 30, 14, 0),
                         "time must advance by the total duration of all items")
        print("✅ add_count honors count")

    def test_add_count_has_no_time_bound(self):
        """add_count applies no boundary; it will run past the build window.

        This is the behaviour that turned a 6-hour marathon slot into days of
        playout, so it must stay visible rather than be smoothed over.
        """
        api, ctx = self._api(start=datetime(2026, 4, 30, 22, 0))
        api.content_durations["show"] = 30
        api.add_count("b", PlayoutCount(content="show", count=200))

        self.assertGreater(ctx.current_time, ctx.finish_time,
                           "add_count is expected to overrun the build window")
        print("✅ add_count overruns the window (bounding is the caller's job)")

    def test_enumerator_persists_across_calls(self):
        """One cursor per content key, advancing across separate calls."""
        api, _ = self._api()
        api.content_counts["show"] = 10
        for _ in range(3):
            api.add_count("b", PlayoutCount(content="show", count=1))

        indices = [e['item_index'] for e in api.schedule if e['type'] == 'content']
        self.assertEqual(indices, [0, 1, 2],
                         "separate add_count calls must continue the sequence")
        print("✅ enumerator persists across calls")

    def test_skip_to_item_positions_cursor_once(self):
        """skip_to_item repositions; it does not pin the cursor."""
        api, _ = self._api()
        api.content_counts["show"] = 30
        api.skip_to_item("b", ControlSkipToItem(content="show", season=3, episode=5))
        api.add_count("b", PlayoutCount(content="show", count=3))

        indices = [e['item_index'] for e in api.schedule if e['type'] == 'content']
        self.assertEqual(indices, [4, 5, 6], "playback must continue from the skip point")
        print("✅ skip_to_item positions the cursor")

    def test_pad_until_is_a_silent_noop_when_target_passed(self):
        """The documented trap: past target + tomorrow=False schedules nothing."""
        api, ctx = self._api(start=datetime(2026, 4, 30, 23, 40))
        api.pad_until("b", PlayoutPadUntil(content="filler", when="00:00", tomorrow=False))

        self.assertEqual(ctx.current_time, datetime(2026, 4, 30, 23, 40),
                         "pad_until must not advance time when the target has passed")
        self.assertEqual([e for e in api.schedule if e['type'] == 'content'], [],
                         "pad_until must schedule no content in this case")
        print("✅ pad_until no-op semantics modelled")

    def test_wait_until_does_not_roll_to_tomorrow_on_its_own(self):
        """wait_until with tomorrow=False does not advance a passed target."""
        api, ctx = self._api(start=datetime(2026, 4, 30, 23, 40))
        api.wait_until("b", ControlWaitUntil(when="00:00", tomorrow=False))

        self.assertEqual(ctx.current_time, datetime(2026, 4, 30, 23, 40),
                         "wait_until must not silently roll forward a day")
        print("✅ wait_until no-op semantics modelled")

    def test_wait_until_rewinds_only_during_reset(self):
        """rewind_on_reset moves the clock backward, but only in reset mode."""
        api, ctx = self._api(start=datetime(2026, 4, 30, 6, 0), mode="reset")
        api.wait_until("b", ControlWaitUntil(when="00:00", tomorrow=False, rewind_on_reset=True))
        self.assertEqual(ctx.current_time, datetime(2026, 4, 30, 0, 0),
                         "reset builds may rewind to the target")

        api2, ctx2 = self._api(start=datetime(2026, 4, 30, 6, 0), mode="continue")
        api2.wait_until("b", ControlWaitUntil(when="00:00", tomorrow=False, rewind_on_reset=True))
        self.assertEqual(ctx2.current_time, datetime(2026, 4, 30, 6, 0),
                         "continue builds must not rewind")
        print("✅ wait_until rewind is reset-only")

    def test_exact_variants_cross_month_boundary(self):
        """The month-boundary case that broke the HH:MM + `tomorrow` pairing.

        Aug 31 23:40 -> Sep 1 00:00 computed `tomorrow` as `1 > 31` == False,
        so the old code asked to pad until a time already past and got silence.
        """
        api, ctx = self._api(start=datetime(2026, 8, 31, 23, 40))
        api.content_durations["filler"] = 5
        target = datetime(2026, 9, 1, 0, 0)
        api.pad_until_exact("b", PlayoutPadUntilExact(content="filler", when=target))

        self.assertEqual(ctx.current_time, target,
                         "pad_until_exact must fill across a month boundary")
        print("✅ exact variants cross month boundaries")


# A stand-in channel for the marathon tests.
#
# These used to run against `channels.cartoon_network`, which meant a framework
# test failed the moment a channel changed its programming -- and it did: the
# Simpsons marathon left Cartoon Network in the restructure, since The Simpsons
# is Fox and never aired there. What is under test here is the engine's
# handling of random start points and marathon windows, so the fixture carries
# the two marathons itself.
#
# `boss.roll` is a pure function of (date, key), so the trigger keys below fire
# on exactly the dates they always did.

def _marathon_fixture(day, build_id):
    """Run a minimal channel holding just the marathons under test."""
    from scripts.logic.models import Marathon
    from scripts.logic import triggers
    from scripts.scheduling import run_daily_schedule
    from scripts.library.animation import COWBOY_BEBOP_COMPLETE

    marathons = [
        Marathon(
            name="Simpsons Marathon",
            trigger=triggers.chance(0.01, "simpsons_takeover"),
            collection="simpsons_random_marathon",
            hours=(16, 22),
            priority=1,
        ),
        Marathon(
            name="Cowboy Bebop",
            trigger=triggers.chance(0.01, "bebop_marathon"),
            collection=COWBOY_BEBOP_COMPLETE,
            hours=(10, 24),
            priority=2,
        ),
    ]

    schedule = {slot: "animated_classic_tv" for slot in
                ("overnight", "early", "morning", "midday", "noon",
                 "afternoon", "evening", "prime", "night")}

    config = ScheduleConfig(
        schedules={"WEEKDAY": schedule},
        marathons=marathons,
        timeslot_preset="default",
        fallback_content="animated_classic_tv",
        logger=ChannelLogger(verbose=False),
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True,
        enable_thematic_injection=True,
    )

    ctx = MockContext(day)
    api = MockAPI(ctx)
    with contextlib.redirect_stdout(io.StringIO()):
        run_daily_schedule(api, ctx, build_id, config)
    return api


class TestMarathonWindow(unittest.TestCase):
    """A marathon must stay inside the hours its channel gave it."""

    def test_unbounded_marathon_stays_in_window(self):
        # 2026-04-30 is a Simpsons Marathon trigger date (16:00-22:00 window).
        api = _marathon_fixture(datetime(2026, 4, 30), "marathon-window")

        simpsons = [e for e in api.schedule
                    if e['type'] == 'content' and 'simpsons' in str(e['content']).lower()]
        self.assertTrue(simpsons, "expected the Simpsons marathon to trigger on 2026-04-30")

        first, last = simpsons[0]['time'], simpsons[-1]['time']
        self.assertEqual(first.date(), date(2026, 4, 30), "marathon must start on its own day")
        self.assertEqual(last.date(), date(2026, 4, 30),
                         f"marathon must not spill into later days (ran to {last})")
        self.assertLess(last, datetime(2026, 4, 30, 22, 0),
                        f"marathon must end by its 22:00 boundary (last item at {last})")
        print(f"✅ marathon bounded: {len(simpsons)} items, {first:%H:%M}-{last:%H:%M}")


class TestMarathonStartPoint(unittest.TestCase):
    """Marathon episode positioning: it must fire, be deterministic, and land."""

    @staticmethod
    def _build(day):
        return _marathon_fixture(day, "start-point")

    def _skips(self, api):
        out = []
        for e in api.schedule:
            if e['type'] != 'skip':
                continue
            body = e['content'].split(': ', 1)[1]
            key, _, se = body.rpartition(' S')
            out.append((key, se))
        return out

    def test_random_start_actually_fires(self):
        """start_mode='random' must produce a skip, not be silently ignored.

        The guard was `play_count > 1`, but play_count is None for the unbounded
        content that declares a random start -- so it never fired for any
        marathon in the library.
        """
        api = self._build(datetime(2026, 4, 30))  # Simpsons Marathon trigger date
        simpsons_skips = [s for s in self._skips(api) if 'simpsons' in s[0].lower()]
        self.assertTrue(simpsons_skips,
                        "a random-start marathon must issue skip_to_item")

        season = int(simpsons_skips[0][1].split('E')[0])
        self.assertIn(season, range(3, 10),
                      f"season {season} must fall in the declared start_season [3, 9]")
        print(f"✅ random start fires (S{season}E1)")

    def test_random_start_is_deterministic(self):
        """Same date -> same season. The old code used the global random module.

        Two DayDirectors built from the same date must agree; the framework's
        core promise is that a date reproduces its schedule.
        """
        seasons = [self._skips(self._build(datetime(2026, 4, 30)))[0][1]
                   for _ in range(3)]
        self.assertEqual(len(set(seasons)), 1,
                         f"random start must be deterministic, got {seasons}")

        # ...and different dates should not all collapse to one season.
        across = {self._skips(self._build(d))[0][1]
                  for d in (datetime(2026, 4, 30), datetime(2026, 5, 27), datetime(2026, 6, 19))}
        self.assertGreater(len(across), 1,
                           "different dates should not all pick the same season")
        print(f"✅ random start deterministic, varies by date: {sorted(across)}")

    def test_skip_targets_the_key_that_actually_plays(self):
        """skip_to_item must be issued after injections settle the final key.

        Issuing it earlier aimed it at the pre-injection key (skipping
        '..._eps_23_26' while playing '..._eps_23_26_auto_spring'), leaving the
        skip orphaned and the marathon starting from episode 1.
        """
        # 2026-04-17 is a Cowboy Bebop trigger date during the spring injection
        # window, which is what rewrites the key.
        api = self._build(datetime(2026, 4, 17))
        sched = api.schedule
        orphaned = []
        for i, e in enumerate(sched):
            if e['type'] != 'skip':
                continue
            key = e['content'].split(': ', 1)[1].rpartition(' S')[0]
            for later in sched[i + 1:]:
                if later['type'] == 'skip':
                    break
                if later['type'] == 'content' and later['content'] == key:
                    break
            else:
                orphaned.append(key)
                continue

        self.assertEqual(orphaned, [],
                         f"every skip must target the key that plays; orphaned: {orphaned}")
        print("✅ skips land on the post-injection key")


class TestSeasonSpecResolution(unittest.TestCase):
    """
    A season may be named on its own ("FALL") or paired with the weekday an
    appointment airs on (("FALL", "THURSDAY")).

    The pair form used to resolve to no date at all, which made
    `_build_season_windows` return an empty list and
    `_resolve_appointment_schedule` bail -- so the Program played its reruns
    forever and never premiered, silently. Six appointments across sitcoms and
    detective were dead this way. These tests pin both forms.
    """

    def test_year_and_bare_season_resolves(self):
        """The original (year, "SEASON") form still resolves to the peak start."""
        from scripts.core import states
        self.assertEqual(states.resolve_season_date((2026, "FALL")), date(2026, 9, 15))

    def test_year_and_season_weekday_pair_resolves(self):
        """(year, ("SEASON", "DAY")) resolves and lands on that weekday."""
        from scripts.core import states
        # FALL peaks 9/15, a Tuesday in 2026; the first Thursday after is 9/17.
        resolved = states.resolve_season_date((2026, ("FALL", "THURSDAY")))
        self.assertEqual(resolved, date(2026, 9, 17))
        self.assertEqual(resolved.strftime("%A").upper(), "THURSDAY")

    def test_weekday_alignment_does_not_move_an_already_matching_date(self):
        """A peak that already falls on the target weekday stays put."""
        from scripts.core import states
        # SPRING peaks 3/15, a Sunday in 2026.
        self.assertEqual(
            states.resolve_season_date((2026, ("SPRING", "SUNDAY"))),
            date(2026, 3, 15))

    def test_bare_season_and_pair_both_resolve_relative(self):
        """Bare "SEASON" and ("SEASON", "DAY") both work without a year."""
        from scripts.core import states
        today = date(2026, 8, 29)
        self.assertEqual(states.resolve_season_date("SUMMER", today), date(2026, 6, 15))
        # SUMMER peaks 6/15, a Monday in 2026; first Saturday after is 6/20.
        self.assertEqual(
            states.resolve_season_date(("SUMMER", "SATURDAY"), today), date(2026, 6, 20))

    def test_unknown_season_still_returns_none(self):
        """Garbage in stays None -- the fix must not make bad specs resolve."""
        from scripts.core import states
        self.assertIsNone(states.resolve_season_date((2026, "HARVEST")))
        self.assertIsNone(states.resolve_season_date((2026, ("HARVEST", "THURSDAY"))))

    def test_season_label_extracts_the_season_half(self):
        from scripts.core import states
        self.assertEqual(states.season_label(("FALL", "THURSDAY")), "FALL")
        self.assertEqual(states.season_label("FALL"), "FALL")
        self.assertIsNone(states.season_label(None))

    def test_appointment_with_pair_season_builds_windows(self):
        """The regression itself: a pair-season appointment has season windows."""
        from scripts.logic.factories import annual_show
        from scripts.logic.resolution.pipeline import _build_season_windows

        prog = annual_show(
            show_title="Test Show",
            episodes_per_season=[6, 8],
            premiere_year=2026,
            premiere_season=("FALL", "THURSDAY"),
            frequency=["THURSDAY"],
            reruns="rerun_key",
            loop=True,
        )
        windows = _build_season_windows(
            prog.scheduling["seasons"], 1, prog.scheduling["frequency"], date(2026, 8, 29))

        self.assertEqual(len(windows), 2, "both seasons must produce a window")
        self.assertEqual(windows[0][0], date(2026, 9, 17))
        # Season 2 premieres a year later, also on a Thursday.
        self.assertEqual(windows[1][0].strftime("%A").upper(), "THURSDAY")

    def test_pair_season_loop_restart_is_normalised(self):
        """loop_restart_season inherits premiere_season; it must not stay a tuple."""
        from scripts.logic.factories import annual_show
        prog = annual_show(
            show_title="Test Show", episodes_per_season=[6], premiere_year=2026,
            premiere_season=("FALL", "THURSDAY"), frequency=["THURSDAY"], loop=True)
        self.assertEqual(prog.scheduling["loop_restart_season"], "FALL",
                         "a tuple here silently selects the immediate-loop branch")

    def test_appointment_premieres_on_the_day_and_not_before(self):
        """End to end: episode 1 on premiere day, nothing the Thursday before."""
        from scripts.logic.factories import annual_show
        from scripts.logic.resolution.pipeline import resolve_scheduled_content

        prog = annual_show(
            show_title="Test Show", episodes_per_season=[6], premiere_year=2026,
            premiere_season=("FALL", "THURSDAY"), frequency=["THURSDAY"],
            reruns="rerun_key", loop=True)

        self.assertIsNone(resolve_scheduled_content(prog, date(2026, 9, 10)),
                          "must not air before the premiere")
        for week, expected in enumerate([1, 2, 3, 4, 5, 6]):
            day = date(2026, 9, 17) + timedelta(weeks=week)
            result = resolve_scheduled_content(prog, day)
            self.assertIsNotNone(result, f"no episode on {day}")
            self.assertEqual(result[2], expected, f"wrong episode on {day}")
        print("✅ pair-season appointments premiere and advance weekly")


class TestFallbackResolution(unittest.TestCase):
    """
    `fallback_content` reaches `circuit_breaker`, which hands it straight to
    `play_item`. `play_item` stringifies anything that is not a key, so an
    unresolved Block arrived at ErsatzTV as
    "Block(name='...', items=<...object at 0x7f...>)" -- matching nothing,
    carrying a memory address, and still logging "fallback succeeded".

    `engines/blocks.py` passed it raw while `engines/dispatcher.py` resolved
    first, so the same config behaved differently depending on which call site
    fired. Both now go through `resolve_fallback_key`.
    """

    def _session(self, fallback, stalled=True):
        from types import SimpleNamespace
        from scripts.library.sources import MASTER_SOURCES
        now = datetime(2026, 9, 1, 12, 0)
        ctx = MagicMock(); ctx.current_time = now
        boss = DayDirector(ctx)
        logger = ChannelLogger(verbose=False)
        cfg = ScheduleConfig(schedules={"WEEKDAY": {}}, fallback_content=fallback)
        session = SimpleNamespace(
            context=ctx, config=cfg, boss=boss,
            holiday_ctx=HolidayContext(boss), logger=logger,
            resolver=ContentResolver(MagicMock(), "b", MASTER_SOURCES, logger),
        )
        # last_time >= now means "stalled"; a past last_time means time moved.
        return session, (now if stalled else now - timedelta(minutes=30))

    def test_string_key_passes_through(self):
        from scripts.engines.dispatcher import resolve_fallback_key
        session, last = self._session("procedural_tv")
        self.assertEqual(resolve_fallback_key(session, last), "procedural_tv")

    def test_collection_resolves_to_a_key(self):
        from scripts.engines.dispatcher import resolve_fallback_key
        from scripts.library import movies
        session, last = self._session(movies.GOLDEN_AGE_CINEMA)
        key = resolve_fallback_key(session, last)
        self.assertIsInstance(key, str)
        self.assertIn(key, tuple(movies.GOLDEN_AGE_CINEMA.items))

    def test_block_fallback_is_rejected_at_construction(self):
        """The guard that fires first: a Block never becomes a config at all."""
        from scripts.library import disney
        with self.assertRaises(ValueError) as caught:
            ScheduleConfig(schedules={"WEEKDAY": {}},
                           fallback_content=disney.THE_DISNEY_AFTERNOON)
        self.assertIn("cannot be a Block", str(caught.exception))

    def test_block_never_leaks_through_as_a_key(self):
        """The actual regression: a Block must yield None, not a stringified Block.

        `ScheduleConfig` now refuses a Block outright, so this reaches the
        runtime guard the only way left -- assigning past the constructor. The
        defence is kept because the two guards fail differently: the
        constructor stops a channel being written wrong, this one stops a
        stringified Block reaching ErsatzTV if it ever gets set another way.
        """
        from scripts.engines.dispatcher import resolve_fallback_key
        from scripts.library import disney
        session, last = self._session("procedural_tv")
        session.config.fallback_content = disney.THE_DISNEY_AFTERNOON
        key = resolve_fallback_key(session, last)
        self.assertIsNone(key)

    def test_not_resolved_when_time_has_not_stalled(self):
        from scripts.engines.dispatcher import resolve_fallback_key
        session, last = self._session("procedural_tv", stalled=False)
        self.assertIsNone(resolve_fallback_key(session, last))

    def test_every_channel_fallback_is_usable(self):
        """
        Repo-wide invariant. A fallback that cannot resolve is invisible until
        the day something stalls, which is exactly the day it is needed.
        """
        import importlib, inspect, re as _re
        bad = []
        for name in ("british", "cartoon_network", "classic_movies", "detective",
                     "disney", "eighties", "nick", "scifi", "sitcoms"):
            mod = importlib.import_module(f"scripts.channels.{name}")
            src = inspect.getsource(mod.build_playout)
            m = _re.search(r"fallback_content=([^,\n]+)", src)
            if not m:
                continue
            value = eval(m.group(1).strip(), mod.__dict__)  # noqa: S307 - test fixture
            session, last = self._session(value)
            from scripts.engines.dispatcher import resolve_fallback_key
            if not isinstance(resolve_fallback_key(session, last), str):
                bad.append(f"{name} ({type(value).__name__})")
        self.assertEqual(bad, [], f"channels whose fallback cannot resolve: {bad}")
        print("✅ every channel fallback resolves to a content key")


class TestSimulatorDurationGuess(unittest.TestCase):
    """
    The mock guessed runtime by substring, so the *show* Home Movies -- key
    `auto_gen_home_movies_<hash>` -- was read as a two-hour film. That one item
    ate the rest of its block and the whole hour after it, which looked like a
    real scheduling failure in an otherwise-green simulation.
    """

    def _api(self):
        api = MockAPI(MockContext(datetime(2026, 9, 4, 12, 0)))
        api.registered_searches["auto_gen_home_movies_x"] = {
            "query": 'type:episode AND show_title:"Home Movies"', "order": "Shuffle"}
        api.registered_searches["disney_movie"] = {
            "query": "type:movie AND genre:animation", "order": "Shuffle"}
        return api

    def test_show_titled_movies_is_not_a_film(self):
        self.assertEqual(self._api()._guess_duration("auto_gen_home_movies_x"), 20)

    def test_registered_movie_query_still_two_hours(self):
        self.assertEqual(self._api()._guess_duration("disney_movie"), 120)

    def test_unregistered_movie_key_falls_back_to_the_name(self):
        self.assertEqual(self._api()._guess_duration("30s_golden_age_movie"), 120)

    def test_branding_stings_are_short(self):
        api = self._api()
        for key in ("adult_swim_intro", "adult_swim_outro", "toonami_bumpers"):
            self.assertEqual(api._guess_duration(key), 5, key)

    def test_matching_is_on_whole_words(self):
        api = self._api()
        self.assertEqual(api._guess_duration("auto_gen_star_trek_voyager_x"), 60)
        self.assertEqual(api._guess_duration("nicktoons_vault_tv"), 30)


class TestCallEfficiency(unittest.TestCase):
    """ErsatzTV kills a scripted build at 30s, so round trips are a budget."""

    def test_play_item_does_not_double_call(self):
        """add_count returns the context; following it with get_context is waste."""
        from scripts.playout import play_item
        ctx = MockContext(datetime(2026, 4, 30, 12, 0))
        api = MockAPI(ctx)
        logger = ChannelLogger(verbose=False)

        play_item(api, "b", "some_show", logger, count=1)
        self.assertEqual(api.call_count, 1,
                         "play_item should cost one round trip, not two")
        print("✅ play_item costs one round trip")


class TestSilentConfigFailures(unittest.TestCase):
    """
    Three shapes that used to resolve fine and then play nothing.

    Each was invisible for the same reason: the config was well-formed, the
    content key was real, and the only symptom was a slot that quietly
    produced no items. All three are now refused where they are written.
    """

    def test_block_rejects_a_bare_content_key(self):
        """`items="key"` played nothing and warned nothing. Japanorama, 19:00-23:00."""
        with self.assertRaises(ValueError) as caught:
            Block(name="Frieren Night", items="frieren_tv")
        message = str(caught.exception)
        self.assertIn("bare content", message)
        self.assertIn('OrderedCollection(["frieren_tv"])', message,
                      "the error must name the fix, not just the fault")

    def test_block_accepts_the_shapes_the_engine_can_walk(self):
        self.assertEqual(Block(name="a", items=["k"]).name, "a")
        self.assertEqual(Block(name="b", items=OrderedCollection(["k"])).name, "b")

    def test_fallback_rejects_a_wrapper_on_either_side(self):
        """A Collection here stringifies to an object repr and matches nothing."""
        for side in ("primary", "secondary"):
            kwargs = {"primary": "a", "secondary": "b", side: RandomCollection(["x"])}
            with self.assertRaises(ValueError, msg=side) as caught:
                Fallback(**kwargs)
            self.assertIn(side, str(caught.exception))

    def test_fallback_accepts_two_keys(self):
        self.assertEqual(Fallback(primary="a", secondary="b").secondary, "b")

    def test_every_block_in_the_lineup_is_iterable(self):
        """
        Repo-wide invariant, not just the one channel that was caught.

        A block whose items the engine cannot walk reports "0 items played"
        and falls through to the circuit breaker, so it never shows up as an
        error -- only as a slot that is somehow always fallback.
        """
        import importlib, pkgutil
        from scripts.engines.blocks import _block_items_are_iterable
        import scripts.channels, scripts.library

        bad = []
        for pkg in (scripts.channels, scripts.library):
            for mod_info in pkgutil.iter_modules(pkg.__path__):
                mod = importlib.import_module(f"{pkg.__name__}.{mod_info.name}")
                for name, value in vars(mod).items():
                    if isinstance(value, Block) and not _block_items_are_iterable(value):
                        bad.append(f"{mod.__name__}.{name} ({type(value.items).__name__})")
        self.assertEqual(bad, [], f"blocks that can never play: {bad}")
        print("✅ every Block in the lineup has iterable items")


class TestFrequencyGatesTheAiring(unittest.TestCase):
    """
    `frequency` used to pace an appointment without gating it.

    `_find_active_episode` returned the current episode for any date inside
    the season window, so a show declared `frequency=["FRIDAY"]` inside a
    block that ran seven nights aired the same episode all seven -- a
    premiere that premieres every night.
    """

    def _friday_show(self, **kw):
        from scripts.logic.factories import annual_show
        return annual_show(
            episodes_per_season=[10], show_title="Friday Thing",
            start_date=date(2026, 3, 6), frequency=["FRIDAY"],
            reruns="some_rerun_bed", **kw)

    def test_off_frequency_days_resolve_to_nothing(self):
        from scripts.logic.resolution.pipeline import resolve_scheduled_content
        show = self._friday_show()
        # 2026-03-06 is a Friday; walk the week after it.
        aired = {}
        for offset in range(7):
            day = date(2026, 3, 6) + timedelta(days=offset)
            aired[day.strftime("%A")] = resolve_scheduled_content(show, day)

        self.assertIsNotNone(aired["Friday"], "the show must air on its own day")
        for name, result in aired.items():
            if name != "Friday":
                self.assertIsNone(result, f"aired off-frequency on {name}")
        print("✅ an appointment airs only on the days it declares")

    def test_the_episode_does_not_advance_on_skipped_days(self):
        """Gating must not also break pacing: consecutive Fridays step by one."""
        from scripts.logic.resolution.pipeline import resolve_scheduled_content
        show = self._friday_show()
        episodes = [resolve_scheduled_content(show, date(2026, 3, 6) + timedelta(weeks=w))[2]
                    for w in range(4)]
        self.assertEqual(episodes, [1, 2, 3, 4], episodes)

    def test_looping_does_not_drop_a_day_the_show_really_airs(self):
        """
        The regression this fix nearly introduced.

        `_apply_schedule_looping` rewrites the date into the season window,
        and the rewritten date lands on an arbitrary weekday. Gating on *that*
        date instead of the real one dropped Rurouni Kenshin from Toonami's
        Thursday -- a day it plainly declares. Caught by diffing 14 days of
        every channel before and after, not by a unit test, which is why the
        diff is worth doing.
        """
        from scripts.logic.factories import annual_show
        from scripts.logic.resolution.pipeline import resolve_scheduled_content
        days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"]
        strip = annual_show(
            episodes_per_season=[27, 35, 33], show_title="Rurouni Kenshin",
            start_date=date(2026, 1, 29), frequency=days,
            reruns="toonami_vault_tv", loop=True, loop_restart_season=False)

        # Well past the end of the run, so looping is certainly active.
        probe = date(2027, 9, 6)
        for offset, name in enumerate(["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"]):
            self.assertIsNotNone(
                resolve_scheduled_content(strip, probe + timedelta(days=offset)),
                f"looped strip lost {name}, a day it declares")
        for offset, name in enumerate(["FRIDAY", "SATURDAY", "SUNDAY"], start=4):
            self.assertIsNone(
                resolve_scheduled_content(strip, probe + timedelta(days=offset)),
                f"looped strip aired on {name}, which it does not declare")
        print("✅ frequency gating survives a looped schedule")

    def test_a_contiguous_strip_does_not_go_dark_waiting_for_autumn(self):
        """
        `loop_restart_season` defaulted to the season half of `premiere_season`
        -- "FALL" -- even in Contiguous Mode, where the caller passed
        `start_date` and named no premiere season. A weekday strip finishing in
        June then resolved to nothing until mid-September.
        """
        from scripts.logic.factories import annual_show
        from scripts.logic.resolution.pipeline import resolve_scheduled_content
        weekdays = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        strip = annual_show(
            episodes_per_season=[20], show_title="Some Strip",
            start_date=date(2026, 3, 2), frequency=weekdays, loop=True)

        self.assertIs(strip.scheduling["loop_restart_season"], False,
                      "a contiguous strip has no premiere season to restart in")
        # Every weekday of a summer week, long after the 20 episodes ran out.
        for offset in range(5):
            day = date(2026, 7, 20) + timedelta(days=offset)
            self.assertIsNotNone(resolve_scheduled_content(strip, day),
                                 f"strip went dark on {day}")
        print("✅ a contiguous strip loops instead of waiting for autumn")


class TestLogCaptureAcrossDays(unittest.TestCase):
    """
    The logger bound `sys.stdout` once, so a multi-day scan captured day one.

    This is the bug that reported "0 errors over 365 days" from a single day
    of log -- a clean result produced by seeing nothing.
    """

    def test_each_redirect_captures_its_own_day(self):
        captured = []
        for day in range(3):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                # Day one constructs the logger while the redirect is active,
                # which is precisely what used to bind the stream.
                ChannelLogger("[POND]", verbose=False).info(f"day {day}")
            captured.append(buf.getvalue())

        for day, text in enumerate(captured):
            self.assertIn(f"day {day}", text,
                          f"day {day} wrote into an earlier day's buffer")
        print("✅ log capture follows redirect_stdout across days")


class TestAnnualLoopAnchoring(unittest.TestCase):
    """
    A looping annual show must reopen on episode 1, on its own weekday, in
    the same part of the calendar, every year.

    It used to do none of those things after year one. `_apply_schedule_looping`
    took a modulo of the raw day count from the run's start to the next season
    peak; 15 March to 15 March is 363 days, so each re-run landed on a
    different weekday, the frequency gate dropped its first slot, and the run
    slid four days earlier a year. 21 of 35 appointments across six channels
    opened on episode 2 or 3 -- including Midnight Mass, whose seven episodes
    are timed to land beside Halloween.
    """

    def _runs(self, program, first, last):
        """Group a program's airings into runs, one per premiere."""
        from scripts.logic.resolution.pipeline import resolve_scheduled_content
        out, prev = [], None
        d = first
        while d < last:
            hit = resolve_scheduled_content(program, d)
            if hit:
                if prev is None or (d - prev).days > 60:
                    out.append([])
                out[-1].append((d, hit[2]))
                prev = d
            d += timedelta(days=1)
        return out

    def test_every_rerun_opens_on_episode_one(self):
        from scripts.library import horror
        runs = self._runs(horror.MIDNIGHT_MASS, date(2026, 1, 1), date(2032, 1, 1))
        self.assertGreater(len(runs), 4, "expected one run a year")
        self.assertEqual([r[0][1] for r in runs], [1] * len(runs),
                         "a re-run opened on something other than episode 1")

    def test_every_rerun_opens_on_the_same_weekday(self):
        from scripts.library import horror
        runs = self._runs(horror.MIDNIGHT_MASS, date(2026, 1, 1), date(2032, 1, 1))
        weekdays = {r[0][0].strftime("%A") for r in runs}
        self.assertEqual(weekdays, {"Saturday"},
                         f"premiere wandered across weekdays: {weekdays}")

    def test_the_run_does_not_slide_through_the_calendar(self):
        """Every premiere stays within a week of the season peak it anchors to."""
        from scripts.library import horror
        runs = self._runs(horror.MIDNIGHT_MASS, date(2026, 1, 1), date(2032, 1, 1))
        for start, _ in (r[0] for r in runs):
            offset = (start - date(start.year, 9, 15)).days
            self.assertTrue(0 <= offset < 7,
                            f"{start} is {offset} days from the FALL peak, not within the week")

    def test_a_multi_season_show_still_premieres_every_year(self):
        """Hannibal runs s1/s2/s3 over three autumns, then starts again."""
        from scripts.library import horror
        runs = self._runs(horror.HANNIBAL, date(2026, 1, 1), date(2032, 1, 1))
        self.assertGreaterEqual(len(runs), 5, "expected a premiere every year")
        self.assertEqual([r[0][1] for r in runs], [1] * len(runs))

    def test_a_contiguous_spring_season_runs_complete_every_year(self):
        """Sharpe: 16 films, in order, opening on Sharpe's Rifles each spring."""
        from scripts.library import british
        runs = self._runs(british.SHARPE, date(2027, 1, 1), date(2032, 1, 1))
        self.assertEqual(len(runs), 5, "expected one season a year")
        for run in runs:
            self.assertEqual(len(run), 16, "a season ran short of the full sixteen")
            self.assertEqual(run[0][1], 1, "a season opened on something other than Rifles")
            self.assertTrue(all(d.strftime("%A") == "Thursday" for d, _ in run),
                            "Sharpe aired off its own night")
        print("✅ annual loops re-anchor on the calendar and open on episode 1")



class TestMultiyearRotation(unittest.TestCase):
    """
    A rotation longer than twelve items must actually air all of them.

    `monthly_rotation` returns one key per month, so a thirteenth item was
    accepted and then never indexed -- and nothing reported it, because a
    rotation that quietly runs twelve of its thirty-six entries looks exactly
    like a rotation of twelve. Be Kind Rewind's Director's Chair was capped
    this way: eight directors, each returning twice a year.

    The fix is a year dimension in the label set. These tests pin both halves
    -- that the labels distinguish years, and that the factory spreads a long
    list across them without dropping or repeating an entry.
    """

    def _aired(self, rotation, first_year, years):
        """What the rotation resolves to, month by month, for `years` years."""
        from scripts.core.states import derive_labels
        out = []
        for year in range(first_year, first_year + years):
            for month in range(1, 13):
                labels = derive_labels(datetime(year, month, 15, 20))
                target = rotation
                while isinstance(target, dict):
                    key = next((k for k in target if k in labels), None)
                    self.assertIsNotNone(
                        key, f"{year}-{month:02d} matched no key in {sorted(target)}")
                    target = target[key]
                out.append(target)
        return out

    def test_labels_distinguish_one_year_from_the_next(self):
        """The defect underneath: without this, every rotation is annual."""
        from scripts.core.states import derive_labels
        same_day = [derive_labels(datetime(y, 3, 15, 20)) for y in (2027, 2028, 2029)]
        for a, b in zip(same_day, same_day[1:]):
            self.assertTrue(a ^ b, "two different years carried identical labels")

    def test_a_thirty_six_item_rotation_airs_all_thirty_six(self):
        from scripts.logic.factories import multiyear_rotation
        items = [f"item{i:02d}" for i in range(36)]
        aired = self._aired(multiyear_rotation(items), 2027, 3)
        self.assertEqual(len(set(aired)), 36, "the rotation dropped entries")
        self.assertEqual(len(aired), len(set(aired)), "an entry aired twice in one cycle")

    def test_the_cycle_repeats_on_schedule_and_not_before(self):
        from scripts.logic.factories import multiyear_rotation
        rotation = multiyear_rotation([f"item{i:02d}" for i in range(36)])
        aired = self._aired(rotation, 2027, 6)
        self.assertEqual(aired[:36], aired[36:], "year four did not repeat year one")

    def test_start_year_anchors_the_front_of_the_list(self):
        from scripts.logic.factories import multiyear_rotation
        items = [f"item{i:02d}" for i in range(36)]
        aired = self._aired(multiyear_rotation(items, start_year=2027), 2027, 1)
        self.assertEqual(aired[0], "item00", "the anchored year did not open the list")

    def test_a_short_list_still_behaves_like_a_monthly_rotation(self):
        from scripts.logic.factories import monthly_rotation, multiyear_rotation
        items = ["a", "b", "c"]
        self.assertEqual(multiyear_rotation(items), monthly_rotation(items))

    def test_a_rotation_too_long_to_label_is_refused_not_truncated(self):
        """The whole point: silent truncation is what this replaces."""
        from scripts.logic.factories import multiyear_rotation
        with self.assertRaises(ValueError):
            multiyear_rotation([f"item{i}" for i in range(61)])

    def test_be_kind_rewind_spotlights_run_three_years_deep(self):
        from scripts.channels import be_kind_rewind
        for name in ("DIRECTORS_CHAIR", "STAR_OF_THE_MONTH"):
            aired = self._aired(getattr(be_kind_rewind, name), 2027, 3)
            self.assertEqual(len(set(map(id, aired))), 36,
                             f"{name} does not run 36 distinct spotlights")
        print("✅ multiyear rotations air every entry and repeat only on cycle")



class TestUnairedConfigDetection(unittest.TestCase):
    """
    The checker that finds config naming content the channel cannot play.

    `unaired_check` sweeps the real lineup, which takes about a minute and is
    too slow to live in this suite. These pin its two judgement calls on
    synthetic input instead, so the tool cannot rot into always saying PASS:

      * a branch nothing under it ever aired is DEAD -- the Disney Star Wars
        reruns block, unreachable because its parent routed every weekend day
        elsewhere and Mon-Fri always carries WEEKDAY;
      * a branch that aired some of its items is THIN, not DEAD -- a random
        collection not getting round to everything, which is what made
        Michael Keaton's spotlight month report as a false positive.
    """

    def test_a_branch_that_never_airs_is_reported_dead(self):
        from scripts.testing.unaired_check import classify
        config = {"a": {"LIVE[x]"}, "b": {"DEAD[y]"}, "c": {"DEAD[y]"}}
        dead, thin = classify(config, played={"a"})
        self.assertEqual(set(dead), {"DEAD[y]"})
        self.assertFalse(thin)

    def test_a_partly_aired_branch_is_thin_not_dead(self):
        from scripts.testing.unaired_check import classify
        config = {"a": {"ROTATION[x]"}, "b": {"ROTATION[x]"}}
        dead, thin = classify(config, played={"a"})
        self.assertFalse(dead, "a random collection that missed one item is not dead")
        self.assertEqual(set(thin), {"ROTATION[x]"})

    def test_an_item_in_two_branches_counts_for_both(self):
        """The false positive this cost: shared films emptied the second branch."""
        from scripts.testing.unaired_check import classify
        config = {"shared": {"BURTON[jan]", "KEATON[dec]"}}
        dead, thin = classify(config, played={"shared"})
        self.assertFalse(dead)
        self.assertFalse(thin)

    def test_a_cycle_longer_than_the_window_is_not_called_dead(self):
        from scripts.testing.unaired_check import longest_cycle
        self.assertEqual(longest_cycle({"SPOT[YEAR_OF_3_1][MARCH]"}), 3)
        self.assertEqual(longest_cycle({"SPOT[MARCH]"}), 1)

    def test_the_real_lineup_declares_nothing_it_cannot_reach(self):
        """A cheap slice of the full sweep -- structure only, one channel."""
        from scripts.testing.unaired_check import declared
        from scripts.channels import disney
        paths = {p for group in declared(disney).values() for p in group}
        self.assertTrue(paths, "walked the config and found no content at all")
        print("✅ unaired-config detection distinguishes dead branches from thin ones")


class TestRotationCeilingIsEnforced(unittest.TestCase):
    """
    `monthly_rotation` truncated silently, and that is the whole defect.

    A year has twelve months, so a thirteenth item could never be indexed and
    never aired -- and the factory returned a perfectly good dict, so nothing
    upstream could tell. It refuses now, and names the replacement.
    """

    def test_more_than_twelve_items_is_refused(self):
        from scripts.logic.factories import monthly_rotation
        with self.assertRaises(ValueError) as caught:
            monthly_rotation([f"item{i}" for i in range(13)])
        self.assertIn("multiyear_rotation", str(caught.exception),
                      "the error should name the factory that handles this")

    def test_exactly_twelve_is_still_fine(self):
        from scripts.logic.factories import monthly_rotation
        self.assertEqual(len(set(monthly_rotation([f"i{i}" for i in range(12)]).values())), 12)
        print("✅ monthly_rotation refuses a rotation it cannot air")



class TestDocAuditReadsBothImportForms(unittest.TestCase):
    """
    The audit matched only single-line imports and reported PASS over the rest.

    Eighteen parenthesised blocks in IMPORTS.md were never executed, and the
    tool had said "docs match the code" the whole time -- a green result that
    meant "not looked at". Widening it surfaced 27 problems, two of them whole
    sections describing an API that never shipped.

    These assert it fails on known-bad input, which is the only thing that
    makes a passing run mean anything.
    """

    def test_a_multiline_import_is_read(self):
        from scripts.testing.doc_audit import _import_lines
        doc = "from scripts.logic.factories import (\n"
        doc += "    annual_show,          # one season a year\n"
        doc += "    multiyear_rotation    # a month per item\n"
        doc += ")\n"
        found = dict(_import_lines(doc))
        self.assertIn("scripts.logic.factories", found)
        symbols = {s.strip() for s in found["scripts.logic.factories"].split(",")}
        self.assertEqual(symbols, {"annual_show", "multiyear_rotation"})

    def test_comments_are_stripped_per_line_not_after_joining(self):
        """Stripping after the join discarded every symbol past the first."""
        from scripts.testing.doc_audit import _import_lines
        doc = "from scripts.logic.models import (\n    Marathon,  # a\n    Fallback  # b\n)\n"
        symbols = dict(_import_lines(doc))["scripts.logic.models"]
        self.assertIn("Marathon", symbols)
        self.assertIn("Fallback", symbols)

    def test_the_single_line_form_still_works(self):
        from scripts.testing.doc_audit import _import_lines
        found = dict(_import_lines("from scripts.logic.triggers import chance, any_of\n"))
        self.assertIn("scripts.logic.triggers", found)

    def test_the_real_docs_pass(self):
        from scripts.testing.doc_audit import audit
        self.assertEqual(audit(), [], "documented imports no longer resolve")
        print("✅ doc audit reads parenthesised imports, and the docs resolve")



if __name__ == "__main__":
    unittest.main()
