# Channel Plan

Working plan for the scripted-schedules lineup. Companion to channel-coverage.md (what exists and where it goes) and the library references in this directory.

> **The rules are now in [channel-rules.md](channel-rules.md)** — founding a
> channel, building the grid, curating across channels, and the checks that
> gate "built". This file stays the working state: the lineup, the grids, and
> the per-channel history each rule came out of.

---

## The organizing principle

**A tune-in channel needs episodes that stand alone.**

This is the rule everything else follows from. ErsatzTV earns its keep when you don't know what to watch and you turn something on — which only works if any given episode is enjoyable cold. Serialized shows fail that test: nobody tunes in mid-season-2 of *Six Feet Under*, they select it. Those belong on-demand.

Every channel already in the lineup selects for episodic content without anyone having decided it: sitcoms, westerns, detective-of-the-week, horror anthology, cartoons, sketch, cooking, DIY, 80s action. That is why they work, and it is why ~75% of the 108 unhomed shows are unhomed — they're serialized.

The escape hatch is `annual_show()` Broadcast Mode: one season a year, chronological, weekly, reruns filling the gap. That converts a serialized show into appointment TV, which is a different promise — "this channel has a Thursday show" rather than "turn it on whenever."

**How many a channel can carry is not a number.** What governs it is whether each appointment has its own night and its own bed. An appointment needs a slot that gates it — a weekday arm of the schedule, not `frequency` — and something to run in that slot the other fifty weeks. Give it both and a channel can carry one or six; High Noon carries six, one a night, with a film bed under each. What breaks a channel is appointments sharing a slot, because a `DailyOrderedCollection` that wraps replays the same episode twice a night — which is the actual defect behind Good Times' `MUST_SEE_THURSDAY`, and it happens at four appointments in one slot just as readily as at two.

---

## Lineup

### Existing

| # | Channel | Content | Scripted |
|---|---|---|---|
| 102 | Wild Horizons | nature & wildlife — **on the server, absent from this plan**; identified 2026-09-02 from `/api/channels` | no |
| 104 | Across the Pond | British television — **a broadcast day**, not "comedy & panel" | yes — **designed**. The last channel still on the default preset |
| 116 | Cartoon Network | CN originals + Toonami + Adult Swim | yes — **rebuilt** |
| 120 | Lucy TV | I Love Lucy 24/7 | no |
| 142 | Cabes Classic Cinema | film, **1920–1979** | yes — **designed**. The 1980s handed back; identity finally stated |
| 144 | Mystery Theatre | detective / procedural | yes — **refined** |
| 151 | Other Worlds | science fiction | yes — **refined**, fantasy & horror removed |
| 164 | Japanorama | anime — **the Japanese broadcast day** | yes — **built** 2026-09-03 |
| 180 | Totally 80s | 80s TV — **stays 80s** | yes — **designed** 2026-09-01 |
| 190 | Good Times | **the studio audience** — multi-camera network sitcom, 1951–1999 | yes — **rebuilt** 2026-09-01 |
| 240 | Travelers Table | cooking — **+ nature docs** | no |
| 241 | Makers Corner | DIY & craft | no |
| 242 | Corncob TV | **comedy after the laugh track** — single-camera, cable, streaming, sketch and alt | yes — **built** 2026-09-01 |
| 243 | High Noon | westerns | yes — **built**. The TV is the spine: 946 episodes, five B&W shows |
| 244 | Nightmare Theatre | horror, TV + film | yes — **built**. The film is the spine: 242 features, 17 h/day |
| 246 | The Beat | **music videos only** | no |
| 247 | Nick (+ Nick at Nite) | Nicktoons, WB animation, classic TV | yes — **built**. Live as *Nickelodeon* |
| 248 | Disney | Disney Afternoon, ABC mornings, Star Wars animation | yes — **built** |
| 249 | Be Kind Rewind | film, **1980–present** | yes — **built**. The video store: a week, not a genre |

### To build

| Channel | Pool | Shows | Notes |
|---|---:|---:|---|
| **Fantasy** | 238 films / 40 shows | 40 | Registry and `library/fantasy.py` built 2026-08-30; **channel deliberately deferred**. Content is there — 333 fantasy films, more than horror |
| ~~Boomerang~~ | 1 show | 1 | **Closed — see below.** Disk problems fixed; the premise is what is gone |

---

## Channel notes

### Cartoon Network — rebuilt
`scripts/channels/cartoon_network.py` · `scripts/library/animation.py`

Restructured against [cartoon-network-review.md](cartoon-network-review.md), which is the audit this grid came from. The channel was giving **27 hours a week to Disney and 13 to Nickelodeon** while Cartoon Network's own originals held five, and Adult Swim ran 20:00–02:00 with Hanna-Barbera behind it until 06:00 — the exact inverse of the real thing. Both other claimants on the animation library were built first, so the eviction list was written down rather than derived.

| Slot | Mon–Thu | Friday | Saturday | Sunday |
|---|---|---|---|---|
| 00–02 after hours | Midnight Run | Midnight Run | Midnight Run | Adult Swim originals *(Sun night)* |
| 02–06 overnight | Adult Swim, acquisitions | ← | ← | **Toonami: The Midnight Run** *(Sat night)* |
| 06–08 early | The Vault | ← | ← | ← |
| 08–10 morning | Cartoon Cartoons | ← | Saturday Morning | The Scooby Block |
| 10–12 midday | Cartoon Network | ← | Cartoon Cartoons | The Vault |
| 12–14 noon | The Vault | ← | Syndication Hour | Cartoon Theatre |
| 14–17 afternoon | Action Hour | ← | Action Hour | Cartoon Network |
| 17–20 evening | **Toonami** | Cartoon Cartoon Fridays | **Toonami Saturday** | Cartoon Cartoons |
| 20–23 prime | Adult Swim originals A/B | A | Toonami Saturday cont. | FOX Primetime |
| 23–24 night | Midnight Run | Midnight Run **premiere** | Midnight Run | Adult Swim originals |

Simulated over 365 continuous days: no gaps, no circuit breakers, no unresolved programs. Airtime share of ~21,000 programme plays — **CN originals 22.6%, anime/Toonami 16.7%, Adult Swim originals 11.1%** (50.4% between them, against ~9% before), acquisitions 14.3%, the vault 19.3%, superhero 9.9%. Disney and Nickelodeon are at zero.

**Adult Swim runs last, not first.** Originals at 20:00, the anime Midnight Run at 23:00, acquisitions 02:00–06:00. The old grid had the 2009–2014 acquisitions as the 20:00 marquee and the Williams Street originals behind them.

**Own timeslot map, split at midnight.** The default preset's `night: (23, 2)` wraps, and a wrapping slot is entered twice under two different day labels — so "Sunday night" resolved to two different nights and a `DailyOrderedCollection` replayed its first items across the boundary. `night` is 23–24 and `after_hours` is 00–02, each with its own block. Same reason Nick and Disney carry their own maps.

**Two appointments, both day-gated by their block.** Dragon Ball DAIMA (20 eps) premieres Saturdays inside Toonami Saturday; Attack on Titan Junior High (12 eps) premieres Fridays at 23:00 inside a Friday-only variant of the Midnight Run. The gating has to come from the slot — `frequency` only paces the episode index, it does not stop the appointment airing on other days. See [KNOWN_ISSUES.md](../KNOWN_ISSUES.md).

**Per-show bumpers are wired.** ~940 Toonami and 5,316 Adult Swim files were unreachable; each Toonami and Adult Swim item now carries its own set through a `Program` wrapper (`animation._with_bumpers`). `play_smart_bumper` would find them by title on its own, but it requires a `bumpers` tag and the trees are tagged `bumps`/`shows`.

**No daytime filler.** `filler_content="adult_swim_bumpers"` was channel-wide and only the five branded blocks overrode it, so ~14 hours of every 24 — Saturday-morning Scooby-Doo included — ran Adult Swim bumps. There is nothing to replace it with: `filler/bumpers/cartoon network/general/` is empty and the 110 files under `commercials/90s` are mislabelled 2000s British adverts. Silence is closer to Cartoon Network than Adult Swim is. Sourcing checkerboard / Powerhouse / CN City branding is the outstanding asset job.

Summer (Jun–Aug) hands weekday 08:00–14:00 to CN's own shows and drops the vault from lunchtime; spring still leans Marvel, in the Action Hour rather than the retired 08:00 superhero hour. Marathons are date-anchored — Thanksgiving and New Year's Toonami, July 4th DBZ, Memorial Day Bebop, first Saturday of the month CN — each keeping its old random chance on top via `triggers.any_of`.

### Japanorama — built
`scripts/channels/japanorama.py` · `scripts/library/anime.py`

**Identity.** A Japanese network's whole day, not an after-school block. Toonami
is the best three hours of anime on the lineup and it is a *block*; a block has
no morning, no feature and no small hours. This channel signs on at six and
reaches 深夜アニメ by 23:00 — the half of the medium American television never
imported. The channel had existed since the beginning with no configuration and
no stated identity.

**Axis: the clock, as a broadcast day.**

| Slot | Mon–Fri | Saturday | Sunday |
|---|---|---|---|
| 02–06 rebroadcast | The Rebroadcast — owned content only | ← | ← |
| 06–08 morning | Morning Cast — iyashikei | ← | ← |
| 08–12 kids | The Kids' Hours — Pokémon, Dragon Ball, Sailor Moon | ← | ← |
| 12–15 midday | The Syndication Hour — One Piece, Naruto, InuYasha, Kenshin | ← | ← |
| 15–17 afternoon | The Dragon Ball Hour — Z, GT, Super | ← | ← |
| 17–19 teatime | Teatime — **owned titles only** | ← | ← |
| 19–21 feature | Japanorama Theatre | the canon | **Ghibli Sunday** |
| 21–23 prime | the named night | the limited series | The Sunday Replay |
| 23–24 late | Deep Night | ← | ← |
| 00–02 deep night | Deep Night — the film half | ← | ← |

365 continuous days simulated: no gaps, no circuit breakers, no unresolved
programs, **15,101 programme plays**. Three years re-run to confirm every named
night airs on its own weekday and nowhere else, and that the three Saturday
limited series stay on Saturdays. Validator clean; test suite passing.

**The library, counted off disk.** 46 anime series / 3,140 episodes and 43
features, of which **587 episodes across 24 shows were claimed by nothing** —
and two shows nothing had ever counted, *The Tatami Time Machine Blues* (6) and
*Midnight Diner: Tokyo Stories* (20, which doubles Midnight Diner to 40). The
feature shelf was the surprise: a **complete 23-film Ghibli run**, 1984–2023,
plus Akira, Perfect Blue, Ghost in the Shell, Metropolis, Tokyo Godfathers,
Paprika, Angel's Egg, Miss Hokusai, Your Name and all four Rebuild of Evangelion.

**TV-led with a nightly feature (F5).** 587 owned episodes plus 2,450 shared
against 43 features — television with a film shelf, the High Noon shape. The
feature still gets two hours because 43 films at seven a week is a six-week
cycle. It opens at 19:00 because C7 measured 18:00–20:00 as the emptiest film
hour and Be Kind Rewind already holds 18:00.

**The hours rule against Toonami is the whole design.** Cartoon Network holds
the entire shonen canon — ~2,450 episodes, four times everything else here.
Ceding it leaves a fortnight's cycle; taking it without a rule breaks C1 a dozen
times a night. So C2 rungs 1 and 2 together: Toonami runs these shows as a
first-run chronological strip after school, Japanorama runs them as **shuffled
daytime syndication**, and the `_syndication_tv` keys carry Shuffle at the key
level (C3). Cartoon Network airs anime in four windows — 17:00–20:00 weekdays,
17:00–23:00 Saturday, 23:00–02:00 nightly, 02:00–06:00 Saturday night — leaving
06:00–17:00 daily plus 20:00–23:00 off-Saturday. Every shared title sits inside
that window. Verified over three simulated years: the only shared titles outside
daytime are Fullmetal Alchemist: Brotherhood and Death Note on Friday
21:00–23:00, which is the documented exception.

**Attack on Titan is deliberately not on this channel** — it anchors CN's
Midnight Run at 23:00 every night, which makes it a coin flip rather than a
rule. Teatime draws no shared title at all because 17:00–19:00 is inside
Toonami's window.

**Measured, not asserted (C6).** `collision_report` groups by key name and so
cannot see any of this — Toonami's `{"title": "One Piece"}` and
`one_piece_syndication_tv` look unrelated to it. Both channels were simulated
together and resolved down to titles: **0 simultaneous same-title airings
against Cartoon Network over 60 days**, and 0 against every other channel once
two real defects were fixed (below). The remaining reported hits are all
`studio:`/`tag:` keys the manifests cannot evaluate, the same supersets
`same_title_check` files under POSSIBLE.

**Three defects found and fixed on the way, none of them this channel's:**

* **`NOT_ANIMATED` was half a rule.** It was `NOT genre:animation` alone, and
  the library tags Laid-Back Camp the Movie and the 1986 Transformers `Anime`
  with no `Animation` — so every live-action film pool on the lineup contained
  two animated films, and Be Kind Rewind's `recent_movie` was drawing Laid-Back
  Camp the Movie against this channel's feature. Now excludes both tags. See G11.
* **The old `ghibli_movie` key was unverifiable.** It was `studio:"Studio
  Ghibli"`, and `library-movies.tsv` has no studio column, so `key_census`
  scored it "not in manifests" and never checked it against anything. It is an
  explicit 23-title list now, and it resolves to exactly 23.
* **Two film keys over-matched on phrase.** `title:"Metropolis"` also returns
  Fritz Lang's 1927 silent — Cabes Classic Cinema's oldest film, on an anime
  channel at midnight — and `title:"Your Name"` returns Call Me by Your Name.
  Both closed by the genre guard rather than per-title year bounds (G10).

**The vault was the near-miss.** `THE_REBROADCAST` at 02:00–06:00 was first
built from the day's syndication wheel, which put four Toonami shows opposite
CN's Saturday-night Midnight Run weekly. The grid was right and the *bed* was
wrong; it is owned content only now, and it is why `fallback_content` is
`japanorama_vault_tv`. This is written up as an addendum to C3.

**It has filler on day one, which no other channel does.** Encouragement of
Climb season 1 and Room Camp are 24 episodes of 3.5-minute shorts — real
programming the right length for an hour boundary, where Cartoon Network has an
empty bumper tree and runs nothing (G12). Running time drove the whole show:
Encouragement of Climb is three shows by length (S1 3.5 min, S2–3 13.5, S4 24)
and had to be cut into them (G2).

**Calendar: all three.** Golden Week (29 Apr – 3 May) runs Ghibli in release
order — it stops on the 3rd rather than the 5th because 4 May is Star Wars Day
and a marathon cannot fire inside a holiday season (G9). Obon (13–16 Aug) is
Grave of the Fireflies and the shelf's other ghost stories. Ōmisoka is a holiday
*schedule* on 31 December for the same G9 reason. All three verified firing.

**No bumpers.** There are no anime assets on disk beyond Toonami's, which belong
to Cartoon Network. Same asset gap Nightmare Theatre has.

### Disney — built
`scripts/channels/disney.py` · `scripts/library/disney.py`

Three eras of one studio, dayparted so they never argue: the ABC morning cartoons at 06:00–08:00, **The Disney Afternoon** at 15:00–17:00, the modern Disney Channel shows after school at 17:00–19:00, and Star Wars 19:00–24:00. 22 shows, 1,364 episodes.

The channel carries its own timeslot map. The default preset puts afternoon at 14–17 and prime at 20–23; the Disney Afternoon is two hours ending at 17:00, so noon becomes 12–15, afternoon 15–17, prime 19–21 and the night splits at 21:00.

**The bench is three strips, not four.** Overnight, morning and midday ride `monthly_rotation()` over four pools — Duckburg (DuckTales, Darkwing Duck, Chip 'n' Dale), Disney Adventure (TaleSpin, Gargoyles, Goof Troop), One Saturday Morning (Aladdin, Hercules, Pepper Ann), Disney Action (Kim Possible, Buzz Lightyear, Mighty Ducks) — each starting the cycle a month apart. 902 episodes.

Noon (12:00–15:00) is deliberately held **off** the bench. Duckburg and Disney Adventure are the two halves of the Disney Afternoon, so a bench turn there would put the marquee's own six shows in the three hours leading into it — four hours of one rotation, and the 15:00 appointment stops meaning anything. Noon gets Disney Toons instead: everything the Afternoon is not. This is the one place Disney departs from the Nick pattern, and the reason is that Disney has a marquee where Nick has a flagship pool.

**Serialized shows stay off the bench.** Gravity Falls, The Owl House and Amphibia carry the chronological-weekday / shuffle-weekend split in the 17:00–19:00 strip, and the shuffle half runs again at 00:00–02:00 as Disney After Dark — same two keys, no third registration. Star Wars (Clone Wars 133, Rebels 69, Bad Batch 47) does the same at 19:00–21:00, with the shuffled vault behind it at 21:00–24:00.

**Four Saturday events.** The short series — Tales of the Jedi (6), Tales of the Empire (6), Tales of the Underworld (6), Maul – Shadow Lord (10) — are too short to strip, so each is an `annual_show()` appointment: one episode a Saturday, six or ten weeks, one per season of the year. Between them they give 28 Saturdays a first-run premiere; the vault covers the other 24. The block uses `DailyOrderedCollection` so each show holds the same position every week and premieres at the same time.

Sunday 19:00–21:00 is **The Wonderful World of Disney** in place of the Star Wars strip, and May 4th takes 08:00–22:00 as a Clone Wars marathon.

No filler: `filler/bumpers/` has cartoon network and fox kids trees and nothing else, and the library has no Disney shorts to stand in.

Built against bare season strings while the `("SEASON", "DAY")` tuple form was broken; that form is now fixed and both work. See [KNOWN_ISSUES.md](../KNOWN_ISSUES.md).

### Nick — built
`scripts/channels/nick.py` · `scripts/library/nickelodeon.py`

Nicktoons daytime, **Nick at Nite** 21:00–02:00. Nick's 8 animated shows can't rotate on their own — the WB trio (Animaniacs 197, Pinky 95, Tiny Toons 98) gives it a real bench, and they sit closer tonally to Ren & Stimpy than to Disney Afternoon. Daria lands here too.

Four daytime pools (Nicktoons Classic, Nicktoons, the WB bench, Nick Learns) ride `monthly_rotation()` across four strips — overnight, morning, midday, afternoon — each starting the cycle a month apart, so all four are showing different pools on any given day and all four move on together at the turn of the month.

Nick at Nite splits at midnight: 21:00–24:00 is pre-1970 (I Love Lucy, Dick Van Dyke, Andy Griffith, Bewitched, I Dream of Jeannie, The Addams Family, Gilligan's Island), 00:00–02:00 is the 70s shift (Mary Tyler Moore, Bob Newhart, Taxi, MASH, Sanford and Son, Good Times, Soap, Mork & Mindy, Smothers Brothers). Sixteen shows, not seventeen — the library's only other pre-1980 comedies are *The Lucy Show* and *The Lucy-Desi Comedy Hour*, which stay with Lucy TV.

The channel does not use the default timeslot preset: Nick at Nite needs 21:00–02:00, which `prime` 20–23 / `night` 23–02 can't express.

Avatar and Korra are the evening strip and the only serialized shows on the channel, so they carry the chronological-weekday / shuffle-weekend split — two content keys per show, because an ErsatzTV key carries its playback order and one key would be pinned to whichever order registered first.

Filler is Schoolhouse Rock — three minutes a piece, and the only interstitial the channel has assets for. There are no Nick bumpers on disk.

### High Noon — built
`scripts/channels/high_noon.py` · `scripts/library/western.py`

Two libraries that do not mix, dayparted so they never argue.

**The spine is five black-and-white network westerns**, 1955–1963, **946 episodes**: Bonanza (431, complete run), Gunsmoke (233, the half-hour Dennis Weaver years), The Rifleman (166, complete), Wanted: Dead or Alive (94, complete), Rawhide (22, season one only). All episodic, all standalone. That is the channel for fifteen hours a day.

The plan's old figure of 1,373 episodes was three things at once. It counted **Cowboy Bebop** (anime, already Toonami's), **Breaking Bad** and **Westworld** — all three carry a Western genre tag and none is a western — and it counted `extras/` folders as episodes. The honest number is 946 for the spine and 234 for the moderns.

| Slot | Mon–Fri | Saturday | Sunday |
|---|---|---|---|
| 00–02 night | Late feature | ← | ← |
| 02–06 overnight | The Long Ride | ← | ← |
| 06–08 early | Wanted: Dead or Alive | Half-Hour West | Half-Hour West |
| 08–10 morning | The Rifleman | Half-Hour West | Dodge City |
| 10–12 midday | Dodge City *(Gunsmoke)* | The Rifleman | Wanted: Dead or Alive |
| 12–14 noon | **High Noon** — the feature | ← | ← |
| 14–17 afternoon | The Ponderosa *(Bonanza)* | Weekend Matinee | Weekend Matinee |
| 17–20 evening | The Trail Drive | Brisco County | The Ponderosa |
| 20–22 prime | **The appointment** | Saturday film night | **Bass Reeves** |
| 22–24 late | Late feature | Saturday film night | Late feature |

Simulated over 365 continuous days: no gaps, no overlaps, no circuit breakers, 17,377 programme plays. Re-run over three years to check the appointments advance.

**Split by running time, not by title.** A two-hour daypart holds four half-hours or two hour-longs, and mixing them strands the slot's tail. Gunsmoke, The Rifleman and Wanted: Dead or Alive are the half-hours; Bonanza and Rawhide are the hour-longs. Each morning strip is one show, so the hour reads as *The Rifleman is on at eight* rather than *westerns are on*.

**Rawhide rides behind Bonanza.** 22 episodes cannot strip — a nightly hour exhausts it in three weeks. It shares the evening wheel instead, where it surfaces every other night and stays a treat. Bonanza carries the afternoon alone; at 431 episodes it is 46% of the spine.

**Six serialized shows, six nights, one season a year.** Justified (Mon), Longmire (Tue), Deadwood (Wed), Dark Winds (Thu), Yellowstone (Fri), Lawmen: Bass Reeves (Sun) — `annual_show()` Broadcast Mode, premieres staggered across the four seasons so the channel always has one or two first-run nights and never six. `modern_western_movie` is the bed under all of them. Saturday has no appointment and runs 20:00–24:00 of film, which is where a 168-minute *Hateful Eight* can actually play.

Six appointments on one channel is the most in the lineup, and it works because each has its own night and its own bed. The alternative was leaving 234 episodes of the 2004+ pool unused, or stripping serialized drama nobody can drop into.

**The day-gating comes from the slot, not from `frequency`.** `PRIME_BLOCK` is a weekday dict, the same shape Mystery Theatre uses. `frequency=["MONDAY"]` alone would air Monday's episode all seven nights. Verified over three simulated years: every appointment aired on its own weekday and nowhere else, and seasons advanced s1→s2→s3 with Yellowstone looping back to s1 after its two on-disk seasons.

**Season lengths are counted off disk**, not read from `library-tv.tsv`, which counts `extras/` folders as episodes — it overstates Justified by 39 and Deadwood by 15. Yellowstone has two of its five seasons on disk and the appointment declares two, rather than opening windows for episodes that would resolve to nothing and stall the block.

**Its own timeslot map, split at midnight.** Prime is 20:00–22:00, not the default's 20:00–23:00: the appointment is two episodes of a 45-minute cable drama and a three-hour slot leaves an hour of bed behind it every night. And the default's `night: (23, 2)` wraps midnight, which is the bug Cartoon Network, Nick and Disney each carry their own map to avoid.

No filler and no bumpers — there are no western assets on disk.

### Nightmare Theatre — built
`scripts/channels/nightmare_theatre.py` · `scripts/library/horror.py`

**The inverse of High Noon, and the library forces it.** High Noon is television with a film shelf — 946 episodes carry fifteen hours a day. Horror is the other way round: **242 non-animated features against about 370 usable episodes**, so this is a film channel with a television spine. Seventeen hours of film, seven of TV.

**There is no classic horror television in this library.** Nothing before 1989, and the one 1989 show — Tales from the Crypt — is tagged *Comedy; Crime; Mystery; Science Fiction* and never Horror. The obvious spine, a black-and-white anthology in the Twilight Zone position, does not exist and cannot be built. Only two shows strip: **Tales from the Crypt** (93 eps, half-hours, anthology, host) and **Poltergeist: The Legacy** (87 eps, hour-long, episodic). Everything else that survives is serialized and can only be an appointment.

**The organizing axis is the clock, not the era.** The channel gets darker as the night goes on. A horror channel that runs a slasher at nine in the morning has no idea what it is.

| Slot | Mon–Fri | Saturday | Sunday |
|---|---|---|---|
| 00–02 night | The Witching Hour | Midnight Movie | The Witching Hour |
| 02–06 overnight | Insomnia Theatre | ← | ← |
| 06–09 early | Creature Feature | ← | ← |
| 09–12 morning | The Vault *(pre-1980)* | ← | ← |
| 12–17 afternoon | Matinee of the Damned | ← | ← |
| 17–19 evening | The Legacy | The Legacy | After Hours Animation |
| 19–20 crypt | **Tales from the Crypt** | The Late Shift *(comedies)* | **Tales from the Crypt** |
| 20–22 prime | **The appointment** | Limited Series | **Twin Peaks** |
| 22–24 late | **NIGHTMARE THEATRE** | Midnight Movie | **NIGHTMARE THEATRE** |

Simulated over 365 continuous days: **no gaps, no overlaps, no circuit breakers, no unresolved programs**, 6,283 programme plays.

**Airtime was budgeted against pool size** so nothing cycles faster than about three weeks — classic 39 films / 3 h a day, eighties 50 / 2 h, modern 102 / 6 h, the whole shelf 191 / 5 h. The two strip shows get an hour and two hours respectively, which cycles 93 and 87 episodes in a little over six weeks; any more airtime and they burn through in a fortnight.

**Saturday is the funny night.** The 51 horror-comedies every other key on the channel excludes — *An American Werewolf in London*, *Re-Animator*, *Return of the Living Dead*, *Fright Night*, *Gremlins*, *Creepshow* — play 22:00–02:00, with the comedy half-hours (What We Do in the Shadows, Santa Clarita Diet, Darkplace, Wednesday) at 19:00. A midnight-movie crowd is a different room from a Tuesday at ten.

**Nine annual appointments, more than any other channel.** Six weeknights — Hannibal (Mon), Evil (Tue), FROM (Wed), Yellowjackets (Thu), Ash vs Evil Dead (Fri), Twin Peaks (Sun) — plus three limited series that share Saturday by season: The Walking Dead (spring), Lovecraft Country (summer), Midnight Mass (autumn, landing next to Halloween on purpose). `modern_horror_movie` is the bed under all of them.

**Saturday's three share a slot by season label, not by collection.** Two earlier shapes failed. An `OrderedCollection` of the three replayed their 23 episodes thirteen times a year. Stacking three Programs in a `DailyOrderedCollection` behind a film key was worse: `annual_show(reruns=...)` hangs the bed on the Program, so the first entry resolved every week and the other two **never aired at all** in a 365-day run — and dropping `reruns` did not help, because a Program that resolves to nothing yields the *whole slot* rather than passing the turn to the next item. A label-keyed dict, the same idiom `PRIME_BLOCK` uses for weekdays, resolves exactly one branch a night.

**Halloween is a schedule, not a marathon — it has to be.** `find_active_marathon` returns nothing while `holiday_ctx.is_holiday_season` is true, and Halloween is one, so a marathon triggered on 30 or 31 October **can never fire**. Holidays outrank marathons on exactly the dates a horror channel most wants one. The holiday schedule does the work: horror from noon, three hours of Tales from the Crypt at 17:00, and the Michael Myers run in order at 20:00 and 22:00. Friday the 13th and Krampusnacht are real marathons because their dates fall outside any holiday season.

**Marathons must be `MarathonSequence`, not a collection.** `find_active_marathon` calls `.pick()` on anything that has one, so a `RandomCollection` or `OrderedCollection` handed to a `Marathon` collapses to a single item — the block plays one film, yields, and the rest of the window falls back to the ordinary grid. Only a `MarathonSequence` survives as a sequence.

**Every franchise title is year-bounded.** `movie_by_title` builds a phrase match: `title:"Halloween"` also returns Halloween II, III, 4 and The Halloween Tree, and `title:"Friday the 13th"` returns all eight sequels plus the 2009 remake. Unbounded, an ordered marathon becomes a shuffle of the whole series — the same fix `library/scifi.py` uses for Star Trek 1966.

**Its own timeslot map**, nine slots rather than the default's ten or the `movies` preset's four. A 104-minute mean running time cuts in half in a two-hour daypart and disappears entirely in a six-hour one. `night` is 00–02 and `late` is 22–24 as separate slots, avoiding the wrapping-midnight bug the other custom-map channels each carry.

No filler and no bumpers — there are no horror assets on disk. **This is the channel's biggest gap:** Nightmare Theatre is a *hosted* format and it currently has no host.

### Boomerang — closed

The original plan was "pre-1990 as a hard rule", which kept it clear of CN when CN's vault sat in the 02:00–06:00 overnight dead zone. **The restructure moved that vault to the centre of the channel** — 06:00–08:00 daily, 12:00–14:00 weekdays, Sunday midday, Saturday morning, and the Saturday Syndication Hour. Pre-1990 stopped being free the day that landed.

Counted against the library: of **24 pre-1990 animated series, 22 are now claimed** — 20 by Cartoon Network, plus DuckTales and Chip 'n' Dale on Disney and Schoolhouse Rock on Nick. What is left is:

| Show | Eps | State |
|---|---:|---|
| Smurfs, The (1981) | 405 | flat, no `tvshow.nfo` — will not index |
| Bullwinkle Show, The (1959) | 0 | empty directory |

As of 2026-08-30 the disk problems are mostly fixed, and they turned out not to be the binding constraint:

| Show | State |
|---|---|
| Smurfs, The (1981) | **Fixed** — 8 season folders, 367 eps, `tvshow.nfo` present. Season 9 still missing |
| Bullwinkle Show, The (1959) | **Gone from `tv/`** under any name; files exist elsewhere, unidentified and unplaced |
| Popeye the Sailor (1933) | Indexes, but foldered by broadcast *year* — `season_number:` against it means the year |
| Superman (1941) | Clean; already on CN's Saturday morning via `superman_fleischer_tv` |

So the pool is **one show**. Smurfs alone is not a channel, and everything else it would have programmed is now Cartoon Network's identity rather than its overflow.

Reviving it would mean re-founding it on a different principle than "pre-1990" — a second window on a shared library, the way Nick at Nite and Good Times share sixteen titles by splitting the clock. That is a sharing-rule design, and with three channels already sharing the animation library it needs the collision report to police it rather than another hand-maintained list. **Until then it is closed, not deferred.**

### Cabes Classic Cinema — designed

**1920–1979. 328 live-action films, a 25-day cycle at twenty-four hours a day.**

The channel had been edited five times and never designed — modern film, then
science fiction, westerns, horror, and half the crime shelf all left it in
turn, and none of those edits ever said what remained. It does now: *Hollywood
before the blockbuster*.

`scripts/channels/classic_movies.py` · `scripts/library/movies.py`

    00-03  Noir Alley          pre-1980 crime
    03-06  The Small Hours     the whole shelf, shuffled
    06-09  First Reel          silents, weighted over early sound
    09-12  The Golden Age      1930-69, the studio system
    12-17  The Matinee         1950-69, seasonally tilted
    17-20  The Big Picture     epics, war, musicals
    20-24  New Hollywood       the 1970s — the appointment

The day walks forward through film history and resets at midnight into noir.
Sunday evening is a director spotlight on a monthly rotation — Hitchcock
(twelve films, all pre-1980, so he is this channel's outright) and Kubrick.

**What it cost, and why.** `80s_pure_movie` was the weekday prime and a
byte-identical copy of Totally 80s' `eighties_daytime_movie` — 229 films drawn
by two channels in the same 18:00–23:00 hours. That was the likeliest
same-title collision on the lineup and the open question `movies.py` had been
deferring to "the full grid pass". The decade went to Totally 80s, whose theme
it is, and to Be Kind Rewind, whose oldest shelf it is.

**It carries its own timeslot map now.** Running the generic four-slot
`"movies"` preset was a real part of why the channel read as a residue: four
six-hour blocks is enough structure to hold content and not enough to have an
identity.

Two findings that outlive it:

- **`musical_movie` is six films before 1980.** `MUSICAL_MARQUEE` had been
  handed a weekend slot on the unbounded key, which reaches every era — it
  looked like a 24-film pool and it was six films and eighteen of Be Kind
  Rewind's. Now `classic_musical_movie`, and weighted to a tenth of its block.
- **Two blocks are only two blocks if they draw different things.** The first
  cut of this grid gave First Reel and The Golden Age the same two keys in a
  different order: six hours a day against a 49-film pool, a repeat inside a
  fortnight. It was invisible until airings were counted per key rather than
  per block, and it is why the silents went from 379 airings a year to 105.
- **`WeightedCollection` had never been used.** It had been in
  `logic/structures.py` since the beginning with no consumer. Thirteen silent
  films against thirty-six Golden Age ones is exactly what it is for.

### Be Kind Rewind — built

**1980–present. 1,530 live-action films, a 122-day cycle** — by a wide margin
the largest pool on the lineup, against Classic Cinema's 328 and High Noon's 46.

`scripts/channels/be_kind_rewind.py` · `scripts/library/modern_movies.py`

The framing survived contact with the library: **a video store, not a cinema.**
The organizing axis is the **week**, because the pool is too big and too
cross-genre for anything else — Nightmare Theatre organizes by the clock, High
Noon around a television spine, and this one by the day:

| Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|---|---|---|---|---|---|---|
| Comedy Night | **The Director's Chair** | Recent | **Star of the Month** | **NEW RELEASES** | Blockbuster Night | The Sunday Feature |

    00-02  Cult Corner          02-06  The Overnight Bin (+ the 1980s)
    06-09  The Morning Matinee  09-12  The Back Catalogue
    12-15  Decade Afternoon     15-18  The Afternoon Double
    18-22  PRIME                22-24  The Late Show

**Prime starts at 18:00, and that is measured rather than chosen.** Simulating
all twelve channels over a fortnight and bucketing film minutes by hour of day
showed **18:00–20:00 is the emptiest film hour on the lineup** — Nightmare
Theatre, High Noon and Other Worlds are all running television, and only
Totally 80s has any film there at all. From 20:00, four channels start features
at once. Opening prime two hours early puts this channel's viewer inside a film
before the rest of the lineup begins.

**The 2018 recency fence was not built.** The plan's centrepiece was to give
this channel exclusive rights to everything from 2018 on so the lineup could
keep "zero shared film pools" — a constraint that had already been retired. It
would have cost the genre channels 164 films and required editing five keys
across three channels, all to serve a rule nobody was enforcing any more. What
survives of it is two keys, `recent_movie` and `new_release_movie`, used as
*programming* — Friday's appointment — rather than as ownership.

**Sub-sorting is what the pool size buys.** Genre × decade now exists for every
decade rather than only the 80s and 90s, and Tuesday and Thursday are
title-built spotlights: eight directors (Spielberg, the Coens, Tarantino,
Scorsese, Ridley Scott, Nolan, Fincher, Carpenter) and four stars
(Schwarzenegger, Bill Murray, Sigourney Weaver, Denzel Washington). These are
**title lists, not `director:` queries** — nothing in the repo uses that field,
`ERSATZTV_API.md` does not document it, and it cannot be verified from the
workstation. Every title was checked against `library-movies.tsv` and
year-bounded, because `movie_by_title` is a phrase match and a bare
`title:"Gladiator"` also returns Gladiator II.

### Across the Pond — designed
`scripts/channels/british.py` · `scripts/library/british.py`

**It was billed as "British comedy & panel" and there is not one panel show on disk.** QI, Taskmaster, Have I Got News for You, Would I Lie to You?, Never Mind the Buzzcocks, 8 Out of 10 Cats — all checked, none present. The identity was a promise the library could not keep, which fails F2 the same way a list of negatives does. The channel is now **a British broadcast day, from the morning repeat to the pub lock-in**, which is what the grid had been reaching for all along.

**The axis is the schedule itself.** Every slot is named for what a British listings page calls that hour and keeps that hour's register. It is the last channel on the lineup to get a design pass, and it was still running the default timeslot preset — the only one left.

**Television with a film shelf, and not close** (F5): roughly 1,600 episodes across 45 shows against sixty-odd named British films plus twenty Bond and eight Potter. Film gets Saturday night and the Sunday matinee, and that is all.

| Slot | Mon–Fri | Saturday | Sunday |
|---|---|---|---|
| 00–03 after_hours | Pub Lock-In | ← | ← |
| 03–06 overnight | Closedown | ← | ← |
| 06–09 early | Breakfast *(Bake Off, Clarkson's Farm)* | ← | ← |
| 09–12 morning | The Daytime Mystery | **Saturday Morning** *(Mr. Bean, W&G)* | **The Omnibus** |
| 12–14 noon | The Lunch Break *(Doc Martin, Pilkington)* | ← | ← |
| 14–17 afternoon | Britcom Afternoon | ← | **The Sunday Matinee** *(film)* |
| 17–19 evening | Teatime — **Top Gear** | ← | ← |
| 19–20 seven | **Doctor Who** | ← | ← |
| 20–23 prime | a drama a night | **Saturday Night Cinema** | **Sunday Night on BBC One** *(Attenborough)* |
| 23–24 night | Pub Lock-In | ← | ← |

Simulated over 365 continuous days: **no gaps, no circuit breakers, no unresolved programs, no errors**, 25,208 programme plays (69/day). Day-gating and the special days re-checked over three simulated years: each drama night appears on its own weekday and nowhere else, Bond fired 5 times, Doctor Who Day fired all three years.

*(Block-tail overrun — the last item of a block running past its slot — measures 308 instances over the year. High Noon and Nightmare Theatre show the same thing at the same rate on the same checker, so it is the framework's `yield` behaviour and not this grid.)*

**Prime is seven different pools and the mystery shelf is not one of them.** Poirot, Marple and Morse own 09:00–12:00 on weekdays. Running them at eight as well would be one pool wearing two blocks (G4) *and* would collide with Mystery Theatre on four nights of seven. Instead: Monday gritty (Peaky, Gangs of London), Tuesday thriller (Killing Eve, The Terror, Years and Years), Wednesday after dark (Luther, Black Mirror, I May Destroy You), Thursday period (Sharpe, A Young Doctor's Notebook, Queer as Folk), Friday sketch (Python, Mitchell and Webb, Serafinowicz), Saturday film, Sunday Attenborough.

**Luther is on Wednesday for a reason.** Mystery Theatre's Monday prime draws `british_mystery_tv`, and Luther is in it. That is C1, not taste.

**`british_comedy_tv` could not see Channel 4.** The key was `studio:(bbc OR itv)`, which silently excluded Peep Show, Father Ted, The IT Crowd, Spaced, Derry Girls, Toast of London, Garth Marenghi's Darkplace and Queer as Folk — twelve shows, 287 episodes, including the largest British comedy on disk. Widened in `sources.py` to the full broadcaster list. `british_mystery_tv` was deliberately **not** widened: Mystery Theatre strips it 17:00–20:00 and the only title widening adds is Black Mirror, which is tagged Mystery and is not one (G11).

**The film shelf is named titles, not `british_movie`.** That key is `tag:british OR studio:(BBC|Film4|Working Title|Ealing|Hammer|Warp|DNA)`, and `library-movies.tsv` has no studio column at all — the key census can only report it as 1,858 films "partial". Nobody can size it offline, it depends on index metadata that may be absent, and the Hammer clause reaches into Nightmare Theatre's shelf. Named titles are checkable by `validate_titles`; that key is not.

**The Sunday matinee is at 14:00 because 20:00 was full.** Bond on a bank-holiday afternoon is the most British thing a schedule can do, and it dodges the hour where four channels start features at once (C7). Measured directly rather than asserted: across 28 simulated days, the 15 distinct films Across the Pond airs in its two film slots collide with **nothing** on the other eleven channels at those hours.

**Three content bugs had been live for some time.** Luther was commented out with 20 episodes on disk. The Cornetto trilogy ran as a double bill, because *The World's End* is filed `World's End, The`. *Life of Brian* resolved to nothing, because it is filed `Monty Pythons Life of Brian` without the apostrophe. All three are filing mismatches that no checker caught, because `validate_titles` checks shows and the film titles were never wrong in a way it could see.

**Both marathons were `RandomCollection`s**, which collapse to a single item (G9) — the window played one film and fell back to the grid. Bond is a `MarathonSequence` of twenty year-bounded titles now. **Doctor Who Day stopped being a marathon entirely**: 23 November falls inside Thanksgiving's fourteen-day ramp in most years, and marathons do not fire while `is_holiday_season` is true, so it had never once run. It is a holiday schedule, and the date is registered in `core/registry.py`.

**110 UK commercials went from idle to scheduled.** Categorised country/decade/gate/product some sessions ago and never once used. The channel runs `commercials_uk_spot` channel-wide; the Saturday-morning block overrides to a new `commercials_uk_family_safe_spot`, because eleven of the 116 are beer and spirits and that block is Mr. Bean.

**Shapes that failed:**

- **Three Pub Lock-In variants.** Splitting 380 episodes three ways left the weekend block at 148 and cycling in nine weeks, while Python and Mitchell and Webb were being spent on it. Two variants — Mon/Wed/Fri/Sun against Tue/Thu/Sat — and the sketch shows promoted to Friday prime, where they read as an event.
- **Britcom Afternoon A/B.** The split halved a pool that was already only four weeks deep and made two blocks out of one. Merged; six shows and 241 episodes is six weeks, the first time the slot has cleared F6.
- **Sunday morning as a second Breakfast.** The first Sunday grid ran the Breakfast block twice, 06:00–12:00 — six unbroken hours of Bake Off and Clarkson's Farm, which is the weekday grid printed twice under another name. It is **The Omnibus** now: the week's drama repeated on a Sunday morning, which is the same title in a different presentation (C2, G8) rather than a second helping of the same pool.
- **A crime hour at prime.** Wanted, and dropped: it would have drawn the morning's own pool and handed Mystery Theatre four collisions.

**Still without:** any panel show, which remains the single most fixable identity gap on the lineup. See acquisitions.md.

### Totally 80s — designed

The last channel on the default timeslot preset, and the last one never given a
design pass. Redesigned 2026-09-01. Identity: **the 1980s as a broadcast day** —
not a decade-tagged shuffle but a grid that reads like a station that only ever
carried one decade.

    00-02  Music video          02-06  Music video
    06-08  Cartoons             08-10  Cartoons / sitcoms (school year)
    10-12  The genre wheel      12-14  THE CULT MATINEE
    14-17  The genre wheel      17-20  The syndication strip
    20-23  PRIME                23-24  The Sketch Hour

| Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|---|---|---|---|---|---|---|
| Action Night | Comedy Gold | P.I. Wednesday | **Must See TV** | Friday Night Movies | Sci-Fi Saturday | The Sunday Film |

**What the pass actually found.** The six empty content keys were the known
defect and the smallest of the four:

- **Four hours a day were never programmed.** The schedule named no `early`
  (06:00–08:00) and no `noon` (12:00–14:00), so both fell to
  `fallback_content`. With `night` and `overnight` already on music video,
  **eleven of twenty-four hours were `eighties_music_videos`.** Now six.
- **`evening` and `prime` were handed the same Block object**, so every themed
  night was a two- or three-item collection stretched across 17:00–23:00.
  Monday read as Knight Rider on a loop before anyone noticed Airwolf was
  missing. Prime is 20:00–23:00 now and 17:00–20:00 is its own strip.
- **`night: (23, 2)` wrapped midnight** — the replay bug Cartoon Network, Nick,
  Disney and High Noon each carry a custom map to avoid. Split into
  `late: (23, 24)` and `night: (0, 2)`.
- **Six content keys resolved to nothing.** See
  acquisitions.md; all six are gone and the blocks are
  rebuilt on what the library holds.

**The cult movie is at noon, and that is not a whim.** `eighties_cult_movie` is
Be Kind Rewind's between 22:00 and 06:00 — Cult Corner and The Late Show both
draw it — so a midnight cult slot here would be the same pool on two channels
in the same hour. Be Kind Rewind holds the 12:00–18:00 afternoon open by
keeping the 1980s out of `DECADE_AFTERNOON`, and this is the channel taking
those hours up. The hours rule working in both directions for the first time.

**Three duplicate registry keys were retired.** `eighties_sitcom_cheers`,
`eighties_sitcom_full_house` and `eighties_action_knight_rider` were
byte-identical to `cheers_tv`, `full_house_tv` and `knight_rider_tv`. That is
not cosmetic: section 1 of the collision report groups by *key name*, so one
pool under two names reads as two pools — Totally 80s and Good Times have been
sharing Cheers and Full House for as long as both have existed and the report
never said so. It says so now.

**Weekend evening is a separate collection from the weekday strip**, because
Good Times declares no `evening` in its `WEEKEND` schedule and those three
hours fall through to `fallback_content` — `LATE_NIGHT_SYNDICATION`, which
holds Cheers, The Wonder Years, Married... with Children and Coach. Four titles
that are unreachable here on Saturday and Sunday no matter how clear the
declared grid looks. Worth checking for on the other channels.

### Good Times — rebuilt (2026-09-01)

**Identity: the studio audience.** Multi-camera network sitcom, 1951–1999 — if
it has a laugh track and it aired on CBS, NBC, ABC or FOX, it is here. That is a
*form* and not a date range (F4): the multi-camera sitcom really does end around
2000, when Malcolm in the Middle and The Office replaced it with single-camera.
Everything past that break — single-camera network, cable, streaming, sketch and
alt comedy — goes to Corncob TV.

**Axis: the week is the networks; the day is that network's history.** Each
weekday belongs to one network and walks its roster across the clock, placed by
what fits the hour rather than by date. CBS Monday opens with The Nanny (1993)
at eight in the morning and signs on at six with Dick Van Dyke (1961).

| Day | Network | Named night |
|---|---|---|
| Mon | CBS | CBS Monday, 1993 — Murphy Brown · Northern Exposure · The Nanny |
| Tue | NBC | NBC Tuesday, 1997 — Mad About You · NewsRadio · Frasier · Just Shoot Me! |
| Wed | ABC | ABC Wednesday, 1995 — The Drew Carey Show · Roseanne · Coach |
| Thu | NBC | **Must See TV** — Seinfeld · Mad About You · Frasier · Will & Grace |
| Fri | ABC | **TGIF** — Full House · Family Matters · Perfect Strangers · Mr. Cooper · Sister, Sister · Dinosaurs |
| Sat | CBS | **The Greatest Night** (CBS Saturday, 1973) — M\*A\*S\*H · Mary Tyler Moore · Bob Newhart |
| Sun | FOX + the fourth networks | Fox Sunday — Married… with Children · In Living Color · Martin |

Ten slots, none wrapping midnight: `after_hours` 00–02, `overnight` 02–06,
`early` 06–08, `morning` 08–10, `midday` 10–12, `noon` 12–14, `afternoon` 14–17,
`evening` 17–20, `prime` 20–23, `late` 23–24. Morning, midday and afternoon
carry a season-keyed **book**, so the daytime reshuffles four times a year while
prime, evening and the overnight stay the spine. The noon hour is one show per
day (G3) drawn from that day's network — M\*A\*S\*H Monday, Wings Tuesday, Taxi
Wednesday, Cheers Thursday.

**Counts.** 51 shows, 8,139 episodes, ~2,984 hours — a 124-day cycle at 24
hours a day. By network: ABC 18 shows, NBC 15, CBS 11, FOX/UPN/WB 5. Two days
each for the big three and one for FOX puts every network on a 16–20 week cycle,
comfortably past F6's three-week floor.

**Simulation.** 365 continuous days, 18,010 programme plays, no gaps, overlaps,
circuit breakers or unresolved programs. Re-run over **three years (1,095 days)**
for two things no existing checker covers: every named night aired on its own
weekday and nowhere else, and **zero hours-rule violations** — including the
16,751 airings carrying a seasonal or thematic injection suffix, which an
exact-key match silently misses. That last point is the reusable one: the
injection system rewrites `bob_newhart_tv` as `bob_newhart_tv_auto_fall`, so any
hand-rolled cross-channel check has to normalise the key first or it will report
clean while the collision is live.

**What the rebuild found.**

- **Era was nailed to the clock**, which is what the channel was rebuilt to fix.
  Every morning was the 60s or 70s, every daytime the 90s, every prime
  `MUST_SEE_TV` — seven identical days with a Thursday and a Friday variant. The
  channel walked through history once and then stood still.
- **`night: (23, 2)` wrapped midnight** (G1), the last channel on the lineup
  still doing it.
- **`MUST_SEE_THURSDAY` stacked four appointments in one slot** — the defect
  channel-rules.md cited for G5. Those four are single-camera and left for
  Corncob.
- **The weekend declared no `evening`**, so 17:00–20:00 on Saturday and Sunday
  fell to `fallback_content`.
- **Half the shelf was unreachable.** Frasier (273 episodes), Will & Grace, Spin
  City, Just Shoot Me!, Martin, Sabrina, Northern Exposure, Soap, Mork & Mindy,
  I Dream of Jeannie, The Addams Family and the Smothers Brothers were all on
  disk with **no registry key at all** — invisible to `key_census`, which only
  scores keys that exist.
- **Two keys were wrong the day they were written**, and `key_census` caught
  both. `show_title:"the addams family"` matches nothing — the library stores it
  as *Addams Family The* — and `show_title:"martin"` is a phrase match that also
  returns **Doc Martin**, 83 episodes of Across the Pond's lunch block. G10
  applies to shows, not only to films. Nick at Nite carried the same Addams
  Family bug in its marquee block and has been running six shows, not seven;
  fixed in the same pass.

**The rule that changed, and the airtime it bought.** The written sharing rule
was "Good Times keeps the shared classics out of 21:00–02:00". Nick's *grid* is
finer than that: `nite` 21:00–24:00 holds the pre-1970 seven and `after_hours`
00:00–02:00 holds the 70s shift. Blocking each title only for the hours Nick
actually airs it is what C1 literally asks — and it frees M\*A\*S\*H, Mary Tyler
Moore and Bob Newhart for 20:00–23:00, which is how the 1973 CBS Saturday
lineup, the most famous lineup in sitcom history, became Saturday prime. See
C2 rung 2, restated.

**Verified on the live server, 2026-09-02 (V5).** Playout reset and read back
out of `xmltv.xml`: 170 programmes, **zero gaps and zero overlaps**, and the
network wheel on air as designed — Wednesday and Friday ABC, Thursday NBC, with
Taxi at noon on Wednesday, Cheers at noon on Thursday, ABC Wednesday at 20:00
and Must See TV at 20:00 Thursday. The sharing rule was checked against the
guide rather than asserted: **zero simultaneous airings** of the sixteen titles
shared with Nick at Nite, with Good Times holding Bewitched, The Addams Family
and I Dream of Jeannie in the 02:00–05:00 vault while Nickelodeon runs I Love
Lucy, Dick Van Dyke and Andy Griffith at 21:00–23:37 and Good Times, M\*A\*S\*H
and Sanford and Son at 00:00–01:41. The Addams Family is on air, which it could
not be before the query fix.

**Shapes that failed.** Three rotation designs were drawn and rejected before
the network wheel:

- **The sliding ladder** — the day walks the decades and the weekday sets which
  rung it starts on, so the era-to-daypart mapping precesses. Mechanically it
  works; it reads as arithmetic rather than as television, and it forces 2015
  single-camera comedy into a 6am slot and black-and-white into 7pm.
- **The day owns a year** — Monday is a 1968 broadcast day top to bottom,
  Tuesday 1976. Highest fidelity to "what would have aired", but tune in on
  Monday and you never see past 1970, and every pre-1980 day's prime is
  unschedulable under the Nick at Nite rule.
- **Independent wheels per slot** — each daypart spins its own weekday wheel at
  a different offset, Nick's monthly-bench trick keyed by day. Maximum variety,
  but the day stops reading as a walk and starts reading as a shuffle.

The network wheel beat all three because it makes the era question disappear
rather than answering it: a network's own roster spans 1951–1998, so walking it
across a day *is* the trip through history, and placement can be by fit. The
laugh-track line is what makes that safe — once single-camera comedy is on
another channel, every show left works at any hour, so nothing has to be fenced
into a daypart.

**What it went without.** Sunday is five shows, and the fourth-network shelf is
the channel's thinnest — see acquisitions.md. The 1973 CBS
Saturday night is three of five: All in the Family and The Carol Burnett Show
are both missing, and All in the Family is the single most valuable acquisition
on the list, since Good Times is a Norman Lear spin-off airing without the show
it came from.

### Corncob TV — built (2026-09-01)

**Identity: comedy after the laugh track.** Single-camera, cable, streaming,
sketch and alt. The line against Good Times is the **studio audience, not the
year** — Freaks and Geeks (1999), The Larry Sanders Show (1992) and Mr. Show
(1995) are single-camera with no audience and are here; Frasier (1993) and Will
& Grace (1998) are multi-camera and are not. Between them the two channels hold
the whole comedy shelf and **neither is defined by what the other is not** (F4).
The split was forced by arithmetic: one channel holding both is 128 shows and
~4,700 hours, a 195-day cycle, six times slower than F6's floor.

**Axis: the clock gets stranger.** Nightmare Theatre's shape in another
register. Morning is the network single-camera sitcom, afternoon the office
comedies, evening cable, and the small hours the far end of the channel. Era is
not the axis here and does not need to be.

| Slot | | |
|---|---|---|
| 00–02 | The Deep End | the newest and strangest — where a six-episode show is an asset |
| 02–06 | The Vault | the alt back catalogue; Red Green (301) and Penn & Teller (89) carry it |
| 06–08 | Sign-On | the gentlest half-hours on the channel |
| 08–10 | The Morning Bench | three pools, a month at a time |
| 10–12 | The Syndication Hour | the channel's own register, in daylight |
| 12–14 | The Noon Hour | one show, one day (G3) |
| 14–17 | The Workplace | the office comedies |
| 17–20 | The Cable Hour | four pools, a month at a time, offset from the morning |
| 20–23 | the named night | |
| 23–24 | The Late Shift | sketch — and the Limited Series on Sunday |

**The named nights.** Seven comedy traditions, one a night:

| Mon | **The Gang** | It's Always Sunny · Workaholics · Trailer Park Boys |
|---|---|---|
| Tue | **Single Camera** | Malcolm · Scrubs · Arrested Development · My Name Is Earl |
| Wed | **The Cringe** | Curb · Nathan For You · The Rehearsal · Jury Duty |
| Thu | **Must See Thursday** | The Office · Parks and Rec · 30 Rock · Community |
| Fri | **Corncob After Dark** | Tim and Eric · Detroiters · I Think You Should Leave · The Chair Company |
| Sat | **Saturday Night Sketch** | Mr. Show · The State · Key & Peele · Chappelle's Show · Strangers with Candy |
| Sun | **HBO Sunday** | Larry Sanders · Veep · Silicon Valley · Flight of the Conchords · Eastbound & Down |

Friday is the Tim Robinson lineage read as a night, and it is the channel's own
name — Corncob TV is a Tim and Eric segment.

**Must See Thursday, and why it is not an appointment.** These four came off
Good Times, where they were four stacked `annual_show` appointments in one slot
and the standing example for G5. Here they are a plain ordered `Block` of
content keys. That is the whole fix and it is worth stating as a rule: **an
`annual_show` Program pins a season and episode, so a collection that wraps
inside its slot replays it; a content key advances.** Four items in a
three-hour slot wrap twice either way — with keys, that is simply the next
episode. Use the appointment machinery when you want a *season a year*, not
when you want a *named night*.

**The Limited Series (Sunday, 23:00).** One short show a season, chronological,
about two episodes a Sunday: Party Down in winter, Enlightened in spring, Wet
Hot American Summer in summer, Vice Principals in autumn. This is G6 used
deliberately — the shelf is full of 16-to-22-episode shows that cannot strip
and are too serialized for a tune-in slot, and a season of Sundays is exactly
their size. Measured over three years: 70–78 airings each, so every one gets a
full season and a short repeat at the tail. Registered `Chronological` (G8),
because a limited series shuffled is not a limited series.

**Counts.** 65 shows, ~4,200 episodes, ~1,530 hours — a 64-day cycle at 24
hours a day.

**Simulation.** 365 continuous days, 17,520 programme plays, 48 slots every
single day, no gaps, overlaps, circuit breakers or unresolved programs. Three
years confirms each named night on its own weekday, all four Limited Series
shows cycling, and zero violations of the one hours rule below.

**The one sharing rule.** Cartoon Network's Adult Swim airs The Eric Andre Show
and Check It Out! with Dr. Steve Brule inside `AS_ORIGINALS_B`: 20:00–23:00
Tuesday and Thursday, 23:00–24:00 Sunday, 00:00–02:00 Monday.
channel-coverage.md already prescribed the C2 rung-1
split for exactly these — Adult Swim first-run, Corncob syndication — and The
Syndication Hour at 10:00–12:00 is it. Adult Swim is not on air at that hour on
any day, so **the split holds by the clock rather than by the grid remembering
it** (C3). Both channels carry the same ten-slot map, which is deliberate: it
makes that fact readable off either file instead of needing a simulation.

Everything else is unshared. The British comedies are Across the Pond's, the
horror-comedies (What We Do in the Shadows, Santa Clarita Diet, Ash vs Evil
Dead, Garth Marenghi's Darkplace) are Nightmare Theatre's, and Monk, Psych,
Bored to Death and Elsbeth are Mystery Theatre's. The collision report shows
**zero new pairings** at any tier after this channel went in.

**No bumpers.** There are no Corncob assets on disk. Adult Swim bumpers exist
and are Cartoon Network's; borrowing them would put its branding on a channel
it does not own, which is the exact mistake G12 was written for. Ships silent.

**Verified on the live server, 2026-09-02 (V5).** Playout reset and read back
out of `xmltv.xml`: 162 programmes, **zero gaps and zero overlaps**. Thursday
at 20:00 is Parks and Recreation, 30 Rock, Community and The Office, with How
To with John Wilson on the late shift. The Adult Swim hours rule holds in the
guide: The Eric Andre Show and Check It Out! with Dr. Steve Brule appear only
between 10:20 and 11:55, never in Cartoon Network's windows. The channel adds
**no same-title collisions** to the lineup.

**What the build found.** The comedy shelf was far larger than any channel
could see. **Scrubs (243 episodes) and Frasier (273) had no registry key at
all** between them — `key_census` scores keys that exist, so a show with no key
is invisible to it, and the only way to find them was diffing
`library-tv.tsv` against every title named anywhere in `library/`. Sixty-four
keys were registered for this channel; twelve more went to Good Times in the
same pass.

**What it went without.** The Larry Sanders Show opens HBO Sunday with **13 of
its 89 episodes** on disk — the one demonstrably partial series in the roster.
Saturday Night Sketch is the thinnest named night at five shows, and the
channel has no variety register at all. See
acquisitions.md, which now opens with a ranked shortlist.

### Travelers Table
Gains the nature documentaries: Planet Earth I–III, Blue Planet II, Seven Worlds One Planet, Prehistoric Planet, Cosmos, Life (2009). Plus 236 episodes of Japanese Food Noodles from `youtube/`.

### The Beat
Music videos only — no Daria, no Jersey Shore, and *The Beatles: Get Back* is a documentary, not a music video. 64 artist folders, currently unstructured. Decide the organizing axis before foldering, because the folder tree becomes the tag schema. MTV's own rotation blocks are the obvious model: morning mix, afternoon countdown, late-night alternative.

---

## Programming mechanics

### Available now, no framework change

**Chronological on weekdays, shuffled on weekends.** `_unwrap_nested_structure` resolves any dict without a `title`/`query` key by day label, so this is valid as a block item today:

```python
{"WEEKDAY": {"title": "DuckTales", "order": "Chronological"},
 "default":  {"title": "DuckTales", "order": "Shuffle"}}
```

Simulates new episodes on weekdays and reruns on weekends.

**Season-then-wait.** `annual_show(premiere_year=, premiere_season=, reruns=, loop=True)` — Broadcast Mode. In production on sitcoms, detective, scifi and Disney. `premiere_season` takes a bare season (`"FALL"`) or a season/weekday pair (`("FALL", "THURSDAY")`), which pins the premiere to that day of the week. Absent from the cartoon channel.

**Short series as yearly events.** Anything too short to strip becomes an annual appointment rather than a rounding error: Dragon Ball DAIMA (20), Attack on Titan Junior High (12), Over the Garden Wall (10), Police Squad! (6), FLCL (6), the Star Wars *Tales* shorts (6 each), Macross Plus (4).

**Probabilistic blending.** `Feather(content, ratio)` inside a `SeasonalBlock` substitutes at a probability scaled by season strength. Right tool for rare specials — the 1941 Superman shorts dropping in occasionally, say.

**Seasonal swaps.** `SeasonalBlock(base=..., seasonal={"SUMMER": Swap(X)})`. Four buckets.

### Built this session

**Month labels.** `derive_labels()` now emits a month label (`JANUARY` … `DECEMBER`) alongside the existing weekday, season, daypart, holiday and positional labels. Month variants resolve anywhere the label system reaches:

```python
MIDDAY_BLOCK = {"JULY": SUMMER_BLOCK, "OCTOBER": SPOOKY_BLOCK, "default": REGULAR}
```

`scripts/core/registry.py::MONTHS` · `scripts/core/states.py::derive_labels`

**`monthly_rotation()`.** Builds a month-keyed variant dict that cycles a list, so short shows stay in rotation instead of being ground down. In production on Nick, where four strips share one four-pool bench:

```python
from scripts.logic.factories import monthly_rotation
MIDDAY = monthly_rotation([BLOCK_A, BLOCK_B, BLOCK_C])   # Jan→A, Feb→B, Mar→C, Apr→A…
MIDDAY = monthly_rotation([SUMMER, WINTER], start_month=6)
```

Returns a plain dict the pipeline already understands — no new resolution logic. `scripts/logic/factories.py`

**Title validation.** `scripts/testing/validate_titles.py` walks each channel's config tree and checks that every scheduled title exists in the library and every bare content key exists in `MASTER_SOURCES`.

```bash
python3 -m scripts.testing.validate_titles                  # all channels
python3 -m scripts.testing.validate_titles cartoon_network  # one
python3 -m scripts.testing.validate_titles --quiet          # findings only
```

Matches on token sets, so the library's `Flintstones, The (1960)` form and a scheduled `the flintstones` line up. It is query-aware: a broad title narrowed by `studio:`/`tag:`/`genre:` is not flagged, an `OR` query passes if any branch resolves, and bare `title:` lookups that name an episode or special are reported separately as unverifiable rather than missing. Exits non-zero when it finds something, so it can gate a build.

Reads the manifests in `reference/`, so it runs offline with no ErsatzTV.

### Still needs building

**Collision report.** The framework has no cross-channel awareness. Sharing rules stay a convention until something can simulate N days across all channels and flag a title double-booked in the same hour. `visualize_week.py` and the walker in `validate_titles.py` are the two halves of it — same traversal, plus a time dimension. Deferred through the Cartoon Network restructure, on the grounds that CN's eviction list was written down rather than needing deriving. That list is now cleared, so the next time two channels overlap nothing will be holding the answer — and `common.HALLOWEEN_TEEN_FRIGHTS` is already one live example. See next-session.md.

---

## Sharing rules

> Stated as rules in [channel-rules.md §3](channel-rules.md#3-curating-across-channels) — C1 is the rule, C2 the escalation ladder. What follows is the per-pair history.

No channel airs a title *while* another channel is airing it. Sharing itself is fine and often the point, because the two channels mean different things by it.

**Nick at Nite vs. Good Times — restated 2026-09-01.** Fifteen shared titles,
and the rule is now split the way Nick's own clock is split rather than as one
blanket window. Nick's `nite` is 21:00–24:00 and holds the pre-1970 seven (I Love
Lucy, Dick Van Dyke, Andy Griffith, Bewitched, I Dream of Jeannie, The Addams
Family, Gilligan's Island); its `after_hours` is 00:00–02:00 and holds the 70s
shift (Mary Tyler Moore, Bob Newhart, Taxi, M\*A\*S\*H, Sanford and Son, Good
Times, Soap, Mork & Mindy, Smothers Brothers). Good Times keeps all fifteen and
stays out of each title's *own* hours — which freed M\*A\*S\*H, Mary Tyler Moore
and Bob Newhart for 20:00–23:00 and made the 1973 CBS Saturday lineup its
Saturday prime. Verified over three simulated years: zero violations.

**I Love Lucy — the exemption, restated 2026-09-02.** Lucy TV runs it 24/7, so
*any* airing anywhere collides with it and no hours rule can fix that. C5 is the
answer — name the exemption and earn it — and it covers **three** channels, not
two: Lucy TV, Nick at Nite (21:00–24:00), and **Good Times**, where it signs the
channel on at 06:00 on both CBS days. Stated by the operator: Good Times is the
studio-audience channel and I Love Lucy is the show that invented the form, so
it belongs there. The one binding constraint is Nick at Nite's window, which
Good Times' prime and late slots respect.

The Lucy Show and The Lucy-Desi Comedy Hour are **not** covered and stay with
Lucy TV alone.

*Done in code when Nick was built.* Good Times used to run a collection literally named `NICK_AT_NITE` in its 23:00–02:00 slot. That is now `LATE_NIGHT_SYNDICATION` — Cheers, Wonder Years, Married… with Children, Newsradio, Drew Carey, Wings, Mad About You, 3rd Rock, The Nanny, Coach — none of them shared. The winter prime variants swapped in `CLASSIC_SITCOMS_60s_70s`, which reaches into 21:00–23:00, so they now take `EIGHTIES_NINETIES_CLASSICS` instead; and the channel fallback moved off the classics for the same reason. Mornings, daytime and the 02:00–06:00 overnight are untouched.

**Disney vs. Cartoon Network — settled.** Everything Cartoon Network was holding for Disney has gone back: `DISNEY_MORNING`, `DISNEY_AFTERNOON`, Gargoyles, and the Star Wars Day marathon that used to run against Disney's own. CN's Halloween schedule no longer reaches for `common.HALLOWEEN_TEEN_FRIGHTS` either — it has `animation.CN_HALLOWEEN`, built from Courage and Infinity Train. Other Worlds was also borrowing CN's Star Wars block at 06:00 and now uses Disney's `star_wars_animation_tv` key.

**Nick vs. Cartoon Network — settled.** The Nicktoons Vault is retired, and Daria, Animaniacs and Pinky and the Brain are Nick's alone. Ed, Edd n Eddy went the other way: it is a Cartoon Cartoon and had been filed under Nicktoons.

**Still crossed:** `common.HALLOWEEN_TEEN_FRIGHTS` is Gravity Falls (Disney), Infinity Train and Courage (both Cartoon Network), and **Nick** is the only channel still using it — so on Halloween Nick airs three shows it does not own. Nick's problem to fix, in Nick's session; it wants a `NICK_HALLOWEEN` the way Disney and CN now have their own.

**Other Worlds vs. Cabes Classic Cinema — settled by eviction.** Both handed
Saturday prime to `movies.SCI_FI_SHOWCASE`, and because each drew a different arm
of the collection they never shared a *key* — nothing flagged it while both ran
sci-fi features 20:00–24:00 every week. Classic Cinema gave it up. Its morning
block also moved to `classic_hollywood_pure_movie`, which is the same 1950–69 era
with science fiction excluded; the unfiltered key was putting Forbidden Planet,
Day the Earth Stood Still and Godzilla opposite Other Worlds' own classic sci-fi
film. Other Worlds gave back Disney's `star_wars_animation_tv` in exchange.

**High Noon vs. Cabes Classic Cinema — settled by eviction.** Classic Cinema ran
`WESTERN_MATINEE` — all 46 western films — across *both* weekend afternoons,
twelve hours a week, and it was the only claim on the pool. High Noon takes the
shelf whole, the same eviction Other Worlds got for science fiction. Classic
Cinema's weekend afternoon is now `movies.WEEKEND_MATINEE`, a `SeasonalBlock`
on its own era with the four `classic_hollywood_<season>_movies` keys feathered
on top — which is where `..._summer_movies` and `..._fall_movies` finally get
used, both having been in the registry and on no channel.

`classic_hollywood_pure_movie` also drops westerns now, not just science
fiction. The 1950–69 slice is The Searchers, Shane, Giant, The Magnificent
Seven, the Leone trilogy and Butch Cassidy — eleven films that are the western
channel's centre, and they were on Classic Cinema's weekday afternoon.
An era split was considered and rejected: 46 films is too few to halve, and the
pre-1980 half is precisely the half High Noon cannot do without.

**Mystery Theatre vs. Cabes Classic Cinema — settled by era split.** Both want
crime film and both run it overnight. `mystery_crime_movie` (365 films) is now
`classic_crime_movie` (pre-1980, 74) for Classic Cinema and `modern_crime_movie`
(1980+, 291) for Mystery Theatre. Neither can draw the other's film. This is the
first era-split on the lineup and it is the pattern to reach for when two
channels have an equally real claim on one genre.

**Mystery Theatre vs. Across the Pond — shared on purpose.** Poirot and Miss
Marple air on both. Decided, not an oversight: both channels have a real claim
and the hours do not overlap. Across the Pond airs them roughly three times as
often, which is fine.

**Adult Swim vs. Corncob TV.** Tim and Eric, The Eric Andre Show, Check It Out! with Dr. Steve Brule. Adult Swim is **first-run** — chronological, appointment-scheduled, late. Corncob is **syndication** — shuffled, daytime, drop in anywhere. Same show, two presentations. This generalizes: it's the cross-channel form of the chronological-weekday / shuffle-weekend pattern.

---

### The era line — the film lineup, settled (2026-08-30)

The whole film library now splits three ways on two dates, and the dates were
already in `filters.py` as `PRE_EIGHTIES_ERA` / `MODERN_FILM_ERA` — the same
line Mystery Theatre and Classic Cinema had already cut the crime shelf along,
so nothing had to be re-drawn to use it.

| Channel | Era | Films |
|---|---|---:|
| Cabes Classic Cinema | 1920–1979 | 328 |
| Totally 80s | 1980–1989 (as its *theme*) | 296 |
| Be Kind Rewind | 1980–present | 1,530 |

Classic Cinema and Be Kind Rewind are **disjoint by construction** — no title
can appear on both, which is the cleanest relationship two channels on this
lineup have. Totally 80s and Be Kind Rewind genuinely share the 1980s, and that
is kept by hours rather than by eviction. Be Kind Rewind's 1980s shelf is
scheduled 00:00–06:00 and 22:00–24:00 only, and the decade is unreachable from
its afternoon and prime keys **at the key level** rather than by the grid
remembering to avoid it. Totally 80s runs film 10:00–17:00 and, on Friday and
Sunday, 20:00–23:00.

**Updated 2026-09-01.** Totally 80s used to run film to 23:00 seven nights;
after its design pass it runs film across the middle of the day and on two
prime nights, and the 17:00–20:00 hours it used to fill with film are now a
television strip. **One hour is still shared:** Friday and Sunday prime run to
23:00 against Be Kind Rewind's Late Show, which starts at 22:00 and draws
`eighties_cult_movie` and `80s_pure_movie`. That hour predates the redesign and
is unchanged by it. Closing it means moving The Late Show or splitting Totally
80s' prime; it is recorded in [KNOWN_ISSUES.md](../KNOWN_ISSUES.md) and was
deliberately left alone rather than fixed from inside an 80s-channel pass.

### Measuring it: `same_title_check.py`

The collision report answers "are two channels airing the same *kind* of thing
at once". `scripts/testing/same_title_check.py` — new this session — answers the
literal question the rule asks: **can the same title be on two channels in the
same hour?** It resolves both keys' Lucene queries against
`library-movies.tsv` and intersects the title sets, so a pair whose sets are
disjoint is cleared no matter how similar the keys look.

That distinction matters immediately. The report flags Classic Cinema's
`classic_crime_movie` against Mystery Theatre's `modern_crime_movie` every
night as SAME GENRE, and it is harmless — the two were split at 1980 precisely
so neither can draw the other's film. Meanwhile it could not see that Be Kind
Rewind's `90s_movie` shared **29 titles** with Nightmare Theatre's
`horror_movie` and aired opposite it nineteen times a fortnight.

**The uncomfortable finding: the lineup already had 28 confirmed same-title
collisions before this session**, none of them visible to any existing tool.
"Zero shared film pools" was never the same claim as "no simultaneous airings",
and the largest are between channels built long before this one:

| Pair | Airings / 14d | Shared titles |
|---|---:|---:|
| Mystery Theatre `modern_crime` vs High Noon `modern_western` | 36 | 6 |
| Mystery Theatre `modern_crime` vs Other Worlds `modern_scifi` | 22 | 10 |
| High Noon `modern_western` vs Nightmare `modern_horror` | 21 | 2 |
| Mystery Theatre `modern_crime` vs Nightmare `eighties_horror` | 20 | 14 |
| Totally 80s `eighties_suspense` vs Nightmare `horror_movie` | 17 | 36 |

None of that was introduced here and none of it is fixed here — it is the next
session's work, and it now has a tool that can measure whether a fix worked.

The two channels built this session went from 25 colliding pairs to 18 (42
airings a fortnight, against ~8,300 total) by adding `NO_HORROR` / `NO_WESTERN`
to the decade keys and moving the 1980s shelf off Mystery Theatre's 23:00–02:00
hours. What remains is genuine cross-genre sharing with Other Worlds and
Mystery Theatre, and it is **deliberately left**: eliminating it would mean
excluding science fiction and crime from a general movie channel, which is most
of what a video store stocks.

## Known gaps

| | Detail |
|---|---|
| **YouTube unused** | 637 eps — Japanese Food Noodles 236, Best of the Worst 154, Historia Civilis 88, On The Line 80, Timothy Wilmots Woodworking 51, Pedulla Studio 28 |
| **Features with zero uses** | `alternating_seasons()`, `timeslot_commercials`, `global_filter`, `seasonal_blocks` param — `loop_restart_season` is now exercised by Disney's four Saturday events |
| **Switched off globally** | `ENABLE_COMMERCIALS` (110 tagged 90s spots idle), `ENABLE_FILLER` (why bumpers never fire outside the 5 branded blocks) |
| **Assets not wired** | ~940 per-show Toonami bumpers reachable by tag, referenced by nothing; 5 AS outros with no registry key; `fox_kids_*` keys referenced but undefined over an empty folder |
| **Empty commercial decades** | 50s, 60s, 70s, 00s, 10s, 20s — the 00s gap matters most |
| **Broken on disk** | Smurfs (405 eps, unindexable), Bullwinkle (empty dir) |
| **Dead code** | `FOX_KIDS_BLOCK`, `ACTION_ANIMATION`, `SYNDICATED_CARTOONS`, `BRANDING_90S_KIDS` |
| **Largest untapped** | ~1,390 films from 1990 on |
| **Manifests overstate episodes** | `library-tv.tsv` counts `extras/` folders as episodes — Justified reads 117 for 78, Deadwood 51 for 36, Rifleman 167 for 166. Count off disk before sizing an `annual_show()` |
| **Genre tags are not genres** | Breaking Bad, Westworld and Cowboy Bebop all carry a Western tag. `western_tv` returns all three, which is why High Noon names its shows instead |
| **No classic horror TV at all** | Not one pre-1989 horror show is on disk — no Dark Shadows, Kolchak, Night Gallery, Tales from the Darkside, Monsters, Thriller. This is why Nightmare Theatre came out film-led. Shopping list in acquisitions.md |
| **Nightmare Theatre has no host** | A hosted format running unhosted, with no horror bumpers on disk. Joe Bob Briggs / Svengoolie / Elvira are worth more to the channel than most shows |
