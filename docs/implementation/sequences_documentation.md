# Secuencias de Control Complejas

## Descripción General

La biblioteca de secuencias de control (`control_sequences.py`) proporciona operaciones de alto nivel para el control del puente grúa, abstrayendo la complejidad del protocolo CANopen y la máquina de estados CiA 402.

## Arquitectura

```
┌─────────────────────┐
│  Usuario/Aplicación │
│   (Web UI, CLI)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ ControlSequences    │  ◄── Esta biblioteca
│  - startup()        │
│  - shutdown()       │
│  - set_velocity()   │
│  - move_to_pos()    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   BL335 Gateway     │
│  (TCP/IP ↔ CAN)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  R13 F Simulator/   │
│  Hardware Real      │
└─────────────────────┘
```

## Clase ControlSequences

### Inicialización

```python
from src.k13_controller.control_sequences import ControlSequences
from src.bl335_gateway.main import BL335Gateway

gateway = BL335Gateway(node_id=1, tcp_port=9999)
sequences = ControlSequences(gateway=gateway, simulator=None)
```

### Parámetros

- **gateway**: Instancia del BL335Gateway para comunicación
- **simulator**: Opcional, instancia del R13FSimulator para verificación directa

## Secuencias Disponibles

### 1. startup_sequence()

Arranque seguro del sistema con transiciones completas de estados.

**Flujo:**
1. Verificar estado inicial
2. Transición a `READY_TO_SWITCH_ON` (Control Word = 0x0006)
3. Transición a `SWITCHED_ON` (Control Word = 0x0007)
4. Transición a `OPERATION_ENABLED` (Control Word = 0x000F)

**Uso:**

```python
result = sequences.startup_sequence()

if result == SequenceResult.SUCCESS:
    print("✅ Sistema arrancado correctamente")
else:
    print(f"❌ Error en arranque: {result}")
```

**Retorna:**
- `SequenceResult.SUCCESS`: Arranque exitoso
- `SequenceResult.FAILED`: Error durante arranque
- `SequenceResult.TIMEOUT`: Timeout en transición de estado

**Ejemplo de salida:**

```
============================================================
🚀 SECUENCIA DE ARRANQUE
============================================================
Paso 1/4: Verificando estado inicial...
  Estado inicial: NOT_READY_TO_SWITCH_ON
Paso 2/4: Transición a READY_TO_SWITCH_ON...
  ✅ En READY_TO_SWITCH_ON
Paso 3/4: Transición a SWITCHED_ON...
  ✅ En SWITCHED_ON
Paso 4/4: Transición a OPERATION_ENABLED...
  ✅ En OPERATION_ENABLED
============================================================
✅ SECUENCIA DE ARRANQUE COMPLETADA
============================================================
```

---

### 2. shutdown_sequence(emergency=False)

Parada del sistema, normal o de emergencia.

**Parámetros:**
- **emergency** (bool): 
  - `False`: Parada normal (desactivar operación)
  - `True`: Parada de emergencia (Quick Stop)

**Uso:**

```python
# Parada normal
result = sequences.shutdown_sequence(emergency=False)

# Parada de emergencia
result = sequences.shutdown_sequence(emergency=True)
```

**Retorna:**
- `SequenceResult.SUCCESS`: Parada exitosa
- `SequenceResult.FAILED`: Error durante parada

**Ejemplo de salida:**

```
============================================================
🛑 SECUENCIA DE PARADA (EMERGENCIA)
============================================================
Estado actual: OPERATION_ENABLED
Ejecutando Quick Stop...
  ✅ Parada de emergencia ejecutada
============================================================
✅ SECUENCIA DE PARADA COMPLETADA
============================================================
```

---

### 3. set_velocity_safe(target_velocity, ramp_time=1.0)

Configurar velocidad con rampa suave para evitar movimientos bruscos.

**Parámetros:**
- **target_velocity** (int): Velocidad objetivo en RPM
- **ramp_time** (float): Tiempo de rampa en segundos (default: 1.0)

**Características:**
- Calcula automáticamente pasos intermedios
- Mínimo 10 pasos para suavidad
- Aborable mediante `sequences.abort()`

**Uso:**

```python
# Rampa de 0 a 1500 RPM en 2 segundos
result = sequences.set_velocity_safe(
    target_velocity=1500,
    ramp_time=2.0
)
```

**Retorna:**
- `SequenceResult.SUCCESS`: Velocidad configurada
- `SequenceResult.FAILED`: Error (estado incorrecto, comunicación fallida)
- `SequenceResult.ABORTED`: Usuario abortó la operación

**Ejemplo de salida:**

```
============================================================
⚡ CONFIGURANDO VELOCIDAD: 1500 RPM
============================================================
Velocidad actual: 0 RPM
Velocidad objetivo: 1500 RPM
Rampa: 15 pasos de 100.0 RPM cada 0.133s
  Paso 1/16: 0 RPM
  Paso 2/16: 100 RPM
  ...
  Paso 16/16: 1500 RPM
  ✅ Velocidad configurada: 1500 RPM
============================================================
```

---

### 4. move_to_position(target_position, velocity=1000)

Mover a una posición específica.

**Parámetros:**
- **target_position** (int): Posición objetivo en mm
- **velocity** (int): Velocidad de movimiento en RPM (default: 1000)

**Características:**
- Monitoreo continuo de posición actual
- Tolerancia de ±10 mm
- Timeout de 30 segundos

**Uso:**

```python
# Mover a 5000 mm a 1500 RPM
result = sequences.move_to_position(
    target_position=5000,
    velocity=1500
)
```

**Retorna:**
- `SequenceResult.SUCCESS`: Posición alcanzada
- `SequenceResult.FAILED`: Error (estado incorrecto, comunicación fallida)
- `SequenceResult.TIMEOUT`: No se alcanzó posición en 30s
- `SequenceResult.ABORTED`: Usuario abortó el movimiento

**Ejemplo de salida:**

```
============================================================
📍 MOVIMIENTO A POSICIÓN: 5000 mm
============================================================
Estado actual: OPERATION_ENABLED
Configurando velocidad: 1500 RPM...
Configurando posición objetivo: 5000 mm...
Moviendo a posición...
  Posición actual: 1234 mm (faltan 3766 mm)
  Posición actual: 2456 mm (faltan 2544 mm)
  ...
  ✅ Posición alcanzada: 5001 mm
============================================================
```

---

## Métodos Auxiliares

### get_device_state()

Obtiene el estado actual del dispositivo.

**Retorna:** String con el estado (`OPERATION_ENABLED`, `SWITCHED_ON`, etc.)

```python
state = sequences.get_device_state()
print(f"Estado: {state}")
```

---

### wait_for_state(target_state, timeout=5.0)

Espera hasta que el dispositivo alcance un estado específico.

**Parámetros:**
- **target_state** (str): Estado objetivo
- **timeout** (float): Tiempo máximo de espera en segundos

**Retorna:** `True` si alcanzó el estado, `False` si timeout o abort

```python
if sequences.wait_for_state('OPERATION_ENABLED', timeout=3.0):
    print("Estado alcanzado")
else:
    print("Timeout o abort")
```

---

### abort()

Aborta la secuencia en ejecución actual.

```python
# En otro thread o callback
sequences.abort()
```

---

### reset_abort()

Resetea el flag de abort para permitir nuevas operaciones.

```python
sequences.reset_abort()
```

---

## Enum SequenceResult

Resultados posibles de las secuencias:

```python
class SequenceResult(Enum):
    SUCCESS = "success"    # Operación exitosa
    FAILED = "failed"      # Error durante operación
    TIMEOUT = "timeout"    # Timeout esperando condición
    ABORTED = "aborted"    # Usuario abortó operación
```

---

## Ejemplos de Uso

### Ejemplo 1: Ciclo Completo de Operación

```python
from src.k13_controller.control_sequences import ControlSequences, SequenceResult
from src.bl335_gateway.simulator_adapter import IntegratedSystem

# Iniciar sistema
system = IntegratedSystem(node_id=1, tcp_port=9999)
system.start()

# Crear secuencias
sequences = ControlSequences(
    gateway=system.gateway,
    simulator=system.simulator
)

# 1. Arrancar
if sequences.startup_sequence() == SequenceResult.SUCCESS:
    print("✅ Sistema arrancado")
    
    # 2. Configurar velocidad
    if sequences.set_velocity_safe(2000, ramp_time=2.0) == SequenceResult.SUCCESS:
        print("✅ Velocidad configurada")
        
        # 3. Operar durante 5 segundos
        time.sleep(5.0)
        
        # 4. Parar normalmente
        sequences.shutdown_sequence(emergency=False)
        print("✅ Sistema detenido")

system.stop()
```

---

### Ejemplo 2: Parada de Emergencia

```python
import threading
import time

# Arrancar y configurar velocidad
sequences.startup_sequence()
sequences.set_velocity_safe(3000)

# Simular operación
def emergency_after_3s():
    time.sleep(3.0)
    print("🚨 EMERGENCIA DETECTADA")
    sequences.shutdown_sequence(emergency=True)

emergency_thread = threading.Thread(target=emergency_after_3s)
emergency_thread.start()

# Operación continua...
time.sleep(10.0)

emergency_thread.join()
```

---

### Ejemplo 3: Múltiples Cambios de Velocidad

```python
sequences.startup_sequence()

velocities = [500, 1000, 1500, 2000, 1000, 0]

for vel in velocities:
    print(f"Cambiando a {vel} RPM...")
    result = sequences.set_velocity_safe(vel, ramp_time=1.0)
    
    if result != SequenceResult.SUCCESS:
        print(f"❌ Error configurando velocidad: {result}")
        break
    
    time.sleep(2.0)  # Operar 2s a cada velocidad

sequences.shutdown_sequence()
```

---

## Ejecución de Demo

El módulo incluye una función de demostración completa:

```bash
# Ejecutar demo
python src/k13_controller/control_sequences.py
```

**Demo incluye:**
1. Secuencia de arranque
2. Rampa de velocidad (0 → 1500 RPM)
3. Parada normal
4. Re-arranque y parada de emergencia

---

## Tests

Tests unitarios completos en `tests/unit/test_control_sequences.py`:

```bash
# Ejecutar todos los tests
pytest tests/unit/test_control_sequences.py -v

# Ejecutar test específico
pytest tests/unit/test_control_sequences.py::TestBasicSequences::test_startup_sequence -v
```

**Cobertura de tests:**
- ✅ Secuencias básicas (3 tests)
- ✅ Secuencias de velocidad (3 tests)
- ✅ Wait for state (3 tests)
- ✅ Secuencias complejas (3 tests)
- ✅ Transiciones de estado (2 tests)
- ✅ Manejo de errores (2 tests)

**Total: 16 tests + 12 tests adicionales en clases auxiliares**

---

## Logging

El módulo utiliza logging de Python para trazabilidad:

```python
import logging

# Configurar nivel de logging
logging.basicConfig(level=logging.INFO)  # INFO, DEBUG, WARNING

# Los mensajes se mostrarán en consola
```

**Niveles de log:**
- **DEBUG**: Detalles de cada paso (posición actual, estados intermedios)
- **INFO**: Progreso de secuencias (pasos, transiciones)
- **WARNING**: Situaciones anormales (timeouts, aborts)
- **ERROR**: Errores críticos (fallas de comunicación, estados inválidos)

---

## Consideraciones de Seguridad

1. **Verificación de Estados**: Todas las secuencias verifican que el dispositivo esté en el estado correcto antes de operar.

2. **Timeouts**: Todas las operaciones tienen timeouts para evitar bloqueos infinitos.

3. **Abort Mechanism**: Sistema de abort permite interrumpir operaciones de forma segura.

4. **Rampas de Velocidad**: Cambios suaves de velocidad evitan movimientos bruscos.

5. **Parada de Emergencia**: Comando de alta prioridad disponible en todo momento.

---

## Integración con Web UI

Las secuencias pueden ser invocadas desde la Web UI:

```python
# En src/web_ui/main.py
from src.k13_controller.control_sequences import ControlSequences

sequences = ControlSequences(gateway=app.gateway)

@app.post("/api/startup")
async def startup():
    result = sequences.startup_sequence()
    return {"status": result.value}

@app.post("/api/set-velocity")
async def set_velocity(velocity: int):
    result = sequences.set_velocity_safe(velocity)
    return {"status": result.value}
```

---

## Próximos Pasos

1. **Secuencias Compuestas**:
   - Cargar carga + mover + descargar
   - Secuencias de mantenimiento
   - Rutinas de calibración

2. **Perfiles de Movimiento**:
   - Perfiles trapezoidales
   - Perfiles S-curve
   - Perfiles personalizados

3. **Integración con Sensores**:
   - Detección de límites
   - Sensores de carga
   - Protecciones adicionales

---

**Fecha**: 8 de septiembre de 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Completado
