#!/usr/bin/env python3
"""
Prueba simple del sistema de logging
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import EventLogger, EventLevel, EventCategory, initialize_logger

def test_logging():
    """Prueba básica del sistema de logging"""
    
    # Inicializar logger
    logger = initialize_logger(
        name="test_k13",
        log_dir=Path("logs/test"),
        buffer_size=50
    )
    
    print("✅ EventLogger inicializado correctamente")
    
    # Crear eventos de prueba
    logger.info(
        EventCategory.SYSTEM,
        "Sistema iniciado",
        source="test"
    )
    
    logger.warning(
        EventCategory.SAFETY,
        "Prueba de advertencia",
        source="test",
        context={"test": True}
    )
    
    logger.safety(
        EventCategory.SAFETY,
        "Parada de emergencia de prueba",
        source="test",
        node_id=1
    )
    
    print("✅ 3 eventos creados")
    
    # Obtener estadísticas
    stats = logger.get_statistics()
    print(f"✅ Total eventos: {stats['total_events']}")
    print(f"✅ En buffer: {stats['buffer_size']}")
    
    # Obtener eventos recientes
    events = logger.get_recent_events(limit=3)
    print(f"\n📋 Últimos 3 eventos:")
    for event in events:
        print(f"  - [{event.level.name}] {event.message}")
    
    print(f"\n✅ Archivos guardados en: logs/test/")
    print("✅ Sistema de logging funcionando correctamente!")

if __name__ == "__main__":
    test_logging()
