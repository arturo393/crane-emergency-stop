"""
Módulo principal para el controlador del receptor Danfoss R13 de puente grúa.

Este módulo contiene la clase principal R13Controller que maneja
la comunicación de red y el control del dispositivo.
"""

import sys
import os
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Agregar el directorio src al path si no estamos importando como módulo
if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from .network_comm import K13NetworkComm, NetworkConfig
    from .protocol import R13CANopenProtocol, CANopenCommands, OperationModes, CANopenObjectDict
except ImportError:
    # Si las importaciones relativas fallan, usar importaciones absolutas
    from k13_controller.network_comm import K13NetworkComm, NetworkConfig
    from k13_controller.protocol import R13CANopenProtocol, CANopenCommands, OperationModes, CANopenObjectDict


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class R13Config:
    """Configuración para el dispositivo Danfoss R13."""
    host: str = "192.168.1.100"  # IP del gateway Ethernet-a-CAN
    port: int = 9999             # Puerto del gateway
    timeout: float = 5.0
    retry_attempts: int = 3


@dataclass
class CraneCommand:
    """Estructura para comandos del puente grúa."""
    action: str  # 'move_up', 'move_down', 'stop', etc.
    speed: int = 50  # Velocidad 0-100
    duration: float = 1.0  # Duración en segundos


class R13Controller:
    """
    Controlador principal para el dispositivo Danfoss R13 de puente grúa.
    
    Esta clase maneja la comunicación de red con un gateway
    que traduce los comandos a CAN bus para el R13.
    """
    
    def __init__(self, config: R13Config = None):
        """
        Inicializar el controlador R13.
        
        Args:
            config: Configuración de red para el gateway
        """
        self.config = config or R13Config()
        network_cfg = NetworkConfig(host=self.config.host, port=self.config.port, timeout=self.config.timeout)
        self.connection = K13NetworkComm(network_cfg)
        
        # Inicializar protocolo CANopen
        self.protocol = R13CANopenProtocol(node_id=1)  # Asumir node_id=1 para el R13
        
        logger.info(f"Inicializando R13Controller para gateway en: {self.config.host}:{self.config.port}")
        
    @property
    def is_connected(self) -> bool:
        """Retorna el estado de la conexión."""
        return self.connection.is_connected

    def connect(self) -> bool:
        """
        Establecer conexión con el gateway de red.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        logger.info(f"Estableciendo conexión con el gateway en {self.config.host}:{self.config.port}...")
        return self.connection.connect()
    
    def disconnect(self) -> None:
        """Desconectar del gateway de red."""
        if self.is_connected:
            logger.info("Desconectando del gateway...")
            self.connection.disconnect()
    
    def send_command(self, command: CraneCommand) -> bool:
        """
        Enviar comando al puente grúa a través del gateway.
        
        Args:
            command: Comando a enviar
            
        Returns:
            bool: True si el comando fue enviado exitosamente
        """
        if not self.is_connected:
            logger.error("No hay conexión con el gateway")
            return False
            
        try:
            logger.info(f"Enviando comando: {command.action} (velocidad: {command.speed})")
            
            # Traducir comando de alto nivel a comando CANopen
            command_map = self.protocol.get_command_map()
            canopen_command = command_map.get(command.action)
            
            if canopen_command is None:
                logger.error(f"Comando desconocido: {command.action}")
                return False

            # Crear mensaje SDO según el comando
            if command.action in ["move_up", "move_down"]:
                # Para movimiento, primero configurar velocidad, luego habilitar
                velocity_msg = self.protocol.set_target_velocity(command.speed * 10)  # Escalar velocidad
                enable_msg = self.protocol.send_control_command(CANopenCommands.ENABLE_OPERATION)
                
                # Enviar configuración de velocidad (simulado como mensaje de red)
                success = self._send_canopen_message(velocity_msg)
                if success:
                    success = self._send_canopen_message(enable_msg)
            else:
                # Para otros comandos, enviar directamente
                control_msg = self.protocol.send_control_command(canopen_command)
                success = self._send_canopen_message(control_msg)
            
            if success:
                logger.info("Comando enviado exitosamente al gateway")
            else:
                logger.error("Fallo al enviar comando al gateway")

            return success
            
        except Exception as e:
            logger.error(f"Error al enviar comando: {e}")
            return False
    
    def emergency_stop(self) -> bool:
        """
        Detener emergencia del puente grúa.
        
        Returns:
            bool: True si la parada de emergencia fue exitosa
        """
        logger.warning("PARADA DE EMERGENCIA activada")
        stop_command = CraneCommand(action="emergency_stop", speed=0)
        return self.send_command(stop_command)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtener estado actual del controlador.
        
        Returns:
            Dict con información del estado
        """
        return {
            "connected": self.is_connected,
            "gateway_host": self.config.host,
            "gateway_port": self.config.port,
            "timestamp": time.time()
        }
    
    def _send_canopen_message(self, sdo_message) -> bool:
        """
        Enviar mensaje CANopen a través del gateway de red.
        
        Args:
            sdo_message: Mensaje SDO a enviar
            
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # Convertir mensaje SDO a formato de red (JSON, por ejemplo)
            # Este formato dependerá de cómo implemente el gateway
            import json
            
            message_dict = {
                "type": "sdo_write" if sdo_message.is_write else "sdo_read",
                "node_id": sdo_message.node_id,
                "index": hex(sdo_message.index),
                "sub_index": sdo_message.sub_index,
                "data": sdo_message.data.hex() if sdo_message.data else ""
            }
            
            # Convertir a JSON y luego a bytes
            json_data = json.dumps(message_dict).encode('utf-8')
            
            # Enviar por red
            return self.connection.write_data(json_data)
            
        except Exception as e:
            logger.error(f"Error al enviar mensaje CANopen: {e}")
            return False
    
    async def read_device_status(self) -> Optional[Dict[str, Any]]:
        """
        Leer el estado del dispositivo R13.
        
        Returns:
            Dict con el estado decodificado o None si hay error
        """
        if not self.is_connected:
            return None
            
        try:
            # Crear mensaje para leer Status Word
            status_msg = self.protocol.read_status_word()
            
            # Enviar solicitud de lectura
            success = self._send_canopen_message(status_msg)
            
            if success:
                # En una implementación real, esperaríamos la respuesta
                # Por ahora, simulamos una respuesta
                # response = self.connection.read_data()
                # status_value = int.from_bytes(response, byteorder='little')
                
                # Simulación para testing
                status_value = 0x0237  # Ejemplo: operación habilitada
                
                decoded_status = self.protocol.decode_status_word(status_value)
                return {
                    "raw_status": status_value,
                    "decoded": decoded_status,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            logger.error(f"Error al leer estado del dispositivo: {e}")
            
        return None


def main():
    """Función principal de prueba."""
    print("=== Danfoss R13 Puente Grúa Controller ===")
    
    # Crear configuración para el gateway
    config = R13Config(
        host="127.0.0.1",  # Usar localhost para simulación
        port=9999
    )
    
    # Crear controlador
    controller = R13Controller(config)
    
    # TODO: Iniciar un servidor TCP de simulación en un hilo separado para testing
    
    try:
        # Conectar (esto fallará si no hay un servidor escuchando)
        if controller.connect():
            print("Conexión establecida con el gateway")
            
            # Obtener estado
            status = controller.get_status()
            print(f"Estado: {status}")
            
            # Enviar comandos de prueba
            commands = [
                CraneCommand("move_up", speed=30, duration=2.0),
                CraneCommand("stop", speed=0, duration=0.5),
                CraneCommand("move_down", speed=20, duration=2.0),
                CraneCommand("stop", speed=0)
            ]
            
            for cmd in commands:
                if controller.send_command(cmd):
                    print(f"Comando {cmd.action} enviado")
                    time.sleep(cmd.duration)
                else:
                    print(f"Error en comando {cmd.action}")
                    break
                    
        else:
            print("Error: No se pudo conectar con el gateway. (¿Está el simulador o dispositivo en línea?)")
            
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
        if controller.is_connected:
            controller.emergency_stop()
        
    finally:
        controller.disconnect()
        print("Programa terminado")


if __name__ == "__main__":
    main()
