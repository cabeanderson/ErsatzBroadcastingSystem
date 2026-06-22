# scripts/testing/__init__.py
"""Testing utilities."""

from .simulator import ChannelSimulator, test_channel, install_mocks

# Auto-install the offline etv_client mock as soon as the testing package is
# imported. This removes the ordering footgun: simply importing anything from
# scripts.testing (e.g. the simulator) makes channel modules importable on a dev
# machine. It is a no-op when the real client is installed (the container).
install_mocks()

__all__ = ['ChannelSimulator', 'test_channel', 'install_mocks']
