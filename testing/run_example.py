#!/usr/bin/env python3
"""
run_example.py -- simulate channels/example_channel.py on a dev machine.

    python3 -m scripts.testing.run_example

This exists only for import ordering. `scripts/channels/__init__.py` imports
every channel eagerly, and several of them import `etv_client` at module level,
so `python3 -m scripts.channels.example_channel` fails on any machine without
the real client -- the package import chain runs before the example's own code
gets a chance to install the mock. Importing `scripts.testing` first installs
it (a no-op where the real client exists, so this is safe inside ErsatzTV too).
"""

import scripts.testing  # noqa: F401 -- installs the etv_client mock on import

from scripts.channels import example_channel
from scripts.testing.simulator import test_channel


def main() -> None:
    print("Running simulator for Example Channel...")
    test_channel(example_channel)


if __name__ == "__main__":
    main()
