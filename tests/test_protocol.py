"""
Tests para el módulo de protocolo K13
"""

import pytest
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from k13_controller.protocol import K13Protocol, K13Command, K13Packet


class TestK13Protocol:
    """Test suite para K13Protocol"""
    
    def test_create_simple_packet(self):
        """Test crear paquete simple sin datos"""
        packet_bytes = K13Protocol.create_packet(K13Command.STOP_ALL)
        
        # Verificar estructura básica: START + CMD + LEN + CHECKSUM + END
        assert len(packet_bytes) == 5
        assert packet_bytes[0] == 0xAA  # START_BYTE
        assert packet_bytes[1] == 0x00  # STOP_ALL command
        assert packet_bytes[2] == 0x00  # Data length = 0
        assert packet_bytes[4] == 0x55  # END_BYTE
    
    def test_create_packet_with_data(self):
        """Test crear paquete con datos"""
        data = [0x32, 0x64]  # Ejemplo: velocidad 50, dirección 100
        packet_bytes = K13Protocol.create_packet(K13Command.MOVE_UP, data)
        
        assert len(packet_bytes) == 7  # START + CMD + LEN + 2 DATA + CHECKSUM + END
        assert packet_bytes[0] == 0xAA  # START_BYTE
        assert packet_bytes[1] == 0x01  # MOVE_UP command
        assert packet_bytes[2] == 0x02  # Data length = 2
        assert packet_bytes[3] == 0x32  # First data byte
        assert packet_bytes[4] == 0x64  # Second data byte
        assert packet_bytes[6] == 0x55  # END_BYTE
    
    def test_checksum_calculation(self):
        """Test cálculo de checksum"""
        # Crear paquete conocido
        packet_bytes = K13Protocol.create_packet(K13Command.MOVE_UP, [0x32])
        
        # Calcular checksum manualmente
        expected_checksum = 0xAA ^ 0x01 ^ 0x32 ^ 0x55
        actual_checksum = packet_bytes[4]  # Posición del checksum
        
        assert actual_checksum == expected_checksum
    
    def test_parse_valid_packet(self):
        """Test parsear paquete válido"""
        # Crear paquete primero
        original_data = [0x25, 0x50]
        packet_bytes = K13Protocol.create_packet(K13Command.SET_SPEED, original_data)
        
        # Parsearlo
        is_valid, parsed_packet = K13Protocol.parse_packet(packet_bytes)
        
        assert is_valid == True
        assert parsed_packet.command == K13Command.SET_SPEED
        assert parsed_packet.data == original_data
    
    def test_parse_invalid_start_byte(self):
        """Test parsear paquete con start byte inválido"""
        invalid_packet = bytearray([0xBB, 0x01, 0x00, 0x10, 0x55])
        
        is_valid, parsed_packet = K13Protocol.parse_packet(bytes(invalid_packet))
        
        assert is_valid == False
        assert parsed_packet is None
    
    def test_parse_invalid_end_byte(self):
        """Test parsear paquete con end byte inválido"""
        invalid_packet = bytearray([0xAA, 0x01, 0x00, 0x10, 0x44])
        
        is_valid, parsed_packet = K13Protocol.parse_packet(bytes(invalid_packet))
        
        assert is_valid == False
        assert parsed_packet is None
    
    def test_parse_invalid_checksum(self):
        """Test parsear paquete con checksum inválido"""
        # Crear paquete válido y modificar checksum
        packet_bytes = bytearray(K13Protocol.create_packet(K13Command.STOP_ALL))
        packet_bytes[3] = 0xFF  # Checksum incorrecto
        
        is_valid, parsed_packet = K13Protocol.parse_packet(bytes(packet_bytes))
        
        assert is_valid == False
        assert parsed_packet is None
    
    def test_parse_packet_too_short(self):
        """Test parsear paquete muy corto"""
        short_packet = bytes([0xAA, 0x01])
        
        is_valid, parsed_packet = K13Protocol.parse_packet(short_packet)
        
        assert is_valid == False
        assert parsed_packet is None
    
    def test_get_command_map(self):
        """Test obtener mapeo de comandos"""
        command_map = K13Protocol.get_command_map()
        
        # Verificar algunos comandos clave
        assert "move_up" in command_map
        assert "move_down" in command_map
        assert "stop" in command_map
        assert "emergency_stop" in command_map
        
        assert command_map["move_up"] == K13Command.MOVE_UP
        assert command_map["stop"] == K13Command.STOP_ALL
        assert command_map["emergency_stop"] == K13Command.EMERGENCY_STOP


class TestK13Command:
    """Test suite para K13Command enum"""
    
    def test_command_values(self):
        """Test valores de comandos"""
        assert K13Command.STOP_ALL.value == 0x00
        assert K13Command.MOVE_UP.value == 0x01
        assert K13Command.MOVE_DOWN.value == 0x02
        assert K13Command.EMERGENCY_STOP.value == 0xFF
    
    def test_command_from_value(self):
        """Test crear comando desde valor"""
        cmd = K13Command(0x01)
        assert cmd == K13Command.MOVE_UP
        
        cmd = K13Command(0xFF)
        assert cmd == K13Command.EMERGENCY_STOP


class TestK13Packet:
    """Test suite para K13Packet dataclass"""
    
    def test_default_packet(self):
        """Test paquete con valores por defecto"""
        packet = K13Packet()
        
        assert packet.start_byte == 0xAA
        assert packet.command == K13Command.STOP_ALL
        assert packet.data == []
        assert packet.checksum == 0
        assert packet.end_byte == 0x55
    
    def test_custom_packet(self):
        """Test paquete con valores personalizados"""
        packet = K13Packet(
            command=K13Command.MOVE_UP,
            data=[0x50, 0x25],
            checksum=0xAB
        )
        
        assert packet.command == K13Command.MOVE_UP
        assert packet.data == [0x50, 0x25]
        assert packet.checksum == 0xAB


# Test de integración
class TestProtocolIntegration:
    """Tests de integración del protocolo"""
    
    def test_roundtrip_packet(self):
        """Test crear y parsear paquete (ida y vuelta)"""
        # Crear paquete
        original_command = K13Command.SET_SPEED
        original_data = [0x64, 0x32, 0x10]  # Ejemplo de datos
        
        packet_bytes = K13Protocol.create_packet(original_command, original_data)
        
        # Parsearlo de vuelta
        is_valid, parsed_packet = K13Protocol.parse_packet(packet_bytes)
        
        # Verificar que coincide
        assert is_valid == True
        assert parsed_packet.command == original_command
        assert parsed_packet.data == original_data
    
    def test_all_commands_roundtrip(self):
        """Test todos los comandos en roundtrip"""
        test_data = [0x50]  # Datos de ejemplo
        
        for command in K13Command:
            # Crear paquete
            packet_bytes = K13Protocol.create_packet(command, test_data)
            
            # Parsearlo
            is_valid, parsed_packet = K13Protocol.parse_packet(packet_bytes)
            
            # Verificar
            assert is_valid == True, f"Failed for command {command}"
            assert parsed_packet.command == command, f"Command mismatch for {command}"
            assert parsed_packet.data == test_data, f"Data mismatch for {command}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
