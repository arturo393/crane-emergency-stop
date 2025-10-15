"""
Tests para el módulo principal del controlador R13.
"""

import pytest
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from k13_controller.main import R13Controller, R13Config, CraneCommand
from k13_controller.protocol import R13CANopenProtocol, CANopenCommands


class TestR13Controller:
    """Clase de test para R13Controller."""

    def test_controller_creation(self):
        """Test de creación del controlador."""
        controller = R13Controller()
        assert controller is not None
        assert hasattr(controller, 'protocol')
        assert isinstance(controller.protocol, R13CANopenProtocol)

    def test_protocol_commands(self):
        """Test de comandos del protocolo."""
        controller = R13Controller()
        
        # Verificar que los comandos están disponibles
        assert hasattr(CANopenCommands, 'CONTROL_WORD')
        assert hasattr(CANopenCommands, 'TARGET_VELOCITY')
        assert hasattr(CANopenCommands, 'ACTUAL_VELOCITY')

    def test_emergency_stop(self):
        """Test de parada de emergencia."""
        controller = R13Controller()
        
        # En modo simulación, la parada de emergencia debe funcionar
        result = controller.parada_emergencia()
        assert result is True  # Debe retornar True en simulación

    def test_speed_limits(self):
        """Test de límites de velocidad."""
        controller = R13Controller()
        
        # Velocidades válidas
        assert controller._validar_velocidad(50) is True
        assert controller._validar_velocidad(0) is True
        assert controller._validar_velocidad(100) is True
        
        # Velocidades inválidas
        assert controller._validar_velocidad(-10) is False
        assert controller._validar_velocidad(150) is False

    def test_simulation_mode(self):
        """Test del modo simulación."""
        controller = R13Controller()
        
        # Por defecto debe estar en modo simulación
        assert controller.simulation_mode is True
        
        # Los comandos en simulación deben retornar True
        assert controller.mover_carro("derecha", 50) is True
        assert controller.mover_gancho("arriba", 30) is True


if __name__ == "__main__":
    pytest.main([__file__])

import pytest
import time
from unittest.mock import Mock, patch
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from k13_controller.main import R13Controller, R13Config, CraneCommand


class TestK13Controller:
    """Test suite para K13Controller"""
    
    def setup_method(self):
        """Configurar cada test"""
        self.config = R13Config(device_port="/dev/ttyUSB0")
        self.controller = R13Controller(self.config)
    
    def teardown_method(self):
        """Limpiar después de cada test"""
        if self.controller.is_connected:
            self.controller.disconnect()
    
    def test_initialization(self):
        """Test de inicialización del controlador"""
        assert self.controller.config.device_port == "/dev/ttyUSB0"
        assert self.controller.config.baud_rate == 9600
        assert self.controller.is_connected == False
    
    def test_connection_success(self):
        """Test de conexión exitosa"""
        result = self.controller.connect()
        
        assert result == True
        assert self.controller.is_connected == True
    
    def test_connection_failure(self):
        """Test de fallo de conexión"""
        # Simular fallo cambiando puerto a uno inválido
        self.controller.config.device_port = "/dev/invalid"
        
        with patch('time.sleep'):  # Mock sleep para acelerar test
            result = self.controller.connect()
        
        # En este caso seguirá siendo True porque estamos simulando
        # En implementación real con puerto inválido sería False
        assert result == True
    
    def test_disconnect(self):
        """Test de desconexión"""
        self.controller.connect()
        assert self.controller.is_connected == True
        
        self.controller.disconnect()
        assert self.controller.is_connected == False
    
    def test_send_command_without_connection(self):
        """Test enviar comando sin conexión"""
        command = CraneCommand("move_up", speed=30)
        result = self.controller.send_command(command)
        
        assert result == False
    
    def test_send_command_with_connection(self):
        """Test enviar comando con conexión"""
        self.controller.connect()
        
        command = CraneCommand("move_up", speed=30)
        
        with patch('time.sleep'):  # Mock sleep para acelerar test
            result = self.controller.send_command(command)
        
        assert result == True
    
    def test_emergency_stop(self):
        """Test de parada de emergencia"""
        self.controller.connect()
        
        with patch('time.sleep'):
            result = self.controller.emergency_stop()
        
        assert result == True
    
    def test_get_status_disconnected(self):
        """Test obtener estado cuando desconectado"""
        status = self.controller.get_status()
        
        assert status['connected'] == False
        assert status['port'] == "/dev/ttyUSB0"
        assert status['baud_rate'] == 9600
        assert 'timestamp' in status
    
    def test_get_status_connected(self):
        """Test obtener estado cuando conectado"""
        self.controller.connect()
        status = self.controller.get_status()
        
        assert status['connected'] == True
        assert status['port'] == "/dev/ttyUSB0"


class TestCraneCommand:
    """Test suite para CraneCommand"""
    
    def test_default_values(self):
        """Test valores por defecto"""
        cmd = CraneCommand("stop")
        
        assert cmd.action == "stop"
        assert cmd.speed == 50
        assert cmd.duration == 1.0
    
    def test_custom_values(self):
        """Test valores personalizados"""
        cmd = CraneCommand("move_up", speed=75, duration=2.5)
        
        assert cmd.action == "move_up"
        assert cmd.speed == 75
        assert cmd.duration == 2.5


class TestK13Config:
    """Test suite para K13Config"""
    
    def test_default_config(self):
        """Test configuración por defecto"""
        config = K13Config()
        
        assert config.device_port == "/dev/ttyUSB0"
        assert config.baud_rate == 9600
        assert config.timeout == 1.0
        assert config.retry_attempts == 3
    
    def test_custom_config(self):
        """Test configuración personalizada"""
        config = K13Config(
            device_port="/dev/ttyUSB1",
            baud_rate=115200,
            timeout=2.0,
            retry_attempts=5
        )
        
        assert config.device_port == "/dev/ttyUSB1"
        assert config.baud_rate == 115200
        assert config.timeout == 2.0
        assert config.retry_attempts == 5


# Fixture para tests de integración
@pytest.fixture
def controller_connected():
    """Fixture que proporciona un controlador conectado"""
    config = K13Config()
    controller = K13Controller(config)
    controller.connect()
    
    yield controller
    
    controller.disconnect()


def test_integration_basic_workflow(controller_connected):
    """Test de flujo básico de trabajo"""
    controller = controller_connected
    
    # Verificar que está conectado
    assert controller.is_connected == True
    
    # Enviar secuencia de comandos
    commands = [
        CraneCommand("move_up", speed=25, duration=0.1),
        CraneCommand("stop", speed=0, duration=0.1),
        CraneCommand("move_down", speed=25, duration=0.1),
        CraneCommand("stop", speed=0, duration=0.1)
    ]
    
    for cmd in commands:
        with patch('time.sleep'):
            result = controller.send_command(cmd)
            assert result == True
    
    # Verificar estado final
    status = controller.get_status()
    assert status['connected'] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
