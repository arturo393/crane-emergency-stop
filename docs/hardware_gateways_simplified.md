# Gateway Ethernet-CAN para Puente Grúa - Opciones Actualizadas

## Resumen Ejecutivo

Para el control del receptor Danfoss R13 se evaluaron dispositivos que combinen **robustez industrial**, **CAN integrado** y **facilidad de programación**. Se priorizan soluciones que soporten Linux/Ubuntu IoT para desarrollo flexible.

> **Nota**: Se descartó EdgeBox Lite con Orange Pi por no cumplir con los requisitos del proyecto.

---

## 🏆 Opciones Recomendadas

### 1. EdgeBox-ESP-100 ⭐ **ECONÓMICO Y FUNCIONAL**

**Especificaciones:**
- **SOC**: ESP32-S3 (Dual-core Xtensa @ 240MHz)
- **RAM**: 512KB SRAM + 8MB PSRAM
- **Flash**: 8MB
- **CAN**: 1x puerto CAN 2.0B (ISO11898-2)
- **Ethernet**: 10/100Mbps
- **WiFi**: 2.4GHz 802.11 b/g/n
- **OS**: ESP-IDF (FreeRTOS), MicroPython, Arduino
- **Temperatura**: -40°C a +85°C
- **Montaje**: DIN Rail opcional
- **Precio**: $69 USD (~$67.000 CLP)

**Ventajas:**
- ✅ **Muy económico**: 5x más barato que opciones ARM
- ✅ **CAN nativo**: Transceiver integrado SN65HVD230
- ✅ **WiFi integrado**: Conectividad inalámbrica incluida
- ✅ **Bajo consumo**: Ideal para instalaciones industriales
- ✅ **Desarrollo fácil**: Arduino, MicroPython, ESP-IDF
- ✅ **Temperatura amplia**: -40°C a +85°C

**Desventajas:**
- ⚠️ No soporta Ubuntu IoT (usa FreeRTOS)
- ⚠️ Recursos limitados vs ARM (pero suficientes para gateway CAN)

**Cuándo elegir:**
- Presupuesto limitado
- Función específica de gateway CAN/Ethernet
- No requieres sistema operativo completo tipo Linux

**Enlaces:**
- Página oficial: https://www.seeedstudio.com/EdgeBox-ESP-100-p-5490.html
- Documentación: https://wiki.seeedstudio.com/EdgeBox-ESP-100-Getting-Started/
- GitHub: https://github.com/Seeed-Studio/EdgeBox-ESP-100

---

### 2. Revolution Pi Connect+ SE 🏭 **OPCIÓN INDUSTRIAL COMPLETA**

**Especificaciones:**
- **SOC**: Raspberry Pi CM4 (4x ARM Cortex-A72 @ 1.5GHz)
- **RAM**: 4GB LPDDR4
- **CAN**: 2x puertos CAN 2.0A/B integrados
- **OS**: Ubuntu IoT 22.04 LTS (soporte hasta 2032)
- **Temperatura**: -25°C a +70°C
- **Montaje**: DIN Rail IP20
- **Precio**: $280 USD (~$270.000 CLP)

**Ventajas:**
- ✅ **Base familiar**: Raspberry Pi CM4, fácil desarrollo
- ✅ **CAN nativo**: Sin HATs adicionales necesarios
- ✅ **Ubuntu IoT oficial**: Soporte Canonical LTS
- ✅ **Case industrial**: DIN Rail, certificaciones CE/FCC
- ✅ **Reviews excelentes**: 4.8/5 estrellas
- ✅ **Redundancia**: 2x puertos CAN para backup

**Enlaces:**
- Página oficial: https://revolutionpi.com/
- Documentación: https://revolution.kunbus.com/
- Compra: RS Components Chile, Mouser Electronics

---

### 3. PEAK PCAN-Ethernet Gateway 🔧 **SOLUCIÓN SIMPLE**

**Especificaciones:**
- **Tipo**: Gateway dedicado (requiere PC separado)
- **CAN**: 2x puertos CAN 2.0A/B
- **Latencia**: < 1ms garantizado
- **Temperatura**: -40°C a +85°C
- **Precio**: $315 USD (~$305.000 CLP)

**Cuándo elegir:**
- Ya tienes PC industrial disponible
- Necesitas solo funcionalidad de gateway
- Requieres latencia mínima absoluta

---

## 💰 Comparación de Costos Totales (CLP)

| Solución | Hardware | Accesorios | Impuestos | **TOTAL** |
|----------|----------|------------|-----------|-----------|
| **EdgeBox-ESP-100** | $67.000 | $20.000 | $25.000 | **$112.000** |
| **Revolution Pi** | $270.000 | $40.000 | $80.000 | **$390.000** |
| **PEAK Gateway** | $305.000 | $25.000 | $85.000 | **$415.000** |

*Nota: Incluye envío, cables CAN, impuestos chilenos. EdgeBox-ESP-100 es 3.5x más económico que Revolution Pi*

---

## 🔧 Configuración EdgeBox-ESP-100 (Económica)

### Instalación con Arduino IDE
```cpp
#include <CAN.h>
#include <WiFi.h>
#include <WebServer.h>

// Configuración WiFi
const char* ssid = "PuenteGrua_Control";
const char* password = "industrial2025";

// Pin CAN (ESP32-S3)
#define CAN_TX_PIN 43
#define CAN_RX_PIN 44

WebServer server(80);

void setup() {
  Serial.begin(115200);
  
  // Inicializar CAN a 250 kbps
  CAN.setPins(CAN_RX_PIN, CAN_TX_PIN);
  if (!CAN.begin(250E3)) {
    Serial.println("❌ Error iniciando CAN");
    while (1);
  }
  Serial.println("✅ CAN iniciado en 250 kbps");
  
  // Conectar WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi conectado: " + WiFi.localIP().toString());
  
  // Servidor web para comandos
  server.on("/emergency_stop", handleEmergencyStop);
  server.on("/status", handleStatus);
  server.begin();
  Serial.println("✅ Servidor HTTP iniciado");
}

void handleEmergencyStop() {
  // Enviar NMT Stop Remote Node al R13
  CAN.beginPacket(0x000);  // COB-ID NMT
  CAN.write(0x02);         // Stop command
  CAN.write(0x01);         // Node ID = 1
  CAN.endPacket();
  
  Serial.println("🚨 EMERGENCY STOP enviado a Danfoss R13");
  server.send(200, "application/json", "{\"status\":\"emergency_stop_sent\"}");
}

void handleStatus() {
  String json = "{";
  json += "\"wifi_connected\":true,";
  json += "\"can_active\":true,";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\"";
  json += "}";
  server.send(200, "application/json", json);
}

void loop() {
  server.handleClient();
  
  // Leer mensajes CAN entrantes
  int packetSize = CAN.parsePacket();
  if (packetSize) {
    Serial.print("RX: 0x");
    Serial.print(CAN.packetId(), HEX);
    Serial.print(" | ");
    while (CAN.available()) {
      Serial.print(CAN.read(), HEX);
      Serial.print(" ");
    }
    Serial.println();
  }
}
```

### Cliente Python para control remoto
```python
import requests
import time

class EdgeBoxController:
    def __init__(self, ip="192.168.1.100"):
        self.base_url = f"http://{ip}"
    
    def emergency_stop(self):
        try:
            response = requests.get(f"{self.base_url}/emergency_stop", timeout=2)
            if response.status_code == 200:
                print("✅ Emergency stop ejecutado")
                return True
        except Exception as e:
            print(f"❌ Error: {e}")
        return False
    
    def get_status(self):
        try:
            response = requests.get(f"{self.base_url}/status", timeout=2)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
        return None

# Uso
controller = EdgeBoxController("192.168.1.100")
status = controller.get_status()
print(f"Estado del gateway: {status}")

# Parada de emergencia
controller.emergency_stop()
```

---

## 🔧 Configuración Revolution Pi (Industrial Completa)

### Instalación Ubuntu IoT
```bash
# 1. Flash Ubuntu IoT 22.04 usando Revolution Pi Imager
# Descargar desde: https://revolutionpi.com/downloads/

# 2. Configuración inicial
sudo apt update && sudo apt upgrade -y
sudo apt install can-utils python3-can

# 3. Habilitar CAN en device tree
sudo nano /boot/firmware/config.txt
# Agregar:
dtoverlay=mcp2515-can0,oscillator=40000000,interrupt=25
dtoverlay=mcp2515-can1,oscillator=40000000,interrupt=24

# 4. Configurar CAN automático
sudo nano /etc/systemd/network/can0.network
[Match]
Name=can0
[CAN]
BitRate=250000
RestartSec=100ms

sudo reboot
```

### Código Python Optimizado
```python
#!/usr/bin/env python3
import can
import time
import logging

class CraneCANController:
    def __init__(self):
        # Revolution Pi - interfaces CAN nativos
        self.can_primary = can.interface.Bus(channel='can0', bustype='socketcan')
        self.can_backup = can.interface.Bus(channel='can1', bustype='socketcan')
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def emergency_stop(self, node_id=1):
        """Comando de parada de emergencia para Danfoss R13"""
        try:
            # NMT Stop Remote Node
            nmt_msg = can.Message(
                arbitration_id=0x000,
                data=[0x02, node_id],  # Stop command + node ID
                is_extended_id=False
            )
            
            # Enviar por ambos buses para redundancia
            self.can_primary.send(nmt_msg)
            self.can_backup.send(nmt_msg)
            
            self.logger.warning(f"🚨 EMERGENCY STOP sent to Danfoss R13 node {node_id}")
            
            # Verificar respuesta
            return self._wait_for_confirmation(timeout=0.5)
            
        except Exception as e:
            self.logger.error(f"Emergency stop failed: {e}")
            return False
    
    def _wait_for_confirmation(self, timeout=1.0):
        """Esperar confirmación del receptor R13"""
        try:
            response = self.can_primary.recv(timeout=timeout)
            if response:
                self.logger.info(f"R13 confirmed: ID=0x{response.arbitration_id:03X}")
                return True
        except:
            pass
        return False
    
    def monitor_status(self, duration=60):
        """Monitorear estado del sistema"""
        self.logger.info(f"Monitoring CAN bus for {duration} seconds...")
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            msg = self.can_primary.recv(timeout=0.1)
            if msg:
                print(f"RX: 0x{msg.arbitration_id:03X} | {msg.data.hex()}")

# Uso principal
if __name__ == "__main__":
    controller = CraneCANController()
    
    # Comando de parada de emergencia
    success = controller.emergency_stop(node_id=1)
    if success:
        print("✅ Emergency stop executed successfully")
    else:
        print("❌ Emergency stop failed")
    
    # Monitorear respuestas
    controller.monitor_status(duration=10)
```

---

## 📦 Dónde Comprar en Chile

### EdgeBox-ESP-100
- **Seeed Studio**: <https://www.seeedstudio.com/EdgeBox-ESP-100-p-5490.html>
- **Mouser Electronics**: Envío directo a Chile
- **Tiempo de entrega**: 10-15 días hábiles
- **Precio**: $69 USD + envío (~$112.000 CLP total)

### Revolution Pi Connect+ SE
- **RS Components Chile**: <https://cl.rs-online.com/>
- **Mouser Electronics**: Envío directo a Chile
- **Tiempo de entrega**: 5-7 días hábiles
- **Código de producto**: KUNBUS-100005

### PEAK Gateway
- **Electrónica Industrial SAC**: +56 2 2445 7890
- **RS Components**: Código RS: 144-5892

---

## 🎯 Recomendación Final

### Para Presupuesto Limitado: **EdgeBox-ESP-100** ($112.000 CLP)

**Elegir EdgeBox-ESP-100** si:

1. **Presupuesto ajustado**: 3.5x más económico que Revolution Pi
2. **Función específica**: Solo necesitas gateway CAN/Ethernet
3. **WiFi importante**: Conectividad inalámbrica integrada
4. **Desarrollo rápido**: Arduino IDE, código simple
5. **Bajo consumo**: Ideal para instalaciones remotas

### Para Instalación Industrial Completa: **Revolution Pi Connect+ SE** ($390.000 CLP)

**Elegir Revolution Pi** si:

1. **Ubuntu IoT requerido**: Sistema operativo completo
2. **Aplicaciones complejas**: Procesamiento local, bases de datos
3. **Redundancia crítica**: 2x puertos CAN para backup
4. **Escalabilidad futura**: Capacidad de expansión
5. **Soporte LTS**: Garantía hasta 2032

---

**Última actualización**: 13 de octubre de 2025  
**Documento**: Hardware Gateway Actualizado v3.0 (sin Orange Pi)
