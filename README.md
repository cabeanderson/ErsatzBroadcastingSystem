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
    *   **Marathons:** Probability-based triggers (e.g., 5% chance of a DBZ marathon on Saturdays).
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
│   ├── core/           # Date math and state
│   ├── logic/          # Scheduling decisions
│   ├── engines/        # Playback behaviors (Marathons, Blocks)
│   ├── testing/        # Simulator
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

3.  Configure your environment:
    *   Ensure `etv_client` is available (generated from ErsatzTV OpenAPI).
    *   Set up `scripts/config_local.py` if you need to override paths (optional).

## Simulation & Testing

You can test your channel logic without affecting your live ErsatzTV server using the included simulator. This allows you to "time travel" to test holidays and special events.

```bash
# Run the simulator for a specific channel
python3 -m scripts.testing.simulator
```

### Deployment

This framework is designed to run alongside ErsatzTV (e.g., inside the container or as a sidecar). It communicates directly with the ErsatzTV API to populate schedules.
