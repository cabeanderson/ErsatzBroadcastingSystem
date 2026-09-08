"""
Logging utility for the framework.
"""
import logging
import logging.handlers
import sys
from scripts.settings import VERBOSE_LOGGING, LOG_DIR, LOG_LEVEL, LOG_BACKUP_RUNS

class _StdoutHandler(logging.StreamHandler):
    """A StreamHandler that resolves `sys.stdout` at emit time, not at build time.

    `logging.StreamHandler` stores the stream object it is handed. Because a
    logger is created once per channel name and then reused, that bound the
    console handler to whatever `sys.stdout` happened to be during the *first*
    construction -- so a validation loop shaped like

        for d in dates:
            with redirect_stdout(buf):
                sim.simulate_day(d)

    captured day one only: day one built the logger while the redirect was
    active, and every later day wrote into that first, long-discarded buffer
    while the caller read an empty one. A 365-day error scan was a one-day
    scan, and it reported clean because it saw nothing.

    Looking the stream up per emit costs nothing and makes `redirect_stdout`
    behave the way every caller already assumed it did.
    """

    @property
    def stream(self):
        return sys.stdout

    @stream.setter
    def stream(self, _value):
        # StreamHandler.__init__ and setStream() both assign here. Swallow it:
        # the whole point is that the stream is never captured.
        pass


class ChannelLogger:
    """Standardized logger for channel events."""
    def __init__(self, prefix: str = "[TV]", verbose: bool = VERBOSE_LOGGING):
        self.prefix: str = prefix
        self.verbose: bool = verbose
        
        # Silence noisy libraries to prevent API request spam in logs
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("etv_client").setLevel(logging.WARNING)
        
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
            c_handler = _StdoutHandler()
            c_format = logging.Formatter(f'{prefix} %(message)s')
            c_handler.setFormatter(c_format)
            self._log.addHandler(c_handler)
            
            # File Handler - Detailed with timestamps.
            #
            # One file per run, not one file forever. `logging.FileHandler`
            # opens in append mode and never rotates, so every simulation and
            # every build stacked into the same file: pond.log held eleven runs
            # and 88MB, and the repetition read like an infinite loop when it
            # was really eleven ordinary builds end to end.
            #
            # maxBytes stays 0 so nothing rotates *during* a run -- a single
            # build always lands in one file. The rollover is issued once, here,
            # so `pond.log` is always the current run and `pond.log.1` the one
            # before it.
            try:
                LOG_DIR.mkdir(parents=True, exist_ok=True)
                log_file = LOG_DIR / f"{clean_name}.log"
                f_handler = logging.handlers.RotatingFileHandler(
                    log_file, maxBytes=0, backupCount=LOG_BACKUP_RUNS
                )
                if LOG_BACKUP_RUNS > 0 and log_file.exists() and log_file.stat().st_size > 0:
                    f_handler.doRollover()
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