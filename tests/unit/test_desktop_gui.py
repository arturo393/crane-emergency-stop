"""
Tests básicos para Desktop GUI
"""
import pytest
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import widgets
from src.web_ui.desktop_gui import (
    DashboardWidget,
    CANMonitorWidget,
    ControlPanelWidget,
    LogWidget,
    StatusUpdateThread
)


@pytest.fixture(scope="module")
def qapp():
    """QApplication fixture - requerido para tests de Qt"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # No llamar app.quit() aquí - puede causar problemas


class TestDashboardWidget:
    """Tests para DashboardWidget"""
    
    def test_widget_creation(self, qapp):
        """Verificar que el widget se puede crear"""
        widget = DashboardWidget()
        assert widget is not None
        assert widget.lbl_device_state is not None
        assert widget.lbl_status_word is not None
        assert widget.lbl_control_word is not None
    
    def test_update_status(self, qapp):
        """Verificar actualización de estado"""
        widget = DashboardWidget()
        
        status = {
            'simulator': {
                'device_state': 'OPERATION_ENABLED',
                'status_word': '0x0237',
                'control_word': '0x000F',
                'target_velocity': 1500,
                'actual_velocity': 1485,
                'target_position': 1000,
                'actual_position': 995,
                'stats': {
                    'total_messages': 42
                }
            }
        }
        
        widget.update_status(status)
        
        # Verificar texto actualizado
        assert 'OPERATION_ENABLED' in widget.lbl_device_state.text()
        assert '0x0237' in widget.lbl_status_word.text()
        assert '1500' in widget.lbl_velocity_target.text()


class TestCANMonitorWidget:
    """Tests para CANMonitorWidget"""
    
    def test_widget_creation(self, qapp):
        """Verificar creación del widget"""
        widget = CANMonitorWidget()
        assert widget is not None
        assert widget.table is not None
        assert widget.btn_clear is not None
        assert widget.btn_pause is not None
    
    def test_add_message(self, qapp):
        """Verificar adición de mensajes"""
        widget = CANMonitorWidget()
        
        # Agregar mensaje
        widget.add_message(0x180, "TPDO1", "21 06 00 00 00 00 00 00")
        
        # Verificar fila agregada
        assert widget.table.rowCount() == 1
        assert '0x180' in widget.table.item(0, 1).text()
        assert 'TPDO1' in widget.table.item(0, 2).text()
    
    def test_pause_resume(self, qapp):
        """Verificar pausar/reanudar"""
        widget = CANMonitorWidget()
        
        # Estado inicial
        assert widget.paused is False
        
        # Pausar
        widget.toggle_pause()
        assert widget.paused is True
        assert 'Reanudar' in widget.btn_pause.text()
        
        # Reanudar
        widget.toggle_pause()
        assert widget.paused is False
        assert 'Pausar' in widget.btn_pause.text()
    
    def test_clear_messages(self, qapp):
        """Verificar limpiar mensajes"""
        widget = CANMonitorWidget()
        
        # Agregar algunos mensajes
        for i in range(5):
            widget.add_message(0x200 + i, "SDO", "00 00 00 00")
        
        assert widget.table.rowCount() == 5
        
        # Limpiar
        widget.clear_messages()
        assert widget.table.rowCount() == 0
    
    def test_buffer_limit(self, qapp):
        """Verificar límite de 100 mensajes"""
        widget = CANMonitorWidget()
        
        # Agregar 150 mensajes
        for i in range(150):
            widget.add_message(0x100, "TEST", f"{i:02X} 00 00 00")
        
        # Debe mantener solo 100
        assert widget.table.rowCount() == 100


class TestControlPanelWidget:
    """Tests para ControlPanelWidget"""
    
    def test_widget_creation(self, qapp):
        """Verificar creación"""
        widget = ControlPanelWidget()
        assert widget is not None
        assert widget.btn_emergency is not None
        assert widget.btn_startup is not None
        assert widget.btn_shutdown is not None
        assert widget.spin_velocity is not None
    
    def test_velocity_range(self, qapp):
        """Verificar rango de velocidad"""
        widget = ControlPanelWidget()
        
        # Verificar rango -3000 a 3000
        assert widget.spin_velocity.minimum() == -3000
        assert widget.spin_velocity.maximum() == 3000
        assert widget.spin_velocity.value() == 0  # Valor inicial
    
    def test_signals_exist(self, qapp):
        """Verificar que las señales existen"""
        widget = ControlPanelWidget()
        
        # Verificar señales definidas
        assert hasattr(widget, 'emergency_stop_clicked')
        assert hasattr(widget, 'startup_clicked')
        assert hasattr(widget, 'shutdown_clicked')
        assert hasattr(widget, 'set_velocity_clicked')


class TestLogWidget:
    """Tests para LogWidget"""
    
    def test_widget_creation(self, qapp):
        """Verificar creación"""
        widget = LogWidget()
        assert widget is not None
        assert widget.log_text is not None
        assert widget.btn_clear_log is not None
    
    def test_add_log(self, qapp):
        """Verificar agregar log"""
        widget = LogWidget()
        
        # Agregar logs de diferentes niveles
        widget.add_log("Test info", "INFO")
        widget.add_log("Test warning", "WARNING")
        widget.add_log("Test error", "ERROR")
        widget.add_log("Test success", "SUCCESS")
        
        # Verificar que se agregaron
        text = widget.log_text.toPlainText()
        assert "Test info" in text
        assert "Test warning" in text
        assert "Test error" in text
        assert "Test success" in text
        assert "INFO" in text
        assert "WARNING" in text
    
    def test_clear_log(self, qapp):
        """Verificar limpiar log"""
        widget = LogWidget()
        
        # Agregar logs
        for i in range(10):
            widget.add_log(f"Message {i}", "INFO")
        
        # Verificar que hay contenido
        assert len(widget.log_text.toPlainText()) > 0
        
        # Limpiar
        widget.clear_log()
        assert len(widget.log_text.toPlainText()) == 0


class TestStatusUpdateThread:
    """Tests para StatusUpdateThread"""
    
    def test_thread_creation(self, qapp):
        """Verificar creación del thread"""
        # Mock IntegratedSystem simple
        class MockSystem:
            def get_status(self):
                return {'simulator': {'device_state': 'TEST'}}
        
        mock_system = MockSystem()
        thread = StatusUpdateThread(mock_system)
        
        assert thread is not None
        assert thread.integrated_system is mock_system
        assert thread.running is True
    
    def test_thread_stop(self, qapp):
        """Verificar detener thread"""
        class MockSystem:
            def get_status(self):
                return {}
        
        thread = StatusUpdateThread(MockSystem())
        thread.stop()
        
        assert thread.running is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
