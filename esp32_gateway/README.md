# ESP32 Gateway - Crane Emergency Stop System

Firmware para gateway ESP32-S3 que conecta sistema de control con receptor Danfoss R13 F vía CANopen.

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

## 📊 Estado del Proyecto - VERSIÓN SIMPLIFICADA

### ✅ Core Funcional (Activo)
- [x] CAN Manager (TWAI) operativo
- [x] CANopen MVP: RPDO1 + TPDO1 + Heartbeat
- [x] CiA 402 State Machine
- [x] Main loop limpio y simple
- [x] **LISTO PARA COMPILAR Y PROBAR**

### 🔄 Componentes Avanzados (Desactivados por ahora)
- [ ] WiFi Manager (no necesario para MVP)
- [ ] Ethernet Manager (no necesario para MVP)
- [ ] OTA Manager (cuando funcione lo básico)
- [ ] Config Manager (hardcoded por ahora)
- [ ] TCP Server (cuando funcione lo básico)

### 🎯 Próximo Paso
**COMPILAR Y PROBAR** con hardware real o simulador

### 🔎 Detalles del MVP CANopen

- Node ID: 0x01 (configurable próximamente vía NVS)
- COB-IDs:
  - TPDO1: 0x180 + NodeID (0x181)
  - RPDO1: 0x200 + NodeID (0x201)
  - Heartbeat: 0x700 + NodeID (0x701)
- CiA 402 soportado (simplificado): SwitchOnDisabled ↔ ReadyToSwitchOn ↔ SwitchedOn ↔ OperationEnabled con QuickStop/Fault reset

### 🧪 Prueba rápida (en banco)

1) Flashea y abre el monitor:
  - `idf.py -p /dev/ttyUSB0 flash monitor`
2) Envía RPDO1 (Control Word) 0x0007 y observa transición a ReadyToSwitchOn:
  - Frame: ID 0x201, DLC 2, Data: 07 00 00 00 00 00 00 00
3) Observa TPDO1 (Status Word) en 0x181 actualizándose cada ~50ms.
4) Heartbeat en 0x701 (byte=0x05) cada 1s.

## 🐛 Debug

```bash
# Monitor serial
idf.py monitor

# Monitor con filtro de logs
idf.py monitor | grep "ESP32_GATEWAY"
```

## 📄 Licencia

Copyright © 2025 - Crane Emergency Stop System
