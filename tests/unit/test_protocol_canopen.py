"""
Tests para el protocolo CANopen del R13.
"""

import pytest
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

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
        # StatusWordBits contiene los índices de bits, no las máscaras
        assert StatusWordBits.READY_TO_SWITCH_ON == 0
        assert StatusWordBits.SWITCHED_ON == 1
        assert StatusWordBits.OPERATION_ENABLED == 2
        assert StatusWordBits.FAULT == 3

    def test_sdo_write_message(self):
        """Test de creación de mensajes SDO Write."""
        protocol = R13CANopenProtocol(node_id=1)
        
        # Test SDO Write para Control Word
        message = protocol.create_sdo_write(0x6040, 0, 0x000F)
        
        assert message is not None
        assert message.node_id == 1
        assert message.index == 0x6040
        assert message.sub_index == 0
        assert message.is_write == True
        # Verificar que data es bytes (little endian)
        assert message.data == (0x000F).to_bytes(4, byteorder='little')

    def test_sdo_read_message(self):
        """Test de creación de mensajes SDO Read."""
        protocol = R13CANopenProtocol(node_id=1)
        
        # Test SDO Read para Status Word
        message = protocol.create_sdo_read(0x6041, 0)
        
        assert message is not None
        assert message.node_id == 1
        assert message.index == 0x6041
        assert message.sub_index == 0
        assert message.is_write == False

    def test_enable_operation_sequence(self):
        """Test de secuencia para habilitar operación usando comandos individuales."""
        protocol = R13CANopenProtocol(node_id=1)
        
        # La secuencia de habilitación típica en CiA 402 es:
        # 1. Shutdown -> 2. Switch On -> 3. Enable Operation
        
        # Test comando Shutdown
        msg1 = protocol.send_control_command(CANopenCommands.SHUTDOWN)
        assert msg1.index == 0x6040
        assert msg1.is_write == True
        
        # Test comando Switch On
        msg2 = protocol.send_control_command(CANopenCommands.SWITCH_ON)
        assert msg2.index == 0x6040
        
        # Test comando Enable Operation
        msg3 = protocol.send_control_command(CANopenCommands.ENABLE_OPERATION)
        assert msg3.index == 0x6040

    def test_velocity_control(self):
        """Test de control de velocidad."""
        protocol = R13CANopenProtocol(node_id=1)
        
        # Test de configuración de velocidad
        velocity = 1000  # RPM
        message = protocol.set_target_velocity(velocity)
        
        assert message.index == 0x6081
        assert message.is_write == True
        # Verificar que velocity se convierte a bytes correctamente
        assert message.data == velocity.to_bytes(4, byteorder='little')

    def test_emergency_stop_command(self):
        """Test de comando de parada de emergencia."""
        protocol = R13CANopenProtocol(node_id=1)
        
        # Parada de emergencia usando el comando Quick Stop
        message = protocol.send_control_command(CANopenCommands.QUICK_STOP)
        
        assert message is not None
        assert message.index == 0x6040
        assert message.is_write == True
        # Verificar que el valor es el correcto para Quick Stop
        assert message.data == (0x0002).to_bytes(2, byteorder='little')


if __name__ == "__main__":
    pytest.main([__file__])
