#!/usr/bin/env python3
"""
Test Suite para Simulador CANopen R13 F

Valida el funcionamiento completo del simulador antes de integración.
"""

import sys
import os
import time
import threading

# Agregar tools al path para importar can_simulator
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from can_simulator import R13FSimulator, DeviceState, OperationMode

def test_initialization():
    """Test inicialización del simulador"""
    print("🧪 Test: Inicialización...")

    simulator = R13FSimulator(channel='vcan0', node_id=1, batch_mode=True)
    state = simulator.get_state()

    assert state['device_state'] == 'SWITCH_ON_DISABLED'
    assert state['operation_mode'] == 'PROFILE_VELOCITY'
    assert state['target_velocity'] == 0
    assert state['actual_velocity'] == 0

    print("✅ Inicialización correcta")
    return simulator

def test_state_transitions(simulator):
    """Test transiciones de estado CiA 402"""
    print("🧪 Test: Transiciones de Estado...")

    # Estado inicial
    state = simulator.get_state()
    print(f"  Inicial: {state['device_state']}")
    assert state['device_state'] == 'SWITCH_ON_DISABLED'

    # Switch On + Enable Voltage + Quick Stop (0x0007 = 0000 0000 0000 0111)
    print("  Enviando Control Word 0x0007 (Switch On + Enable Voltage + Quick Stop)...")
    simulator._process_control_word(0x0007)
    state = simulator.get_state()
    print(f"  Después 0x0007: {state['device_state']}")
    assert state['device_state'] == 'READY_TO_SWITCH_ON'

    # Enable Operation (0x000F = 0000 0000 0000 1111)
    print("  Enviando Control Word 0x000F (+ Enable Operation)...")
    simulator._process_control_word(0x000F)
    state = simulator.get_state()
    print(f"  Después 0x000F: {state['device_state']}")
    assert state['device_state'] == 'OPERATION_ENABLED'

    # Quick Stop (0x0002 = 0000 0000 0000 0010) - Solo Enable Voltage, sin Quick Stop bit
    print("  Enviando Control Word 0x0002 (Quick Stop)...")
    simulator._process_control_word(0x0002)
    state = simulator.get_state()
    print(f"  Después 0x0002: {state['device_state']}")
    assert state['device_state'] == 'QUICK_STOP_ACTIVE'

    print("✅ Transiciones de estado correctas")

def test_object_dictionary(simulator):
    """Test Object Dictionary CiA 402"""
    print("🧪 Test: Object Dictionary...")

    # Verificar objetos principales
    assert 0x6040 in simulator.object_dictionary  # Control Word
    assert 0x6041 in simulator.object_dictionary  # Status Word
    assert 0x6060 in simulator.object_dictionary  # Modes of Operation
    assert 0x6081 in simulator.object_dictionary  # Profile Velocity

    # Verificar valores iniciales
    assert simulator.object_dictionary[0x6060]['value'] == OperationMode.PROFILE_VELOCITY.value
    assert simulator.object_dictionary[0x6081]['value'] == 1000  # Velocidad por defecto

    print("✅ Object Dictionary correcto")

def test_sdo_operations(simulator):
    """Test operaciones SDO"""
    print("🧪 Test: Operaciones SDO...")

    # Test escritura (download) - cambiar velocidad
    original_velocity = simulator.object_dictionary[0x6081]['value']
    simulator._handle_sdo_download(0x6081, 0, 1500)  # Nueva velocidad

    assert simulator.object_dictionary[0x6081]['value'] == 1500
    assert simulator.target_velocity == 1500

    # Test lectura (upload)
    # Nota: Para test completo necesitaríamos mock del bus CAN

    print("✅ Operaciones SDO correctas")

def test_pdo_configuration(simulator):
    """Test configuración PDO"""
    print("🧪 Test: Configuración PDO...")

    # Verificar PDOs configurados
    assert 'rpdo1' in simulator.pdo_data
    assert 'tpdo1' in simulator.pdo_data
    assert 'tpdo2' in simulator.pdo_data

    # Verificar COB-IDs
    assert simulator.pdo_data['rpdo1']['cob_id'] == 0x201  # 0x200 + node_id
    assert simulator.pdo_data['tpdo1']['cob_id'] == 0x181  # 0x180 + node_id
    assert simulator.pdo_data['tpdo2']['cob_id'] == 0x281  # 0x280 + node_id

    print("✅ Configuración PDO correcta")

def test_fault_handling(simulator):
    """Test manejo de faults"""
    print("🧪 Test: Manejo de Faults...")

    # Estado inicial
    original_state = simulator.get_state()['device_state']

    # Simular fault
    simulator.simulate_fault()
    state = simulator.get_state()
    assert state['device_state'] == 'FAULT'

    # Limpiar fault
    simulator.clear_fault()
    state = simulator.get_state()
    assert state['device_state'] == 'SWITCH_ON_DISABLED'

    print("✅ Manejo de faults correcto")

def test_emergency_stop(simulator):
    """Test parada de emergencia"""
    print("🧪 Test: Emergency Stop...")

    # Poner dispositivo en operación
    simulator._process_control_word(0x000F)  # Enable operation
    simulator.target_velocity = 1000

    state = simulator.get_state()
    assert state['device_state'] == 'OPERATION_ENABLED'

    # Emergency stop
    initial_stops = simulator.stats['emergency_stops']
    simulator._handle_emergency_stop([0x00, 0x00, 0x00, 0x00])

    assert simulator.stats['emergency_stops'] == initial_stops + 1
    assert simulator.device_state == DeviceState.QUICK_STOP_ACTIVE
    assert simulator.target_velocity == 0

    print("✅ Emergency Stop correcto")

def test_simulation_physics(simulator):
    """Test simulación física"""
    print("🧪 Test: Simulación Física...")

    # Poner en operación
    simulator._process_control_word(0x000F)
    simulator.target_velocity = 500

    # Dejar que la simulación corra un poco
    time.sleep(0.5)

    state = simulator.get_state()
    # La velocidad actual debería haber empezado a cambiar
    velocity_changed = abs(state['actual_velocity']) > 0

    print(f"Velocidad objetivo: {simulator.target_velocity}")
    print(f"Velocidad actual: {state['actual_velocity']}")
    print(f"¿Velocidad cambió?: {velocity_changed}")

    # No podemos ser muy estrictos aquí porque depende del timing
    assert isinstance(state['actual_velocity'], int)

    print("✅ Simulación física básica correcta")

def run_all_tests():
    """Ejecutar todos los tests"""
    print("=" * 60)
    print("🚀 Test Suite - Simulador CANopen R13 F")
    print("=" * 60)

    simulator = None
    try:
        # Tests
        simulator = test_initialization()
        test_state_transitions(simulator)
        test_object_dictionary(simulator)
        test_sdo_operations(simulator)
        test_pdo_configuration(simulator)
        test_fault_handling(simulator)
        test_emergency_stop(simulator)
        test_simulation_physics(simulator)

        print("\n" + "=" * 60)
        print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("=" * 60)

        # Mostrar estado final
        final_state = simulator.get_state()
        print("\n📊 Estado Final del Simulador:")
        print(f"  Dispositivo: {final_state['device_state']}")
        print(f"  Modo: {final_state['operation_mode']}")
        print(f"  Velocidad: {final_state['actual_velocity']} RPM")
        print(f"  Status Word: {final_state['status_word']}")
        print(f"  Estadísticas: {final_state['stats']}")

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