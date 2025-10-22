"""
BL335 Gateway - Python CANopen Gateway para Danfoss R13 F

Implementación del gateway que conecta vía Ethernet (TCP/IP) y 
se comunica con el receptor R13 F usando protocolo CANopen sobre SocketCAN.
"""

import canopen
import can  # Fallback para envío CAN en crudo cuando no hay EDS/PDOs
import socket
import json
import logging
import threading
import time
import os
from typing import Dict, Any, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BL335Gateway")


class BL335Gateway:
    """Gateway Ethernet-CAN usando python-canopen"""
    
    def __init__(self, can_channel='can0', node_id=1, tcp_port=9999, can_interface='socketcan'):
        """
        Inicializar gateway
        
        Args:
            can_channel: Canal CAN (can0, can1, vcan0 para testing)
            node_id: ID del nodo R13 F en la red CANopen
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
        
        # Estado del sistema
        self.system_state = {
            'operational': False,
            'nmt_state': 'unknown',
            'pdo_active': False,
            'heartbeat_active': False,
            'last_heartbeat': None
        }
        
        # Estado de conexión
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
            
            # Agregar nodo R13 F con EDS
            logger.info(f"Agregando nodo R13 F (ID={self.node_id})...")
            
            # Cargar EDS file completo (CiA 301/402)
            eds_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'danfoss_r13f_complete.eds')
            if os.path.exists(eds_path):
                logger.info(f"Cargando EDS desde: {eds_path}")
                self.k13_node = self.network.add_node(self.node_id, eds_path)
                logger.info("✅ EDS completo cargado correctamente (CiA 301/402)")
                
                # Configurar PDO directamente desde el EDS sin intentar leer del dispositivo
                # (el simulador puede no tener todos los objetos SDO implementados)
                try:
                    if hasattr(self.k13_node, 'pdo'):
                        logger.info("Configurando PDO desde EDS (sin leer del dispositivo)...")
                        
                        # Asignar COB-IDs directamente sin intentar leer del dispositivo
                        if 1 in self.k13_node.pdo.tx or hasattr(self.k13_node.pdo, 'tx'):
                            if 1 not in self.k13_node.pdo.tx:
                                # Crear el PDO si no existe
                                self.k13_node.pdo.tx[1] = type('obj', (object,), {
                                    'cob_id': None,
                                    'enabled': False,
                                    'transmission_type': 255,
                                    'mapping': [],
                                    'data': bytes()
                                })()
                            
                            self.k13_node.pdo.tx[1].cob_id = 0x180 + self.node_id
                            self.k13_node.pdo.tx[1].enabled = True
                            logger.info(f"✅ TPDO1 COB-ID asignado: 0x{0x180 + self.node_id:03X}")
                        
                        if 1 in self.k13_node.pdo.rx or hasattr(self.k13_node.pdo, 'rx'):
                            if 1 not in self.k13_node.pdo.rx:
                                # Crear el PDO si no existe
                                self.k13_node.pdo.rx[1] = type('obj', (object,), {
                                    'cob_id': None,
                                    'enabled': False,
                                    'transmission_type': 255,
                                    'mapping': []
                                })()
                            
                            self.k13_node.pdo.rx[1].cob_id = 0x200 + self.node_id
                            self.k13_node.pdo.rx[1].enabled = True
                            logger.info(f"✅ RPDO1 COB-ID asignado: 0x{0x200 + self.node_id:03X}")
                        
                        logger.info("✅ PDO configurados desde EDS (sin comunicación con dispositivo)")
                except Exception as pdo_error:
                    logger.warning(f"Error configurando PDO desde EDS: {pdo_error}")
            else:
                logger.warning(f"⚠️  EDS no encontrado en {eds_path}, usando Object Dictionary vacío")
                self.k13_node = self.network.add_node(self.node_id, object_dictionary=None)
            
            self.connected = True
            logger.info("Red CANopen inicializada correctamente")
            
            # Configurar NMT y PDO
            self._configure_nmt_pdo()
            
            # Iniciar servidor TCP
            self._start_tcp_server()
            
            logger.info("✅ Gateway BL335 iniciado correctamente")
        
        except Exception as e:
            logger.error(f"Error iniciando gateway: {e}")
            self.last_error = str(e)
            self.connected = False
            raise
    
    def _configure_nmt_pdo(self):
        """Configurar NMT (Network Management) y PDO (Process Data Objects)"""
        try:
            logger.info("Configurando NMT y PDO...")

            # Configurar NMT State Machine (flujo completo)
            if hasattr(self.k13_node, 'nmt'):
                # Reset Communication
                self.k13_node.nmt.state = 'RESET COMMUNICATION'
                time.sleep(0.1)

                # Reset Application
                self.k13_node.nmt.state = 'RESET APPLICATION'
                time.sleep(0.1)

                # Ir a PRE-OPERATIONAL
                self.k13_node.nmt.state = 'PRE-OPERATIONAL'
                time.sleep(0.1)

                # Finalmente OPERATIONAL
                self.k13_node.nmt.state = 'OPERATIONAL'
                self.system_state['operational'] = True
                self.system_state['nmt_state'] = 'OPERATIONAL'
                logger.info("NMT configurado: OPERATIONAL")
            
            # Configurar PDO completo
            self._configure_pdo_mappings()
            
            logger.info("NMT y PDO configurados correctamente")
            
        except Exception as e:
            logger.error(f"Error configurando NMT/PDO: {e}")
            self.system_state['operational'] = False
    
    def _configure_pdo_mappings(self):
        """Configurar mapeos de PDO (Process Data Objects)"""
        try:
            logger.info("Configurando mapeos PDO...")
            
            if not hasattr(self.k13_node, 'pdo'):
                logger.warning("Nodo no tiene soporte PDO")
                return
            
            # Verificar si los PDOs ya están configurados desde el EDS
            try:
                if 1 in self.k13_node.pdo.rx and self.k13_node.pdo.rx[1].cob_id:
                    logger.info("✅ PDOs ya configurados desde EDS, omitiendo configuración manual")
                    # Asegurar que COB-IDs estén correctamente asignados incluso si vienen del EDS
                    if 1 in self.k13_node.pdo.tx and self.k13_node.pdo.tx[1].cob_id is None:
                        self.k13_node.pdo.tx[1].cob_id = 0x180 + self.node_id
                        logger.info(f"✅ TPDO1 COB-ID re-asignado: 0x{0x180 + self.node_id:03X}")
                    if 1 in self.k13_node.pdo.rx and self.k13_node.pdo.rx[1].cob_id is None:
                        self.k13_node.pdo.rx[1].cob_id = 0x200 + self.node_id
                        logger.info(f"✅ RPDO1 COB-ID re-asignado: 0x{0x200 + self.node_id:03X}")
                    self.system_state['pdo_active'] = True
                    return
            except:
                pass
            
            # Configurar manualmente solo si no están en el EDS
            logger.info("PDOs no configurados en EDS, configurando manualmente...")
            
            # Configurar RPDO1 (Receive PDO 1) - Para comandos de control
            # RPDO1 Parameter (0x1400)
            # Configurar COB-ID para RPDO1 (0x200 + node_id)
            rpdo1_cob_id = 0x200 + self.node_id
            self.k13_node.pdo.rx[1].cob_id = rpdo1_cob_id
            self.k13_node.pdo.rx[1].enabled = True
            
            # Configurar Transmission Type (255 = asynchronous)
            self.k13_node.pdo.rx[1].transmission_type = 255
            
            # Configurar mapping de RPDO1 (0x1600)
            # Map Control Word (0x6040:00) - 16 bits
            self.k13_node.pdo.rx[1].mapping = [
                (0x6040, 0, 16),  # Control Word
            ]
            logger.info(f"RPDO1 configurado: COB-ID=0x{rpdo1_cob_id:03X}")
            
            # Configurar TPDO1 (Transmit PDO 1) - Para estado del dispositivo
            # Configurar COB-ID para TPDO1 (0x180 + node_id)
            tpdo1_cob_id = 0x180 + self.node_id
            self.k13_node.pdo.tx[1].cob_id = tpdo1_cob_id
            self.k13_node.pdo.tx[1].enabled = True
            
            # Configurar Transmission Type (255 = asynchronous)
            self.k13_node.pdo.tx[1].transmission_type = 255
            
            # Configurar mapping de TPDO1 (0x1A00)
            # Map Status Word (0x6041:00) - 16 bits
            self.k13_node.pdo.tx[1].mapping = [
                (0x6041, 0, 16),  # Status Word
            ]
            logger.info(f"TPDO1 configurado: COB-ID=0x{tpdo1_cob_id:03X}")
            
            # Configurar TPDO2 para datos adicionales (opcional)
            tpdo2_cob_id = 0x280 + self.node_id
            self.k13_node.pdo.tx[2].cob_id = tpdo2_cob_id
            self.k13_node.pdo.tx[2].enabled = True
            self.k13_node.pdo.tx[2].transmission_type = 255
            
            # Map Position Actual Value (0x6064:00) - 32 bits
            self.k13_node.pdo.tx[2].mapping = [
                (0x6064, 0, 32),  # Position Actual Value
            ]
            logger.info(f"TPDO2 configurado: COB-ID=0x{tpdo2_cob_id:03X}")
            
            self.system_state['pdo_active'] = True
            logger.info("Mapeos PDO configurados correctamente")
            
        except Exception as e:
            logger.error(f"Error configurando PDO mappings: {e}")
            self.system_state['pdo_active'] = False
    
    def _configure_heartbeat(self):
        """Configurar heartbeat producer/consumer"""
        try:
            logger.info("Configurando heartbeat...")
            
            # Configurar heartbeat producer (este nodo produce heartbeat)
            if hasattr(self.k13_node, 'nmt'):
                # Producer Heartbeat Time (0x1017) - 1000ms
                self.k13_node.sdo[0x1017].raw = 1000
                logger.info("Heartbeat producer configurado: 1000ms")
            
            # Configurar heartbeat consumer (monitorea otros nodos)
            # Consumer Heartbeat Time (0x1016)
            # Formato: Bit 15-16: Consumer number, Bit 0-15: Heartbeat time
            # Para nodo 1: 0x00010000 | 1000 = 0x000103E8
            heartbeat_config = (1 << 16) | 1000  # Consumer 1, 1000ms timeout
            self.k13_node.sdo[0x1016][1].raw = heartbeat_config
            logger.info("Heartbeat consumer configurado para nodo 1: 1000ms")
            
            self.system_state['heartbeat_active'] = True
            self.system_state['last_heartbeat'] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error configurando heartbeat: {e}")
            self.system_state['heartbeat_active'] = False
    
    def _configure_sync(self):
        """Configurar SYNC producer (opcional)"""
        try:
            logger.info("Configurando SYNC producer...")
            
            # Communication Cycle Period (0x1006) - 10ms
            self.k13_node.sdo[0x1006].raw = 10000  # microseconds
            
            # Synchronous Window Length (0x1007) - 5ms
            self.k13_node.sdo[0x1007].raw = 5000   # microseconds
            
            logger.info("SYNC producer configurado: 10ms cycle, 5ms window")
            
        except Exception as e:
            logger.error(f"Error configurando SYNC: {e}")
    
    def load_eds_file(self, eds_path: str) -> bool:
        """
        Cargar archivo EDS (Electronic Data Sheet)
        
        Args:
            eds_path: Ruta al archivo EDS
            
        Returns:
            True si se cargó correctamente
        """
        try:
            logger.info(f"Cargando archivo EDS: {eds_path}")
            
            # Verificar que el archivo existe
            if not os.path.exists(eds_path):
                logger.error(f"Archivo EDS no encontrado: {eds_path}")
                return False
            
            # Cargar EDS file
            self.k13_node = self.network.add_node(self.node_id, eds_path)
            
            logger.info("✅ Archivo EDS cargado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando EDS file: {e}")
            return False
    
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
            
            elif cmd_type == 'pdo_read':
                pdo_number = command.get('pdo_number', 1)
                return self.pdo_read(pdo_number)
            
            elif cmd_type == 'pdo_write':
                pdo_number = command.get('pdo_number', 1)
                data_hex = command.get('data', '')
                data = bytes.fromhex(data_hex) if data_hex else b''
                return self.pdo_write(pdo_number, data)
            
            elif cmd_type == 'load_eds':
                eds_path = command.get('eds_path', '')
                success = self.load_eds_file(eds_path)
                return {'status': 'ok' if success else 'error', 'message': 'EDS loaded' if success else 'EDS load failed'}
            
            else:
                return {'error': f'Unknown command: {cmd_type}'}
        
        except Exception as e:
            logger.error(f"Error procesando comando: {e}")
            return {'error': str(e)}
    
    def emergency_stop(self) -> Dict[str, Any]:
        """Ejecutar parada de emergencia usando CiA 402 Control Word"""
        logger.warning("⚠️  PARADA DE EMERGENCIA SOLICITADA")
        
        try:
            # Método 1: Usar SDO con Object Dictionary (preferido si EDS cargado)
            if hasattr(self.k13_node, 'sdo'):
                try:
                    # Control Word: Quick Stop (bit 2 = 0)
                    # CiA 402: Quick Stop = 0x0002 (solo Enable Voltage)
                    self.k13_node.sdo[0x6040].raw = 0x0002
                    logger.info("✅ Parada de emergencia ejecutada via SDO (Control Word=0x0002)")
                    return {'status': 'ok', 'message': 'Emergency stop activated via SDO'}
                except Exception as sdo_error:
                    logger.warning(f"SDO falló: {sdo_error}, intentando PDO...")
            
            # Método 2: Usar PDO si está configurado
            if hasattr(self.k13_node, 'pdo') and 1 in self.k13_node.pdo.rx:
                quick_stop_data = b'\x02\x00'  # Control Word: 0x0002 (Quick Stop)
                self.k13_node.pdo.rx[1].data = quick_stop_data
                logger.info("✅ Parada de emergencia ejecutada via PDO")
                return {'status': 'ok', 'message': 'Emergency stop activated via PDO'}
            
            # Método 3: Fallback - enviar CAN raw
            logger.warning("Usando fallback: enviando CAN raw")
            return self.pdo_write(1, b'\x02\x00')
        
        except Exception as e:
            logger.error(f"❌ Error en parada de emergencia: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema incluyendo Object Dictionary"""
        try:
            status = {
                'status': 'ok',
                'connected': self.connected,
                'can_channel': self.can_channel,
                'node_id': self.node_id,
                'tcp_port': self.tcp_port,
                'last_error': self.last_error,
                'system_state': self.system_state
            }
            
            # Información del Object Dictionary si está disponible
            if hasattr(self.k13_node, 'object_dictionary') and self.k13_node.object_dictionary:
                status['eds_loaded'] = True
                status['device_type'] = self.k13_node.object_dictionary.device_information.product_name if hasattr(self.k13_node.object_dictionary, 'device_information') else 'Unknown'
            else:
                status['eds_loaded'] = False
                status['device_type'] = None
            
            # Intentar leer objetos CiA 402 vía SDO
            if hasattr(self.k13_node, 'sdo'):
                try:
                    # Status Word (0x6041)
                    status_word = self.k13_node.sdo[0x6041].raw
                    status['status_word'] = f"0x{status_word:04X}"
                    status['device_state'] = self._decode_status_word(status_word)
                except Exception as e:
                    logger.debug(f"No se pudo leer Status Word: {e}")
                    status['status_word'] = None
                    status['device_state'] = None
                
                try:
                    # Control Word (0x6040)
                    control_word = self.k13_node.sdo[0x6040].raw
                    status['control_word'] = f"0x{control_word:04X}"
                except Exception as e:
                    logger.debug(f"No se pudo leer Control Word: {e}")
                    status['control_word'] = None
                
                try:
                    # Velocity Actual Value (0x606C)
                    velocity = self.k13_node.sdo[0x606C].raw
                    status['velocity'] = velocity
                except Exception as e:
                    logger.debug(f"No se pudo leer Velocity: {e}")
                    status['velocity'] = None
                
                try:
                    # Position Actual Value (0x6064)
                    position = self.k13_node.sdo[0x6064].raw
                    status['position'] = position
                except Exception as e:
                    logger.debug(f"No se pudo leer Position: {e}")
                    status['position'] = None
            
            # Agregar información de PDO si está disponible
            if hasattr(self.k13_node, 'pdo') and self.system_state['pdo_active']:
                pdo_info = {}
                
                # Información de RPDO
                for i in range(1, 5):  # RPDO 1-4
                    if i in self.k13_node.pdo.rx:
                        rpdo = self.k13_node.pdo.rx[i]
                        pdo_info[f'rpdo_{i}'] = {
                            'cob_id': rpdo.cob_id,
                            'enabled': rpdo.enabled,
                            'transmission_type': rpdo.transmission_type,
                            'mapping': rpdo.mapping
                        }
                
                # Información de TPDO
                for i in range(1, 5):  # TPDO 1-4
                    if i in self.k13_node.pdo.tx:
                        tpdo = self.k13_node.pdo.tx[i]
                        pdo_info[f'tpdo_{i}'] = {
                            'cob_id': tpdo.cob_id,
                            'enabled': tpdo.enabled,
                            'transmission_type': tpdo.transmission_type,
                            'mapping': tpdo.mapping
                        }
                
                status['pdo_info'] = pdo_info
            
            return status
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _decode_status_word(self, status_word: int) -> Dict[str, bool]:
        """
        Decodificar Status Word del dispositivo
        
        Args:
            status_word: Valor del Status Word
            
        Returns:
            Diccionario con estado decodificado
        """
        return {
            'ready_to_switch_on': bool(status_word & (1 << 0)),
            'switched_on': bool(status_word & (1 << 1)),
            'operation_enabled': bool(status_word & (1 << 2)),
            'fault': bool(status_word & (1 << 3)),
            'voltage_enabled': bool(status_word & (1 << 4)),
            'quick_stop': bool(status_word & (1 << 5)),
            'switch_on_disabled': bool(status_word & (1 << 6)),
            'warning': bool(status_word & (1 << 7)),
            'manufacturer_specific': bool(status_word & (1 << 8)),
            'remote': bool(status_word & (1 << 9)),
            'target_reached': bool(status_word & (1 << 10)),
            'internal_limit': bool(status_word & (1 << 11)),
        }
    
    def reset(self) -> Dict[str, Any]:
        """Reset del sistema usando NMT y Fault Reset"""
        logger.info("Reset solicitado")
        
        try:
            # Paso 1: Si hay EDS, intentar Fault Reset via Control Word
            if hasattr(self.k13_node, 'sdo'):
                try:
                    # CiA 402: Fault Reset (bit 7 = 1)
                    # Control Word = 0x0080
                    self.k13_node.sdo[0x6040].raw = 0x0080
                    logger.info("✅ Fault Reset ejecutado via SDO")
                    time.sleep(0.1)  # Dar tiempo al dispositivo
                except Exception as sdo_error:
                    logger.warning(f"Fault Reset via SDO falló: {sdo_error}")
            
            # Paso 2: NMT Reset Node
            self.k13_node.nmt.send_command(0x81)  # Reset Node
            logger.info("✅ NMT Reset ejecutado")
            
            # Paso 3: Esperar a que el nodo reinicie
            time.sleep(0.5)
            
            # Paso 4: Poner en modo operacional
            self.k13_node.nmt.state = 'OPERATIONAL'
            logger.info("✅ Nodo en estado OPERATIONAL")
            
            return {'status': 'ok', 'message': 'System reset completed'}
        
        except Exception as e:
            logger.error(f"❌ Error en reset: {e}")
            return {'status': 'error', 'message': str(e)}
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
            # Acceso correcto según subindex
            if subindex == 0:
                value = self.k13_node.sdo[index].raw
            else:
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
            # Acceso correcto según subindex
            if subindex == 0:
                self.k13_node.sdo[index].raw = value
            else:
                self.k13_node.sdo[index][subindex].raw = value
            
            logger.info(f"SDO Write: 0x{index:04X}:{subindex} = {value}")
            return {'status': 'ok', 'message': 'Value written'}
        
        except Exception as e:
            logger.error(f"Error escribiendo SDO: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def pdo_read(self, pdo_number: int) -> Dict[str, Any]:
        """
        Leer datos de PDO
        
        Args:
            pdo_number: Número del PDO (1-4 para TPDO, 1-4 para RPDO)
            
        Returns:
            Diccionario con datos del PDO
        """
        try:
            if not hasattr(self.k13_node, 'pdo'):
                return {'status': 'error', 'message': 'PDO not supported'}
            
            if pdo_number not in self.k13_node.pdo.tx:
                return {'status': 'error', 'message': f'TPDO{pdo_number} not configured'}
            
            # Leer datos del PDO
            pdo_data = self.k13_node.pdo.tx[pdo_number].data
            cob_id = self.k13_node.pdo.tx[pdo_number].cob_id
            
            cob_id_str = f"0x{cob_id:03X}" if cob_id is not None else "None"
            logger.info(f"PDO Read TPDO{pdo_number}: COB-ID={cob_id_str}, Data={pdo_data.hex() if pdo_data else 'None'}")
            
            return {
                'status': 'ok',
                'pdo_number': pdo_number,
                'cob_id': cob_id,
                'data': list(pdo_data) if pdo_data else [],
                'data_hex': pdo_data.hex() if pdo_data else ''
            }
        
        except Exception as e:
            logger.error(f"Error leyendo PDO: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def pdo_write(self, pdo_number: int, data: bytes) -> Dict[str, Any]:
        """
        Escribir datos a PDO
        
        Args:
            pdo_number: Número del PDO (1-4 para RPDO)
            data: Datos a escribir
            
        Returns:
            Diccionario con resultado
        """
        try:
            # Ruta normal con PDOs configurados
            if hasattr(self.k13_node, 'pdo') and pdo_number in getattr(self.k13_node.pdo, 'rx', {}):
                # Escribir datos al PDO
                self.k13_node.pdo.rx[pdo_number].data = data
                cob_id = self.k13_node.pdo.rx[pdo_number].cob_id
                cob_id_str = f"0x{cob_id:03X}" if cob_id is not None else "None"
                logger.info(f"PDO Write RPDO{pdo_number}: COB-ID={cob_id_str}, Data={data.hex()}")

                # Enviar explícitamente por el bus CAN para asegurar entrega al simulador
                try:
                    if cob_id is not None and hasattr(self.network, 'bus') and self.network.bus is not None:
                        msg = can.Message(arbitration_id=cob_id, data=data, is_extended_id=False)
                        self.network.bus.send(msg)
                        logger.info(f"PDO RAW Enforced RPDO{pdo_number}: COB-ID=0x{cob_id:03X}, Data={data.hex()}")
                except Exception as send_err:
                    logger.warning(f"Fallo envío RAW RPDO{pdo_number} (se continúa): {send_err}")
                return {
                    'status': 'ok',
                    'pdo_number': pdo_number,
                    'cob_id': cob_id,
                    'data': list(data),
                    'data_hex': data.hex()
                }

            # Fallback: enviar CAN en crudo usando COB-IDs por defecto (CiA 301)
            default_bases = {1: 0x200, 2: 0x300, 3: 0x400, 4: 0x500}
            base = default_bases.get(pdo_number)
            if base is None:
                return {'status': 'error', 'message': f'RPDO{pdo_number} not supported'}

            cob_id = base + int(self.node_id)
            if not hasattr(self.network, 'bus') or self.network.bus is None:
                return {'status': 'error', 'message': 'CAN bus not available'}

            msg = can.Message(arbitration_id=cob_id, data=data, is_extended_id=False)
            self.network.bus.send(msg)
            logger.info(f"PDO RAW Write RPDO{pdo_number}: COB-ID=0x{cob_id:03X}, Data={data.hex()}")
            return {
                'status': 'ok',
                'pdo_number': pdo_number,
                'cob_id': cob_id,
                'data': list(data),
                'data_hex': data.hex(),
                'raw': True
            }

        except Exception as e:
            logger.error(f"Error escribiendo PDO: {e}")
            return {'status': 'error', 'message': str(e)}


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BL335 Gateway')
    parser.add_argument('--can', default='vcan0', help='Canal CAN (default: vcan0 para testing)')
    parser.add_argument('--interface', default='virtual', 
                       choices=['socketcan', 'virtual'],
                       help='Interfaz CAN: socketcan (Linux real) o virtual (testing)')
    parser.add_argument('--node-id', type=int, default=1, help='Node ID del R13 F')
    parser.add_argument('--port', type=int, default=9999, help='Puerto TCP')
    parser.add_argument('--eds', help='Ruta al archivo EDS del R13 F')
    parser.add_argument('--verbose', action='store_true', help='Modo verbose')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Crear gateway
    gateway = BL335Gateway(
        can_channel=args.can,
        node_id=args.node_id,
        tcp_port=args.port,
        can_interface=args.interface
    )
    
    # Cargar EDS file si se especificó
    if args.eds:
        if not gateway.load_eds_file(args.eds):
            print(f"⚠️  Error cargando EDS file: {args.eds}")
            print("Continuando sin EDS file...")
    
    print("=" * 60)
    print("🚀 BL335 Gateway - Python CANopen")
    print("=" * 60)
    print(f"CAN Channel: {args.can}")
    print(f"CAN Interface: {args.interface}")
    print(f"Node ID: {args.node_id}")
    print(f"TCP Port: {args.port}")
    if args.eds:
        print(f"EDS File: {args.eds}")
    print("\nModos de interfaz CAN:")
    print("  - socketcan: Linux con módulos kernel (producción)")
    print("  - virtual: Sin módulos kernel (testing/desarrollo)")
    print("\nPresiona Ctrl+C para detener")
    print("=" * 60)
    
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
