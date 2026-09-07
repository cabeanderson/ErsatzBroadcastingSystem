# Filler Taxonomy — Proposal

Status: **agreed and applied 2026-08-29.** 6,658 files moved, 7,501 verified present, none lost. Undo manifest retained.
Companion to [bumper-inventory.md](bumper-inventory.md), which this document corrects in four places.

> **How this was verified.** There is no ErsatzTV instance, database, or container on this machine, so nothing here was confirmed against a live index. Every claim about tag behaviour was read from ErsatzTV's source on `main` — the scanner, the fallback metadata provider, the Lucene index writer and the query analyzer, each cited inline. File counts come from a full walk of `/media/filler` on 2026-08-29. One consequence is flagged as open question 7.

---

## 1. The assumption, verified

The prior session's premise was "ErsatzTV derives tags from the folder path, so the folder tree is the tag schema."

**Confirmed for Other Videos**, at source. `ErsatzTV.Core/Metadata/FallbackMetadataProvider.cs::GetOtherVideoMetadata`:

```csharp
string libraryPath = metadata.OtherVideo.LibraryPath.Path;
string parent      = Directory.GetParent(libraryPath)?.FullName ?? libraryPath;
string diff        = Path.GetRelativePath(parent, folder);
var tags = diff.Split(Path.DirectorySeparatorChar).Map(t => new Tag { Name = t }).ToList();
```

Three consequences the premise did not capture, each of which changes the design.

### 1a. Tags are flat, not hierarchical

The path is *split* into independent tags. `bumpers/cartoon network/toonami/naruto` yields four separate tags — `bumpers`, `cartoon network`, `toonami`, `naruto` — with no record of their order or nesting. Two folders with the same name anywhere in the tree are indistinguishable afterwards. `toonami/general` and `cartoon network/general` both produce the tag `general`, which is why `toonami_bumpers` has to AND `tag:toonami` to mean anything.

Two useful corollaries:

- **Depth is free.** Adding a level costs one extra tag and nothing else.
- **Adding a level never breaks an existing query.** `tag:"toonami" AND tag:"naruto"` keeps matching after `naruto/` moves under a new `shows/` parent — the query just becomes less specific than it could be. This is why the registry keys below were safe to ship before the tree is reorganized.

### 1b. `tag` is tokenized; `tag_full` is exact — and we are using the wrong one

Both fields are populated from the same value (`LuceneSearchIndex.cs:1275`) but indexed differently, and `SearchQueryParser.AnalyzerWrapper()` assigns them different analyzers:

| Field | Analyzer | Behaviour |
|---|---|---|
| `tag` | `CustomAnalyzer` — `WhitespaceTokenizer` + `LowerCaseFilter` | split on spaces, lowercased |
| `tag_full` | `KeywordAnalyzer` | whole value, **case-sensitive** |

So `tag:eureka` matches the `eureka` folder **and** the `eureka 7` folder, because both emit the token `eureka`. Same for `tag:naruto` against `naruto` and `naruto shippuden`. Every registry key that addresses one folder should use `tag_full`. Folder names on disk are lowercase, so `tag_full` queries must be written lowercase to match.

There is no stopword filtering or stemming, so `tag:"the room"` is safe as a phrase.

### 1c. Music videos are a different library kind, and derive **no** tags from folders

This is the correction that matters most for The Beat. `GetMusicVideoMetadata` sets `Tags = []`, `Genres = []`, `Artists = []` and derives only a title, from an `Artist - Title.ext` filename pattern. `MusicVideoFolderScanner` calls `ListSubdirectories(libraryPath.Path)` — **immediate children only** — and treats each as one artist.

So under `/media/music_videos`, the folders `hip_hop`, `rock`, `pop`, `oldies`, `dance` are currently being ingested as five *artists*, and the 239 files nested beneath them are attributed to those "artists". The folder tree is not a tag schema here; it is an artist list, exactly one level deep. Genre blocks for The Beat cannot come from folders at all — they need NFO sidecars or ErsatzTV collections.

---

## 2. Corrections to the prior inventory

| Claim | Actual |
|---|---|
| Adult Swim `seasonal` — 0, EMPTY | **233 files** across 8 subfolders: holidays 88, christmas 64, halloween 32, thanksgiving 16, summer 11, spring 9, winter 9, fall 4 |
| Toonami `marathon`, `seasonal` — 0, EMPTY | `marathon/cowboy bebop` has 18 (+1 in `intro/`); `seasonal` is genuinely empty |
| `commercials/90s` is "mostly 2000s UK adverts" | Correct on country, **wrong on decade.** `s2006`–`s2013` is the ripper's season numbering (episode = MMDDHH), not the advert date. Reading the descriptions instead: 57 are explicitly 1990s, 2 are 1980s, 1 is 2000s, 50 carry no year. The folder is correctly named `90s`. |
| Toonami tree fully accounted for | **93 files sit loose at `toonami/` root**, tagged `toonami` and nothing else |

Also: Adult Swim `marathon/astroboy` vs Toonami `astro boy` are inconsistent spellings and produce different tags.

---

## 3. Proposed taxonomy

One rule, from which the rest follows:

> **Every leaf folder is a schedulable pool, and no folder holds both loose files and subfolders.**

A file loose at a level that also has subfolders picks up no leaf tag, so it can only be addressed as "everything under the parent" — which is exactly why 93 Toonami files and 5,316 Adult Swim files are currently unaddressable at any useful granularity. The fix is a `general/` sibling wherever that happens.

The path reads **network → brand → function → subject**.

```
filler/
  bumpers/
    cartoon network/
      general/                       0  ← empty; CN daytime branding is a real gap
      adult swim/
        intro/                      29
        outro/                       5
        bumps/
          general/                ~4,600  ← was loose at bumps/
          schedules/                 134
          tagged videos/             191
          pool/                       35
          fan service/                10
        shows/                              ← NEW: the auto-sortable 716
          king of the hill/          107
          aqua teen hunger force/     74
          robot chicken/              53
          metalocalypse/              52
          ... 27 more with >=5 files
        seasonal/
          christmas/ halloween/ thanksgiving/ holidays/
          winter/ spring/ summer/ fall/
        marathon/
          general/                    25  ← was loose at marathon/
          astro boy/                   6  ← renamed from "astroboy"
          cowboy bebop/               13
          yu yu hakusho/              13
        april fools/                  46
        the room/                     43
        childrens hospital/           31
      toonami/
        intro/                        84
        outro/                         6
        general/                     111  ← 18 existing + the 93 loose at toonami/
        bumps/                         3
        shows/                              ← the 33 existing per-show folders move here
          naruto/ inuyasha/ cowboy bebop/ ...
        marathon/
          cowboy bebop/               18
  commercials/
    uk/
      80s/                             6
      90s/                           104
        toys/ beer/                    6
    us/                                     ← empty, ready for US spots
  marathons/
```

### Why these shapes

**`shows/` as an explicit level.** It buys a "any per-show bumper" pool (`tag_full:"toonami" AND tag_full:"shows"`), and it separates subject folders from function folders so that a future show named e.g. *Marathon* cannot collide with the `marathon/` function. Because tags are flat and AND-ed, it does not invalidate the 33 per-show keys already in `sources.py`.

**Show folder names should match library titles exactly.** This is the highest-leverage decision here, because of a mechanism already in the code. `dispatcher.py::play_smart_bumper` builds:

```python
bumper_query = f'type:"other_video" AND tag:"{title}" AND {" AND ".join(tag_queries)}'
```

with `required_tags` defaulting to `["bumpers"]` — and `bumpers/` is a real folder in this tree, so that tag already exists on every file. `title` is extracted from the scheduled content's own query. So **if a show's bumper folder is named exactly as its library title, per-show bumpers fire automatically with no registry key at all.** That turns the taxonomy from a filing exercise into working behaviour, and it argues for these renames:

| Current folder | Rename to | Reason |
|---|---|---|
| `full metal alchemist` | `fullmetal alchemist brotherhood` | library title is *Fullmetal Alchemist Brotherhood (2009)* |
| `sym bionic` | `sym-bionic titan` | truncated |
| `sword art` | `sword art online` | truncated |
| `astroboy` (AS) | `astro boy` | matches the Toonami spelling |
| `eureka` + `eureka 7` | **needs your call** — see below |

**`commercials/uk` + `commercials/us`.** The decade folders were never the problem; the country was. Splitting on nationality first means a US-branded channel and Across the Pond (104) can draw from the same tree without either getting the wrong accent, and it preserves the decade tags underneath.

---

## 4. Auto-sorting: what is recoverable, honestly

Measured against the 5,316 loose files in `adult swim/bumps/`, matching a 74-pattern show vocabulary over filenames normalized to space-separated tokens.

| Axis | Files | Share |
|---|---:|---:|
| Show-identifiable | 716 | 13.5% |
| Function-identifiable (schedule / promo / social / PSA / holiday) | 738 | 13.9% |
| Union of both | ~1,300 | **~25%** |
| **Must stay generic** | **~4,000** | **~75%** |

Ambiguous matches (two shows in one filename): 5. Effectively zero.

Top show clusters: king of the hill 107, aqua teen hunger force 74, robot chicken 53, metalocalypse 52, inuyasha 35, squidbillies 33, futurama 27, superjail 26, venture bros 26, family guy 22, delocated 20, boondocks 20, eagleheart 18, space ghost 16, china il 15, tim and eric 14. 31 shows clear 5 files; the tail below that is not worth a folder.

**The 75% is not a failure of the regex — it is what Adult Swim bumps are.** The unmatched set is network voice, not show promos: `Millenials_Buy_Impulsively`, `Algebra_Shattered_Our_Faith`, `AS_Complaint_Line_Number`, `Found_Aquaman_on_Drive_Thru`. There is no show to sort these under, and no amount of pattern work will change that. They belong in `bumps/general/` and they are perfectly good as an undifferentiated late-night pool — which is exactly how they were used on air.

### Method

Three passes, each reviewable before the next:

1. **Generate a manifest**, not moves — a TSV of `current path → proposed path → matched pattern`. Nothing touches disk.
2. **Review the manifest**, especially the ambiguous and the just-above-threshold cases. Correct by editing the TSV.
3. **Apply** with `git mv`-style logging so any move is reversible from the manifest alone.

A rescan is required after any move, since these tags are fallback metadata computed at scan time.

---

## 5. Commercials

Not a re-dating job. `commercials/90s/` keeps its name; the tree gains a nationality level above it, and the 104 loose files move to `commercials/uk/90s/`. The 6 in `80s/` move to `commercials/uk/80s/`. Both sets are British.

The payoff is that these 110 spots stop being idle: **Across the Pond (104)** is the channel that actually wants them, and it can reach them with `tag_full:"commercials" AND tag_full:"uk"` without a US channel ever drawing a Dime Bar advert.

### Categorised 2026-08-29

The path is now **country / decade / audience-gate / product**, so any combination of the four is an AND of flat tags. The gate level is the one that drives scheduling.

| Gate | Files | |
|---|---:|---|
| `alcohol/` | 11 | `beer` 9, `spirits` 2 — must never reach a kids daypart |
| `kids/` | 37 | `cereal` 9, `confectionery` 11, `snacks` 8, `toys` 7, `drinks` 2 |
| `christmas/` | 6 | seasonal-block fodder |
| `general/` | 62 | `confectionery` 18, `food` 16, `drinks` 7, `snacks` 6, `retail` 6, `household` 4, `tech` 2, `leisure` 2, `psa` 1 |

**`commercials_family_safe_spot`** is the key a kids or daytime channel should use — `NOT tag_full:"alcohol"`, resolving to 105 of 116.

Corrections made in the same pass:

- Three decade misfiles: *British Telecom* (1988) and *Country Life butter* (1984) to `80s`, *Gillette Venus* (2000) to `00s`.
- Two files were never British: `budweiser wassup` to `us/90s`, `7 UP (Australian ad, 1992)` to `au/90s`. The Fosters ad names Mexico but is a UK commercial shot abroad, so it stayed.
- No byte-identical duplicates exist. The `Pog`/`POG`, Boddingtons, Dairylea and John Smith's pairs are genuinely different ads.

One deliberate call: **`Malibu Mobile Phone Ad` is filed under `alcohol/spirits`** despite the ambiguous name. A false alcohol tag only withholds it from kids blocks; the opposite error would air rum in one.

The empty `general/` and `seasonal/` subfolders under the old `90s/` were removed, but every empty *decade* and *country* folder is kept as scaffolding.

---

## 6. Registry keys — **done**

`scripts/library/sources.py` FILLERS went from 8 keys to 65. All of them address folders that exist on disk today and that this proposal leaves in place, so they work now and survive the reorganization.

- 33 `toonami_<show>_bumpers` keys — the ~940 per-show bumpers, previously reachable by tag but referenced by nothing
- `adult_swim_outro` — the 5 outros that had no key
- 8 `adult_swim_seasonal_*` keys — the 233 files the inventory recorded as empty
- Sub-pools: `adult_swim_schedules`, `adult_swim_tagged_videos`, `adult_swim_pool`, `adult_swim_fan_service`
- Marathon keys for both networks, `toonami_all_bumpers`, `commercials_80s_spot_folder`
- A `filler_source(*folders)` builder, matching the file's existing builder-function style, emitting `tag_full` so single-folder keys stop colliding

`toonami_bumpers` still resolves to 21 files. It cannot improve until the 93 loose Toonami files move into `general/`.

`python3 -m scripts.testing.validate_titles` → 1 problem, the pre-existing `Cunk` ambiguity in `library/british.py:178`. No new findings.

---

## 7. What it takes to make filler actually fire

> **Updated 2026-09-05.** Gate 2 was rebuilt; the paragraph below the table is the
> current state. See [interstitial-policy.md](interstitial-policy.md) for the design.

Four independent gates, two of them still shut. `filler_content="adult_swim_bumpers"` is already set on Cartoon Network and does nothing on its own.

| # | Gate | State | Fix |
|---|---|---|---|
| 1 | `ENABLE_FILLER = False` (`settings.py`) | shut | `enable_filler=True` in CN's `ScheduleConfig`. Gates the hour-boundary filler at `dispatcher.py`, the only consumer of `config.filler_content`. |
| 2 | `SMART_BUMPERS = "none"` (`settings.py`) | shut, **but now per-channel** | Three modes — `"none"` / `"some"` / `"all"` — resolved by `resolve_smart_bumpers()` through the same Program > Block > Channel > Global cascade as filler. Set `smart_bumpers=` on a `ScheduleConfig`, `Block` or `Program`. |
| 3 | `config.bumpers` never set | unset | CN passes no channel-level `bumpers=`, so `resolve_bumper_collection` falls through to `None`. Individual blocks in `animation.py` do set `bumpers=`, so block-level branding works and channel-level does not. |
| 4 | `enable_bumpers=True` | **already set** on CN | drives `play_block_intro` / `play_block_outro` only |

Note that `fill_to_boundary`'s `enabled` parameter defaults to `True` and `blocks.py` never passes it, so a block with `fill_strategy="fill"` fills regardless of `ENABLE_FILLER`. Gate 1 governs the hour-boundary path specifically.

**What changed in gate 2.** It was a module-level `ENABLE_SMART_BUMPERS` bool read directly by the dispatcher, which made the choice lineup-wide: every channel or none. That could not express "Cartoon Network yes, Good Times no", and it could not express Japanorama at all — 1,249 of the 1,251 files in the Toonami tree are literally named `Toonami_*`, so a generic fallback there puts a Cartoon Network ident on a Japanese broadcast-day channel. The `"all"` mode exists for exactly that case: per-show bumpers where one genuinely belongs to the show, and silence everywhere else.

The per-show query was also corrected from `tag` to `tag_full` in the same pass. Both fields carry the folder name, but §1b applies: `tag` is whitespace-tokenized, so `tag:"naruto"` matched the `naruto shippuden` folder too. Titles are lowercased at the call site because `tag_full` is case-sensitive and folder names on disk are lowercase.

Recommended order is unchanged for gate 1, and gate 2's precondition is now met for films and for the 32 Toonami show folders whose names already match library titles.

---

## 8. Open questions before any file moves

1. **`eureka` (14) vs `eureka 7` (23).** Toonami aired *Eureka Seven*. Are these one set that got split, or is `eureka` something else? If one set, merge to `eureka seven`. **Cannot determine from filenames alone.**
2. **`shows/` level — in or out?** It buys an "any per-show bumper" pool and collision safety, at the cost of one more level. Out is defensible; the tree is already unambiguous.
3. **Show-title renames** — confirm the four in §3. They are what makes smart bumpers work without registry keys.
4. ~~**`fox kids/`** is empty and its keys are undefined over it.~~ **CLOSED 2026-09-05 — deleted.** The empty tree is gone; no key in `sources.py` referenced it.
5. **The 5-file threshold** for cutting a show folder out of `bumps/general/`. 31 shows clear it.
7. ~~**Is `filler` itself a tag?**~~ **CLOSED 2026-09-05 — yes.** The library is
   local, rooted at `/media/filler` inside the container (host
   `/media` mounts to `/media:ro`), added as Other Videos.
   So every item carries `filler` as its first tag, and the NFO sidecars
   generated on 2026-09-05 emit it correctly. Original question below.

   **Is `filler` itself a tag?** The relative path is computed from the *parent* of the ErsatzTV library root, so the root folder's own name becomes a tag on every item. If the library is rooted at `.../media/filler`, everything carries `filler` and it is free namespacing; if it is rooted at `.../media`, the first tag is `media` instead. Not determinable from disk — it depends on how the library path is configured in ErsatzTV, which is not on this machine. None of the 65 keys depend on it either way, but it is worth checking on the next scan.
8. **Music videos** are a separate problem with separate rules (§1c) and no folder-tag lever at all. Worth its own pass rather than being folded into this one — the immediate defect is that 5 genre folders are being ingested as artists, plus ~40 artist folders with trailing spaces in their names.

---

## 9. Movie interstitials — trailers and extras

Status: **built and applied 2026-09-04.** 8,809 hardlinks, 0 bytes of disk. Built
by `scripts/filler/sync_interstitials.py`, which is re-runnable and is the only
thing that should ever write to this tree.

### Why none of it was reachable

The library holds 2,260 trailers across 2,012 film folders and 6,559 extras —
1.2TB — and ErsatzTV could see none of it. `MovieFolderScanner` excludes extras
two ways, and only one of them is the obvious one:

1. A filename filter. `MovieFolderScanner.cs:133` drops any file whose stem ends
   in one of `ExtraFiles` (`behindthescenes, deleted, featurette, interview,
   scene, short, trailer, other`), so `…-trailer.mp4` never survives.
2. **The recursion gate.** Subfolders are enqueued *only* when the current folder
   yielded no video files. A film folder containing the film therefore never has
   its `extras/` or `trailers/` walked at all.

The natural assumption — that `ExtraDirectories` (`extras`, `trailers`,
`specials`, …) is a folder blocklist — is wrong. Grepped repo-wide, that constant
is referenced **only** by `MovieFolderScannerTests.cs:867`, as the `ValueSource`
of `Should_Ignore_Extra_Folders`. It is a test fixture. The production exclusion
is the recursion gate, which means **the folder names carry no magic**: nothing
will skip a folder called `trailers/` in a library of a different kind.

That is what makes this possible. `OtherVideoFolderScanner` recurses
unconditionally and applies no `ExtraFiles` filter, so an Other Videos library
sees everything beneath it.

### The tree

Pointing Other Videos at `/media/movies` would ingest all 2,072 features a second
time, so the farm is a parallel tree. Hardlinks, not copies: 1.2TB against 3.3TB
free, and both trees sit on the same export. Free space was unchanged after the
run, which is the only proof that matters.

```text
filler/
  interstitials/
    trailers/            2,261     <- 2,971 per-film folders across all types
      1920s/ … 2020s/
        a clockwork orange/
        alien/
    extras/              6,279
    deleted scenes/         85
    interviews/             78
    behind the scenes/      65
    featurettes/            28
    shorts/                 13
```

Every level earns its place. Because tags are flat (§1a), one tree answers two
different questions at once:

- `tag:"trailers" AND tag:"1970s"` — an era pool for a film channel.
- The **film-title level** is what `dispatcher.play_smart_bumper` needs. It
  interpolates `type:"other_video" AND tag:"{title}" AND tag:"bumpers"`, and with
  `required_tags=["trailers"]` it resolves a film's *own* trailer as its pre-roll
  **with no registry key at all** — the same mechanism §3 identified for per-show
  bumpers, now with matching titles. Titles are un-inverted (`Knight's Tale, A` →
  `a knight's tale`) precisely so they match the library title the dispatcher
  interpolates.

Trailer coverage against the film-era line: **425 pre-1980, 351 in the eighties,
1,485 from 1990 on**. `acquisitions.md` calls interstitials the largest single
thing Cabes Classic Cinema and Be Kind Rewind are missing; they were already on
disk. Genre cross-referenced against `library-movies.tsv` (2,008 of 2,012 films
matched) reaches the two channels that own **nothing**: Horror 240, Western 46 —
plus Science Fiction 410 and Fantasy 324 for the channel not yet built.

### Why the types are not flattened into `extras/`

The folder is the only length signal there is, and the spread is an order of
magnitude:

| Type | Median | Max |
|---|---|---|
| trailers | 2m11s | 2m51s |
| deleted scenes | 1m38s | 29m38s |
| featurettes | 6m55s | 43m17s |
| behind the scenes | 6m58s | 48m03s |
| shorts | 8m34s | 36m34s |
| interviews | 12m56s | 49m45s |

Flattened, a 50-minute interview shares a pool with a 98-second deleted scene.
Trailers are the outlier worth isolating: a 2m11s median against a 2m51s max is
tight enough to schedule against without peeking at durations.

### Case is normalised in the script, not on disk

71 source dirs are capitalised — `Extras` 30, `Trailers` 17, `Interviews` 12,
`Deleted Scenes` 5, `Featurettes` 4, `Shorts` 2, `Behind the Scenes` 1 — plus one
singular `trailer`. **`Featurettes` has no lowercase form at all**, so a
lowercase-only match misses the type entirely.

This matters for the reason §1b gives: `tag_full` is indexed with a
`KeywordAnalyzer` and is case-sensitive, so a stray `Extras/` would yield
`tag_full:"Extras"` and never match a lowercase query. The script matches sources
case-insensitively and always writes destinations lowercase, which fixes it
without renaming 71 directories or triggering a Jellyfin rescan. Renaming the
source tree would be cosmetic — Jellyfin's extras matching is case-insensitive
too.

One true collision exists: `Animatrix, The (2003)` holds both `Extras` and
`extras`. No filenames overlap, so the two merge into one destination folder.

### What the traversal had to learn

A depth-limited read silently dropped 237 files. Three findings, all now handled:

- **22 dirs nest a subtype inside `extras/`** — `Whiplash (2014)/extras/Deleted
  Scenes`, and one pathological `extras/extras`. A nested known type reclassifies
  what is under it.
- **236 files sit three and four levels down** in free-form disc groupings:
  `Mission Control`, `Outtakes - Day 2`, `Press Timeline - 16 Interviews &
  Conversations`. These are not types; their names fold into the destination
  filename.
- That folding is not cosmetic. **`Panic Room (2002)` ships seven same-named
  files** (`B-Roll.mkv`, `Dailies.mkv`, `Storyboards.mkv`, …) across different
  grouping folders. Discard the grouping and they collide; they now read
  `Sequence Breakdowns - The Phone Jack - B-Roll.mkv`.

Coverage was verified against an independent `find`: 8,809 planned links against
8,810 files on disk, the difference being `.deletedByTMM/` — tinyMediaManager's
trash, which ErsatzTV's `ShouldIncludeFolder` skips for the same dot-prefix
reason the script does.

### Staying in sync

The farm is derived state, so the script reconciles rather than appends, and all
three paths were tested end to end with a scratch film folder:

| Event | Behaviour |
|---|---|
| New disc ripped | linked |
| Disc **re-ripped** | **relinked** |
| Film deleted | pruned, empty dirs removed |

The middle row is the one with teeth. A re-rip writes a **new inode at the same
path**, so a script that only asks "does the destination exist?" leaves a link
serving stale content *and* pinning the replaced file's blocks forever. The
script compares `st_ino` on both sides and repairs. Re-running is otherwise a
no-op, and dry-run is the default.

Scheduled by a `systemd --user` timer at 04:30 daily, `Persistent=true`. Caveat:
`Linger=no` on the account, so it only fires while logged in —
`loginctl enable-linger cabe` (root) removes that.

### Still gated

The tree is inert until the ErsatzTV side is done, and none of it is reachable
from this machine (no read API beyond `/api/channels`; the DB is root-only):

1. **Confirm the Other Videos library root.** This is open question 7. Rooted at
   `/media/filler`, every item here also carries `filler` and the existing
   `filler_source()` keys keep working; rooted at `/media`, the namespacing tag
   is `media` instead.
2. `ENABLE_FILLER = False` (`settings.py:44`) — gate 1 of §7.
3. `ENABLE_SMART_BUMPERS` is what fires the per-film trailer. Still a
   module-level global, so flipping it is lineup-wide — but §7's precondition
   ("once show folder names match library titles") is now met for films.

Genre is deliberately absent. Adding a genre level would mean hardlinking a
multi-genre film's trailer into several folders, which registers as several
items and skews shuffle. Other Videos reads NFO sidecars
(`OtherVideoNfoReader` supports `<title> <year> <plot> <genre> <tag>`), so genre
belongs there — and would replace filename titles with real ones in the guide.

> **Source note.** `ErsatzTV/ErsatzTV` now redirects to **`ErsatzTV/legacy`**;
> the paths cited throughout this document resolve under that name.

---

## 9a. NFO and folder tags are mutually exclusive — verified 2026-09-05

§9 above says genre "belongs in NFO sidecars". That is right, and it is more
dangerous than it reads, because **an NFO does not add to the folder tags. It
replaces them.**

`ErsatzTV.Core/Metadata/FallbackMetadataProvider.cs::GetOtherVideoMetadata`
does not merge — it assigns, and clears its neighbours:

```csharp
metadata.Tags    = tags;   // the split folder path
metadata.Genres  = [];
metadata.Actors  = [];
metadata.Studios = [];
```

and `ErsatzTV.Scanner/Core/Metadata/OtherVideoFolderScanner.cs::UpdateMetadata`
selects between them on `MetadataKind`, refreshing sidecar metadata when the
current kind is `Fallback`. The two are alternatives, not layers.

**Consequence.** The moment any filler file gains an NFO, every folder-derived
tag on it stops existing — and every `filler_source()` key in
`library/sources.py` is an AND of exactly those tags. A single hand-written NFO
dropped next to a commercial silently removes it from
`commercials_us_spot`, `commercials_90s_spot` and everything else.

**What the reader accepts.**
`ErsatzTV.Scanner/Core/Metadata/Nfo/OtherVideoNfoReader.cs` handles roots
`episodedetails`, `movie`, `musicvideo`, and elements `title`, `sorttitle`,
`outline`, `year`, `mpaa`, `premiered`, `plot`, `genre`, `tag`, `studio`,
`actor`, `credits`, `director`, `uniqueid`. **`<tag>` repeats and accumulates**,
which is the whole reason NFO is worth the risk: it is how a file says "and".

**The resolution adopted.** NFO is *compiled*, never hand-written —
`scripts/filler/generate_filler_nfo.py`. It re-emits every path segment as a
lowercase `<tag>` (so no registry key changes), then appends what folders
structurally cannot carry. Folders keep the single-valued navigation spine —
country, decade, gate — and stay the source of truth. `--verify` proves the
floor holds and is the only check that matters; it passed 4,128/4,128 on
2026-09-05.

Casing is load-bearing: `tag_full` is a KeywordAnalyzer field (§1), so
`<tag>Commercials</tag>` would index as `tag_full:"Commercials"` and match
nothing while looking correct in the file.

---

## 9b. The NFS client will lie about directory contents

Found the hard way on 2026-09-05, while verifying the NFO write above.

`/srv/library` is `nfs4` with default attribute caching. After a large
write burst, **`readdir` served a stale listing indefinitely**: a directory
reported one entry while `stat` on a file inside it succeeded and returned the
correct size. Files created seconds earlier were invisible to `ls`, `find`,
`os.listdir` and `os.scandir` alike, in any spelling of the path, because the
directory's cached mtime never advanced (it read 09:58 at 17:08).

`touch <dir>` forces revalidation and the entries appear at once.

Two consequences worth carrying:

1. **Any file count taken from this machine over NFS is provisional.** Re-touch
   the tree before trusting one. The counts in this document were re-taken
   after a `find … -type d -exec touch {} +` across `/media/filler`.
2. **This is a plausible failure mode for ErsatzTV's own scanner**, which
   enumerates directories over the same kind of mount. A scan that runs against
   a stale listing will not see new files and will report no error.

---

## 10. US commercials — acquired 2026-09-05

Status: **208 spots filed**, from two archive.org items. `commercials/us/` is no
longer the empty scaffold §3 left it as. Filed by
`scripts/filler/file_us_commercials.py`.

### What was actually acquired

The larger item advertises itself as a commercial collection. By duration it is
mostly not one:

| Band | Files | Hours |
|---|---:|---:|
| Single spot (≤75s) | 128 | 1.2 |
| Ad break (75s–7m) | 43 | 2.0 |
| **Off-air reel (>7m)** | **56** | **29.7** |

**Ninety percent of the runtime is in 56 reels**, the longest a 131-minute
`1999-2000 NBC Commercials`. Those are tape recordings, not interstitials, and
they were **not filed** — they remain staged under `.staging/us_commercials`
pending a decision on whether silence-and-scene splitting is worth a session. It
plausibly yields well over a thousand spots, which would dwarf everything else
in this tree.

Two counting traps are worth recording, because the item's file list misleads:

- **IA derivatives inflate the count.** `X.mp4` and `X.ia.mp4` are the same
  commercial. Filtering on the API's `source` field gives 227 genuine originals,
  not the 254 a naive extension match reports.
- Picking one file per spot — the h.264 derivative where it exists, the original
  otherwise — is 13.56 GB rather than 16.16.

The second item (37 spots, explicitly public domain) is the better filler
despite being a fortieth of the size: 10–89s durations, median 30s, all genuine
single spots.

### Two new gates

**`tobacco/`.** The gate vocabulary had `alcohol/` and nothing for cigarettes,
which does not survive contact with 1950s television. Six of the 37 public-domain
spots are tobacco ads: Chesterfield, L&M (two), Roi-Tan cigars, Philip Morris
(Lucille Ball and Desi Arnaz) — and **Winston, in a Flintstones cartoon**.

That last one is why this section exists. It is animation, so any heuristic
reading "cartoon" as "children's content" files a cigarette commercial into a
kids block, and the filename (`ctvc_FLINT.AVI`) says nothing. It was identified
only by extracting its closing frame, where the Winston pack appears over
Bedrock. **Filenames were not sufficient for either the Winston or the L&M
spots.**

**`uncategorized/`.** 122 of the 209, and the most important gate here.

### A gate is a determination, never a residue

The first filing pass got this wrong and is worth recording as a mistake. It
sent anything matching no kids or mature keyword to `general/` — so `general/`
meant "no keyword fired", which is not evidence of anything. Half of what landed
there was not a categorized commercial at all: network promos (Dolly, Wings,
*Sister Sister*), movie TV spots (*The Wiz*, *Mystic Pizza*), and PSAs. A promo
also tells you nothing about the rated content it advertises.

The rule, corrected: **categorize only when the category is clear — a named
consumer brand, a named children's property — and send everything else to
`uncategorized/`,** which no daytime or kids key draws from. Channels that want
the whole reel ask for it by name. The brand list in
`scripts/filler/recategorize_commercials.py` is deliberately explicit rather
than heuristic: "clear" means the product can be named, so the list *is* the
definition of the gate.

Re-gating on that basis moved 126 files and cut `general/` from 102 to 47.

Three traps the second pass had to handle, each caught by a check rather than by
reading the code:

- **Frame evidence outranks any filename rule.** A regex over `ctvc_RICECRPS`
  and `ctvc_KAISER` cannot know they are Rice Krispies and a *Maverick* mail-in
  premium. The public-domain set keeps its determinations in an explicit map.
- **Mature themes must override brand matches.** `Pepsi Cool Sex Cans` carries a
  brand that would otherwise have promoted it into daytime.
- **An off-air break is not about the show it was recorded from.**
  `Commercials (from ABC's Brady Bunch Hour)` is 28 minutes of 1977 advertising;
  gating it as children's content on the title is exactly the Winston error in
  another costume. A `(from <network>)` guard forces those to `uncategorized`
  whatever else matches.

Both new gates are excluded from `commercials_family_safe_spot` and
`commercials_uk_family_safe_spot`, which previously excluded only `alcohol`.
This **changes the meaning of an existing key** — it now returns 185 rather than
239 — and is the §5 rule applied consistently: a false gate withholds a spot
from daytime, the opposite error airs a Winston ad in a children's block.

### The tree

```text
commercials/us/
  50s/   general 24  kids  3  tobacco 6  uncategorized  4   <- dated from frames
  60s/   general  1  kids  3             uncategorized 10
  70s/   general  3  kids  3             uncategorized  8
  80s/   general 11  kids  8  christmas 1  uncategorized 32
  90s/   general  8  kids 11             uncategorized 52  (+1 alcohol/beer)
  00s/                kids  3  christmas 1  uncategorized 14
  10s/                                   uncategorized  2
```

209 files, of which **122 are uncategorized — 58%**. That number is the honest
shape of the collection, not a failure of the pass.

The 50s decade is the outlier at 89% categorized, and the reason is simply that
those 37 were watched: frames were extracted and read. Every other decade was
classified from filenames alone, which is why so little of it clears the bar.
The gap between the two is the argument for viewing the rest.

The 50s decade is also the only one dated by inspection — the item carries no
date metadata at all, and the frames place it 1950s to early 60s (a DeSoto
dealer card, DeSoto having died in 1961; a *Zorro* title card; a *Maverick*
mail-in premium; all black-and-white). A few are certainly early 60s and are
filed under `50s` anyway. Every other spot is year-prefixed at source, so its
decade is exact.

### Registry

`FILLERS` gains 37 commercial keys (27 → 64), all verified against files on
disk: none resolves to zero. The per-decade key lists differ by gate because
they track what is actually there — no decade after the eighties has a spot
whose product is clear enough for `general`.

`commercials_us_spot` returns 209 and `commercials_us_family_safe_spot` returns
80 — the difference being 6 tobacco, 122 uncategorized and the one pre-existing
Budweiser spot.

`python3 -m scripts.testing.validate_titles` → no problems.
