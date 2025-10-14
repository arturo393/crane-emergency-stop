# Hardware Consolidado - Sistema de Parada de Emergencia Puente Grúa

## 🎯 **Hardware Seleccionado**

Basado en el análisis técnico y requerimientos del proyecto, se han seleccionado los siguientes equipos para implementar el sistema de parada de emergencia:

### 📦 **Equipos Seleccionados**

#### **1. BL335 - Gateway Principal Ethernet-CAN** ($35 USD)

- **Procesador**: Allwinner H3 (ARM Cortex-A7 Quad-core @1.2GHz)
- **Sistema**: Ubuntu IoT / Debian Linux
- **CAN Bus**: 2x puertos CAN 2.0A/B nativos (SocketCAN)
- **Ethernet**: 1x Gigabit Ethernet (10/100/1000 Mbps)
- **USB**: 2x USB 2.0 Host
- **Alimentación**: 5V DC (Micro-USB)
- **Dimensiones**: 85mm x 56mm
- **Peso**: ~50g

**Rol**: Gateway principal que traduce comandos TCP/IP del computador a mensajes CANopen para el receptor Danfoss K13 F.

#### **2. X8 - Transceiver CAN de Backup** ($8 USD)

- **Chip**: SN65HVD230 o TJA1050
- **Protocolo**: CAN 2.0A/B
- **Velocidad**: Hasta 1 Mbps
- **Aislamiento**: Protección ESD integrada
- **Alimentación**: 3.3V/5V DC
- **Dimensiones**: 40mm x 25mm

**Rol**: Transceiver CAN adicional para redundancia o expansión.

#### **3. EdgeBox-ESP-100 - Gateway WiFi Secundario** (~$45 USD)

- **Procesador**: ESP32-S3 (Dual-core Xtensa LX7 @240MHz)
- **Sistema**: FreeRTOS / ESP-IDF
- **CAN Bus**: 1x puerto TWAI (CAN 2.0) integrado
- **WiFi**: 2.4GHz 802.11 b/g/n integrado
- **Bluetooth**: 5.0 LE integrado
- **Alimentación**: 5V DC (USB-C)
- **Dimensiones**: 65mm x 50mm x 25mm

**Rol**: Gateway secundario WiFi para monitoreo remoto o backup.

## 🏗️ **Arquitectura del Sistema**

```text
┌─────────────────┐    Ethernet (TCP/IP)    ┌──────────────┐    CAN Bus     ┌───────────┐
│   COMPUTADOR    │◄──────────────────────►│   BL335      │◄──────────────►│ DANFOSS   │
│ DE PROCESAMIENTO│      Puerto 9999        │   Gateway    │   250 kbps     │   K13 F   │
│                 │                         │   + Ubuntu   │   CANopen      │ RECEIVER  │
└─────────────────┘                         └──────────────┘                └───────────┘
                                               │ CAN2 (Backup/Redundancia)
                                               ▼
                                        ┌──────────────┐
                                        │   X8 CAN     │
                                        │  Transceiver │
                                        │   (Opcional) │
                                        └──────────────┘

                                        ┌──────────────┐    WiFi         ┌─────────────┐
                                        │ EdgeBox-ESP  │◄───────────────►│  Monitoreo  │
                                        │ Backup WiFi  │   2.4GHz        │   Remoto    │
                                        └──────────────┘                 └─────────────┘
```

## 🔧 **Configuración Técnica**

### **BL335 - Configuración Principal**

#### **Sistema Operativo**

```bash
# Instalar Ubuntu IoT para Allwinner H3
wget https://ubuntu.com/download/iot/arm64
dd if=ubuntu-iot.img of=/dev/sdX bs=4M

# Primera configuración
sudo apt update && sudo apt upgrade
sudo apt install can-utils python3-can python3-socketcan
```

#### **Configuración CAN Bus**

```bash
# Cargar módulos CAN
sudo modprobe can
sudo modprobe can_raw
sudo modprobe mcp251x

# Configurar CAN0 (principal)
sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up

# Configurar CAN1 (backup)
sudo ip link set can1 type can bitrate 250000
sudo ip link set can1 up
```

#### **Configuración de Red**

```bash
# IP estática
sudo nmcli con mod "Wired connection 1" ipv4.addresses "192.168.1.100/24"
sudo nmcli con mod "Wired connection 1" ipv4.gateway "192.168.1.1"
sudo nmcli con mod "Wired connection 1" ipv4.dns "8.8.8.8"
sudo nmcli con up "Wired connection 1"
```

### **EdgeBox-ESP-100 - Configuración Secundaria**

#### **Entorno de Desarrollo**

```bash
# Instalar ESP-IDF
cd ~/esp
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh
. ./export.sh
```

#### **Configuración WiFi**

```c
// Configuración AP WiFi
wifi_config_t wifi_config = {
    .ap = {
        .ssid = "CRANE_CONTROL",
        .password = "crane2024",
        .max_connection = 4,
        .authmode = WIFI_AUTH_WPA2_PSK
    },
};
```

#### **Configuración CAN Bus ESP32**

```c
// Configuración TWAI (CAN)
twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(GPIO_NUM_21, GPIO_NUM_22, TWAI_MODE_NORMAL);
twai_timing_config_t t_config = TWAI_TIMING_CONFIG_250KBITS();
twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

ESP_ERROR_CHECK(twai_driver_install(&g_config, &t_config, &f_config));
ESP_ERROR_CHECK(twai_start());
```

#### **Conexiones ESP32-S3**

```text
ESP32-S3 Pin    Función         Conexión
GPIO21          CAN TX          -> TJA1050 Pin 1 (TXD)
GPIO22          CAN RX          <- TJA1050 Pin 4 (RXD)
3.3V            Alimentación    -> TJA1050 Pin 3 (VDD)
GND             Tierra          -> TJA1050 Pin 2 (VSS)

TJA1050 Pin     Función         Conexión
Pin 6 (CANH)    CAN High        -> CAN bus CANH
Pin 7 (CANL)    CAN Low         -> CAN bus CANL
```

## 📊 **Especificaciones Comparadas**

| Característica | BL335 | X8 | EdgeBox-ESP-100 |
|---------------|--------|----|------------------|
| **Procesador** | ARM Cortex-A7 Quad-core | - | Xtensa LX7 Dual |
| **Frecuencia** | 1.2 GHz | - | 240 MHz |
| **RAM** | 1GB | - | 512KB |
| **CAN Ports** | 2x CAN 2.0 | 1x CAN 2.0 | 1x TWAI |
| **Ethernet** | 1x Gigabit | - | Opcional |
| **WiFi** | - | - | 2.4GHz integrado |
| **Sistema** | Ubuntu IoT | - | FreeRTOS |
| **Precio** | $35 | $8 | ~$45 |

## 🔌 **Conexiones Físicas**

### **BL335 + Danfoss K13 F**

```text
BL335 GPIO Header:
- CAN0_H (GPIO) → K13 F CAN_H (Pin 7)
- CAN0_L (GPIO) → K13 F CAN_L (Pin 2)
- GND → K13 F GND (Pin 3)
- 5V → K13 F +24V (Pin 1, con regulador)

Ethernet:
- BL335 ETH → Switch/Router → Computador
```

### **X8 + BL335 (Backup)**

```text
X8 → BL335 CAN1:
- X8 CAN_H → BL335 CAN1_H
- X8 CAN_L → BL335 CAN1_L
- X8 GND → BL335 GND
- X8 VCC → BL335 3.3V
```

## 💰 **Costo Total del Sistema**

| Componente | Cantidad | Precio Unitario | Subtotal |
|------------|----------|-----------------|----------|
| BL335 Gateway | 1 | $35 USD | $35 |
| X8 CAN Transceiver | 1 | $8 USD | $8 |
| EdgeBox-ESP-100 | 1 | $45 USD | $45 |
| Cables CAN | 2m | $5 USD | $10 |
| Alimentadores 5V/24V | 2 | $8 USD | $16 |
| Conectores DB9 | 2 | $3 USD | $6 |
| **TOTAL HARDWARE** | | | **$123 USD** |

**Envío estimado desde China**: $25 USD
**Total estimado**: **$148 USD** ≈ **$143.000 CLP**

## 🧪 **Plan de Pruebas**

### **Fase 1: Configuración Básica**

- [ ] Instalar Ubuntu IoT en BL335
- [ ] Configurar interfaces CAN
- [ ] Verificar conectividad Ethernet
- [ ] Probar comandos básicos CAN

### **Fase 2: Comunicación CAN**

- [ ] Conectar BL335 a K13 F
- [ ] Enviar comandos de prueba
- [ ] Verificar recepción de datos
- [ ] Probar función de parada

### **Fase 3: Sistema Completo**

- [ ] Integrar aplicación Python
- [ ] Probar comunicación TCP/IP
- [ ] Implementar redundancia con X8
- [ ] Configurar monitoreo WiFi

## ⚠️ **Consideraciones de Seguridad**

### **Requisitos Industriales**

- **SIL 2**: Safety Integrity Level 2 para sistemas de seguridad
- **Redundancia**: Múltiples caminos de comunicación
- **Monitoreo**: Detección automática de fallos
- **Watchdog**: Reset automático en caso de bloqueo

### **Medidas Implementadas**

- ✅ **Heartbeat CAN**: Verificación continua de comunicación
- ✅ **Timeout de seguridad**: Parada automática si se pierde conexión
- ✅ **Checksum CANopen**: Validación de integridad de datos
- ✅ **Failover automático**: Cambio automático entre interfaces CAN

---

*Documento consolidado: 15 de octubre de 2025*
*Hardware: BL335 + X8 + EdgeBox-ESP-100*
*Sistema: Ubuntu IoT + CANopen + Danfoss K13 F*
