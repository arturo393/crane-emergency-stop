"""
Event Logger - Sistema de Logging de Eventos
Logging centralizado para el sistema K13 Puente Grúa con soporte para
trazabilidad, auditoría y cumplimiento normativo industrial.
"""

import logging
import json
import time
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading
from collections import deque


class EventLevel(Enum):
    """Niveles de eventos del sistema"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    SAFETY = 60  # Nivel especial para eventos de seguridad


class EventCategory(Enum):
    """Categorías de eventos del sistema"""
    SAFETY = "SAFETY"  # Paradas de emergencia, fault reactions
    CONTROL = "CONTROL"  # Cambios de estado, comandos
    COMMUNICATION = "COMMUNICATION"  # CAN, SDO, PDO, NMT
    SYSTEM = "SYSTEM"  # Inicio/parada, errores, warnings
    USER = "USER"  # Acciones del operador
    HARDWARE = "HARDWARE"  # Conexión/desconexión dispositivos
    DIAGNOSTIC = "DIAGNOSTIC"  # Información de diagnóstico


class Event:
    """Representa un evento del sistema"""
    
    def __init__(
        self,
        level: EventLevel,
        category: EventCategory,
        message: str,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        node_id: Optional[int] = None
    ):
        self.timestamp = datetime.now()
        self.level = level
        self.category = category
        self.message = message
        self.source = source
        self.context = context or {}
        self.node_id = node_id
        self.stack_trace = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir evento a diccionario"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "timestamp_unix": self.timestamp.timestamp(),
            "level": self.level.name,
            "level_value": self.level.value,
            "category": self.category.value,
            "source": self.source,
            "node_id": self.node_id,
            "message": self.message,
            "context": self.context,
            "stack_trace": self.stack_trace
        }
    
    def to_json(self) -> str:
        """Convertir evento a JSON"""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_log_line(self) -> str:
        """Convertir evento a línea de log legible"""
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        node_str = f"[Node {self.node_id}]" if self.node_id else ""
        context_str = f" | Context: {json.dumps(self.context)}" if self.context else ""
        return f"{ts} | {self.level.name:8} | {self.category.value:13} | {self.source:15} {node_str} | {self.message}{context_str}"


class EventLogger:
    """
    Logger centralizado de eventos del sistema
    
    Características:
    - Múltiples niveles y categorías
    - Buffer en memoria para eventos recientes
    - Logging a archivo con rotación
    - Thread-safe
    - Callbacks para notificaciones en tiempo real
    """
    
    def __init__(
        self,
        name: str = "k13_system",
        log_dir: Optional[Path] = None,
        buffer_size: int = 1000,
        min_level: EventLevel = EventLevel.DEBUG
    ):
        self.name = name
        self.log_dir = log_dir or Path("logs")
        self.buffer_size = buffer_size
        self.min_level = min_level
        
        # Buffer circular de eventos recientes (thread-safe)
        self._event_buffer: deque = deque(maxlen=buffer_size)
        self._buffer_lock = threading.Lock()
        
        # Callbacks para notificaciones en tiempo real
        self._callbacks: List[callable] = []
        self._callbacks_lock = threading.Lock()
        
        # Contadores de eventos por nivel y categoría
        self._counters = {
            "by_level": {level: 0 for level in EventLevel},
            "by_category": {cat: 0 for cat in EventCategory},
            "total": 0
        }
        self._counters_lock = threading.Lock()
        
        # Configurar logging a archivo
        self._setup_file_logging()
    
    def _setup_file_logging(self):
        """Configurar logging a archivo con rotación"""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear logger de Python estándar
        self.file_logger = logging.getLogger(f"{self.name}_file")
        self.file_logger.setLevel(logging.DEBUG)
        
        # Handler para archivo de texto
        log_file = self.log_dir / f"{self.name}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formato simple para el archivo
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        
        self.file_logger.addHandler(file_handler)
        
        # Handler para archivo JSON
        json_file = self.log_dir / f"{self.name}.json"
        self.json_file = json_file
    
    def log(
        self,
        level: EventLevel,
        category: EventCategory,
        message: str,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        node_id: Optional[int] = None
    ) -> Event:
        """
        Registrar un evento
        
        Args:
            level: Nivel del evento
            category: Categoría del evento
            message: Mensaje descriptivo
            source: Origen del evento (ej: "bl335_gateway", "web_ui")
            context: Contexto adicional (diccionario)
            node_id: ID del nodo CANopen (opcional)
        
        Returns:
            Event: Objeto evento creado
        """
        # Filtrar por nivel mínimo
        if level.value < self.min_level.value:
            return None
        
        # Crear evento
        event = Event(
            level=level,
            category=category,
            message=message,
            source=source,
            context=context,
            node_id=node_id
        )
        
        # Agregar a buffer
        with self._buffer_lock:
            self._event_buffer.append(event)
        
        # Actualizar contadores
        with self._counters_lock:
            self._counters["by_level"][level] += 1
            self._counters["by_category"][category] += 1
            self._counters["total"] += 1
        
        # Escribir a archivo de texto
        self.file_logger.info(event.to_log_line())
        
        # Escribir a archivo JSON (append)
        try:
            with open(self.json_file, 'a', encoding='utf-8') as f:
                f.write(event.to_json() + '\n')
        except Exception as e:
            print(f"Error escribiendo JSON: {e}")
        
        # Notificar callbacks
        self._notify_callbacks(event)
        
        return event
    
    def debug(self, category: EventCategory, message: str, source: str, **kwargs):
        """Log nivel DEBUG"""
        return self.log(EventLevel.DEBUG, category, message, source, **kwargs)
    
    def info(self, category: EventCategory, message: str, source: str, **kwargs):
        """Log nivel INFO"""
        return self.log(EventLevel.INFO, category, message, source, **kwargs)
    
    def warning(self, category: EventCategory, message: str, source: str, **kwargs):
        """Log nivel WARNING"""
        return self.log(EventLevel.WARNING, category, message, source, **kwargs)
    
    def error(self, category: EventCategory, message: str, source: str, **kwargs):
        """Log nivel ERROR"""
        return self.log(EventLevel.ERROR, category, message, source, **kwargs)
    
    def critical(self, category: EventCategory, message: str, source: str, **kwargs):
        """Log nivel CRITICAL"""
        return self.log(EventLevel.CRITICAL, category, message, source, **kwargs)
    
    def safety(self, category: EventCategory, message: str, source: str, **kwargs):
        """Log nivel SAFETY (máxima prioridad)"""
        return self.log(EventLevel.SAFETY, category, message, source, **kwargs)
    
    def get_recent_events(self, limit: Optional[int] = None) -> List[Event]:
        """
        Obtener eventos recientes del buffer
        
        Args:
            limit: Número máximo de eventos a retornar (None = todos)
        
        Returns:
            Lista de eventos (más recientes primero)
        """
        with self._buffer_lock:
            events = list(self._event_buffer)
        
        # Invertir para tener más recientes primero
        events.reverse()
        
        if limit:
            events = events[:limit]
        
        return events
    
    def get_events_by_category(self, category: EventCategory, limit: Optional[int] = None) -> List[Event]:
        """Obtener eventos filtrados por categoría"""
        events = self.get_recent_events()
        filtered = [e for e in events if e.category == category]
        
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def get_events_by_level(self, min_level: EventLevel, limit: Optional[int] = None) -> List[Event]:
        """Obtener eventos filtrados por nivel mínimo"""
        events = self.get_recent_events()
        filtered = [e for e in events if e.level.value >= min_level.value]
        
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de eventos"""
        with self._counters_lock:
            stats = {
                "total_events": self._counters["total"],
                "events_by_level": {
                    level.name: count 
                    for level, count in self._counters["by_level"].items()
                },
                "events_by_category": {
                    cat.value: count 
                    for cat, count in self._counters["by_category"].items()
                },
                "buffer_size": len(self._event_buffer),
                "buffer_max_size": self.buffer_size
            }
        
        return stats
    
    def register_callback(self, callback: callable):
        """
        Registrar callback para notificaciones en tiempo real
        
        Args:
            callback: Función que recibe Event como parámetro
        """
        with self._callbacks_lock:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: callable):
        """Remover callback"""
        with self._callbacks_lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def _notify_callbacks(self, event: Event):
        """Notificar a todos los callbacks registrados"""
        with self._callbacks_lock:
            callbacks = self._callbacks.copy()
        
        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Error en callback: {e}")
    
    def clear_buffer(self):
        """Limpiar buffer de eventos"""
        with self._buffer_lock:
            self._event_buffer.clear()
    
    def export_to_json(self, output_file: Path, limit: Optional[int] = None) -> int:
        """
        Exportar eventos a archivo JSON
        
        Args:
            output_file: Ruta del archivo de salida
            limit: Número máximo de eventos a exportar
        
        Returns:
            Número de eventos exportados
        """
        events = self.get_recent_events(limit)
        events_data = [e.to_dict() for e in events]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, indent=2)
        
        return len(events_data)


# Instancia global del logger (singleton)
_global_logger: Optional[EventLogger] = None


def get_logger() -> EventLogger:
    """Obtener instancia global del logger (singleton)"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = EventLogger()
    
    return _global_logger


def initialize_logger(
    name: str = "k13_system",
    log_dir: Optional[Path] = None,
    buffer_size: int = 1000,
    min_level: EventLevel = EventLevel.DEBUG
) -> EventLogger:
    """
    Inicializar logger global con configuración personalizada
    
    Args:
        name: Nombre del logger
        log_dir: Directorio de logs
        buffer_size: Tamaño del buffer circular
        min_level: Nivel mínimo de logging
    
    Returns:
        EventLogger configurado
    """
    global _global_logger
    
    _global_logger = EventLogger(
        name=name,
        log_dir=log_dir,
        buffer_size=buffer_size,
        min_level=min_level
    )
    
    return _global_logger
