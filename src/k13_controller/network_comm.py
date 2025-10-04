"""
Módulo de comunicación de red para el dispositivo Danfoss R13.

Este módulo maneja la comunicación de bajo nivel con el receptor R13
a través de una conexión de red (TCP/IP).
"""

import socket
import logging
import time
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NetworkConfig:
    """Configuración para la comunicación de red."""
    host: str
    port: int
    timeout: float = 5.0
    

class K13NetworkComm:
    """
    Clase para manejar la comunicación de red con el R13.
    """
    
    def __init__(self, config: NetworkConfig):
        """
        Inicializar comunicación de red.
        
        Args:
            config: Configuración de red (host, port)
        """
        self.config = config
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """
        Establecer conexión TCP con el dispositivo.
        
        Returns:
            bool: True si se conectó exitosamente
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.config.timeout)
            self.socket.connect((self.config.host, self.config.port))
            
            self.is_connected = True
            logger.info(f"Conexión TCP establecida con {self.config.host}:{self.config.port}")
            return True
                
        except (socket.timeout, socket.error) as e:
            logger.error(f"Error al conectar vía TCP: {e}")
            self.socket = None
            self.is_connected = False
            return False
    
    def disconnect(self) -> None:
        """Cerrar la conexión de red."""
        if self.socket:
            self.socket.close()
            self.socket = None
            self.is_connected = False
            logger.info("Conexión de red cerrada")
    
    def write_data(self, data: bytes) -> bool:
        """
        Escribir datos al socket de red.
        
        Args:
            data: Datos a escribir
            
        Returns:
            bool: True si se escribió exitosamente
        """
        if not self.is_connected or not self.socket:
            logger.error("No hay conexión de red para escribir datos")
            return False
            
        try:
            self.socket.sendall(data)
            logger.debug(f"Enviados {len(data)} bytes: {data.hex()}")
            return True
            
        except socket.error as e:
            logger.error(f"Error al enviar datos por red: {e}")
            return False
    
    def read_data(self, size: int = 1024) -> Optional[bytes]:
        """
        Leer datos del socket de red.
        
        Args:
            size: Número máximo de bytes a leer
            
        Returns:
            bytes: Datos leídos o None si hay error
        """
        if not self.is_connected or not self.socket:
            logger.error("No hay conexión de red para leer datos")
            return None
            
        try:
            data = self.socket.recv(size)
            if data:
                logger.debug(f"Leídos {len(data)} bytes: {data.hex()}")
            return data
            
        except socket.timeout:
            logger.warning("Timeout esperando datos de la red")
            return None
        except socket.error as e:
            logger.error(f"Error al leer datos de la red: {e}")
            return None
