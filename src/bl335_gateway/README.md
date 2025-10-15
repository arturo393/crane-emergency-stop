# BL335 Gateway

Gateway Ethernet-CAN implementado en Python para dispositivo BL335 Ubuntu IoT Gateway.

## Descripción

El BL335 Gateway conecta vía Ethernet (TCP/IP) y se comunica con el receptor Danfoss K13 F usando protocolo CANopen sobre SocketCAN.

## Características

- 🔌 Servidor TCP/IP multicliente
- 🚌 Comunicación CANopen via SocketCAN
- 📡 Comandos JSON para control
- ⚠️  Parada de emergencia
- 📊 Lectura/escritura SDO
- 🔄 Reset de dispositivo
- 🧪 Soporte para testing con vCAN

## Requisitos

- Python 3.8+
- python-can
- python-canopen
- Linux con SocketCAN

## Instalación

```bash
pip install python-can python-canopen
```

## Uso

### Testing con canal virtual (vcan0)

```bash
# Crear interfaz virtual CAN
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# Iniciar gateway
python src/bl335_gateway/main.py --can vcan0 --port 9999
```

### Uso en producción con hardware real

```bash
# Configurar interfaz CAN real
sudo ip link set can0 type can bitrate 250000
sudo ip link set up can0

# Iniciar gateway
python src/bl335_gateway/main.py --can can0 --port 9999 --node-id 1
```

## Protocolo de Comunicación

### Formato de Comandos

Los comandos se envían como JSON via TCP:

```json
{
  "command": "emergency_stop"
}
```

### Comandos Disponibles

#### 1. `get_status` - Obtener estado del sistema

**Request:**
```json
{
  "command": "get_status"
}
```

**Response:**
```json
{
  "status": "ok",
  "connected": true,
  "can_channel": "can0",
  "node_id": 1,
  "tcp_port": 9999,
  "last_error": null
}
```

#### 2. `emergency_stop` - Parada de emergencia

**Request:**
```json
{
  "command": "emergency_stop"
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Emergency stop activated"
}
```

#### 3. `reset` - Reset del dispositivo

**Request:**
```json
{
  "command": "reset"
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Reset sent"
}
```

#### 4. `sdo_read` - Leer objeto CANopen

**Request:**
```json
{
  "command": "sdo_read",
  "index": 4096,
  "subindex": 0
}
```

**Response:**
```json
{
  "status": "ok",
  "value": 1234
}
```

#### 5. `sdo_write` - Escribir objeto CANopen

**Request:**
```json
{
  "command": "sdo_write",
  "index": 4119,
  "subindex": 0,
  "value": 500
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Value written"
}
```

## Cliente de Ejemplo

```python
import socket
import json

# Conectar al gateway
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.100', 9999))

# Enviar comando
command = {'command': 'get_status'}
sock.send(json.dumps(command).encode('utf-8'))

# Recibir respuesta
response = sock.recv(4096)
data = json.loads(response.decode('utf-8'))
print(data)

sock.close()
```

## Testing

```bash
# Ejecutar tests
pytest tests/test_bl335_gateway.py -v

# Test con cobertura
pytest tests/test_bl335_gateway.py --cov=src/bl335_gateway
```

## Arquitectura

```
┌──────────────────┐
│  Monitor UI      │ (PyQt6)
│  (192.168.1.X)   │
└────────┬─────────┘
         │ TCP/IP
         │ Port 9999
┌────────▼─────────┐
│  BL335 Gateway   │ (Python)
│  Ubuntu IoT      │
│  192.168.1.100   │
└────────┬─────────┘
         │ SocketCAN
         │ 250 kbps
┌────────▼─────────┐
│  Danfoss K13 F   │ (CANopen)
│  Receptor Radio  │
│  Node ID: 1      │
└──────────────────┘
```

## Objetos CANopen Relevantes

| Índice | Sub | Nombre | Acceso | Descripción |
|--------|-----|--------|--------|-------------|
| 0x1000 | 0 | Device Type | RO | Tipo de dispositivo |
| 0x1001 | 0 | Error Register | RO | Registro de errores |
| 0x1017 | 0 | Producer Heartbeat | RW | Heartbeat (ms) |
| 0x6040 | 0 | Control Word | RW | Palabra de control |
| 0x6041 | 0 | Status Word | RO | Palabra de estado |

## Desarrollo

### Estructura del Código

```
src/bl335_gateway/
├── __init__.py         # Módulo Python
├── main.py             # Gateway principal
└── README.md           # Esta documentación

tests/
└── test_bl335_gateway.py  # Tests unitarios
```

### Próximas Características

- [ ] Carga de archivo EDS del K13 F
- [ ] Monitoreo de heartbeat
- [ ] Logging avanzado
- [ ] Métricas y estadísticas
- [ ] Configuración via archivo YAML
- [ ] Autenticación TCP
- [ ] WebSocket support
- [ ] REST API

## Troubleshooting

### Error: "No such device"

```bash
# Verificar interfaces CAN disponibles
ip link show

# Crear interfaz virtual para testing
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### Error: "Permission denied"

```bash
# Agregar usuario a grupo dialout
sudo usermod -a -G dialout $USER

# Logout y login nuevamente
```

### Error: "Address already in use"

```bash
# Cambiar puerto TCP
python src/bl335_gateway/main.py --port 10000

# O matar proceso usando el puerto
sudo lsof -ti:9999 | xargs kill -9
```

## Referencias

- [python-canopen Documentation](https://canopen.readthedocs.io/)
- [SocketCAN Documentation](https://www.kernel.org/doc/Documentation/networking/can.txt)
- [CANopen Protocol](https://www.can-cia.org/canopen/)

## Licencia

Ver archivo LICENSE en el directorio raíz del proyecto.
