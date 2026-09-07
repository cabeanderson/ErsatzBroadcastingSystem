# ErsatzTV Scheduling Framework

A declarative, feature-rich scheduling system for [ErsatzTV](https://ersatztv.org/) that enables professional-grade broadcast programming with minimal code.

## Overview

This framework separates **scheduling logic** from **channel configuration**. Instead of manually dragging items into a GUI, you define your channel's personality in Python code (e.g., "Play 80s movies on Friday nights", "Switch to Christmas theme in December"). The framework handles the complex date math, probability, and API calls.

## Features

*   **Declarative Configuration:** Define complex channels in 60-100 lines of Python.
*   **Temporal Intelligence:** The framework understands Seasons, Holidays, Weekends, and "Vibes".
*   **Dynamic Scheduling:**
    *   **Seasonal Blending:** Slowly transition content from Summer to Fall.
    *   **Holiday Takeovers:** Automatically switch to Halloween or Christmas programming.
    *   **Marathons:** Trigger special events based on probability, date, or day of the week (e.g., a 5% chance of a DBZ marathon on Saturdays, or a guaranteed Star Wars marathon on May 4th).
    *   **Appointment TV:** Schedule specific seasons of shows to premiere on exact dates (e.g., "Lost Season 1 starts Fall 2026").
*   **Smart Content Resolution:** Handles collections, fillers, intros/outros, and bumpers.
*   **Safety First:** Includes circuit breakers, fallbacks, and pre-flight checks to ensure continuous playback.

## Documentation

*   [Architecture Guide](ARCHITECTURE.md) - Deep dive into the "Architect", "Brain", and "Vault".
*   [Core Concepts](CONCEPTS.md) - Understanding Labels, Signals, and Resolution.
*   [Import Reference](IMPORTS.md) - Cheat sheet for imports and classes.
*   [ErsatzTV API Contract](ERSATZTV_API.md) - The scripted-schedule endpoints, their real semantics, and where the simulator's mock does and does not match them.
*   [Known Issues & Tech Debt](KNOWN_ISSUES.md) - Tracked findings and fixes-for-later.
*   [Channel Rules](reference/channel-rules.md) - How channels get founded, gridded, curated against each other, and verified. The law, with the channel that proved each rule.
*   [Reference](reference/README.md) - The programming method: founding a channel, building the grid, curating across channels, and composing a break. The reasoning the channel code was written against.

## Project Structure

**This repository *is* the `scripts` package.** Clone it so that the checkout
directory is named `scripts`, sitting inside the directory ErsatzTV reads
scripted schedules from. ErsatzTV imports channels out of it directly; every
module resolves as `scripts.<something>`, which is why the directory name
matters.

```text
<ErsatzTV scripting directory>/
└── scripts/                # <- this repository
    ├── channels/           # Channel configurations (the grids)
    ├── library/            # Content queries and collections
    ├── scheduling/         # Config and Runner
    ├── core/               # Date math and state
    ├── logic/              # Scheduling decisions
    ├── engines/            # Playback behaviours (Marathons, Blocks, Programs)
    ├── testing/            # Simulator and validators
    ├── filler/             # Interstitial acquisition, splitting, classification
    ├── nfo/                # Movie-library NFO tooling
    ├── reference/          # Programming method and channel design notes
    ├── config.py           # Paths and server address — see Configuration
    ├── settings.py         # Framework behaviour flags
    └── env.example         # Copy to .env for the offline tools
```

## Getting Started

### Prerequisites

*   An [ErsatzTV](https://ersatztv.org/) instance running and accessible.
*   Python 3.10+.
*   Media content indexed in ErsatzTV.

### Installation

Clone the repository into ErsatzTV's scripting directory, named `scripts`:

```bash
cd <ErsatzTV scripting directory>
git clone https://github.com/cabeanderson/ErsatzBroadcastingSystem.git scripts
```

There is nothing to install. The scheduler runs on the standard library, and
`etv_client` — the API binding — already ships inside ErsatzTV, so it is
importable from the scripting runtime with no action on your part.

If you also want the offline tooling in `filler/` and `nfo/`, those have real
dependencies; see [requirements.txt](requirements.txt).

## Configuration

Two files, with different jobs:

* **[config.py](config.py) — where things are.** Every filesystem path and the
  ErsatzTV address, in one place. The defaults are correct inside the container
  (`/media`, `http://127.0.0.1:8409`), so in the normal case you configure
  nothing.

  The offline tools are the exception: they run on a workstation, where the
  library is mounted somewhere else. Point one variable at it and every tool
  follows:

  ```bash
  cp env.example .env && $EDITOR .env
  set -a && . ./.env && set +a
  ```

  `.env` is gitignored. `config.py` holds no machine-specific values and is
  meant to stay that way — override through the environment, not by editing it.

* **[settings.py](settings.py) — how it behaves.** Fill strategies, smart
  bumpers, commercial and filler toggles, log verbosity. Framework behaviour,
  not deployment.

## Simulation & Testing

### Local channel planning

You can test your channel logic on any dev machine **without ErsatzTV and without
the real `etv_client`**. The simulator ships an in-memory mock of `etv_client`
that is installed automatically the moment you import anything from
`scripts.testing` — so you can just import a channel and run it:

```python
from datetime import date
from scripts.testing.simulator import ChannelSimulator   # auto-installs the mock
from scripts.channels import detective

sim = ChannelSimulator(detective)
schedule = sim.simulate_day(date(2026, 10, 31))   # "time travel" to Halloween
```

> The mock never shadows a real `etv_client`: inside the ErsatzTV container the
> real client is used, and the mock install is a no-op. If you ever import a
> channel *before* touching `scripts.testing`, call `install_mocks()` from
> `scripts.testing` first.

The bundled test scripts already do this and are a good smoke check:

```bash
python3 -m scripts.testing.test_refactor     # imports + resolution
python3 -m unittest scripts.testing.test_scenarios
```

### Deployment

This framework is designed to run alongside ErsatzTV (e.g., inside the container or as a sidecar). It communicates directly with the ErsatzTV API to populate schedules.
