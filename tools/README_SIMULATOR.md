# Simulador CANopen R13 F

## 📋 Descripción

Simulador completo del dispositivo Danfoss R13 F (receptor de radio control para puente grúa) que implementa el protocolo CANopen con perfil CiA 402 (Motion Control).

Este simulador permite desarrollar y probar el sistema de control sin necesidad del hardware físico, simulando todas las características del dispositivo real.

## ✨ Características Implementadas

### 🔄 Máquina de Estados CiA 402

Implementa completamente la máquina de estados estándar:
- **SWITCH_ON_DISABLED**: Estado inicial después de power-on
- **READY_TO_SWITCH_ON**: Listo para encendido
- **SWITCHED_ON**: Encendido, listo para operación
- **OPERATION_ENABLED**: Operación activa
- **QUICK_STOP_ACTIVE**: Parada de emergencia
- **FAULT**: Estado de error

### 📚 Object Dictionary

Implementa objetos estándar CiA 301 y CiA 402:

#### Objetos CiA 301 (Comunicación)
- `0x1000`: Device Type
- `0x1001`: Error Register
- `0x1017`: Producer Heartbeat Time
- `0x1018`: Identity Object (Vendor ID, Product Code, etc.)

#### Objetos CiA 402 (Control de Movimiento)
- `0x6040`: Control Word - Control del dispositivo
- `0x6041`: Status Word - Estado del dispositivo
- `0x6060`: Modes of Operation - Modo actual
- `0x6061`: Modes of Operation Display
- `0x6081`: Profile Velocity - Velocidad objetivo
- `0x6083`: Profile Acceleration
- `0x6084`: Profile Deceleration
- `0x6063`: Position Actual Value
- `0x6064`: Velocity Actual Value

### 📡 Comunicación CANopen

#### SDO (Service Data Object)
- **Upload**: Lectura de objetos del diccionario
- **Download**: Escritura de objetos del diccionario
- Soporte para objetos de 8, 16 y 32 bits

#### PDO (Process Data Object)

**RPDO1** (Receive, COB-ID: 0x200 + Node ID):
- Bytes 0-1: Control Word
- Bytes 2-5: Target Velocity (opcional)

**TPDO1** (Transmit, COB-ID: 0x180 + Node ID, cada 100ms):
- Bytes 0-1: Status Word
- Bytes 2-5: Actual Velocity
- Bytes 6-7: Actual Position (parcial)

**TPDO2** (Transmit, COB-ID: 0x280 + Node ID, cada 200ms):
- Byte 0: Operation Mode
- Bytes 1-2: Error Code
- Byte 3: Temperature (simulado)

### 🎮 Simulación Física

- **Aceleración y desaceleración**: Simulación realista de cambios de velocidad
- **Control de posición**: Tracking de posición basado en velocidad
- **Límites**: Velocidad máxima, aceleración máxima
- **Temperatura**: Simulación de temperatura del dispositivo

### 🚨 Manejo de Emergencias

- **Emergency Stop**: Parada inmediata con publicación de EMCY
- **Fault Handling**: Detección y recuperación de faults
- **Quick Stop**: Parada controlada según CiA 402

## 🚀 Uso

### Inicialización Básica

```python
from tools.can_simulator import R13FSimulator

# Crear simulador (en modo batch para tests)
simulator = R13FSimulator(
    node_id=1,
    channel='vcan0',
    batch_mode=True  # True para tests sin bus CAN real
)

# Iniciar simulador
simulator.start()

# Obtener estado
state = simulator.get_state()
print(f"Estado: {state['device_state']}")
print(f"Velocidad: {state['actual_velocity']} RPM")
```

### Control de Estados

```python
# Transición: SWITCH_ON_DISABLED -> READY_TO_SWITCH_ON
simulator._process_control_word(0x0007)  # Switch On + Enable Voltage

# Transición a OPERATION_ENABLED
simulator._process_control_word(0x000F)  # + Enable Operation

# Parada de emergencia
simulator._process_control_word(0x0006)  # Quick Stop
```

### Control Words Estándar

| Control Word | Bits | Descripción | Transición |
|--------------|------|-------------|------------|
| `0x0006` | `0110` | Shutdown | → READY_TO_SWITCH_ON |
| `0x0007` | `0111` | Switch On | → READY_TO_SWITCH_ON |
| `0x000F` | `1111` | Enable Operation | → OPERATION_ENABLED |
| `0x0006` | `0110` | Quick Stop (sin bit 0) | → QUICK_STOP_ACTIVE |
| `0x0086` | `1000 0110` | Fault Reset | FAULT → SWITCH_ON_DISABLED |

Bits del Control Word:
- Bit 0: Switch On
- Bit 1: Enable Voltage  
- Bit 2: Quick Stop
- Bit 3: Enable Operation
- Bit 7: Fault Reset

### Operaciones SDO

```python
# Leer objeto (ejemplo: velocidad objetivo)
value = simulator.object_dictionary[0x6081]['value']

# Escribir objeto (ejemplo: cambiar velocidad)
simulator._handle_sdo_download(0x6081, 0, 1500)  # 1500 RPM
```

## 🧪 Suite de Tests

Incluye suite completa de tests en `test_simulator.py`:

```bash
python test_simulator.py
```

Tests implementados:
1. ✅ **Inicialización**: Verificar creación correcta
2. ✅ **Transiciones de Estado**: Validar máquina CiA 402
3. ✅ **Object Dictionary**: Verificar estructura y valores
4. ✅ **Operaciones SDO**: Validar lectura/escritura
5. ✅ **Configuración PDO**: Verificar COB-IDs y mappings
6. ✅ **Manejo de Faults**: Probar fault injection y recovery
7. ✅ **Emergency Stop**: Validar parada de emergencia
8. ✅ **Simulación Física**: Verificar cambios de velocidad

## 📊 Estadísticas y Monitoreo

El simulador mantiene estadísticas de operación:

```python
state = simulator.get_state()
stats = state['stats']

print(f"Heartbeats enviados: {stats['heartbeats_sent']}")
print(f"PDOs enviados: {stats['pdo_sent']}")
print(f"SDO requests: {stats['sdo_requests']}")
print(f"Paradas de emergencia: {stats['emergency_stops']}")
print(f"Errores: {stats['errors']}")
```

## 🔧 Configuración

### Parámetros del Constructor

```python
R13FSimulator(
    node_id=1,              # ID del nodo CANopen (1-127)
    channel='vcan0',        # Canal CAN (vcan0 para virtual)
    batch_mode=False,       # True para tests sin bus real
    heartbeat_time=1000,    # Intervalo de heartbeat (ms)
    max_velocity=3000,      # Velocidad máxima (RPM)
    max_acceleration=1000   # Aceleración máxima (RPM/s)
)
```

### Modos de Operación

Actualmente implementado:
- **PROFILE_VELOCITY** (0x03): Control de velocidad con perfil

Futuros modos (planificados):
- PROFILE_POSITION (0x01)
- HOMING (0x06)
- CYCLIC_SYNC_VELOCITY (0x09)

## 🐛 Debugging

El simulador incluye logging configurable:

```python
import logging

# Activar debug logging
logging.basicConfig(level=logging.DEBUG)

# Crear simulador (desactivar batch_mode para ver mensajes)
simulator = R13FSimulator(node_id=1, batch_mode=False)
```

## 📚 Referencias

- **CiA 301**: CANopen Application Layer and Communication Profile
- **CiA 402**: CANopen Device Profile for Drives and Motion Control
- **Danfoss R13 F**: Manual técnico del receptor de radio control
- **Python-can**: Documentación de la biblioteca python-can

## 🎯 Casos de Uso

### 1. Desarrollo sin Hardware
```python
# Desarrollar lógica de control sin dispositivo físico
simulator = R13FSimulator(node_id=1, batch_mode=True)
simulator.start()

# Tu código de control aquí...
# Probar diferentes secuencias de control
# Validar respuestas esperadas
```

### 2. Pruebas Automatizadas
```python
# Integrar en suite de tests
def test_control_sequence():
    sim = R13FSimulator(node_id=1, batch_mode=True)
    sim.start()
    
    # Probar secuencia específica
    sim._process_control_word(0x0007)
    assert sim.get_state()['device_state'] == 'READY_TO_SWITCH_ON'
    
    sim.stop()
```

### 3. Entrenamiento y Demostración
```python
# Demostrar comportamiento del sistema
simulator = R13FSimulator(node_id=1, batch_mode=False)
simulator.start()

# Mostrar transiciones de estado en tiempo real
# Simular diferentes escenarios operacionales
```

## 🔜 Próximos Pasos

- [ ] Añadir más modos de operación (Position, Homing)
- [ ] Implementar límites de carrera (limit switches)
- [ ] Simular cargas mecánicas variables
- [ ] GUI para visualización en tiempo real
- [ ] Integración con hardware real (transición simulador↔real)
- [ ] Grabación y replay de secuencias

## 📝 Notas

- El simulador usa threading para PDO/heartbeat periódicos
- En `batch_mode=True`, no se requiere interfaz CAN real
- Los valores físicos son aproximados pero realistas
- Estado thread-safe con locks para acceso concurrente

## 🤝 Contribución

Para mejorar el simulador:
1. Fork del proyecto
2. Crear feature branch
3. Implementar mejora con tests
4. Abrir pull request

---

**Versión**: 1.0.0  
**Autor**: Sistema de Control K13 Puente Grúa  
**Fecha**: Octubre 2025
