# Interstitial Acquisition — where the material is and how to get it

Status: **opened 2026-09-05.** Companion to
[interstitial-policy.md](interstitial-policy.md), which ranks eight acquisition
gaps in its §8 and names the search term that unlocks them. It does not say
where to point it. This is that half, plus the split of the staged reels that
its §8 ranked first.

Everything below was verified against archive.org's `advancedsearch.php` on
2026-09-05 via `scripts/filler/scout_archive.py`. Item sizes and download counts
are as reported by the API on that date.

---

## 1. What shipped in this pass

### The 56 staged reels are split — §8's item 1, the one that cost no acquisition

`scripts/filler/split_reels.py`. Dry-run by default, cache-backed, re-runnable.

| | |
|---|---:|
| Reels staged | 56 |
| Twin containers resolved to one | 4 pairs |
| Reels actually split | **52** |
| Staged runtime | 28.6 h |
| **Spots produced** | **3,721** |
| Runtime kept | 26.1 h |
| Runtime dropped | 2.6 h |

The policy estimated "well over a thousand". It is **3,721**, which is 11× the
existing 324-file US commercial tree and makes the split the single largest
addition to the filler library to date — from material already on disk.

By decade, filed to `commercials/us/<decade>/uncategorized/`:

| Decade | Spots |
|---|---:|
| 70s | 70 |
| 80s | 1,071 |
| 90s | 1,605 |
| 00s | 526 |
| 10s | 449 |

Segment lengths, against the shapes a US spot actually comes in:

| Length | Count | Reading |
|---|---:|---|
| under 10s | 198 | idents and station tags |
| 10–20s | 1,393 | the 15-second spot |
| 20–40s | **1,785** | the 30-second spot — the bulk |
| 40–70s | 271 | the 60-second spot |
| 70–125s | 74 | promo blocks and multi-spot pods |

That distribution is the correctness check. Real US broadcast advertising is
overwhelmingly 30s with a 15s second place, and the detector reproduced that
shape without being told to — 85% of segments land in the two standard slots.

**How the boundaries were found.** `blackdetect` and `silencedetect` in one
decoding pass, unioned. Calibrated against `1970s TV Commercials.mp4`, a clean
30-second reel with a knowable right answer: black alone found 13 of 14
boundaries and missed the one at 211.9s where the tape cuts with no black
field; silence alone found that one and missed others where a spot ends on a
jingle. Cuts are placed at the midpoint of a black interval, which keeps black
frames out of both neighbours — verified, 13 of 13 segments open on picture.

**What was dropped, and why it is not a loss.** 1,493 segments. 1,472 of them
are under 8 seconds — the black-and-silence gaps *between* spots, correctly
discarded. Only 21 are over 125 seconds, i.e. two spots with a boundary the
detector missed. The reels stay staged, so a retune recovers them.

### Acquisition, tiers 1–4 — fetched and split

Approved and executed 2026-09-05. **3.4 GB downloaded, not the ~16 GB the item
sizes implied** — `fetch_archive.py` takes the h.264 derivative, which on this
material runs a fifth to a tenth of the advertised item size.

| What | Result |
|---|---|
| `cartoon-network-city-complete-bumper-archive` | **282 bumpers** into `bumpers/cartoon network/general/`, which held **0** before. Gap #7 closed. |
| `Televisi1960` | 31 spots into `commercials/us/50s/` — public domain, and the first 1950s–60s material acquired |
| Disney Afternoon 1992-07 (WOC), Vista 1995-12 Disney Christmas, ABC Sat AM 1993 + 1986 (WOC) | **239 spots** total across 50s/80s/90s |
| 4 Toonami compilations | **153 segments held in `.staging/toonami_review/`**, deliberately *not* filed — see below |

Two findings from doing it:

**WOC captures are mostly programme.** 6.0 hours staged yielded 2.4 hours of
spots. That is not a failure — the over-length filter is correctly discarding
the shows and keeping the breaks — but it means a WOC item's *listed* runtime
overstates its yield by roughly 2.5×.

**Two Toonami compilations are hard-cut and barely split**: `2001 Best of
Toonami Bumpers` produced 6 segments from 265 MB and `2001-08 …` produced 3 from
58 MB, because they are edited with no black or silence between bumpers.
`blackdetect`/`silencedetect` cannot see those boundaries at all. Recovering
them needs scene-change detection (`select='gt(scene,0.4)'`), which is a
different detector and is not built.

The Toonami segments are held in review rather than filed because the tree
already holds 1,251 Toonami files and nothing here has been checked against
them. Filing first and deduplicating later would skew shuffle in the meantime.

### Transcription — `scripts/filler/analyze_spots.py`

The gating problem turned out to be tractable, and not by looking at pictures.

`recategorize_commercials.gate()` matches regexes against a **filename**. For a
segment cut out of a reel that is no evidence whatsoever — every segment
inherits one name describing the programme the break came from. Against a
**transcript** the same question is easy: a 30-second spot is 60–80 words and
says its brand aloud, usually twice.

Measured on 40 spots from the 80s tree, `faster-whisper base.en` at int8 on CPU
took **52 seconds** — so the whole library is about 80 minutes, cached per file.
It returned Head & Shoulders, Oldsmobile, Whirlpool, Honda Civic, Enjoli, Jeep
Cherokee, Scope and Wrangler in plain text.

### The full corpus — 4,075 spots transcribed 2026-09-05

| | |
|---|---:|
| Spots | 4,075 |
| Yielded speech | 3,972 (97.5%) |
| Silent or failed | 103 |
| Total words | 237,914 |
| Median words per spot | 50 |

Run time was about 80 minutes on CPU, cached per file, and the cache plus one
frame per spot occupies 46 MB.

**The existing gate vocabulary classified 6% of it.** 3,832 of 4,075 stayed
`uncategorized`; 129 came back `general`, 77 `christmas`, 37 `kids`. That is the
measured version of the finding below, at full scale: the evidence is now there
and the decision rule is what is missing.

**Promo claim types.** §6 distinguishes promos by whether their claim can be
false. Measured across the corpus:

| Claim | Count | Share of speech |
|---|---:|---:|
| **dated — day *and* clock** | **67** | 1.7% |
| day only | 646 | 16.3% |
| clock only | 20 | 0.5% |
| relative — "coming up next" | 48 | 1.2% |
| tune-in, untimed | 76 | 1.9% |
| no promo signal | 3,115 | 78.4% |
| **any promo signal** | **857** | **21.6%** |

**The falsifiable set is 67 files.** Everything else either makes no time claim,
or makes one that placement can satisfy — a "Saturday" promo aired on Saturday
is simply correct, which is the rule §6 already proposed. So the question of
whether to keep time-claiming promos is not a policy dilemma; it is 67 files,
and they can be quarantined in one folder that is deletable in one command.

**Promos for shows in the library exist.** Matching transcripts against
`library-tv.tsv` surfaces roughly 34 owned titles across ~91 mentions —
Roseanne, Murphy Brown, Home Improvement, Night Court, Murder She Wrote, Freaks
and Geeks, Family Matters, The Golden Girls, Seinfeld, Northern Exposure,
I Dream of Jeannie. These are §6 option 2 — *"real show promos aired inside the
block they advertise"*, true by construction, the approach the policy already
chose.

Caveat, stated because the number will otherwise be reused as if it were exact:
**naive title matching is noisy.** Generic titles produce false positives at
roughly 25-30% even after filtering — "Hercules" matched a Rocky ad, "The
Pacific" matched Marine Land, "Wednesday" matched the weekday. A trustworthy
count needs a curated title list, not a manifest column.

**Transcription unblocks §6 option 3.** That section deferred schedule-aware
promos because they need *"the promo's claimed day/hour as metadata (NFO
sidecars)"*. The transcript is that metadata in plain text, and the schedules
are static grids in code, so a dated promo can be matched to a slot where its
claim is true. What made option 3 expensive no longer does.

---

**But only 1 of those 40 received a suggested gate**, because `gate()`'s
vocabulary is filename-shaped — a list of brands someone once typed into a
filename — and transcripts speak a much larger language. The evidence problem is
solved; the *decision rule* is now the bottleneck, and extending it is a
deliberate choice rather than a mechanical one, because `gate()` is shared with
the filename path and changing it changes both.

**The unexpected finding: a large share of these are promos, not commercials.**
Five of the first eighteen transcripts are network promos — *BJ and the Bear*
("Saturday at 8, 7 Central"), *The Six O'Clock Follies*, a Robby Benson picture,
a Disney two-hour special, *Speak Up America*. §6 of the policy treats promos as
a distinct third kind of interstitial with a truth condition, and the reel split
has just produced a lot of them filed as commercials. They are identifiable from
the transcript — a time claim is a strong, cheap signal — and they are currently
mixed in.

### How far to trust the transcripts — measured 2026-09-05

"Is whisper accurate" is the wrong question, because the cost of an error spans
orders of magnitude depending on what the transcript is used for. It was
evaluated three ways on a seeded random sample of 24 spots, none of which
required hand-labelled ground truth.

**1. Model agreement.** The same 24 re-run on `small.en` and diffed against
`base.en`: **mean similarity 0.83, median 0.92**. Disagreement between two
models is an upper bound on reliability and costs nothing but compute.

**2. Model confidence.** `avg_logprob`, free at transcription time. It isolated
the failures exactly: the only two transcripts judged unusable from their frames
— `"I get for moms"` (4 words) and `"Yeah."` (1 word) — are precisely the two
scoring below **-0.6** (-0.98 and -0.84). Two for two, no false positives.
The threshold rests on 2 positives in 24 and is provisional.

**3. Cross-modal corroboration.** The 24 frames were read blind and then
compared: **~18 of 24 corroborated cleanly** — the Mrs. Dash bottle against
"Mrs. Dash", the AIDS hotline card against the spoken number, the Roseanne logo
against "on the next Roseanne show". Frames and audio fail independently, which
is what makes their agreement evidence rather than restatement.

**`base.en` is weak on exactly what titles need.** Its failure profile is good
gist, bad proper nouns — the worst possible shape for a `<title>`:

| `base.en` | `small.en` | Actual |
|---|---|---|
| "toblur chocolate orange" | "Tobler Chocolate Orange" | Tobler |
| "Carwini, Team Harvey Corbin" | "Comedy team Harvey Korman" | Harvey Korman |
| "Who you want to share it" | "Here you went to Jared" | "He went to Jared!" |

Hence: **`base.en` for `<plot>`, `small.en` for anything that becomes a title.**

### The rule, by cost of error

| Use | Verdict | Condition |
|---|---|---|
| `<plot>` / search | ship as-is | an error costs recall and nothing else |
| promo claim type | trust, spot-check | day and time words are high-frequency vocabulary, the thing ASR is best at |
| `<title>` | gate it | `small.en`, logprob > -0.5, **and** frame corroboration |
| audience gate | never on ASR alone | asymmetric: a miss airs beer in a kids block |

For gates the question is not accuracy but the cost of a miss. ASR should
*nominate* broadly — favouring recall, accepting false positives — with each
candidate confirmed against the frame, and anything unconfirmed staying in
`uncategorized`. That is what the tree already does, and it is the one place the
existing conservatism is exactly right.

### One hypothesis that did not survive

Frame/transcript disagreement was expected to detect bad cuts, on the theory
that a merged segment would show an anomalous words-per-second. **It does not.**
The two spots that looked merged at 163 and 151 words are 65s and 62s — ordinary
density — and a 3.0 w/s threshold flagged three perfectly good fast-read ads.
Words-per-second is not a bad-cut detector and was dropped rather than kept as a
plausible-sounding metric.

### An expensive small bug, recorded because it is easy to repeat

The transcript cache was keyed on file path alone, so a re-run under a different
model would have silently reused the first model's output — making the whole
base/small comparison meaningless while appearing to work. Both the cache and
the result index are now scoped by model name (`transcripts.small.en.json`,
`index.small.en.json`). A `--limit` run had also truncated the full index for
the same reason; that is why the index is scoped too.

### Filing decisions taken 2026-09-05

**Promos are their own tree.** 325 spots moved to `promos/us/<decade>/<claim>/`
by `filler/split_promos.py`, with `_moved_from.json` as an undo and remap
manifest. Sidecars regenerated at the new paths, all 325 carrying their
transcript.

A first pass classified 857 on time words alone and was mostly wrong: "All week
long, Kohl's is offering great savings ... this Thursday" is a retail ad naming
a sale date. Requiring *programme* evidence and letting retail language veto a
weak match cut it to 325, and `day` from 646 to 213. `dated` — the only
falsifiable claim — is **37 files**.

**Toonami: 144 filed, 9 rejected as already owned.** `filler/dedupe_bumpers.py`
compares a difference hash of a mid-frame, because these are re-encodes and
every exact-identity test (checksum, size, duration) reports "different" for
identical content. `toonami/general/` went 111 -> 255. The 15 Dragon Ball
segments are among them.

**Bumpers deliberately get no NFO.** With no transcript and no title, a sidecar
would only restate the folder path — churn plus the §9a risk for zero gain. NFO
earns its place only where it carries facets a folder cannot.

### The gate classifier does not auto-apply, and that is the finding

`filler/transcript_gate.py` is a second classifier over transcripts, leaving
`recategorize_commercials.gate()` untouched.

It was designed to auto-apply *restrictive* gates (alcohol, tobacco) on the
argument that over-restricting is the safe error. **That argument did not
survive the data.** Auto-applying would have filed:

| Nominated as | Actually |
|---|---|
| tobacco — "quit smoking today and your heart will thank you" | an **anti**-smoking PSA |
| alcohol — "Despicable Me 2 ... vodka diva, vodka!" | a film trailer |
| tobacco — "Kool" | **Kool-Aid**, a children's drink |
| alcohol — "Killian" | a character name in *Midnight Caller* |
| tobacco — "Parliament" | "Russian President Boris ... parliament" |
| tobacco — "Winston" | NASCAR's Winston Cup |

"Restrictive errors are harmless" is wrong: `commercials_alcohol_spot` is a real
key, and filling it with cartoon trailers makes it useless. So **nothing is
auto-applied.** All 154 nominations go to a review queue carrying the matched
phrase as evidence, and `--apply-reviewed` takes a queue a human has pruned.

That is the same position `recategorize_commercials` reached from the other
direction: a gate is a positive determination, never the residue of a regex.

### `small.en` over the whole corpus — 2026-09-05

The re-transcription finished. It confirmed the 24-spot evaluation and changed
what is on disk.

| | |
|---|---:|
| Spots | 4,075 |
| `avg_logprob` median / mean | -0.285 / -0.308 |
| Below -0.5 (the proposed title gate) | 267 (6.7%) |
| Below -0.6 | 127 (3.2%) |
| Empty transcripts | 94 (`base.en` had 103) |

**Agreement with `base.en`: mean 0.793, median 0.917** across 3,987 spots —
against the sample's 0.83 / 0.92, so the 24-spot evaluation was representative.

**But the two models disagree materially on one spot in five**: 19.3% score
below 0.6 similarity and 12.1% below 0.4. Since `small.en` is the better model
on proper nouns, the `<plot>` text written from `base.en` was materially wrong
for roughly a fifth of the library. **All 4,130 sidecars were regenerated from
`small.en`.**

Titling readiness: 3,681 of 4,075 (90%) clear `logprob > -0.5` with at least 8
words. That narrows the review queue; it does not make titles automatic, and the
frame-corroboration condition stands.

### Two bugs the regeneration exposed

**The NFO generator carried its own copy of the promo rules.** Written before the
PROGRAMME/RETAIL gate existed, it tagged **557** spots in the commercial tree as
`promo` that `split_promos` had already judged were not. It now imports `claim`
from `split_promos`, which is the only place the rules live. The count fell to 25.

**That import needed a `sys.path` hack, which was the symptom of a misplaced
file.** `nfo/` is movie-library tooling — `normalize_tag_case.py` operates on
`/media/movies`. The sidecar compiler is filler tooling, so it moved to
`filler/generate_filler_nfo.py`, where the import is a plain sibling one and the
hack is gone.

A known imprecision, recorded rather than smoothed over: **20 of the 325 promos
no longer classify as promos under `small.en`.** They were moved on `base.en`
evidence the better model disagrees with. They keep their folder tags, so nothing
is unreachable.

### Channel 4 continuity — tier 5, fetched and split 2026-09-07

`BBCClosedown` is **mislabelled**: it is largely Channel 4, not BBC, and 104 of
its 320 files are programmes (Brookside, Countdown, *Greatest Toys*). Fetching
with `--match` over continuity/advert/ident/closedown names and collapsing the
`.ia` twins took it from 14.0 GB to **189 files, 5.8 GB** — under half the item.

The fetch applied one `--name` to every file, which put a false `1996` on
material spanning 1991-2002. Since `split_reels.decade()` reads the leading year
and nothing else, that would have misfiled a fifth of it. Renamed from the dates
already in each filename — **186 corrected**, spanning 1991-2002 with the mass at
1995 (62) and 1996 (87). Three carry no recoverable year and are left undated,
which the splitter skips rather than guessing.

Filed to `commercials/uk/<decade>/uncategorized/`. **These reels are continuity
*and* adverts mixed**, so the tree is impure by construction: idents filed as
commercials are the same mislabel the promo split just corrected. Separating them
wants a transcript pass — a continuity announcer is highly distinctive ("you're
watching Channel 4", "next on Four") — and that is the outstanding work on this
material.

### An acquisition scout — `scripts/filler/scout_archive.py`

Read-only; it never downloads. Seven named queries, one per §8 gap, so the
ranked list and the search that serves it are the same artifact and cannot
drift apart.

One trap it exists to avoid: archive.org's `services/search/v1/scrape` endpoint
**silently ignores unfielded phrases**. `mediatype:movies AND "nick at nite"`
returns 57.7 million items — the whole archive, sorted by identifier — rather
than an error. A caller who does not check `total` gets a confident page of
unrelated results and no warning. `advancedsearch.php` parses the same query
correctly and is what the scout uses.

---

## 2. What is actually best for this setup

The honest answer, before any shopping list.

**Deep generic pools are the least scarce thing here, and the least valuable.**
Adult Swim's 4,682-file `bumps/general` pool is proof: it is 28% of the entire
filler library and it serves one block on one channel. §4 of the policy already
established that a break is a recipe, not a pool — a 90-second break spends two
bumpers, not nine. Volume was never the constraint.

**What is scarce is position and period.** The three things worth acquiring, in
order:

1. **Break-position material** — `to ads` and `back` bumpers. These are what
   make a break read as television rather than as a playlist, and the invariant
   in `dispatcher.BreakState` is already built to consume them. Toonami's
   filenames encode this for 653 files and nothing else on disk does.
2. **Period-correct continuity for the eras we actually program.** The lineup
   runs 1951 to the present across nineteen channels. One network's voice fits
   one channel. This is the real gap and it is mostly unfilled.
3. **Per-show bumpers for shows that anchor blocks** — which is a five-file
   problem named Dragon Ball Z, not a general one.

**Airchecks beat clip compilations, and it is not close.** A two-hour off-air
capture of Disney Channel 1994 yields the bumpers, the promos *and* the
commercials, in period-correct sequence, from one download — and `split_reels.py`
now turns that into filed spots automatically. A YouTube rip titled "Disney
Channel Bumpers Compilation" yields bumpers only, usually re-encoded twice,
often with a compiler's music bed over them. The pipeline that just produced
3,721 spots is an aircheck pipeline. Feed it airchecks.

---

## 3. Where the material is — verified identifiers

Ranked as §8 ranks the gaps. Sizes are the full item; the useful derivative is
typically a fifth of that.

### Gap #2 — Disney (257 matching items)

The named ask with zero assets on disk. Well served.

| Item | Size | Note |
|---|---:|---|
| `TheVistaGroup-Y2KTVCommercialsDisneyChannelOrigi` | 4.4 G | 2000 + 2004 Fall, Disney Channel, off-air |
| `TheVistaGroup-Mid90sDisneyChannelChristmasSeason` | 3.6 G | **1995 Christmas** — period-correct seasonal, rare |
| `TheVistaGroup-Y2KTVCommercialsDisneyHalloweentow` | 6.3 G | 2004 October, Halloween |
| `disney-channel-commercials-on-screen-banners-oct` | 0.45 G | October 2002 |
| `disney-channel-commercial-breaks-october-23-2007` | 0.09 G | small, quick win |

The Vista Group entries are true airchecks and are the ones to take. Note the
gap this does *not* fill: the 1983–1992 subscription era and the syndicated
*Disney Afternoon* wraparounds are much thinner than the 2000s material.

### Gap #3 — Good Times, 1950s/60s (97 matching items)

Scarcest era on the lineup and it also serves Lucy TV (120) and Nick at Nite (247).

| Item | Size | Downloads | Note |
|---|---:|---:|---|
| `Televisi1960` | 1.8 G | **284,423** | *Television Commercials (1950s–1960s)* — the best-known set of the era |
| `USATVCommercialCollection` | 30.7 G | 13,470 | *American TV Commercials (1960s–2000s)* — the single deepest US item found |
| `1958Alka-seltzerCommercialsWithBusterKeaton` | 0.20 G | 33,949 | |
| `CapnCrunchCereal1960s-70s` | 1.2 G | 11,570 | kids gate, positively determinable |

`Televisi1960` at 1.8 GB is the highest value-per-byte item in this document.

### Gap #4 — Nick at Nite (1,320 matching items)

| Item | Size | Note |
|---|---:|---|
| `nickelodeon-snick-promo-1999` | 0.94 G | SNICK block promos |
| `randomnickelodeoncommercialsvol2february2001` | 0.07 G | full commercial break |
| `TheVistaGroup-TVCommercialsNickelodeonHBOStarzMa` | 6.3 G | 1991/1999/2000, off-air |
| `youtube-KbXrTqspSDY` | 0.11 G | Classic Nickelodeon bumper collection |

Caveat: most high-ranking results are Nickelodeon *daytime*, not Nick at Nite.
The classic-TV block's own idents are a narrower search than this query makes it
look — 247 wants the Nick at Nite wraparounds specifically.

### Gap #5 — UK continuity (640 matching items)

The most distinctive material in this document and the one set that cannot be
substituted from US sources. Across the Pond (104) is the only consumer.

| Item | Size | Note |
|---|---:|---|
| `BBCProgrammes2000-01` | 33.5 G | continuity, 2000–01 |
| `BBCCBBC2002` | 19.2 G | continuity, 2000–02 |
| `BBCClosedown` | 17.3 G | **closedown sequences** — the clock, the pips, the shutdown |
| `videoplayback_20181019` | 15.4 G | continuity, 2000–05 |

These are large because they are whole recorded evenings. That is exactly what
`split_reels.py` wants. `BBCClosedown` is the interesting one: closedown is
unrepeatable elsewhere and would give 104 a genuine overnight identity.

**Note the era mismatch.** The policy asks for 1960s–2000s UK; what is well
preserved online is heavily 2000s. The 60s/70s end is scarce here too.

### Gap #6 — Dragon Ball Z / Toonami (63 matching items)

The five-file pool that anchors two blocks.

| Item | Size | Note |
|---|---:|---|
| `toonami-promos-and-intros-hd` | 0.63 G | |
| `BestOfToonamiBumpersHD` | 0.31 G | |
| `Cartoon_Network_Toonami_August_2001_Promos_Bumpe` | 0.10 G | dated — files into the right era |
| `Cartoon_Network_Toonami_1997_Promos_and_Bumpers-` | 0.15 G | dated |

All small. This gap is cheap to close and it is the one where airtime most
badly outruns assets.

### Gap #7 — Cartoon Network daytime (614 matching items)

`bumpers/cartoon network/general/` is scaffolded and **empty**.

| Item | Size | Downloads | Note |
|---|---:|---:|---|
| `cartoon-network-city-complete-bumper-archive` | 0.47 G | 13,595 | **the answer to this gap** — CN City is the 1999–2004 daytime identity, and "COMPLETE" is the claim |
| `Taste_of_Cartoon_Network_1993_Promo_VHS_Tape` | 3.0 G | 9,988 | 1993, the launch era |
| `youtube-xNFMzTM37NY` | 1.5 G | 4,757 | July 2007, bumpers + commercials |

**`cartoon-network-city-complete-bumper-archive` is the single best
cost-to-value item in this document**: 470 MB fills an empty folder that the
registry already has a key pointing at.

### `WOC` — the search term that beats "aircheck" (2,441 matching items)

The policy names `aircheck` as the term of art, and for radio it is. On
archive.org's television material the higher-yield token is **`WOC` — "with
original commercials"**, a convention uploaders use to mark a capture whose ad
breaks are intact. It returns 2,441 items on title alone — 2,977 including description matches —
where `aircheck` returns mostly radio.

| Item | Size | Downloads | Serves |
|---|---:|---:|---|
| `vts-01-2_20200824` | 5.1 G | 86,262 | **ABC Saturday Morning Cartoons, 1993-08-21** — Disney/kids Saturday morning |
| `vts-01-1_20200929_2234` | 2.7 G | 40,117 | **ABC Saturday Morning Cartoons, 1986-12-20** — and it is December, so Christmas ads |
| `Vintage_Commercials_Advertisements_80s` | 34.4 G | 42,166 | 80s/90s Saturday morning, the deepest single 80s item found |
| `Good_Will_Hunting_ABC_WOC_2001-02-19` | 4.5 G | 96,164 | ABC 2001 network-movie break — Corncob, Be Kind Rewind |
| `MST3K_Godzilla_Vs_Megalon_Comedy_Central_WOC_199` | 7.2 G | 53,302 | Comedy Central 1996 — cable-era voice |
| `Brave_New_World_NBC_WOC_1998-04-19` | 7.0 G | 35,111 | NBC 1998 — Must See Thursday era |

**This corrects §3's Disney entry.** The *Disney Afternoon* wraparounds were
called the weakest-covered named ask on the lineup. They are not — they are
sitting in `WOC` captures:

| Item | Size | Downloads |
|---|---:|---:|
| `1992-07_Disney_Afternoon_-_Duck_Tales__Rescue_Ra` | 3.0 G | 27,485 |
| `talespin-darkwing-duck-disney-afternoon-1991` | 6.9 G | 5,496 |
| `Gargoyles_Disney_Afternoon_WOC_1995-02-03` | 1.3 G | 5,594 |

A dated network-movie capture is the ideal input to this pipeline: two to three
hours, one date, one network, ad breaks intact, and the date goes straight into
the filename that `split_reels.decade()` reads.

### The deep well — Vista Group off-air captures (277 matching items)

`collection:the-vista-group-video`, 1,940 items overall, of which 277 are TV
commercial captures totalling **1.21 TB**. Las Vegas, Seattle, Boston,
Baltimore and Green Bay affiliates plus MTV, HBO, A&E, USA, TNT, TNN and
Discovery, 1980 through the 2000s.

This is the deepest single source found and it is also the biggest trap in this
document — see §4.

---

## 4. How to get it — the cycle, and the storage arithmetic

**The pool has 3.3 TB free. The Vista Group commercial subset alone is 1.21 TB.
"Download the collection" is not a plan.**

These items are stored at archival bitrates — 60 fps upscales of VHS, 5 to
77 GB apiece — and we want them at broadcast filler bitrates. The staged reels
just demonstrated the real ratio: 28.6 hours of source produced 3,721 spots
that occupy a small fraction of it. Roughly **35:1**.

So the cycle is one item at a time, and the source does not stay:

```
1. fetch      curl -O https://archive.org/download/<identifier>/<file>.ia.mp4
              -> into /media/.staging/us_commercials/  (or a new staging dir)
2. name it    lead with the year: "1995 Disney Channel Christmas.mp4"
              split_reels.decade() reads the leading year and nothing else
3. split      python3 filler/split_reels.py --only "1995 Disney" --apply
4. verify     check the length histogram looks like broadcast advertising
5. delete     the source. The spots are the asset; the capture was scaffolding.
```

Step 2 is the one that is easy to get wrong and expensive to fix: an undated
filename is skipped entirely by the splitter, because guessing a decade is
worse than not filing.

`scout_archive.py --plan <gap>` prints this arithmetic for any gap before you
commit to it.

**No API key, no `ia` CLI.** Every item is plain HTTPS;
`https://archive.org/download/<identifier>/` lists its files. Prefer the
`*.ia.mp4` derivative — about a fifth of the item size and already the format
the staged reels arrived in.

---

## 5. How it gets organized

The tree is already defined by [filler-taxonomy.md](filler-taxonomy.md) §5 and
nothing here changes it. `commercials/<country>/<decade>/<gate>/`, where every
path segment becomes its own flat tag.

**Everything the splitter produces lands in `uncategorized/`, and that is
correct, not a shortcut.** A gate is a positive determination. A segment cut
from the middle of a reel inherits the reel's filename, which names *the
programme the break was recorded from* and says nothing about the product on
screen — the weakest evidence available. `recategorize_commercials.py` exists
because the first pass treated "no keyword matched" as evidence of safety, and
the Winston-cigarette Flintstones spot is the standing reminder of what that
costs.

Consequence, and it is deliberate: `commercials_family_safe_spot` excludes
`uncategorized`, so **no kids or daytime key draws from the 3,721 new spots**.
Channels that want them ask by name — `commercials_us_spot`,
`commercials_90s_spot`, `commercials_uncategorized_spot`.

That is the right default for a 30-hour bulk import of unreviewed broadcast
advertising. Promoting a subset out of `uncategorized` is a later, human pass,
and it wants frames rather than filenames — the 1950s set was gated from
extracted closing frames, which is the only method here that has actually
worked.

**Bumpers acquired for a network go in the bumper tree, not here.** CN City
bumpers belong at `bumpers/cartoon network/general/`, which already exists and
is empty, and they must keep the `bumpers` tag that `play_smart_bumper`
requires. Do not file network-branded material as country-neutral commercials.

---

## 6. Recommended order

| # | Step | Cost | State |
|---|---|---|---|
| 1 | Split the staged reels | none | **done — 3,721 spots** |
| 2 | Acquisition tiers 1–4 | 3.4 GB | **done** — 282 CN City bumpers, 270 new spots, 153 Toonami in review |
| 3 | Transcribe the library | none | **running** — `analyze_spots.py` over 4,075 spots |
| 4 | **Rescan the ErsatzTV Other Videos library** | none | **required before any of it is reachable** |
| 5 | Decide the transcript gate vocabulary | none | the evidence exists; the rule does not. Blocks promoting anything out of `uncategorized` |
| 6 | Separate the promos | none | they are in the commercial tree today and §6 says they are a different kind |
| 7 | Dedupe and file the 153 Toonami segments | none | against the existing 1,251 |
| 8 | Scene-change detector for hard-cut compilations | none | two Toonami items are unreachable without it |
| 9 | Apply `sort_bumper_positions.py`, Toonami scope | none | 653 moves, dry-run already reviewed |
| 10 | `BBCClosedown` + one BBC continuity item (tier 5) | ~35 GB | not yet approved; 104's overnight identity |
| 11 | Genre NFO sidecars for trailers | none | generation pass over `library-movies.tsv` |

Step 2 is not optional and is easy to forget: 3,721 files now exist on disk that
ErsatzTV has never seen.

---

## 7. What this does not solve

- **The 1950s–60s remain thin**, here and everywhere. `Televisi1960` is good and
  it is not five decades of CBS continuity. Good Times spans 1951–1999 and this
  document meaningfully serves maybe its back half.
- **Disney's subscription era (1983–1992)** is far thinner than its 2000s
  material — though the *Disney Afternoon* wraparounds turned out to be well
  covered under `WOC`, contrary to this document's first draft.
- **UK material skews 2000s.** The 60s/70s continuity that Across the Pond's
  older programming wants is scarce.
- **Nothing here is verified for content.** Download counts and titles are not
  quality signals, and no item in §3 has been watched. Every one of them needs a
  look before it is filed — the 3,721 spots included.
