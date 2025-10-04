# Guía de Instalación ESP32 Gateway

## Materiales Necesarios (Chile)

### Hardware
- **ESP32-S3** con CAN TWAI (~$12.000 CLP)
  - Disponible en MercadoLibre Chile
  - Buscar: "ESP32-S3 CAN" o "ESP32 TWAI"
- **Transceiver CAN TJA1050** (~$3.000 CLP)
  - Para comunicación CAN bus
- **Conectores** y cables (~$5.000 CLP)
- **Fuente 12V** para alimentación general

### Software
- Arduino IDE 2.x
- Librerías ESP32 CAN TWAI
- ArduinoJson library

## Instalación Paso a Paso

### 1. Configurar Arduino IDE

```bash
# Instalar Arduino IDE desde: https://www.arduino.cc/en/software

# Agregar ESP32 boards:
# File -> Preferences -> Additional Boards Manager URLs:
# https://dl.espressif.com/dl/package_esp32_index.json
```

### 2. Instalar Librerías

En Arduino IDE:
- Tools -> Manage Libraries
- Buscar e instalar:
  - **ArduinoJson** by Benoit Blanchon
  - **WiFi** (incluida con ESP32)

### 3. Configurar Hardware

#### Conexiones ESP32-S3:
```
ESP32-S3 Pin    Función         Conexión
GPIO21          CAN TX          -> TJA1050 Pin 1 (TXD)
GPIO22          CAN RX          <- TJA1050 Pin 4 (RXD)
3.3V            Alimentación    -> TJA1050 Pin 3 (VDD)
GND             Tierra          -> TJA1050 Pin 2 (VSS)

TJA1050 Pin     Función         Conexión
Pin 6 (CANH)    CAN High        -> CAN bus CANH
Pin 7 (CANL)    CAN Low         -> CAN bus CANL
```

### 4. Cargar Código

1. Abrir `scripts/esp32_gateway.ino` en Arduino IDE
2. Configurar WiFi en las líneas:
   ```cpp
   const char* ssid = "TU_WIFI_SSID";
   const char* password = "TU_WIFI_PASSWORD";
   ```
3. Seleccionar board: **ESP32S3 Dev Module**
4. Configurar:
   - Upload Speed: 921600
   - CPU Frequency: 240MHz
   - Flash Size: 4MB
   - PSRAM: Enabled
5. Conectar ESP32 por USB y hacer Upload

### 5. Probar Funcionamiento

#### Monitor Serie:
Debería mostrar:
```
=== Gateway ESP32 CAN-WiFi para R13 ===
Inicializando CAN bus...
Driver TWAI instalado
CAN bus iniciado exitosamente
Conectando a WiFi...
WiFi conectado!
IP: 192.168.1.XXX
Servidor TCP iniciado en puerto 9999
Gateway listo - Esperando conexiones...
```

#### Probar desde Python:
```python
from src.k13_controller.main import R13Controller

# Usar la IP que aparece en el monitor serie
controller = R13Controller()
controller.config.gateway_ip = "192.168.1.XXX"  # IP del ESP32

# Probar conexión
if controller.connect():
    print("Conexión exitosa!")
    controller.get_status()
else:
    print("Error de conexión")
```

## Configuración del Proyecto Python

### Actualizar configuración:
Editar `config/k13_config.yaml`:
```yaml
network:
  gateway_ip: "192.168.1.XXX"  # IP del ESP32
  gateway_port: 9999
  timeout: 5.0

canopen:
  node_id: 1
  baudrate: 250000
```

## Solución de Problemas

### WiFi no conecta:
- Verificar SSID y password
- Verificar que la red es 2.4GHz (ESP32 no soporta 5GHz)
- Monitor serie para ver errores

### CAN bus no funciona:
- Verificar conexiones TJA1050
- Verificar alimentación 12V al bus CAN
- Usar multímetro para verificar señales

### TCP no responde:
- Verificar que el puerto 9999 no esté bloqueado
- Usar `telnet IP_ESP32 9999` para probar conexión
- Verificar firewall del computador

## Comandos de Diagnóstico

### Desde Monitor Serie Arduino:
El ESP32 mostrará logs automáticamente de:
- Estado WiFi cada 5 segundos
- Comandos recibidos por TCP
- Mensajes CAN transmitidos/recibidos
- Errores de comunicación

### Desde Python:
```python
# Ejecutar diagnósticos
controller = R13Controller()
controller.connect()

# Ver estado
status = controller.get_status()
print(f"Estado: {status}")

# Test de emergencia
controller.emergency_stop()
```

## Costos Totales (Chile)

| Componente | Precio CLP | Precio USD |
|------------|------------|------------|
| ESP32-S3 CAN | $12.000 | $15 |
| TJA1050 | $3.000 | $4 |
| Conectores/PCB | $5.000 | $6 |
| **Total** | **$20.000** | **$25** |

## Ventajas de esta Solución

✅ **Costo**: 5 veces más barato que Raspberry Pi
✅ **Tiempo Real**: Mejor para aplicaciones críticas
✅ **Simplicidad**: Una sola placa, menos cables
✅ **Confiabilidad**: Menos componentes = menos fallas
✅ **Consumo**: Mucho menor consumo energético
✅ **Disponibilidad**: Fácil de conseguir en Chile

## Próximos Pasos

1. **Comprar ESP32-S3** con CAN en MercadoLibre (~$12.000)
2. **Armar circuito** con TJA1050
3. **Cargar código** y configurar WiFi
4. **Conectar al R13** y probar comandos
5. **Configurar EDS file** del Danfoss R13
