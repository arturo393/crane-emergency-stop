# Archivo EDS - Danfoss R13 F CANopen Receiver

## 📋 Información General

Este archivo EDS (Electronic Data Sheet) define el **Object Dictionary** completo para el receptor Danfoss R13 F, permitiendo comunicación CANopen estándar según:

- **CiA 301 v4.2.0**: Application layer and communication profile
- **CiA 402 v3.3**: CANopen device profile for drives and motion control

## 🔧 Características Implementadas

### Información del Dispositivo
- **Vendor ID**: 0x57 (Danfoss)
- **Product Code**: 0x00130001 (R13 F)
- **Baud Rates soportados**: 10, 20, 50, 125, 250, 500, 1000 kbps
- **LSS**: Layer Setting Services habilitado

### Objetos Obligatorios CiA 301

| Índice | Objeto | Descripción |
|--------|--------|-------------|
| 0x1000 | Device Type | Tipo de dispositivo (0x00020192 = Drive) |
| 0x1001 | Error Register | Registro de errores |
| 0x1018 | Identity Object | Identidad (Vendor, Product, Revision, Serial) |

### Objetos Opcionales CiA 301

| Índice | Objeto | Descripción | Valor Default |
|--------|--------|-------------|---------------|
| 0x1005 | COB-ID SYNC | ID de sincronización | 0x80 |
| 0x1008 | Device Name | Nombre del dispositivo | "Danfoss R13 F" |
| 0x1009 | Hardware Version | Versión de hardware | "1.0" |
| 0x100A | Software Version | Versión de software | "1.0.0" |
| 0x1014 | COB-ID EMCY | ID de emergencia | NodeID+0x80 |
| 0x1017 | Heartbeat Time | Período de heartbeat | 500 ms |

## 📡 Configuración PDO

### RPDO1 (Receive PDO 1) - Comandos de Control

**COB-ID**: `NodeID + 0x200` (ej: 0x201 para NodeID=1)

**Mapeo**:
1. **Control Word (0x6040)**: 16 bits - Palabra de control CiA 402
2. **Modes of Operation (0x6060)**: 8 bits - Modo de operación

**Uso**: Enviar comandos al R13 F en tiempo real

```python
# Ejemplo: Enviar Control Word
rpdo1_data = [
    0x06, 0x00,  # Control Word: Enable Operation (0x0006)
    0x03,        # Mode: Profile Velocity
    0x00, 0x00, 0x00, 0x00, 0x00  # Padding
]
can.send(Message(arbitration_id=0x201, data=rpdo1_data))
```

### TPDO1 (Transmit PDO 1) - Estado Principal

**COB-ID**: `NodeID + 0x180` (ej: 0x181 para NodeID=1)

**Mapeo**:
1. **Status Word (0x6041)**: 16 bits - Palabra de estado CiA 402
2. **Modes of Operation Display (0x6061)**: 8 bits - Modo actual

**Event Timer**: 100 ms (envío periódico automático)

**Uso**: Recibir estado del R13 F continuamente

```python
# Ejemplo: Leer Status Word
msg = can.recv()
if msg.arbitration_id == 0x181:
    status_word = (msg.data[1] << 8) | msg.data[0]
    mode_display = msg.data[2]
    print(f"Status: 0x{status_word:04X}, Mode: {mode_display}")
```

### TPDO2 (Transmit PDO 2) - Información de Movimiento

**COB-ID**: `NodeID + 0x280` (ej: 0x281 para NodeID=1)

**Mapeo**:
1. **Velocity Actual Value (0x606C)**: 32 bits - Velocidad actual
2. **Torque Actual Value (0x6077)**: 16 bits - Torque actual

**Event Timer**: 200 ms

**Uso**: Monitorear velocidad y torque del motor

## 🎮 Objetos CiA 402 Principales

### Control Word (0x6040) - Comandos

| Bits | Comando | Descripción |
|------|---------|-------------|
| 0-2-3 | 0x06 | Switch On + Enable Voltage + Quick Stop |
| 0-1-2-3 | 0x0F | Enable Operation (dispositivo activo) |
| 7 | 0x80 | Fault Reset (limpiar errores) |
| 8 | 0x100 | Halt (detener movimiento temporalmente) |

**Secuencia de activación**:
```
0x0006 → Switch On
0x0007 → Enable Voltage  
0x000F → Enable Operation (listo para comandos)
```

### Status Word (0x6041) - Estado

| Bits | Estado | Máscara | Valor | Descripción |
|------|--------|---------|-------|-------------|
| 0-5-6 | Not Ready to Switch On | 0x004F | 0x0000 | Inicializando |
| 0-5-6 | Switch On Disabled | 0x004F | 0x0040 | Deshabilitado |
| 0-1-5-6 | Ready to Switch On | 0x006F | 0x0021 | Listo para activar |
| 0-1-2-5 | Switched On | 0x006F | 0x0023 | Activado |
| 0-1-2-3-5 | Operation Enabled | 0x006F | 0x0027 | Operación habilitada |
| 3-5 | Fault | 0x004F | 0x0008 | Error presente |

**Verificar estado operacional**:
```python
if (status_word & 0x006F) == 0x0027:
    print("✅ Dispositivo operacional")
```

### Modos de Operación (0x6060/0x6061)

| Valor | Modo | Descripción | Uso en R13 F |
|-------|------|-------------|--------------|
| 0 | No mode | Sin modo activo | Estado inicial |
| 1 | Profile Position | Control de posición con perfil | Movimiento preciso |
| 3 | Profile Velocity | Control de velocidad con perfil | **Modo principal** |
| 6 | Homing | Búsqueda de origen | Calibración |
| -1 | Manual Mode | Control manual | Joystick/botones |

**Configurar modo**:
```python
# SDO Write: Set Profile Velocity mode
sdo.download(0x6060, 0, bytes([3]))
```

### Parámetros de Movimiento

| Objeto | Nombre | Tipo | Unidad | Default |
|--------|--------|------|--------|---------|
| 0x607A | Target Position | INT32 | Encoder counts | 0 |
| 0x60FF | Target Velocity | INT32 | RPM o custom | 0 |
| 0x6081 | Profile Velocity | UINT32 | RPM | 1000 |
| 0x6083 | Profile Acceleration | UINT32 | RPM/s | 1000 |
| 0x6084 | Profile Deceleration | UINT32 | RPM/s | 1000 |

### Valores Actuales (Solo Lectura)

| Objeto | Nombre | Tipo | Descripción |
|--------|--------|------|-------------|
| 0x6064 | Position Actual Value | INT32 | Posición actual del encoder |
| 0x606C | Velocity Actual Value | INT32 | Velocidad actual |
| 0x6077 | Torque Actual Value | INT16 | Torque aplicado |

## 🚀 Uso del Archivo EDS

### Con Python CANopen

```python
import canopen

# Crear red CANopen
network = canopen.Network()
network.connect(channel='can0', bustype='socketcan')

# Cargar EDS y agregar nodo
node = network.add_node(1, 'config/danfoss_r13f_complete.eds')

# Iniciar heartbeat
node.nmt.state = 'OPERATIONAL'

# Leer objeto del dictionary
device_name = node.sdo['Device Name'].raw
print(f"Dispositivo: {device_name}")

# Escribir Control Word via SDO
node.sdo[0x6040].raw = 0x0006  # Switch On

# O usar PDO para tiempo real
node.rpdo[1]['Controlword'].raw = 0x000F  # Enable Operation
node.rpdo[1].transmit()

# Leer estado
status = node.tpdo[1]['Statusword'].raw
print(f"Status: 0x{status:04X}")
```

### Con BL335 Gateway

El gateway Python carga automáticamente este EDS:

```python
from src.bl335_gateway.main import BL335Gateway

gateway = BL335Gateway(
    can_interface='can0',
    node_id=1,
    eds_file='config/danfoss_r13f_complete.eds'
)

gateway.start()
```

## 🧪 Validación

### Verificar Sintaxis EDS

Usa herramientas online o locales:
- [CANopen EDS Checker](https://www.can-cia.org/services/cia-member-services/cia-test-specification/)
- `canopen-check` (comando Python)

```bash
pip install canopen
python -c "import canopen; canopen.ObjectDictionary.from_eds('config/danfoss_r13f_complete.eds')"
```

### Probar con Simulador

```bash
# Terminal 1: Simulador R13 F
python tools/can_simulator.py --eds config/danfoss_r13f_complete.eds

# Terminal 2: Gateway
python src/bl335_gateway/main.py

# Terminal 3: Enviar comando
cansend can0 201#0600030000000000  # Enable Operation
```

## 📚 Referencias

- **CiA 301**: CANopen Application Layer and Communication Profile
- **CiA 402**: CANopen Device Profile for Drives and Motion Control
- **Danfoss R13 F Manual**: `docs/RECEPTOR K13 F.md`
- **CANopen Wizard**: https://www.canopenwizard.com/

## ⚠️ Notas Importantes

1. **Node ID Configurable**: El R13 F real puede tener un NodeID diferente (verificar con DIP switches o configuración)

2. **Unidades de Velocidad**: Las unidades reales (RPM, mm/s, etc.) dependen de la configuración del R13 F

3. **Emergency Stop**: Para parada de emergencia, enviar Control Word = 0x0002 (Quick Stop activo)

4. **Heartbeat**: Configure el heartbeat para detectar desconexiones (recomendado: 500ms)

5. **Versión**: Este EDS es una aproximación basada en estándares. Contacta a Danfoss para el EDS oficial si está disponible

## 🔄 Actualizaciones Futuras

- [ ] Agregar objetos manufacturer-specific (0x2000-0x5FFF)
- [ ] Definir mapeosSDO adicionales
- [ ] Incluir parámetros de seguridad (Safety PDO)
- [ ] Validar con hardware R13 F real
- [ ] Optimizar Event Timers según pruebas de latencia

---

**Archivo**: `config/danfoss_r13f_complete.eds`  
**Versión**: 1.0.0  
**Fecha**: 21 de octubre de 2025  
**Autor**: K13 Puente Grúa Project
