# Guía de Configuración - Hardware Seleccionado

## 🎯 **Configuración BL335 + X8 + EdgeBox-ESP-100**

Esta guía detalla la configuración paso a paso de los equipos seleccionados para el sistema de parada de emergencia del puente grúa.

### **1. BL335 - Gateway Principal**

#### **Especificaciones Técnicas**
- **CPU:** Allwinner H3 (ARM Cortex-A7 Quad-core @1.2GHz)
- **RAM:** 1GB DDR3
- **Almacenamiento:** 8GB eMMC
- **Interfaces:** 1x Gigabit Ethernet, 2x CAN 2.0, USB 2.0
- **Sistema:** Ubuntu IoT compatible

#### **Instalación del Sistema Operativo**
```bash
# Descargar imagen Ubuntu IoT para ARM
wget https://ubuntu.com/download/iot/arm64 -O ubuntu-iot-arm64.img

# Flashear en tarjeta SD/microSD
sudo dd if=ubuntu-iot-arm64.img of=/dev/sdX bs=4M status=progress

# Insertar SD en BL335 y encender
# Conectar via Ethernet y SSH
ssh ubuntu@bl335.local  # IP por defecto: 192.168.1.100
```

#### **Configuración de Red**
```bash
# Configurar IP estática
sudo nmcli con mod "Wired connection 1" ipv4.addresses "192.168.1.100/24"
sudo nmcli con mod "Wired connection 1" ipv4.gateway "192.168.1.1"
sudo nmcli con mod "Wired connection 1" ipv4.dns "8.8.8.8"
sudo nmcli con up "Wired connection 1"

# Verificar conectividad
ping 192.168.1.1
```

#### **Configuración CAN Bus**
```bash
# Instalar herramientas CAN
sudo apt update
sudo apt install can-utils python3-can python3-socketcan

# Cargar módulos CAN
sudo modprobe can
sudo modprobe can_raw
sudo modprobe mcp251x

# Configurar interfaz CAN0 (principal)
sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up

# Configurar interfaz CAN1 (backup con X8)
sudo ip link set can1 type can bitrate 250000
sudo ip link set can1 up

# Verificar interfaces
ip link show can0
ip link show can1
```

#### **Instalación de Dependencias Python**
```bash
# Instalar Python y pip
sudo apt install python3 python3-pip python3-venv

# Crear entorno virtual
python3 -m venv ~/k13_env
source ~/k13_env/bin/activate

# Instalar dependencias del proyecto
pip install pyserial pyyaml canopen numpy
```

### **2. X8 - Transceiver CAN de Backup**

#### **Conexión Física con BL335**
```
X8 Module → BL335 GPIO Header:
- X8 CAN_H → BL335 CAN1_H (GPIO correspondiente)
- X8 CAN_L → BL335 CAN1_L (GPIO correspondiente)
- X8 GND → BL335 GND
- X8 VCC → BL335 3.3V
```

#### **Configuración de Redundancia**
```bash
# Script de monitoreo de redundancia CAN
#!/bin/bash
while true; do
    # Verificar CAN0 (principal)
    if ! ip link show can0 | grep -q "UP"; then
        echo "CAN0 down, switching to CAN1"
        # Lógica de failover
    fi

    # Verificar CAN1 (backup)
    if ! ip link show can1 | grep -q "UP"; then
        echo "CAN1 down, using CAN0 only"
    fi

    sleep 5
done
```

### **3. EdgeBox-ESP-100 - Gateway WiFi**

#### **Instalación del Entorno de Desarrollo**
```bash
# Instalar ESP-IDF
mkdir -p ~/esp
cd ~/esp
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh
. ./export.sh
```

#### **Configuración del Proyecto**
```bash
# Crear proyecto ESP-IDF
idf.py create-project k13_monitor
cd k13_monitor

# Configurar WiFi
idf.py menuconfig
# → Component config → WiFi → WiFi Mode → Station
# → Component config → WiFi → SSID: "CRANE_CONTROL"
# → Component config → WiFi → Password: "crane2024"
```

#### **Configuración CAN Bus en ESP32**
```c
// main.c - Configuración CAN
#include "driver/twai.h"

void app_main() {
    // Configuración TWAI (CAN)
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(GPIO_NUM_21, GPIO_NUM_22, TWAI_MODE_NORMAL);
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_250KBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    // Instalar driver TWAI
    ESP_ERROR_CHECK(twai_driver_install(&g_config, &t_config, &f_config));
    ESP_ERROR_CHECK(twai_start());

    // Configuración WiFi
    wifi_init_sta();
}
```

#### **Conexión Física**
```
ESP32-S3 GPIO → CAN Transceiver:
- GPIO 21 (TX) → CAN RX
- GPIO 22 (RX) → CAN TX
- GND → CAN GND
- 3.3V → CAN VCC
```

## 🔧 **Configuración del Sistema Completo**

### **Diagrama de Conexiones**
```
┌─────────────────┐    Ethernet     ┌──────────────┐    CAN Bus     ┌───────────┐
│   COMPUTADOR    │◄──────────────►│   BL335       │◄──────────────►│ DANFOSS   │
│                 │   192.168.1.x  │   Gateway     │   250 kbps     │   K13 F   │
│ Control App     │   Port: 9999   │   + Ubuntu    │   Primary      │ RECEIVER  │
└─────────────────┘                └──────────────┘                └───────────┘
                                         │ CAN1 (Backup)
                                         ▼
                                  ┌──────────────┐
                                  │   X8 CAN     │
                                  │  Transceiver │
                                  │   (Redund.)  │
                                  └──────────────┘

                                  ┌──────────────┐    WiFi        ┌─────────────┐
                                  │ EdgeBox-ESP  │◄──────────────►│  Monitoreo  │
                                  │ WiFi Monitor │   2.4GHz       │   Remoto    │
                                  └──────────────┘               └─────────────┘
```

### **Configuración de Redundancia**
```python
# config/redundancy_config.yaml
network:
  primary_gateway: "192.168.1.100:9999"
  backup_gateway: "192.168.1.101:9999"  # EdgeBox-ESP
  wifi_monitor: "192.168.4.100:8080"

can:
  primary_interface: "can0"
  backup_interface: "can1"
  bitrate: 250000
  timeout: 100  # ms

safety:
  heartbeat_interval: 500  # ms
  max_response_time: 1000  # ms
  auto_failover: true
```

### **Script de Inicio del Sistema**
```bash
#!/bin/bash
# scripts/start_system.sh

echo "Iniciando Sistema de Parada de Emergencia Puente Grúa"

# Verificar conectividad de red
ping -c 3 192.168.1.100

# Iniciar servicios CAN
sudo systemctl start can0
sudo systemctl start can1

# Iniciar aplicación principal
cd /home/ubuntu/puente_grua
source k13_env/bin/activate
python src/k13_controller/main.py &

# Iniciar monitoreo WiFi (EdgeBox)
# Conectar via WiFi y ejecutar monitor

echo "Sistema iniciado correctamente"
```

## 🧪 **Pruebas de Configuración**

### **Prueba Básica de Comunicación**
```bash
# Enviar mensaje de prueba CAN
cansend can0 123#DEADBEEF

# Monitorear mensajes CAN
candump can0

# Probar conectividad TCP
telnet 192.168.1.100 9999
```

### **Prueba de Redundancia**
```bash
# Simular fallo en CAN0
sudo ip link set can0 down

# Verificar que CAN1 toma el control
candump can1

# Restaurar CAN0
sudo ip link set can0 up
```

### **Prueba de Monitoreo WiFi**
```bash
# Conectar al AP del EdgeBox-ESP
nmcli device wifi connect "CRANE_CONTROL" password "crane2024"

# Verificar datos de monitoreo
curl http://192.168.4.100:8080/status
```

## ⚠️ **Consideraciones de Seguridad**

### **Configuración Industrial**
- **Aislamiento Eléctrico:** Usar transceivers con aislamiento galvanico
- **Protección ESD:** Implementar protección contra descargas electrostáticas
- **Redundancia:** Configurar failover automático entre interfaces CAN
- **Monitoreo:** Implementar watchdog para reinicio automático

### **Certificaciones Requeridas**
- **SIL 2:** Safety Integrity Level 2 para sistemas de seguridad
- **IP65:** Protección contra polvo y agua
- **EMC:** Compatibilidad electromagnética
- **ATEX:** Para entornos explosivos (opcional)

## 📋 **Lista de Verificación de Configuración**

### **BL335 Gateway**
- [ ] Ubuntu IoT instalado y actualizado
- [ ] IP estática configurada (192.168.1.100)
- [ ] Interfaces CAN configuradas (can0, can1)
- [ ] Dependencias Python instaladas
- [ ] Servicio de aplicación configurado

### **X8 CAN Transceiver**
- [ ] Conexión física correcta con BL335
- [ ] Configuración de redundancia implementada
- [ ] Pruebas de failover realizadas

### **EdgeBox-ESP-100**
- [ ] ESP-IDF instalado y configurado
- [ ] WiFi configurado como Access Point
- [ ] CAN bus configurado en ESP32
- [ ] Aplicación de monitoreo compilada

### **Sistema Completo**
- [ ] Comunicación TCP/IP verificada
- [ ] Protocolo CANopen implementado
- [ ] Funciones de seguridad probadas
- [ ] Documentación de configuración completa

---

*Guía actualizada: 14 de octubre de 2025*
*Hardware: BL335 + X8 + EdgeBox-ESP-100*
*Sistema: Ubuntu IoT + CANopen + Danfoss K13 F*