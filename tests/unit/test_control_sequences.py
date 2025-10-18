"""
Tests para las secuencias de control complejas
"""

import pytest
import time
import logging
from src.k13_controller.control_sequences import (
    ControlSequences,
    SequenceResult
)
from src.bl335_gateway.simulator_adapter import IntegratedSystem


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestSequences")


@pytest.fixture
def integrated_system():
    """Fixture para sistema integrado"""
    system = IntegratedSystem(node_id=1, tcp_port=9998)
    
    if not system.start():
        pytest.skip("No se pudo iniciar sistema integrado")
    
    time.sleep(1)
    
    yield system
    
    system.stop()


@pytest.fixture
def control_sequences(integrated_system):
    """Fixture para secuencias de control"""
    sequences = ControlSequences(
        gateway=integrated_system.gateway,
        simulator=integrated_system.simulator
    )
    
    yield sequences
    
    sequences.reset_abort()


class TestBasicSequences:
    """Tests para secuencias básicas"""
    
    def test_startup_sequence(self, control_sequences):
        """Test: Secuencia de arranque completa"""
        result = control_sequences.startup_sequence()
        
        assert result == SequenceResult.SUCCESS
        assert control_sequences.get_device_state() == 'OPERATION_ENABLED'
    
    def test_normal_shutdown(self, control_sequences):
        """Test: Parada normal"""
        # Primero arrancar
        control_sequences.startup_sequence()
        time.sleep(0.5)
        
        # Luego parar normalmente
        result = control_sequences.shutdown_sequence(emergency=False)
        
        assert result == SequenceResult.SUCCESS
        state = control_sequences.get_device_state()
        assert state in ['SWITCHED_ON', 'READY_TO_SWITCH_ON']
    
    def test_emergency_shutdown(self, control_sequences):
        """Test: Parada de emergencia"""
        # Arrancar
        control_sequences.startup_sequence()
        time.sleep(0.5)
        
        # Parada de emergencia
        result = control_sequences.shutdown_sequence(emergency=True)
        
        assert result == SequenceResult.SUCCESS


class TestVelocitySequences:
    """Tests para secuencias de velocidad"""
    
    def test_set_velocity_safe(self, control_sequences):
        """Test: Configurar velocidad con rampa"""
        # Arrancar
        control_sequences.startup_sequence()
        time.sleep(0.5)
        
        # Configurar velocidad
        result = control_sequences.set_velocity_safe(
            target_velocity=1500,
            ramp_time=1.0
        )
        
        assert result == SequenceResult.SUCCESS
        
        # Verificar que se aplicó
        state = control_sequences.simulator.get_state()
        assert state['target_velocity'] == 1500
    
    def test_velocity_ramp_multiple_steps(self, control_sequences):
        """Test: Rampa de velocidad con múltiples pasos"""
        control_sequences.startup_sequence()
        time.sleep(0.5)
        
        # Rampa de 0 a 3000 RPM
        result = control_sequences.set_velocity_safe(
            target_velocity=3000,
            ramp_time=2.0
        )
        
        assert result == SequenceResult.SUCCESS
    
    def test_velocity_without_operation_enabled(self, control_sequences):
        """Test: Intentar configurar velocidad sin estar en OPERATION_ENABLED"""
        # NO arrancar, intentar configurar velocidad
        result = control_sequences.set_velocity_safe(1000)
        
        assert result == SequenceResult.FAILED


class TestWaitForState:
    """Tests para wait_for_state"""
    
    def test_wait_for_state_success(self, control_sequences):
        """Test: Esperar estado exitoso"""
        # Inicialmente debería estar en NOT_READY_TO_SWITCH_ON
        current = control_sequences.get_device_state()
        
        # Comando para ir a READY_TO_SWITCH_ON
        data = bytes([0x06, 0x00, 0x00, 0x00])
        control_sequences.gateway.pdo_write(1, data)
        
        # Esperar transición
        success = control_sequences.wait_for_state('READY_TO_SWITCH_ON', timeout=3.0)
        
        assert success is True
    
    def test_wait_for_state_timeout(self, control_sequences):
        """Test: Timeout esperando estado imposible"""
        success = control_sequences.wait_for_state('IMPOSSIBLE_STATE', timeout=1.0)
        
        assert success is False
    
    def test_wait_for_state_abort(self, control_sequences):
        """Test: Abortar espera de estado"""
        import threading
        
        def abort_after_delay():
            time.sleep(0.5)
            control_sequences.abort()
        
        # Iniciar thread que abortará
        abort_thread = threading.Thread(target=abort_after_delay)
        abort_thread.start()
        
        # Intentar esperar estado que nunca llegará
        success = control_sequences.wait_for_state('IMPOSSIBLE_STATE', timeout=5.0)
        
        abort_thread.join()
        
        assert success is False


class TestComplexSequences:
    """Tests para secuencias complejas"""
    
    def test_full_operation_cycle(self, control_sequences):
        """Test: Ciclo completo de operación"""
        # 1. Arranque
        result = control_sequences.startup_sequence()
        assert result == SequenceResult.SUCCESS
        
        time.sleep(0.5)
        
        # 2. Configurar velocidad
        result = control_sequences.set_velocity_safe(2000, ramp_time=1.0)
        assert result == SequenceResult.SUCCESS
        
        time.sleep(1.0)
        
        # 3. Parada normal
        result = control_sequences.shutdown_sequence(emergency=False)
        assert result == SequenceResult.SUCCESS
    
    def test_emergency_during_operation(self, control_sequences):
        """Test: Emergencia durante operación"""
        # Arrancar y configurar velocidad
        control_sequences.startup_sequence()
        time.sleep(0.5)
        
        control_sequences.set_velocity_safe(2500, ramp_time=0.5)
        time.sleep(0.3)
        
        # Parada de emergencia
        result = control_sequences.shutdown_sequence(emergency=True)
        
        assert result == SequenceResult.SUCCESS
    
    def test_multiple_velocity_changes(self, control_sequences):
        """Test: Múltiples cambios de velocidad"""
        control_sequences.startup_sequence()
        time.sleep(0.5)
        
        velocities = [1000, 2000, 1500, 500, 2500]
        
        for vel in velocities:
            result = control_sequences.set_velocity_safe(vel, ramp_time=0.5)
            assert result == SequenceResult.SUCCESS
            time.sleep(0.3)


class TestStateTransitions:
    """Tests para transiciones de estado"""
    
    def test_startup_from_different_initial_states(self, control_sequences):
        """Test: Arranque desde diferentes estados iniciales"""
        # Caso 1: Desde NOT_READY_TO_SWITCH_ON
        result = control_sequences.startup_sequence()
        assert result == SequenceResult.SUCCESS
        
        # Caso 2: Desde SWITCHED_ON (parada normal primero)
        control_sequences.shutdown_sequence(emergency=False)
        time.sleep(0.5)
        
        result = control_sequences.startup_sequence()
        assert result == SequenceResult.SUCCESS
    
    def test_state_machine_integrity(self, control_sequences):
        """Test: Integridad de la máquina de estados"""
        # Secuencia completa de transiciones
        states = []
        
        # Arranque
        control_sequences.startup_sequence()
        states.append(control_sequences.get_device_state())
        
        # Parada normal
        control_sequences.shutdown_sequence(emergency=False)
        time.sleep(0.3)
        states.append(control_sequences.get_device_state())
        
        # Re-arranque
        control_sequences.startup_sequence()
        states.append(control_sequences.get_device_state())
        
        # Verificar estados válidos
        valid_states = [
            'NOT_READY_TO_SWITCH_ON',
            'SWITCH_ON_DISABLED', 
            'READY_TO_SWITCH_ON',
            'SWITCHED_ON',
            'OPERATION_ENABLED',
            'QUICK_STOP_ACTIVE'
        ]
        
        for state in states:
            assert state in valid_states


class TestErrorHandling:
    """Tests para manejo de errores"""
    
    def test_abort_sequence(self, control_sequences):
        """Test: Abortar secuencia en progreso"""
        import threading
        
        def abort_after_delay():
            time.sleep(0.3)
            control_sequences.abort()
        
        # Iniciar arranque
        control_sequences.startup_sequence()
        
        # Thread que abortará
        abort_thread = threading.Thread(target=abort_after_delay)
        abort_thread.start()
        
        # Intentar rampa larga
        result = control_sequences.set_velocity_safe(5000, ramp_time=3.0)
        
        abort_thread.join()
        
        # Debería haberse abortado
        assert result == SequenceResult.ABORTED
    
    def test_reset_abort_flag(self, control_sequences):
        """Test: Resetear flag de abort"""
        control_sequences.abort()
        assert control_sequences.abort_requested is True
        
        control_sequences.reset_abort()
        assert control_sequences.abort_requested is False


def test_demo_sequences():
    """Test: Ejecutar demo de secuencias"""
    from src.k13_controller.control_sequences import demo_sequences
    
    # Ejecutar demo (debería retornar 0 en éxito)
    # Nota: Este test puede ser lento
    result = demo_sequences()
    
    assert result == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
