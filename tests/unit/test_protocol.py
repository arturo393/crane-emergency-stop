"""
Tests para el módulo de protocolo CANopen del Danfoss R13
"""

import pytest
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from k13_controller.protocol import (
    R13CANopenProtocol, 
    CANopenCommands, 
    OperationModes, 
    StatusWordBits, 
    CANopenObjectDict,
    CANopenSDO,
    CANopenPDO
)


"""
Tests para el módulo de protocolo CANopen del Danfoss R13
"""

import pytest
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from k13_controller.protocol import (
    R13CANopenProtocol, 
    CANopenCommands, 
    OperationModes, 
    StatusWordBits, 
    CANopenObjectDict,
    CANopenSDO,
    CANopenPDO
)


class TestR13CANopenProtocol:
    """Test suite para R13CANopenProtocol"""
    
    def test_initialization(self):
        """Test inicialización del protocolo"""
        protocol = R13CANopenProtocol(node_id=5)
        assert protocol.node_id == 5
        
        # Test con node_id por defecto
        protocol_default = R13CANopenProtocol()
        assert protocol_default.node_id == 1
    
    def test_create_sdo_write(self):
        """Test crear mensaje SDO de escritura"""
        protocol = R13CANopenProtocol(node_id=1)
        
        # Test escritura de 4 bytes
        sdo = protocol.create_sdo_write(0x6040, 0, 0x000F, 4)
        assert sdo.node_id == 1
        assert sdo.index == 0x6040
        assert sdo.sub_index == 0
        assert sdo.data == b'\x0f\x00\x00\x00'  # Little endian
        assert sdo.is_write == True
        
        # Test escritura de 2 bytes
        sdo = protocol.create_sdo_write(0x6060, 0, 0x0003, 2)
        assert sdo.data == b'\x03\x00'
        
        # Test escritura de 1 byte
        sdo = protocol.create_sdo_write(0x6060, 0, 0x01, 1)
        assert sdo.data == b'\x01'
    
    def test_create_sdo_read(self):
        """Test crear mensaje SDO de lectura"""
        protocol = R13CANopenProtocol(node_id=2)
        
        sdo = protocol.create_sdo_read(0x6041, 0)
        assert sdo.node_id == 2
        assert sdo.index == 0x6041
        assert sdo.sub_index == 0
        assert sdo.data == b''
        assert sdo.is_write == False
    
    def test_set_operation_mode(self):
        """Test configurar modo de operación"""
        protocol = R13CANopenProtocol()
        
        sdo = protocol.set_operation_mode(OperationModes.PROFILE_VELOCITY)
        assert sdo.index == CANopenObjectDict.MODES_OF_OPERATION
        assert sdo.sub_index == 0
        assert sdo.data == b'\x03'  # PROFILE_VELOCITY = 3
        assert sdo.is_write == True
    
    def test_send_control_command(self):
        """Test enviar comando de control"""
        protocol = R13CANopenProtocol()
        
        sdo = protocol.send_control_command(CANopenCommands.ENABLE_OPERATION)
        assert sdo.index == CANopenObjectDict.CONTROL_WORD
        assert sdo.sub_index == 0
        assert sdo.data == b'\x0f\x00'  # ENABLE_OPERATION = 0x000F
        assert sdo.is_write == True
    
    def test_set_target_velocity(self):
        """Test establecer velocidad objetivo"""
        protocol = R13CANopenProtocol()
        
        sdo = protocol.set_target_velocity(1000)
        assert sdo.index == CANopenObjectDict.PROFILE_VELOCITY
        assert sdo.sub_index == 0
        assert sdo.data == b'\xe8\x03\x00\x00'  # 1000 en little endian
        assert sdo.is_write == True
    
    def test_set_target_position(self):
        """Test establecer posición objetivo"""
        protocol = R13CANopenProtocol()
        
        sdo = protocol.set_target_position(50000)
        assert sdo.index == CANopenObjectDict.TARGET_POSITION
        assert sdo.sub_index == 0
        assert sdo.data == b'\x50\xc3\x00\x00'  # 50000 en little endian
        assert sdo.is_write == True
    
    def test_read_status_operations(self):
        """Test operaciones de lectura de estado"""
        protocol = R13CANopenProtocol()
        
        # Status word
        sdo = protocol.read_status_word()
        assert sdo.index == CANopenObjectDict.STATUS_WORD
        assert sdo.is_write == False
        
        # Actual velocity
        sdo = protocol.read_actual_velocity()
        assert sdo.index == CANopenObjectDict.VELOCITY_ACTUAL_VALUE
        assert sdo.is_write == False
        
        # Actual position
        sdo = protocol.read_actual_position()
        assert sdo.index == CANopenObjectDict.POSITION_ACTUAL_VALUE
        assert sdo.is_write == False


class TestCANopenSDO:
    """Test suite para CANopenSDO dataclass"""
    
    def test_sdo_creation(self):
        """Test creación de SDO"""
        sdo = CANopenSDO(
            node_id=1,
            index=0x6040,
            sub_index=0,
            data=b'\x0f\x00\x00\x00',
            is_write=True
        )
        
        assert sdo.node_id == 1
        assert sdo.index == 0x6040
        assert sdo.sub_index == 0
        assert sdo.data == b'\x0f\x00\x00\x00'
        assert sdo.is_write == True
    
    def test_sdo_defaults(self):
        """Test valores por defecto de SDO"""
        sdo = CANopenSDO(node_id=1, index=0x6041, sub_index=0, data=b'')
        
        assert sdo.is_write == True  # Default value


class TestCANopenPDO:
    """Test suite para CANopenPDO dataclass"""
    
    def test_pdo_creation(self):
        """Test creación de PDO"""
        pdo = CANopenPDO(
            cob_id=0x201,
            data=b'\x0f\x00\x00\x00\x00\x00\x00\x00',
            length=8
        )
        
        assert pdo.cob_id == 0x201
        assert pdo.data == b'\x0f\x00\x00\x00\x00\x00\x00\x00'
        assert pdo.length == 8
    
    def test_pdo_defaults(self):
        """Test valores por defecto de PDO"""
        pdo = CANopenPDO(cob_id=0x181, data=b'\x00\x00')
        
        assert pdo.length == 8  # Default value


class TestStatusWordDecoding:
    """Test suite para decodificación del Status Word"""
    
    def test_decode_status_word_all_bits(self):
        """Test decodificar Status Word con todos los bits"""
        protocol = R13CANopenProtocol()
        
        # Status word con varios bits activados: 0,1,2,4,5,7,9,10
        # Bits: 0+1+2+4+5+7+9+10 = 1+2+4+16+32+128+512+1024 = 1719
        status_value = 1719  # 0b11010110111
        
        decoded = protocol.decode_status_word(status_value)
        
        assert decoded['ready_to_switch_on'] == True
        assert decoded['switched_on'] == True
        assert decoded['operation_enabled'] == True
        assert decoded['fault'] == False
        assert decoded['voltage_enabled'] == True
        assert decoded['quick_stop'] == True
        assert decoded['switch_on_disabled'] == False
        assert decoded['warning'] == True
        assert decoded['remote'] == True
        assert decoded['target_reached'] == True
    
    def test_decode_status_word_fault_state(self):
        """Test decodificar Status Word en estado de error"""
        protocol = R13CANopenProtocol()
        
        # Solo bit de fault activado
        status_value = (1 << StatusWordBits.FAULT)
        
        decoded = protocol.decode_status_word(status_value)
        
        assert decoded['fault'] == True
        assert decoded['ready_to_switch_on'] == False
        assert decoded['operation_enabled'] == False


class TestCommandMappings:
    """Test suite para mapeos de comandos"""
    
    def test_get_command_map(self):
        """Test obtener mapeo de comandos"""
        command_map = R13CANopenProtocol.get_command_map()
        
        assert isinstance(command_map, dict)
        assert "enable" in command_map
        assert "disable" in command_map
        assert "stop" in command_map
        assert "reset" in command_map
        
        assert command_map["enable"] == CANopenCommands.ENABLE_OPERATION
        assert command_map["stop"] == CANopenCommands.QUICK_STOP
        assert command_map["reset"] == CANopenCommands.FAULT_RESET
    
    def test_get_operation_modes(self):
        """Test obtener mapeo de modos de operación"""
        modes_map = R13CANopenProtocol.get_operation_modes()
        
        assert isinstance(modes_map, dict)
        assert "position" in modes_map
        assert "velocity" in modes_map
        assert "homing" in modes_map
        
        assert modes_map["position"] == OperationModes.PROFILE_POSITION
        assert modes_map["velocity"] == OperationModes.PROFILE_VELOCITY
        assert modes_map["homing"] == OperationModes.HOMING


class TestEnums:
    """Test suite para enums del protocolo"""
    
    def test_canopen_commands_values(self):
        """Test valores de comandos CANopen"""
        assert CANopenCommands.SHUTDOWN.value == 0x0006
        assert CANopenCommands.SWITCH_ON.value == 0x0007
        assert CANopenCommands.ENABLE_OPERATION.value == 0x000F
        assert CANopenCommands.QUICK_STOP.value == 0x0002
        assert CANopenCommands.FAULT_RESET.value == 0x0080
    
    def test_operation_modes_values(self):
        """Test valores de modos de operación"""
        assert OperationModes.PROFILE_POSITION.value == 1
        assert OperationModes.PROFILE_VELOCITY.value == 3
        assert OperationModes.HOMING.value == 6
        assert OperationModes.CYCLIC_SYNC_POSITION.value == 8
    
    def test_status_word_bits_values(self):
        """Test valores de bits del Status Word"""
        assert StatusWordBits.READY_TO_SWITCH_ON.value == 0
        assert StatusWordBits.SWITCHED_ON.value == 1
        assert StatusWordBits.OPERATION_ENABLED.value == 2
        assert StatusWordBits.FAULT.value == 3
        assert StatusWordBits.TARGET_REACHED.value == 10


class TestObjectDictionary:
    """Test suite para el diccionario de objetos CANopen"""
    
    def test_mandatory_objects(self):
        """Test objetos obligatorios del diccionario"""
        assert CANopenObjectDict.DEVICE_TYPE == 0x1000
        assert CANopenObjectDict.ERROR_REGISTER == 0x1001
        assert CANopenObjectDict.MANUFACTURER_STATUS_REGISTER == 0x1002
    
    def test_pdo_objects(self):
        """Test objetos PDO"""
        assert CANopenObjectDict.RPDO1_PARAMETER == 0x1400
        assert CANopenObjectDict.RPDO1_MAPPING == 0x1600
        assert CANopenObjectDict.TPDO1_PARAMETER == 0x1800
        assert CANopenObjectDict.TPDO1_MAPPING == 0x1A00
    
    def test_motion_control_objects(self):
        """Test objetos de control de movimiento"""
        assert CANopenObjectDict.CONTROL_WORD == 0x6040
        assert CANopenObjectDict.STATUS_WORD == 0x6041
        assert CANopenObjectDict.MODES_OF_OPERATION == 0x6060
        assert CANopenObjectDict.POSITION_ACTUAL_VALUE == 0x6064
        assert CANopenObjectDict.VELOCITY_ACTUAL_VALUE == 0x606C
        assert CANopenObjectDict.TARGET_POSITION == 0x607A
        assert CANopenObjectDict.PROFILE_VELOCITY == 0x6081


# Test de integración
class TestProtocolIntegration:
    """Tests de integración del protocolo CANopen"""
    
    def test_full_control_sequence(self):
        """Test secuencia completa de control"""
        protocol = R13CANopenProtocol(node_id=1)
        
        # 1. Configurar modo de operación
        mode_sdo = protocol.set_operation_mode(OperationModes.PROFILE_VELOCITY)
        assert mode_sdo.index == 0x6060
        assert mode_sdo.data == b'\x03'
        
        # 2. Establecer velocidad objetivo
        velocity_sdo = protocol.set_target_velocity(1500)
        assert velocity_sdo.index == 0x6081
        assert velocity_sdo.data == b'\xdc\x05\x00\x00'  # 1500
        
        # 3. Habilitar operación
        enable_sdo = protocol.send_control_command(CANopenCommands.ENABLE_OPERATION)
        assert enable_sdo.index == 0x6040
        assert enable_sdo.data == b'\x0f\x00'
        
        # 4. Leer estado
        status_sdo = protocol.read_status_word()
        assert status_sdo.index == 0x6041
        assert status_sdo.is_write == False
    
    def test_emergency_sequence(self):
        """Test secuencia de parada de emergencia"""
        protocol = R13CANopenProtocol()
        
        # Enviar parada rápida
        stop_sdo = protocol.send_control_command(CANopenCommands.QUICK_STOP)
        assert stop_sdo.index == 0x6040
        assert stop_sdo.data == b'\x02\x00'
        
        # Reset de errores
        reset_sdo = protocol.send_control_command(CANopenCommands.FAULT_RESET)
        assert reset_sdo.index == 0x6040
        assert reset_sdo.data == b'\x80\x00'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
