# The Listings Magazine — plan for a guide site

A companion website to the lineup: not an EPG with a retro skin, but an **issue**
— channels described, blocks explained, the week's events called out, with
per-title writing that talks about the episode or the film rather than just
naming it.

Written 2026-09-03. Every number here was verified against the live server that
day (ErsatzTV `26.3.0`, `<ersatztv-host>:8409`), not read off the offline manifests.

Design memo, with a worked mock issue:
<https://claude.ai/code/artifact/c986e68f-2d36-4c39-b2af-62e62d792f1e>

---

## What the feed actually gives you

One pull of `/iptv/xmltv.xml` — 4.5 MB, about a second on the LAN:

| | |
|---|---|
| Programmes | 4,352 across 18 channels |
| Distinct titles | 898 |
| With episode subtitle | 3,041 |
| With synopsis | 3,246 |
| With content rating | 3,288 |
| Films carrying a `<date>` release year | 253 |
| Unique posters / stills | 334 / 2,892 |

Poster and still URLs point at `http://<ersatztv-host>:8409/iptv/artwork/…`. They
work on the couch and nowhere else — cache and rewrite them at build time. **Never
proxy them**; that is the one design choice that would turn a safe static site
into an exposed one.

## Querying ErsatzTV directly is not possible

Probed 2026-09-03, discriminating on **content type** rather than status code —
the Blazor SPA catch-all returns `200` with a ~39 KB HTML body for any unmatched
path, so status alone proves nothing.

| Path | Result |
|---|---|
| `/api/channels` | `application/json`, 2,246 b — **real** |
| `/iptv/xmltv.xml` | `application/xml`, 4.5 MB — **real** |
| `/api/playouts`, `/api/playout`, `/api/schedules`, `/api/collections`, `/api/media/movies`, `/api/search`, `/api/epg`, `/api/guide`, `/api/scripted`, `/api/programs`, `/api/settings`, `/api/playout/1`, `/api/channels/1` | `text/html`, ~39,680 b each — **SPA shell** |
| `/swagger/v1/swagger.json` | 404 — no schema served at runtime |

The scripted-schedule API exists only inside a running build, under
`/api/scripted/playout/build/{buildId}/…`, and it is a *write* interface with no
"give me the schedule" verb. The full playout is in root-only SQLite. **XMLTV is
the only door, and it carries more than a query API would.**

## The two-day wall is the XMLTV export, not the playout

The feed stopped at `now + 2 days` (last stop 2026-09-05 16:19, identical across
two pulls minutes apart) while the playout in the UI was correctly built to 4
days.

**ErsatzTV truncates the XMLTV export independently of the playout** — a
deliberate optimisation, so a long playout doesn't force a huge guide file on
every client that pulls it. This was initially misdiagnosed as the playout being
short; it is not.

To get a week:

1. Raise the **XMLTV days** setting — this is the one clamping the feed.
2. Raise **playout days** to match. A guide can only describe what the playout
   has actually decided.
3. **Raise `PlayoutScriptedScheduleTimeoutSeconds` first** (default 30). The
   script is killed at that mark and a non-zero exit fails the whole build.
   Doubling the horizon doubles the day loop and the API round trips inside the
   same budget. 180s costs nothing if unused.

Go to **10–12 days rather than 8**. At exactly 8 there is one issue and zero
slack, so a slipped build leaves the next issue short.

Verify by re-pulling and checking two things: the wall moved, and all eighteen
channels are still present. A failed build shows up as a channel silently
vanishing from the feed.

Expect the file to grow to roughly 18 MB. Irrelevant for a generator on the LAN.

## Two sources, and the repo is the more valuable one

An EPG needs the feed. An issue needs the feed *and* the reasoning behind the
lineup — and the second half is what makes it a magazine instead of a grid.

| Source | Gives | Changes |
|---|---|---|
| **The repo** — channel and library modules | Channel identity, block structure, daypart logic, why each hour is what it is | When a channel is redesigned |
| **The feed** — `xmltv.xml` | What actually lands in each block this week | Every rebuild |

`horror.py` opens with forty lines explaining why Nightmare Theatre is shaped the
way it is. Every module has that, in a voice no metadata API sells.

**It goes in `channels.toml`, rewritten as reader-facing copy.** The docstrings
are written for the author, not for a reader. The scheduler owns the file and
ignores it; the guide reads it. This keeps the web toolchain out of the scheduler
and makes the copy editable without touching code.

## Events: the rule is recurrence, not episode number

Announce a premiere when it is **appointment** television — when the next
occurrence is far enough away that a reader would regret missing this one. Lost's
fall premiere is news precisely because the next one is a year out.

This has nothing to do with whether the episode number is 1. There are **210
first-episode airings** in a six-day window; Peep Show airs seasons 4, 5, 7, 8
and 9 inside it, Are You Being Served? touches all ten. A shuffle doing its job
is not an event.

The framework already encodes the distinction:

| Structure | Count | Recurs | Announce? |
|---|---|---|---|
| `annual_show` | 46 | Yearly | **Always** — the headline events |
| `SeasonalBlock` | 16 | Yearly | **Always** — block changes, holiday themes |
| `MarathonSequence` | 10 | Occasional | **Always** — the cover story |
| `OrderedCollection` | 175 | Weeks | Season boundaries only |
| `DailyOrderedCollection` | 22 | Daily | Describe, don't announce |
| `RandomCollection` | 200 | Constantly | **Never** |

Calling a *finale* needs season lengths. `reference/library-tv.tsv` has totals
per show, not per season — backfill from TMDB for the ordered strips only (a much
smaller set than 898 titles) and cache permanently.

## Per-title copy — where it comes from

All free, all cacheable once per title. Verified live 2026-09-03.

| For | Source | Notes |
|---|---|---|
| Episode writing | The feed | 3,246 synopses already present |
| Film trivia / BTS | **Wikipedia API**, no key | Articles carry `Production`, `Development and writing`, `Filming`, `Casting`, `Accolades` sections |
| Awards | Wikipedia `Accolades`, or OMDb | OMDb returns a ready-made awards string plus RT/Metacritic; free key, 1,000/day |
| Review snippets | OMDb scores + Wikipedia `Critical response` | Quote sparingly, attribute |
| Posters / stills | The feed | Cached and resized at build time |

**Wikidata is not the answer for awards.** Querying `P166` by label matched the
*novel* for "The Maltese Falcon", not the film. Resolving to a QID first would
work, but Wikipedia's own sections are simpler and read better.

What the Anaconda (1997) article yielded in one call — shot on location in Brazil
and finished at the LA County Arboretum lagoon; the idea came from writer Hans
Bauer's false memory of King Kong fighting a giant snake (it was a lizard, he
never looked at the feet); six Razzie nominations including Worst New Star for
*the animatronic anaconda*. That is the register the column should be in.

### The one piece of plumbing

Title-to-article resolution must disambiguate **by year**. Searching
`Anaconda 1997 film` returns the 1997 film *and* the 2025 one; `Companion 2025
film` correctly returns `Companion (film)`. The feed supplies the year — 253 film
airings carry `<date>` alongside a `Movie` category.

Resolve once, cache on title + year, review misses by hand. An afternoon, once.

## Architecture: generate on the LAN, publish flat

A Python generator on the workstation or OMV box pulls the feed, cleans it,
caches artwork, merges `channels.toml` and the per-title cache, and emits
`issue.json` plus static pages. Cron it. Push to Cloudflare Pages.

Static is the right call and was the user's own starting position. The page knows
the time, so "on now" and the dimming of past days are computed client-side with
no rebuild. A hosted CI runner **cannot** do this job — it has no route to
<ersatztv-host>. The generator must run on the LAN.

Rejected: a public reverse proxy to ErsatzTV. Its endpoints are completely
unauthenticated.

### Issues are immutable once published

Write each week to its own dated path and **stop regenerating it**. Otherwise a
mid-week rebuild silently rewrites Monday's listings to whatever the shuffle
decided on the second pass, and the archive stops being a record of what actually
aired. The live grid stays continuous; the issue is a snapshot.

Past days dim rather than disappear — a Thursday reader still wants to see that
Monday's block change happened.

The archive compounds. A year of issues is a history of how the lineup evolved,
which the channel modules currently record only as git history.

## Known content defects the guide will expose

Filler and bumpers are leaking into the EPG as programmes. Invisible today,
unmissable the moment there is a guide:

- **Across the Pond** — `s2014e112400 - Magic Moments Quality Street 1990's`
- **Cartoon Network** — `Toonami_Later`, `2003_HowTo___Intro`
- **The Beat** — genre slugs as titles: `hip_hop`, `oldies`, `rock`

The generator needs a title-cleanup pass that drops these and title-cases the
slugs. **Emit a report of what it dropped** — it doubles as a defect check
against the channel modules, in the spirit of `same_title_check.py`.

## Publishing publicly: low risk, three precautions

The exposure is **disclosure, not compromise**. Static files on a CDN have no
request path back to the network, no credential to leak, nothing to inject into.

| Exposure | Do |
|---|---|
| The listing discloses the library (898 titles, implying more) | Inherent — it is what the site *is*. Decide once. |
| Search engines index it | `noindex` + `robots.txt` disallow. Removes the discovery vector at no cost to readers. |
| Domain links the guide to the media server | Host on `*.pages.dev` or an unrelated domain. Note **certificate transparency logs already publish every subdomain issued a cert** — subdomain obscurity is not a control. |
| Internal addresses in the payload | Strip them. RFC1918 leaks topology, not access — but you're rewriting artwork URLs anyway. |
| Proxying artwork through to the server | **Don't.** |

Cloudflare Access (free tier) gates the whole site behind an emailed one-time
code, ~10 minutes, no password to manage, addable later without changing how the
site is built. Worth knowing it exists; not worth doing preemptively.

## Cost

Everything is $0/month: Cloudflare Pages free tier, cron on hardware already
owned, Wikipedia and OMDb free tiers, Resend free tier (3,000 sends) for the
weekly email — Gmail SMTP also works but expect layout quirks. One-time
model-written period copy, if used at all, is cents and cached to disk.

Nothing here has a growth path into a bill.

## Build order

0. **Move the wall** (½ hr) — timeout to 180s, then XMLTV days and playout days
   to 10–12. Rebuild, re-pull, confirm the horizon moved *and* all 18 channels
   survive. The only step that can fail for reasons outside the code.
1. **Extract channel copy** (1 hr) — modules → `channels.toml`, rewritten for a
   reader. Cheapest part; decides whether the magazine idea works.
2. **The parser** (evening) — parse, clean filler, cache posters, resolve films to
   Wikipedia by title + year, emit `issue.json`.
3. **The issue** (weekend) — channel pages, week's listings with production notes
   and awards, block-change callouts, past days dimmed, dated immutable path. The
   scrollable grid rides along as a second view.
4. **Publish** (1 hr) — Cloudflare Pages, `noindex`, cron, staleness banner.
5. **Events and the Sunday email** (evening) — recurrence-rule detection off the
   framework, TMDB season lengths for finales. The email is the issue's front
   page: five things worth setting time aside for, not a listing.

## Open questions

- **How much per-title writing by hand?** Auto-generate everything, hand-edit
  only the week's three or four featured items, and store edits in the same cache
  so they survive rebuilds and accumulate. After a year the frequently-aired
  films are hand-written and the long tail is still covered.
- **Separate repo?** Yes — different deploy target, different cadence, and a web
  toolchain the scheduler should not inherit. The only shared surface is
  `channels.toml`.

## Related

- `ERSATZTV_API.md` — "Reading the live server", the visibility ladder, the SPA
  catch-all trap, and the XMLTV export setting
- `reference/channel-plan.md`, `reference/channel-rules.md` — the source of the
  channel copy
- `testing/same_title_check.py`, `testing/collision_report.py` — the existing
  offline checkers the cleanup report complements
