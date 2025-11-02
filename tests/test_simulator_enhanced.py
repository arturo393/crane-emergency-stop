#!/usr/bin/env python3
"""
Test Suite Mejorado para Simulador CANopen R13 F

Tests para nuevas funcionalidades: diagnósticos, callbacks y eventos.
"""

import sys
import os
import time
import threading

# Agregar tools al path para importar can_simulator
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))

from can_simulator import R13FSimulator, DeviceState, OperationMode


def test_diagnostics(simulator):
    """Test de sistema de diagnósticos"""
    print("🧪 Test: Sistema de Diagnósticos...")

    # Obtener diagnósticos
    diag = simulator.get_diagnostics()

    # Verificar estructura
    assert 'uptime_seconds' in diag
    assert 'device_state' in diag
    assert 'operation_mode' in diag
    assert 'heartbeats_sent' in diag
    assert 'pdo_sent' in diag
    assert 'sdo_requests' in diag
    assert 'emergency_stops' in diag
    assert 'errors' in diag
    assert 'bus_errors' in diag
    assert 'timeout_errors' in diag
    assert 'state_changes' in diag
    assert 'emergency_events' in diag

    # Verificar tipos
    assert isinstance(diag['uptime_seconds'], float)
    assert isinstance(diag['device_state'], str)
    assert isinstance(diag['state_changes'], int)
    assert isinstance(diag['emergency_events'], list)

    print(f"  ✓ Uptime: {diag['uptime_seconds']:.2f}s")
    print(f"  ✓ Estado: {diag['device_state']}")
    print(f"  ✓ Cambios de estado: {diag['state_changes']}")
    print(f"  ✓ Eventos de emergencia: {len(diag['emergency_events'])}")

    print("✅ Sistema de diagnósticos correcto")


def test_event_callbacks(simulator):
    """Test de callbacks de eventos"""
    print("🧪 Test: Callbacks de Eventos...")

    events_received = []

    def event_callback(event_type, event_data):
        events_received.append({
            'type': event_type,
            'data': event_data
        })

    # Registrar callback
    simulator.register_event_callback(event_callback)

    # Simular fault
    simulator.simulate_fault()
    time.sleep(0.1)  # Dar tiempo para procesar

    # Verificar evento recibido
    assert len(events_received) > 0
    assert events_received[-1]['type'] == 'fault'
    assert 'timestamp' in events_received[-1]['data']

    # Limpiar fault
    simulator.clear_fault()
    time.sleep(0.1)

    # Verificar evento de limpieza
    assert len(events_received) > 1
    assert events_received[-1]['type'] == 'fault_cleared'

    print(f"  ✓ Eventos recibidos: {len(events_received)}")
    print(f"  ✓ Tipos: {[e['type'] for e in events_received]}")

    print("✅ Callbacks de eventos correctos")


def test_state_change_tracking(simulator):
    """Test de tracking de cambios de estado"""
    print("🧪 Test: Tracking de Cambios de Estado...")

    # Obtener estado inicial
    initial_diag = simulator.get_diagnostics()
    initial_changes = initial_diag['state_changes']

    # Hacer transiciones de estado
    simulator._process_control_word(0x0007)  # READY_TO_SWITCH_ON
    time.sleep(0.1)
    simulator._process_control_word(0x000F)  # OPERATION_ENABLED
    time.sleep(0.1)
    simulator._process_control_word(0x0002)  # QUICK_STOP_ACTIVE
    time.sleep(0.1)

    # Obtener estado final
    final_diag = simulator.get_diagnostics()
    final_changes = final_diag['state_changes']

    # Verificar que se registraron cambios
    changes = final_changes - initial_changes
    print(f"  ✓ Cambios de estado registrados: {changes}")
    assert changes >= 3  # Al menos 3 transiciones

    print("✅ Tracking de cambios correcto")


def test_emergency_event_logging(simulator):
    """Test de logging de eventos de emergencia"""
    print("🧪 Test: Logging de Eventos de Emergencia...")

    # Simular múltiples emergencias
    for i in range(3):
        simulator.simulate_fault()
        time.sleep(0.05)
        simulator.clear_fault()
        time.sleep(0.05)

    # Obtener diagnósticos
    diag = simulator.get_diagnostics()

    # Verificar que se registraron eventos
    emergency_events = diag['emergency_events']
    print(f"  ✓ Eventos de emergencia: {len(emergency_events)}")

    # Verificar estructura de eventos
    if emergency_events:
        event = emergency_events[0]
        assert 'timestamp' in event
        assert 'type' in event
        print(f"  ✓ Estructura del evento: {list(event.keys())}")

    print("✅ Logging de eventos de emergencia correcto")


def test_message_history(simulator):
    """Test de historial de mensajes"""
    print("🧪 Test: Historial de Mensajes...")

    # El simulador debe tener historial vacío en batch mode
    assert isinstance(simulator.message_history, list)
    assert len(simulator.message_history) <= simulator.max_message_history

    print(f"  ✓ Capacidad de historial: {simulator.max_message_history}")
    print(f"  ✓ Mensajes actuales: {len(simulator.message_history)}")

    print("✅ Historial de mensajes correcto")


def test_multiple_callbacks(simulator):
    """Test de múltiples callbacks"""
    print("🧪 Test: Múltiples Callbacks...")

    callback1_events = []
    callback2_events = []

    def callback1(event_type, event_data):
        callback1_events.append(event_type)

    def callback2(event_type, event_data):
        callback2_events.append(event_type)

    # Registrar ambos callbacks
    simulator.register_event_callback(callback1)
    simulator.register_event_callback(callback2)

    # Generar evento
    simulator.simulate_fault()
    time.sleep(0.1)

    # Verificar que ambos recibieron el evento
    assert len(callback1_events) > 0
    assert len(callback2_events) > 0
    assert callback1_events[-1] == 'fault'
    assert callback2_events[-1] == 'fault'

    print(f"  ✓ Callback 1 recibió: {len(callback1_events)} eventos")
    print(f"  ✓ Callback 2 recibió: {len(callback2_events)} eventos")

    print("✅ Múltiples callbacks correctos")


def test_diagnostic_timestamps(simulator):
    """Test de timestamps en diagnósticos"""
    print("🧪 Test: Timestamps en Diagnósticos...")

    # Simular actividad
    simulator._process_control_word(0x000F)
    time.sleep(0.2)

    # Obtener diagnósticos
    diag = simulator.get_diagnostics()

    # Verificar campos de timestamp
    timestamp_fields = ['last_heartbeat', 'last_pdo_rx', 'last_pdo_tx', 'last_sdo']

    print("  Timestamps:")
    for field in timestamp_fields:
        value = diag.get(field)
        print(f"    {field}: {value}")

    print("✅ Timestamps en diagnósticos correctos")


def run_all_tests():
    """Ejecutar todos los tests mejorados"""
    print("=" * 60)
    print("🚀 Test Suite Mejorado - Simulador CANopen R13 F")
    print("=" * 60)

    simulator = None
    try:
        # Crear simulador
        simulator = R13FSimulator(channel='vcan0', node_id=1, batch_mode=True)

        # Tests
        test_diagnostics(simulator)
        test_event_callbacks(simulator)
        test_state_change_tracking(simulator)
        test_emergency_event_logging(simulator)
        test_message_history(simulator)
        test_multiple_callbacks(simulator)
        test_diagnostic_timestamps(simulator)

        print("\n" + "=" * 60)
        print("🎉 TODOS LOS TESTS MEJORADOS PASARON!")
        print("=" * 60)

        # Mostrar diagnósticos finales
        final_diag = simulator.get_diagnostics()
        print("\n📊 Diagnósticos Finales:")
        print(f"  Uptime: {final_diag['uptime_seconds']:.2f}s")
        print(f"  Estado: {final_diag['device_state']}")
        print(f"  Cambios de estado: {final_diag['state_changes']}")
        print(f"  Emergencias: {final_diag['emergency_stops']}")
        print(f"  Errores: {final_diag['errors']}")
        print(f"  Errores de bus: {final_diag['bus_errors']}")

        return True

    except Exception as e:
        print(f"\n❌ ERROR en tests: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if simulator:
            simulator.stop()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
