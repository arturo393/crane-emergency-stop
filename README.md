# Control de Puente Grúa - Sistema R13 CANopen

## 📋 Resumen Ejecutivo

Este sistema desarrolla una **solución de parada de emergencia remota** par### Gateways Hardware Recomendados

**Opciones de Gateway Ethernet-CAN evaluadas:**

#### Industriales (Profesionales)

- PEAK PCAN-Ethernet Gateway (~---

## 🛠️ Hardware Recomendado - EdgeBox Lite WiFi

### ✅ **Equipo Seleccionado: EdgeBox Lite WiFi**

Después de evaluar múltiples opciones, **recomendamos el EdgeBox Lite WiFi** como gateway ideal para tu proyecto:

#### 🎯 **¿Por qué EdgeBox Lite WiFi?**

| Característica | EdgeBox Lite WiFi | ✅ Cumple Requisito |
|----------------|-------------------|-------------------|
| **Sistema Operativo** | Ubuntu IoT 22.04 LTS | ✅ Compatible 100% |
| **CAN Bus** | Puerto CAN nativo | ✅ CANopen listo |
| **Ethernet** | Gigabit Ethernet | ✅ Comunicación industrial |
| **WiFi** | 802.11ac integrado | ✅ Configuración remota |
| **Procesador** | ARM Cortex-A53 | ✅ Suficiente para control |
| **Precio** | ~$180 USD | ✅ Costo accesible |
| **Certificaciones** | CE, FCC Industrial | ✅ Entorno puente grúa |

#### 📋 **Especificaciones Técnicas**
- **CPU:** Rockchip RK3566 Quad-core ARM Cortex-A55 @ 1.8GHz
- **RAM:** 2GB LPDDR4
- **Almacenamiento:** 16GB eMMC
- **Conectividad:** Ethernet Gigabit + WiFi + CAN Bus + USB
- **Alimentación:** 5V DC (USB-C)
- **Temperatura:** -20°C a 60°C
- **Tamaño:** Compacto (100x70x25mm)

#### 📚 **Documentación del EdgeBox**
- **[Especificaciones Completas](docs/edgebox_lite_wifi_specs.md)** - Detalles técnicos completos
- **[Cotización Alibaba](docs/alibaba_edgebox_quote.md)** - Email y búsquedas preparadas
- **[Script de Configuración](scripts/edgebox_setup.py)** - Configuración automática

#### 🛒 **Dónde Comprar**
- **Alibaba:** Buscar "EdgeBox Lite WiFi" (~$150-200 USD)
- **Chile:** RS Components, Farnell, DigiKey
- **Internacional:** Seeed Studio, Mouser Electronics

#### 💰 **Costo Total Estimado**
| Componente | Precio (CLP) | Precio (USD) |
|------------|--------------|--------------|
| EdgeBox Lite WiFi | $350.000 | $180 |
| Cable CAN + Terminadores | $15.000 | $8 |
| Antena WiFi externa | $25.000 | $13 |
| Alimentación Industrial | $30.000 | $15 |
| **TOTAL** | **$420.000** | **$216** |

---

## 📊 Estado del Proyecto

**✅ Completado:**
- Arquitectura del sistema definida
- Protocolo CANopen implementado
- **Hardware seleccionado: EdgeBox Lite WiFi**
- Scripts de configuración preparados
- Documentación técnica completa
- Suite de tests unitarios
- Repositorio GitHub optimizado

**🔄 En Proceso:**
- Obtención de archivo EDS del Danfoss R13
- Desarrollo de interfaz gráfica

**🎯 Próximos Pasos:**
1. **Adquirir EdgeBox Lite WiFi** (Alibaba o distribuidores locales)
2. **Configurar hardware** con script `edgebox_setup.py`
3. **Pruebas de integración** con receptor R13
4. **Certificación de seguridad industrial**
5. **Integración con sistemas PLC existentes**C200 Controller (~$400 USD) 
- HMS Anybus X-gateway (~$400 USD)
- **Revolution Pi Connect+ SE** (~$350 USD) ⭐ **RECOMENDADO**

#### Económicas (Prototipos/DIY)

- ESP32-S3 + Transceiver TJA1050 (~$15 USD)
- Raspberry Pi 4 + MCP2515 CAN HAT (~$80 USD)
- BeagleBone Black + CAN Cape (~$90 USD)

#### Alibaba - Gateways Industriales Chinos (Precio/Calidad)

- **USR-CANET200** (~$70 USD) - Ethernet-CAN básico
- **ZLG CANNET-200I** (~$120 USD) - Industrial profesional
- **Gateways ARM Linux con CAN** (~$150-200 USD) - Programables

📄 **[Ver cotización completa para Alibaba](docs/alibaba_quote_request.md)**  
🔗 **[Enlaces de búsqueda directos](docs/alibaba_search_links.md)**ediante un receptor Danfoss R13 con protocolo CANopen. La arquitectura consta de tres componentes: una aplicación de control en computador, un gateway Ethernet-CAN que traduce comandos TCP/IP a mensajes CANopen, y el receptor R13 que controla los motores del puente grúa. El proceso de parada funciona así: el computador envía un comando de emergencia al gateway via Ethernet, el gateway traduce el mensaje a protocolo CAN bus hacia el R13, que detiene inmediatamente todos los motores y envía confirmación de vuelta al computador. Las conexiones físicas incluyen comunicación Ethernet entre computador y gateway, cable CAN blindado con terminación 120Ω entre gateway y R13, y alimentación industrial 12V/24V DC.

```
                     SISTEMA COMPLETO DE PARADA DE EMERGENCIA

    ┌─────────────────┐    Wifi         ┌─────────────────┐    CAN Bus     ┌─────────────────┐
    │   COMPUTADOR    │    TCP/IP       │     GATEWAY     │   CANopen      │   DANFOSS R13   │
    │                 │◄─────────────-─►│                 │◄──────────────►│                 │
    │ • Control App   │  1. Comando     │ • ETH ↔ CAN     │ 2. Mensaje     │ • Receptor      │
    │ • Emergency API │     Parada      │ • Protocol      │    Industrial  │ • Motor Control │
    │ • Interface     │                 │   Bridge        │                │ • Status Mon.   │
    └─────────────────┘                 └─────────────────┘                └─────────────────┘
            │                                    │                                   │
            │ 4. Confirmación                    │ 3. Confirmación                   │
            │    "Parada OK"                     │    Status                         ▼
            └────────────────────────────────────┴───────────────────┌─────────────────────┐
                                                                     │      MOTORES        │
                                                                     │   PUENTE GRÚA       │
                                                                     │                     │
    PROCESO:                                                         │ ████ PARADA ████    │
    1. Computador → Gateway (Comando parada via Ethernet)            │                     │
    2. Gateway → R13 (Mensaje CANopen via CAN Bus)                   │                     │
    3. R13 → Motores (Detención inmediata + Status)                  │                     │
    4. R13 → Computador (Confirmación parada completada)             │                     │
                                                                     └─────────────────────┘
    
    CONEXIONES FÍSICAS:
    • Wifi: Computador ↔ Gateway 
    • CAN Bus: Gateway ↔ R13 (Cable blindado, Terminación 120Ω)  
    • Alimentación: 12V/24V DC Industrial
```

## 🎯 ¿Qué es este proyecto?

Este proyecto desarrolla un **sistema de parada de emergencia remota** para puente grúa que utiliza un **receptor Danfoss R13** con protocolo CANopen. El objetivo es crear una aplicación que permita detener el puente grúa de forma segura desde una computadora remota.

**Arquitectura:** La comunicación se realiza a través de un Gateway Ethernet-CAN que traduce comandos TCP/IP a mensajes CANopen, permitiendo que la aplicación de control remoto detenga directamente el receptor R13 y sus variadores asociados.

**Estado actual:** Sistema base programado y documentado. Falta seleccionar el hardware gateway, obtener especificaciones técnicas del R13, y desarrollar la interfaz de usuario final.

**Próximos pasos:**

1. Selección y adquisición del Gateway Ethernet-CAN
2. Obtención del manual técnico y archivo EDS del Danfoss K13 F
3. Desarrollo de la aplicación de control con interfaz gráfica
4. Integración y pruebas con hardware real

## 🔧 Arquitectura del Sistema

### Componentes Principales

El sistema implementa una arquitectura distribuida de tres capas que permite el control remoto seguro del puente grúa:

```
    COMPUTADOR DE PROCESAMIENTO       GATEWAY ETHERNET-CAN           DANFOSS K13 F RECEIVER
    ┌─────────────────────────────┐   ┌─────────────────────────┐   ┌────────────────────────┐
    │                             │   │                         │   │                        │
    │  ┌─────────────────────────┐│   │  ┌───────────────────┐  │   │ ┌────────────────────┐ │
    │  │  CONTROL APPLICATION   │ │   │  │  PROTOCOL BRIDGE  │  │   │ │   CANOPEN STACK    │ │
    │  │                        │ │   │  │                   │  │   │ │                    │ │
    │  │  • R13Controller       │ │   │  │ TCP/IP ←→ CANopen │  │   │ │ • Message Process. │ │
    │  │  • CANopen Protocol    │ │   │  │                   │  │   │ │ • Motor Control    │ │
    │  │  • Command Interface   │ │   │  │ • Message Trans.  │  │   │ │ • Status Feedback  │ │
    │  └────────────────────────┘ │   │  └───────────────────┘  │   │ └────────────────────┘ │
    │                             │   │                         │   │                        │
    └─────────────────────────────┘   └─────────────────────────┘   └────────────────────────┘
                 │                                 │                               │
                 │          ETHERNET               │            CAN BUS            │
                 │       192.168.1.xxx             │                               │
                 │        Port: 9999               │                               │
                 └─────────────────────────────────┘───────────────────────────────┘
                                                                    │
                                                   ┌─────────────────────────┐
                                                   │      MOTORES            │
                                                   │   PUENTE GRÚA           │
                                                   │                         │
                                                   │  • Motor Carro          │
                                                   │  • Motor Gancho         │
                                                   │  • Motor Puente         │
                                                   │  • Sensores Posición    │
                                                   └─────────────────────────┘
```

### Secuencia de Comunicación

**Flujo de Datos Simplificado:**

```
    USUARIO                APLICACIÓN              GATEWAY               R13 RECEIVER
       │                      │                      │                      │
       │ 1. Botón Parada      │                      │                      │
       │ ───────────────────► │                      │                      │
       │                      │ 2. Comando JSON      │                      │
       │                      │ ───────────────────► │                      │
       │                      │                      │ 3. Mensaje CAN       │
       │                      │                      │ ───────────────────► │
       │                      │                      │                      │ 4. PARADA MOTORES
       │                      │                      │                      │ ████████████████
       │                      │                      │                      │
       │                      │                      │ 5. Confirmación CAN  │
       │                      │                      │ ◄─────────────────── │
       │                      │ 6. Respuesta JSON    │                      │
       │                      │ ◄─────────────────── │                      │
       │ 7. "Parada OK"       │                      │                      │
       │ ◄─────────────────── │                      │                      │
```

**En palabras simples:**
1. **Usuario presiona parada** → Aplicación recibe comando
2. **Aplicación envía JSON** → Gateway traduce a lenguaje CAN
3. **Gateway envía CAN** → R13 recibe y detiene motores inmediatamente
4. **R13 confirma parada** → Gateway recibe confirmación  
5. **Gateway responde JSON** → Aplicación confirma al usuario

**Tiempo total del proceso: < 100ms**

### Conexiones Físicas

```
                         IMPLEMENTACIÓN HARDWARE

    ┌─────────────────┐                    ┌─────────────────┐                    ┌─────────────────┐
    │   COMPUTADOR    │    Ethernet/WiFi   │    GATEWAY      │       CAN Bus      │   DANFOSS R13   │
    │ DE PROCESAMIENTO│◄──────────────────►│  ETHERNET-CAN   │◄──────────────────►│    RECEIVER     │
    │                 │   192.168.1.xxx    │                 │   Twisted Pair     │                 │
    │  Control App    │    Port: 9999      │ ETH ←→ CAN      │   Shielded Cable   │  CANopen Node   │
    │  IP: Auto       │                    │                 │   120Ω Term       │                 │
    └─────────────────┘                    │ CAN_H ──────────┼────────────────────┼──── CAN_H IN   │
                                           │ CAN_L ──────────┼────────────────────┼──── CAN_L IN   │
                                           │ Industrial      │                    │                 │
                                           │ Grade Gateway   │                    │                 │
                                           └─────────────────┘                    └─────────────────┘
                                                    │                                       │
                                           ┌─────────────────┐                    ┌─────────────────┐
                                           │   ALIMENTACIÓN  │                    │   MOTORES       │
                                           │   12V/24V DC    │                    │   PUENTE GRÚA   │
                                           │ Fuente Switching│                    │ • Motor Carro   │
                                           └─────────────────┘                    │ • Motor Gancho  │
                                                                                  │ • Motor Puente  │
                                                                                  └─────────────────┘
```

---

## 🛠️ **Hardware Seleccionado**

### **Configuración Final del Sistema**

**✅ EQUIPOS SELECCIONADOS:**
- **[BL335 Gateway](docs/hardware_final_selection.md)** ($35 USD) - Gateway principal Ethernet-CAN con Ubuntu IoT
- **[X8 CAN Transceiver](docs/hardware_final_selection.md)** ($8 USD) - Backup CAN para redundancia
- **[EdgeBox-ESP-100](docs/hardware_final_selection.md)** (~$45 USD) - Gateway WiFi secundario

**📊 COSTO TOTAL:** ~$148 USD (≈$143.000 CLP) incluyendo envío

**🏗️ ARQUITECTURA IMPLEMENTADA:**
```
COMPUTADOR ──Ethernet──► BL335 ──CAN──► Danfoss K13 F ──► MOTORES PUENTE GRÚA
                    │         │
                    └──X8────┘ (Backup CAN)
                    │
                    └──EdgeBox-ESP-100 (WiFi Monitor)
```

**[📋 Documentación Completa del Hardware](docs/hardware_final_selection.md)** - Especificaciones técnicas, configuración, diagramas de conexión y plan de pruebas.

---

## 🚀 Instalación y Uso

### Requisitos del Sistema

```bash
# Clonar repositorio
git clone <repository-url>
cd puente_grua

# Configurar entorno Python 3.12+
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuración

Editar `config/k13_config.yaml`:

```yaml
network:
  gateway_ip: "192.168.1.100"
  gateway_port: 9999
  
canopen:
  baudrate: 250000
  timeout: 5.0
  
safety:
  emergency_stop_enabled: true
  max_response_time: 500ms
```

### API de Control

```python
from src.k13_controller.main import R13Controller

controller = R13Controller()
controller.connect("192.168.1.100", 9999)

# Comando de parada de emergencia
controller.emergency_stop()

# Verificar estado del sistema
status = controller.get_status()
```

---

## � Documentación Convertida

**Optimización de Documentación:** Los archivos PDF originales han sido convertidos a formato Markdown para reducir significativamente el tamaño del repositorio y mejorar la accesibilidad.

### Archivos Convertidos

| Documento Original | Tamaño Original | Versión Markdown | Tamaño Final | Reducción |
|-------------------|----------------|------------------|--------------|-----------|
| `BC292382016572en-000201.pdf` | 3.5 MB | [BC292382016572en-000201.md](docs/BC292382016572en-000201.md) | 17 KB | 99.5% |
| `EMISOR IK3.pdf` | 528 KB | [EMISOR IK3.md](docs/EMISOR%20IK3.md) | 3.8 KB | 99.3% |
| `Manual Gama TM70 Pupitre.pdf` | 22 MB | [Manual Gama TM70 Pupitre.md](docs/Manual%20Gama%20TM70%20Pupitre.md) | 190 KB | 99.1% |
| `RECEPTOR K13 F.pdf` | 272 KB | [RECEPTOR K13 F.md](docs/RECEPTOR%20K13%20F.md) | 3.0 KB | 98.9% |

**Beneficios:**
- ✅ **Reducción total del 99.2%** en tamaño de documentación (26MB → 214KB)
- ✅ **Mejor versionado** con Git (diffs legibles)
- ✅ **Búsqueda mejorada** en GitHub
- ✅ **Renderizado automático** en navegadores
- ✅ **Edición colaborativa** simplificada

**Script de Conversión:** `scripts/convert_pdfs_to_markdown.py` (usa pdfplumber + Python)

---

## 📊 **Estado del Proyecto**

**✅ Completado:**
- Arquitectura del sistema definida y hardware seleccionado
- Protocolo CANopen implementado
- Documentación técnica completa (PDFs convertidos a Markdown)
- Suite de tests unitarios
- **Hardware final seleccionado:** BL335 + X8 + EdgeBox-ESP-100

**🔄 En Proceso:**
- Adquisición de hardware (BL335, X8, EdgeBox-ESP-100)
- Desarrollo de drivers para BL335 con Ubuntu IoT
- Configuración de comunicación CANopen con Danfoss K13 F

**🎯 Próximos Pasos:**
1. **Compra inmediata:** BL335 ($35), X8 ($8), EdgeBox-ESP-100 (~$45)
2. **Configuración BL335:** Instalar Ubuntu IoT, configurar CAN bus
3. **Pruebas de comunicación:** BL335 ↔ Danfoss K13 F
4. **Desarrollo interfaz:** Aplicación de control con monitoreo en tiempo real
5. **Certificación industrial:** Validación de seguridad SIL 2
