# Arquitectura del Sistema de Parada de Emergencia - Puente Grúa

## 📋 Resumen Ejecutivo

Sistema de **parada de emergencia remota** para puente grúa basado en receptor **Danfoss K13 F (R13 F)** con protocolo **CANopen**. El sistema utiliza un gateway industrial que traduce comandos TCP/IP a mensajes CANopen, permitiendo el control remoto desde una aplicación web.

**Objetivo**: Detener el puente grúa de forma segura y remota desde cualquier computador en la red industrial.

---

## 🏗️ Arquitectura General del Sistema

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│                            SISTEMA COMPLETO                                        │
│                                                                                    │
│  ┌──────────────┐    Ethernet      ┌─────────────┐    CAN Bus     ┌────────────┐ │
│  │  SERVIDOR    │◄─────────────────►│   GATEWAY   │◄───────────────►│  DANFOSS   │ │
│  │ Web UI/API   │   TCP/IP JSON    │  Industrial │   CANopen      │  K13 F     │ │
│  │ (FastAPI)    │   192.168.1.x    │ Ethernet→CAN│   250 kbps     │  Receiver  │ │
│  └──────────────┘                  └─────────────┘                └────────────┘ │
│                                            │                             │         │
│                                            │                             ▼         │
│                                            │                    ┌────────────────┐ │
│                                            │                    │   MOTORES      │ │
│                                            │                    │  PUENTE GRÚA   │ │
│                                            │                    │ • Carro        │ │
│                                            │                    │ • Gancho       │ │
│                                            │                    │ • Puente       │ │
│                                            ▼                    └────────────────┘ │
│                                   ┌─────────────────┐                             │
│                                   │   ALIMENTACIÓN  │                             │
│                                   │   12V/24V DC    │                             │
│                                   │   Industrial    │                             │
│                                   └─────────────────┘                             │
└────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Gateways Candidatos - Comparación

Se evaluarán **DOS gateways industriales** para determinar cuál ofrece mejor rendimiento, confiabilidad y flexibilidad:

### **Opción 1: ARMxy BL335** 
**Industrial-Grade Embedded Computer**

| Especificación | Detalle |
|----------------|---------|
| **Modelo** | BL335 Industrial-Grade Embedded Computer |
| **Procesador** | ARM Cortex (no especificado exactamente) |
| **Sistema Operativo** | Linux (Debian/Ubuntu compatible) |
| **Ethernet** | 1x 1000M + 1x 100M Ethernet |
| **CAN Bus** | Integrado (SocketCAN compatible) |
| **Protocolo** | CANopen nativo |
| **Montaje** | DIN Rail (carril industrial) |
| **Aplicación** | SCADA Smart Manufacturing |
| **Temperatura** | -20°C a 60°C (grado industrial) |
| **Precio** | **$130 USD** |
| **Origen** | China (Alibaba) |

#### Ventajas BL335
- ✅ **Linux nativo**: Fácil desarrollo con Python/C++
- ✅ **Dual Ethernet**: Red redundante o separación de tráfico
- ✅ **DIN Rail**: Instalación industrial estándar
- ✅ **SCADA Ready**: Diseñado para manufactura inteligente
- ✅ **SocketCAN**: Integración directa con stack CANopen
- ✅ **Bajo costo**: $130 USD es muy competitivo

#### Desventajas BL335
- ❌ Documentación limitada (producto chino)
- ❌ Soporte técnico en inglés/chino
- ❌ Sin WiFi integrado

---

### **Opción 2: Custom Industrial PLC Controller**
**ESP32-S3 Based 4G LTE WiFi IoT Gateway**

| Especificación | Detalle |
|----------------|---------|
| **Modelo** | ESP32-S3 Based 4G LTE WiFi IoT Gateway |
| **Procesador** | Xtensa® Dual-Core LX7 @ 240MHz |
| **Sistema Operativo** | FreeRTOS / ESP-IDF |
| **Conectividad** | WiFi 2.4GHz + 4G LTE |
| **Ethernet** | Sí (probablemente W5500) |
| **CAN Bus** | TWAI (CAN 2.0) integrado ESP32-S3 |
| **Protocolo** | CANopen (requiere implementación) |
| **Montaje** | DIN Rail compatible |
| **Temperatura** | -10°C a 55°C (industrial light) |
| **Precio** | **$277 USD** |
| **Origen** | China (Alibaba) |

#### Ventajas ESP32-S3 Gateway
- ✅ **WiFi + 4G LTE**: Conectividad flexible y remota
- ✅ **ESP32-S3**: Ecosistema maduro (ESP-IDF, Arduino)
- ✅ **TWAI nativo**: CAN 2.0 integrado en MCU
- ✅ **Edge Computing**: Procesamiento local IoT
- ✅ **Programación flexible**: C/C++, MicroPython, Arduino

#### Desventajas ESP32-S3 Gateway
- ❌ **Precio elevado**: $277 USD (2.1x más caro que BL335)
- ❌ **RTOS**: FreeRTOS menos potente que Linux
- ❌ **Recursos limitados**: RAM/Flash menor que Linux
- ❌ **CANopen**: Requiere implementación custom

---

## 📊 Comparación Detallada

| Característica | BL335 ($130) | ESP32-S3 Gateway ($277) | ✅ Mejor |
|----------------|--------------|-------------------------|---------|
| **SO** | Linux completo | FreeRTOS | BL335 |
| **Ethernet** | 2x (1000M + 100M) | 1x (100M típico) | BL335 |
| **WiFi** | ❌ No | ✅ 2.4GHz | ESP32-S3 |
| **4G LTE** | ❌ No | ✅ Sí | ESP32-S3 |
| **CAN Bus** | SocketCAN nativo | TWAI (CAN 2.0) | BL335 |
| **CANopen** | Stack disponible | Implementación custom | BL335 |
| **Procesador** | ARM (potente) | Dual-core 240MHz | BL335 |
| **RAM** | ≥256MB típico | 512KB SRAM | BL335 |
| **Desarrollo** | Python/C++ fácil | C/C++ embedded | BL335 |
| **DIN Rail** | ✅ Estándar | ✅ Compatible | Empate |
| **Temperatura** | -20°C a 60°C | -10°C a 55°C | BL335 |
| **Precio** | $130 | $277 | BL335 |
| **Conectividad Remota** | Solo Ethernet | WiFi + 4G | ESP32-S3 |

### **Puntuación Final**

| Gateway | Puntos | Recomendación |
|---------|--------|---------------|
| **BL335** | ⭐⭐⭐⭐⭐ (9/10) | **IDEAL para instalación fija con Ethernet** |
| **ESP32-S3** | ⭐⭐⭐⭐ (7/10) | **Mejor para ubicaciones remotas con WiFi/4G** |

---

## 🔌 Conexiones Físicas Detalladas

### **Configuración con BL335**

```
                    CONEXIONES BL335 → SERVIDOR → K13 F

┌──────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│  SERVIDOR DE PROCESAMIENTO                                                      │
│  (Computador con FastAPI)                                                       │
│  IP: 192.168.1.50                                                               │
│  Puerto: 8000 (Web UI)                                                          │
│                                                                                  │
└─────────────────┬────────────────────────────────────────────────────────────────┘
                  │
                  │ Cable Ethernet Cat5e/6
                  │ (hasta 100 metros)
                  │
┌─────────────────▼────────────────────────────────────────────────────────────────┐
│                                                                                  │
│  GATEWAY BL335                                                                   │
│  • ETH1 (1000M): 192.168.1.100 → Servidor                                      │
│  • ETH2 (100M): 192.168.2.100 → Red SCADA (opcional)                           │
│  • CAN: can0 @ 250 kbps                                                        │
│  • Montaje: DIN Rail en gabinete industrial                                     │
│  • Alimentación: 24V DC                                                         │
│                                                                                  │
└─────────────────┬────────────────────────────────────────────────────────────────┘
                  │
                  │ Cable CAN Bus Blindado
                  │ (Twisted Pair Shielded)
                  │ Máximo: 40 metros @ 250 kbps
                  │
                  │ Terminación: 120Ω en ambos extremos
                  │
┌─────────────────▼────────────────────────────────────────────────────────────────┐
│                                                                                  │
│  DANFOSS K13 F (R13 F) RECEIVER                                                 │
│  • Node ID: 0x10 (16 decimal)                                                  │
│  • CAN_H (Pin 7): Amarillo                                                     │
│  • CAN_L (Pin 2): Verde                                                        │
│  • GND (Pin 3): Negro                                                          │
│  • Terminación: 120Ω resistor                                                  │
│                                                                                  │
└─────────────────┬────────────────────────────────────────────────────────────────┘
                  │
                  │ Conexión Radio
                  │ (Protocolo propietario Danfoss)
                  │
                  ▼
       ┌────────────────────┐
       │  EMISOR IK3        │
       │  (Control Remoto)  │
       └────────────────────┘
                  │
                  ▼
       ┌────────────────────────┐
       │   MOTORES PUENTE GRÚA  │
       │   • Motor Carro        │
       │   • Motor Gancho       │
       │   • Motor Puente       │
       └────────────────────────┘
```

#### **Pinout BL335**

```
BL335 Terminal Block:
┌─────────────────────────────────┐
│  ETH1 (RJ45) - Gigabit Ethernet │
│  ETH2 (RJ45) - Fast Ethernet    │
│  CAN_H (Screw Terminal)         │
│  CAN_L (Screw Terminal)         │
│  GND (Screw Terminal)           │
│  +24V IN (Screw Terminal)       │
│  GND (Screw Terminal)           │
└─────────────────────────────────┘
```

#### **Cable CAN Bus**

```
Especificaciones del Cable:
• Tipo: Twisted Pair Shielded (TPS)
• AWG: 24 AWG o 22 AWG
• Impedancia: 120Ω característico
• Blindaje: Trenzado + Foil + Malla
• Longitud máxima: 40m @ 250 kbps
• Colores estándar:
  - CAN_H: Amarillo
  - CAN_L: Verde
  - Blindaje: Conectado a GND en un extremo
```

---

### **Configuración con ESP32-S3 Gateway**

```
                    CONEXIONES ESP32-S3 → SERVIDOR → K13 F

┌──────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│  SERVIDOR DE PROCESAMIENTO                                                      │
│  (Computador con FastAPI)                                                       │
│  IP: 192.168.1.50 (Ethernet)                                                    │
│  O                                                                               │
│  WiFi: SSID "CRANE_NETWORK" (si usa WiFi)                                      │
│                                                                                  │
└─────────────────┬─────────────────────────┬────────────────────────────────────┘
                  │ Ethernet                │ WiFi 2.4GHz
                  │ (opción 1)              │ (opción 2)
                  │                         │
┌─────────────────▼─────────────────────────▼──────────────────────────────────────┐
│                                                                                  │
│  ESP32-S3 GATEWAY                                                               │
│  • ETH: 192.168.1.101 (si usa Ethernet)                                        │
│  • WiFi: 192.168.1.101 (si usa WiFi)                                           │
│  • 4G LTE: Backup connectivity                                                  │
│  • CAN (TWAI): GPIO21 (TX), GPIO22 (RX)                                        │
│  • Montaje: DIN Rail                                                            │
│  • Alimentación: 12V/24V DC                                                     │
│                                                                                  │
└─────────────────┬────────────────────────────────────────────────────────────────┘
                  │
                  │ Cable CAN Bus Blindado
                  │ (Twisted Pair Shielded)
                  │
┌─────────────────▼────────────────────────────────────────────────────────────────┐
│  DANFOSS K13 F (R13 F) RECEIVER                                                 │
│  (Igual que configuración BL335)                                                │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 💰 Análisis de Costos Completo

### **Opción 1: Sistema con BL335**

| Componente | Cantidad | Precio Unit. | Subtotal |
|------------|----------|--------------|----------|
| **Gateway BL335** | 1 | $130 USD | $130 |
| Cable Ethernet Cat6 (50m) | 1 | $15 USD | $15 |
| Cable CAN blindado (20m) | 1 | $25 USD | $25 |
| Terminadores CAN 120Ω | 2 | $3 USD | $6 |
| Fuente 24V DC 2A industrial | 1 | $20 USD | $20 |
| Conectores DB9 CAN | 2 | $5 USD | $10 |
| Gabinete industrial IP54 | 1 | $40 USD | $40 |
| **SUBTOTAL HARDWARE** | | | **$246 USD** |
| **TOTAL SISTEMA BL335** | | | **$276 USD** |
| | | | **≈ $267.000 CLP** |

### **Opción 2: Sistema con ESP32-S3 Gateway**

| Componente | Cantidad | Precio Unit. | Subtotal |
|------------|----------|--------------|----------|
| **Gateway ESP32-S3** | 1 | $277 USD | $277 |
| Cable Ethernet Cat6 (50m) | 1 | $15 USD | $15 |
| Cable CAN blindado (20m) | 1 | $25 USD | $25 |
| Terminadores CAN 120Ω | 2 | $3 USD | $6 |
| Fuente 12V/24V DC 2A | 1 | $20 USD | $20 |
| Antena 4G LTE (incluida) | 1 | $0 USD | $0 |
| Antena WiFi externa | 1 | $12 USD | $12 |
| Gabinete industrial IP54 | 1 | $40 USD | $40 |
| **SUBTOTAL HARDWARE** | | | **$395 USD** |
| **TOTAL SISTEMA ESP32-S3** | | | **$430 USD** |
| | | | **≈ $416.000 CLP** |

### **Comparación de Costos**

| Sistema | Costo Total | Diferencia | Observaciones |
|---------|-------------|------------|---------------|
| **BL335** | $276 USD | Base | Ethernet only, más económico |
| **ESP32-S3** | $430 USD | +$154 (+56%) | WiFi + 4G, más flexible |

**Conclusión de Costos**: El BL335 es **56% más económico** que el ESP32-S3 Gateway.

---

## 🔄 Flujo de Comunicación Detallado

### **Secuencia de Parada de Emergencia**

```
USUARIO          WEB UI (FastAPI)      GATEWAY           K13 F RECEIVER      MOTORES
  │                    │                   │                    │                │
  │ 1. Click botón     │                   │                    │                │
  │ "PARADA"           │                   │                    │                │
  ├───────────────────►│                   │                    │                │
  │                    │ 2. POST /api/     │                    │                │
  │                    │    emergency-stop │                    │                │
  │                    ├──────────────────►│ 3. TCP Socket      │                │
  │                    │                   │    JSON Command    │                │
  │                    │                   ├───────────────────►│ 4. CANopen     │
  │                    │                   │    NMT Stop (0x02) │    PDO/SDO     │
  │                    │                   │    Node ID: 0x10   │    Emergency   │
  │                    │                   │                    ├───────────────►│
  │                    │                   │                    │                │ 5. PARADA
  │                    │                   │                    │                │    FÍSICA
  │                    │                   │                    │                │    ████████
  │                    │                   │                    │                │
  │                    │                   │ 6. CAN ACK         │◄───────────────┤
  │                    │                   │◄───────────────────│                │
  │                    │ 7. JSON Response  │                    │                │
  │                    │◄──────────────────┤                    │                │
  │ 8. Confirmación    │                   │                    │                │
  │    "Parada OK"     │                   │                    │                │
  │◄───────────────────┤                   │                    │                │
  │                    │                   │                    │                │
  │ 9. WebSocket update│                   │                    │                │
  │◄───────────────────┤                   │                    │                │
  │    (Tiempo real)   │                   │                    │                │

⏱️ Tiempo total: < 100ms (típico 50-80ms)
```

### **Desglose de Tiempos**

| Paso | Operación | Tiempo (ms) |
|------|-----------|-------------|
| 1-2 | Click → POST API | 10-20 ms |
| 3 | TCP/IP → Gateway | 5-10 ms |
| 4 | CANopen Message | 5-10 ms |
| 5 | Parada física | 10-30 ms |
| 6-7 | Confirmación CAN | 5-10 ms |
| 8-9 | Response UI | 10-20 ms |
| **TOTAL** | **Latencia completa** | **45-100 ms** |

---

## 📡 Protocolos de Comunicación

### **Nivel 1: Ethernet/WiFi (Servidor ↔ Gateway)**

**Protocolo**: TCP/IP con JSON sobre HTTP REST

**Formato de Comando**:
```json
{
  "command": "emergency_stop",
  "node_id": 16,
  "timestamp": "2025-10-16T14:30:00Z",
  "priority": "critical"
}
```

**Formato de Respuesta**:
```json
{
  "status": "success",
  "node_id": 16,
  "state": "stopped",
  "timestamp": "2025-10-16T14:30:00.085Z",
  "latency_ms": 85
}
```

### **Nivel 2: CAN Bus (Gateway ↔ K13 F)**

**Protocolo**: CANopen (CiA 301)

**Mensajes Principales**:

1. **NMT (Network Management)**
   ```
   COB-ID: 0x000
   Data: [0x02, 0x10]  // Stop Node 16
   ```

2. **PDO (Process Data Object)**
   ```
   COB-ID: 0x200 + Node ID
   Data: Emergency stop bit pattern
   ```

3. **SDO (Service Data Object)**
   ```
   COB-ID: 0x600 + Node ID
   Data: Object 0x6040 (Control Word) = 0x0006 (Shutdown)
   ```

4. **EMCY (Emergency)**
   ```
   COB-ID: 0x080 + Node ID
   Data: Error code + error register
   ```

---

## 🧪 Plan de Pruebas Comparativas

### **Fase 1: Pruebas Individuales**

#### **Test BL335**
- [ ] Instalación Linux y configuración SocketCAN
- [ ] Comunicación Ethernet con servidor
- [ ] Envío/recepción mensajes CAN básicos
- [ ] Latencia de comando completo
- [ ] Estabilidad 24/7 (1 semana)

#### **Test ESP32-S3**
- [ ] Programación ESP-IDF y configuración TWAI
- [ ] Comunicación WiFi/Ethernet con servidor
- [ ] Envío/recepción mensajes CAN básicos
- [ ] Latencia de comando completo
- [ ] Estabilidad 24/7 (1 semana)

### **Fase 2: Pruebas con K13 F Real**

- [ ] Conexión física CAN con K13 F
- [ ] Comando de parada de emergencia
- [ ] Lectura de estado del receptor
- [ ] Pruebas de robustez (100 paradas)
- [ ] Prueba de interferencia electromagnética

### **Fase 3: Pruebas de Estrés**

- [ ] Múltiples comandos simultáneos
- [ ] Desconexión y reconexión de red
- [ ] Latencia bajo carga de red
- [ ] Comportamiento ante fallos CAN
- [ ] Tiempo de recuperación

### **Criterios de Evaluación**

| Criterio | Peso | BL335 | ESP32-S3 |
|----------|------|-------|----------|
| **Latencia promedio** | 25% | TBD | TBD |
| **Estabilidad 24/7** | 20% | TBD | TBD |
| **Facilidad de desarrollo** | 15% | TBD | TBD |
| **Robustez industrial** | 15% | TBD | TBD |
| **Costo total** | 10% | 9/10 | 6/10 |
| **Conectividad** | 10% | 7/10 | 10/10 |
| **Documentación** | 5% | TBD | 9/10 |
| **TOTAL** | 100% | **TBD** | **TBD** |

---

## ✅ Recomendación Preliminar

### **Usar BL335 si:**
- ✅ Instalación fija con Ethernet disponible
- ✅ Presupuesto limitado ($276 vs $430)
- ✅ Necesitas Linux completo para desarrollo
- ✅ Red SCADA existente con Ethernet
- ✅ Prioridad: Estabilidad y robustez

### **Usar ESP32-S3 Gateway si:**
- ✅ Necesitas conectividad WiFi/4G
- ✅ Ubicación remota sin Ethernet
- ✅ Necesitas monitoreo móvil
- ✅ Desarrollo IoT Edge Computing
- ✅ Prioridad: Flexibilidad de conectividad

### **Decisión Final**

⏳ **La decisión se tomará después de las pruebas de campo** con ambos equipos conectados al K13 F real. El gateway que demuestre:

1. **Menor latencia** (< 80ms objetivo)
2. **Mayor estabilidad** (0 fallos en 1 semana)
3. **Mejor facilidad de desarrollo** (tiempo de implementación)
4. **Robustez industrial probada** (resistencia a interferencias)

Será seleccionado como **gateway definitivo del proyecto**.

---

**Documento**: Arquitectura Sistema Completo  
**Versión**: 1.0  
**Fecha**: 16 de octubre de 2025  
**Autor**: Proyecto Puente Grúa R13 F  
**Estado**: En evaluación - Esperando pruebas de campo
