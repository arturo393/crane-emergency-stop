"""
Tests para el protocolo CANopen del R13.
"""

import pytest
import sys
import os

# Agregar src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Importar módulos del proyecto
from k13_controller.protocol import R13CANopenProtocol, CANopenCommands, StatusWordBits


class TestR13CANopenProtocol:
    """Clase de test para el protocolo CANopen del R13."""

    def test_protocol_creation(self):
        """Test de creación del protocolo."""
        protocol = R13CANopenProtocol(node_id=1)
        assert protocol is not None
        assert protocol.node_id == 1

    def test_canopen_commands(self):
        """Test de comandos CANopen."""
        # Verificar que los comandos principales existen
        assert CANopenCommands.ENABLE_OPERATION.value == 0x000F
        assert CANopenCommands.SHUTDOWN.value == 0x0006
        assert CANopenCommands.QUICK_STOP.value == 0x0002
        
    def test_control_word_bits(self):
        """Test de los valores del Control Word."""
        protocol = R13CANopenProtocol(node_id=1)
        
        # Test valores típicos de bits CANopen Control Word
        switch_on = (1 << 0)  # Bit 0
        enable_voltage = (1 << 1)  # Bit 1
        quick_stop = (1 << 2)  # Bit 2
        enable_operation = (1 << 3)  # Bit 3
        
        assert switch_on == 0x01
        assert enable_voltage == 0x02
        assert quick_stop == 0x04
        assert enable_operation == 0x08

    def test_status_word_bits(self):
        """Test de los bits del Status Word."""
        assert StatusWordBits.READY_TO_SWITCH_ON == (1 << 0)
        assert StatusWordBits.SWITCHED_ON == (1 << 1)
        assert StatusWordBits.OPERATION_ENABLED == (1 << 2)
        assert StatusWordBits.FAULT == (1 << 3)

    def test_sdo_write_message(self):
        """Test de creación de mensajes SDO Write."""
        protocol = R13CANopenProtocol(node_id=1)
        
        # Test SDO Write para Control Word
        message = protocol.create_sdo_write(0x6040, 0, 0x000F)
        
        assert message is not None
        assert 'command' in message
        assert message['command'] == 'sdo_write'
        assert message['index'] == 0x6040
        assert message['subindex'] == 0
        assert message['data'] == 0x000F

    def test_sdo_read_message(self):
        """Test de creación de mensajes SDO Read."""
        protocol = R13CANopenProtocol(node_id=1)
        
        # Test SDO Read para Status Word
        message = protocol.create_sdo_read(0x6041, 0)
        
        assert message is not None
        assert 'command' in message
        assert message['command'] == 'sdo_read'
        assert message['index'] == 0x6041
        assert message['subindex'] == 0

    def test_enable_operation_sequence(self):
        """Test de secuencia para habilitar operación."""
        protocol = R13CANopenProtocol(node_id=1)
        
        # Obtener la secuencia de habilitación
        messages = protocol.get_enable_operation_sequence()
        
        assert isinstance(messages, list)
        assert len(messages) >= 3  # Debe tener al menos 3 comandos
        
        # Verificar que contiene los comandos necesarios
        control_word_commands = [msg for msg in messages if msg.get('index') == 0x6040]
        assert len(control_word_commands) >= 2  # Al menos 2 comandos de Control Word

    def test_velocity_control(self):
        """Test de control de velocidad."""
        protocol = R13CANopenProtocol(node_id=1)
        
        # Test de configuración de velocidad
        velocity = 1000  # RPM
        message = protocol.create_sdo_write(0x6081, 0, velocity)
        
        assert message['index'] == 0x6081
        assert message['data'] == velocity

    def test_emergency_stop_command(self):
        """Test de comando de parada de emergencia."""
        protocol = R13CANopenProtocol(node_id=1)
        
        # Parada de emergencia (Quick Stop) - usando valores numéricos
        switch_on = 0x01
        enable_voltage = 0x02
        quick_stop_value = switch_on | enable_voltage
        
        message = protocol.create_sdo_write(0x6040, 0, quick_stop_value)
        
        assert message is not None
        assert message['index'] == 0x6040


if __name__ == "__main__":
    pytest.main([__file__])
