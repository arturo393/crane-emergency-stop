# 🔄 Estrategia Dual Hardware - Evaluación Comparativa

**Fecha**: 31 de octubre de 2025  
**Estado**: AMBOS HARDWARE ADQUIRIDOS Y EN POSESIÓN  
**Objetivo**: Implementar funcionalidad IDÉNTICA en ambos gateways para evaluación comparativa real

---

## 📊 **Estado Actual del Proyecto**

### **✅ Hardware Adquirido**

| Hardware | Estado | Ubicación | Costo | Características Clave |
|----------|--------|-----------|-------|----------------------|
| **BL335 Gateway** | ✅ Comprado, en posesión | Por verificar | $130 USD | Linux ARM, Dual Ethernet, SocketCAN |
| **EdgeBox Lite (ESP32)** | ✅ Comprado, en posesión | Por verificar | Por confirmar | ESP32, WiFi+Eth+4G, TWAI CAN |

### **🎯 Objetivo de la Estrategia**

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVALUACIÓN COMPARATIVA                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MISMO CÓDIGO FUNCIONAL → PROBAR AMBOS → DECIDIR EL MEJOR      │
│                                                                 │
│  Criterios de Evaluación:                                       │
│  • Confiabilidad en entorno industrial                         │
│  • Latencia de respuesta (emergency stop)                      │
│  • Facilidad de mantenimiento                                  │
│  • Robustez ante errores                                       │
│  • Capacidades de diagnóstico                                  │
│  • Sistema de recuperación automática                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 **Matriz de Paridad Funcional**

### **Funcionalidades Requeridas (AMBOS deben tener)**

| # | Funcionalidad | BL335 Status | ESP32 Status | Prioridad |
|---|---------------|--------------|--------------|-----------|
| **1. Core CANopen** |
| 1.1 | CAN bus communication (250 kbps) | ✅ SocketCAN | ✅ TWAI | CRÍTICA |
| 1.2 | CANopen CiA 402 (Drive profile) | ✅ Python-canopen | ✅ C++ implementado | CRÍTICA |
| 1.3 | PDO (Process Data Objects) | ✅ Completo | ✅ RPDO1/TPDO1 | CRÍTICA |
| 1.4 | SDO (Service Data Objects) | ✅ Completo | ✅ Básico | CRÍTICA |
| 1.5 | NMT (Network Management) | ✅ Completo | ⚠️ Heartbeat only | ALTA |
| 1.6 | Emergency messages | ✅ Soportado | ⚠️ Pendiente | ALTA |
| **2. Control K13 F** |
| 2.1 | Emergency stop (triple redundancia) | ✅ Implementado | ✅ Implementado | CRÍTICA |
| 2.2 | Startup sequence (CiA 402) | ✅ Completo | ✅ Completo | CRÍTICA |
| 2.3 | Shutdown sequence | ✅ Completo | ✅ Completo | CRÍTICA |
| 2.4 | Velocity control | ✅ Completo | ✅ Completo | ALTA |
| 2.5 | Position control | ✅ Completo | ⚠️ Básico | MEDIA |
| **3. Conectividad** |
| 3.1 | TCP server (port 9999) | ✅ Implementado | ⚠️ **PENDIENTE** | CRÍTICA |
| 3.2 | JSON protocol (comandos) | ✅ Completo | ⚠️ **PENDIENTE** | CRÍTICA |
| 3.3 | WebSocket (tiempo real) | ⚠️ Pendiente | ❌ No planeado | BAJA |
| 3.4 | WiFi | ❌ No disponible | ✅ 802.11 b/g/n | MEDIA |
| 3.5 | Ethernet | ✅ Dual (1000M+100M) | ✅ 10/100 Mbps | ALTA |
| 3.6 | 4G/LTE | ❌ No disponible | ✅ Integrado | BAJA |
| **4. Diagnósticos Industriales** |
| 4.1 | Event logging system | ⚠️ **PENDIENTE** | ⚠️ **PENDIENTE** | CRÍTICA |
| 4.2 | Safety event level (SAFETY=60) | ⚠️ **PENDIENTE** | ⚠️ **PENDIENTE** | CRÍTICA |
| 4.3 | 7 categorías de eventos | ⚠️ **PENDIENTE** | ⚠️ **PENDIENTE** | CRÍTICA |
| 4.4 | Real-time event callbacks | ⚠️ **PENDIENTE** | ⚠️ **PENDIENTE** | ALTA |
| 4.5 | Event persistence (file/flash) | ⚠️ **PENDIENTE** | ⚠️ **PENDIENTE** | ALTA |
| 4.6 | CAN bus monitor (diagnóstico) | ✅ Implementado | ✅ Básico | ALTA |
| 4.7 | Error counters por categoría | ⚠️ **PENDIENTE** | ⚠️ **PENDIENTE** | MEDIA |
| **5. Recuperación de Errores** |
| 5.1 | Watchdog timer | ⚠️ Verificar | ✅ FreeRTOS | CRÍTICA |
| 5.2 | Auto-recovery de CAN bus | ⚠️ **PENDIENTE** | ⚠️ **PENDIENTE** | CRÍTICA |
| 5.3 | Fault state handling | ✅ CiA 402 | ✅ CiA 402 | CRÍTICA |
| 5.4 | Connection retry logic | ⚠️ **PENDIENTE** | ⚠️ **PENDIENTE** | ALTA |
| 5.5 | Graceful degradation | ⚠️ **PENDIENTE** | ⚠️ **PENDIENTE** | ALTA |
| 5.6 | System health monitoring | ⚠️ **PENDIENTE** | ⚠️ **PENDIENTE** | ALTA |
| **6. Simulación y Testing** |
| 6.1 | Simulador K13 F integrado | ✅ Completo | ✅ Básico | CRÍTICA |
| 6.2 | Virtual CAN (testing sin HW) | ✅ vcan0 | ⚠️ Loopback mode | ALTA |
| 6.3 | Test automation | ⚠️ Básico | ❌ Pendiente | MEDIA |
| 6.4 | CI/CD integration | ❌ Pendiente | ❌ Pendiente | BAJA |

**Leyenda**:
- ✅ Implementado y funcional
- ⚠️ Parcialmente implementado o pendiente
- ❌ No implementado / No disponible en hardware

---

## 📋 **Plan de Implementación - Paridad Completa**

### **FASE 1: Completar Funcionalidades Core** (Prioridad CRÍTICA)

#### **Semana 1 (1-7 Nov 2025)**

**Para ESP32 (EdgeBox Lite)**:
- [ ] **TCP Server con JSON** (6-8 horas)
  - Puerto 9999
  - Multi-cliente (hasta 4 simultáneos)
  - Comandos JSON idénticos a BL335
  - Respuestas JSON con mismo formato
  
- [ ] **Event Logging System** (4-6 horas)
  - Implementar EventLogger en C++
  - 6 niveles (DEBUG→SAFETY)
  - 7 categorías (SAFETY, CONTROL, etc.)
  - Almacenamiento en SPIFFS/NVS
  - Buffer circular thread-safe

**Para BL335**:
- [ ] **Event Logging System** (2-3 horas)
  - Integrar EventLogger existente
  - Conectar a BL335Gateway
  - Logging a archivo con rotación
  - Export JSON para auditorías

**Ambos**:
- [ ] **Sistema de Recuperación de Errores** (4-6 horas cada uno)
  - Watchdog implementation
  - CAN bus auto-recovery
  - Connection retry logic
  - Health monitoring

---

#### **Semana 2 (8-14 Nov 2025)**

**Para ESP32**:
- [ ] **NMT completo** (3-4 horas)
  - Implementar estados NMT
  - Boot-up message
  - Node guarding / Heartbeat consumer
  
- [ ] **Emergency messages** (2-3 horas)
  - EMCY object (0x1001, 0x1003, 0x1014)
  - Error register
  - Pre-defined error field

**Para BL335**:
- [ ] **Mejorar simulador** (2-3 horas)
  - Paridad con ESP32
  - Mejores trazas CAN

**Ambos**:
- [ ] **Testing E2E** (6-8 horas)
  - Test suite idéntico
  - Validación de comportamiento
  - Métricas de rendimiento

---

### **FASE 2: Capacidades Industriales** (Prioridad ALTA)

#### **Semana 3 (15-21 Nov 2025)**

**Ambos**:
- [ ] **Sistema de Diagnósticos Avanzado** (8-10 horas cada uno)
  - Panel de diagnósticos en tiempo real
  - Histórico de eventos
  - Estadísticas por categoría
  - Exportación de reportes
  - Alertas configurables

- [ ] **Robustez Industrial** (6-8 horas cada uno)
  - Manejo de desconexiones CAN
  - Recuperación automática
  - Failover mechanisms
  - Degradación gradual

---

### **FASE 3: Validación Comparativa** (Prioridad CRÍTICA)

#### **Semana 4 (22-30 Nov 2025)**

**Preparación**:
- [ ] **Setup físico dual** (4 horas)
  - Montar ambos gateways
  - Cableado CAN en paralelo (splitter)
  - Alimentación independiente
  - Acceso de red a ambos

**Testing Comparativo**:
- [ ] **Pruebas funcionales** (8 horas)
  - Ejecutar MISMA secuencia de comandos
  - Medir latencias
  - Validar respuestas idénticas
  - Stress testing

- [ ] **Métricas de rendimiento** (4 horas)
  - Latencia emergency stop
  - Throughput CAN messages
  - Memoria utilizada
  - CPU load
  - Tiempo de recovery

- [ ] **Pruebas de confiabilidad** (8 horas)
  - Test de 24 horas continuas
  - Inyección de errores
  - Desconexión/reconexión
  - Power cycling
  - Variaciones de temperatura

**Documentación**:
- [ ] **Reporte comparativo** (4 horas)
  - Matriz de resultados
  - Pros/cons de cada uno
  - Recomendación final
  - Justificación técnica

---

## 🎯 **Criterios de Evaluación Final**

### **Categorías de Evaluación** (Ponderación)

| Categoría | Peso | Métricas Clave |
|-----------|------|----------------|
| **Seguridad** | 30% | - Latencia emergency stop<br>- Confiabilidad del sistema<br>- Trazabilidad de eventos |
| **Rendimiento** | 25% | - Throughput CAN<br>- Latencia promedio<br>- Uso de recursos |
| **Confiabilidad** | 20% | - Uptime en 24h<br>- Recovery exitoso<br>- Errores registrados |
| **Mantenibilidad** | 15% | - Facilidad de actualización<br>- Diagnósticos disponibles<br>- Documentación |
| **Costo TCO** | 10% | - Precio hardware<br>- Costo de operación<br>- Vida útil estimada |

### **Umbrales Mínimos Aceptables**

| Métrica | Umbral Mínimo | Objetivo |
|---------|---------------|----------|
| Latencia Emergency Stop | < 100 ms | < 50 ms |
| Uptime 24h | > 99.5% | > 99.9% |
| Recovery exitoso | > 95% | 100% |
| Mensajes CAN/s | > 100 msg/s | > 500 msg/s |
| Pérdida de mensajes | < 0.1% | 0% |

---

## 📂 **Estructura de Código Unificada**

### **Organización Propuesta**

```
puente_grua/
├── src/
│   ├── common/                    # 🆕 Código compartido
│   │   ├── event_logger/         # Sistema de eventos (spec común)
│   │   │   ├── event_types.h     # Niveles y categorías
│   │   │   └── event_schema.json # Schema JSON para ambos
│   │   ├── protocol/             # Protocolo CANopen común
│   │   │   ├── cia402_states.h   # State machine
│   │   │   └── object_dict.h     # Object dictionary
│   │   └── recovery/             # Sistema de recuperación
│   │       ├── watchdog.h        # Especificación común
│   │       └── retry_logic.h     # Lógica de reintentos
│   │
│   ├── bl335_gateway/            # Implementación BL335
│   │   ├── main.py               # ✅ Existente
│   │   ├── event_logger.py       # 🆕 Por implementar
│   │   ├── recovery_manager.py   # 🆕 Por implementar
│   │   └── diagnostics.py        # 🆕 Por implementar
│   │
│   ├── esp32_gateway/            # Implementación ESP32
│   │   ├── main/
│   │   │   ├── main.cpp          # ✅ Existente
│   │   │   ├── tcp_server.cpp    # 🆕 Por implementar
│   │   │   ├── event_logger.cpp  # 🆕 Por implementar
│   │   │   ├── recovery_mgr.cpp  # 🆕 Por implementar
│   │   │   └── diagnostics.cpp   # 🆕 Por implementar
│   │   └── components/
│   │       ├── canopen/          # ✅ Existente
│   │       └── event_system/     # 🆕 Por implementar
│   │
│   ├── web_ui/                   # ✅ Agnóstico (TCP/IP)
│   ├── desktop_gui/              # ✅ Agnóstico (TCP/IP)
│   └── k13_controller/           # ✅ Lógica de alto nivel
│
├── tests/
│   ├── common/                   # Tests del protocolo común
│   ├── bl335/                    # Tests específicos BL335
│   ├── esp32/                    # Tests específicos ESP32
│   └── comparative/              # 🆕 Tests comparativos
│       ├── latency_test.py
│       ├── stress_test.py
│       └── endurance_test.py
│
└── docs/
    ├── comparative_results/      # 🆕 Resultados de comparación
    │   ├── metrics_report.md
    │   └── decision_matrix.xlsx
    └── deployment/
        ├── bl335_setup.md
        └── esp32_setup.md
```

---

## 🔄 **Protocolo TCP/IP Unificado**

### **Comandos JSON (AMBOS gateways)**

```json
// Comando genérico
{
  "command": "emergency_stop|startup|shutdown|set_velocity|get_status",
  "params": {
    // Parámetros específicos del comando
  },
  "timestamp": "2025-11-01T10:30:00Z",
  "request_id": "uuid-1234"
}

// Respuesta genérica
{
  "status": "ok|error",
  "result": {
    // Datos de respuesta
  },
  "events": [
    // Eventos generados (opcional)
  ],
  "timestamp": "2025-11-01T10:30:00.123Z",
  "request_id": "uuid-1234",
  "gateway": "bl335|esp32",
  "execution_time_ms": 45
}
```

### **Eventos (Formato Unificado)**

```json
{
  "level": "DEBUG|INFO|WARNING|ERROR|CRITICAL|SAFETY",
  "category": "SAFETY|CONTROL|COMMUNICATION|SYSTEM|USER|HARDWARE|DIAGNOSTIC",
  "timestamp": "2025-11-01T10:30:00.123Z",
  "source": "bl335_gateway|esp32_gateway",
  "message": "Emergency stop activated by user command",
  "context": {
    "can_msg_count": 1234,
    "device_state": "OPERATION_ENABLED",
    "uptime_seconds": 86400
  },
  "event_id": 12345
}
```

---

## 📊 **Siguiente Paso INMEDIATO**

### **HOY (31 Oct 2025) - Planificación** ✅

- [x] Aclarar estrategia dual hardware
- [x] Crear este documento de paridad
- [ ] Crear tareas JIRA para paridad
- [ ] Priorizar implementaciones pendientes

### **MAÑANA (1 Nov 2025) - Inicio Desarrollo**

**Prioridad 1: TCP Server ESP32** (CRÍTICO para testing)
- Implementar TCP server en ESP32
- Puerto 9999, multi-cliente
- Protocolo JSON idéntico a BL335

**Prioridad 2: Event Logging (ambos)** (CRÍTICO para industrial)
- ESP32: EventLogger en C++
- BL335: Integrar EventLogger Python existente

---

## ✅ **Entregables Finales**

Al completar este plan, tendrás:

1. ✅ **Dos gateways funcionalmente idénticos**
2. ✅ **Sistema de diagnósticos industrial completo**
3. ✅ **Sistema de recuperación automática de errores**
4. ✅ **Suite de tests comparativos**
5. ✅ **Reporte técnico con recomendación justificada**
6. ✅ **Código de producción listo para el gateway seleccionado**

---

**Última actualización**: 31 de octubre de 2025  
**Estado**: Plan aprobado, iniciando implementación  
**Responsable**: Arturo  
**Próxima acción**: Implementar TCP server ESP32 + Event logging (ambos)
