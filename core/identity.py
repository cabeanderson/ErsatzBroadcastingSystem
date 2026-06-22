# scripts/core/identity.py
"""
Stable, process-independent identity for content structures.

Used to seed deterministic RNGs. Seeding with id() (a memory address) makes
selections vary between process runs, which breaks the framework's core promise
that the same date always produces the same schedule. stable_hash() derives a
seed from the *contents* of a structure instead, so a given logical collection
or list yields identical selections across restarts.
"""

import hashlib
from typing import Any


def stable_hash(obj: Any) -> str:
    """Return a short, deterministic hash of a content structure."""
    try:
        material = _canonical(obj)
    except Exception:
        material = repr(obj)
    return hashlib.sha1(material.encode("utf-8")).hexdigest()[:12]


def _canonical(obj: Any) -> str:
    """Build a deterministic string representation of common content shapes."""
    if isinstance(obj, str):
        return obj
    if obj is None or isinstance(obj, (int, float, bool)):
        return repr(obj)
    if isinstance(obj, dict):
        items = sorted(obj.items(), key=lambda kv: str(kv[0]))
        return "{" + ",".join(f"{k}={_canonical(v)}" for k, v in items) + "}"
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(_canonical(x) for x in obj) + "]"

    # Objects (e.g. ContentItem): prefer identifying attributes over the default
    # repr, which would embed an id() and reintroduce non-determinism.
    for attr in ("query", "title", "name", "key", "content"):
        val = getattr(obj, attr, None)
        if val is not None:
            return f"{type(obj).__name__}:{_canonical(val)}"
    return type(obj).__name__
