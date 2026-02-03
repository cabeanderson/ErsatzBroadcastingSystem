# scripts/core/__init__.py
"""
Core primitives - the "Physics Engine" of the scheduling system.
Contains pure logic for time, state, signals, and resolution.
"""

from .director import DayDirector
__all__ = ['DayDirector']