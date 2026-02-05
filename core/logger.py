"""
Logging utility for the framework.
"""
from scripts.config import VERBOSE_LOGGING

class ChannelLogger:
    """Standardized logger for channel events."""
    def __init__(self, prefix: str = "[TV]", verbose: bool = VERBOSE_LOGGING):
        self.prefix: str = prefix
        self.verbose: bool = verbose

    def info(self, msg: str) -> None:
        print(f"{self.prefix} {msg}", flush=True)

    def debug(self, msg: str) -> None:
        if self.verbose:
            print(f"{self.prefix} [DEBUG] {msg}", flush=True)
            
    def warn(self, msg: str) -> None:
        print(f"{self.prefix} [WARN] {msg}", flush=True)

    def error(self, msg: str) -> None:
        print(f"{self.prefix} [ERROR] {msg}", flush=True)