# Guía Rápida - Desktop GUI K13 Puente Grúa

## 🚀 Inicio Rápido

### Método 1: Desde VS Code (Recomendado)
1. Presiona `Cmd+Shift+P` (macOS) o `Ctrl+Shift+P` (Windows/Linux)
2. Escribe "Run Task"
3. Selecciona **"Iniciar Desktop GUI"**
4. La ventana de la aplicación se abrirá automáticamente

### Método 2: Desde Terminal
```bash
cd /Users/arturo/puente_grua
source .venv/bin/activate
python scripts/launch_gui.py
```

### Método 3: Directo
```bash
cd /Users/arturo/puente_grua
source .venv/bin/activate
python src/web_ui/desktop_gui.py
```

---

## 🖥️ Interfaz de Usuario

La aplicación tiene **dos paneles principales**:

### Panel Izquierdo - Control y Monitoreo

#### 📊 Dashboard
- **Estado del Dispositivo**: Color-coded según estado CiA 402
  - 🟢 Verde: OPERATION_ENABLED (listo para operar)
  - 🔵 Azul: SWITCHED_ON (encendido pero no habilitado)
  - 🟠 Naranja: READY_TO_SWITCH_ON (listo para encender)
  - ⚪ Gris: SWITCH_ON_DISABLED (apagado)
  - 🔴 Rojo: FAULT (error/falla)

- **Status/Control Words**: Valores hexadecimales en tiempo real
- **Velocidad**: Objetivo vs Actual (RPM)
- **Posición**: Objetivo vs Actual (mm)
- **Estadísticas**: Tiempo operación, mensajes CAN, errores

#### 🎮 Panel de Control

**Emergency Stop** 🚨
- Botón rojo grande
- Detiene inmediatamente todo movimiento
- Transición a estado FAULT

**Arrancar Sistema** ▶️
- Ejecuta secuencia completa de startup
- Fases: READY_TO_SWITCH_ON → SWITCHED_ON → OPERATION_ENABLED
- Verifica estado en cada transición

**Apagar Sistema** ⏹️
- Shutdown ordenado
- Detiene movimientos antes de apagar
- Transición inversa segura

**Control de Velocidad**
- SpinBox: -3000 a +3000 RPM
- Botón "Aplicar Velocidad"
- Escribe directamente en objeto 0x6081

### Panel Derecho - Tabs

#### 📡 Monitor CAN
Tabla en tiempo real con:
- **Timestamp**: HH:MM:SS.mmm
- **COB-ID**: Identificador CAN (hex)
- **Tipo**: RPDO1, TPDO1, SDO Write, etc.
- **Datos**: Payload en hexadecimal
- **ASCII**: Interpretación texto (si aplica)

**Controles**:
- **Limpiar**: Borra todos los mensajes
- **Pausar/Reanudar**: Congela captura

**Límites**:
- Mantiene últimos 100 mensajes
- Auto-scroll to bottom
- Buffer circular

#### 📋 Logs
Registro de eventos con:
- Timestamps
- Niveles: INFO, WARNING, ERROR, SUCCESS
- Color coding automático

**Controles**:
- **Limpiar Log**: Borra todo el historial

---

## 🔧 Funcionalidades Avanzadas

### Threading Asíncrono
- **StatusUpdateThread** actualiza cada 500ms
- No bloquea la UI principal
- Usa señales Qt (thread-safe)

### Color Coding Automático
Estados del dispositivo:
```python
OPERATION_ENABLED   → Verde  (listo)
SWITCHED_ON         → Azul   (encendido)
READY_TO_SWITCH_ON  → Naranja (preparando)
SWITCH_ON_DISABLED  → Gris   (apagado)
FAULT               → Rojo   (error)
```

### Integración con IntegratedSystem
```python
# La GUI se conecta automáticamente
self.integrated_system = IntegratedSystem(node_id=1, tcp_port=9999)

# Inicia simulador + gateway
self.integrated_system.start()

# Obtiene estado cada 500ms
status = self.integrated_system.get_status()
```

---

## 🎯 Flujo de Trabajo Típico

### Sesión Normal de Operación
1. **Iniciar GUI** → Ventana se abre, sistema integrado arranca
2. **Verificar Dashboard** → Estado inicial: SWITCH_ON_DISABLED
3. **Arrancar Sistema** → Clic "▶️ Arrancar Sistema"
4. **Esperar transiciones** → Logs muestran progreso
5. **Verificar OPERATION_ENABLED** → Dashboard en verde ✅
6. **Configurar Velocidad** → SpinBox + "Aplicar Velocidad"
7. **Monitorear CAN** → Tab "Monitor CAN" muestra mensajes
8. **Apagar Sistema** → Clic "⏹️ Apagar Sistema" al terminar

### Debugging / Diagnóstico
1. **Iniciar GUI** con modo verbose
2. **Tab Logs** → Ver eventos detallados
3. **Tab Monitor CAN** → Analizar tráfico CAN
4. **Pausar captura** si necesita estudiar mensajes específicos
5. **Emergency Stop** si detecta comportamiento anómalo
6. **Revisar logs** para identificar problema

### Desarrollo / Testing
1. **GUI + Terminal** → Ver output de ambos
2. **Probar comandos** desde Control Panel
3. **Verificar respuestas** en Monitor CAN
4. **Logs automáticos** de éxito/error
5. **Iteración rápida** sin recompilar

---

## ⚙️ Configuración

### Puerto TCP del Gateway
Editar `src/web_ui/desktop_gui.py`:
```python
# Línea ~250
self.integrated_system = IntegratedSystem(
    node_id=1, 
    tcp_port=9999  # <-- Cambiar aquí
)
```

### Frecuencia de Actualización
Editar `desktop_gui.py`:
```python
# Línea ~35 en StatusUpdateThread.run()
time.sleep(0.5)  # <-- 500ms, cambiar a 0.1 para 100ms
```

### Node ID del K13 F
```python
# Línea ~250
self.integrated_system = IntegratedSystem(
    node_id=1,  # <-- ID del nodo CANopen
    tcp_port=9999
)
```

---

## 🐛 Troubleshooting

### Problema: Ventana no abre
**Solución**:
```bash
# Verificar instalación PyQt6
pip list | grep PyQt6

# Reinstalar si necesario
pip install --upgrade PyQt6
```

### Problema: "Address already in use"
**Solución**: Puerto 9999 ocupado
```bash
# Opción 1: Matar proceso
lsof -ti:9999 | xargs kill -9

# Opción 2: Cambiar puerto en código (ver Configuración)
```

### Problema: No actualiza estado
**Solución**: Thread no corriendo
- Verificar logs: "Sistema integrado iniciado" debe aparecer
- Revisar `StatusUpdateThread.start()` fue llamado
- Conectar señal `status_updated` al slot

### Problema: Monitor CAN vacío
**Causas posibles**:
1. **Captura pausada** → Clic "Reanudar"
2. **Sin comunicación CAN** → Verificar gateway activo
3. **Filtros activos** → (feature pendiente)

### Problema: Emergency Stop no responde
**Diagnóstico**:
```python
# Agregar print en on_emergency_stop()
def on_emergency_stop(self):
    print("DEBUG: Emergency stop clicked")  # <-- Debug
    # ... resto del código
```

---

## 📚 Código de Ejemplo

### Agregar Widget Personalizado
```python
class CustomWidget(QWidget):
    """Nuevo widget"""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Tu código aquí
        label = QLabel("Hola Mundo")
        layout.addWidget(label)

# En MainWindow.__init__():
self.custom_widget = CustomWidget()
left_layout.addWidget(self.custom_widget)
```

### Conectar Nueva Señal
```python
# En ControlPanelWidget
new_signal = pyqtSignal(str)

# En MainWindow.__init__()
self.control_panel.new_signal.connect(self.on_new_signal)

# Handler
def on_new_signal(self, data: str):
    self.log_widget.add_log(f"Recibido: {data}", "INFO")
```

### Agregar Comando al Control Panel
```python
# En ControlPanelWidget.__init__()
self.btn_custom = QPushButton("Mi Comando")
self.btn_custom.clicked.connect(self.custom_clicked.emit)
state_layout.addWidget(self.btn_custom)

# Señal
custom_clicked = pyqtSignal()

# En MainWindow
self.control_panel.custom_clicked.connect(self.on_custom_command)
```

---

## 🔮 Próximas Mejoras

### Versión 1.1 (Noviembre 2025)
- [ ] **PyQtGraph**: Gráficos históricos de velocidad/posición
- [ ] **QSettings**: Configuración persistente (puerto, node_id)
- [ ] **Temas**: Modo claro/oscuro
- [ ] **Exportar**: Logs a CSV/JSON
- [ ] **Filtros CAN**: Por COB-ID, tipo, datos

### Versión 1.2 (Diciembre 2025)
- [ ] **Grabación**: Capturar sesiones completas
- [ ] **Replay**: Reproducir grabaciones
- [ ] **Estadísticas**: Gráficos de performance
- [ ] **Atajos de teclado**: F1=Help, ESC=Emergency Stop
- [ ] **Multi-idioma**: Español/Inglés

### Versión 2.0 (2026 Q1)
- [ ] **Hardware real**: Integración con BL335 físico
- [ ] **CAN Analyzer**: Herramientas de diagnóstico avanzadas
- [ ] **Scripting**: Python REPL embebido
- [ ] **Plugins**: Sistema de extensiones
- [ ] **Network**: Acceso remoto seguro (SSH tunneling)

---

## 📖 Referencias

- **PyQt6 Docs**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **Qt Designer**: Para diseño visual de UI
- **CANopen CiA 402**: Estado del drive motor
- **IntegratedSystem**: `src/bl335_gateway/simulator_adapter.py`

---

**Última Actualización**: 24 de octubre de 2025  
**Versión GUI**: 1.0  
**Autor**: Arturo  
**Proyecto**: K13 Puente Grúa - Control CANopen
