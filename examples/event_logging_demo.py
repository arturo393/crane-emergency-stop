#!/usr/bin/env python3
"""
Ejemplo de uso del sistema de logging de eventos
Demuestra todas las características principales del EventLogger
"""

import time
from pathlib import Path
from datetime import datetime

# Importar componentes del core
from src.core import (
    EventLogger,
    EventStorage,
    EventLevel,
    EventCategory,
    initialize_logger,
    get_logger
)


def ejemplo_basico():
    """Ejemplo básico de uso del EventLogger"""
    print("=" * 60)
    print("EJEMPLO 1: Uso Básico del EventLogger")
    print("=" * 60)
    
    # Inicializar logger
    logger = initialize_logger(
        name="ejemplo_k13",
        log_dir=Path("logs/examples"),
        buffer_size=100,
        min_level=EventLevel.DEBUG
    )
    
    # Registrar eventos de diferentes niveles
    logger.debug(
        EventCategory.SYSTEM,
        "Sistema iniciando",
        source="main"
    )
    
    logger.info(
        EventCategory.CONTROL,
        "Inicializando controlador K13",
        source="k13_controller",
        context={"node_id": 1, "firmware_version": "1.0.3"}
    )
    
    logger.warning(
        EventCategory.COMMUNICATION,
        "Latencia alta detectada",
        source="can_bus",
        context={"latency_ms": 150, "threshold_ms": 100}
    )
    
    logger.error(
        EventCategory.HARDWARE,
        "Error de comunicación serial",
        source="serial_comm",
        context={"port": "/dev/ttyUSB0", "error": "Device not found"}
    )
    
    logger.critical(
        EventCategory.SAFETY,
        "Botón de emergencia presionado",
        source="emergency_monitor",
        node_id=1,
        context={"timestamp_pressed": datetime.now().isoformat()}
    )
    
    logger.safety(
        EventCategory.SAFETY,
        "PARADA DE EMERGENCIA ACTIVADA",
        source="safety_system",
        node_id=1,
        context={
            "trigger": "emergency_button",
            "response_time_ms": 15,
            "motors_stopped": True
        }
    )
    
    # Mostrar estadísticas
    stats = logger.get_statistics()
    print(f"\n📊 Estadísticas:")
    print(f"  Total de eventos: {stats['total_events']}")
    print(f"  Por nivel:")
    for level_name, count in stats['events_by_level'].items():
        if count > 0:
            print(f"    - {level_name}: {count}")
    print(f"  Por categoría:")
    for cat_name, count in stats['events_by_category'].items():
        if count > 0:
            print(f"    - {cat_name}: {count}")
    
    print(f"\n✅ Logs guardados en: {logger.log_dir}")
    print(f"  - Texto: {logger.log_dir}/ejemplo_k13.log")
    print(f"  - JSON: {logger.log_dir}/ejemplo_k13.json")


def ejemplo_callback():
    """Ejemplo de uso de callbacks para notificaciones en tiempo real"""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Callbacks en Tiempo Real")
    print("=" * 60)
    
    logger = get_logger()
    
    # Definir callback para eventos de seguridad
    def safety_alert(event):
        if event.level == EventLevel.SAFETY or event.category == EventCategory.SAFETY:
            print(f"\n🚨 ALERTA DE SEGURIDAD:")
            print(f"   {event.message}")
            print(f"   Fuente: {event.source}")
            if event.context:
                print(f"   Contexto: {event.context}")
    
    # Definir callback para eventos críticos
    def critical_logger(event):
        if event.level.value >= EventLevel.CRITICAL.value:
            print(f"\n⚠️  EVENTO CRÍTICO: {event.level.name}")
            print(f"   {event.message}")
    
    # Registrar callbacks
    logger.register_callback(safety_alert)
    logger.register_callback(critical_logger)
    
    # Generar eventos de prueba
    logger.info(
        EventCategory.CONTROL,
        "Movimiento iniciado: subir carga",
        source="crane_controller",
        context={"direction": "up", "speed": 0.5}
    )
    
    time.sleep(0.1)
    
    logger.critical(
        EventCategory.COMMUNICATION,
        "Pérdida de conexión con nodo 1",
        source="can_monitor",
        node_id=1
    )
    
    time.sleep(0.1)
    
    logger.safety(
        EventCategory.SAFETY,
        "Límite superior alcanzado - motor detenido",
        source="limit_switch",
        context={"position": "top", "auto_stop": True}
    )
    
    # Limpiar callbacks
    logger.unregister_callback(safety_alert)
    logger.unregister_callback(critical_logger)


def ejemplo_filtrado():
    """Ejemplo de filtrado y búsqueda de eventos"""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Filtrado de Eventos")
    print("=" * 60)
    
    logger = get_logger()
    
    # Obtener solo eventos de seguridad
    safety_events = logger.get_events_by_category(EventCategory.SAFETY)
    print(f"\n🛡️  Eventos de SEGURIDAD ({len(safety_events)}):")
    for event in safety_events:
        print(f"  [{event.timestamp.strftime('%H:%M:%S')}] {event.level.name:8} - {event.message}")
    
    # Obtener solo eventos de nivel ERROR o superior
    critical_events = logger.get_events_by_level(EventLevel.ERROR)
    print(f"\n🔴 Eventos ERROR o superior ({len(critical_events)}):")
    for event in critical_events:
        print(f"  [{event.timestamp.strftime('%H:%M:%S')}] {event.level.name:8} - {event.message}")


def ejemplo_storage():
    """Ejemplo de almacenamiento persistente en SQLite"""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Almacenamiento Persistente (SQLite)")
    print("=" * 60)
    
    # Crear storage
    storage = EventStorage(
        db_dir=Path("logs/examples/db"),
        retention_days=30,
        auto_rotate=True
    )
    
    logger = get_logger()
    
    # Almacenar eventos recientes
    events = logger.get_recent_events(limit=10)
    print(f"\n💾 Almacenando {len(events)} eventos en SQLite...")
    
    for event in events:
        storage.store_event(event)
    
    # Consultar eventos almacenados
    stored_events = storage.query_events(
        min_level=EventLevel.WARNING,
        limit=5
    )
    
    print(f"\n📋 Eventos almacenados (WARNING+): {len(stored_events)}")
    for event in stored_events:
        print(f"  [{event['timestamp_iso'][:19]}] {event['level']:8} - {event['message'][:50]}")
    
    # Estadísticas de almacenamiento
    db_stats = storage.get_statistics()
    print(f"\n📊 Estadísticas de base de datos:")
    print(f"  Total de eventos: {db_stats['total_events']}")
    print(f"  Por nivel: {db_stats['by_level']}")
    
    storage.close()
    print(f"\n✅ Base de datos guardada en: {storage.db_dir}")


def ejemplo_exportar():
    """Ejemplo de exportación de eventos a JSON"""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Exportar Eventos a JSON")
    print("=" * 60)
    
    logger = get_logger()
    
    # Exportar últimos 20 eventos
    output_file = Path("logs/examples/exported_events.json")
    count = logger.export_to_json(output_file, limit=20)
    
    print(f"\n📤 Exportados {count} eventos a:")
    print(f"   {output_file.absolute()}")
    
    # Mostrar tamaño del archivo
    if output_file.exists():
        size_kb = output_file.stat().st_size / 1024
        print(f"   Tamaño: {size_kb:.2f} KB")


def ejemplo_simulacion_operacion():
    """Simular una operación real del puente grúa con eventos"""
    print("\n" + "=" * 60)
    print("EJEMPLO 6: Simulación de Operación Real")
    print("=" * 60)
    
    logger = get_logger()
    
    print("\n🏗️  Simulando operación de puente grúa...")
    
    # 1. Inicio del sistema
    logger.info(
        EventCategory.SYSTEM,
        "Sistema K13 iniciado",
        source="main",
        context={"version": "1.0.0", "mode": "production"}
    )
    time.sleep(0.2)
    
    # 2. Conexión al nodo
    logger.info(
        EventCategory.COMMUNICATION,
        "Conexión CANopen establecida",
        source="bl335_gateway",
        node_id=1,
        context={"baudrate": 250000, "protocol": "CANopen"}
    )
    time.sleep(0.2)
    
    # 3. Usuario solicita movimiento
    logger.info(
        EventCategory.USER,
        "Operador solicita movimiento: SUBIR",
        source="desktop_gui",
        context={"user": "operador_1", "action": "up"}
    )
    time.sleep(0.2)
    
    # 4. Envío de comando SDO
    logger.debug(
        EventCategory.CONTROL,
        "Enviando SDO: 0x6040 = 0x000F (Operation Enabled)",
        source="bl335_gateway",
        node_id=1,
        context={"index": "0x6040", "subindex": 0, "value": "0x000F"}
    )
    time.sleep(0.2)
    
    # 5. Motor en movimiento
    logger.info(
        EventCategory.CONTROL,
        "Motor activado - movimiento SUBIR iniciado",
        source="r13f_motor",
        node_id=1,
        context={"direction": "up", "speed_rpm": 1200}
    )
    time.sleep(0.5)
    
    # 6. Monitoreo de posición (PDO)
    logger.debug(
        EventCategory.COMMUNICATION,
        "TPDO1 recibido - posición actualizada",
        source="can_monitor",
        node_id=1,
        context={"position": 450, "velocity": 1200}
    )
    time.sleep(0.3)
    
    # 7. Advertencia de límite cercano
    logger.warning(
        EventCategory.SAFETY,
        "Acercándose al límite superior",
        source="limit_monitor",
        context={"position": 950, "limit": 1000, "margin": 50}
    )
    time.sleep(0.3)
    
    # 8. Límite alcanzado - parada automática
    logger.safety(
        EventCategory.SAFETY,
        "LÍMITE SUPERIOR ALCANZADO - Parada automática",
        source="safety_system",
        node_id=1,
        context={
            "trigger": "upper_limit_switch",
            "position": 1000,
            "stop_time_ms": 25,
            "motors_stopped": True
        }
    )
    time.sleep(0.2)
    
    # 9. Confirmación de parada
    logger.info(
        EventCategory.CONTROL,
        "Motor detenido correctamente",
        source="r13f_motor",
        node_id=1,
        context={"final_position": 1000, "velocity": 0}
    )
    time.sleep(0.2)
    
    # 10. Operación completada
    logger.info(
        EventCategory.USER,
        "Operación completada exitosamente",
        source="desktop_gui",
        context={"duration_s": 2.0, "status": "success"}
    )
    
    print("\n✅ Simulación completada")
    
    # Mostrar resumen
    recent = logger.get_recent_events(limit=10)
    print(f"\n📜 Últimos 10 eventos:")
    for event in recent:
        emoji = {
            "DEBUG": "🔍",
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🔴",
            "SAFETY": "🚨"
        }.get(event.level.name, "•")
        
        print(f"  {emoji} [{event.timestamp.strftime('%H:%M:%S.%f')[:-3]}] "
              f"{event.category.value:13} - {event.message}")


def main():
    """Ejecutar todos los ejemplos"""
    print("\n" + "=" * 60)
    print("SISTEMA DE LOGGING DE EVENTOS - K13 PUENTE GRÚA")
    print("Demostración de características")
    print("=" * 60)
    
    try:
        ejemplo_basico()
        ejemplo_callback()
        ejemplo_filtrado()
        ejemplo_storage()
        ejemplo_exportar()
        ejemplo_simulacion_operacion()
        
        print("\n" + "=" * 60)
        print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
        print("=" * 60)
        
        # Estadísticas finales
        logger = get_logger()
        stats = logger.get_statistics()
        
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"  Total de eventos generados: {stats['total_events']}")
        print(f"  Eventos en buffer: {stats['buffer_size']}/{stats['buffer_max_size']}")
        
        print(f"\n📁 Archivos generados:")
        print(f"  - logs/examples/ejemplo_k13.log")
        print(f"  - logs/examples/ejemplo_k13.json")
        print(f"  - logs/examples/db/events_*.db")
        print(f"  - logs/examples/exported_events.json")
        
        print("\n💡 Próximos pasos:")
        print("  1. Integrar EventLogger en BL335 Gateway")
        print("  2. Agregar logging a Desktop GUI")
        print("  3. Crear página de eventos en Web UI")
        print("  4. Configurar alertas en tiempo real")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
