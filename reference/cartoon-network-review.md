# Cartoon Network channel — programming review

Reviewed `scripts/channels/cartoon_network.py` + `scripts/library/animation.py` against the library at `/media` on 2026-08-29.

Companion references: [library-animation-tv.md](library-animation-tv.md) · [library-animation-movies.md](library-animation-movies.md) · [bumper-inventory.md](bumper-inventory.md) · [library-tv-all.txt](library-tv-all.txt) · [library-movies-all.txt](library-movies-all.txt)

---

## 1. The grid as actually coded

The module docstring describes a different channel than the code builds. Ignore the docstring; this is the real grid.

| Slot | Hours | Mon–Fri | Saturday | Sunday |
|---|---|---|---|---|
| overnight | 02–06 | Classic Cartoons | Classic Cartoons | Classic Cartoons |
| early | 06–08 | Disney Morning | Classic Cartoons | Classic Cartoons |
| morning | 08–10 | Superhero Hour *(Marvel Hour in spring)* | Saturday Morning | Classic Cartoons |
| midday | 10–12 | Cartoon Network Classics | Superhero Hour | Classic Cartoons |
| noon | 12–14 | Nicktoons Vault | Disney Afternoon *(WB in spring)* | Animation Showcase |
| afternoon | 14–17 | Disney Afternoon *(WB in spring)* | Nicktoons Vault | Animation Showcase |
| evening | 17–20 | **Toonami** | Anime Block | Animation Showcase |
| prime | 20–23 | AS Prime A *(M/W/F)* · B *(Tu/Th)* | Animation Showcase | FOX Primetime |
| night | 23–02 | AS Night A *(M/W/F)* · B *(Tu/Th)* | Anime Block | AS Night B |

Two things the docstring claims that the code does not do: overnight is *not* Adult Swim (it's Hanna-Barbera), and prime is 20:00, not 19:00.

## 2. Where the focus actually went

Weekly airtime by source family, out of 168 hours:

| Source family | Hrs/wk | Share |
|---|---:|---:|
| Hanna-Barbera / theatrical shorts vault | 38 | 22.6% |
| Adult Swim | 33 | 19.6% |
| **Disney** | 27 | **16.1%** |
| Toonami | 15 | 8.9% |
| Nickelodeon | 13 | 7.7% |
| DC/Marvel superhero | 12 | 7.1% |
| Animated features | 11 | 6.5% |
| **"Cartoon Network Classics"** | 10 | **6.0%** |
| Saturday Anime Block | 6 | 3.6% |
| FOX Primetime | 3 | 1.8% |

**Disney gets 2.7× the airtime of the Cartoon Network block.** And the CN block isn't CN: of its ten shows, *Daria* is MTV, *Gravity Falls* and *The Owl House* are Disney, *Animaniacs* and *Pinky and the Brain* are WB/Kids' WB. Actual Cartoon Network originals — Dexter, Powerpuff Girls, Johnny Bravo, Courage, Infinity Train — hold **5 of 168 hours, about 3% of the week.**

Meanwhile *Ed, Edd n Eddy*, CN's longest-running original, is filed inside **Nicktoons Vault**.

## 3. Cartoon Network shows you own and never air

Every one of these is in the library with a usable episode count and appears nowhere in `animation.py`:

| Show | Eps | Why it matters |
|---|---:|---|
| Adventure Time | 278 | Largest unused CN original in the library |
| Steven Universe (+ Future) | 174 | — |
| Space Ghost Coast to Coast | 81 | The show Adult Swim was built out of |
| Samurai Jack | 62 | 27 Toonami bumpers on disk, zero airtime |
| The Brak Show | 28 | Original Adult Swim Sunday launch night |
| Primal | 20 | — |
| Over the Garden Wall | 10 | CN's one great miniseries |
| Venture Bros. | 81 | Adult Swim flagship, entirely absent |
| Tim and Eric Awesome Show | in library | absent |

And the anime side, all owned, all unaired: **Fullmetal Alchemist Brotherhood** (64), **One Piece** (574), **Death Note** (37), **Attack on Titan** (87), **Neon Genesis Evangelion** (26), **Samurai Champloo** (26), **Space Dandy** (26), **FLCL** (6). FLCL, Champloo, Bebop and Space Dandy are the four shows most people mean when they say "Adult Swim anime" — one of the four airs.

Period-correct syndication also sitting idle: ThunderCats (125), He-Man (130), Transformers (98), Rocko's Modern Life (100), Tiny Toon Adventures (98, only in the spring WB swap), Beast Wars (52), Schoolhouse Rock (51), Street Sharks (43), Where on Earth is Carmen Sandiego (40), What's New Scooby-Doo (39), The Tick 1994 (36), Hong Kong Phooey (31).

## 4. Branding is wired to the wrong era

`build_playout` sets `filler_content="adult_swim_bumpers"` channel-wide, and only the four `AS_*` blocks and `TOONAMI_BLOCK` override it. Every other block inherits it. That means roughly **14 of every 24 hours — including Saturday-morning Scooby-Doo and the 6am Disney block — runs Adult Swim bumps between shows.**

There is no fix available in the current asset tree, because `filler/bumpers/cartoon network/general/` is **empty**. You have zero daytime Cartoon Network branding: no checkerboard era, no Powerhouse, no CN City, no "Yes!" era. That single gap is what stops the daytime half of this channel from feeling like Cartoon Network.

The Toonami block has the inverse problem: it draws from `tag:toonami AND (tag:bumps OR tag:general)` = **21 files**, while ~940 per-show Toonami bumpers sit on disk unreachable because nothing wires per-show bumpers. Adult Swim draws from 5,316. See [bumper-inventory.md](bumper-inventory.md).

You also have **110 tagged 90s commercials** and commercials are globally disabled (`ENABLE_COMMERCIALS = False`, `DEFAULT_COMMERCIAL_DURATION = 0`). For a nostalgia channel that is the single highest-value asset going unused.

## 5. Against the historical grid

CN's peak-era weekday, roughly 1997–2003:

| Real CN | Your channel |
|---|---|
| 9am–noon **Cartoon Cartoons** — Dexter, PPG, Johnny Bravo, Ed Edd n Eddy, Courage | 8–10 Superhero Hour, 10–12 half-CN block |
| noon–2pm the **vault** — Looney Tunes, Tom & Jerry, Scooby | noon–2 Nicktoons Vault |
| 4–7pm **Toonami** | 5–8pm Toonami ✓ closest match in the whole grid |
| 11pm–6am **Adult Swim** | 8pm–2am Adult Swim; **2–6am is Hanna-Barbera** |
| Fri 8–10pm **Cartoon Cartoon Fridays** | nothing — Friday is an ordinary weekday |
| Sat 7–11pm **Toonami Saturdays** (2003+) | Sat evening is a weaker generic Anime Block |
| Summer daytime stunt programming | no summer treatment exists |

Four specific inversions:

1. **Overnight 02–06 is the vault, not Adult Swim.** In the real thing 2–6am was ATHF and anime reruns. This is the largest single historical inversion in the grid, and it's 28 hours a week.
2. **Adult Swim's internal halves are swapped.** `AS_PRIME` (20–23) is King of the Hill / Family Guy / Archer / Rick and Morty — that's the 2009–2014 acquisitions era. `AS_NIGHT` (23–02) is ATHF / Harvey Birdman / Bebop — that's the 2001–2005 Williams Street era. Historically the originals ran *first* at 11pm and the syndicated shows filled the back half toward 6am. *(Defensible as-is if you want easier viewing at 8pm — but it is backwards relative to memory.)*
3. **Toonami never runs Saturday.** Saturday evening and night both get `ANIME_BLOCK` (Pokémon + Dragon Ball + DBZ + an open query), which is a thinner duplicate of the Toonami lineup. Toonami Saturdays 7–11pm is the defining 00s Toonami memory.
4. **Sunday is a Pixar/Ghibli movie day** — noon through 8pm, plus Saturday prime, is 11 hrs/wk of `ANIMATION_SHOWCASE` drawing from Ghibli/Disney/Pixar/DreamWorks. None of that ever aired on Cartoon Network. Meanwhile the films that *are* CN-shaped — Batman: Mask of the Phantasm, The Iron Giant, Transformers: The Movie (1986), Akira, Ghost in the Shell, Titan A.E., Who Framed Roger Rabbit, Steven Universe: The Movie, DBZ: Battle of Gods — are never scheduled.

## 6. Seasonal and event programming is mostly inert

- **Seasonal variants only exist for spring.** `CN_MORNING_HERO` and `CN_AFTERNOON_BLOCK` each define exactly one swap (`SPRING`). Summer, fall and winter are identical to the base. Summer is the miss that matters most — 90s/00s CN *was* summer weekday mornings.
- **Marathons effectively never fire.** Cowboy Bebop 1%, DBZ 2%, Simpsons 1%, Toonami 1% — about a 5% chance any marathon runs on a given day, once every three weeks. Real CN ran marathons as scheduled appointments: Thanksgiving Toonami, New Year's, Memorial Day, "Invaded", "Sleepover Camp". Date-anchoring these would fire them ~20× more often and make them feel like events rather than accidents.
- **The Simpsons marathon takes 4pm–10pm.** The Simpsons is Fox and never aired on Cartoon Network; a six-hour Simpsons takeover is the wrong flag on this channel. Fine on a separate Fox/sitcom channel.

## 7. Bugs and dead code

| Issue | Location | Effect |
|---|---|---|
| `fox_kids_intro` / `fox_kids_bumper` referenced but defined nowhere | `library/branding.py:15-17` | `BRANDING_90S_KIDS` resolves to nothing; disk tree is empty too |
| `FOX_KIDS_BLOCK` never referenced | `library/animation.py` | dead code, and broken per above |
| `ACTION_ANIMATION` never referenced | `library/animation.py` | dead code |
| `SYNDICATED_CARTOONS` never referenced | `library/animation.py` | dead code — and it holds ThunderCats-era content you want |
| `cowboy_bebop_bumpers` defined, never used | `library/sources.py` | 72 bumpers unreachable |
| `Bullwinkle Show, The (1959)/` is an empty directory | media | show cannot air |
| `Smurfs, The (1981)/` — 405 episodes, flat, no season folders, no `tvshow.nfo` | media | almost certainly won't index into ErsatzTV |
| `"anime_action_tv"` is an unbounded `type:show AND genre:anime AND genre:action` query inside `ANIME_BLOCK` | `library/animation.py` | pulls TV-MA titles (Vinland Saga, Blue Eye Samurai, Attack on Titan) into the **Saturday 17:00** slot |
| `use_epg_group=False` on Toonami and all AS blocks | `library/animation.py` | the guide shows individual episodes instead of "Toonami" / "Adult Swim" — the block name in the EPG is a large part of the feel |
| `SCHEDULES = {"WEEKDAY": DAILY_SCHEDULE, "WEEKEND": DAILY_SCHEDULE}` | `channels/cartoon_network.py` | both keys point at one dict; the `WEEKEND` key does nothing (all weekend logic lives in the per-slot variant dicts) |

## 8. Recommended grid

Keeps the framework's default timeslots. Changes are marked ▲.

| Slot | Mon–Thu | Friday | Saturday | Sunday |
|---|---|---|---|---|
| 02–06 overnight | ▲ **Adult Swim Late** (acquisitions + repeats) | ▲ AS Late | ▲ **Toonami Midnight Run** | ▲ AS Late |
| 06–08 early | ▲ **The Vault** (Looney Tunes, Tom & Jerry, Popeye, HB) | ▲ The Vault | ▲ The Vault | ▲ The Vault |
| 08–10 morning | ▲ **Cartoon Cartoons** (Dexter, PPG, Johnny Bravo, Ed Edd n Eddy, Courage) | ▲ Cartoon Cartoons | **Saturday Morning** *(keep)* | ▲ **Scooby Block** |
| 10–12 midday | ▲ **CN Modern** (Adventure Time, Steven Universe, Samurai Jack, Amphibia) | ▲ CN Modern | ▲ **Cartoon Cartoons** | ▲ The Vault |
| 12–14 noon | **The Vault** *(keep, retitle)* | The Vault | ▲ **Syndication Hour** (ThunderCats, He-Man, Transformers, TMNT) | ▲ **Cartoon Theatre** (one film) |
| 14–17 afternoon | ▲ **Action Hour** (Batman TAS, Superman TAS, Justice League, Gargoyles, X-Men, SWAT Kats) | ▲ Action Hour | ▲ Nicktoons Vault *(keep)* | ▲ Disney Afternoon |
| 17–20 evening | **Toonami** *(keep — best block you have)* | ▲ **Cartoon Cartoon Friday** | ▲ **Toonami Saturday** (Naruto, One Piece, Samurai Jack, Justice League) | ▲ Cartoon Cartoons |
| 20–23 prime | ▲ **Adult Swim Originals** (ATHF, Space Ghost, Brak, Sealab, Harvey Birdman, Home Movies, Venture Bros.) | ▲ Cartoon Cartoon Friday → AS | ▲ **Toonami Saturday** cont. | ▲ **FOX Primetime** *(keep)* |
| 23–02 night | ▲ **Midnight Run** (Bebop, Champloo, FLCL, Evangelion, FMA, Death Note, Space Dandy) | ▲ Midnight Run | ▲ Midnight Run | ▲ Adult Swim Originals |

Resulting weekly balance — CN + Adult Swim originals go from ~9% to roughly 40%, Disney drops from 16% to about 5%, the vault stays around 20% but moves to the dayparts where it belongs (early morning and midday), and every Toonami bumper set you own maps to a show that actually airs.

## 9. Change list, in order of payoff

**Do first — highest ratio of feel to effort**

1. Move Adult Swim to 23:00–06:00 and move the vault out of overnight into 06–08 and 12–14. Fixes the largest single inversion, 28 hrs/wk.
2. Split `CARTOON_NETWORK_CLASSICS` into a real **Cartoon Cartoons** block (Dexter, PPG, Johnny Bravo, Ed Edd n Eddy, Courage, Infinity Train) and move Daria / Gravity Falls / Owl House / Animaniacs / Pinky out. Move Ed, Edd n Eddy out of Nicktoons Vault. Give the block the 8–10am and 10–12 weekday strip.
3. Add a **CN Modern** block for Adventure Time, Steven Universe, Samurai Jack, Over the Garden Wall, Primal — 460+ unused episodes.
4. Add **Toonami Saturday** at 17:00–23:00 replacing `ANIME_BLOCK`, built on Naruto, One Piece, Samurai Jack, Justice League, FMA. Retire `ANIME_BLOCK` and its unbounded `anime_action_tv` query.
5. Build an **Adult Swim Originals** block for 20:00 that actually leads with Williams Street: Space Ghost, Brak, ATHF, Sealab, Harvey Birdman, Home Movies, Venture Bros. Push Family Guy / King of the Hill / Futurama to the 02–06 acquisitions slot where they historically sat.
6. Add a **Midnight Run** anime block: Bebop, Champloo, FLCL, Evangelion, FMA Brotherhood, Death Note, Space Dandy.

**Asset work — blocks the daytime half**

7. Source Cartoon Network daytime bumpers (checkerboard 1992–97, Powerhouse 1997–2004, CN City 1999–2004) into `filler/bumpers/cartoon network/general/`, tag them, and add a `cn_bumpers` registry key. Until this exists, daytime cannot stop sounding like Adult Swim.
8. Wire per-show Toonami bumpers. ~940 files are currently unreachable; add per-show keys (`toonami_fma_bumpers`, `toonami_naruto_bumpers`, …) and set `bumpers=` on each Toonami program rather than block-wide.
9. Turn on commercials for the daytime blocks with the 110 tagged 90s spots. Highest-value nostalgia asset you own that is currently switched off.
10. Fix `Smurfs, The (1981)` — reorganize into `Season NN/` folders and add `tvshow.nfo`, or 405 episodes stay invisible. Delete or fill the empty `Bullwinkle Show, The (1959)/`.

**Programming polish**

11. Date-anchor the marathons — Thanksgiving weekend, New Year's Eve, Memorial Day, first Saturday of each month — keeping a small random chance on top. Drop or relocate the Simpsons marathon.
12. Add a **summer** seasonal variant (Jun–Aug): extend Cartoon Cartoons across 08:00–14:00 on weekdays and skip the Disney/superhero slots. This is the highest-impact single seasonal change for the 90s/00s goal.
13. Add **Cartoon Cartoon Fridays** as a Friday 17:00–20:00 override.
14. Retarget `ANIMATION_SHOWCASE` — cut Sunday from three movie blocks to one **Cartoon Theatre** slot, and build the pool from Mask of the Phantasm, Iron Giant, Transformers: The Movie, Akira, Ghost in the Shell, Titan A.E., Roger Rabbit, Steven Universe: The Movie, DBZ films.
15. Set `use_epg_group=True` on Toonami, Adult Swim, Saturday Morning and Cartoon Cartoons so the guide reads as blocks.
16. Delete `FOX_KIDS_BLOCK`, `ACTION_ANIMATION`, `BRANDING_90S_KIDS`; fold `SYNDICATED_CARTOONS` into the new Saturday Syndication Hour.
