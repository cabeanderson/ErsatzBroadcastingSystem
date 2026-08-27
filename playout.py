# scripts/playout.py
"""
The Engineer - Technical execution layer.
Handles ErsatzTV API interaction, circuit breakers, and utilities.
"""

from etv_client.models import (
    PlayoutCount,
    PlayoutDuration,
    ControlWaitUntilExact,
    PlayoutPadUntilExact,
    ControlStartEpgGroup
)
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Any, Optional, Callable, Tuple, List, Union

from scripts.logic.models import Fallback, CommercialBreak
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. BASIC PLAYBACK
# ==============================================================================

def play_item(api: Any, build_id: str, content_key: str, logger: ChannelLogger, count: int = 1, suppress_errors: bool = False) -> Any:
    """
    Adds item(s) and returns the updated context.
    
    Args:
        api: ErsatzTV API instance
        build_id: Build UUID
        content_key: Content key to play
        logger: ChannelLogger instance
        count: Number of items to play (default 1)
        suppress_errors: If True, logs failures as DEBUG instead of WARN
    
    Returns:
        Updated PlayoutContext
    """
    if count > 1:
        logger.info(f"    ↳ Playing {count} items sequentially (Multi-part detected)")
    if not isinstance(content_key, str):
        logger.warn(f"play_item received non-string content: {type(content_key)} - {content_key}")
        content_key = str(content_key)
        
    try:
        # add_count returns the updated PlayoutContext, so there is no need to
        # follow it with get_context. This is the hottest path in the framework
        # -- one extra round trip here doubled the API calls for a whole build,
        # against ErsatzTV's 30s scripted-schedule timeout.
        context = api.add_count(build_id, PlayoutCount(content=content_key, count=count))
        logger.debug(f"API add_count successful for {content_key}") # Add debug log for successful add_count
        if context is not None:
            return context
    except Exception as e:
        if suppress_errors:
            logger.debug(f"API add_count failed for {content_key} (suppressed): {e}")
        else:
            logger.warn(f"API add_count failed for {content_key}: {e}")

    # Only on failure, or if the client returned nothing, ask for the context.
    return api.get_context(build_id)


def play_for_duration(api: Any, build_id: str, content_key: Any, logger: ChannelLogger,
                      until: datetime, context: Any = None, filler_key: Optional[str] = None) -> Any:
    """
    Adds items from content_key until `until`, then returns the updated context.

    Unlike play_item(count=N), this is bounded by the clock: ErsatzTV fits whole
    items into the span and stops. Use it for open-ended content (a marathon of
    a whole show) where a count would be a guess -- and where guessing high
    overruns the slot by days, because add_count applies no time bound at all.
    """
    if context is None:
        context = api.get_context(build_id)

    remaining = until - context.current_time
    if remaining.total_seconds() <= 0:
        logger.debug(f"play_for_duration: no time left before {until:%H:%M}, nothing to add")
        return context

    if isinstance(content_key, Fallback):
        content_key = content_key.primary
    if not isinstance(content_key, str):
        logger.warn(f"play_for_duration received non-string content: {type(content_key)}")
        content_key = str(content_key)

    total_minutes = int(remaining.total_seconds() // 60)
    duration = f"{total_minutes // 60:02d}:{total_minutes % 60:02d}:00"
    logger.info(f"    ↳ Filling {duration} until {until:%H:%M} from '{content_key}'")

    try:
        return api.add_duration(build_id, PlayoutDuration(
            content=content_key,
            duration=duration,
            fallback=filler_key,
            stop_before_end=True
        ))
    except Exception as e:
        logger.warn(f"API add_duration failed for {content_key}: {e}")
        return api.get_context(build_id)


def play_with_fallback(api: Any, build_id: str, content: Any, logger: ChannelLogger, context: Any = None, count: int = 1) -> Any:
    """
    Plays content, handling Fallback objects gracefully.
    
    Args:
        api: ErsatzTV API instance
        build_id: Build UUID
        content: Content key or Fallback object
        logger: ChannelLogger instance
        context: Optional current context to avoid an extra API call for time checking.
        count: Number of items to play
    
    Returns:
        Updated context
    """
    if isinstance(content, CommercialBreak):
        # If a CommercialBreak object leaks through, treat it as its content key
        content = content.content

    if isinstance(content, Fallback):
        # Get baseline time
        if context is None:
            context = api.get_context(build_id)
        last_time = context.current_time
        
        # Try primary (Holiday variant) - Speculative attempt
        logger.debug(f"Trying primary: {content.primary}")
        context = play_item(api, build_id, content.primary, logger, count=count, suppress_errors=True)
        
        # If primary didn't advance time, try secondary
        if context.current_time <= last_time:
            logger.info(f"    ↳ Fallback to secondary: {content.secondary}")
            context = play_item(api, build_id, content.secondary, logger, count=count)
        
        return context
    
    # Not a Fallback - just play normally
    return play_item(api, build_id, content, logger, count=count)


# ==============================================================================
# 2. TIME MANAGEMENT
# ==============================================================================

# Both helpers below take an absolute datetime and use ErsatzTV's *_exact
# endpoints rather than the time-of-day ones. The HH:MM variants take no date:
# the day is carried by a separate `tomorrow` flag, and when the clock is
# already past the given time of day with tomorrow=False, ErsatzTV schedules
# NOTHING and reports no error (see PadUntil/WaitUntil in SchedulingEngine).
# Callers were computing that flag as `target.day > now.day`, which is False
# across a month boundary (Aug 31 -> Sep 1 is `1 > 31`) -- producing exactly
# that silent no-op. ErsatzTV also flags its own time-of-day reconstruction as
# "wrong when offset changes" (DST). Passing a full datetime avoids all of it.

def wait_until_time(api: Any, build_id: str, context: Any, logger: ChannelLogger, target_dt: datetime, rewind_on_reset: bool = False) -> Any:
    """
    Waits (dead air) until target_dt.
    Creates a hard jump in the timeline.

    Args:
        api: ErsatzTV API instance
        build_id: Build UUID
        context: Current playout context (unused but kept for signature consistency)
        logger: ChannelLogger instance (unused but kept for signature consistency)
        target_dt: Absolute datetime to jump to
        rewind_on_reset: Allow the build clock to move backward during a reset

    Returns:
        Updated context
    """
    return api.wait_until_exact(build_id, ControlWaitUntilExact(
        when=target_dt,
        rewind_on_reset=rewind_on_reset
    ))


def fill_until_time(api: Any, build_id: str, context: Any, logger: ChannelLogger, target_dt: datetime, filler_key: Optional[str] = None) -> Any:
    """
    Pads until target_dt with filler content.
    Falls back to wait_until_time if no filler or if padding fails.

    Args:
        api: ErsatzTV API instance
        build_id: Build UUID
        context: Current playout context
        logger: ChannelLogger instance
        target_dt: Absolute datetime to pad until
        filler_key: Content key for filler (optional)

    Returns:
        Updated context
    """
    if filler_key:
        try:
            return api.pad_until_exact(build_id, PlayoutPadUntilExact(
                when=target_dt,
                content=filler_key,
                stop_before_end=True
            ))
        except Exception as e:
            logger.warn(f"Pad until failed: {e}. Using wait instead.")
            # Fall through to wait_until_time

    # No filler or filler failed - just wait (dead air)
    return wait_until_time(api, build_id, context, logger, target_dt)


def fill_until_next_hour(api: Any, build_id: str, context: Any, logger: ChannelLogger, filler_key: str) -> Any:
    """
    Convenience wrapper - pads to next hour boundary.

    Args:
        api: ErsatzTV API instance
        build_id: Build UUID
        context: Current playout context
        logger: ChannelLogger instance
        filler_key: Content key for filler content
    """
    next_hour_dt = (context.current_time + timedelta(hours=1)).replace(
        minute=0, second=0, microsecond=0
    )
    return fill_until_time(api, build_id, context, logger, next_hour_dt, filler_key)


# ==============================================================================
# 3. SAFETY & EPG
# ==============================================================================

def circuit_breaker(
    api: Any, 
    build_id: str, 
    context: Any, 
    last_time: datetime, 
    logger: ChannelLogger,
    fallback_content: Optional[str] = None,
    skip_minutes: int = 30
) -> Any:
    """
    Prevents infinite loops by attempting fallback or forcing time forward.
    """
    if context.current_time <= last_time:
        assert skip_minutes > 0, "circuit_breaker skip_minutes must be > 0"

        logger.warn(
            f"⚠️ Circuit breaker: Time stalled at {context.current_time.strftime('%H:%M')}"
        )
        logger.debug(f"Circuit breaker skip configured: {skip_minutes} minutes")
        
        # Try fallback first
        if fallback_content:
            try:
                logger.info(f"   Attempting fallback due to stalled time: {fallback_content}")
                context = play_item(api, build_id, fallback_content, logger)
                
                if context.current_time > last_time:
                    logger.info("   ✅ Fallback succeeded")
                    return context
                
                logger.warn("   ❌ Fallback also stalled")
            except Exception as e:
                logger.warn(f"   ❌ Fallback error: {e}")
        
        # Force time skip as last resort
        new_time = context.current_time + timedelta(minutes=skip_minutes)

        logger.warn(
            f"🔧 Forcing time skip: {context.current_time.strftime('%H:%M')} → "
            f"{new_time.strftime('%H:%M')}"
        )

        try:
            return wait_until_time(api, build_id, context, logger, new_time)
        except Exception as e:
            logger.error(f"🛑 Circuit breaker failed: {e}")
            return context
    
    return context


def toggle_epg_group(api: Any, build_id: str, name: Optional[str] = None, description: Optional[str] = None, start: bool = True) -> None:
    """
    Manages EPG grouping for blocks or marathons.
    Fails gracefully if EPG commands fail.
    
    Args:
        api: ErsatzTV API instance
        build_id: Build UUID
        name: Group name for EPG (e.g. "Saturday Morning Cartoons")
        description: Optional description
        start: If True, enables branding. If False, disables.
    """
    try:
        if start:
            if name:
                api.start_epg_group(
                    build_id, 
                    ControlStartEpgGroup(
                        custom_title=name,
                        description=description,
                        advance=True
                    )
                )
        else:
            api.stop_epg_group(build_id)
    except Exception as e:
        # EPG grouping is cosmetic - log but don't fail
        action = "start" if start else "stop"
        print(f"[WARN] Failed to {action} EPG group: {e}", flush=True)

@contextmanager
def epg_group(api: Any, build_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Any:
    """Context manager for EPG grouping. Automatically handles start/stop."""
    if name:
        toggle_epg_group(api, build_id, name=name, description=description, start=True)
    try:
        yield
    finally:
        if name:
            toggle_epg_group(api, build_id, start=False)
