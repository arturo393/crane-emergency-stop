#!/usr/bin/env python3
"""
Simulador CAN Virtual para Testing sin Hardware

Simula el receptor Danfoss R13 F y responde a comandos CANopen.
Útil para desarrollo y testing antes de tener hardware real.
"""

import can
import canopen
import time
import logging
from threading import Thread, Event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CAN_Simulator")


class R13FSimulator:
    """Simulador del receptor Danfoss R13 F"""
    
    def __init__(self, channel='vcan0', node_id=1):
        """
        Inicializar simulador
        
        Args:
            channel: Canal CAN virtual (default: vcan0)
            node_id: ID del nodo CANopen (default: 1)
        """
        self.channel = channel
        self.node_id = node_id
        self.bus = None
        self.running = Event()
        
        # Estado del simulador
        self.state = {
            'operational': False,
            'emergency_stop': False,
            'last_command': None,
            'heartbeat_count': 0,
            'error_count': 0
        }
        
        logger.info(f"Simulador R13 F inicializado: Node ID={node_id}, Channel={channel}")
    
    def start(self):
        """Iniciar simulador"""
        try:
            # Crear bus CAN virtual
            self.bus = can.interface.Bus(
                channel=self.channel,
                interface='socketcan',
                bitrate=250000
            )
            
            self.running.set()
            
            # Iniciar threads
            Thread(target=self._heartbeat_task, daemon=True).start()
            Thread(target=self._receive_task, daemon=True).start()
            
            logger.info("Simulador iniciado correctamente")
            self.state['operational'] = True
            
        except Exception as e:
            logger.error(f"Error iniciando simulador: {e}")
            logger.info("Asegúrate de crear el canal virtual: sudo modprobe vcan && sudo ip link add dev vcan0 type vcan && sudo ip link set up vcan0")
    
    def stop(self):
        """Detener simulador"""
        self.running.clear()
        if self.bus:
            self.bus.shutdown()
        logger.info("Simulador detenido")
    
    def _heartbeat_task(self):
        """Enviar heartbeat cada 500ms"""
        while self.running.is_set():
            try:
                # Heartbeat CANopen: COB-ID = 0x700 + Node ID
                cob_id = 0x700 + self.node_id
                
                # Estado: 0x05 = Operational, 0x04 = Stopped
                state = 0x05 if self.state['operational'] else 0x04
                
                msg = can.Message(
                    arbitration_id=cob_id,
                    data=[state],
                    is_extended_id=False
                )
                
                self.bus.send(msg)
                self.state['heartbeat_count'] += 1
                
                if self.state['heartbeat_count'] % 10 == 0:
                    logger.debug(f"Heartbeat enviado: {self.state['heartbeat_count']}")
                
            except Exception as e:
                logger.error(f"Error enviando heartbeat: {e}")
                self.state['error_count'] += 1
            
            time.sleep(0.5)  # 500ms
    
    def _receive_task(self):
        """Recibir y procesar mensajes CAN"""
        while self.running.is_set():
            try:
                msg = self.bus.recv(timeout=0.1)
                if msg:
                    self._process_message(msg)
            except Exception as e:
                logger.error(f"Error recibiendo mensaje: {e}")
    
    def _process_message(self, msg: can.Message):
        """Procesar mensaje CAN recibido"""
        cob_id = msg.arbitration_id
        data = msg.data
        
        logger.debug(f"RX: ID=0x{cob_id:03X}, Data={data.hex()}")
        
        # NMT (Network Management) - COB-ID 0x000
        if cob_id == 0x000:
            self._handle_nmt(data)
        
        # SDO (Service Data Object) - COB-ID 0x600 + Node ID
        elif cob_id == 0x600 + self.node_id:
            self._handle_sdo_request(data)
        
        # Emergency Stop - Comando específico
        elif cob_id == 0x200:  # ID arbitrario para emergencia
            self._handle_emergency_stop(data)
        
        else:
            logger.debug(f"Mensaje no manejado: COB-ID=0x{cob_id:03X}")
    
    def _handle_nmt(self, data):
        """Manejar comandos NMT"""
        if len(data) < 2:
            return
        
        command = data[0]
        node_id = data[1]
        
        # Si el comando es para este nodo o broadcast (0)
        if node_id == self.node_id or node_id == 0:
            if command == 0x01:  # Start (Operational)
                self.state['operational'] = True
                logger.info("Estado: OPERATIONAL")
            elif command == 0x02:  # Stop
                self.state['operational'] = False
                logger.info("Estado: STOPPED")
            elif command == 0x80:  # Pre-operational
                self.state['operational'] = False
                logger.info("Estado: PRE-OPERATIONAL")
            elif command == 0x81:  # Reset
                logger.info("Reset solicitado")
                self._reset()
    
    def _handle_sdo_request(self, data):
        """Manejar solicitud SDO"""
        if len(data) < 4:
            return
        
        command = data[0]
        index = (data[2] << 8) | data[1]
        subindex = data[3]
        
        logger.debug(f"SDO Request: cmd=0x{command:02X}, index=0x{index:04X}, sub={subindex}")
        
        # Responder con SDO (simplificado)
        response_cob_id = 0x580 + self.node_id
        response_data = [0x60, data[1], data[2], data[3], 0x00, 0x00, 0x00, 0x00]
        
        msg = can.Message(
            arbitration_id=response_cob_id,
            data=response_data,
            is_extended_id=False
        )
        
        self.bus.send(msg)
        logger.debug(f"SDO Response enviada")
    
    def _handle_emergency_stop(self, data):
        """Manejar parada de emergencia"""
        self.state['emergency_stop'] = True
        self.state['operational'] = False
        self.state['last_command'] = 'EMERGENCY_STOP'
        
        logger.warning("⚠️  PARADA DE EMERGENCIA ACTIVADA")
        
        # Enviar confirmación
        msg = can.Message(
            arbitration_id=0x201,
            data=[0xFF, 0xFF, 0xFF, 0xFF],  # Confirmación
            is_extended_id=False
        )
        self.bus.send(msg)
    
    def _reset(self):
        """Reset del simulador"""
        self.state = {
            'operational': False,
            'emergency_stop': False,
            'last_command': None,
            'heartbeat_count': 0,
            'error_count': 0
        }
        logger.info("Simulador reseteado")
    
    def get_state(self):
        """Obtener estado actual del simulador"""
        return self.state.copy()


def main():
    """Función principal para ejecutar el simulador"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simulador CAN R13 F')
    parser.add_argument('--channel', default='vcan0', help='Canal CAN virtual')
    parser.add_argument('--node-id', type=int, default=1, help='ID del nodo')
    parser.add_argument('--verbose', action='store_true', help='Modo verbose')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Crear y ejecutar simulador
    simulator = R13FSimulator(channel=args.channel, node_id=args.node_id)
    
    print("=" * 60)
    print("🚀 Simulador CAN Danfoss R13 F")
    print("=" * 60)
    print(f"Canal: {args.channel}")
    print(f"Node ID: {args.node_id}")
    print(f"Bitrate: 250 kbps")
    print("\nPara crear el canal virtual ejecuta:")
    print("  sudo modprobe vcan")
    print("  sudo ip link add dev vcan0 type vcan")
    print("  sudo ip link set up vcan0")
    print("\nPresiona Ctrl+C para detener")
    print("=" * 60)
    
    simulator.start()
    
    try:
        # Mostrar estado cada 5 segundos
        while True:
            time.sleep(5)
            state = simulator.get_state()
            print(f"\n📊 Estado: Operational={state['operational']}, "
                  f"Heartbeats={state['heartbeat_count']}, "
                  f"Errors={state['error_count']}")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Deteniendo simulador...")
        simulator.stop()
        print("✅ Simulador detenido")


if __name__ == "__main__":
    main()
