"""
Módulo de comunicación serie para el dispositivo K13.

Este módulo maneja la comunicación de bajo nivel con el dispositivo K13
a través de puerto serie (USB/RS232).
"""

import serial
import logging
import time
from typing import Optional, bytes
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SerialConfig:
    """Configuración para la comunicación serie."""
    port: str
    baud_rate: int = 9600
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = 'N'  # None, Even, Odd
    timeout: float = 1.0
    

class K13SerialComm:
    """
    Clase para manejar la comunicación serie con K13.
    """
    
    def __init__(self, config: SerialConfig):
        """
        Inicializar comunicación serie.
        
        Args:
            config: Configuración de puerto serie
        """
        self.config = config
        self.serial_port: Optional[serial.Serial] = None
        self.is_open = False
        
    def open(self) -> bool:
        """
        Abrir puerto serie.
        
        Returns:
            bool: True si se abrió exitosamente
        """
        try:
            self.serial_port = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baud_rate,
                bytesize=self.config.data_bits,
                stopbits=self.config.stop_bits,
                parity=self.config.parity,
                timeout=self.config.timeout
            )
            
            if self.serial_port.is_open:
                self.is_open = True
                logger.info(f"Puerto serie {self.config.port} abierto exitosamente")
                return True
            else:
                logger.error(f"No se pudo abrir el puerto {self.config.port}")
                return False
                
        except serial.SerialException as e:
            logger.error(f"Error al abrir puerto serie: {e}")
            return False
    
    def close(self) -> None:
        """Cerrar puerto serie."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.is_open = False
            logger.info("Puerto serie cerrado")
    
    def write_data(self, data: bytes) -> bool:
        """
        Escribir datos al puerto serie.
        
        Args:
            data: Datos a escribir
            
        Returns:
            bool: True si se escribió exitosamente
        """
        if not self.is_open:
            logger.error("Puerto serie no está abierto")
            return False
            
        try:
            bytes_written = self.serial_port.write(data)
            logger.debug(f"Escritos {bytes_written} bytes: {data.hex()}")
            return bytes_written == len(data)
            
        except Exception as e:
            logger.error(f"Error al escribir datos: {e}")
            return False
    
    def read_data(self, size: int = 1) -> Optional[bytes]:
        """
        Leer datos del puerto serie.
        
        Args:
            size: Número de bytes a leer
            
        Returns:
            bytes: Datos leídos o None si hay error
        """
        if not self.is_open:
            logger.error("Puerto serie no está abierto")
            return None
            
        try:
            data = self.serial_port.read(size)
            if data:
                logger.debug(f"Leídos {len(data)} bytes: {data.hex()}")
            return data
            
        except Exception as e:
            logger.error(f"Error al leer datos: {e}")
            return None
    
    def flush_buffers(self) -> None:
        """Limpiar buffers de entrada y salida."""
        if self.is_open:
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            logger.debug("Buffers serie limpiados")
