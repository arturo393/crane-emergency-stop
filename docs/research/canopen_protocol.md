# CANopen Protocol - Guía Técnica para Control del Danfoss R13

## ¿Qué es CANopen?

CANopen es un protocolo de comunicación de alto nivel basado en CAN bus, diseñado para sistemas de automatización industrial. Es el "idioma" que los dispositivos usan para entenderse entre sí.

### Conceptos Fundamentales

#### 1. Object Dictionary (OD) - El "Cerebro" del Dispositivo
El Object Dictionary es como una base de datos dentro de cada dispositivo CANopen. Contiene:
- **Configuración**: Parámetros como velocidad máxima, aceleración
- **Estado**: Información actual como posición, velocidad, errores  
- **Control**: Variables que permiten comandar el dispositivo

Cada entrada en el OD tiene:
- **Índice**: Dirección única (ej: 0x6040 para Control Word)
- **Sub-índice**: Para datos complejos (ej: 0x6040.01)
- **Tipo de datos**: UINT8, INT16, STRING, etc.
- **Permisos**: Solo lectura, escritura, lectura/escritura

#### 2. Comunicación en CANopen

##### SDO (Service Data Objects) - Configuración
- **Propósito**: Leer/escribir el Object Dictionary
- **Características**: Comunicación confiable pero más lenta
- **Uso típico**: Configurar parámetros antes de la operación

```python
# Ejemplo conceptual
sdo.write(0x6081, 0, 1000)  # Escribir velocidad de perfil
velocity = sdo.read(0x606C, 0)  # Leer velocidad actual
```

##### PDO (Process Data Objects) - Tiempo Real
- **Propósito**: Transferencia rápida de datos críticos
- **Características**: Muy eficiente, para control en tiempo real
- **Tipos**:
  - **TPDO (Transmit PDO)**: Datos que el dispositivo envía
  - **RPDO (Receive PDO)**: Datos que el dispositivo recibe

```python
# Ejemplo conceptual
pdo.tx[1]['target_velocity'] = 50  # Enviar velocidad deseada
current_pos = pdo.rx[1]['position_actual']  # Leer posición actual
```

##### NMT (Network Management) - Control de Red
- **Propósito**: Controlar el estado operacional de los dispositivos
- **Estados**:
  - **Pre-operational**: Configuración inicial
  - **Operational**: Funcionamiento normal
  - **Stopped**: Detenido

## Perfiles Estándar de CANopen

### CiA 402 - Motion Control Profile
El receptor Danfoss R13 muy probablemente implementa el perfil CiA 402, que es el estándar para control de movimiento. Este perfil define:

#### Objetos Principales del Object Dictionary

| Índice | Nombre | Descripción | Tipo | Acceso |
|--------|--------|-------------|------|--------|
| 0x6040 | Control Word | Palabra de control principal | UINT16 | RW |
| 0x6041 | Status Word | Estado del dispositivo | UINT16 | RO |
| 0x6060 | Modes of Operation | Modo de operación | INT8 | RW |
| 0x6061 | Modes of Operation Display | Modo actual | INT8 | RO |
| 0x607A | Target Position | Posición objetivo | INT32 | RW |
| 0x6081 | Profile Velocity | Velocidad de perfil | UINT32 | RW |
| 0x606C | Velocity Actual Value | Velocidad actual | INT32 | RO |

#### Control Word (0x6040) - Comandos Principales

La Control Word es una palabra de 16 bits donde cada bit tiene un significado específico:

| Bit | Nombre | Descripción |
|-----|--------|-------------|
| 0 | Switch On | Habilitar dispositivo |
| 1 | Enable Voltage | Habilitar voltaje |
| 2 | Quick Stop | Parada rápida |
| 3 | Enable Operation | Habilitar operación |
| 4-7 | Operation Mode Specific | Específico del modo |
| 8 | Reset | Reiniciar errores |
| 9 | Halt | Detener movimiento |

#### Status Word (0x6041) - Estado del Dispositivo

| Bit | Nombre | Descripción |
|-----|--------|-------------|
| 0 | Ready to Switch On | Listo para activar |
| 1 | Switched On | Activado |
| 2 | Operation Enabled | Operación habilitada |
| 3 | Fault | Error presente |
| 4 | Voltage Enabled | Voltaje habilitado |
| 5 | Quick Stop | En parada rápida |
| 6 | Switch On Disabled | Activación deshabilitada |

#### Modos de Operación (0x6060)

| Valor | Modo | Descripción |
|-------|------|-------------|
| 1 | Profile Position | Control de posición con perfil |
| 3 | Profile Velocity | Control de velocidad con perfil |
| 6 | Homing | Modo de búsqueda de origen |
| 8 | Cyclic Synchronous Position | Posición síncrona cíclica |
| 9 | Cyclic Synchronous Velocity | Velocidad síncrona cíclica |

## Secuencia de Inicialización

### 1. Configuración del Dispositivo (SDO)
```python
# Configurar modo de operación
sdo.write(0x6060, 0, 3)  # Modo Profile Velocity

# Configurar velocidad máxima
sdo.write(0x6081, 0, 1000)  # RPM o unidades específicas

# Configurar aceleración
sdo.write(0x6083, 0, 500)  # Aceleración del perfil

# Configurar desaceleración  
sdo.write(0x6084, 0, 500)  # Desaceleración del perfil
```

### 2. Activación del Dispositivo (Control Word)
```python
# Secuencia de activación según CiA 402
control_word = 0x0000

# Paso 1: Switch On
control_word |= (1 << 0) | (1 << 1) | (1 << 2)  # Bits 0,1,2
sdo.write(0x6040, 0, control_word)

# Paso 2: Enable Operation  
control_word |= (1 << 3)  # Bit 3
sdo.write(0x6040, 0, control_word)
```

### 3. Control en Tiempo Real (PDO)
```python
# Configurar PDOs para transmisión automática
# El dispositivo enviará su estado cada X ms
pdo.tx[1].period = 100  # 100ms

# Enviar comando de velocidad
pdo.rx[1]['target_velocity'] = velocidad_deseada
pdo.rx[1].transmit()
```

## Implementación con Python

### Librerías Necesarias
```bash
pip install canopen python-can
```

### Estructura de Código Típica
```python
import canopen
import can

# 1. Crear la red CANopen
network = canopen.Network()

# 2. Conectar al bus CAN físico  
network.connect(channel='can0', bustype='socketcan')

# 3. Agregar el dispositivo R13 a la red
r13_node = canopen.RemoteNode(node_id=1, object_dictionary='r13.eds')
network.add_node(r13_node)

# 4. Inicializar el dispositivo
r13_node.nmt.state = 'OPERATIONAL'

# 5. Configurar modo de operación
r13_node.sdo[0x6060].raw = 3  # Profile Velocity

# 6. Enviar comandos
r13_node.sdo[0x6081].raw = 500  # Velocidad objetivo
```

## Archivos EDS (Electronic Data Sheet)

### ¿Qué es un archivo EDS?
- **Definición**: Descripción completa del Object Dictionary del dispositivo
- **Formato**: Archivo de texto similar a un INI
- **Propósito**: Permite a las herramientas CANopen conocer todas las capacidades del dispositivo
- **Ubicación**: Proporcionado por Danfoss para el R13

### Obtener el archivo EDS del Danfoss R13
1. **Sitio web de Danfoss**: Descargar desde el área de soporte técnico
2. **Software de configuración**: Danfoss PLUS+1 Service Tool
3. **Contacto directo**: Solicitar a soporte técnico de Danfoss

## Diagnóstico y Troubleshooting

### Herramientas de Monitoreo
- **CANopen for Python**: Monitoreo del tráfico
- **Peak PCAN-View**: Analizador visual del bus CAN
- **Kvaser CANking**: Herramienta profesional de diagnóstico

### Problemas Comunes

#### Error en Status Word
```python
status = r13_node.sdo[0x6041].raw
if status & (1 << 3):  # Bit 3 = Fault
    print("Error en el dispositivo")
    # Leer registro de errores específico
    error_code = r13_node.sdo[0x603F].raw
```

#### Timeout en SDO
- **Causa**: Dispositivo no responde
- **Solución**: Verificar conexión CAN, velocidad del bus, terminaciones

#### PDO no recibidos
- **Causa**: Configuración incorrecta de PDO mapping
- **Solución**: Verificar configuración de PDOs en el archivo EDS

## Próximos Pasos para el Proyecto

1. **Obtener archivo EDS**: Contactar a Danfoss para el archivo EDS del R13
2. **Configurar hardware CAN**: Raspberry Pi + CAN HAT
3. **Implementar capa CANopen**: Adaptar el código actual para usar `python-can` y `canopen`
4. **Testing con dispositivo real**: Probar la comunicación con el R13 físico

---

**Referencias:**
- CiA 301: CANopen Application Layer and Communication Profile
- CiA 402: CANopen Device Profile for Motion Control
- Danfoss R13 F Manual y documentación técnica

**Fecha**: 8 de septiembre de 2025
**Estado**: Documentación técnica completa - Listo para implementación
