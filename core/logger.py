"""
Logging utility for the framework.
"""
import logging
import sys
from scripts.settings import VERBOSE_LOGGING, LOG_DIR, LOG_LEVEL

class ChannelLogger:
    """Standardized logger for channel events."""
    def __init__(self, prefix: str = "[TV]", verbose: bool = VERBOSE_LOGGING):
        self.prefix: str = prefix
        self.verbose: bool = verbose
        
        # Extract clean name for file (e.g. "[SCIFI]" -> "scifi")
        clean_name = prefix.replace("[", "").replace("]", "").strip().lower()
        if not clean_name:
            clean_name = "system"

        # Setup Python Logger
        self._log = logging.getLogger(clean_name)
        self._log.propagate = False
        
        # Set Level
        level = logging.DEBUG if verbose else getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        self._log.setLevel(level)
        
        # Avoid adding duplicate handlers if re-initialized
        if not self._log.handlers:
            # Console Handler (stdout) - Matches original format
            c_handler = logging.StreamHandler(sys.stdout)
            c_format = logging.Formatter(f'{prefix} %(message)s')
            c_handler.setFormatter(c_format)
            self._log.addHandler(c_handler)
            
            # File Handler - Detailed with timestamps
            try:
                log_file = LOG_DIR / f"{clean_name}.log"
                f_handler = logging.FileHandler(log_file)
                f_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
                f_handler.setFormatter(f_format)
                self._log.addHandler(f_handler)
            except Exception as e:
                print(f"{prefix} [WARN] Failed to setup file logging: {e}")

    def info(self, msg: str) -> None:
        self._log.info(msg)

    def debug(self, msg: str) -> None:
        self._log.debug(msg)
            
    def warn(self, msg: str) -> None:
        self._log.warning(msg)

    def error(self, msg: str) -> None:
        self._log.error(msg)