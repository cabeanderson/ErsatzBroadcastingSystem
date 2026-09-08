# Channel Rules

The accumulated law for making and curating channels on this lineup. Every rule
here was paid for by a channel that got it wrong first, so each one names the
channel that proved it.

**What this file is for.** [channel-plan.md](channel-plan.md) is the working
state of the lineup — what exists, what each channel's grid is, what is left to
build. It changes every session. This file is the part that outlives any one
channel: read it before founding a channel, consult §2 while building the grid,
and run §4 before calling anything done.

Rules are numbered so a review can cite them. `F` founding, `G` grid,
`C` curation, `V` verification.

---

## 1. Founding — is this a channel at all

### F1 · A tune-in channel needs episodes that stand alone

The organizing principle everything else follows from. ErsatzTV earns its keep
when you don't know what to watch and you turn something on, which only works if
any given episode is enjoyable cold. Nobody tunes into mid-season-2 of *Six Feet
Under*; they select it. Serialized shows belong on-demand.

Every channel in the lineup selects for episodic content whether or not anyone
decided to — sitcoms, westerns, detective-of-the-week, horror anthology,
cartoons, sketch, cooking, DIY, 80s action. It is also why roughly 75% of the
108 unhomed shows are unhomed.

The escape hatch is `annual_show()` Broadcast Mode: one season a year,
chronological, weekly, reruns filling the gap. That converts a serialized show
into appointment TV, which is a *different promise* — "this channel has a
Thursday show" rather than "turn it on whenever". Use it deliberately, not as a
way to smuggle serialized drama onto a tune-in channel.

### F2 · State the identity in one line before building

**Cabes Classic Cinema had been edited five times and never designed.** Modern
film, science fiction, westerns, horror and half the crime shelf each left it in
turn, and no edit ever said what remained. The channel only stopped reading as
residue when it was given a sentence — *Hollywood before the blockbuster* — and
a grid built to that sentence.

If the one-line identity is a list of what the channel is *not*, it is not an
identity yet. See F4.

### F3 · Pick one organizing axis and name it

A channel needs a spine that a viewer could describe without seeing the config:

| Channel | Axis |
|---|---|
| Nightmare Theatre | **The clock** — the channel gets darker as the night goes on |
| Be Kind Rewind | **The week** — Monday is comedy night, Friday is new releases |
| High Noon | **A television spine** — five B&W westerns carry fifteen hours a day |
| Cabes Classic Cinema | **Film history** — the day walks forward and resets at midnight |
| Disney | **Eras of one studio**, dayparted so they never argue |

Nightmare Theatre states the reason plainly: *a horror channel that runs a
slasher at nine in the morning has no idea what it is.* Pool size and daypart
count fall out of the axis; they do not substitute for it.

### F4 · A negative is not a premise

**Boomerang was founded on "pre-1990 as a hard rule"** and closed when Cartoon
Network's restructure moved its vault from the 02:00–06:00 dead zone to the
centre of the channel. Counted against the library afterwards: 22 of 24
pre-1990 animated series were claimed, leaving one show. The disk problems that
looked like the blocker were fixed and it made no difference — the premise was
the problem.

A channel built on "everything not claimed yet" dies the day another channel
grows into its shelf. Re-found it on a positive claim or leave it closed.

### F5 · Let the library decide whether it is TV-led or film-led

High Noon and Nightmare Theatre are the same shape inverted, and neither choice
was taste. High Noon has **946 episodes** across five black-and-white network
westerns against 46 films: television with a film shelf, fifteen hours a day of
TV. Nightmare Theatre has **242 non-animated features against ~370 usable
episodes**, and only two shows that can strip at all: film with a television
spine, seventeen hours of film to seven of TV.

Count the disk before drawing the grid, not after.

### F6 · Budget airtime against pool size

Nothing should cycle faster than about three weeks. Nightmare Theatre's film
keys were sized directly: classic 39 films / 3 h a day, eighties 50 / 2 h,
modern 102 / 6 h, the whole shelf 191 / 5 h. Its two strip shows get one and two
hours, cycling 93 and 87 episodes in a little over six weeks — any more airtime
and they burn through in a fortnight.

The same arithmetic upward: Cabes Classic Cinema's 328 films are a 25-day cycle
at 24 h/day; Be Kind Rewind's 1,530 are 122 days.

### F7 · Serialized-but-wanted becomes an appointment, and appointments are not counted

**How many appointments a channel can carry is not a number.** What governs it
is whether each one has its own night and its own bed — a slot that gates it and
something to run there the other fifty weeks. High Noon carries six, one a
night, with `modern_western_movie` under all of them. Nightmare Theatre carries
nine. Good Times used to break on four, because they shared one slot (see
G5); the four moved to Corncob TV in its 2026-09-01 rebuild.

---

## 2. Building the grid

### G1 · Carry your own timeslot map unless the preset genuinely fits

**Never define a slot that wraps midnight.** The default preset's
`night: (23, 2)` does, and a wrapping slot is entered twice under two different
day labels — so "Sunday night" resolves to two different nights and a
`DailyOrderedCollection` replays its first items across the boundary.

Cartoon Network, Nick, Disney, High Noon and Nightmare Theatre each carry their
own map, mostly for this. Split at midnight instead: `night` 23–24 and
`after_hours` 00–02 as separate slots, each with its own block.

The other half of the rule is fit. Cabes Classic Cinema ran the generic
four-slot `"movies"` preset, and four six-hour blocks is *enough structure to
hold content and not enough to have an identity* — a real part of why the
channel read as a residue. Nightmare Theatre needs nine slots because a
104-minute mean running time halves in a two-hour daypart and disappears in a
six-hour one.

### G2 · Split by running time, not by title

A two-hour daypart holds four half-hours or two hour-longs; mixing them strands
the slot's tail. High Noon puts Gunsmoke, The Rifleman and Wanted: Dead or Alive
in the half-hour strips and Bonanza and Rawhide in the hour-longs.

### G3 · One show per strip

Each of High Noon's morning strips is a single show, so the hour reads as *The
Rifleman is on at eight* rather than *westerns are on*. A strip that means
something is worth more than a strip with more variety in it.

### G4 · Two blocks are only two blocks if they draw different keys

Cabes Classic Cinema's first grid gave First Reel and The Golden Age the same
two keys in a different order — six hours a day against a 49-film pool, a repeat
inside a fortnight. **It was invisible until airings were counted per key rather
than per block.** Fixing it took the silents from 379 airings a year to 105.

Corollary: check what a key actually returns before budgeting a block around it.
`musical_movie` looked like a 24-film pool handed a weekend slot; before 1980 it
is **six films**, and the other eighteen belong to Be Kind Rewind. It is
`classic_musical_movie` now, weighted to a tenth of its block.

### G5 · An appointment needs its own night and its own bed, and the gating comes from the slot

`frequency=["MONDAY"]` alone paces the episode index — it does **not** stop the
appointment airing on other days. The day-gate has to come from the slot: a
weekday dict, the shape `PRIME_BLOCK` uses on High Noon and Mystery Theatre.
Verified over three simulated years on High Noon: every appointment aired on its
own weekday and nowhere else.

**Never stack appointments in one slot.** A `DailyOrderedCollection` that wraps
replays the same episode twice a night. That is the live defect in Good Times'
`MUST_SEE_THURSDAY` — four appointments in a three-hour slot — and it happens at
two just as readily as at four. *Fixed 2026-09-01: those four are single-camera
and went to Corncob TV. Good Times now gates each night with a weekday arm of
`SCHEDULES`, verified over three simulated years — every named night airs on
its own weekday and nowhere else.* Nightmare Theatre's three Saturday limited
series share a slot safely because they are keyed by **season label**, a dict
that resolves exactly one branch a night, not stacked in a collection.

Related trap, same channel: `annual_show(reruns=...)` hangs the bed on the
Program, and a Program that resolves to nothing yields the *whole slot* rather
than passing the turn to the next item — so stacked Programs silently never air.

### G6 · Too short to strip is a feature, not a rounding error

Anything that cannot strip becomes a yearly event: Dragon Ball DAIMA (20 eps),
Attack on Titan Junior High (12), Over the Garden Wall (10), Police Squad! (6),
FLCL (6), Macross Plus (4), the Star Wars *Tales* shorts (6 each). Disney's four
run one per season of the year and between them give 28 Saturdays a premiere.

A pool too small to strip but not special enough to be an event rides a wheel
behind a bigger show instead. **Rawhide's 22 episodes** would be exhausted in
three weeks by a nightly hour; sharing High Noon's evening wheel it surfaces
every other night and stays a treat.

### G7 · Keep the marquee's own pool off the bench leading into it

Disney's noon block (12:00–15:00) is deliberately held **off** the monthly
rotation. Duckburg and Disney Adventure are the two halves of The Disney
Afternoon, so a bench turn at noon would put the marquee's own six shows in the
three hours before it — four hours of one rotation, and the 15:00 appointment
stops meaning anything.

### G8 · A serialized show on a tune-in channel takes two keys

An ErsatzTV content key carries its playback order, so one key is pinned to
whichever order registered first. Chronological on weekdays, shuffled on
weekends is two registrations:

```python
{"WEEKDAY": {"title": "DuckTales", "order": "Chronological"},
 "default":  {"title": "DuckTales", "order": "Shuffle"}}
```

New episodes on weekdays, reruns on weekends. In production on Nick (Avatar,
Korra) and Disney (Gravity Falls, The Owl House, Amphibia).

### G9 · Marathons must be `MarathonSequence`, and holidays outrank them

`find_active_marathon` calls `.pick()` on anything that has one, so a
`RandomCollection` or `OrderedCollection` handed to a `Marathon` collapses to a
single item — the block plays one film, yields, and the rest of the window falls
back to the ordinary grid.

It also returns nothing while `holiday_ctx.is_holiday_season` is true. **A
marathon triggered on 30 or 31 October can never fire**, which is exactly when a
horror channel most wants one. Nightmare Theatre's Halloween is a holiday
*schedule*; Friday the 13th and Krampusnacht stay marathons because their dates
fall outside any holiday season.

### G10 · Year-bound every title query

`movie_by_title` builds a phrase match. `title:"Halloween"` also returns
Halloween II, III, 4 and The Halloween Tree; `title:"Friday the 13th"` returns
eight sequels and the remake; `title:"Gladiator"` returns Gladiator II.
Unbounded, an ordered marathon becomes a shuffle of the whole series. Same fix
`library/scifi.py` uses for Star Trek 1966.

**It bites television harder than film, because show titles are shorter.**
`show_title:"Life"` — the BBC 2009 natural-history series — also reaches
**Homicide: Life on the Street (123 episodes), Rocko's Modern Life (101) and
The Moaning of Life (11)**: 235 episodes of crime drama, Nickelodeon animation
and Ricky Gervais, in a block meant to be Attenborough. Travelers Table found
it in 2026-09-07 and bounds the key with a studio clause.

Two corollaries, both paid for by that key:

* **Bound to the exact studio, not a prefix.** `show_studio:BBC` also matches
  BBC Two, which is why Across the Pond's own `Life` item still carries Life's
  Too Short. `show_studio:"BBC One"` is the fix.
* **Put the bound at the top level, not inside an `OR`.** `key_census` splits a
  query on top-level `AND` only, so a clause nested inside a bracketed group
  reads as unevaluable and the checker silently stops scoring it — the key read
  as six shows instead of seven. Same reason `NOT_ANIMATED` in `queries.py` is
  left unparenthesised: **write the query so the checker can still score it.**

### G11 · Genre tags are not genres

Breaking Bad, Westworld and Cowboy Bebop all carry a Western tag, which is why
`western_tv` returns all three and why High Noon names its five shows explicitly
instead. **The New Yankee Workshop is tagged `Action; Documentary`**, so
`eighties_action_tv` — 1980s plus `genre:action` — had been returning a PBS
woodworking show alongside The A-Team, Knight Rider and Magnum P.I. for as long
as the key existed. Nobody saw it until Makers Corner claimed the show on
2026-09-07 and `same_show_check` reported the pair: **a genre key that quietly
holds the wrong show looks exactly like a genre key that works, until a second
channel wants that show.** Fixed with `NO_DOCUMENTARY`. Tales from the Crypt — the only pre-1990 horror show on disk — is
tagged *Comedy; Crime; Mystery; Science Fiction* and never Horror. When the tag
lies, name the titles.

**The film side is worse, because there the tag is often absent rather than
wrong.** `genre:anime` is on **two films in the whole library** — Laid-Back Camp
the Movie and the 1986 Transformers — so it cannot carry an anime channel's
shelf, and both of those films carry *no* `Animation` tag at all while the 23
Ghibli films carry `Animation` and never `Anime`. Japanorama's four film keys
are explicit title lists closed with `(genre:animation OR genre:anime)` for
exactly this reason.

The same split had a cost nobody had noticed: `NOT_ANIMATED` was
`NOT genre:animation` alone, so **every live-action film pool on the lineup
quietly contained two animated films**, and Be Kind Rewind's `recent_movie` was
drawing Laid-Back Camp the Movie against Japanorama's feature. `NOT_ANIMATED`
now excludes both tags. If a genre key matters, check what the *absence* of the
tag lets through, not only what its presence catches.

### G12 · Silence beats the wrong branding

Cartoon Network ran `filler_content="adult_swim_bumpers"` channel-wide with only
five branded blocks overriding it, so ~14 hours of every 24 — Saturday-morning
Scooby-Doo included — carried Adult Swim bumps. There was nothing to replace it
with, so it now runs none. Filler is a real asset dependency: if the tree for
this channel is empty, ship the channel with no filler and put it on the
acquisitions list.

(Note that `ENABLE_FILLER` and `ENABLE_COMMERCIALS` are off globally, which is
why bumpers never fire outside the branded blocks in the first place.)

---

## 3. Curating across channels

### C1 · The rule

**Overlap between channels is fine. The same title must not air on two channels
at the same time.**

Sharing is often the point, because the two channels mean different things by
it. "Zero shared film pools" was a proxy for this rule that got optimised for on
its own account, and it has been retired — it would have cost the genre channels
164 films and edits to five keys across three channels to enforce something
nobody was checking. In the collision report, section 1 (SHARED KEYS) is **not**
a defect list; section 2 (SIMULTANEOUS AIRINGS) is the number that matters.

The companion rule, stated by the operator: **each channel should feel unique,
varied and themed.**

### C2 · Escalation ladder — cheapest fix first

1. **Different presentation.** Adult Swim runs Tim and Eric, Eric Andre and Dr.
   Steve Brule as *first-run* — chronological, appointment-scheduled, late.
   Corncob TV runs them as *syndication* — shuffled, daytime, drop in anywhere.
   Same show, two presentations, no collision. This is the cross-channel form of
   the chronological/shuffle split in G8.
2. **An hours rule.** Nick at Nite and Good Times share fifteen titles; Good
   Times keeps all of them and simply does not schedule them while Nick is
   airing them. **Write the rule at the resolution the other channel's grid
   actually has.** "Not during 21:00–02:00" was the rule for years and it was
   stricter than Nick: Nick's `nite` is 21:00–24:00 and holds the pre-1970
   seven, its `after_hours` is 00:00–02:00 and holds the 70s shift. Splitting
   the rule the way Nick splits its clock is what let Good Times put M\*A\*S\*H,
   Mary Tyler Moore and Bob Newhart — the 1973 CBS Saturday lineup — into its
   own Saturday prime. A rule coarser than the grid it protects costs airtime
   for nothing.
3. **An era split.** `mystery_crime_movie` (365 films) became
   `classic_crime_movie` (pre-1980, 74) for Classic Cinema and
   `modern_crime_movie` (1980+, 291) for Mystery Theatre. Neither can draw the
   other's film. Reach for this when both channels have an equally real claim on
   one genre.
4. **Eviction.** Only when one channel has an unambiguous claim: science fiction
   and the western shelf both left Classic Cinema whole, and everything Cartoon
   Network was holding for Disney went back.

Do not build `_pure_` exclusion keys reflexively. The existing ones are not
worth unwinding, but they are no longer the default answer to an overlap.

### C3 · Enforce at the key level, not by the grid remembering

Totally 80s and Be Kind Rewind genuinely share the 1980s. It is kept by hours —
Totally 80s runs film 10:00–23:00, so Be Kind Rewind schedules its 1980s shelf
at 02:00–06:00 and 22:00–24:00 — and the decade is unreachable from its
afternoon and prime keys **at the key level**, not because the grid remembers to
avoid it. A convention that lives only in a grid survives until the next edit.

**And the rule has to cover the beds, not just the grid.** Japanorama shares
about 2,450 episodes with Toonami under an hours rule — shared titles daytime
only, 06:00–17:00 — and its grid honoured that exactly. Its *overnight vault*
did not: `THE_REBROADCAST` fills 02:00–06:00 and the obvious thing to fill it
with was the day's own syndication wheel, which put One Piece, Naruto, Dragon
Ball Z and Yu Yu Hakusho opposite Cartoon Network's **Toonami: The Midnight
Run** — 02:00–06:00 on Saturday nights, out of those same four shows — once a
week, every week.

Nothing in the grid was wrong. The bed was built from the wrong half of the
library, and a bed is reached *past* the grid. Vaults, rerun beds and
`fallback_content` all need drawing from owned content, which is why Japanorama's
fallback is `japanorama_vault_tv` and not one of the shared pools.

It took a three-year simulation to see, because no checker looks for it:
`collision_report` groups by key *name*, so Toonami's `{"title": "One Piece"}`
and Japanorama's `one_piece_syndication_tv` read as unrelated pools to it.

### C4 · The era line

The film library splits three ways on two dates already present in `filters.py`
as `PRE_EIGHTIES_ERA` / `MODERN_FILM_ERA`:

| Channel | Era | Films |
|---|---|---:|
| Cabes Classic Cinema | 1920–1979 | 328 |
| Totally 80s | 1980–1989, as its *theme* | 296 |
| Be Kind Rewind | 1980–present | 1,530 |

Classic Cinema and Be Kind Rewind are **disjoint by construction** — the
cleanest relationship two channels on this lineup have. Do not redraw this line
for a new channel; slice within it.

### C5 · Exceptions get named and earned — and check the claimant is one

**The lineup's one standing exemption turned out not to be an exemption.** For
as long as this file has existed, I Love Lucy was documented as a C1 exception
on the grounds that Lucy TV runs it 24 hours a day, so every airing of it
anywhere collided and no hours rule could help. By 2026-09-02 that had grown
into a *three-channel* exemption — Lucy TV, Nick at Nite and Good Times —
written down in three places.

**It dissolved on 2026-09-08 when the operator stated that Lucy TV claims
nothing.** It is a background channel that runs one show; every other channel
schedules as though it did not exist. Remove a non-claimant from the curation
scope and what is left is Nick at Nite and Good Times sharing one title under
Nick's 21:00–24:00 hours rule — **an ordinary C2 rung 2, which the grid was
already honouring.** There was never anything to except.

**So: before writing an exemption, establish that the other channel is
claiming.** A channel that exists is not automatically a claimant. C1 governs
channels that are curated against each other; a channel deliberately outside
that — background television, a single-show comfort loop, anything the operator
wants left alone — constrains nobody, and treating it as a claimant does real
damage. This one cost the lineup two shows: **The Lucy Show (156 episodes) and
The Lucy-Desi Comedy Hour (13)** were reserved for Lucy TV for months, which
meant no channel could take them and Lucy TV was never going to air them. Both
are on Good Times now. **An exemption invented for a channel that does not
claim is a hold on content that nothing releases.**

**The original lesson still stands, because it is about documentation rather
than about Lucy.** An undocumented exception is a collision; a loosely
documented one invites the opposite error. The Good Times rebuild read "Nick at
Nite's I Love Lucy is the lineup's one named exemption" as *excluding* Good
Times and dropped the show off the channel, which nobody had decided. **Name
the channels an exemption covers, not just the title** — and now also name why
each one is a claimant, because that is the sentence that would have caught
this three months earlier.

### C6 · Measure the fix, don't assert it

`scripts/testing/same_title_check.py` resolves both keys' Lucene queries against
`library-movies.tsv` and intersects the title sets, so it answers the literal
question C1 asks. It cleared the crime era-split as harmless — the sets are
disjoint by construction — and simultaneously found that Be Kind Rewind's
`90s_movie` shared **29 titles** with Nightmare Theatre's `horror_movie` and
aired opposite it nineteen times a fortnight.

**The lineup had 28 confirmed same-title collisions that no existing tool could
see.** The two film channels went from 25 colliding pairs to 18 by adding
`NO_HORROR` / `NO_WESTERN` to the decade keys and moving the 1980s shelf off
Mystery Theatre's hours. Some collisions are deliberately left: excluding
science fiction and crime from a general movie channel would remove most of what
a video store stocks. Deliberate is fine — unmeasured is not.

### C7 · Prime is contested; find the empty hour

Be Kind Rewind opens prime at 18:00, and that was measured rather than chosen.
Simulating all twelve channels over a fortnight and bucketing film minutes by
hour showed **18:00–20:00 is the emptiest film hour on the lineup**; from 20:00,
four channels start features at once. The lineup is a schedule, not a set of
independent channels.

---

## 4. Before you call it built

### V1 · 365 continuous days, clean

No gaps, no overlaps, no circuit breakers, no unresolved programs. Every built
channel in the lineup has this recorded in its note in
[channel-plan.md](channel-plan.md), with the programme-play count.

### V2 · Three years if it has appointments

High Noon was re-run over three simulated years to confirm every appointment
aired on its own weekday and nowhere else, and that seasons advanced s1→s2→s3
with Yellowstone looping back after its two on-disk seasons.

### V3 · Run the four offline checkers

```bash
python3 -m scripts.testing.validate_titles <channel>   # every title resolves
python3 -m scripts.testing.key_census                  # every key selects something
python3 -m scripts.testing.same_title_check            # C1, literally
python3 -m scripts.testing.collision_report            # section 2 is the number
```

All four read the manifests in `reference/`, so they run with no ErsatzTV. A
stale manifest makes them wrong in the direction of false alarms — regenerate
when the library changes:

```bash
ETV_MEDIA_ROOT=$HOME/hdpool/data/media \
  python3 -m scripts.testing.library_census --out-dir scripts/reference
```

**And a manifest can be stale by a whole library, not just by a few titles.**
The scanners read the roots named in `library_census.SHOW_ROOTS`, and that was
`tv/` alone until 2026-09-07 — so `youtube/`, 637 episodes across six series
that ErsatzTV could see perfectly well, was invisible to every checker here.
`key_census` reported live keys as EMPTY and `same_show_check` could not have
found a collision involving them. **A scanner that knows about fewer libraries
than the server does reports absence as certainty.** When a new tree is added
to ErsatzTV, add it to `SHOW_ROOTS` in the same pass.

### V4 · Count episodes off disk

`library-tv.tsv` counts `extras/` folders as episodes: Justified reads 117 for
78, Deadwood 51 for 36, The Rifleman 167 for 166. Size every `annual_show()`
against the disk. Yellowstone declares the two seasons that exist rather than
five, because a window opened over episodes that resolve to nothing stalls the
block.

**And a file the scanner cannot see is not on disk, whatever `ls` says.** Ten
of The New Yankee Workshop's twenty-one seasons are `.divx` files, and `.divx`
was not in `library_census.VIDEO_EXTENSIONS`, so **130 episodes and 49.8 hours
were invisible to every checker here** and the show was budgeted as the
smallest shelf on its channel — 63.9 hours against the 113.7 it actually has.
ErsatzTV had indexed all 281 the whole time. This is V3's SHOW_ROOTS lesson one
level down: there a scanner knew about fewer *libraries* than the server, here
about fewer *extensions*, and both report absence as certainty.

**Two corollaries, and the second cost more than the first.**

*A scanner's own report is not evidence about a different scanner.* The note
that first recorded this finding also claimed ErsatzTV could not see the files,
on the grounds that the manifest and the folder agreed at 151 — but the
manifest *is* `library_census` output, so it was the allowlist agreeing with
itself. The server said 281 the moment anyone asked it. **"What does the
manifest say" and "what does the thing that actually plays the files think" are
different questions, and only one of them is evidence.**

*A blind spot is never one show.* This surfaced on one channel, and a sweep of
every extension in the library found **Magnum, P.I.'s entire season 7 in
`.divx` as well** — 138 episodes read against 160, in every pool key reaching
that show on two other channels, for as long as the manifests have existed.
`.webm` was a second gap. **Extension blind spots are silent, library-wide, and
invisible to every other check in this file**, because nothing downstream can
tell "this show has 138 episodes" from "this show has 138 episodes I can see".
Sweep after acquisitions, and keep `VIDEO_EXTENSIONS` at least as wide as
ErsatzTV's own list:

```bash
find tv movies youtube -type f | sed 's/.*\.//' | tr 'A-Z' 'a-z' \
  | sort | uniq -c | sort -rn
```

The same applies to genre pools:
library-analysis.md answers *is there enough content for
a channel*, registry-inventory.md answers *can the
scheduler address it*. Those are different questions and a pool can be large in
one and unreachable in the other.

### V5 · A local simulation is not a build

The stack runs on OMV under docker over SSH. Local logs prove the config
resolves; they do not prove ErsatzTV accepted it. Confirm on the box.

### V6 · Write the channel note

A channel is not finished until [channel-plan.md](channel-plan.md) has its grid,
its counts, its simulation result and — most valuable to the next session — the
shapes that *failed*. Nightmare Theatre's note is the model: three rejected
Saturday shapes, each with the reason, is worth more than the grid that worked.
Update channel-coverage.md for the titles it claims, and
acquisitions.md for what it went without.

---

## Appendix — what no tool enforces

Rules the framework cannot check, and where they can bite:

| Rule | Status |
|---|---|
| C1 same-title | Tooled on both sides — `same_title_check.py` for film keys, `same_show_check.py` for television. Both discover channels by import as of 2026-09-07; the hardcoded list `same_show_check` used to carry had already hidden Travelers Table once. **It over-reported until 2026-09-07 too**: an inline `{"title": ...}` item is resolved to an `auto_gen_*` key whose query the checker cannot read, so it guessed from the key name by substring — and matched `house` inside *This Old House*, putting a collision that does not exist in the CONFIRMED section. Exact title now wins over the substring sweep; the 30-day confirmed count fell from 10,468 to 10,145. **A checker that over-reports gets ignored exactly as fast as one that under-reports.** |
| G5 appointment gating | Only visible by simulating and reading the output |
| G4 blocks drawing the same keys | Requires counting airings per key, which no checker does automatically |
| F6 airtime vs pool size | Hand arithmetic every time |
| G12 filler assets | `bumper-inventory.md` is hand-maintained; missing assets are silent |

The framework has no cross-channel awareness beyond the two report scripts.
Everything above stays a convention held in the block definitions, which is why
it is written down here.
