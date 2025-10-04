# Implementación del Sistema R13 CANopen

## Arquitectura del Sistema

### Componentes Principales

1. **R13Controller**: Clase principal que maneja la lógica de control
2. **NetworkComm**: Módulo de comunicación de red TCP/IP
3. **R13CANopenProtocol**: Definición del protocolo CANopen para el R13
4. **CANopen Gateway**: Raspberry Pi que traduce Ethernet a CAN bus
5. **Configuration**: Manejo de archivos de configuración

### Diagrama de Arquitectura Actualizada

```
┌─────────────────┐    TCP/IP     ┌─────────────────────┐    CAN bus    ┌─────────────────┐
│   Aplicación    │◄────────────►│     Gateway         │◄────────────►│   Danfoss R13   │
│     Usuario     │               │ ESP32/Arduino/RPi   │               │    Receptor     │
│  (main.py)      │               │ (WiFi + CAN)        │               └─────────────────┘
└─────────────────┘               └─────────────────────┘                         │
        │                                    │                                    ▼
        ▼                              ┌─────────────┐                      ┌─────────────┐
┌─────────────────┐                    │ CANopen     │                      │  Variador   │
│  NetworkComm    │                    │ Network     │                      │ Puente Grúa │
│ (network_comm.py)│                   │ Management  │                      └─────────────┘
└─────────────────┘                    └─────────────┘
        │
        ▼
┌─────────────────┐
│ R13CANopen      │
│ Protocol        │
│ (protocol.py)   │
└─────────────────┘
```

## Opciones de Hardware Gateway

### 1. ESP32 (Recomendada) 🏆

**Ventajas:**
- CAN controller integrado (TWAI)
- WiFi nativo para TCP/IP
- Tiempo real para aplicaciones críticas
- Bajo costo (~$12.000 CLP)
- Fácil programación con Arduino IDE

**Implementación:**
- Archivo: `scripts/esp32_gateway.ino`
- Hardware: ESP32-S3 con CAN TWAI
- Comunicación: WiFi TCP servidor puerto 9999
- Protocolo: JSON sobre TCP + CANopen sobre CAN

### 2. Arduino UNO R4 + CAN Shield

**Ventajas:**
- Plataforma conocida y estable
- WiFi integrado en R4
- Modular (fácil reemplazo componentes)

**Desventajas:**
- Requiere shield CAN adicional (MCP2515)
- Mayor costo (~$40.000 CLP)
- Más conexiones/cables

### 3. Raspberry Pi 4 + CAN HAT

**Ventajas:**
- Máxima potencia de procesamiento
- Python nativo
- Ethernet + WiFi
- Sistema operativo completo

**Desventajas:**
- No tiempo real (Linux)
- Mayor latencia
- Alto consumo energético
- Costo elevado (~$95.000 CLP)

## Protocolo de Comunicación CANopen

### Flujo de Control

1. **Aplicación Python** (main.py):
   - Recibe comandos del usuario
   - Los traduce a mensajes CANopen usando `R13CANopenProtocol`
   - Los envía por TCP/IP al gateway

2. **Gateway Raspberry Pi** (canopen_gateway_rpi.py):
   - Escucha comandos TCP/IP en puerto 9999
   - Traduce mensajes JSON a comandos CANopen
   - Envía por CAN bus al receptor R13

3. **Receptor Danfoss R13**:
   - Recibe comandos CANopen por CAN bus
   - Ejecuta acciones en el variador del puente grúa
   - Envía respuestas de estado por CAN bus

### Mensajes CANopen Típicos

#### Inicialización del Dispositivo
```python
# 1. Configurar modo de operación (Velocity Profile)
sdo_write(0x6060, 0, 3)  # Modo Profile Velocity

# 2. Activar dispositivo
sdo_write(0x6040, 0, 0x000F)  # Control Word: Enable Operation

# 3. Configurar velocidad máxima
sdo_write(0x6081, 0, 1000)  # Profile Velocity
```

#### Control en Tiempo Real
```python
# Enviar velocidad objetivo
sdo_write(0x6081, 0, velocity_rpm)

# Leer estado actual
status = sdo_read(0x6041, 0)  # Status Word
actual_velocity = sdo_read(0x606C, 0)  # Velocity Actual Value
```

## Implementación de Seguridad

### Medidas de Seguridad Implementadas

1. **Timeout de Comunicación**:
   - Máximo 30 segundos sin comunicación
   - Parada automática del puente grúa
   - Notificación de error al operador

2. **Verificación de Comandos**:
   - Checksum en todos los mensajes
   - Códigos de autenticación
   - Confirmación de recepción

3. **Parada de Emergencia**:
   - Comando de prioridad máxima
   - No puede ser interrumpido
   - Detiene todos los movimientos inmediatamente

### Manejo de Errores

```python
class K13Error(Exception):
    """Excepción base para errores K13"""
    pass

class ConnectionError(K13Error):
    """Error de conexión con dispositivo"""
    pass

class ProtocolError(K13Error):
    """Error de protocolo de comunicación"""
    pass

class SafetyError(K13Error):
    """Error de seguridad crítico"""
    pass
```

## Testing y Validación

### Estrategia de Testing

1. **Tests Unitarios**:
   - Probar cada módulo por separado
   - Validar formato de mensajes
   - Verificar cálculo de checksums

2. **Tests de Integración**:
   - Comunicación extremo a extremo
   - Simulación de dispositivo K13
   - Pruebas de timeout y errores

3. **Tests de Seguridad**:
   - Parada de emergencia
   - Manejo de desconexión
   - Validación de comandos malformados

### Casos de Prueba

#### Test 1: Conexión Básica
```python
def test_basic_connection():
    controller = K13Controller()
    assert controller.connect() == True
    assert controller.is_connected == True
    controller.disconnect()
```

#### Test 2: Envío de Comandos
```python
def test_send_command():
    controller = K13Controller()
    controller.connect()
    
    cmd = CraneCommand("move_up", speed=50)
    result = controller.send_command(cmd)
    
    assert result == True
    controller.disconnect()
```

#### Test 3: Parada de Emergencia
```python
def test_emergency_stop():
    controller = K13Controller()
    controller.connect()
    
    result = controller.emergency_stop()
    
    assert result == True
    controller.disconnect()
```

## Configuración y Deployment

### Archivos de Configuración

- `config/k13_config.yaml`: Configuración principal
- `config/logging.conf`: Configuración de logs
- `config/safety.yaml`: Parámetros de seguridad

### Instalación en Producción

1. **Preparar entorno**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configurar dispositivo**:
   ```bash
   # Verificar puerto serie
   ls /dev/tty*
   
   # Dar permisos de acceso
   sudo usermod -a -G dialout $USER
   ```

3. **Probar conexión**:
   ```bash
   python src/k13_controller/main.py --test
   ```

## Monitoreo y Logging

### Niveles de Log

- **DEBUG**: Información detallada de comunicación
- **INFO**: Operaciones normales
- **WARNING**: Situaciones que requieren atención
- **ERROR**: Errores recuperables
- **CRITICAL**: Errores que requieren parada inmediata

### Métricas de Monitoreo

- Tiempo de respuesta de comandos
- Tasa de errores de comunicación
- Tiempo de operación continua
- Estado de batería del transmisor

## Próximos Pasos

### Funcionalidades Pendientes

1. **Interface Gráfica**:
   - Panel de control visual
   - Monitoreo en tiempo real
   - Configuración interactiva

2. **Control Remoto Web**:
   - API REST para control remoto
   - Dashboard web
   - Autenticación y autorización

3. **Integración con PLC**:
   - Protocolo Modbus
   - Señales de estado
   - Automatización avanzada

### Optimizaciones

1. **Rendimiento**:
   - Reducir latencia de comandos
   - Optimizar protocolo de comunicación
   - Cache de configuración

2. **Robustez**:
   - Reconexión automática
   - Redundancia de comunicación
   - Recuperación de errores

---

**Fecha de implementación**: 8 de septiembre de 2025  
**Versión**: 1.0.0  
**Estado**: En desarrollo
