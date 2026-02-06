# scripts/core/director.py
import random
import hashlib
from datetime import timedelta
from datetime import datetime, date
from functools import cached_property
from typing import Any, Optional, List, Set, Tuple, Dict, Union
from . import registry, states, signals


class DayDirector:
    """
    Main interface for channels to query day state and make scheduling decisions.
    
    Features:
    - Label checking (has/had/has_any/has_all)
    - Signal strength (holidays, seasons)
    - Deterministic selection (pick/pick_weighted/roll)
    - Time travel (anniversary dates)
    - Seasonal crossfading (season_vibe)
    """
    
    def __init__(self, context: Any, anniversary_years: Optional[int] = None):
        self.context = context
        self._initial_time: datetime = context.current_time
        self._label_cache: Dict[datetime, Set[str]] = {}
        
        if anniversary_years is not None:
            self.anniversary: Optional[datetime] = self._get_anniversary_date(self._initial_time, anniversary_years)
            self.past_labels: Set[str] = states.derive_labels(self.anniversary)
        else:
            self.anniversary = None
            self.past_labels = set()

    @property
    def now(self) -> datetime:
        return self.context.current_time

    # --- INTERNAL HELPERS ---

    def _rng(self, key: str) -> random.Random:
        """Centralized deterministic RNG factory based on the current date."""
        seed = f"{self.date}::{key}"
        return random.Random(seed)

    def _get_anniversary_date(self, dt: datetime, years: int) -> datetime:
        """Teleport date back, handling leap years."""
        try:
            return dt.replace(year=dt.year - years)
        except ValueError:  # Handles Feb 29
            return dt - timedelta(days=(365 * years) + (years // 4))

    # --- CACHED PROPERTIES ---

    @cached_property
    def date(self) -> date:
        return self._initial_time.date()

    @property
    def labels(self) -> Set[str]:
        """Dynamic labels based on current time."""
        dt = self.now
        if dt not in self._label_cache:
            self._label_cache[dt] = states.derive_labels(dt)
        return self._label_cache[dt]

    # --- DETERMINISTIC SELECTION ---
    
    def roll(self, probability: float, key: str = "default") -> bool:
        """Deterministic daily probability check."""
        seed = f"{self.date}::{key}"
        # Use SHA256 to generate a uniform float 0.0-1.0
        hash_bytes = hashlib.sha256(seed.encode('utf-8')).digest()
        # Convert first 4 bytes to int and divide by max 32-bit int
        val = int.from_bytes(hash_bytes[:4], 'big')
        return (val / 0xFFFFFFFF) < probability

    def pick(self, key: str, items: Union[List[Any], str, None]) -> Optional[Any]:
        """Deterministic selection from a list."""
        if not items:
            return None
        if isinstance(items, str):
            return items
        return self._rng(f"pick:{key}").choice(items)
    
    def pick_weighted(self, key: str, items_with_weights: Optional[List[Tuple[Any, float]]]) -> Optional[Any]:
        """Deterministic weighted selection."""
        if not items_with_weights:
            return None
        items, weights = zip(*items_with_weights)
        rng = self._rng(f"pick_weighted:{key}")
        
        if sum(weights) == 0:
            return rng.choice(items)
        return rng.choices(items, weights=weights, k=1)[0]

    # --- LABEL & WINDOW CHECKING ---
    
    def has(self, label: str) -> bool:
        """Check if current time has this label."""
        return label in self.labels
    
    def has_any(self, *labels: str) -> bool:
        """Check if ANY of the labels match."""
        return any(label in self.labels for label in labels)
    
    def has_all(self, *labels: str) -> bool:
        """Check if ALL of the labels match."""
        return all(label in self.labels for label in labels)
    
    def had(self, label: str) -> bool:
        """Check if anniversary time had this label."""
        return label in self.past_labels

    def window(self, event_name: str, before: int = 0, after: int = 0) -> bool:
        """Boolean check if current date is within a holiday window."""
        # Look up event date from HOLIDAYS
        event_date = None
        
        for (m, d), name in registry.HOLIDAYS.items():
            if name == event_name:
                event_date = (m, d)
                break
        
        if not event_date:
            return False
        
        return states.in_window(self.now, event_date[0], event_date[1], before, after)
    
    def days_until(self, event_name: str) -> int:
        """Returns days until the next occurrence of the event."""
        for (m, d), name in registry.HOLIDAYS.items():
            if name == event_name:
                return states.days_until(self.now, m, d)
        
        # Fallback for unknown events (effectively infinite distance)
        return 999

    def days_since(self, event_name: str) -> int:
        """Returns days since the last occurrence of the event."""
        for (m, d), name in registry.HOLIDAYS.items():
            if name == event_name:
                return states.days_since(self.now, m, d)
        
        # Fallback for unknown events
        return 999

    # --- SIGNAL STRENGTH ---
    
    def signal(self, event_name: str, window: int = 10, hangover: bool = False) -> float:
        """
        Calculates 0.0-1.0 signal strength for an event.
        
        Args:
            event_name: Holiday name from registry.HOLIDAYS
            window: Days before/after event for signal calculation
            hangover: If True, uses decay curve (post-event), else surge curve (pre-event)
        
        Returns:
            Float from 0.0 (no signal) to 1.0 (peak signal)
        
        Note: Floating holidays (THANKSGIVING, etc.) don't support signals since they
        don't have fixed dates. Use has() to check for their presence instead.
        """
        # Look up event date from HOLIDAYS
        event_date = None
        
        for (m, d), name in registry.HOLIDAYS.items():
            if name == event_name:
                event_date = (m, d)
                break

        if not event_date:
            # Try to find a floating rule
            for rule in registry.FLOATING_RULES:
                if rule["name"] == event_name:
                    dt = states.get_floating_date(self.now.year, rule)
                    if dt:
                        event_date = (dt.month, dt.day)
                    break
            
            if not event_date:
                return 0.0
        
        # Calculate distance and signal
        if hangover:
            dist = states.days_since(self.now, event_date[0], event_date[1])
            return signals.get_decay_signal(dist, window)
        else:
            dist = states.days_until(self.now, event_date[0], event_date[1])
            return signals.get_parabolic_surge(dist, window)

    def signal_any(self, *event_names: str) -> float:
        """Returns the strongest signal among multiple events."""
        return max((self.signal(name) for name in event_names), default=0.0)

    def signal_all(self, *event_names: str) -> float:
        """Returns the weakest signal among multiple events (intersection)."""
        return min((self.signal(name) for name in event_names), default=0.0)

    # --- SEASONAL STRENGTH ---

    def get_season_strength(self, season_name: str) -> float:
        """
        Calculates the strength (0.0-1.0) of a given season for the current date.
        This is a wrapper around the pure function in signals.py.
        """
        return signals.get_season_strength(self.now, season_name)

    # --- BROADCAST SEASONS ---

    @cached_property
    def season_vibe(self) -> str:
        """
        Returns the current broadcast season (WINTER, SPRING, SUMMER, FALL).
        This is deterministic. For probabilistic blending, use get_season_strength().
        """
        m = self.now.month
        for season, months in registry.SEASONS.items():
            if m in months:
                return season
        return "WINTER"
    
    # --- DEBUG ---
    
    def debug(self) -> Dict[str, Any]:
        """Returns structured diagnostic data."""
        return {
            "now": self.now.strftime('%Y-%m-%d %H:%M'),
            "labels": sorted(list(self.labels)),
            "season_vibe": self.season_vibe,
            "anniversary": self.anniversary.strftime('%Y-%m-%d') if self.anniversary else None
        }

    def debug_print(self) -> None:
        """Prints diagnostic info to logs."""
        data = self.debug()
        print(f"--- DIRECTOR DEBUG ---")
        for k, v in data.items():
            print(f"{k.upper():<15}: {v}")
