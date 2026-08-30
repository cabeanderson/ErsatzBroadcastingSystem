#!/usr/bin/env python3
"""
Scenario-based tests for ErsatzTV Scheduling Framework.
Covers Smoke Tests, Edge Cases, and Feature Toggles.
"""

import sys
import os
import io
import contextlib
import unittest
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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
from scripts.logic.structures import Program, Block, DailyOrderedCollection, RandomCollection
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


class TestMarathonWindow(unittest.TestCase):
    """A marathon must stay inside the hours its channel gave it."""

    def test_unbounded_marathon_stays_in_window(self):
        from scripts.channels import cartoon_network

        # 2026-04-30 is a Simpsons Marathon trigger date (16:00-22:00 window).
        ctx = MockContext(datetime(2026, 4, 30))
        api = MockAPI(ctx)
        with contextlib.redirect_stdout(io.StringIO()):
            cartoon_network.build_playout(api, ctx, "marathon-window")

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
        from scripts.channels import cartoon_network
        ctx = MockContext(day)
        api = MockAPI(ctx)
        with contextlib.redirect_stdout(io.StringIO()):
            cartoon_network.build_playout(api, ctx, "start-point")
        return api

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


if __name__ == "__main__":
    unittest.main()
