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

They are also keyed by content, so they must be issued against the key that
will actually play. Anything that rewrites the key afterwards — a seasonal or
holiday injection turning `foo` into `foo_auto_spring` — leaves the skip
positioning an enumerator nobody reads. `play_program` therefore resolves
injections first and skips last.

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

## Reading the live server, outside a build

Everything above is scoped to `/api/scripted/playout/build/{buildId}/…` and only
exists while a build is running. Separately, the server exposes a small set of
**unauthenticated read endpoints** that need no build, and they are the only way
to check what a channel actually aired. Verified 2026-09-01 against ErsatzTV
`26.3.0-docker-amd64`, `apiVersion 3`, at `<ersatztv-host>:8409`.

| Endpoint | Type | Use |
|---|---|---|
| `/api/channels` | JSON | Channel roster — id, number, name, ffmpeg profile, streaming mode |
| `/api/version` | JSON | Build and API version |
| `/iptv/channels.m3u` | M3U | The **enabled** lineup |
| `/iptv/xmltv.xml` | XML | Every scheduled programme, with titles and start/stop. ~20MB |
| `/iptv/channel/{number}.m3u8` | HLS | Live stream, frame-grabbable with ffmpeg |
| `/iptv/logos/gen?text=…` | PNG | Generated channel logo |

**A 200 proves nothing.** ErsatzTV serves the Blazor SPA shell for *any*
unmatched path, so `/api/playouts`, `/api/health`, `/api/collections` and any
invented name all return `200` with a ~39KB HTML body. There is no `/api/search`
and no OpenAPI document served at runtime. The only reliable discriminator is
`content-type`: `application/json` is real, `text/html` is the catch-all. Probe
with `curl -o /dev/null -w '%{http_code} %{content_type}'`, never status alone.

### The channel-visibility ladder

A channel occupies one of three states, and the feeds distinguish them. This
cost a wrong diagnosis on 2026-08-31 — m3u presence was read as proof of a
playout, and it is not.

| State | `/api/channels` | `channels.m3u` | `xmltv.xml` |
|---|---|---|---|
| Defined but disabled | yes | no | no |
| Enabled, playout not built | yes | **yes** | no |
| Enabled and built | yes | yes | **yes** |

So: **m3u means tunable, xmltv means scheduled.** A channel in the m3u and
absent from the xmltv has no playout items — it needs an EPG enable and a build,
which is exactly what High Noon needed on 2026-09-01. A channel in
`/api/channels` and in neither feed is disabled (Wild Horizons) or never
attached.

### What this is actually for

`key_census` and `validate_titles` resolve against the on-disk manifests and
**cannot see the ErsatzTV index** — both say so in their own docstrings. They
answer "can the library satisfy this query". The EPG answers the stricter
question, "is the right thing on the air", and the two came apart badly on
2026-08-31 when Nightmare Theatre aired the Good Times lineup while every
relevant key resolved perfectly.

Useful checks, none of which need more than `curl`:

- **Content correctness.** Pull `xmltv.xml`, read the real titles per channel,
  compare against what the channel is *for*. Caught the sitcoms-on-a-horror-
  channel defect and the Casablanca era slip.
- **Playout existence.** Compare `/api/channels` against the m3u and the xmltv
  using the ladder above.
- **Differential snapshots.** Two pulls minutes apart show what a rebuild
  changed — this is what proved the Nightmare regression rather than suggesting it.
- **Span-normalised health.** Raw programme counts are not comparable across
  channels, because playouts are built to very different horizons (4071h for
  Cabes Classic Cinema against 67h for Across the Pond on the same pull). Use
  programmes per hour of span, and unique titles, and read the titles themselves
  before calling a channel healthy.
- **Visual confirmation.** `ffmpeg -i http://…/iptv/channel/{n}.m3u8 -frames:v 1`
  grabs a real frame. It opens a transcode session on the server, so use it
  sparingly.

### The XMLTV export is truncated separately from the playout

Found 2026-09-03. `xmltv.xml` stopped at `now + 2 days` (last stop 09-05 16:19,
identical across two pulls minutes apart) while the playout in the UI was
correctly built to 4 days.

**ErsatzTV clamps the XMLTV export with its own days setting, independent of
`PlayoutDaysToBuild`** — a deliberate optimisation, so a long playout does not
force a huge guide file on every client that pulls it. A short feed is therefore
*not* evidence of a short playout, and this was misdiagnosed that way once.

To extend the guide horizon, raise **both** settings, and raise
`PlayoutScriptedScheduleTimeoutSeconds` (default 30) first — the script is killed
at that mark and a non-zero exit fails the whole build, so doubling the day loop
inside an unchanged budget is the likeliest way to break a working channel. The
failure mode is a channel silently vanishing from the feed, so re-pull and count
channels after the first rebuild.

### There is no read API beyond these

Probed 2026-09-03, discriminating on content type. `/api/channels` and the
`/iptv/*` feeds are the whole surface. All of `/api/playouts`, `/api/playout`,
`/api/schedules`, `/api/collections`, `/api/media/movies`, `/api/search`,
`/api/epg`, `/api/guide`, `/api/scripted`, `/api/programs`, `/api/settings`,
`/api/playout/1` and `/api/channels/1` return the SPA shell (`text/html`,
~39,680 b). `/swagger/v1/swagger.json` is a genuine 404 — no schema at runtime.

So **there is no way to ask the server for the schedule other than XMLTV**, and
the scripted API under `/api/scripted/playout/build/{buildId}/…` is write-only in
this sense: it has no verb that returns the built playout. What XMLTV carries is
richer than a query API would be anyway — on the 2026-09-03 pull, 3,041 episode
subtitles, 3,246 synopses, 3,288 content ratings, 253 film release years, and
poster/still art for every programme.

**Still out of reach:** the playout-to-script wiring lives in the SQLite DB under
`/srv/appdata/ersatztv`, which is `drwx------ root root`, and the SSH account has
no passwordless sudo and no docker access. Mis-wiring can be *detected* from the
EPG but only *fixed* in the UI. HTTP writes were deliberately not probed —
`OPTIONS` returns no `Allow` header (catch-all again), and a malformed request
against an undiscovered write endpoint could create or destroy a channel.

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
5. **Does `start_epg_group(advance=True)` *without* `custom_title` produce a
   group that keeps per-item metadata and artwork?** Observed on a live build:
   a group started with `custom_title` renders in the guide as a single
   name-only entry with no artwork, no episode title and no description —
   consistent with `custom_title` creating a synthetic entry backed by no media
   item, but that is inference, not something the spec states. If dropping the
   title preserves the underlying items' metadata, that is the only version of
   block branding worth having, and re-enabling it is a small change to the two
   `if name:` guards in `playout.py` (`epg_group` and `toggle_epg_group`), which
   today make a group without a custom title unreachable. If it does not, EPG
   grouping is only ever worth it where the individual items genuinely are
   noise — i.e. marathons. **This is why all 32 static `use_epg_group=True`
   flags were removed from animation/disney/nickelodeon (2026-08-30);** the
   marathon grouping in `logic/calendar/assembly.py:122` was deliberately kept.
   Note the mock cannot answer this — see the "EPG grouping effects" row in the
   fidelity table above.
