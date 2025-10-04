"""
Test simple para verificar que el proyecto funciona básicamente.
"""

import pytest
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from k13_controller.main import R13Controller, R13Config
from k13_controller.protocol import R13CANopenProtocol, CANopenCommands


class TestBasicFunctionality:
    """Tests básicos del proyecto."""

    def test_imports_work(self):
        """Test que las importaciones funcionan."""
        assert R13Controller is not None
        assert R13Config is not None
        assert R13CANopenProtocol is not None
        assert CANopenCommands is not None

    def test_controller_creation(self):
        """Test creación del controlador."""
        controller = R13Controller()
        assert controller is not None
        assert hasattr(controller, 'config')
        assert hasattr(controller, 'protocol')

    def test_protocol_creation(self):
        """Test creación del protocolo."""
        protocol = R13CANopenProtocol(node_id=1)
        assert protocol is not None
        assert protocol.node_id == 1

    def test_canopen_commands_exist(self):
        """Test que los comandos CANopen existen."""
        assert hasattr(CANopenCommands, 'ENABLE_OPERATION')
        assert hasattr(CANopenCommands, 'SHUTDOWN')
        assert hasattr(CANopenCommands, 'QUICK_STOP')

    def test_basic_controller_methods(self):
        """Test métodos básicos del controlador."""
        controller = R13Controller()
        
        # Verificar que los métodos existen
        assert hasattr(controller, 'emergency_stop')
        assert hasattr(controller, 'is_connected')
        assert hasattr(controller, 'get_status')
        assert hasattr(controller, 'connect')
        assert hasattr(controller, 'disconnect')

    def test_controller_initial_state(self):
        """Test estado inicial del controlador."""
        controller = R13Controller()
        # Debe estar desconectado inicialmente
        assert controller.is_connected is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
