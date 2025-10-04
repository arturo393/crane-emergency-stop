#!/usr/bin/env python3
"""
Gateway CANopen para Raspberry Pi
Implementación de ejemplo para conectar Ethernet con CAN bus

Este script debe ejecutarse en una Raspberry Pi con un módulo CAN
para actuar como gateway entre la red Ethernet y el bus CAN donde
está conectado el receptor Danfoss R13.
"""

import asyncio
import json
import logging
import socket
from typing import Dict, Any, Optional

try:
    import canopen
    import can
except ImportError:
    print("Error: Instalar dependencias CAN con 'pip install canopen python-can'")
    exit(1)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CanOpenGateway:
    """Gateway entre Ethernet y CAN bus para control del R13."""
    
    def __init__(self, can_interface: str = 'can0', can_bitrate: int = 250000, 
                 tcp_port: int = 9999, r13_node_id: int = 1):
        """
        Inicializar el gateway.
        
        Args:
            can_interface: Interfaz CAN (ej: 'can0')
            can_bitrate: Velocidad del bus CAN en bits/segundo
            tcp_port: Puerto TCP para escuchar conexiones Ethernet
            r13_node_id: ID del nodo R13 en la red CAN
        """
        self.can_interface = can_interface
        self.can_bitrate = can_bitrate
        self.tcp_port = tcp_port
        self.r13_node_id = r13_node_id
        
        # Componentes CANopen
        self.network = None
        self.r13_node = None
        
        # Servidor TCP
        self.server_socket = None
        self.client_connections = []
        
        # Estado
        self.running = False
    
    async def initialize_can_network(self):
        """Inicializar la red CANopen."""
        try:
            logger.info(f"Inicializando red CAN en {self.can_interface} a {self.can_bitrate} bps")
            
            # Crear la red CANopen
            self.network = canopen.Network()
            
            # Conectar al bus CAN físico
            # Nota: En Raspberry Pi, primero configurar la interfaz con:
            # sudo ip link set can0 up type can bitrate 250000
            self.network.connect(channel=self.can_interface, bustype='socketcan')
            
            # Crear nodo para el R13 (necesita archivo EDS)
            # IMPORTANTE: Obtener el archivo EDS real de Danfoss
            # Por ahora, usar configuración básica
            self.r13_node = self.network.add_node(self.r13_node_id, 'r13_basic.eds')
            
            # Configurar el R13 en modo operacional
            self.r13_node.nmt.state = 'OPERATIONAL'
            
            logger.info("Red CAN inicializada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando red CAN: {e}")
            return False
    
    async def start_tcp_server(self):
        """Iniciar servidor TCP para recibir comandos."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.tcp_port))
            self.server_socket.listen(5)
            self.server_socket.setblocking(False)
            
            logger.info(f"Servidor TCP iniciado en puerto {self.tcp_port}")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando servidor TCP: {e}")
            return False
    
    async def handle_client_connection(self, client_socket, address):
        """Manejar conexión de cliente TCP."""
        logger.info(f"Cliente conectado desde {address}")
        
        try:
            while self.running:
                # Recibir datos del cliente
                data = await asyncio.get_event_loop().sock_recv(client_socket, 1024)
                
                if not data:
                    break
                
                # Procesar comando JSON
                try:
                    command = json.loads(data.decode('utf-8'))
                    response = await self.process_canopen_command(command)
                    
                    # Enviar respuesta
                    response_json = json.dumps(response).encode('utf-8')
                    await asyncio.get_event_loop().sock_sendall(client_socket, response_json)
                    
                except json.JSONDecodeError:
                    error_response = {"error": "Invalid JSON format"}
                    await asyncio.get_event_loop().sock_sendall(
                        client_socket, 
                        json.dumps(error_response).encode('utf-8')
                    )
                
        except Exception as e:
            logger.error(f"Error en conexión de cliente: {e}")
            
        finally:
            client_socket.close()
            logger.info(f"Cliente {address} desconectado")
    
    async def process_canopen_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesar comando CANopen recibido por TCP.
        
        Args:
            command: Comando en formato JSON
            
        Returns:
            Dict: Respuesta del comando
        """
        try:
            cmd_type = command.get('type')
            node_id = command.get('node_id', self.r13_node_id)
            index = command.get('index')
            sub_index = command.get('sub_index', 0)
            data = command.get('data', '')
            
            if cmd_type == 'sdo_write':
                # Escribir en el Object Dictionary
                index_int = int(index, 16) if isinstance(index, str) else index
                data_bytes = bytes.fromhex(data) if data else b''
                
                # Convertir bytes a valor según el tamaño
                if len(data_bytes) == 1:
                    value = int.from_bytes(data_bytes, byteorder='little')
                elif len(data_bytes) == 2:
                    value = int.from_bytes(data_bytes, byteorder='little')
                elif len(data_bytes) == 4:
                    value = int.from_bytes(data_bytes, byteorder='little')
                else:
                    value = data_bytes
                
                # Escribir usando CANopen
                self.r13_node.sdo[index_int][sub_index].raw = value
                
                logger.info(f"SDO Write: {index}[{sub_index}] = {value}")
                return {"status": "success", "operation": "sdo_write"}
                
            elif cmd_type == 'sdo_read':
                # Leer del Object Dictionary
                index_int = int(index, 16) if isinstance(index, str) else index
                
                value = self.r13_node.sdo[index_int][sub_index].raw
                
                logger.info(f"SDO Read: {index}[{sub_index}] = {value}")
                return {
                    "status": "success", 
                    "operation": "sdo_read",
                    "value": value,
                    "hex_value": hex(value) if isinstance(value, int) else str(value)
                }
            
            else:
                return {"status": "error", "message": f"Unknown command type: {cmd_type}"}
                
        except Exception as e:
            logger.error(f"Error procesando comando CANopen: {e}")
            return {"status": "error", "message": str(e)}
    
    async def run_server_loop(self):
        """Loop principal del servidor."""
        while self.running:
            try:
                # Aceptar nueva conexión
                client_socket, address = await asyncio.get_event_loop().sock_accept(self.server_socket)
                
                # Crear task para manejar cliente
                asyncio.create_task(self.handle_client_connection(client_socket, address))
                
            except Exception as e:
                if self.running:  # Solo log si no estamos cerrando
                    logger.error(f"Error en loop del servidor: {e}")
                await asyncio.sleep(0.1)
    
    async def start(self):
        """Iniciar el gateway."""
        logger.info("Iniciando CANopen Gateway...")
        
        # Inicializar CAN
        if not await self.initialize_can_network():
            return False
        
        # Inicializar servidor TCP
        if not await self.start_tcp_server():
            return False
        
        self.running = True
        
        # Iniciar loop del servidor
        await self.run_server_loop()
        
        return True
    
    async def stop(self):
        """Detener el gateway."""
        logger.info("Deteniendo CANopen Gateway...")
        
        self.running = False
        
        # Cerrar conexiones
        if self.server_socket:
            self.server_socket.close()
        
        # Desconectar red CAN
        if self.network:
            self.network.disconnect()
        
        logger.info("Gateway detenido")


async def main():
    """Función principal."""
    # Configuración del gateway
    gateway = CanOpenGateway(
        can_interface='can0',      # Interfaz CAN en Raspberry Pi
        can_bitrate=250000,        # 250 kbps (verificar con configuración R13)
        tcp_port=9999,             # Puerto TCP
        r13_node_id=1              # Node ID del R13
    )
    
    try:
        await gateway.start()
    except KeyboardInterrupt:
        logger.info("Interrumpido por usuario")
    finally:
        await gateway.stop()


if __name__ == "__main__":
    print("=== CANopen Gateway para Danfoss R13 ===")
    print("Configurar primero la interfaz CAN:")
    print("sudo modprobe can")
    print("sudo modprobe can_raw")
    print("sudo ip link set can0 up type can bitrate 250000")
    print()
    
    # Verificar si estamos en Raspberry Pi
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read()
            if 'Raspberry Pi' not in model:
                print("ADVERTENCIA: Este script está optimizado para Raspberry Pi")
    except:
        print("ADVERTENCIA: No se pudo verificar el modelo del dispositivo")
    
    print("Iniciando gateway...")
    asyncio.run(main())
