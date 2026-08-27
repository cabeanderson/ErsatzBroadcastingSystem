# ErsatzTV Scripted Schedules — API Contract

Reference for the ErsatzTV scripted-schedule API this framework is built on,
derived from primary sources (below) rather than from the local mock. Written
2026-08-27.

`etv_client` ships inside the ErsatzTV container and is not installable locally,
so `scripts/testing/simulator.py` acts as our de facto spec. **The mock is not
authoritative and is known to diverge** — see "Mock divergences". When the two
disagree, this document follows the C# implementation.

## Sources

| What | Where |
|---|---|
| OpenAPI spec (authoritative for shapes) | [`ErsatzTV/wwwroot/openapi/scripted-schedule.json`](https://github.com/ErsatzTV/legacy/blob/main/ErsatzTV/wwwroot/openapi/scripted-schedule.json) |
| Engine implementation (authoritative for semantics) | [`ErsatzTV.Core/Scheduling/Engine/SchedulingEngine.cs`](https://github.com/ErsatzTV/legacy/blob/main/ErsatzTV.Core/Scheduling/Engine/SchedulingEngine.cs) |
| Build host / timeout / days-to-build | [`ErsatzTV.Core/Scheduling/ScriptedScheduling/ScriptedPlayoutBuilder.cs`](https://github.com/ErsatzTV/legacy/blob/main/ErsatzTV.Core/Scheduling/ScriptedScheduling/ScriptedPlayoutBuilder.cs) |
| Official entrypoint | [`scripts/scripted-schedules/entrypoint.py`](https://github.com/ErsatzTV/legacy/blob/main/scripts/scripted-schedules/entrypoint.py) |
| Docs | <https://ersatztv.org/docs/scheduling/scripted/> |

Note: active development lives in `ErsatzTV/legacy` on `main`. Spec version
`scripted-schedule 1.0.0`, OpenAPI 3.1.1.

## How a build runs

ErsatzTV executes the script as a subprocess:

```
<script> <host> <build_id> <mode> [custom args...]
```

`mode` is `reset` or `continue`. The entrypoint imports the module and calls
three hooks in order — `define_content(api, context, build_id)`,
`reset_playout(...)` (only when mode is `reset`), then
`build_playout(...)`. Our channel modules implement all three.

Three host-side facts that constrain everything:

- **Build window defaults to 2 days.** `PlayoutDaysToBuild`, `IfNoneAsync(2)`;
  `finish = start.AddDays(daysToBuild)`. `isDone` flips when `currentTime`
  passes `finish`.
- **The script is killed after 30 seconds.** `PlayoutScriptedScheduleTimeoutSeconds`,
  default 30. A non-zero exit code fails the whole build. Every HTTP round trip
  spends this budget.
- **Items before `start - 4h` are trimmed** after the build
  (`RemoveBefore`), except on on-demand channels.

`schedulingEngine.WithSeed(playout.Seed)` — ErsatzTV seeds its own shuffle
ordering per playout. That is independent of our `stable_hash()` determinism
work; a `shuffle` ordering is reproducible to ErsatzTV, not to us.

## Endpoints

All paths are `/api/scripted/playout/build/{buildId}/...`. Client method names
are the snake_case of the operationId. Status is our framework's usage.

### Content registration — define a key, no scheduling effect

| Method | Required | Optional | Status |
|---|---|---|---|
| `add_search` | `key`, `query` | `order` | **used** |
| `add_collection` | `key`, `collection` | `order` | unused |
| `add_smart_collection` | `key`, `smartCollection` | `order` | unused |
| `add_multi_collection` | `key`, `multiCollection` | `order` | unused |
| `add_show` | `key`, `guids` | `order` | unused |
| `add_playlist` | `key`, `playlist`, `playlistGroup` | — | **used** |
| `create_playlist` | `key`, `items[{content,count}]` | — | unused |
| `add_marathon` | `key`, `groupBy` | `itemOrder`, `guids`, `searches`, `playAllItems`, `shuffleGroups` | unused |

`order` / `itemOrder` accept `chronological` and `shuffle` only. **Ordering binds
at registration, not at play time.**

`add_marathon` is a first-class marathon primitive we do not use: `groupBy` is
`show`/`season`/`artist`/`album`, `playAllItems` toggles all-of-a-group vs.
one-at-a-time, `shuffleGroups` randomizes group order. It combines multiple
`searches` into one key.

### Scheduling — advance the playout clock

| Method | Required | Key optional | Returns | Status |
|---|---|---|---|---|
| `add_count` | `content`, `count` | `fillerKind`, `customTitle`, `disableWatermarks` | `PlayoutContext` | **used** |
| `add_all` | `content` | same | `PlayoutContext` | unused |
| `add_duration` | `content`, `duration` | `fallback`, `trim`, `discardAttempts`, `stopBeforeEnd`, `offlineTail`, + above | `PlayoutContext` | unused |
| `pad_until` | `content`, `when` (HH:MM) | `tomorrow`, + all `add_duration` optionals | `PlayoutContext` | **used** |
| `pad_until_exact` | `content`, `when` (date-time) | same, no `tomorrow` | `PlayoutContext` | unused |
| `pad_to_next` | `content`, `minutes` | same | `PlayoutContext` | unused |
| `wait_until` | `when` (HH:MM) | `tomorrow`, `rewindOnReset` | `PlayoutContext` | **used** |
| `wait_until_exact` | `when` (date-time) | `rewindOnReset` | `PlayoutContext` | unused |

### Cursor control, inspection, overlays

| Method | Required | Returns | Status |
|---|---|---|---|
| `get_context` | — | `PlayoutContext` | **used** |
| `peek_next/{content}` (GET) | — | `PeekItemDuration {content, milliseconds}` | unused |
| `skip_to_item` | `content`, `season`, `episode` | — | **used** |
| `skip_items` | `content`, `count` | — | unused |
| `start_epg_group` | — (`advance`, `customTitle`) | — | **used** |
| `stop_epg_group` | — | — | **used** |
| `graphics_on` / `graphics_off` | `graphics[]`, `variables` | — | unused |
| `watermark_on` / `watermark_off` | `watermark[]` | — | unused |
| `pre_roll_on` / `pre_roll_off` | `playlist` | — | unused |

`PlayoutContext` = `currentTime`, `startTime`, `finishTime` (date-time) and
`isDone` (bool). The generated client exposes these snake_case.

## Semantics that matter

### Enumerators persist per key for the whole build

`SchedulingEngine` holds `Dictionary<string, EnumeratorDetails> _enumerators`,
populated at registration and living for the session. `AddCountInternal` loops
`count` times, and each iteration reads `Enumerator.Current`, appends a
`PlayoutItem`, advances `_state.CurrentTime` by the item duration, then calls
`Enumerator.MoveNext(...)`.

**Therefore `add_count(key, N)` is exactly N sequential `add_count(key, 1)`
calls.** The cursor never resets per call. Splitting a bulk count into
single-item calls preserves ordering — chronological stays consecutive, shuffle
stays shuffled — and is the mechanism that lets a caller re-check the clock
between items.

`skip_to_item` and `skip_items` mutate that same persistent cursor. They are
positioning operations, not per-play modifiers: issuing `skip_to_item` before
every single-item add pins the cursor and replays the same episode forever.
Position once, then pull.

### `add_count` has no time bound

`AddCountInternal` contains no comparison against `finishTime`, `isDone`, or any
boundary. It appends exactly `count` items regardless of how far past the build
window that lands. Bounding is entirely the caller's responsibility — or you use
`add_duration` / `pad_until*`, which do take a target time.

This was the root of the marathon overrun; see [KNOWN_ISSUES.md](KNOWN_ISSUES.md).
Unbounded marathon content now uses `add_duration` instead of a guessed count.

### `pad_until` silently schedules nothing when the target is in the past

From `SchedulingEngine.PadUntil`, `when` parses as `TimeOnly` (time of day, no
date). Then:

```csharp
if (timeOnly > padUntilTime)
{
    if (tomorrow)
    {
        dayOnly = dayOnly.AddDays(1);
        targetTime = new DateTimeOffset(dayOnly, padUntilTime, targetTime.Offset);
    }
}
else
{
    targetTime = new DateTimeOffset(dayOnly, padUntilTime, targetTime.Offset);
}
```

When the current time is already past `when` **and `tomorrow` is false**,
`targetTime` is left at `CurrentTime` — a zero-length pad. No content, no error,
no log. The spec says as much: *"When false, no content will be scheduled by
this request."*

That is the failure mode behind the defensive comment in
[`engines/dispatcher.py:265`](engines/dispatcher.py). `pad_until` is not
unreliable; it is precise about a contract we get wrong. Our `is_tomorrow` is
computed as `target_dt.day > current_time.day`, which returns `False` across a
month boundary (Aug 31 → Sep 1 is `1 > 31`), producing exactly this input.

### ErsatzTV has known DST bugs in the time-of-day variants

`PadUntil` carries two `// this is wrong when offset changes` comments from the
ErsatzTV authors, on both branches that reconstruct a `DateTimeOffset` from a
`TimeOnly`. `wait_until` shares the pattern.

`pad_until_exact` and `wait_until_exact` take a full `date-time` and skip the
reconstruction entirely. **Prefer the `_exact` variants** — they sidestep both
the `tomorrow` contract and the DST defect, and they let the caller pass the
`boundary_dt` it already computed instead of degrading it to `"%H:%M"`.

`playout.fill_until_time` and `playout.wait_until_time` now take a `datetime`
and call the `_exact` endpoints. The one place the time-of-day form is still
correct is each channel's `reset_playout`, which depends on `wait_until`'s
reset-mode rewind branch (`rewindOnReset` with `tomorrow=false`).

### Every scheduling call already returns the context

`add_count`, `add_all`, `add_duration`, all three `pad_*` and both `wait_until*`
return `PlayoutContext`. [`playout.py:46`](playout.py) discards it and issues a
separate `get_context`, doubling HTTP round trips on the hottest path in the
framework — against a 30-second build timeout.

## Mock fidelity

`scripts/testing/simulator.py` was aligned to the semantics above on
2026-08-27. It previously diverged in ways that hid the marathon overrun
entirely — `add_count` ignored `count`, there was no per-key cursor, and both
`pad_until` and `wait_until` always jumped to their target.

What the mock now models, and what it still does not:

| Behavior | Modelled? |
|---|---|
| `add_count` appends `count` items, no time bound | yes |
| Persistent per-key enumerator; `skip_to_item` / `skip_items` reposition it | yes |
| `pad_until` silent no-op when target passed and `tomorrow` false | yes |
| `wait_until` no-op on a passed target; rewind only in `reset` mode | yes |
| `add_duration` / `pad_until_exact` / `pad_to_next` / `add_all` / `peek_next` | yes |
| Build window defaults to 2 days (`DEFAULT_DAYS_TO_BUILD`) | yes |
| API round trips counted (`MockAPI.call_count`) | yes |
| 30-second build timeout enforced | **no** — count calls instead |
| Real item durations, real library sizes | **no** — guessed from key names |
| `trim`, `discardAttempts`, `fillerKind`, EPG grouping effects | **no** |

`TestApiContract` in `testing/test_scenarios.py` pins each modelled row. Those
tests assert against the mock, so they are only as good as its fidelity to
`SchedulingEngine.cs` — treat them as a record of intent, not proof about a
live ErsatzTV.

## Unused capability worth a look

- **`add_duration`** — bounded by wall-clock duration, with `trim`,
  `stopBeforeEnd`, `offlineTail` and a `fallback` key for the remainder. This is
  the natural primitive for "play this marathon for six hours".
- **`add_marathon`** — native multi-show marathon with grouping and per-group
  ordering. Overlaps substantially with `logic/calendar/assembly.py`.
- **`peek_next/{content}`** — next item's duration without consuming it. Enables
  exact fitting decisions, and would give `dispatcher.play_smart_bumper` real
  metadata instead of interpolating `tag:"{title}"`.
- **`customTitle`** on any add, and `advance`/`customTitle` on
  `start_epg_group` — EPG naming we currently approximate.
- **`fillerKind`** — flags content as filler for EPG grouping. We track filler
  ourselves and never tell ErsatzTV.
- **`graphics_*` / `watermark_*` / `pre_roll_*`** — per-slot overlay control,
  entirely unexplored.
- **`skip_items`** — the mock implements it; nothing calls it.

## Open questions

Not answerable from source; needs one real build to confirm.

1. Does the generated client surface `peek_next` with a usable return type, and
   what does it do when the enumerator is empty?
2. What does `add_count` do when the enumerator has fewer items than `count` —
   loop the collection, or stop? `AddCountInternal` loops on `count` and reads
   `Enumerator.Current` each time, which implies wrap-around, but the enumerator
   implementations were not read.
3. Exact `duration` string format accepted by `TimeSpanParser` for
   `add_duration`.
4. Whether `guids` (object) on `add_show` / `add_marathon` is keyed by provider
   (`imdb`, `tvdb`) — shape not documented in the spec.
