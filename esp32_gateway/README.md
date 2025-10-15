# ESP32 Gateway - Crane Emergency Stop System

Firmware para gateway ESP32-S3 que conecta sistema de control con receptor Danfoss K13 F vía CANopen.

## 🚀 Características

- **WiFi**: Cliente (STA) y Access Point (AP) con DHCP
- **Ethernet**: Soporte W5500/LAN8720 con DHCP configurable
- **CAN Bus**: Driver TWAI con protocolo CANopen
- **FOTA**: Actualizaciones Over-The-Air seguras
- **FreeRTOS**: Tareas concurrentes y gestión de recursos

## 🛠️ Requisitos

- ESP-IDF v5.x o superior
- ESP32-S3 con soporte TWAI (CAN)
- Transceiver CAN TJA1050 o similar

## 📦 Estructura del Proyecto

```
esp32_gateway/
├── main/
│   ├── main.cpp              # Punto de entrada principal
│   ├── wifi_manager.cpp/h    # Gestión WiFi
│   ├── can_manager.cpp/h     # Gestión CAN/TWAI
│   ├── ethernet_manager.cpp/h # Gestión Ethernet (TODO)
│   ├── ota_manager.cpp/h     # Gestión FOTA (TODO)
│   └── CMakeLists.txt
├── components/
│   ├── canopen/              # Componente CANopen (TODO)
│   └── network/              # Componente de red (TODO)
└── CMakeLists.txt
```

## 🔧 Compilación

```bash
# Configurar ESP-IDF environment
. $HOME/esp/esp-idf/export.sh

# Configurar proyecto
cd esp32_gateway
idf.py menuconfig

# Compilar
idf.py build

# Flashear
idf.py -p /dev/ttyUSB0 flash monitor
```

## 📝 Configuración

### Pines CAN (GPIO)
- **TX**: GPIO 21 (configurable)
- **RX**: GPIO 22 (configurable)

### Velocidad CAN
- **Default**: 250 kbps (configurable en código)

### WiFi
- **SSID**: Configurar en código o NVS
- **Password**: Configurar en código o NVS
- **DHCP**: Habilitado por defecto

## 🔗 Referencias

- [ESP-IDF Documentation](https://docs.espressif.com/projects/esp-idf/)
- [TWAI Driver](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/twai.html)
- [CANopen Protocol](https://www.can-cia.org/canopen/)
- [Danfoss K13 F Datasheet](../docs/RECEPTOR%20K13%20F.md)

## 📊 Estado del Proyecto

- [x] Estructura base del proyecto
- [x] Main loop con FreeRTOS
- [x] CAN Manager básico (TWAI driver)
- [x] WiFi Manager estructura
- [ ] Ethernet Manager
- [ ] OTA Manager
- [ ] Protocolo CANopen completo
- [ ] Tests unitarios
- [ ] Documentación completa

## 🐛 Debug

```bash
# Monitor serial
idf.py monitor

# Monitor con filtro de logs
idf.py monitor | grep "ESP32_GATEWAY"
```

## 📄 Licencia

Copyright © 2025 - Crane Emergency Stop System
