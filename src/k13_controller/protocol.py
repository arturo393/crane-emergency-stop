"""
Protocolos de comunicación CANopen para el dispositivo Danfoss R13.

Este módulo define las estructuras y comandos específicos para controlar
el receptor Danfoss R13 a través del protocolo CANopen.
"""

from enum import Enum, IntEnum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class CANopenCommands(Enum):
    """Comandos principales para control CANopen del R13."""
    # Control Word commands (0x6040)
    SHUTDOWN = 0x0006          # Apagar
    SWITCH_ON = 0x0007         # Encender
    ENABLE_OPERATION = 0x000F  # Habilitar operación
    DISABLE_OPERATION = 0x0007 # Deshabilitar operación
    QUICK_STOP = 0x0002        # Parada rápida
    DISABLE_VOLTAGE = 0x0000   # Deshabilitar voltaje
    FAULT_RESET = 0x0080       # Reset de errores


class OperationModes(IntEnum):
    """Modos de operación según CiA 402."""
    PROFILE_POSITION = 1       # Control de posición con perfil
    PROFILE_VELOCITY = 3       # Control de velocidad con perfil
    PROFILE_TORQUE = 4         # Control de torque con perfil
    HOMING = 6                 # Modo de búsqueda de origen
    INTERPOLATED_POSITION = 7  # Posición interpolada
    CYCLIC_SYNC_POSITION = 8   # Posición síncrona cíclica
    CYCLIC_SYNC_VELOCITY = 9   # Velocidad síncrona cíclica
    CYCLIC_SYNC_TORQUE = 10    # Torque síncrono cíclico


class StatusWordBits(IntEnum):
    """Bits del Status Word (0x6041)."""
    READY_TO_SWITCH_ON = 0     # Bit 0: Listo para activar
    SWITCHED_ON = 1            # Bit 1: Activado
    OPERATION_ENABLED = 2      # Bit 2: Operación habilitada
    FAULT = 3                  # Bit 3: Error presente
    VOLTAGE_ENABLED = 4        # Bit 4: Voltaje habilitado
    QUICK_STOP = 5             # Bit 5: En parada rápida
    SWITCH_ON_DISABLED = 6     # Bit 6: Activación deshabilitada
    WARNING = 7                # Bit 7: Advertencia
    REMOTE = 9                 # Bit 9: Control remoto activo
    TARGET_REACHED = 10        # Bit 10: Objetivo alcanzado


class CANopenObjectDict:
    """Diccionario de objetos CANopen para el R13 (según CiA 402)."""
    
    # Identity Objects (Mandatory)
    DEVICE_TYPE = 0x1000
    ERROR_REGISTER = 0x1001
    MANUFACTURER_STATUS_REGISTER = 0x1002
    
    # SDO Parameters
    SDO_SERVER_PARAMETER = 0x1200
    
    # PDO Parameters
    RPDO1_PARAMETER = 0x1400  # Receive PDO 1 (comandos hacia el dispositivo)
    RPDO1_MAPPING = 0x1600
    TPDO1_PARAMETER = 0x1800  # Transmit PDO 1 (estado del dispositivo)
    TPDO1_MAPPING = 0x1A00
    
    # Motion Control Objects (CiA 402)
    CONTROL_WORD = 0x6040           # Control principal
    STATUS_WORD = 0x6041            # Estado del dispositivo
    MODES_OF_OPERATION = 0x6060     # Modo de operación
    MODES_OF_OPERATION_DISPLAY = 0x6061  # Modo actual
    POSITION_ACTUAL_VALUE = 0x6064  # Posición actual
    VELOCITY_ACTUAL_VALUE = 0x606C  # Velocidad actual
    TARGET_POSITION = 0x607A        # Posición objetivo
    PROFILE_VELOCITY = 0x6081       # Velocidad de perfil
    PROFILE_ACCELERATION = 0x6083   # Aceleración
    PROFILE_DECELERATION = 0x6084   # Desaceleración
    QUICK_STOP_DECELERATION = 0x6085 # Desaceleración parada rápida
    
    # Danfoss specific objects (ejemplo - verificar con EDS real)
    DANFOSS_CUSTOM_STATUS = 0x2000  # Estado personalizado Danfoss
    DANFOSS_DIAGNOSTICS = 0x2100    # Diagnósticos


@dataclass
class CANopenSDO:
    """Estructura para mensajes SDO (Service Data Object)."""
    node_id: int
    index: int
    sub_index: int
    data: bytes
    is_write: bool = True


@dataclass
class CANopenPDO:
    """Estructura para mensajes PDO (Process Data Object)."""
    cob_id: int  # Communication Object Identifier
    data: bytes
    length: int = 8


class R13CANopenProtocol:
    """
    Clase para manejar el protocolo CANopen específico del Danfoss R13.
    """
    
    def __init__(self, node_id: int = 1):
        """
        Inicializar protocolo CANopen para R13.
        
        Args:
            node_id: ID del nodo R13 en la red CAN (típicamente 1-127)
        """
        self.node_id = node_id
        
    def create_sdo_write(self, index: int, sub_index: int, data: int, data_size: int = 4) -> CANopenSDO:
        """
        Crear mensaje SDO para escribir en el Object Dictionary.
        
        Args:
            index: Índice del objeto (ej: 0x6040)
            sub_index: Sub-índice (típicamente 0)
            data: Datos a escribir
            data_size: Tamaño de los datos (1, 2, 4 bytes)
            
        Returns:
            CANopenSDO: Mensaje SDO listo para enviar
        """
        # Convertir datos a bytes según el tamaño
        if data_size == 1:
            data_bytes = data.to_bytes(1, byteorder='little')
        elif data_size == 2:
            data_bytes = data.to_bytes(2, byteorder='little')
        elif data_size == 4:
            data_bytes = data.to_bytes(4, byteorder='little')
        else:
            raise ValueError("data_size debe ser 1, 2 o 4 bytes")
        
        return CANopenSDO(
            node_id=self.node_id,
            index=index,
            sub_index=sub_index,
            data=data_bytes,
            is_write=True
        )
    
    def create_sdo_read(self, index: int, sub_index: int = 0) -> CANopenSDO:
        """
        Crear mensaje SDO para leer del Object Dictionary.
        
        Args:
            index: Índice del objeto
            sub_index: Sub-índice
            
        Returns:
            CANopenSDO: Mensaje SDO de lectura
        """
        return CANopenSDO(
            node_id=self.node_id,
            index=index,
            sub_index=sub_index,
            data=b'',
            is_write=False
        )
    
    def set_operation_mode(self, mode: OperationModes) -> CANopenSDO:
        """
        Configurar el modo de operación del R13.
        
        Args:
            mode: Modo de operación deseado
            
        Returns:
            CANopenSDO: Mensaje para configurar el modo
        """
        return self.create_sdo_write(
            CANopenObjectDict.MODES_OF_OPERATION, 
            0, 
            mode.value, 
            1  # 1 byte
        )
    
    def send_control_command(self, command: CANopenCommands) -> CANopenSDO:
        """
        Enviar comando de control al R13.
        
        Args:
            command: Comando a enviar
            
        Returns:
            CANopenSDO: Mensaje de control
        """
        return self.create_sdo_write(
            CANopenObjectDict.CONTROL_WORD,
            0,
            command.value,
            2  # 2 bytes
        )
    
    def set_target_velocity(self, velocity: int) -> CANopenSDO:
        """
        Establecer velocidad objetivo.
        
        Args:
            velocity: Velocidad en unidades específicas del R13
            
        Returns:
            CANopenSDO: Mensaje para establecer velocidad
        """
        return self.create_sdo_write(
            CANopenObjectDict.PROFILE_VELOCITY,
            0,
            velocity,
            4  # 4 bytes
        )
    
    def set_target_position(self, position: int) -> CANopenSDO:
        """
        Establecer posición objetivo.
        
        Args:
            position: Posición en unidades específicas del R13
            
        Returns:
            CANopenSDO: Mensaje para establecer posición
        """
        return self.create_sdo_write(
            CANopenObjectDict.TARGET_POSITION,
            0,
            position,
            4  # 4 bytes
        )
    
    def read_status_word(self) -> CANopenSDO:
        """
        Leer el Status Word del R13.
        
        Returns:
            CANopenSDO: Mensaje para leer estado
        """
        return self.create_sdo_read(CANopenObjectDict.STATUS_WORD, 0)
    
    def read_actual_velocity(self) -> CANopenSDO:
        """
        Leer la velocidad actual del R13.
        
        Returns:
            CANopenSDO: Mensaje para leer velocidad actual
        """
        return self.create_sdo_read(CANopenObjectDict.VELOCITY_ACTUAL_VALUE, 0)
    
    def read_actual_position(self) -> CANopenSDO:
        """
        Leer la posición actual del R13.
        
        Returns:
            CANopenSDO: Mensaje para leer posición actual
        """
        return self.create_sdo_read(CANopenObjectDict.POSITION_ACTUAL_VALUE, 0)
    
    def decode_status_word(self, status_value: int) -> Dict[str, bool]:
        """
        Decodificar el Status Word en un diccionario legible.
        
        Args:
            status_value: Valor del Status Word
            
        Returns:
            Dict: Estado decodificado
        """
        return {
            'ready_to_switch_on': bool(status_value & (1 << StatusWordBits.READY_TO_SWITCH_ON)),
            'switched_on': bool(status_value & (1 << StatusWordBits.SWITCHED_ON)),
            'operation_enabled': bool(status_value & (1 << StatusWordBits.OPERATION_ENABLED)),
            'fault': bool(status_value & (1 << StatusWordBits.FAULT)),
            'voltage_enabled': bool(status_value & (1 << StatusWordBits.VOLTAGE_ENABLED)),
            'quick_stop': bool(status_value & (1 << StatusWordBits.QUICK_STOP)),
            'switch_on_disabled': bool(status_value & (1 << StatusWordBits.SWITCH_ON_DISABLED)),
            'warning': bool(status_value & (1 << StatusWordBits.WARNING)),
            'remote': bool(status_value & (1 << StatusWordBits.REMOTE)),
            'target_reached': bool(status_value & (1 << StatusWordBits.TARGET_REACHED)),
        }
    
    @staticmethod
    def get_command_map() -> Dict[str, CANopenCommands]:
        """
        Obtener mapeo de comandos de texto a comandos CANopen.
        
        Returns:
            Dict: Mapeo de strings a comandos CANopen
        """
        return {
            "enable": CANopenCommands.ENABLE_OPERATION,
            "disable": CANopenCommands.DISABLE_OPERATION,
            "stop": CANopenCommands.QUICK_STOP,
            "shutdown": CANopenCommands.SHUTDOWN,
            "reset": CANopenCommands.FAULT_RESET,
            "switch_on": CANopenCommands.SWITCH_ON,
        }
    
    @staticmethod
    def get_operation_modes() -> Dict[str, OperationModes]:
        """
        Obtener mapeo de modos de operación.
        
        Returns:
            Dict: Mapeo de strings a modos
        """
        return {
            "position": OperationModes.PROFILE_POSITION,
            "velocity": OperationModes.PROFILE_VELOCITY,
            "homing": OperationModes.HOMING,
            "torque": OperationModes.PROFILE_TORQUE,
        }
