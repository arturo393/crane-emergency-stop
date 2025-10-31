"""
Core Module - Sistema K13 Puente Grúa
Componentes centrales compartidos entre todos los módulos del sistema
"""

from .event_logger import (
    EventLogger,
    Event,
    EventLevel,
    EventCategory,
    get_logger,
    initialize_logger
)
from .event_storage import EventStorage

__version__ = "1.0.0"

__all__ = [
    "EventLogger",
    "Event",
    "EventLevel",
    "EventCategory",
    "EventStorage",
    "get_logger",
    "initialize_logger"
]
