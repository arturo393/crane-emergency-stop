# 🚀 ESP32 Gateway - Quick Start

## 📋 Requisitos Previos

- macOS con Homebrew instalado
- ESP-IDF v5.1+ instalado
- ESP32-S3 DevKit con soporte CAN (TWAI)

## 🔧 Configuración Inicial

### 1. Activar ESP-IDF

En cada nueva terminal, activa el entorno ESP-IDF:

```bash
source ~/esp/esp-idf/export.sh
```

O agrega un alias a tu `~/.zshrc`:

```bash
alias get_idf='. ~/esp/esp-idf/export.sh'
```

Luego usa: `get_idf`

### 2. Verificar Instalación

```bash
idf.py --version
# Debe mostrar: ESP-IDF v5.1.x
```

## 🏗️ Compilar el Firmware

### Versión Simplificada (Actual)

```bash
cd esp32_gateway
idf.py build
```

Esto compila solo:
- CAN Manager (TWAI driver)
- CiA 402 State Machine
- PDO Handler básico
- Heartbeat CANopen

**Tamaño esperado**: ~500KB

### Configurar Target

Si es la primera vez o cambias de chip:

```bash
# Para ESP32-S3
idf.py set-target esp32s3

# Para ESP32 clásico
idf.py set-target esp32
```

## 📱 Flashear al ESP32

### 1. Conectar ESP32 vía USB

```bash
# Listar puertos disponibles
ls /dev/cu.usbserial-* /dev/cu.usbmodem-*

# Ejemplo de puerto: /dev/cu.usbserial-14410
```

### 2. Flashear

```bash
idf.py -p /dev/cu.usbserial-14410 flash
```

### 3. Monitorear Serial

```bash
idf.py -p /dev/cu.usbserial-14410 monitor
```

O todo en uno:

```bash
idf.py -p /dev/cu.usbserial-14410 flash monitor
```

**Presiona `Ctrl+]` para salir del monitor**

## 🔌 Conexiones Hardware

### CAN Transceiver (Ejemplo: SN65HVD230)

```
ESP32-S3        SN65HVD230
---------       ----------
GPIO 4   -----> TX
GPIO 5   <----- RX
3.3V     -----> VCC
GND      -----> GND

SN65HVD230      CAN Bus
----------      -------
CANH     -----> CANH (K13 F)
CANL     -----> CANL (K13 F)
```

⚠️ **Importante**: Asegúrate de tener resistencia de terminación de 120Ω si estás al final del bus.

## 📊 Salida Esperada

```
==============================================
   K13 Gateway - Control Puente Grúa
   Compilado: Oct 21 2025 10:30:00
==============================================

🔧 Inicializando CAN bus...
✅ CAN bus listo

📡 CANopen configurado:
   Node ID: 0x01
   RPDO1 (recibe Control Word): 0x201
   TPDO1 (envía Status Word):   0x181
   Heartbeat:                   0x701

========================================
🚀 Sistema listo - Loop principal activo
========================================

💓 Heartbeat
💓 Heartbeat
📥 Control Word: 0x0006
💓 Heartbeat
...
```

## 🐛 Troubleshooting

### Error: "idf.py not found"

```bash
# Activa el entorno
source ~/esp/esp-idf/export.sh
```

### Error: "CAN driver install failed"

- Verifica conexiones TX/RX (GPIO 4 y 5)
- Verifica que el transceiver tenga alimentación (3.3V)
- Revisa pines en `can_manager.h` si usas otros GPIOs

### Error: "No se puede abrir puerto serial"

```bash
# Verifica permisos
sudo chmod 666 /dev/cu.usbserial-*

# O identifica el puerto correcto
ls /dev/cu.*
```

### No hay comunicación CAN

1. Verifica bus CAN con osciloscopio (debe haber pulsos en CANH/CANL)
2. Confirma bitrate (250 kbps por defecto)
3. Verifica resistencias de terminación (120Ω en cada extremo)
4. Revisa que CANH y CANL no estén invertidos

## 🔧 Configuración Avanzada

### Cambiar Bitrate CAN

Edita `can_manager.cpp`:

```cpp
timing_config.brp = 16;  // Para 250 kbps
// timing_config.brp = 8;  // Para 500 kbps
```

### Cambiar Node ID

Edita `main.cpp`:

```cpp
static const uint8_t NODE_ID = 0x01;  // Cambiar aquí
```

### Habilitar Logs DEBUG

```bash
idf.py menuconfig
# Component config -> Log output -> Default log verbosity -> Debug
```

## 📚 Próximos Pasos

1. **Testing sin Hardware**: Usa tests nativos en `test/native/` (ver `test/native/README.md`)
2. **Con Hardware Real**: Conecta el K13 F y prueba comandos
3. **BL335 Gateway**: Conecta vía TCP para control remoto
4. **Web UI**: Usa `src/web_ui/` para monitoreo visual
5. **Avanzado**: Re-habilita Ethernet/WiFi/OTA cuando sea necesario

## 🆘 Soporte

- **Documentación ESP-IDF**: https://docs.espressif.com/projects/esp-idf/
- **Proyecto**: Ver `README.md` principal
- **Issues**: Sistema TODO local en VS Code

---

**Última actualización**: 21 de octubre de 2025  
**Versión**: Simplificada - Solo CAN Core
