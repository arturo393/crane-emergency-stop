# 📦 Hardware Adquirido - Estrategia Dual

**Fecha de Actualización**: 31 de octubre de 2025  
**Estado**: ✅ AMBOS HARDWARE ADQUIRIDOS Y EN POSESIÓN  
**Estrategia**: Evaluación comparativa para seleccionar gateway definitivo

---

## 🎯 **Estrategia Dual Hardware**

Este proyecto implementa una **estrategia de evaluación comparativa** con dos gateways industriales:

```
┌─────────────────────────────────────────────────────────────┐
│              EVALUACIÓN COMPARATIVA DUAL                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  OBJETIVO: Probar AMBOS gateways con código funcional      │
│            idéntico para decidir cuál es mejor             │
│                                                             │
│  CRITERIOS:                                                 │
│  • Confiabilidad en entorno industrial                     │
│  • Latencia de respuesta (emergency stop)                  │
│  • Facilidad de mantenimiento                              │
│  • Robustez ante errores                                   │
│  • Capacidades de diagnóstico                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 **Hardware Adquirido - Comparativa**

| Característica | BL335 Gateway | EdgeBox Lite (ESP32) |
|----------------|---------------|----------------------|
| **Estado** | ✅ Comprado, en posesión | ✅ Comprado, en posesión |
| **Precio** | $130 USD | Por confirmar |
| **Procesador** | ARM Cortex (Linux) | ESP32 Dual-core @ 240MHz |
| **Conectividad** | Ethernet dual (1000M+100M) | WiFi + Ethernet + 4G/LTE |
| **CAN Bus** | SocketCAN (kernel Linux) | TWAI (CAN 2.0 nativo) |
| **Sistema Operativo** | Linux (Debian/Ubuntu) | FreeRTOS (ESP-IDF) |
| **Alimentación** | Por confirmar | 10.8-36V DC |
| **Temperatura** | -20°C a +60°C | -20°C a +60°C |
| **Código** | Python (python-canopen) | C++ (ESP-IDF) |
| **Montaje** | DIN Rail | Por confirmar |

---

## 🔧 **GATEWAY A: BL335 Industrial Embedded Computer**

### **Especificaciones Técnicas**

**Modelo**: ARMxy BL335 Industrial-Grade Embedded Computer  
**Fabricante**: ARMxy / HMS Networks (distribuido en Alibaba)  
**Precio**: $130 USD  
**Fecha de Adquisición**: 31 de octubre de 2025  
**Estado**: ✅ En posesión, pendiente de unboxing

**Procesador**:
- CPU: ARM Cortex (arquitectura no especificada exactamente)
- Velocidad: Por confirmar (típicamente 400MHz-1GHz)
- Arquitectura: 32-bit ARM

**Sistema Operativo**:
- OS: Linux embebido (Debian/Ubuntu compatible)
- Kernel: Compatible con SocketCAN
- Runtime: Python 3.x compatible

**Conectividad**:
- ✅ **Ethernet Dual**: 1x 1000M + 1x 100M (redundancia/separación)
- ❌ **WiFi**: No disponible
- ❌ **4G/LTE**: No disponible
- ✅ **Serial**: RS232/RS485 (por confirmar)

**CAN Bus**:
- ✅ **Interfaz**: 2x CAN 2.0A/B integrado
- ✅ **SocketCAN**: Soporte nativo en kernel Linux
- ✅ **Velocidad**: Hasta 1 Mbps
- ✅ **Protocolo**: CANopen Master/Slave ready

**Características Industriales**:
- ✅ Temperatura operativa: -20°C a +60°C (grado industrial)
- ✅ Montaje: DIN Rail estándar
- ✅ Alimentación: 12-24V DC (por confirmar)
- ✅ Protecciones: Por confirmar

**Software y Desarrollo**:
- ✅ **python-canopen**: Librería Python completa
- ✅ **SSH**: Acceso remoto Linux
- ✅ **OTA**: Actualizaciones remotas (via SSH/SCP)
- ✅ **SCADA Ready**: Diseñado para manufactura inteligente

**Aplicaciones**:
- Gateway CANopen → Ethernet
- Control industrial distribuido
- SCADA/HMI integration
- Smart Manufacturing

### **Ventajas BL335**

✅ **Linux Nativo**
- Ecosistema maduro y probado
- Herramientas estándar (SSH, SCP, systemd)
- Debug fácil con herramientas Linux

✅ **python-canopen**
- Librería completa y madura
- CANopen stack completo (NMT, SDO, PDO, EMCY)
- EDS parsing automático

✅ **Ethernet Dual**
- Redundancia de red
- Separación de tráfico (control vs monitoreo)
- Mayor throughput

✅ **DIN Rail**
- Instalación industrial estándar
- Integración fácil en gabinetes

✅ **SCADA Ready**
- Diseñado para manufactura
- Protocolos industriales

### **Desventajas BL335**

❌ **Sin WiFi/4G**
- Requiere cableado Ethernet
- No hay backup inalámbrico

❌ **Documentación Limitada**
- Producto chino (ARMxy)
- Soporte técnico en inglés/chino
- Menos comunidad que ESP32

❌ **Mayor Consumo**
- Linux consume más recursos que FreeRTOS
- Requiere más memoria y CPU

❌ **Costo Mayor**
- $130 USD vs ESP32 (precio menor)

---

## 🔧 **GATEWAY B: OpenEmbed EdgeBox Lite (ESP32)**

### **Especificaciones Técnicas**

**Modelo**: EdgeBox Lite  
**Fabricante**: OpenEmbed  
**URL Producto**: <https://www.openembed.com/products/71.html>  
**Precio**: Por confirmar  
**Fecha de Adquisición**: 31 de octubre de 2025  
**Estado**: ✅ En posesión, pendiente de unboxing

**Procesador**:

- MCU: ESP32 (Dual-core Xtensa LX6)
- Velocidad: 240 MHz
- Arquitectura: 32-bit

**Sistema Operativo**:

- OS: FreeRTOS (ESP-IDF framework)
- Real-time: Sí (RTOS)
- Runtime: C/C++ nativo

**Conectividad**:

- ✅ **WiFi**: 802.11 b/g/n (2.4GHz)
- ✅ **Ethernet**: 10/100 Mbps
- ✅ **4G/LTE**: Radio celular integrado
- ✅ **Fieldbus**: Comunicación PLC

**CAN Bus**:

- ✅ **Interfaz**: TWAI (Two-Wire Automotive Interface)
- ✅ **Compatibilidad**: CAN 2.0 (ISO 11898-1)
- ✅ **Velocidad**: Hasta 1 Mbps
- ✅ **Implementación**: Firmware C++ custom

**Características Industriales**:

- ✅ Temperatura operativa: -20°C a +60°C (grado industrial)
- ✅ Alimentación: 10.8V - 36V DC (amplio rango)
- ✅ Alta aislación eléctrica
- ✅ Protección contra sobretensión
- ✅ Protección contra cortocircuitos
- ✅ Hardware rugoso, bajo mantenimiento

**Software y Desarrollo**:

- ✅ **ESP-IDF**: Framework oficial Espressif
- ✅ **OTA Updates**: Actualizaciones over-the-air
- ✅ **FreeRTOS**: Sistema operativo real-time
- ✅ **Custom Firmware**: Programación completa en C++

**Aplicaciones**:

- Edge Computing
- IoT Industrial
- Robótica
- M2M Wireless
- Control de campo
- Gateway PLC

### **Ventajas EdgeBox Lite**

✅ **Conectividad Triple**

- WiFi + Ethernet + 4G/LTE
- Backup celular para emergencias
- Flexibilidad de despliegue

✅ **ESP32 Maduro**

- Ecosistema enorme (ESP-IDF, Arduino)
- Comunidad muy activa
- Documentación excelente

✅ **TWAI Nativo**

- CAN 2.0 integrado en MCU
- Bajo overhead de comunicación
- Alta eficiencia

✅ **Alimentación Flexible**

- 10.8-36V DC (amplio rango)
- Compatible con 12V/24V industrial
- Protecciones eléctricas completas

✅ **Edge Computing**

- Procesamiento local IoT
- Baja latencia
- Menor dependencia de red

### **Desventajas EdgeBox Lite**

❌ **FreeRTOS vs Linux**

- Menos herramientas estándar
- Debug más complejo que Linux
- Requiere firmware C++

❌ **CANopen Custom**

- Implementación manual en C++
- Sin librería python-canopen
- Mayor esfuerzo de desarrollo

❌ **Recursos Limitados**

- 520KB RAM vs ~256MB+ en BL335
- Menor capacidad de procesamiento
- Limitaciones de memoria

❌ **Documentación Específica**

- Menos info sobre EdgeBox Lite específicamente
- Documentación genérica ESP32

---

## � **Resumen Comparativo - Decisión Pendiente**

| Criterio | BL335 | EdgeBox Lite | Ganador |
|----------|-------|--------------|---------|
| **Conectividad** | Ethernet dual | WiFi+Eth+4G | 🏆 EdgeBox |
| **Software** | Linux + Python | FreeRTOS + C++ | 🏆 BL335 |
| **CANopen** | python-canopen | Custom C++ | 🏆 BL335 |
| **Costo** | $130 USD | < $130 (TBD) | ⏳ Pendiente |
| **Comunidad** | Limitada | Muy activa | 🏆 EdgeBox |
| **Industrial** | DIN Rail, SCADA | Protecciones, -20°C | 🏆 Empate |
| **Mantenimiento** | SSH, Linux tools | OTA, FreeRTOS | ⏳ Pendiente |
| **Latencia** | ⏳ Por medir | ⏳ Por medir | ⏳ Pendiente |
| **Confiabilidad** | ⏳ Por validar | ⏳ Por validar | ⏳ Pendiente |

**Decisión final**: Pendiente de pruebas reales (Noviembre 2025)

---

## ✅ **Estado de Integración - AMBOS GATEWAYS**

### **FASE 1: Adquisición** ✅ COMPLETADA

- ✅ BL335 Gateway seleccionado y adquirido
- ✅ EdgeBox Lite seleccionado y adquirido
- ✅ AMBOS hardware en posesión
- ✅ Documentación revisada

### **FASE 2: Preparación** 🚀 EN PROGRESO

**Pendiente - AMBOS dispositivos**:

- [ ] Unboxing e inspección física
- [ ] Verificar accesorios incluidos
- [ ] Documentación fotográfica
- [ ] Identificar pines y conectores
- [ ] Verificar voltaje de alimentación
- [ ] Preparar cables de conexión

### **FASE 3: Desarrollo de Paridad** 🚀 EN PROGRESO

**Código BL335**:

- ✅ BL335Gateway Python implementado (876 líneas)
- ✅ CANopen completo (PDO/SDO/NMT)
- ✅ TCP server JSON (port 9999)
- ⚠️ Event logging (por integrar)
- ⚠️ Recovery system (pendiente)

**Código ESP32**:

- ✅ Firmware base compilado (227.17 KB)
- ✅ TWAI CAN manager
- ✅ CANopen CiA 402 básico
- ❌ TCP server JSON (pendiente)
- ❌ Event logging (pendiente)
- ❌ Recovery system (pendiente)

**Ver**: `docs/DUAL_HARDWARE_STRATEGY.md` para plan completo

### **FASE 4: Testing Comparativo** ⏳ PENDIENTE

- [ ] Setup físico dual (ambos en paralelo)
- [ ] Suite de tests comparativos
- [ ] Métricas de rendimiento
- [ ] Pruebas de confiabilidad (24h)
- [ ] Evaluación ponderada

### **FASE 5: Decisión Final** ⏳ PENDIENTE

- [ ] Reporte técnico comparativo
- [ ] Matriz de decisión ponderada
- [ ] Selección de gateway definitivo
- [ ] Plan de implementación para ganador

---

## 🔗 **Próximos Pasos Inmediatos**

### **HOY (31 octubre 2025)** ✅

1. ✅ Documentar hardware adquirido (ambos)
2. ✅ Crear tareas JIRA de paridad (GAT-63)
3. ✅ Estrategia dual clarificada

### **Esta Semana (1-7 Nov)**

1. 📦 **Unboxing de ambos dispositivos** (Día 1)
2. 🔍 **Identificación de hardware** (Día 1-2)
3. 💻 **TCP Server ESP32** (Día 2-3, 6-8h)
4. � **Event Logging ambos** (Día 3-4, 8-10h)
5. 🔧 **Recovery System ambos** (Día 4-5, 8-10h)

### **Próximas 4 Semanas**

1. **Semana 1**: Funcionalidades core (TCP, Events, Recovery)
2. **Semana 2**: Completar paridad (NMT, EMCY, Simuladores)
3. **Semana 3**: Diagnósticos y robustez industrial
4. **Semana 4**: Evaluación comparativa y decisión

---

## � **Recursos de Soporte**

### **BL335 Gateway**

- **Fabricante**: ARMxy / HMS Networks
- **Alibaba**: Búsqueda "BL335 CANopen Gateway"
- **Soporte**: Vendedor Alibaba (inglés/chino)

### **EdgeBox Lite**

- **Sitio web**: <https://www.openembed.com/>
- **Producto**: <https://www.openembed.com/products/71.html>
- **Wiki**: Disponible en sitio
- **Soporte**: OpenEmbed support

### **Comunidad ESP32**

- **ESP-IDF Docs**: <https://docs.espressif.com/projects/esp-idf/>
- **Forum**: <https://esp32.com/>
- **GitHub**: <https://github.com/espressif/esp-idf>

### **Proyecto K13**

- **Repositorio**: crane-emergency-stop
- **Documentación**: `docs/`
- **Hardware specs**: `hardware/`
- **Firmware ESP32**: `esp32_gateway/`
- **BL335 Gateway**: `src/bl335_gateway/`

---

## 🎯 **Objetivo de la Estrategia Dual**

**Probar AMBOS gateways** con código funcionalmente idéntico para:

1. **Medir rendimiento real** (latencia, throughput, confiabilidad)
2. **Validar robustez industrial** (recovery, diagnósticos, uptime)
3. **Evaluar mantenibilidad** (facilidad de actualización, debug)
4. **Decidir con datos** cuál es mejor para producción

**Timeline**: Decisión final en **finales de noviembre 2025**

---

**Última actualización**: 31 de octubre de 2025, 23:00  
**Estado**: AMBOS hardware adquiridos, estrategia dual en ejecución ✅  
**Responsable**: Arturo  
**Próxima acción**: Unboxing ambos dispositivos + TCP Server ESP32
