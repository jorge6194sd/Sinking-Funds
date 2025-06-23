"""
sinking_funds package.

Expose core objects.
"""

from .simulation import sinking_funds_simulation  # noqa: F401
from .events import Event, EventType, add_event, load_events  # noqa: F401

__all__ = [
    "sinking_funds_simulation",
    "Event",
    "EventType",
    "add_event",
    "load_events",
]
