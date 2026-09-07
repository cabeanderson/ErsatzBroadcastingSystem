# Interstitial Policy — bumpers, promos, trailers

Status: **evaluated and partly built, 2026-09-05.** The composition rules and the
smart-bumper cascade shipped in this pass; acquisition is the open half.
Companion to [filler-taxonomy.md](filler-taxonomy.md) (the tree) and
bumper-inventory.md (superseded counts).

> **§8 item 1 is done.** The 56 staged reels were split on 2026-09-05 and
> yielded **3,721 spots** — not the "well over a thousand" estimated below.
> Sources for the remaining gaps are now verified and listed in
> [interstitial-acquisition.md](interstitial-acquisition.md), which supersedes
> §8's "where to look" and leaves its ranking intact.

The goal: *a random mix that fits each channel's vibe as the default, specific
sets inside specific blocks, 1–2 minutes between shows, only when it's worth it,
and some channels get none at all.*

Two things had to be true before any of that could be expressed. Both now are.

---

## 0. Two corrections to the first read of this

Recorded because both were wrong in the obvious direction, and the second cost a
whole section of a previous draft.

**Filler was never global.** `resolve_filler_content` and
`resolve_bumper_collection` already cascade Program > Block > Channel > Global,
and have since the config_utils refactor. Only `ENABLE_SMART_BUMPERS` was the
outlier — a module-level bool the dispatcher read directly. The fix was to make
the one exception match the rule the rest of the system already followed, not to
invent a hierarchy.

**The promos were never missing.** They are in the bumper tree with their
function written in the filename and nowhere else — see §5. An earlier draft of
this document reported "0 promos, and no promo concept". There are 221.

---

## 1. What is on disk

16,514 files. Counted 2026-09-05 by a full walk of `/media/filler`.

| Tree | Files | Reachable today |
|---|---:|---|
| `bumpers/` | 7,381 | yes, 56 registry keys |
| `interstitials/` | 8,809 | tree built 2026-09-04, **nothing wired** |
| `commercials/` | 324 | yes |
| `marathons/` | 4 | one DBZ Cell Games stub — a show, not filler |

### The bumper tree is one network

| Set | Files |
|---|---:|
| Adult Swim | 6,130 |
| — `bumps/general` | 4,682 |
| — `shows/` (32 shows) | 708 |
| — `seasonal/` (8 folders) | 233 |
| — intro / outro / marathon / april fools | 507 |
| Toonami | 1,251 |
| — `shows/` (32 shows) | 1,028 |
| — `general` | 111 |
| — intro / outro / bumps / marathon | 112 |
| **Cartoon Network daytime `general/`** | **0** |
| **Fox Kids** | **0** |

**Every bumper we own belongs to Cartoon Network, and 83% of those to Adult Swim.**
Of the 19 channels in [channel-plan.md](channel-plan.md), one has branding assets.
Two more borrow them: Japanorama can legitimately draw Toonami show bumpers for the
2,450 episodes it shares, and nothing else can draw anything.

The channel plan already says so in two places, in its own words: Disney — *"No
filler: `filler/bumpers/` has cartoon network and fox kids trees and nothing else"*;
Nick — *"There are no Nick bumpers on disk."*

---

## 2. The five asks, scored

| Ask | Assets | Verdict |
|---|---:|---|
| Random channel-vibe mix, as the default | CN only | Expressible now (§3, §4). Ready on 1 channel of 19 — everywhere else it is a **zero**, not a wiring gap. |
| Toonami DBZ bumpers between Dragon Ball shows | **5** (+8 Cooler's Revenge) | Mechanism built and the folder is already named right. The pool is still the thinnest in the tree relative to airtime — §2a. |
| Disney Saturday-morning bumpers | **0** | Acquisition. No Disney folder exists at any level. |
| 30 Rock promos in Must See Thursday | **221 promos exist** | Not an acquisition after all — the `next` files are promos, filed nowhere. Option 2 in §6 is true by construction and needs no new mechanism. |
| Movie channels: trailers between films, occasional BTS | **8,809**, title-matched | **The one that can ship this week.** |

### 2a. The inversion — depth runs opposite to airtime

The per-show bumper sets are deepest for shows that never air, and thinnest for the
shows that anchor the blocks.

| Show | Bumpers | Airs |
|---|---:|---|
| Fullmetal Alchemist Brotherhood | 108 | **no** |
| Inuyasha | 90 (+35 AS) | yes |
| Cowboy Bebop | 72 (+11 AS) | yes |
| Naruto | 66 | yes |
| Ghost in the Shell | 53 | film only |
| Bleach | 52 | **not owned** |
| One Piece | 44 | yes — Japanorama Syndication Hour |
| King of the Hill | 114 (AS) | yes |
| **Dragon Ball Z** | **5** | **yes — anchors two blocks** |
| **Yu Yu Hakusho** | **5** (+13 marathon) | **yes — Toonami anchor** |

Dragon Ball runs roughly two hours a day on Japanorama's Dragon Ball Hour (15:00–17:00)
plus its Toonami turns on 116. Even at one break an hour and three bumpers a break,
a 5-file pool recycles inside a single afternoon. **Of everything here, DBZ is the
one set where the ask is real and the assets are not.**

---

## 3. Smart bumpers — three modes, resolved per block — **built**

`ENABLE_SMART_BUMPERS` was a module-level bool read at `dispatcher.py:116`. It
was not resolvable per channel, so flipping it was lineup-wide: nineteen channels
or none. It is now `SMART_BUMPERS`, with three values, resolved by
`resolve_smart_bumpers()` through the same Program > Block > Channel > Global
cascade filler and commercials already used.

| Mode | Behaviour |
|---|---|
| `"none"` | Never look up a per-show bumper. Generic pools only. |
| `"some"` | Per-show first, generic pool when the show has none. The mix. |
| `"all"` | Per-show only. A show with no bumper of its own gets **nothing** rather than borrowing the channel's generic voice. |

**`"all"` exists because of Japanorama.** 1,249 of the 1,251 files in the Toonami
tree are literally named `Toonami_*` — the two exceptions are *Bring Back
Toonami* clips, which are no less Toonami. There is no unbranded subset to
borrow, so a generic fallback on Japanorama puts a Cartoon Network ident on a
Japanese broadcast-day channel. Under `"all"` the channel takes a per-show bumper
where one genuinely belongs to the show and stays silent everywhere else.

Changed in the same pass: the per-show query now interpolates `tag_full`, not
`tag`. Both carry the folder name, but `tag` is whitespace-tokenized, so
`tag:"naruto"` also matched `naruto shippuden`. `tag_full` is case-sensitive and
folder names are lowercase, so the title is lowercased at the call site rather
than relying on callers.

| File | Change |
|---|---|
| `settings.py` | `SMART_BUMPERS` replaces the bool; `MAX_BUMPERS_PER_BREAK = 2` |
| `logic/resolution/config_utils.py` | `resolve_smart_bumpers()`; unknown value degrades to `"none"` rather than raising |
| `logic/structures.py` | `smart_bumpers` on `Block` and `Program` |
| `scheduling/config.py` | `ScheduleConfig.smart_bumpers` |
| `engines/dispatcher.py` | mode-aware `play_bumper` / `play_smart_bumper`, `tag_full` fix |
| `engines/blocks.py` | resolves and threads the mode |

---

## 4. What "1–2 minutes" actually costs

Sampled durations, 2026-09-05:

| Pool | Median | p90 | Max |
|---|---:|---:|---:|
| Adult Swim `bumps/general` | 15s | 15s | 30s |
| Adult Swim `intro` | 15s | 20s | 20s |
| Toonami `intro` | 20s | 20s | 21s |
| Toonami `general` | 10s | 15s | 15s |
| Toonami DBZ | 10s | 10s | 15s |
| US commercials | 34s | 106s | 257s |
| UK commercials | 31s | 61s | 123s |
| Trailers *(from taxonomy §9)* | 2m11s | — | 2m51s |

**Ninety seconds of pure Toonami bumpers is nine files.** Filled that way, the
111-file `general` pool recycles visibly within a week, and DBZ's 5 cannot fill even
one break without repeating itself.

The fix is the one real TV used: **a break is a recipe, not a pool.** A 90-second
break composed as

> block intro (15–20s) → 1 commercial (30s) → 2 show bumpers (20–30s)

spends only two files from the thin per-show set, reads as a real commercial break,
and lets the deep pools (4,682 AS general, 324 commercials) carry the volume. It
also means DBZ's 5 bumpers become adequate rather than embarrassing — 2 per break
against 3 breaks a day is a 2-day cycle, not a 20-minute one.

Trailers are the exception: one trailer *is* the break at 2m11s median.

---

### The invariant — **built**

The rule lives in one place, `dispatcher.BreakState`, which every branding path
passes through. Putting it at the call sites would have meant re-deriving it in
`play_bumper`, `play_generic_branding` and both commercial paths, and any future
path would have missed it.

Two rules:

1. **Never two bumpers back to back.** A bumper sits against a show on one side.
2. **At most `MAX_BUMPERS_PER_BREAK` (2) bumpers between two shows.**

**"Normally one, two on the longer breaks" is not a setting — it falls out.** A
second bumper is only legal once commercials have separated it from the first,
so a break with no ad time gets one bumper and a 1–2 minute break gets two. One
invariant, both behaviours:

```
no ad time:     SHOW -> bump -> (bump refused) -> SHOW
1-2 min break:  SHOW -> bump -> ads -> bump -> SHOW
three offered:  SHOW -> bump -> ads -> bump -> ads -> (bump refused) -> SHOW
budget resets:  SHOW -> bump -> ads -> bump -> SHOW -> bump -> ads -> bump -> SHOW
```

Intros and outros count as branding for adjacency but do not spend the bumper
budget — they are the block's own top and tail, not break filler. One consequence
is a **behaviour change at block seams**: `outro -> intro` back to back is now
refused, and the intro is skipped unless commercials separate it. That is the
strict reading, and it matches the medium — the outro/intro pair is separated by
the break, not adjacent to itself.

The budget resets on content, guarded on the clock actually advancing, so a
program that resolves to nothing cannot clear the state and let branding stack.

---

## 5. "Only when it's worth it"

Where a break earns its 1–2 minutes:

- **Between shows inside a branded block** — the Toonami hour, Adult Swim prime, the Disney Afternoon. This is the whole point.
- **Before a marquee appointment** — 15:00 Disney Afternoon, Must See Thursday, High Noon's 12:00 feature. A promo or intro here is what makes the appointment feel like one.
- **At the hour boundary**, where `fill_to_boundary` already runs.
- **Between films** on the movie channels, where the gap exists anyway.

Where it does not:

- **Between two halves of a serialized arc.** Disney's Gravity Falls / Owl House strip, Nick's Avatar, anything running chronological-weekday. Breaking the run is the cost; there is no branding payoff.
- **Mid-marathon**, except with marathon-specific assets — which we have and which are correctly separated: 25 AS `marathon/general`, 18 Toonami Bebop, 13 Yu Yu Hakusho, 6 Astro Boy.
- **Channels whose identity is continuity** — Lucy TV, the overnight strips. Some channels should get nothing, and that is a design position, not a gap.

---

## 6. Promos — we have 221, and they are not categorized

A promo is a third kind of interstitial. The distinction is not pedantry: it is
the only one of the three that can be **false**.

| Type | Says | Truth condition |
|---|---|---|
| **Bumper** | "You're watching Toonami." | none — always true |
| **Commercial** | "Buy Rice Krispies." | none — it's an ad |
| **Promo** | "30 Rock, Thursdays at 8." | **claims a future airing** |

### The break-position vocabulary already on disk

The promos were never missing. Toonami's filenames encode a complete break
position for every file, and nothing else records it:

```
Toonami_Evangelion_1_11_Next.mp4      <- a promo. "Next: Evangelion."
Toonami_Now_Evangelion_1_11.mp4       <- immediately before the show
Toonami_Evangelion_1_11_To_Ads.mp4    <- immediately after it
Toonami_Evangelion_1_11_Back_3.mp4    <- returns from the break
```

Counted across the Cartoon Network tree:

| Position | Files | What it is |
|---|---:|---|
| `next` | 221 | **the promos** |
| `now` | 149 | goes immediately before the show |
| `to ads` | 124 | goes immediately after it |
| `back` | 109 | returns from the break |
| `intro` | 86 | block opener |

That is exactly the structure §4's invariant wants — `to ads` on the outgoing
side of a break, `back` or `now` on the incoming side. A filename is not a tag,
though: ErsatzTV derives tags from folder path segments only, so none of it is
addressable today.

### The filing script

`scripts/filler/sort_bumper_positions.py`, dry-run by default. It files each
file into a position folder **under its existing parent**:

```
shows/dragon ball z/Toonami_DBZ_To_Ads.mp4
shows/dragon ball z/to ads/Toonami_DBZ_To_Ads.mp4
```

Tags are flat, so `dragon ball z` survives untouched and every per-show key keeps
working — §1a's "depth is free, and adding a level never breaks an existing
query". What is gained is a second tag:

```
tag_full:"dragon ball z" AND tag_full:"to ads"     leaving the show
tag_full:"dragon ball z" AND tag_full:"back"       returning to it
tag_full:"next"                                    the promo pool
```

**Deliberately not moved to a separate `promos/` tree.** These files are
Toonami-branded whatever they advertise, so filing them as network-neutral promos
would be a lie by folder path — and it would strip the `bumpers` tag
`play_smart_bumper` requires. A `next` folder makes them addressable as promos at
neither cost.

**Apply to Toonami only.** The two networks are not equal quality:

| Scope | Moves | Verdict |
|---|---:|---|
| `cartoon network/toonami` | 653 | Clean. Rigid `Toonami_<Show>_<Position>` naming. |
| `cartoon network/adult swim` | 36 | **Leave it.** `Bring_Back_Toonami_Rap` is a false positive ("bring back" is not a return from break), and `ATHF_New_Next_Sunday` is a promo with a time claim, not an up-next bumper. Not worth the misfile risk against a 4,682-file generic pool that works as it is. |

### Schedule-aware promos are easier here than in general

The general problem is hard. This system's is not, **because the schedules are
static weekly grids defined in code**. A promo saying "Thursdays at 8" is
permanently true as long as `config.schedules` says so; there is no runtime state
to consult and nothing to keep in sync.

Three approaches, and the middle one needs no new mechanism at all:

| # | Approach | Cost |
|---|---|---|
| 1 | **Era promos with no time claim** — generic "next, on NBC" network voice. | Safe anywhere. Cheapest real win. |
| 2 | **Real show promos aired inside the block they advertise.** A 30 Rock promo during Must See Thursday is true by construction. | **Chosen.** Needs only a pool and matching folder names. |
| 3 | **Schedule-aware** — "tomorrow at 8". | Needs the promo's *claimed* day/hour as metadata (NFO sidecars), matched against the slot. Real, but later. |

A cheap middle path to 3: prefer promos that say "Thursday nights" over
"Thursdays at 8". Day-accurate and time-vague is satisfiable by every channel.

---

## 7. Movie channels — ready now, with one correction

The interstitial farm is built, hardlinked, re-runnable and inert. 2,261 trailers
across 2,012 films, decade-tagged and title-tagged.

Trailer coverage against the era line: **425 pre-1980** (Cabes Classic Cinema),
**351 in the eighties** (Totally 80s), **1,485 from 1990 on** (Be Kind Rewind).
Genre-matched: Horror 240 for Nightmare Theatre, Western 46 for High Noon,
Sci-Fi 410 and Fantasy 324 for Other Worlds and the unbuilt fantasy channel.

**The correction.** `play_smart_bumper` with `required_tags=["trailers"]` resolves a
film's **own** trailer as its pre-roll. The taxonomy presents this as the payoff, and
mechanically it is elegant — but it is not what television does, and it is mildly
self-defeating: a trailer is a *tease for something you haven't seen*, and running it
against the film that immediately follows spends the surprise and reads as padding.

Channels play trailers for **other** films. The decade tags already support exactly
that, with no new content and no new mechanism:

```
tag_full:"trailers" AND tag_full:"1970s"     → Cabes Classic Cinema between features
tag_full:"trailers" AND tag_full:"1980s"     → Totally 80s
```

A genre pool would be better still, and the taxonomy is right that it belongs in NFO
sidecars rather than more folders — hardlinking a multi-genre film into several
folders would skew shuffle. `library-movies.tsv` already carries the genre for 2,008
of 2,012 films, so the sidecars are generatable.

**Behind-the-scenes as an occasional feature** is the other half of the ask, and the
type split makes it schedulable: 65 BTS, 28 featurettes, 78 interviews, 85 deleted
scenes, 13 shorts. Medians run 6m55s–12m56s, so these are not break-fillers — they
are a *segment*, and they want a named slot. Nightmare Theatre and Cabes Classic
Cinema both have late slots where a 7-minute featurette after the feature would read
as programming rather than filler. The 6,279 `extras/` are unsorted by length and
should stay out of any automatic pool until they are.

---

## 8. Acquisition — the lineup wants five decades, not one network

The obvious framing of this is "get NBC Must See TV promos for Corncob." That is
one block on one channel. The lineup runs **1951 to the present across nineteen
channels**, and most of them want period-correct continuity that has nothing to
do with 1990s NBC.

**The term of art is "aircheck"** — an off-air recording of a broadcast as it
went out, ads and continuity intact. It is the search word that unlocks nearly
all of this, and it is the highest-yield format by a wide margin: a single
two-hour tape of Disney Channel 1994 yields the bumpers, the promos *and* the
commercials, in period-correct sequence, from one capture. The 56 staged reels
already prove the pipeline works.

### What each channel actually wants

| Channel | Era | Material |
|---|---|---|
| **190 Good Times** | **1951–1999** | The widest need on the lineup. CBS/NBC/ABC promos across five decades — the channel spans from *I Love Lucy* to *Frasier*, so one era's voice fits maybe a fifth of it. |
| **247 Nick at Nite** | 1950s–70s + 1985–2000 | Two distinct layers: the classic TV the block airs, and Nick at Nite's own idents wrapping it. The idents are well preserved — the block had a strong graphic identity people collected. |
| **248 Disney** | 1983–2005 | The named gap. `Disney Channel` 1990s idents, `One Saturday Morning` (ABC), and the syndicated `Disney Afternoon` wraparounds — the last of which is what the 15:00 appointment wants. |
| **120 Lucy TV** | 1951–1957 | CBS continuity of the period. Small, specific, and the channel is continuity-first, so it may want almost none — see §5. |
| **243 High Noon** | 1955–1975 | Network western promos and the era's sponsor billboards. The 60s end of this is genuinely scarce. |
| **180 Totally 80s** | 1980–1989 | 80s network promos and idents. Sits alongside the 351 eighties trailers already on disk. |
| **144 Mystery Theatre** | 1970s–90s | Procedural promos — "tonight, on a very special…". A well-defined voice and a well-recorded era. |
| **104 Across the Pond** | 1960s–2000s | **The most distinctive and most separable.** BBC/ITV continuity announcers, regional idents, the clock. Pairs with the 114 UK spots already filed, and must never mix with US material. |
| **242 Corncob TV** | 1999– | NBC Thursday, and the cable/streaming era's promo voice generally. |
| **246 The Beat** | 1981– | MTV/VH1 idents. The channel has no interstitials at all today. |
| **116 Cartoon Network** | 1992–2007 | The one gap in an otherwise deep tree: `cartoon network/general/` is scaffolded and empty, so CN daytime borrows Adult Swim's late-night voice or nothing. |
| **151 / 244 / 142 / 249** | varies | Film channels — served by trailers (§7), plus the 215 TV spots already on disk. |
| **240 / 241** | 1990s– | PBS/Food Network/HGTV pledge-era continuity. Lowest priority; both channels are unbuilt. |

### Ranked

| # | What | Why it ranks here |
|---|---|---|
| 1 | **Split the 56 staged off-air reels** | 12 GB, ~30 hours, already on disk under `/media/.staging/us_commercials`. Silence-and-scene splitting plausibly yields **well over a thousand** US spots plus whatever continuity survives in them. The only line here that costs no acquisition at all. |
| 2 | **Disney airchecks** | Named ask, zero assets, sharpest block definition in the lineup. |
| 3 | **Good Times, by decade** | Widest span, and the channel is 8 hours a day of the lineup's most-watched format. Acquire 1950s/60s first — it is scarcest and it also serves Lucy TV and Nick at Nite. |
| 4 | **Nick at Nite idents** | Strong identity, well preserved, and serves two blocks on 247. |
| 5 | **BBC/ITV continuity** | Highest distinctiveness per file, and it is the one set that cannot be substituted from US material. |
| 6 | **Deepen Dragon Ball Z** | §2a. The one per-show set where airtime badly outruns assets. |
| 7 | **Cartoon Network daytime `general/`** | Folder already scaffolded and empty. |
| 8 | **Genre NFO sidecars for trailers** | Not an acquisition — a generation pass over `library-movies.tsv`. Unlocks genre trailer pools for five channels. |

### What to keep from a capture, in priority order

Given §4's invariant, the positions that make a break read as television are
`to ads` and `back`. Promos (`next`) are second. Generic network voice is a
distant third — Adult Swim's 4,682-file pool is proof that very few are needed
per channel, and that the deep pool is the *least* scarce thing here.

### Already owned, worth mining before acquiring anything

- **215 TV spots and teasers** inside `interstitials/extras/` — 52 `TV Spots.mkv`, 43 `Teaser.mkv`, plus `king kong/NBC Promos.mkv` and `network/Tune in Next Tuesday.mkv`. Period *television* advertising for films, which is a better between-features interstitial than a theatrical trailer.
- **The 221 `next` files** — §6.
- **The 56 reels** — item 1 above.

---

## 9. Recommended order of work

| Step | State |
|---|---|
| 1. Make `SMART_BUMPERS` per-channel | **done** — §3 |
| 2. Fix `tag` → `tag_full` in `play_smart_bumper` | **done** — §3 |
| 3. Enforce break composition | **done** — §4, `dispatcher.BreakState` |
| 4. Apply `sort_bumper_positions.py` to the Toonami scope | ready — dry-run reviewed, 653 moves. Requires a rescan after. |
| 5. Turn on the movie channels, decade pools not own-film | ready — assets exist, titles match, no acquisition |
| 6. Wire a first channel pair: CN on `"some"`, Japanorama on `"all"` | ready |
| 7. Confirm the Other Videos library root | open question 7 of the taxonomy; unanswerable from this machine |
| 8. Acquisition, in §8 order | open |

Steps 1–3 shipped 2026-09-05 and cost nothing in storage. Steps 4–6 are
configuration over assets already on disk. Step 8 is where the Disney and
period-continuity gaps actually get answered.
