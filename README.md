# Control de Puente Grúa - Sistema R13 CANopen

## 📋 Resumen Ejecutivo

Este sistema desarrolla una **solución de parada de emergencia remota** para puente grúa mediante un receptor Danfoss R13 con protocolo CANopen. La arquitectura consta de tres componentes: una aplicación de control en computador, un gateway Ethernet-CAN que traduce comandos TCP/IP a mensajes CANopen, y el receptor R13 que controla los motores del puente grúa. El proceso de parada funciona así: el computador envía un comando de emergencia al gateway via Ethernet, el gateway traduce el mensaje a protocolo CAN bus hacia el R13, que detiene inmediatamente todos los motores y envía confirmación de vuelta al computador. Las conexiones físicas incluyen comunicación Ethernet entre computador y gateway, cable CAN blindado con terminación 120Ω entre gateway y R13, y alimentación industrial 12V/24V DC.

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
2. Obtención del manual técnico y archivo EDS del Danfoss R13  
3. Desarrollo de la aplicación de control con interfaz gráfica
4. Integración y pruebas con hardware real

## 🔧 Arquitectura del Sistema

### Componentes Principales

El sistema implementa una arquitectura distribuida de tres capas que permite el control remoto seguro del puente grúa:

```
    COMPUTADOR DE PROCESAMIENTO       GATEWAY ETHERNET-CAN           DANFOSS R13 RECEIVER
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

## 🛠️ Opciones de Hardware

### Gateway Ethernet-CAN

**Industrial (Recomendado para Producción):**
- PEAK PCAN-Ethernet Gateway (~$300 USD)
- HMS Anybus X-gateway (~$400 USD) 
- Kvaser Ethernet-CAN Gateway (~$350 USD)
- Ventajas: Certificación industrial, soporte técnico, configuración plug-and-play

**Desarrollo/Prototipo:**
- ESP32-S3 + Transceiver TJA1050 (~$15 USD)
- Arduino UNO R4 WiFi + CAN Shield MCP2515 (~$50 USD)
- Raspberry Pi 4 + CAN HAT (~$120 USD)
- Ventajas: Económico, personalizable, fácil desarrollo

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

## 📊 Estado del Proyecto

**✅ Completado:**
- Arquitectura del sistema definida
- Protocolo CANopen implementado
- Gateway scripts desarrollados (ESP32, Raspberry Pi)
- Documentación técnica
- Suite de tests unitarios

**� En Proceso:**
- Selección final de hardware gateway
- Obtención de archivo EDS del Danfoss R13
- Desarrollo de interfaz gráfica

**� Próximos Pasos:**
1. Adquisición e instalación de gateway hardware
2. Pruebas con sistema real de puente grúa
3. Certificación de seguridad industrial
4. Integración con sistemas PLC existentes
