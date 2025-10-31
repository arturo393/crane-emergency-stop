"""
Test específico para verificar el fix de SDO velocity con delay adaptativo
"""

import pytest
import time
import logging
from src.k13_controller.control_sequences import ControlSequences, SequenceResult
from src.bl335_gateway.simulator_adapter import IntegratedSystem

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_sdo_velocity_with_delay():
    """Test aislado: Verificar que SDO velocity funciona con delay adaptativo"""
    
    # Crear sistema integrado con puerto único
    import random
    port = random.randint(15000, 16000)
    
    logger.info(f"🚀 Iniciando sistema en puerto {port}")
    system = IntegratedSystem(node_id=1, tcp_port=port)
    
    try:
        # Iniciar sistema
        if not system.start():
            pytest.fail("No se pudo iniciar sistema integrado")
        
        time.sleep(2.0)  # Dar tiempo para inicialización completa
        
        # Crear control sequences
        sequences = ControlSequences(
            gateway=system.gateway,
            simulator=system.simulator
        )
        
        # 1. Startup sequence
        logger.info("=" * 60)
        logger.info("PASO 1: Startup sequence")
        logger.info("=" * 60)
        
        result = sequences.startup_sequence()
        assert result == SequenceResult.SUCCESS, f"Startup falló: {result}"
        
        time.sleep(0.5)
        
        # Verificar estado
        state = system.simulator.get_state()
        logger.info(f"Estado después de startup: {state['device_state']}")
        assert state['device_state'] == 'OPERATION_ENABLED', f"Estado incorrecto: {state['device_state']}"
        
        # 2. Configurar velocidad con rampa
        logger.info("=" * 60)
        logger.info("PASO 2: Configurar velocidad 1500 RPM")
        logger.info("=" * 60)
        
        result = sequences.set_velocity_safe(
            target_velocity=1500,
            ramp_time=1.0
        )
        
        assert result == SequenceResult.SUCCESS, f"set_velocity_safe falló: {result}"
        
        time.sleep(0.5)  # Dar tiempo para procesamiento final
        
        # 3. Verificar velocidad
        state = system.simulator.get_state()
        logger.info("=" * 60)
        logger.info(f"✅ Velocidad target: {state['target_velocity']} RPM")
        logger.info(f"✅ Velocidad actual: {state['actual_velocity']} RPM")
        logger.info(f"✅ Estado: {state['device_state']}")
        logger.info("=" * 60)
        
        # ASSERTION CRÍTICA
        assert state['target_velocity'] == 1500, \
            f"Velocidad incorrecta: esperado=1500, actual={state['target_velocity']}"
        
        logger.info("🎉 TEST PASADO: Velocidad configurada correctamente con delay adaptativo")
        
    finally:
        # Cleanup
        logger.info("🛑 Deteniendo sistema")
        system.stop()
        time.sleep(0.5)


if __name__ == "__main__":
    test_sdo_velocity_with_delay()
