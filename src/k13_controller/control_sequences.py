"""
Biblioteca de Secuencias de Control Complejas
Operaciones de alto nivel para el sistema K13 Puente Grúa
"""

import time
import logging
from typing import Dict, Any, Callable, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ControlSequences")


class SequenceResult(Enum):
    """Resultados posibles de una secuencia"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ABORTED = "aborted"


class ControlSequences:
    """
    Biblioteca de secuencias de control de alto nivel
    
    Proporciona operaciones compuestas como:
    - Arranque seguro del sistema
    - Movimiento controlado
    - Parada normal y de emergencia
    - Secuencias de posicionamiento
    """
    
    def __init__(self, gateway, simulator=None):
        """
        Inicializar secuencias de control
        
        Args:
            gateway: Instancia del BL335Gateway
            simulator: Instancia opcional del R13FSimulator (para verificación directa)
        """
        self.gateway = gateway
        self.simulator = simulator
        self.abort_requested = False
        
        logger.info("ControlSequences inicializado")
    
    def get_device_state(self) -> str:
        """Obtener estado actual del dispositivo"""
        if self.simulator:
            return self.simulator.get_state()['device_state']
        else:
            # Leer via gateway
            status = self.gateway.get_status()
            if 'k13_decoded_status' in status:
                # Decodificar estado desde status word
                decoded = status['k13_decoded_status']
                if decoded['fault']:
                    return 'FAULT'
                elif decoded['operation_enabled']:
                    return 'OPERATION_ENABLED'
                elif decoded['switched_on']:
                    return 'SWITCHED_ON'
                elif decoded['ready_to_switch_on']:
                    return 'READY_TO_SWITCH_ON'
                elif decoded['switch_on_disabled']:
                    return 'SWITCH_ON_DISABLED'
            return 'UNKNOWN'
    
    def wait_for_state(self, target_state: str, timeout: float = 5.0) -> bool:
        """
        Esperar hasta que el dispositivo alcance un estado específico
        
        Args:
            target_state: Estado objetivo
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            True si se alcanzó el estado, False si timeout
        """
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            if self.abort_requested:
                logger.warning("Espera de estado abortada")
                return False
            
            current_state = self.get_device_state()
            logger.debug(f"Estado actual: {current_state}, objetivo: {target_state}")
            
            if current_state == target_state:
                return True
            
            time.sleep(0.1)
        
        logger.warning(f"Timeout esperando estado {target_state}")
        return False
    
    def startup_sequence(self) -> SequenceResult:
        """
        Secuencia de arranque completa y segura
        
        Pasos:
        1. Verificar estado inicial
        2. Transición a READY_TO_SWITCH_ON
        3. Transición a SWITCHED_ON
        4. Transición a OPERATION_ENABLED
        
        Returns:
            SequenceResult indicando éxito o falla
        """
        logger.info("=" * 60)
        logger.info("🚀 SECUENCIA DE ARRANQUE")
        logger.info("=" * 60)
        
        try:
            # Paso 1: Verificar estado inicial
            logger.info("Paso 1/4: Verificando estado inicial...")
            initial_state = self.get_device_state()
            logger.info(f"  Estado inicial: {initial_state}")
            
            if initial_state == 'FAULT':
                logger.error("  ❌ Dispositivo en FAULT. Se requiere reset.")
                return SequenceResult.FAILED
            
            # Paso 2: Transición a READY_TO_SWITCH_ON
            logger.info("Paso 2/4: Transición a READY_TO_SWITCH_ON...")
            
            if initial_state != 'READY_TO_SWITCH_ON':
                # Control Word = 0x0006 (Shutdown)
                data = bytes([0x06, 0x00, 0x00, 0x00])
                result = self.gateway.pdo_write(1, data)
                
                if result.get('status') != 'ok':
                    logger.error(f"  ❌ Error enviando comando: {result}")
                    return SequenceResult.FAILED
                
                if not self.wait_for_state('READY_TO_SWITCH_ON', timeout=3.0):
                    logger.error("  ❌ Timeout en transición")
                    return SequenceResult.TIMEOUT
            
            logger.info("  ✅ En READY_TO_SWITCH_ON")
            
            # Paso 3: Transición a SWITCHED_ON
            logger.info("Paso 3/4: Transición a SWITCHED_ON...")
            
            # Control Word = 0x0007 (Switch On)
            data = bytes([0x07, 0x00, 0x00, 0x00])
            result = self.gateway.pdo_write(1, data)
            
            if result.get('status') != 'ok':
                logger.error(f"  ❌ Error enviando comando: {result}")
                return SequenceResult.FAILED
            
            time.sleep(0.3)  # Dar tiempo para transiciones en cadena
            
            # Verificar que llegamos a SWITCHED_ON o más allá
            current_state = self.get_device_state()
            if current_state not in ['SWITCHED_ON', 'OPERATION_ENABLED']:
                logger.error(f"  ❌ Estado inesperado: {current_state}")
                return SequenceResult.FAILED
            
            logger.info(f"  ✅ En {current_state}")
            
            # Paso 4: Transición a OPERATION_ENABLED
            logger.info("Paso 4/4: Transición a OPERATION_ENABLED...")
            
            # Control Word = 0x000F (Enable Operation)
            data = bytes([0x0F, 0x00, 0x00, 0x00])
            result = self.gateway.pdo_write(1, data)
            
            if result.get('status') != 'ok':
                logger.error(f"  ❌ Error enviando comando: {result}")
                return SequenceResult.FAILED
            
            if not self.wait_for_state('OPERATION_ENABLED', timeout=3.0):
                logger.error("  ❌ Timeout en transición")
                return SequenceResult.TIMEOUT
            
            logger.info("  ✅ En OPERATION_ENABLED")
            
            logger.info("=" * 60)
            logger.info("✅ SECUENCIA DE ARRANQUE COMPLETADA")
            logger.info("=" * 60)
            
            return SequenceResult.SUCCESS
        
        except Exception as e:
            logger.error(f"❌ Error en secuencia de arranque: {e}")
            return SequenceResult.FAILED
    
    def shutdown_sequence(self, emergency: bool = False) -> SequenceResult:
        """
        Secuencia de parada
        
        Args:
            emergency: Si True, ejecuta parada de emergencia (Quick Stop)
                      Si False, ejecuta parada normal
        
        Returns:
            SequenceResult indicando éxito o falla
        """
        logger.info("=" * 60)
        logger.info(f"🛑 SECUENCIA DE PARADA ({'EMERGENCIA' if emergency else 'NORMAL'})")
        logger.info("=" * 60)
        
        try:
            current_state = self.get_device_state()
            logger.info(f"Estado actual: {current_state}")
            
            if emergency:
                # Parada de emergencia: Quick Stop
                logger.info("Ejecutando Quick Stop...")
                result = self.gateway.emergency_stop()
                
                if result.get('status') != 'ok':
                    logger.error(f"  ❌ Error en parada de emergencia: {result}")
                    return SequenceResult.FAILED
                
                if not self.wait_for_state('QUICK_STOP_ACTIVE', timeout=2.0):
                    logger.warning("  ⚠️  No se pudo verificar QUICK_STOP_ACTIVE")
                
                logger.info("  ✅ Parada de emergencia ejecutada")
            
            else:
                # Parada normal: desactivar operación
                logger.info("Desactivando operación...")
                
                # Control Word = 0x0007 (Disable Operation)
                data = bytes([0x07, 0x00, 0x00, 0x00])
                result = self.gateway.pdo_write(1, data)
                
                if result.get('status') != 'ok':
                    logger.error(f"  ❌ Error en parada: {result}")
                    return SequenceResult.FAILED
                
                time.sleep(0.3)
                logger.info("  ✅ Operación desactivada")
            
            logger.info("=" * 60)
            logger.info("✅ SECUENCIA DE PARADA COMPLETADA")
            logger.info("=" * 60)
            
            return SequenceResult.SUCCESS
        
        except Exception as e:
            logger.error(f"❌ Error en secuencia de parada: {e}")
            return SequenceResult.FAILED
    
    def set_velocity_safe(self, target_velocity: int, ramp_time: float = 1.0) -> SequenceResult:
        """
        Configurar velocidad con rampa suave
        
        Args:
            target_velocity: Velocidad objetivo en RPM
            ramp_time: Tiempo de rampa en segundos
            
        Returns:
            SequenceResult indicando éxito o falla
        """
        logger.info("=" * 60)
        logger.info(f"⚡ CONFIGURANDO VELOCIDAD: {target_velocity} RPM")
        logger.info("=" * 60)
        
        try:
            # Verificar que estamos en OPERATION_ENABLED
            current_state = self.get_device_state()
            
            if current_state != 'OPERATION_ENABLED':
                logger.error(f"  ❌ Estado incorrecto: {current_state}")
                logger.error("  Se requiere OPERATION_ENABLED")
                return SequenceResult.FAILED
            
            # Obtener velocidad actual
            if self.simulator:
                current_velocity = self.simulator.get_state()['actual_velocity']
            else:
                # Leer via SDO
                result = self.gateway.sdo_read(0x606C, 0)  # Velocity Actual Value
                current_velocity = result.get('value', 0)
            
            logger.info(f"Velocidad actual: {current_velocity} RPM")
            logger.info(f"Velocidad objetivo: {target_velocity} RPM")
            
            # Calcular pasos de rampa
            velocity_delta = target_velocity - current_velocity
            num_steps = max(10, int(abs(velocity_delta) / 100))  # Mínimo 10 pasos
            step_size = velocity_delta / num_steps
            step_time = ramp_time / num_steps
            
            logger.info(f"Rampa: {num_steps} pasos de {step_size:.1f} RPM cada {step_time:.3f}s")
            
            # Aplicar rampa
            for i in range(num_steps + 1):
                if self.abort_requested:
                    logger.warning("  ⚠️  Rampa abortada")
                    return SequenceResult.ABORTED
                
                intermediate_velocity = int(current_velocity + (step_size * i))
                
                # Escribir velocidad objetivo (0x6081)
                result = self.gateway.sdo_write(0x6081, 0, intermediate_velocity)
                
                if result.get('status') != 'ok':
                    logger.error(f"  ❌ Error escribiendo velocidad: {result}")
                    return SequenceResult.FAILED
                
                logger.debug(f"  Paso {i+1}/{num_steps+1}: {intermediate_velocity} RPM")
                time.sleep(step_time)
            
            logger.info(f"  ✅ Velocidad configurada: {target_velocity} RPM")
            logger.info("=" * 60)
            
            return SequenceResult.SUCCESS
        
        except Exception as e:
            logger.error(f"❌ Error configurando velocidad: {e}")
            return SequenceResult.FAILED
    
    def move_to_position(self, target_position: int, velocity: int = 1000) -> SequenceResult:
        """
        Mover a posición específica
        
        Args:
            target_position: Posición objetivo en mm
            velocity: Velocidad de movimiento en RPM
            
        Returns:
            SequenceResult indicando éxito o falla
        """
        logger.info("=" * 60)
        logger.info(f"📍 MOVIMIENTO A POSICIÓN: {target_position} mm")
        logger.info("=" * 60)
        
        try:
            # Verificar estado
            current_state = self.get_device_state()
            
            if current_state != 'OPERATION_ENABLED':
                logger.error(f"  ❌ Estado incorrecto: {current_state}")
                return SequenceResult.FAILED
            
            # Configurar velocidad
            logger.info(f"Configurando velocidad: {velocity} RPM...")
            result = self.gateway.sdo_write(0x6081, 0, velocity)
            
            if result.get('status') != 'ok':
                logger.error(f"  ❌ Error configurando velocidad: {result}")
                return SequenceResult.FAILED
            
            # Configurar posición objetivo
            logger.info(f"Configurando posición objetivo: {target_position} mm...")
            result = self.gateway.sdo_write(0x607A, 0, target_position)
            
            if result.get('status') != 'ok':
                logger.error(f"  ❌ Error configurando posición: {result}")
                return SequenceResult.FAILED
            
            # Monitorear hasta alcanzar posición
            logger.info("Moviendo a posición...")
            timeout = 30.0  # 30 segundos máximo
            start_time = time.time()
            tolerance = 10  # mm de tolerancia
            
            while (time.time() - start_time) < timeout:
                if self.abort_requested:
                    logger.warning("  ⚠️  Movimiento abortado")
                    return SequenceResult.ABORTED
                
                # Leer posición actual
                if self.simulator:
                    current_position = self.simulator.get_state()['actual_position']
                else:
                    result = self.gateway.sdo_read(0x6064, 0)
                    current_position = result.get('value', 0)
                
                distance = abs(target_position - current_position)
                
                if distance <= tolerance:
                    logger.info(f"  ✅ Posición alcanzada: {current_position} mm")
                    logger.info("=" * 60)
                    return SequenceResult.SUCCESS
                
                logger.debug(f"  Posición actual: {current_position} mm (faltan {distance} mm)")
                time.sleep(0.5)
            
            logger.error("  ❌ Timeout alcanzando posición")
            return SequenceResult.TIMEOUT
        
        except Exception as e:
            logger.error(f"❌ Error en movimiento: {e}")
            return SequenceResult.FAILED
    
    def abort(self):
        """Abortar secuencia en ejecución"""
        logger.warning("⚠️  ABORTANDO SECUENCIA")
        self.abort_requested = True
    
    def reset_abort(self):
        """Resetear flag de abort"""
        self.abort_requested = False


def demo_sequences():
    """Demostración de secuencias de control"""
    import sys
    import os
    
    # Añadir rutas
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    from src.bl335_gateway.simulator_adapter import IntegratedSystem
    
    print("=" * 70)
    print("🎯 DEMO: Secuencias de Control Complejas")
    print("=" * 70)
    
    # Iniciar sistema integrado
    print("\n🚀 Iniciando sistema integrado...")
    system = IntegratedSystem(node_id=1, tcp_port=9999)
    
    if not system.start():
        print("❌ Error iniciando sistema")
        return 1
    
    time.sleep(2)
    
    try:
        # Crear instancia de secuencias
        sequences = ControlSequences(
            gateway=system.gateway,
            simulator=system.simulator
        )
        
        # Demo 1: Secuencia de arranque
        print("\n" + "=" * 70)
        print("DEMO 1: Secuencia de Arranque")
        print("=" * 70)
        result = sequences.startup_sequence()
        print(f"\nResultado: {result.value}")
        time.sleep(2)
        
        # Demo 2: Configurar velocidad con rampa
        print("\n" + "=" * 70)
        print("DEMO 2: Rampa de Velocidad")
        print("=" * 70)
        result = sequences.set_velocity_safe(1500, ramp_time=2.0)
        print(f"\nResultado: {result.value}")
        time.sleep(3)
        
        # Demo 3: Parada normal
        print("\n" + "=" * 70)
        print("DEMO 3: Parada Normal")
        print("=" * 70)
        result = sequences.shutdown_sequence(emergency=False)
        print(f"\nResultado: {result.value}")
        time.sleep(2)
        
        # Demo 4: Arranque y parada de emergencia
        print("\n" + "=" * 70)
        print("DEMO 4: Parada de Emergencia")
        print("=" * 70)
        sequences.startup_sequence()
        time.sleep(1)
        result = sequences.shutdown_sequence(emergency=True)
        print(f"\nResultado: {result.value}")
        
        print("\n" + "=" * 70)
        print("✅ DEMOS COMPLETADOS")
        print("=" * 70)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrumpido")
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        print("\n⏹️  Deteniendo sistema...")
        system.stop()


if __name__ == "__main__":
    import sys
    sys.exit(demo_sequences())
