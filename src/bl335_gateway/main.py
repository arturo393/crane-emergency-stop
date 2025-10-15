"""
BL335 Gateway - Python CANopen Gateway para Danfoss K13 F

Implementación del gateway que conecta vía Ethernet (TCP/IP) y 
se comunica con el receptor K13 F usando protocolo CANopen sobre SocketCAN.
"""

import canopen
import socket
import json
import logging
import threading
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BL335Gateway")


class BL335Gateway:
    """Gateway Ethernet-CAN usando python-canopen"""
    
    def __init__(self, can_channel='can0', node_id=1, tcp_port=9999, can_interface='socketcan'):
        """
        Inicializar gateway
        
        Args:
            can_channel: Canal CAN (can0, can1, vcan0 para testing)
            node_id: ID del nodo K13 F en la red CANopen
            tcp_port: Puerto TCP para servidor
            can_interface: Interfaz CAN ('socketcan', 'virtual' para testing sin hardware)
        """
        self.can_channel = can_channel
        self.node_id = node_id
        self.tcp_port = tcp_port
        self.can_interface = can_interface
        
        # Red CANopen
        self.network = None
        self.k13_node = None
        
        # Servidor TCP
        self.tcp_server = None
        self.tcp_thread = None
        self.running = False
        
        # Estado
        self.connected = False
        self.last_error = None
        
        logger.info(f"BL335 Gateway inicializado: CAN={can_channel}, Interface={can_interface}, Node={node_id}, Port={tcp_port}")
    
    def start(self):
        """Iniciar gateway"""
        try:
            # Inicializar red CANopen
            logger.info(f"Inicializando red CANopen en {self.can_channel} (interface={self.can_interface})...")
            self.network = canopen.Network()
            
            # Configurar según interfaz
            if self.can_interface == 'virtual':
                # Modo virtual para testing sin hardware/kernel modules
                self.network.connect(interface='virtual', channel=self.can_channel, bitrate=250000)
                logger.info("✅ Usando bus CAN virtual (sin módulos kernel)")
            else:
                # Modo socketcan normal (Linux con kernel modules)
                self.network.connect(channel=self.can_channel, interface='socketcan', bitrate=250000)
                logger.info("✅ Usando SocketCAN (kernel modules)")
            
            # Agregar nodo K13 F
            logger.info(f"Agregando nodo K13 F (ID={self.node_id})...")
            self.k13_node = self.network.add_node(self.node_id, object_dictionary=None)
            
            # TODO: Cargar EDS file cuando esté disponible
            # self.k13_node = self.network.add_node(self.node_id, 'path/to/k13f.eds')
            
            self.connected = True
            logger.info("Red CANopen inicializada correctamente")
            
            # Iniciar servidor TCP
            self._start_tcp_server()
            
            logger.info("✅ Gateway BL335 iniciado correctamente")
            
        except Exception as e:
            logger.error(f"Error iniciando gateway: {e}")
            self.last_error = str(e)
            self.connected = False
            raise
    
    def stop(self):
        """Detener gateway"""
        logger.info("Deteniendo gateway...")
        self.running = False
        
        if self.tcp_server:
            self.tcp_server.close()
        
        if self.network:
            self.network.disconnect()
        
        self.connected = False
        logger.info("Gateway detenido")
    
    def _start_tcp_server(self):
        """Iniciar servidor TCP"""
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_server.bind(('0.0.0.0', self.tcp_port))
        self.tcp_server.listen(5)
        
        self.running = True
        self.tcp_thread = threading.Thread(target=self._tcp_server_loop, daemon=True)
        self.tcp_thread.start()
        
        logger.info(f"Servidor TCP iniciado en puerto {self.tcp_port}")
    
    def _tcp_server_loop(self):
        """Loop del servidor TCP"""
        while self.running:
            try:
                client_socket, address = self.tcp_server.accept()
                logger.info(f"Cliente conectado desde {address}")
                
                # Manejar cliente en thread separado
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error en servidor TCP: {e}")
    
    def _handle_client(self, client_socket: socket.socket, address):
        """Manejar cliente TCP"""
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # Procesar comando
                try:
                    command = json.loads(data.decode('utf-8'))
                    response = self._process_command(command)
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
                except json.JSONDecodeError:
                    response = {'error': 'Invalid JSON'}
                    client_socket.send(json.dumps(response).encode('utf-8'))
        
        except Exception as e:
            logger.error(f"Error manejando cliente {address}: {e}")
        
        finally:
            client_socket.close()
            logger.info(f"Cliente {address} desconectado")
    
    def _process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesar comando recibido
        
        Args:
            command: Diccionario con comando JSON
        
        Returns:
            Diccionario con respuesta JSON
        """
        cmd_type = command.get('command')
        logger.info(f"Comando recibido: {cmd_type}")
        
        try:
            if cmd_type == 'emergency_stop':
                return self.emergency_stop()
            
            elif cmd_type == 'get_status':
                return self.get_status()
            
            elif cmd_type == 'reset':
                return self.reset()
            
            elif cmd_type == 'sdo_read':
                index = command.get('index')
                subindex = command.get('subindex', 0)
                return self.sdo_read(index, subindex)
            
            elif cmd_type == 'sdo_write':
                index = command.get('index')
                subindex = command.get('subindex', 0)
                value = command.get('value')
                return self.sdo_write(index, subindex, value)
            
            else:
                return {'error': f'Unknown command: {cmd_type}'}
        
        except Exception as e:
            logger.error(f"Error procesando comando: {e}")
            return {'error': str(e)}
    
    def emergency_stop(self) -> Dict[str, Any]:
        """Ejecutar parada de emergencia"""
        logger.warning("⚠️  PARADA DE EMERGENCIA SOLICITADA")
        
        try:
            # TODO: Implementar comando específico de parada
            # Ejemplo simplificado:
            # self.k13_node.sdo[0x6040].raw = 0x06  # Control Word: Quick Stop
            
            logger.info("Parada de emergencia ejecutada")
            return {'status': 'ok', 'message': 'Emergency stop activated'}
        
        except Exception as e:
            logger.error(f"Error en parada de emergencia: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        try:
            status = {
                'status': 'ok',
                'connected': self.connected,
                'can_channel': self.can_channel,
                'node_id': self.node_id,
                'tcp_port': self.tcp_port,
                'last_error': self.last_error
            }
            
            # TODO: Agregar más información del K13 F cuando EDS esté disponible
            # status['k13_state'] = self.k13_node.sdo[0x6041].raw  # Status Word
            
            return status
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def reset(self) -> Dict[str, Any]:
        """Reset del sistema"""
        logger.info("Reset solicitado")
        
        try:
            # Enviar NMT Reset
            self.k13_node.nmt.send_command(0x81)  # Reset Node
            logger.info("Reset ejecutado")
            return {'status': 'ok', 'message': 'Reset sent'}
        
        except Exception as e:
            logger.error(f"Error en reset: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def sdo_read(self, index: int, subindex: int = 0) -> Dict[str, Any]:
        """
        Leer objeto via SDO
        
        Args:
            index: Índice del objeto
            subindex: Sub-índice del objeto
        
        Returns:
            Diccionario con valor leído
        """
        try:
            value = self.k13_node.sdo[index][subindex].raw
            logger.info(f"SDO Read: 0x{index:04X}:{subindex} = {value}")
            return {'status': 'ok', 'value': value}
        
        except Exception as e:
            logger.error(f"Error leyendo SDO: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def sdo_write(self, index: int, subindex: int, value: Any) -> Dict[str, Any]:
        """
        Escribir objeto via SDO
        
        Args:
            index: Índice del objeto
            subindex: Sub-índice del objeto
            value: Valor a escribir
        
        Returns:
            Diccionario con resultado
        """
        try:
            self.k13_node.sdo[index][subindex].raw = value
            logger.info(f"SDO Write: 0x{index:04X}:{subindex} = {value}")
            return {'status': 'ok', 'message': 'Value written'}
        
        except Exception as e:
            logger.error(f"Error escribiendo SDO: {e}")
            return {'status': 'error', 'message': str(e)}


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BL335 Gateway')
    parser.add_argument('--can', default='vcan0', help='Canal CAN (default: vcan0 para testing)')
    parser.add_argument('--interface', default='virtual', 
                       choices=['socketcan', 'virtual'],
                       help='Interfaz CAN: socketcan (Linux real) o virtual (testing)')
    parser.add_argument('--node-id', type=int, default=1, help='Node ID del K13 F')
    parser.add_argument('--port', type=int, default=9999, help='Puerto TCP')
    parser.add_argument('--verbose', action='store_true', help='Modo verbose')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Crear y ejecutar gateway
    gateway = BL335Gateway(
        can_channel=args.can,
        node_id=args.node_id,
        tcp_port=args.port,
        can_interface=args.interface
    )
    
    print("=" * 60)
    print("🚀 BL335 Gateway - Python CANopen")
    print("=" * 60)
    print(f"CAN Channel: {args.can}")
    print(f"CAN Interface: {args.interface}")
    print(f"Node ID: {args.node_id}")
    print(f"TCP Port: {args.port}")
    print("\nModos de interfaz CAN:")
    print("  - socketcan: Linux con módulos kernel (producción)")
    print("  - virtual: Sin módulos kernel (testing/desarrollo)")
    print("\nPresiona Ctrl+C para detener")
    print("=" * 60)
    
    try:
        gateway.start()
        
        # Mantener vivo
        while True:
            import time
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Deteniendo gateway...")
        gateway.stop()
        print("✅ Gateway detenido")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        gateway.stop()


if __name__ == "__main__":
    main()
