"""
Adaptador Simulador-Gateway
Conecta el simulador CANopen R13 F con el BL335 Gateway
"""

import can
import time
import logging
import threading
from typing import Optional, Dict, Any
import sys
import os

# Añadir el directorio tools al path para importar el simulador
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from tools.can_simulator import R13FSimulator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SimulatorAdapter")


class SimulatorBridge:
    """
    Puente entre el simulador CANopen y el Gateway BL335
    
    Este adaptador permite que el BL335 Gateway se comunique con el
    simulador CANopen como si fuera el dispositivo físico R13 F real.
    """
    
    def __init__(self, simulator: R13FSimulator, virtual_bus: can.Bus):
        """
        Inicializar puente
        
        Args:
            simulator: Instancia del simulador R13 F
            virtual_bus: Bus CAN virtual para comunicación con gateway
        """
        self.simulator = simulator
        self.virtual_bus = virtual_bus
        self.running = False
        
        # Threads para mensajes bidireccionales
        self.sim_to_gateway_thread = None
        self.gateway_to_sim_thread = None
        
        logger.info("SimulatorBridge inicializado")
    
    def start(self):
        """Iniciar puente bidireccional"""
        if self.running:
            logger.warning("Bridge ya está corriendo")
            return
        
        self.running = True
        
        # Thread 1: Reenviar mensajes del simulador al gateway
        self.sim_to_gateway_thread = threading.Thread(
            target=self._forward_simulator_to_gateway,
            daemon=True
        )
        self.sim_to_gateway_thread.start()
        
        # Thread 2: Reenviar mensajes del gateway al simulador
        self.gateway_to_sim_thread = threading.Thread(
            target=self._forward_gateway_to_simulator,
            daemon=True
        )
        self.gateway_to_sim_thread.start()
        
        logger.info("✅ SimulatorBridge iniciado (bidireccional)")
    
    def stop(self):
        """Detener puente"""
        logger.info("Deteniendo SimulatorBridge...")
        self.running = False
        
        if self.sim_to_gateway_thread:
            self.sim_to_gateway_thread.join(timeout=1.0)
        if self.gateway_to_sim_thread:
            self.gateway_to_sim_thread.join(timeout=1.0)
        
        logger.info("SimulatorBridge detenido")
    
    def _forward_simulator_to_gateway(self):
        """Reenviar mensajes del simulador al gateway"""
        logger.info("Thread Sim→Gateway iniciado")
        
        while self.running:
            try:
                # Leer mensaje del bus del simulador
                msg = self.simulator.bus.recv(timeout=0.1)
                
                if msg:
                    # Reenviar al bus virtual del gateway
                    self.virtual_bus.send(msg)
                    logger.debug(f"Sim→Gateway: ID=0x{msg.arbitration_id:03X}, Data={msg.data.hex()}")
            
            except can.CanError as e:
                if self.running:
                    logger.error(f"Error CAN Sim→Gateway: {e}")
            except Exception as e:
                if self.running:
                    logger.error(f"Error forwarding Sim→Gateway: {e}")
    
    def _forward_gateway_to_simulator(self):
        """Reenviar mensajes del gateway al simulador"""
        logger.info("Thread Gateway→Sim iniciado")
        
        while self.running:
            try:
                # Leer mensaje del bus virtual del gateway
                msg = self.virtual_bus.recv(timeout=0.1)
                
                if msg:
                    # Reenviar al bus del simulador
                    self.simulator.bus.send(msg)
                    logger.debug(f"Gateway→Sim: ID=0x{msg.arbitration_id:03X}, Data={msg.data.hex()}")
            
            except can.CanError as e:
                if self.running:
                    logger.error(f"Error CAN Gateway→Sim: {e}")
            except Exception as e:
                if self.running:
                    logger.error(f"Error forwarding Gateway→Sim: {e}")


class IntegratedSystem:
    """
    Sistema integrado: Simulador + Bridge + Gateway
    
    Proporciona una interfaz unificada para iniciar/detener todo el sistema.
    """
    
    def __init__(self, node_id: int = 1, tcp_port: int = 9999):
        """
        Inicializar sistema integrado
        
        Args:
            node_id: ID del nodo CANopen
            tcp_port: Puerto TCP del gateway
        """
        self.node_id = node_id
        self.tcp_port = tcp_port
        
        # Componentes
        self.simulator = None
        self.bridge = None
        self.gateway = None
        
        # Buses CAN virtuales
        self.simulator_bus = None
        self.gateway_bus = None
        
        logger.info(f"IntegratedSystem creado: Node={node_id}, Port={tcp_port}")
    
    def start(self):
        """Iniciar sistema completo"""
        try:
            logger.info("=" * 60)
            logger.info("🚀 Iniciando Sistema Integrado")
            logger.info("=" * 60)
            
            # 1. Crear buses CAN virtuales
            logger.info("1/4 Creando buses CAN virtuales...")
            self.simulator_bus = can.interface.Bus(
                interface='virtual',
                channel='sim_bus',
                receive_own_messages=False
            )
            self.gateway_bus = can.interface.Bus(
                interface='virtual',
                channel='sim_bus',
                receive_own_messages=False
            )
            logger.info("   ✅ Buses CAN virtuales creados")
            
            # 2. Iniciar simulador R13 F
            logger.info("2/4 Iniciando simulador R13 F...")
            self.simulator = R13FSimulator(
                node_id=self.node_id,
                channel='sim_bus',
                batch_mode=False,  # Modo normal con bus CAN
                bus=self.simulator_bus  # Usar bus pre-creado
            )
            self.simulator.start()
            logger.info("   ✅ Simulador R13 F iniciado")
            
            # 3. Crear puente Simulador-Gateway
            logger.info("3/4 Creando puente Simulador↔Gateway...")
            self.bridge = SimulatorBridge(
                simulator=self.simulator,
                virtual_bus=self.gateway_bus
            )
            self.bridge.start()
            logger.info("   ✅ Puente bidireccional activo")
            
            # 4. Iniciar Gateway BL335
            logger.info("4/4 Iniciando BL335 Gateway...")
            # Importar aquí para evitar circular imports
            from .main import BL335Gateway
            
            self.gateway = BL335Gateway(
                can_channel='sim_bus',
                node_id=self.node_id,
                tcp_port=self.tcp_port,
                can_interface='virtual'
            )
            
            # Inyectar el bus virtual del gateway
            self.gateway._virtual_bus = self.gateway_bus
            self.gateway.start()
            logger.info("   ✅ Gateway BL335 iniciado")
            
            logger.info("=" * 60)
            logger.info("✅ Sistema Integrado LISTO")
            logger.info("=" * 60)
            logger.info(f"📡 Servidor TCP: puerto {self.tcp_port}")
            logger.info(f"🤖 Simulador: Node ID {self.node_id}")
            logger.info(f"🌉 Puente: Simulador ↔ Gateway")
            logger.info("=" * 60)
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Error iniciando sistema integrado: {e}")
            self.stop()
            return False
    
    def stop(self):
        """Detener sistema completo"""
        logger.info("Deteniendo sistema integrado...")
        
        # Detener en orden inverso
        if self.gateway:
            try:
                self.gateway.stop()
            except Exception as e:
                logger.error(f"Error deteniendo gateway: {e}")
        
        if self.bridge:
            try:
                self.bridge.stop()
            except Exception as e:
                logger.error(f"Error deteniendo bridge: {e}")
        
        if self.simulator:
            try:
                self.simulator.stop()
            except Exception as e:
                logger.error(f"Error deteniendo simulador: {e}")
        
        # Cerrar buses
        if self.simulator_bus:
            try:
                self.simulator_bus.shutdown()
            except Exception as e:
                logger.error(f"Error cerrando simulator bus: {e}")
        
        if self.gateway_bus:
            try:
                self.gateway_bus.shutdown()
            except Exception as e:
                logger.error(f"Error cerrando gateway bus: {e}")
        
        logger.info("✅ Sistema integrado detenido")
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema completo"""
        status = {
            'simulator': None,
            'gateway': None,
            'bridge': None
        }
        
        if self.simulator:
            status['simulator'] = self.simulator.get_state()
        
        if self.gateway:
            status['gateway'] = self.gateway.get_status()
        
        if self.bridge:
            status['bridge'] = {
                'running': self.bridge.running
            }
        
        return status


def main():
    """Función principal - Demo del sistema integrado"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sistema Integrado: Simulador R13 F + BL335 Gateway'
    )
    parser.add_argument('--node-id', type=int, default=1, 
                       help='Node ID del R13 F (default: 1)')
    parser.add_argument('--port', type=int, default=9999, 
                       help='Puerto TCP del gateway (default: 9999)')
    parser.add_argument('--verbose', action='store_true', 
                       help='Modo verbose (más logs)')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("=" * 70)
    print("🎯 SISTEMA INTEGRADO: Simulador R13 F + BL335 Gateway")
    print("=" * 70)
    print()
    print("Este sistema integra:")
    print("  1. Simulador CANopen R13 F (dispositivo virtual)")
    print("  2. Puente bidireccional (reenvío de mensajes CAN)")
    print("  3. BL335 Gateway (servidor TCP/IP)")
    print()
    print(f"Configuración:")
    print(f"  • Node ID: {args.node_id}")
    print(f"  • Puerto TCP: {args.port}")
    print()
    print("Prueba la conexión con:")
    print(f"  $ telnet localhost {args.port}")
    print()
    print("O usa el cliente Python:")
    print(f"  $ python src/k13_controller/network_comm.py")
    print()
    print("Presiona Ctrl+C para detener")
    print("=" * 70)
    
    # Crear sistema integrado
    system = IntegratedSystem(
        node_id=args.node_id,
        tcp_port=args.port
    )
    
    try:
        # Iniciar sistema
        if not system.start():
            print("\n❌ Error iniciando sistema")
            return 1
        
        print("\n✅ Sistema integrado funcionando")
        print("\n📊 Verificando estado inicial...")
        time.sleep(1)
        
        status = system.get_status()
        print(f"\n   Simulador: {status['simulator']['device_state']}")
        print(f"   Gateway: {'Conectado' if status['gateway']['connected'] else 'Desconectado'}")
        print(f"   Bridge: {'Activo' if status['bridge']['running'] else 'Inactivo'}")
        
        print("\n🔄 Sistema listo para recibir comandos TCP...")
        
        # Mantener vivo
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Deteniendo sistema...")
        system.stop()
        print("✅ Sistema detenido correctamente")
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        system.stop()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
