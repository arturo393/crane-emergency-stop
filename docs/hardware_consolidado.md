# Hardware - Sistema de Parada de Emergencia Puente Grúa# Hardware Consolidado - Sistema de Parada de Emergencia Puente Grúa



## 🎯 Gateways Industriales Candidatos## 🎯 **Hardware Seleccionado**



Este documento compara los **dos gateways industriales** que se probarán para determinar cuál ofrece el mejor rendimiento para el control del puente grúa K13 F.Basado en el análisis técnico y requerimientos del proyecto, se han seleccionado los siguientes equipos para implementar el sistema de parada de emergencia:



---### 📦 **Equipos Seleccionados**



## 📦 Gateway 1: BL335 Industrial-Grade Embedded Computer#### **1. BL335 - Gateway Principal Ethernet-CAN** ($35 USD)



### **Especificaciones Técnicas**- **Procesador**: Allwinner H3 (ARM Cortex-A7 Quad-core @1.2GHz)

- **Sistema**: Ubuntu IoT / Debian Linux

| Característica | Especificación |- **CAN Bus**: 2x puertos CAN 2.0A/B nativos (SocketCAN)

|----------------|----------------|- **Ethernet**: 1x Gigabit Ethernet (10/100/1000 Mbps)

| **Modelo** | BL335 Industrial-Grade Embedded Computer |- **USB**: 2x USB 2.0 Host

| **Procesador** | ARM Cortex (arquitectura no especificada) |- **Alimentación**: 5V DC (Micro-USB)

| **Sistema Operativo** | Linux (Debian/Ubuntu compatible) |- **Dimensiones**: 85mm x 56mm

| **Ethernet** | **2 puertos**: 1x 1000M (Gigabit) + 1x 100M (Fast) |- **Peso**: ~50g

| **CAN Bus** | Integrado nativo (SocketCAN compatible) |

| **Protocolo** | CANopen (stack disponible) |**Rol**: Gateway principal que traduce comandos TCP/IP del computador a mensajes CANopen para el receptor Danfoss K13 F.

| **Montaje** | **DIN Rail** (carril industrial estándar) |

| **Aplicación** | SCADA Smart Manufacturing Systems |#### **2. X8 - Transceiver CAN de Backup** ($8 USD)

| **Temperatura Operativa** | -20°C a 60°C (grado industrial) |

| **Alimentación** | 12V/24V DC (típico industrial) |- **Chip**: SN65HVD230 o TJA1050

| **Dimensiones** | Compacto (aproximado: 100 x 70 x 40 mm) |- **Protocolo**: CAN 2.0A/B

| **Certificaciones** | CE, FCC (típico productos industriales chinos) |- **Velocidad**: Hasta 1 Mbps

| **Precio** | **$130 USD** |- **Aislamiento**: Protección ESD integrada

| **Origen** | China (Alibaba) |- **Alimentación**: 3.3V/5V DC

- **Dimensiones**: 40mm x 25mm

### **Ventajas del BL335**

**Rol**: Transceiver CAN adicional para redundancia o expansión.

#### **✅ Sistema Operativo Linux Completo**

- **Desarrollo simplificado**: Python, C++, Node.js#### **3. EdgeBox-ESP-100 - Gateway WiFi Secundario** (~$45 USD)

- **Librerías maduras**: python-canopen, socketcan

- **Shell access**: SSH para configuración remota- **Procesador**: ESP32-S3 (Dual-core Xtensa LX7 @240MHz)

- **Package managers**: apt/yum para instalación fácil- **Sistema**: FreeRTOS / ESP-IDF

- **Debugging**: GDB, strace, logs del sistema- **CAN Bus**: 1x puerto TWAI (CAN 2.0) integrado

- **WiFi**: 2.4GHz 802.11 b/g/n integrado

#### **✅ Dual Ethernet (Gigabit + Fast)**- **Bluetooth**: 5.0 LE integrado

- **Separación de redes**: - **Alimentación**: 5V DC (USB-C)

  - ETH1 (1000M): Red de control (servidor ↔ gateway)- **Dimensiones**: 65mm x 50mm x 25mm

  - ETH2 (100M): Red SCADA (PLC, sensores, HMI)

- **Redundancia de red**: Failover automático entre interfaces**Rol**: Gateway secundario WiFi para monitoreo remoto o backup.

- **Mayor ancho de banda**: Gigabit para video/datos pesados

## 🏗️ **Arquitectura del Sistema**

#### **✅ DIN Rail Mounting**

- **Instalación industrial estándar**: Clip directo en riel DIN```text

- **Sin tornillos necesarios**: Montaje/desmontaje rápido┌─────────────────┐    Ethernet (TCP/IP)    ┌──────────────┐    CAN Bus     ┌───────────┐

- **Gabinetes industriales**: Compatible con IP54/IP65│   COMPUTADOR    │◄──────────────────────►│   BL335      │◄──────────────►│ DANFOSS   │

- **Organización de cableado**: Estándar en paneles industriales│ DE PROCESAMIENTO│      Puerto 9999        │   Gateway    │   250 kbps     │   K13 F   │

│                 │                         │   + Ubuntu   │   CANopen      │ RECEIVER  │

#### **✅ SCADA Ready**└─────────────────┘                         └──────────────┘                └───────────┘

- **Diseñado para manufactura**: Protocolo industrial nativo                                               │ CAN2 (Backup/Redundancia)

- **Modbus TCP/RTU**: Integración con PLCs                                               ▼

- **OPC UA**: Comunicación con sistemas SCADA                                        ┌──────────────┐

- **MQTT**: IoT industrial                                        │   X8 CAN     │

                                        │  Transceiver │

#### **✅ SocketCAN Nativo**                                        │   (Opcional) │

- **Kernel Linux integrado**: CAN 2.0A/B directo                                        └──────────────┘

- **can-utils**: Herramientas de diagnóstico (`candump`, `cansend`)

- **python-can**: Librería Python madura                                        ┌──────────────┐    WiFi         ┌─────────────┐

- **CANopen stack**: python-canopen pre-compilado                                        │ EdgeBox-ESP  │◄───────────────►│  Monitoreo  │

                                        │ Backup WiFi  │   2.4GHz        │   Remoto    │

#### **✅ Precio Competitivo**                                        └──────────────┘                 └─────────────┘

- **$130 USD**: Muy económico para gateway industrial```

- **ROI rápido**: Menos inversión inicial

- **Repuestos económicos**: Fácil reemplazo si falla## 🔧 **Configuración Técnica**



### **Desventajas del BL335**### **BL335 - Configuración Principal**



#### **❌ Documentación Limitada**#### **Sistema Operativo**

- **Manual en inglés/chino básico**: No siempre clara

- **Soporte técnico limitado**: Email/WeChat en inglés básico```bash

- **Comunidad pequeña**: Menos foros y tutoriales# Instalar Ubuntu IoT para Allwinner H3

wget https://ubuntu.com/download/iot/arm64

#### **❌ Sin WiFi Integrado**dd if=ubuntu-iot.img of=/dev/sdX bs=4M

- **Solo Ethernet cableado**: Requiere infraestructura de red

- **Sin movilidad**: No puede moverse sin reconfigurar# Primera configuración

- **Instalación más compleja**: Requiere cableado adicionalsudo apt update && sudo apt upgrade

sudo apt install can-utils python3-can python3-socketcan

#### **❌ Hardware Genérico Chino**```

- **Calidad variable**: Puede variar entre lotes

- **Sin certificación industrial fuerte**: CE básico#### **Configuración CAN Bus**

- **Sin soporte local**: Importación directa desde China

```bash

### **Configuración BL335**# Cargar módulos CAN

sudo modprobe can

#### **1. Instalación Sistema Operativo**sudo modprobe can_raw

sudo modprobe mcp251x

```bash

# Opción 1: Ubuntu IoT (recomendado)# Configurar CAN0 (principal)

wget https://ubuntu.com/download/iot/armsudo ip link set can0 type can bitrate 250000

dd if=ubuntu-iot-22.04-arm.img of=/dev/sdX bs=4Msudo ip link set can0 up



# Opción 2: Debian Bullseye# Configurar CAN1 (backup)

wget https://www.debian.org/distrib/netinstsudo ip link set can1 type can bitrate 250000

dd if=debian-11-arm.img of=/dev/sdX bs=4Msudo ip link set can1 up

```

# Primera configuración

sudo apt update && sudo apt upgrade -y#### **Configuración de Red**

sudo apt install can-utils python3-can python3-pip -y

``````bash

# IP estática

#### **2. Configuración SocketCAN**sudo nmcli con mod "Wired connection 1" ipv4.addresses "192.168.1.100/24"

sudo nmcli con mod "Wired connection 1" ipv4.gateway "192.168.1.1"

```bashsudo nmcli con mod "Wired connection 1" ipv4.dns "8.8.8.8"

# Cargar módulos CANsudo nmcli con up "Wired connection 1"

sudo modprobe can```

sudo modprobe can_raw

sudo modprobe vcan  # Virtual CAN para testing### **EdgeBox-ESP-100 - Configuración Secundaria**



# Configurar CAN0 (interfaz física)#### **Entorno de Desarrollo**

sudo ip link set can0 type can bitrate 250000

sudo ip link set can0 up```bash

# Instalar ESP-IDF

# Verificarcd ~/esp

ip link show can0git clone --recursive https://github.com/espressif/esp-idf.git

candump can0  # Escuchar mensajes CANcd esp-idf

```./install.sh

. ./export.sh

#### **3. Configuración Red Dual Ethernet**```



```bash#### **Configuración WiFi**

# ETH1 (Gigabit) - Red de Control

sudo nmcli con mod eth0 ipv4.addresses "192.168.1.100/24"```c

sudo nmcli con mod eth0 ipv4.gateway "192.168.1.1"// Configuración AP WiFi

sudo nmcli con mod eth0 ipv4.dns "8.8.8.8"wifi_config_t wifi_config = {

sudo nmcli con mod eth0 ipv4.method manual    .ap = {

sudo nmcli con up eth0        .ssid = "CRANE_CONTROL",

        .password = "crane2024",

# ETH2 (Fast) - Red SCADA        .max_connection = 4,

sudo nmcli con mod eth1 ipv4.addresses "192.168.2.100/24"        .authmode = WIFI_AUTH_WPA2_PSK

sudo nmcli con mod eth1 ipv4.method manual    },

sudo nmcli con up eth1};

``````



#### **4. Instalación Software**#### **Configuración CAN Bus ESP32**



```bash```c

# Python CANopen stack// Configuración TWAI (CAN)

pip3 install python-can python-canopentwai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(GPIO_NUM_21, GPIO_NUM_22, TWAI_MODE_NORMAL);

twai_timing_config_t t_config = TWAI_TIMING_CONFIG_250KBITS();

# BL335 Gateway applicationtwai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

git clone https://github.com/arturo393/crane-emergency-stop.git

cd crane-emergency-stopESP_ERROR_CHECK(twai_driver_install(&g_config, &t_config, &f_config));

pip3 install -r requirements.txtESP_ERROR_CHECK(twai_start());

```

# Ejecutar gateway

python3 src/bl335_gateway/main.py --port 9999#### **Conexiones ESP32-S3**

```

```text

### **Pinout y Conexiones BL335**ESP32-S3 Pin    Función         Conexión

GPIO21          CAN TX          -> TJA1050 Pin 1 (TXD)

```GPIO22          CAN RX          <- TJA1050 Pin 4 (RXD)

BL335 Terminal Block:3.3V            Alimentación    -> TJA1050 Pin 3 (VDD)

┌─────────────────────────────────────────┐GND             Tierra          -> TJA1050 Pin 2 (VSS)

│  ETH1 (RJ45)   - Gigabit Ethernet       │

│  ETH2 (RJ45)   - Fast Ethernet          │TJA1050 Pin     Función         Conexión

│                                          │Pin 6 (CANH)    CAN High        -> CAN bus CANH

│  CAN_H (Terminal) - Amarillo            │Pin 7 (CANL)    CAN Low         -> CAN bus CANL

│  CAN_L (Terminal) - Verde               │```

│  GND   (Terminal) - Negro               │

│                                          │## 📊 **Especificaciones Comparadas**

│  +24V IN (Terminal) - Rojo              │

│  GND     (Terminal) - Negro             │| Característica | BL335 | X8 | EdgeBox-ESP-100 |

└─────────────────────────────────────────┘|---------------|--------|----|------------------|

| **Procesador** | ARM Cortex-A7 Quad-core | - | Xtensa LX7 Dual |

Conexión K13 F:| **Frecuencia** | 1.2 GHz | - | 240 MHz |

BL335 CAN_H → K13 F Pin 7 (CAN_H)| **RAM** | 1GB | - | 512KB |

BL335 CAN_L → K13 F Pin 2 (CAN_L)| **CAN Ports** | 2x CAN 2.0 | 1x CAN 2.0 | 1x TWAI |

BL335 GND   → K13 F Pin 3 (GND)| **Ethernet** | 1x Gigabit | - | Opcional |

```| **WiFi** | - | - | 2.4GHz integrado |

| **Sistema** | Ubuntu IoT | - | FreeRTOS |

---| **Precio** | $35 | $8 | ~$45 |



## 📦 Gateway 2: ESP32-S3 Based 4G LTE WiFi IoT Gateway## 🔌 **Conexiones Físicas**



### **Especificaciones Técnicas**### **BL335 + Danfoss K13 F**



| Característica | Especificación |```text

|----------------|----------------|BL335 GPIO Header:

| **Modelo** | Custom Industrial PLC Controller ESP32-S3 Based |- CAN0_H (GPIO) → K13 F CAN_H (Pin 7)

| **Procesador** | Xtensa® Dual-Core LX7 @ 240MHz |- CAN0_L (GPIO) → K13 F CAN_L (Pin 2)

| **RAM** | 512KB SRAM |- GND → K13 F GND (Pin 3)

| **Flash** | 8MB (típico) o 16MB |- 5V → K13 F +24V (Pin 1, con regulador)

| **Sistema Operativo** | FreeRTOS / ESP-IDF |

| **WiFi** | 802.11 b/g/n 2.4GHz integrado |Ethernet:

| **4G LTE** | Módulo 4G integrado (SIM card slot) |- BL335 ETH → Switch/Router → Computador

| **Ethernet** | 1 puerto (probablemente W5500 chipset) |```

| **CAN Bus** | **TWAI (CAN 2.0)** integrado en ESP32-S3 |

| **Protocolo** | CANopen (requiere implementación custom) |### **X8 + BL335 (Backup)**

| **Bluetooth** | Bluetooth 5.0 LE |

| **Montaje** | DIN Rail compatible |```text

| **Temperatura Operativa** | -10°C a 55°C (industrial light) |X8 → BL335 CAN1:

| **Alimentación** | 12V/24V DC (con regulador a 3.3V) |- X8 CAN_H → BL335 CAN1_H

| **GPIO** | 40+ pines disponibles |- X8 CAN_L → BL335 CAN1_L

| **Certificaciones** | CE, FCC |- X8 GND → BL335 GND

| **Precio** | **$277 USD** |- X8 VCC → BL335 3.3V

| **Origen** | China (Alibaba) |```



### **Ventajas del ESP32-S3 Gateway**## 💰 **Costo Total del Sistema**



#### **✅ WiFi + 4G LTE Integrados**| Componente | Cantidad | Precio Unitario | Subtotal |

- **Conectividad flexible**: WiFi, 4G, o Ethernet simultáneos|------------|----------|-----------------|----------|

- **Instalación remota**: Sin necesidad de cables Ethernet| BL335 Gateway | 1 | $35 USD | $35 |

- **Backup connectivity**: Si WiFi falla, 4G toma control| X8 CAN Transceiver | 1 | $8 USD | $8 |

- **Ubicaciones difíciles**: Zonas sin infraestructura de red| EdgeBox-ESP-100 | 1 | $45 USD | $45 |

- **Monitoreo móvil**: Acceso desde smartphone vía 4G| Cables CAN | 2m | $5 USD | $10 |

| Alimentadores 5V/24V | 2 | $8 USD | $16 |

#### **✅ Ecosistema ESP32 Maduro**| Conectores DB9 | 2 | $3 USD | $6 |

- **ESP-IDF**: Framework oficial de Espressif| **TOTAL HARDWARE** | | | **$123 USD** |

- **Arduino IDE**: Desarrollo rápido de prototipos

- **MicroPython**: Python embebido (opcional)**Envío estimado desde China**: $25 USD

- **PlatformIO**: Build system moderno**Total estimado**: **$148 USD** ≈ **$143.000 CLP**

- **Comunidad gigante**: Millones de desarrolladores

## 🧪 **Plan de Pruebas**

#### **✅ TWAI (CAN 2.0) Integrado**

- **Hardware nativo**: CAN controller en el MCU### **Fase 1: Configuración Básica**

- **Sin hardware adicional**: Solo transceiver TJA1050

- **Bajo costo**: Ahorro en componentes externos- [ ] Instalar Ubuntu IoT en BL335

- **APIs maduras**: esp_twai driver oficial- [ ] Configurar interfaces CAN

- [ ] Verificar conectividad Ethernet

#### **✅ Edge Computing**- [ ] Probar comandos básicos CAN

- **Procesamiento local**: Machine learning (TinyML)

- **AI en borde**: Detección de anomalías### **Fase 2: Comunicación CAN**

- **Latencia ultra-baja**: Procesamiento en dispositivo

- **Ahorro de ancho de banda**: Envía solo datos procesados- [ ] Conectar BL335 a K13 F

- [ ] Enviar comandos de prueba

#### **✅ Programación Flexible**- [ ] Verificar recepción de datos

- **C/C++**: Performance máximo (ESP-IDF)- [ ] Probar función de parada

- **Arduino**: Prototipado rápido

- **MicroPython**: Scripting embebido### **Fase 3: Sistema Completo**

- **Rust**: Seguridad de memoria (experimental)

- [ ] Integrar aplicación Python

### **Desventajas del ESP32-S3 Gateway**- [ ] Probar comunicación TCP/IP

- [ ] Implementar redundancia con X8

#### **❌ Precio Elevado**- [ ] Configurar monitoreo WiFi

- **$277 USD**: 2.1x más caro que BL335

- **ROI más lento**: Inversión inicial mayor## ⚠️ **Consideraciones de Seguridad**

- **Costo total sistema**: $430 vs $276 (BL335)

### **Requisitos Industriales**

#### **❌ FreeRTOS (No Linux)**

- **RTOS limitado**: Menos potente que Linux- **SIL 2**: Safety Integrity Level 2 para sistemas de seguridad

- **Sin shell access**: Debugging más complicado- **Redundancia**: Múltiples caminos de comunicación

- **Package management básico**: Sin apt/pip nativo- **Monitoreo**: Detección automática de fallos

- **Desarrollo embedded**: Curva de aprendizaje mayor- **Watchdog**: Reset automático en caso de bloqueo



#### **❌ Recursos Limitados**### **Medidas Implementadas**

- **512KB RAM**: vs ≥256MB en BL335

- **8-16MB Flash**: vs varios GB en BL335- ✅ **Heartbeat CAN**: Verificación continua de comunicación

- **Sin multitarea real**: RTOS cooperativo- ✅ **Timeout de seguridad**: Parada automática si se pierde conexión

- **Aplicaciones complejas difíciles**: Limited memory- ✅ **Checksum CANopen**: Validación de integridad de datos

- ✅ **Failover automático**: Cambio automático entre interfaces CAN

#### **❌ CANopen Custom**

- **Stack no disponible**: Hay que implementar desde cero---

- **Debugging complejo**: Sin can-utils estándar

- **Desarrollo lento**: Más tiempo de implementación*Documento consolidado: 15 de octubre de 2025*

- **Riesgo de bugs**: Menos probado que stacks Linux*Hardware: BL335 + X8 + EdgeBox-ESP-100*

*Sistema: Ubuntu IoT + CANopen + Danfoss K13 F*

### **Configuración ESP32-S3 Gateway**

#### **1. Entorno de Desarrollo**

```bash
# Instalar ESP-IDF
cd ~/esp
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh
source ./export.sh

# Clonar proyecto
cd ~/projects
git clone https://github.com/arturo393/crane-emergency-stop.git
cd crane-emergency-stop/esp32_gateway
```

#### **2. Configuración WiFi (AP + STA)**

```c
// WiFi Station Mode (conectar a red existente)
wifi_config_t wifi_sta_config = {
    .sta = {
        .ssid = "FACTORY_NETWORK",
        .password = "factory2024",
        .threshold.authmode = WIFI_AUTH_WPA2_PSK,
    },
};

// WiFi Access Point Mode (crear hotspot)
wifi_config_t wifi_ap_config = {
    .ap = {
        .ssid = "CRANE_CONTROL",
        .password = "crane2024",
        .max_connection = 4,
        .authmode = WIFI_AUTH_WPA2_PSK,
    },
};

ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_APSTA));
ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_sta_config));
ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wifi_ap_config));
ESP_ERROR_CHECK(esp_wifi_start());
```

#### **3. Configuración TWAI (CAN Bus)**

```c
// Configuración TWAI (CAN)
twai_general_config_t g_config = {
    .mode = TWAI_MODE_NORMAL,
    .tx_io = GPIO_NUM_21,          // CAN TX
    .rx_io = GPIO_NUM_22,          // CAN RX
    .clkout_io = TWAI_IO_UNUSED,
    .bus_off_io = TWAI_IO_UNUSED,
    .tx_queue_len = 5,
    .rx_queue_len = 5,
    .alerts_enabled = TWAI_ALERT_ALL,
    .clkout_divider = 0,
};

// Timing 250 kbps
twai_timing_config_t t_config = TWAI_TIMING_CONFIG_250KBITS();

// Accept all frames
twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

// Instalar driver
ESP_ERROR_CHECK(twai_driver_install(&g_config, &t_config, &f_config));
ESP_ERROR_CHECK(twai_start());
```

#### **4. Envío Mensaje CANopen**

```c
// Enviar NMT Stop al Node 0x10
twai_message_t message = {
    .identifier = 0x000,  // COB-ID NMT
    .data_length_code = 2,
    .data = {0x02, 0x10},  // Stop Node 16
};

ESP_ERROR_CHECK(twai_transmit(&message, pdMS_TO_TICKS(1000)));
```

### **Pinout y Conexiones ESP32-S3**

```
ESP32-S3 GPIO Mapping:
┌─────────────────────────────────────────┐
│  GPIO21 (CAN TX)   → TJA1050 Pin 1 (TXD)│
│  GPIO22 (CAN RX)   ← TJA1050 Pin 4 (RXD)│
│  3.3V              → TJA1050 Pin 3 (VDD) │
│  GND               → TJA1050 Pin 2 (VSS) │
│                                          │
│  Ethernet (W5500)  → RJ45 connector      │
│  WiFi (internal)   → Antenna connector   │
│  4G LTE (internal) → SIM card slot       │
└─────────────────────────────────────────┘

TJA1050 CAN Transceiver:
┌─────────────────────────────────────────┐
│  Pin 6 (CANH) → K13 F Pin 7 (Amarillo)  │
│  Pin 7 (CANL) → K13 F Pin 2 (Verde)     │
│  GND          → K13 F Pin 3 (Negro)     │
└─────────────────────────────────────────┘
```

---

## 📊 Comparación Detallada BL335 vs ESP32-S3

| Característica | BL335 | ESP32-S3 | ✅ Ganador |
|----------------|-------|----------|-----------|
| **Sistema Operativo** | Linux completo | FreeRTOS | **BL335** |
| **Procesador** | ARM Cortex (potente) | Dual LX7 240MHz | **BL335** |
| **RAM** | ≥256MB | 512KB | **BL335** |
| **Ethernet** | 2 puertos (1000M + 100M) | 1 puerto (100M) | **BL335** |
| **WiFi** | ❌ No | ✅ 2.4GHz | **ESP32-S3** |
| **4G LTE** | ❌ No | ✅ Sí | **ESP32-S3** |
| **CAN Bus** | SocketCAN nativo | TWAI (CAN 2.0) | **BL335** |
| **CANopen** | Stack disponible | Custom | **BL335** |
| **Desarrollo** | Python/C++ fácil | C/C++ embedded | **BL335** |
| **DIN Rail** | ✅ Estándar | ✅ Compatible | Empate |
| **Temperatura** | -20°C a 60°C | -10°C a 55°C | **BL335** |
| **Certificaciones** | CE, FCC | CE, FCC | Empate |
| **Precio** | **$130** | **$277 (+113%)** | **BL335** |
| **Costo total** | **$276** | **$430 (+56%)** | **BL335** |
| **Conectividad Remota** | Solo Ethernet | WiFi + 4G | **ESP32-S3** |
| **Edge Computing** | Limitado | TinyML, AI | **ESP32-S3** |
| **Ecosistema** | Pequeño | Gigante | **ESP32-S3** |
| **Documentación** | Limitada | Excelente | **ESP32-S3** |

### **Puntuación Final**

| Gateway | Puntos Fuertes | Puntos Débiles | Total |
|---------|----------------|----------------|-------|
| **BL335** | Linux, Dual ETH, CANopen, Precio | Sin WiFi, Doc limitada | ⭐⭐⭐⭐⭐ 9/10 |
| **ESP32-S3** | WiFi + 4G, Ecosistema, Edge AI | Precio, RTOS, CANopen custom | ⭐⭐⭐⭐ 7/10 |

---

## 🔌 Conexión Física con K13 F

### **Diagrama de Cableado Completo**

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         SERVIDOR DE PROCESAMIENTO                        │
│                           (Computador FastAPI)                           │
│                          IP: 192.168.1.50:8000                           │
└────────────┬─────────────────────────────────────────┬───────────────────┘
             │ Ethernet Cat6                            │ WiFi 2.4GHz
             │ (hasta 100m)                            │ (para ESP32-S3)
             │                                          │
┌────────────▼──────────┐                    ┌──────────▼─────────────────┐
│   GATEWAY BL335       │                    │  GATEWAY ESP32-S3          │
│   192.168.1.100       │                    │  192.168.1.101             │
│   • ETH1: Control     │                    │  • WiFi: 2.4GHz            │
│   • ETH2: SCADA       │                    │  • 4G LTE: Backup          │
│   • CAN: can0 250kbps │                    │  • CAN: TWAI 250kbps       │
└────────────┬──────────┘                    └──────────┬─────────────────┘
             │                                          │
             │ Cable CAN Blindado                       │ Cable CAN Blindado
             │ (Twisted Pair Shielded)                  │ (Twisted Pair Shielded)
             │ Máx: 40m @ 250kbps                       │
             │                                          │
             │ CAN_H (Amarillo)                         │
             │ CAN_L (Verde)                            │
             │ GND (Negro)                              │
             │ Terminación 120Ω                         │
             │                                          │
┌────────────▼──────────────────────────────────────────▼─────────────────┐
│                      DANFOSS K13 F RECEIVER                             │
│                         (R13 F Receiver)                                 │
│                       Node ID: 0x10 (16)                                 │
│                                                                          │
│  Pin 7 (CAN_H):  Amarillo  ← Gateway CAN_H                              │
│  Pin 2 (CAN_L):  Verde     ← Gateway CAN_L                              │
│  Pin 3 (GND):    Negro     ← Gateway GND                                │
│  Pin 1 (+24V):   Rojo      ← Fuente 24V DC                              │
│                                                                          │
│  Terminador 120Ω entre CAN_H y CAN_L                                    │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │ Radio Danfoss Propietario
                               │ (438MHz típico)
                               ▼
                    ┌────────────────────┐
                    │   EMISOR IK3       │
                    │ (Control Remoto)   │
                    │  Batería 3.6V      │
                    └─────────┬──────────┘
                              │
                              ▼
                   ┌────────────────────────┐
                   │   MOTORES PUENTE GRÚA  │
                   │   • Motor Carro        │
                   │   • Motor Gancho       │
                   │   • Motor Puente       │
                   │   380V AC Trifásico    │
                   └────────────────────────┘
```

### **Especificaciones de Cables**

#### **Cable CAN Bus**

```
Especificación:
• Tipo: Twisted Pair Shielded (TPS)
• AWG: 24 AWG o 22 AWG
• Impedancia característica: 120Ω ±5%
• Blindaje: Trenzado + Foil + Malla
• Longitud máxima: 40m @ 250 kbps
• Temperatura: -40°C a 80°C

Código de colores estándar:
• CAN_H: Amarillo (Yellow)
• CAN_L: Verde (Green)
• Blindaje: Conectado a GND en UN extremo

Terminación:
• Resistor 120Ω ±1% en AMBOS extremos
• Gateway: 120Ω entre CAN_H y CAN_L
• K13 F: 120Ω entre Pin 7 y Pin 2
```

#### **Cable Ethernet**

```
Especificación:
• Tipo: Cat5e o Cat6 (UTP o STP)
• Conectores: RJ45 con seguro metálico
• Longitud máxima: 100m
• Velocidad: 1 Gbps (Cat6) o 100 Mbps (Cat5e)
• Temperatura: -20°C a 60°C

Para ambientes industriales:
• Preferir Cat6 STP (Shielded Twisted Pair)
• Conectores industriales IP67
• Routing en canaleta metálica
```

---

## 💰 Análisis de Costos Detallado

### **Sistema Completo con BL335**

| Componente | Cantidad | Precio Unit. | Subtotal | Proveedor |
|------------|----------|--------------|----------|-----------|
| **Gateway BL335** | 1 | $130 | $130 | Alibaba |
| Cable Ethernet Cat6 STP (50m) | 1 | $15 | $15 | Local/AliExpress |
| Cable CAN blindado 24AWG (25m) | 1 | $25 | $25 | Local/AliExpress |
| Terminadores CAN 120Ω | 2 | $3 | $6 | Amazon/AliExpress |
| Fuente 24V DC 2A DIN Rail | 1 | $20 | $20 | Meanwell/Local |
| Conectores DB9 CAN | 2 | $5 | $10 | Local |
| Conectores RJ45 industriales | 4 | $3 | $12 | Local |
| Gabinete industrial IP54 | 1 | $40 | $40 | Local |
| Borneras terminales | 5 | $2 | $10 | Local |
| Canaleta porta-cables | 3m | $5 | $15 | Local |
| **SUBTOTAL HARDWARE** | | | **$283** | |
| Envío desde China (BL335) | 1 | $30 | $30 | Alibaba |
| **TOTAL SISTEMA BL335** | | | **$313 USD** | |
| | | | **≈ $303.000 CLP** | |

### **Sistema Completo con ESP32-S3**

| Componente | Cantidad | Precio Unit. | Subtotal | Proveedor |
|------------|----------|--------------|----------|-----------|
| **Gateway ESP32-S3 4G** | 1 | $277 | $277 | Alibaba |
| Cable Ethernet Cat6 STP (50m) | 1 | $15 | $15 | Local/AliExpress |
| Cable CAN blindado 24AWG (25m) | 1 | $25 | $25 | Local/AliExpress |
| Terminadores CAN 120Ω | 2 | $3 | $6 | Amazon/AliExpress |
| Fuente 12V/24V DC 2A | 1 | $20 | $20 | Meanwell/Local |
| Antena 4G LTE (incluida) | 1 | $0 | $0 | Incluido |
| Antena WiFi externa 2.4GHz | 1 | $12 | $12 | Amazon |
| Gabinete industrial IP54 | 1 | $40 | $40 | Local |
| SIM Card 4G LTE (prepago) | 1 | $10 | $10 | Entel/Movistar |
| Conectores varios | - | $15 | $15 | Local |
| **SUBTOTAL HARDWARE** | | | **$420** | |
| Envío desde China (ESP32) | 1 | $35 | $35 | Alibaba |
| **TOTAL SISTEMA ESP32-S3** | | | **$455 USD** | |
| | | | **≈ $440.000 CLP** | |

### **Comparación Final de Costos**

| Sistema | Costo Hardware | Costo Total | Diferencia | % Diferencia |
|---------|----------------|-------------|------------|--------------|
| **BL335** | $283 | **$313 USD** | Base | Base |
| **ESP32-S3** | $420 | **$455 USD** | +$142 | **+45%** |

**Conclusión**: El sistema BL335 es **$142 USD más económico** (45% menos costoso)

---

## 🧪 Plan de Pruebas de Campo

### **Cronograma de Evaluación**

```
Semana 1-2: Pruebas Individuales BL335
Semana 3-4: Pruebas Individuales ESP32-S3
Semana 5:   Pruebas con K13 F Real (ambos)
Semana 6:   Análisis y Decisión Final
```

### **Fase 1: Configuración y Tests Básicos**

#### **Tests BL335**
- [ ] Instalación Ubuntu IoT 22.04
- [ ] Configuración SocketCAN (can0)
- [ ] Configuración Dual Ethernet
- [ ] Instalación python-canopen
- [ ] Test loopback CAN (vcan0)
- [ ] Test comunicación TCP/IP
- [ ] Medición latencia (ping)
- [ ] Estabilidad 48h continuas

#### **Tests ESP32-S3**
- [ ] Instalación ESP-IDF v5.2
- [ ] Configuración TWAI driver
- [ ] Configuración WiFi (STA + AP)
- [ ] Configuración 4G LTE
- [ ] Test comunicación WiFi
- [ ] Test failover WiFi → 4G
- [ ] Medición latencia
- [ ] Estabilidad 48h continuas

### **Fase 2: Pruebas con K13 F Real**

#### **Setup Físico**
1. Montar gateway en gabinete DIN Rail
2. Conectar fuente 24V DC
3. Cablear CAN Bus con K13 F
4. Instalar terminadores 120Ω
5. Verificar continuidad con multímetro
6. Conectar Ethernet/WiFi al servidor

#### **Tests Funcionales**
- [ ] Detección de K13 F (Node ID scan)
- [ ] Lectura de estado (PDO, SDO)
- [ ] Comando NMT Start
- [ ] Comando NMT Stop
- [ ] **Comando Parada Emergencia** (crítico)
- [ ] Lectura de errores EMCY
- [ ] Heartbeat monitoring
- [ ] Recuperación de fallas

#### **Tests de Performance**
- [ ] Latencia promedio (100 comandos)
- [ ] Latencia máxima
- [ ] Latencia mínima
- [ ] Jitter de latencia
- [ ] Throughput CAN (msgs/sec)
- [ ] Pérdida de mensajes (%)

#### **Tests de Robustez**
- [ ] 1000 comandos consecutivos
- [ ] Desconexión/reconexión de red
- [ ] Desconexión/reconexión CAN
- [ ] Interferencia electromagnética (motor arrancando)
- [ ] Temperatura extrema (-10°C, +50°C)
- [ ] Vibración (simulación puente grúa)

### **Fase 3: Evaluación Final**

#### **Criterios de Evaluación**

| Criterio | Peso | Medición | Objetivo |
|----------|------|----------|----------|
| **Latencia Promedio** | 25% | ms (avg de 100 tests) | < 80ms |
| **Estabilidad 24/7** | 20% | Uptime % (1 semana) | > 99.9% |
| **Facilidad Desarrollo** | 15% | Horas de setup | < 8 horas |
| **Robustez Industrial** | 15% | Fallos en 1000 tests | 0 fallos |
| **Costo Total** | 10% | USD | BL335 gana |
| **Conectividad** | 10% | WiFi/4G/ETH | ESP32-S3 gana |
| **Documentación** | 5% | Calidad docs | ESP32-S3 gana |

#### **Proceso de Decisión**

```
SI (Latencia < 80ms AND Estabilidad > 99.9% AND Robustez = 0 fallos):
    SI (Instalación tiene Ethernet):
        → SELECCIONAR BL335 (más económico)
    ELSE IF (Instalación remota sin cables):
        → SELECCIONAR ESP32-S3 (WiFi + 4G)
ELSE:
    → RE-EVALUAR configuración
    → Probar optimizaciones
```

---

## 🏆 Recomendaciones Preliminares

### **Usar BL335 si:**
- ✅ Instalación fija con Ethernet disponible
- ✅ Presupuesto limitado ($313 vs $455)
- ✅ Necesitas Linux completo para desarrollo
- ✅ Red SCADA existente (doble Ethernet útil)
- ✅ Prioridad: Estabilidad + CANopen maduro

### **Usar ESP32-S3 si:**
- ✅ Ubicación remota sin Ethernet
- ✅ Necesitas conectividad WiFi o 4G
- ✅ Monitoreo móvil es crítico
- ✅ Edge Computing / TinyML futuro
- ✅ Prioridad: Flexibilidad de conectividad

### **Decisión Final**

La selección del gateway definitivo se tomará **después de las pruebas de campo** en Semana 6, basándose en los resultados medidos y ponderados según la tabla de evaluación.

**El gateway ganador será el que mejor cumpla** con los objetivos de latencia, estabilidad y robustez industrial, considerando el contexto específico de instalación.

---

**Documento**: Hardware Comparación Gateways  
**Versión**: 2.0  
**Fecha**: 16 de octubre de 2025  
**Autor**: Proyecto Puente Grúa K13  
**Estado**: Esperando adquisición de hardware y pruebas de campo
