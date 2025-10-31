"""
CANbus Monitor Desktop GUI con PyQt6
Interfaz de escritorio para monitoreo y control del K13 Puente Grúa
"""

import sys
import time
from datetime import datetime
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QTabWidget, QSpinBox, QStatusBar, QMessageBox, QHeaderView
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor

# Import sistema integrado
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.bl335_gateway.simulator_adapter import IntegratedSystem


class StatusUpdateThread(QThread):
    """Thread para actualizar estado sin bloquear la UI"""
    status_updated = pyqtSignal(dict)
    
    def __init__(self, integrated_system):
        super().__init__()
        self.integrated_system = integrated_system
        self.running = True
    
    def run(self):
        """Actualizar estado cada 500ms"""
        while self.running:
            try:
                if self.integrated_system:
                    status = self.integrated_system.get_status()
                    self.status_updated.emit(status)
            except Exception as e:
                print(f"Error en actualización: {e}")
            
            time.sleep(0.5)
    
    def stop(self):
        """Detener thread"""
        self.running = False


class CANMonitorWidget(QWidget):
    """Widget para monitorear mensajes CAN"""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Tabla de mensajes CAN
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Timestamp', 'COB-ID', 'Tipo', 'Datos', 'ASCII'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setMaximumHeight(300)
        
        layout.addWidget(QLabel("<b>📡 Monitor CAN Tiempo Real</b>"))
        layout.addWidget(self.table)
        
        # Controles
        controls = QHBoxLayout()
        self.btn_clear = QPushButton("Limpiar")
        self.btn_pause = QPushButton("Pausar")
        controls.addWidget(self.btn_clear)
        controls.addWidget(self.btn_pause)
        controls.addStretch()
        layout.addLayout(controls)
        
        # Estado
        self.paused = False
        self.btn_clear.clicked.connect(self.clear_messages)
        self.btn_pause.clicked.connect(self.toggle_pause)
    
    def add_message(self, cob_id, msg_type, data, timestamp=None):
        """Agregar mensaje CAN a la tabla"""
        if self.paused:
            return
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        row = self.table.rowCount()
        if row >= 100:  # Mantener últimos 100 mensajes
            self.table.removeRow(0)
            row = 99
        
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.table.setItem(row, 1, QTableWidgetItem(f"0x{cob_id:03X}"))
        self.table.setItem(row, 2, QTableWidgetItem(msg_type))
        self.table.setItem(row, 3, QTableWidgetItem(data))
        
        # ASCII (si es texto)
        try:
            ascii_data = bytes.fromhex(data.replace(" ", "")).decode('ascii', errors='ignore')
            self.table.setItem(row, 4, QTableWidgetItem(ascii_data))
        except:
            self.table.setItem(row, 4, QTableWidgetItem(""))
        
        # Scroll to bottom
        self.table.scrollToBottom()
    
    def clear_messages(self):
        """Limpiar todos los mensajes"""
        self.table.setRowCount(0)
    
    def toggle_pause(self):
        """Pausar/reanudar captura"""
        self.paused = not self.paused
        self.btn_pause.setText("Reanudar" if self.paused else "Pausar")


class DashboardWidget(QWidget):
    """Widget principal con estado del K13 F"""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Estado del dispositivo
        status_group = QGroupBox("Estado del Dispositivo K13 F")
        status_layout = QVBoxLayout()
        
        self.lbl_device_state = QLabel("Estado: DESCONOCIDO")
        self.lbl_device_state.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.lbl_device_state.setStyleSheet("color: gray;")
        
        self.lbl_status_word = QLabel("Status Word: 0x0000")
        self.lbl_control_word = QLabel("Control Word: 0x0000")
        
        status_layout.addWidget(self.lbl_device_state)
        status_layout.addWidget(self.lbl_status_word)
        status_layout.addWidget(self.lbl_control_word)
        status_group.setLayout(status_layout)
        
        # Velocidad y posición
        motion_group = QGroupBox("Movimiento")
        motion_layout = QVBoxLayout()
        
        self.lbl_velocity_target = QLabel("Velocidad Objetivo: 0 RPM")
        self.lbl_velocity_actual = QLabel("Velocidad Actual: 0 RPM")
        self.lbl_position_target = QLabel("Posición Objetivo: 0 mm")
        self.lbl_position_actual = QLabel("Posición Actual: 0 mm")
        
        motion_layout.addWidget(self.lbl_velocity_target)
        motion_layout.addWidget(self.lbl_velocity_actual)
        motion_layout.addWidget(self.lbl_position_target)
        motion_layout.addWidget(self.lbl_position_actual)
        motion_group.setLayout(motion_layout)
        
        # Estadísticas
        stats_group = QGroupBox("Estadísticas")
        stats_layout = QVBoxLayout()
        
        self.lbl_uptime = QLabel("Tiempo Operación: 0s")
        self.lbl_msg_count = QLabel("Mensajes CAN: 0")
        self.lbl_errors = QLabel("Errores: 0")
        
        stats_layout.addWidget(self.lbl_uptime)
        stats_layout.addWidget(self.lbl_msg_count)
        stats_layout.addWidget(self.lbl_errors)
        stats_group.setLayout(stats_layout)
        
        layout.addWidget(status_group)
        layout.addWidget(motion_group)
        layout.addWidget(stats_group)
        layout.addStretch()
    
    def update_status(self, status: dict):
        """Actualizar dashboard con nuevo estado"""
        if 'simulator' in status:
            sim = status['simulator']
            
            # Estado del dispositivo
            device_state = sim.get('device_state', 'UNKNOWN')
            self.lbl_device_state.setText(f"Estado: {device_state}")
            
            # Color según estado
            color_map = {
                'OPERATION_ENABLED': 'green',
                'SWITCHED_ON': 'blue',
                'READY_TO_SWITCH_ON': 'orange',
                'SWITCH_ON_DISABLED': 'gray',
                'FAULT': 'red'
            }
            self.lbl_device_state.setStyleSheet(f"color: {color_map.get(device_state, 'gray')};")
            
            # Status/Control Word
            self.lbl_status_word.setText(f"Status Word: {sim.get('status_word', '0x0000')}")
            self.lbl_control_word.setText(f"Control Word: {sim.get('control_word', '0x0000')}")
            
            # Velocidad y posición
            self.lbl_velocity_target.setText(f"Velocidad Objetivo: {sim.get('target_velocity', 0)} RPM")
            self.lbl_velocity_actual.setText(f"Velocidad Actual: {sim.get('actual_velocity', 0)} RPM")
            self.lbl_position_target.setText(f"Posición Objetivo: {sim.get('target_position', 0)} mm")
            self.lbl_position_actual.setText(f"Posición Actual: {sim.get('actual_position', 0)} mm")
            
            # Estadísticas
            if 'stats' in sim:
                stats = sim['stats']
                self.lbl_msg_count.setText(f"Mensajes CAN: {stats.get('total_messages', 0)}")


class ControlPanelWidget(QWidget):
    """Panel de control con comandos"""
    
    # Señales
    emergency_stop_clicked = pyqtSignal()
    startup_clicked = pyqtSignal()
    shutdown_clicked = pyqtSignal()
    set_velocity_clicked = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Comandos de estado
        state_group = QGroupBox("Control de Estado")
        state_layout = QVBoxLayout()
        
        self.btn_emergency = QPushButton("🚨 EMERGENCY STOP")
        self.btn_emergency.setStyleSheet("background-color: red; color: white; font-weight: bold; font-size: 14px;")
        self.btn_emergency.setMinimumHeight(50)
        self.btn_emergency.clicked.connect(self.emergency_stop_clicked.emit)
        
        self.btn_startup = QPushButton("▶️ Arrancar Sistema")
        self.btn_startup.clicked.connect(self.startup_clicked.emit)
        
        self.btn_shutdown = QPushButton("⏹️ Apagar Sistema")
        self.btn_shutdown.clicked.connect(self.shutdown_clicked.emit)
        
        state_layout.addWidget(self.btn_emergency)
        state_layout.addWidget(self.btn_startup)
        state_layout.addWidget(self.btn_shutdown)
        state_group.setLayout(state_layout)
        
        # Control de velocidad
        velocity_group = QGroupBox("Control de Velocidad")
        velocity_layout = QHBoxLayout()
        
        self.spin_velocity = QSpinBox()
        self.spin_velocity.setRange(-3000, 3000)
        self.spin_velocity.setSuffix(" RPM")
        self.spin_velocity.setValue(0)
        
        self.btn_set_velocity = QPushButton("Aplicar Velocidad")
        self.btn_set_velocity.clicked.connect(self._on_set_velocity)
        
        velocity_layout.addWidget(QLabel("Velocidad:"))
        velocity_layout.addWidget(self.spin_velocity)
        velocity_layout.addWidget(self.btn_set_velocity)
        velocity_group.setLayout(velocity_layout)
        
        layout.addWidget(state_group)
        layout.addWidget(velocity_group)
        layout.addStretch()
    
    def _on_set_velocity(self):
        """Emitir señal de velocidad"""
        velocity = self.spin_velocity.value()
        self.set_velocity_clicked.emit(velocity)


class LogWidget(QWidget):
    """Widget de logs y eventos"""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("<b>📋 Log de Eventos</b>"))
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        # Controles
        controls = QHBoxLayout()
        self.btn_clear_log = QPushButton("Limpiar Log")
        self.btn_clear_log.clicked.connect(self.clear_log)
        controls.addWidget(self.btn_clear_log)
        controls.addStretch()
        layout.addLayout(controls)
    
    def add_log(self, message: str, level: str = "INFO"):
        """Agregar entrada al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": "black",
            "WARNING": "orange",
            "ERROR": "red",
            "SUCCESS": "green"
        }
        color = color_map.get(level, "black")
        
        self.log_text.append(f'<span style="color:{color};">[{timestamp}] {level}: {message}</span>')
        
        # Scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def clear_log(self):
        """Limpiar log"""
        self.log_text.clear()


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("K13 Puente Grúa - CANbus Monitor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Sistema integrado
        self.integrated_system: Optional[IntegratedSystem] = None
        self.update_thread: Optional[StatusUpdateThread] = None
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Panel izquierdo - Dashboard y Control
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.dashboard = DashboardWidget()
        self.control_panel = ControlPanelWidget()
        
        left_layout.addWidget(self.dashboard)
        left_layout.addWidget(self.control_panel)
        
        # Panel derecho - Tabs
        right_panel = QTabWidget()
        
        self.can_monitor = CANMonitorWidget()
        self.log_widget = LogWidget()
        
        right_panel.addTab(self.can_monitor, "📡 Monitor CAN")
        right_panel.addTab(self.log_widget, "📋 Logs")
        
        # Layout principal
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)
        
        # Barra de estado
        self.statusBar().showMessage("Desconectado")
        
        # Conectar señales
        self.control_panel.emergency_stop_clicked.connect(self.on_emergency_stop)
        self.control_panel.startup_clicked.connect(self.on_startup)
        self.control_panel.shutdown_clicked.connect(self.on_shutdown)
        self.control_panel.set_velocity_clicked.connect(self.on_set_velocity)
        
        # Iniciar sistema
        self.init_system()
    
    def init_system(self):
        """Inicializar sistema integrado"""
        self.log_widget.add_log("Iniciando sistema integrado...", "INFO")
        
        try:
            self.integrated_system = IntegratedSystem(node_id=1, tcp_port=9999)
            
            if self.integrated_system.start():
                self.log_widget.add_log("✅ Sistema integrado iniciado", "SUCCESS")
                self.statusBar().showMessage("Conectado - Sistema integrado activo")
                
                # Iniciar thread de actualización
                self.update_thread = StatusUpdateThread(self.integrated_system)
                self.update_thread.status_updated.connect(self.on_status_update)
                self.update_thread.start()
                
                # Agregar mensaje CAN de ejemplo
                self.can_monitor.add_message(0x180, "TPDO1", "21 06 00 00 00 00 00 00")
            else:
                self.log_widget.add_log("❌ Error iniciando sistema", "ERROR")
                self.statusBar().showMessage("Error - No se pudo iniciar")
        
        except Exception as e:
            self.log_widget.add_log(f"❌ Error: {e}", "ERROR")
            self.statusBar().showMessage(f"Error: {e}")
    
    def on_status_update(self, status: dict):
        """Callback cuando se actualiza el estado"""
        self.dashboard.update_status(status)
    
    def on_emergency_stop(self):
        """Manejar emergency stop"""
        try:
            if self.integrated_system:
                result = self.integrated_system.gateway.emergency_stop()
                if result.get('status') == 'ok':
                    self.log_widget.add_log("🚨 EMERGENCY STOP activado", "WARNING")
                    self.can_monitor.add_message(0x201, "RPDO1", "00 00 00 00 00 00 00 00")
                else:
                    self.log_widget.add_log(f"Error: {result.get('message')}", "ERROR")
        except Exception as e:
            self.log_widget.add_log(f"Error en emergency stop: {e}", "ERROR")
    
    def on_startup(self):
        """Arrancar sistema"""
        try:
            self.log_widget.add_log("Ejecutando secuencia de arranque...", "INFO")
            
            if self.integrated_system:
                # Importar control sequences
                from src.k13_controller.control_sequences import ControlSequences, SequenceResult
                
                sequences = ControlSequences(
                    gateway=self.integrated_system.gateway,
                    simulator=self.integrated_system.simulator
                )
                
                result = sequences.startup_sequence()
                
                if result == SequenceResult.SUCCESS:
                    self.log_widget.add_log("✅ Sistema arrancado correctamente", "SUCCESS")
                    self.can_monitor.add_message(0x201, "RPDO1", "0F 00 00 00 00 00 00 00")
                else:
                    self.log_widget.add_log(f"❌ Error en arranque: {result}", "ERROR")
        
        except Exception as e:
            self.log_widget.add_log(f"Error: {e}", "ERROR")
    
    def on_shutdown(self):
        """Apagar sistema"""
        try:
            self.log_widget.add_log("Ejecutando shutdown...", "INFO")
            
            if self.integrated_system:
                from src.k13_controller.control_sequences import ControlSequences, SequenceResult
                
                sequences = ControlSequences(
                    gateway=self.integrated_system.gateway,
                    simulator=self.integrated_system.simulator
                )
                
                result = sequences.normal_shutdown()
                
                if result == SequenceResult.SUCCESS:
                    self.log_widget.add_log("✅ Sistema apagado correctamente", "SUCCESS")
                else:
                    self.log_widget.add_log(f"❌ Error en shutdown: {result}", "ERROR")
        
        except Exception as e:
            self.log_widget.add_log(f"Error: {e}", "ERROR")
    
    def on_set_velocity(self, velocity: int):
        """Configurar velocidad"""
        try:
            self.log_widget.add_log(f"Configurando velocidad: {velocity} RPM", "INFO")
            
            if self.integrated_system:
                result = self.integrated_system.gateway.sdo_write(0x6081, 0, velocity)
                
                if result.get('status') == 'ok':
                    self.log_widget.add_log(f"✅ Velocidad configurada: {velocity} RPM", "SUCCESS")
                    self.can_monitor.add_message(0x601, "SDO Write", f"6081 00 {velocity:04X}")
                else:
                    self.log_widget.add_log(f"❌ Error: {result.get('message')}", "ERROR")
        
        except Exception as e:
            self.log_widget.add_log(f"Error: {e}", "ERROR")
    
    def closeEvent(self, event):
        """Manejar cierre de la aplicación"""
        if self.update_thread:
            self.update_thread.stop()
            self.update_thread.wait()
        
        if self.integrated_system:
            self.log_widget.add_log("Deteniendo sistema...", "INFO")
            self.integrated_system.stop()
        
        event.accept()


def main():
    """Entry point"""
    app = QApplication(sys.argv)
    
    # Estilo
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
