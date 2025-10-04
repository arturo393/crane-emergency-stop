# Raspberry Pi CAN HAT Driver para Danfoss R13
# Compatible con Waveshare RS485 CAN HAT y PiCAN2

import can
import time
import logging
from typing import Optional, Dict, Any

class RaspberryPiCANGateway:
    """
    Driver para comunicación CANopen con Danfoss R13 usando Raspberry Pi + CAN HAT
    """
    
    def __init__(self, interface: str = 'can0', bitrate: int = 250000):
        """
        Inicializar gateway CAN en Raspberry Pi
        
        Args:
            interface: Interface CAN (can0, can1)
            bitrate: Velocidad del bus CAN en bps
        """
        self.interface = interface
        self.bitrate = bitrate
        self.bus: Optional[can.Bus] = None
        self.is_connected = False
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """
        Establecer conexión con el bus CAN
        
        Returns:
            bool: True si conexión exitosa
        """
        try:
            # Configurar interface CAN si no está activo
            import os
            os.system(f'sudo ip link set {self.interface} up type can bitrate {self.bitrate}')
            
            # Crear bus CAN
            self.bus = can.interface.Bus(
                channel=self.interface,
                bustype='socketcan'
            )
            
            self.is_connected = True
            self.logger.info(f"Conectado a {self.interface} @ {self.bitrate} bps")
            return True
            
        except Exception as e:
            self.logger.error(f"Error conectando CAN: {e}")
            return False
    
    def disconnect(self):
        """Desconectar del bus CAN"""
        if self.bus:
            self.bus.shutdown()
            self.is_connected = False
            self.logger.info("Desconectado del bus CAN")
    
    def send_nmt_command(self, node_id: int, command: int) -> bool:
        """
        Enviar comando NMT (Network Management)
        
        Args:
            node_id: ID del nodo Danfoss R13 (típicamente 1)
            command: Comando NMT (1=Start, 2=Stop, 128=Reset)
            
        Returns:
            bool: True si envío exitoso
        """
        if not self.is_connected:
            self.logger.error("No conectado al bus CAN")
            return False
        
        try:
            # NMT Master usa COB-ID 0x000
            msg = can.Message(
                arbitration_id=0x000,
                data=[command, node_id],
                is_extended_id=False
            )
            
            self.bus.send(msg)
            self.logger.info(f"NMT enviado: CMD={command}, Node={node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enviando NMT: {e}")
            return False
    
    def emergency_stop(self, node_id: int = 1) -> bool:
        """
        Comando de parada de emergencia para puente grúa
        
        Args:
            node_id: ID del receptor Danfoss R13
            
        Returns:
            bool: True si comando enviado exitosamente
        """
        self.logger.warning(f"🚨 PARADA DE EMERGENCIA - Nodo {node_id}")
        
        # Enviar comando NMT Stop
        if self.send_nmt_command(node_id, 0x02):
            # Confirmar con PDO de control
            return self.send_pdo_stop(node_id)
        return False
    
    def send_pdo_stop(self, node_id: int) -> bool:
        """
        Enviar PDO para detener todos los movimientos
        
        Args:
            node_id: ID del nodo
            
        Returns:
            bool: True si enviado exitosamente
        """
        try:
            # RPDO1 - Control Word (detener movimientos)
            pdo_id = 0x200 + node_id  # RPDO1 por defecto
            control_data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            
            msg = can.Message(
                arbitration_id=pdo_id,
                data=control_data,
                is_extended_id=False
            )
            
            self.bus.send(msg)
            self.logger.info(f"PDO Stop enviado a nodo {node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enviando PDO: {e}")
            return False
    
    def read_status(self, node_id: int, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Leer estado del receptor Danfoss R13
        
        Args:
            node_id: ID del nodo
            timeout: Timeout en segundos
            
        Returns:
            Dict con información de estado o None
        """
        if not self.is_connected:
            return None
        
        try:
            # Escuchar mensajes por timeout especificado
            msg = self.bus.recv(timeout=timeout)
            
            if msg:
                return {
                    'timestamp': time.time(),
                    'can_id': f"0x{msg.arbitration_id:03X}",
                    'data': msg.data.hex(),
                    'length': msg.dlc
                }
                
        except Exception as e:
            self.logger.debug(f"No hay mensajes disponibles: {e}")
            
        return None
    
    def monitor_bus(self, duration: float = 10.0):
        """
        Monitorear actividad del bus CAN
        
        Args:
            duration: Duración del monitoreo en segundos
        """
        if not self.is_connected:
            self.logger.error("No conectado al bus CAN")
            return
        
        self.logger.info(f"Monitoreando bus CAN por {duration} segundos...")
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            msg = self.bus.recv(timeout=0.1)
            if msg:
                print(f"RX: ID=0x{msg.arbitration_id:03X} Data={msg.data.hex().upper()}")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Ejemplo de uso
if __name__ == "__main__":
    # Usar como context manager
    with RaspberryPiCANGateway() as gateway:
        if gateway.is_connected:
            print("✅ Conectado al bus CAN")
            
            # Monitorear bus por 5 segundos
            gateway.monitor_bus(5.0)
            
            # Comando de parada de emergencia
            gateway.emergency_stop(node_id=1)
            
            # Leer respuesta
            status = gateway.read_status(node_id=1, timeout=2.0)
            if status:
                print(f"Estado recibido: {status}")
        else:
            print("❌ Error conectando al bus CAN")