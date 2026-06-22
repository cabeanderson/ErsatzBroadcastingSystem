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

*   [Architecture Guide](scripts/ARCHITECTURE.md) - Deep dive into the "Architect", "Brain", and "Vault".
*   [Core Concepts](scripts/CONCEPTS.md) - Understanding Labels, Signals, and Resolution.
*   [Import Reference](scripts/IMPORTS.md) - Cheat sheet for imports and classes.

## Project Structure

```text
scripted-schedules/
├── scripts/            # Main Package
│   ├── channels/       # Your channel configurations (User Data)
│   ├── library/        # Content queries and collections (User Data)
│   ├── scheduling/     # The Scheduling Subsystem (Config, Runner)
│   ├── core/           # Date math and state
│   ├── logic/          # Scheduling decisions
│   ├── engines/        # Playback behaviors (Marathons, Blocks, Programs)
│   ├── testing/        # Simulator
│   ├── settings.py     # Global settings
│   └── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

*   An [ErsatzTV](https://ersatztv.org/) instance running and accessible.
*   Python 3.10+.
*   Media content indexed in ErsatzTV.

### Installation

1.  Clone this repository:
    ```bash
    git clone https://github.com/yourusername/ersatztv-scheduling-framework.git
    cd ersatztv-scheduling-framework
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    > **Note:** The framework uses only the Python standard library, so this is
    > effectively a no-op. There are no third-party packages to install.

3.  Make `etv_client` available:
    *   `etv_client` is the API binding that **ships inside ErsatzTV**; it is not
        on PyPI and is not part of this repo.
    *   **Running inside the ErsatzTV container** (the normal case): it is already
        importable from ErsatzTV's scripting runtime — there is nothing to do.
        See ErsatzTV's scripting documentation:
        <https://github.com/ErsatzTV/ErsatzTV>.
    *   **Running locally** (simulator/tests for channel planning): you do **not**
        need the real client — see [Local channel planning](#local-channel-planning) below.

## Simulation & Testing

### Local channel planning

You can test your channel logic on any dev machine **without ErsatzTV and without
the real `etv_client`**. The simulator ships an in-memory mock of `etv_client`;
install it *before* importing any channel module (channels import `etv_client`
at the top level), then drive a channel through the `ChannelSimulator`:

```python
from datetime import date
from scripts.testing import install_mocks
install_mocks()                      # must run before importing channels

from scripts.channels import detective
from scripts.testing.simulator import ChannelSimulator

sim = ChannelSimulator(detective)
schedule = sim.simulate_day(date(2026, 10, 31))   # "time travel" to Halloween
```

The bundled test scripts already do this and are a good smoke check:

```bash
python3 -m scripts.testing.test_refactor     # imports + resolution
python3 -m unittest scripts.testing.test_scenarios
```

### Deployment

This framework is designed to run alongside ErsatzTV (e.g., inside the container or as a sidecar). It communicates directly with the ErsatzTV API to populate schedules.
