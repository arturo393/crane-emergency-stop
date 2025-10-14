# Especificaciones Técnicas - EdgeBox-ESP-100 para Control Puente Grúa

## 📋 Información del Producto

**Producto:** EdgeBox-ESP-100 Industrial Edge Controller  
**Fabricante:** Seeed Studio  
**Precio aproximado:** USD $139.00  
**SKU:** 102991735  
**Disponibilidad:** En stock  

## 🎯 ¿Por qué este equipo es perfecto para tu proyecto?

Este gateway industrial cumple con los requisitos de tu sistema de parada de emergencia para puente grúa:

### ✅ Requisitos Cumplidos
- **⚠️ Sistema Operativo:** ESP-IDF (FreeRTOS-based), **NO soporta Ubuntu IoT** (es ESP32, no Linux completo)
- **✅ Ethernet:** 1 puerto RJ45 100M
- **✅ CAN bus para CANopen:** 1 puerto CAN bus aislado
- **✅ Control industrial:** Diseñado específicamente para automatización industrial
- **✅ Programación:** ESP-IDF, Arduino, MicroPython

### ⚠️ IMPORTANTE: Limitación del Sistema Operativo
Este equipo usa **ESP32-S3** (microcontrolador), no un procesador ARM con Linux completo. Si necesitas **Ubuntu IoT obligatoriamente**, este NO es el equipo adecuado. Considera alternativas como:
- **Raspberry Pi CM4** con CAN HAT
- **Revolution Pi Connect+ SE**
- **WAGO PFC200**

## 🔧 Especificaciones Técnicas Detalladas

### Hardware Principal
| Componente | Especificación |
|------------|---------------|
| **CPU** | ESP32-S3 (Dual-core Xtensa LX7 @ 240MHz) |
| **Arquitectura** | Xtensa 32-bit (NO es ARM Cortex) |
| **Sistema Operativo** | FreeRTOS (ESP-IDF), NO Linux/Ubuntu IoT |
| **Memoria RAM** | 512KB SRAM + 8MB PSRAM |
| **Almacenamiento** | 16MB Flash |
| **Temperatura de operación** | -20°C a +60°C |
| **Certificaciones** | RoHS, CE, FCC, UKCA |
| **Garantía** | 2 años |

### Conectividad (CRÍTICA para tu proyecto)
| Interfaz | Detalles | Uso en tu proyecto |
|----------|----------|-------------------|
| **CAN Bus** | 1 puerto aislado | ✅ Comunicación CANopen con receptor R13 |
| **Ethernet** | 1 puerto RJ45 100M | ✅ Conexión a red industrial |
| **WiFi** | 2.4 GHz integrado | ✅ Backup/alternativo |
| **Bluetooth** | 5.0, BLE | ✅ Configuración/paring |
| **4G LTE** | Módulo A7670G SIMCom | ✅ Conectividad remota |

### Interfaces Industriales
| Tipo | Cantidad | Especificaciones |
|------|----------|-----------------|
| **Entradas Digitales** | 4 | Aisladas, 24V DC |
| **Salidas Digitales** | 6 | Aisladas, 24V DC |
| **Entradas Analógicas** | 4 | 0-20mA (configurable 0-10V) |
| **Salidas Analógicas** | 2 | 0-5V |
| **RS485** | 1 puerto | Aislado, comunicación serial industrial |
| **USB** | 1 puerto USB 2.0 | Programación/debugging |

### Alimentación y Protección
- **Voltaje de entrada:** 10.8V - 36V DC
- **Protección:** Alta aislación, protección contra surges y cortocircuitos
- **RTC:** Reloj de tiempo real integrado
- **Chip de encriptación:** Atecc608a (opcional)

## 🏗️ Arquitectura de Implementación

### Para tu Sistema de Parada de Emergencia:

```
    TU COMPUTADOR          EdgeBox-ESP-100          DANFOSS R13
         │                        │                        │
         │   Comando parada       │                        │
         │ ─────────────────────► │                        │
         │                        │   Mensaje CANopen      │
         │                        │ ─────────────────────► │
         │                        │                        │
         │                        │   ✓ Confirmación       │
         │   ←──────────────────── │   ✓ Motores detenidos  │
         │   "Parada OK"           │                        │
```

### Ventajas Clave

1. **Protocolo CAN bus integrado** - Comunicación con R13 (requiere implementar stack CANopen)
2. **Ethernet industrial** - Integración en red de control
3. **Programable con ESP-IDF** - Desarrollo en C/C++ o MicroPython
4. **Aislamiento industrial** - Protección contra ruido eléctrico
5. **Temperatura industrial** - Funciona en ambientes de puente grúa

### ⚠️ Desventajas vs Requisito de Ubuntu IoT

1. **NO ejecuta Linux/Ubuntu IoT** - Es un microcontrolador, no un SBC
2. **Requiere desarrollo embebido** - No puedes usar librerías Python estándar de Linux
3. **Stack CANopen manual** - Debes implementar o portar biblioteca CANopen
4. **Menor capacidad de procesamiento** - vs Raspberry Pi o sistemas ARM

## 💰 Costo Total Estimado

| Componente | Precio | Cantidad | Subtotal |
|------------|--------|----------|----------|
| EdgeBox-ESP-100 | $139 | 1 | $139 |
| Cables CAN (terminados) | $15 | 1 | $15 |
| Alimentación 24V industrial | $25 | 1 | $25 |
| **TOTAL** | | | **$179** |

## 🛒 Enlaces de Compra

### Seeed Studio (Fabricante Directo)
- **Producto principal:** https://www.seeedstudio.com/EdgeBox-ESP-100-p-5490.html
- **Documentación técnica:** https://files.seeedstudio.com/wiki/edge_box_esp/Seeed_Studio_Edgebox-ESP-100.pdf
- **Manual de usuario:** https://files.seeedstudio.com/wiki/edge_box_esp/EdgeBox-ESP-100-User_manual-V1.1.pdf

### Distribuidores Alternativos
- **Arrow Electronics:** Buscar "EdgeBox-ESP-100"
- **DigiKey:** Buscar SKU 102991735
- **Mouser:** Buscar "EdgeBox ESP"

## 🔍 Búsqueda en Alibaba

**Términos de búsqueda recomendados:**
```
"EdgeBox ESP-100 industrial gateway"
"ESP32 CAN bus Ethernet gateway"
"industrial IoT gateway CAN RS485 Ethernet"
"Seeed Studio EdgeBox ESP-100"
```

**Filtros a aplicar:**
- Precio: $100 - $200
- Certificaciones: CE, FCC, RoHS
- Interfaces: CAN bus, Ethernet, RS485
- Aplicación: Industrial automation, IIoT gateway

## 📞 Contacto y Soporte

- **Sitio web:** https://www.seeedstudio.com/
- **Foro:** https://forum.seeedstudio.com/
- **Discord:** https://discord.com/invite/QqMgVwHT3X
- **Email:** order@seeed.io

## ✅ Conclusión

El **EdgeBox-ESP-100** es una opción **económica pero limitada** para tu proyecto:

### ✅ Ventajas
- ✅ **Precio accesible** ($139 vs $300+ de alternativas)
- ✅ **CAN bus nativo** con aislamiento industrial
- ✅ **Interfaces industriales** completas (DI/DO, AI/AO)
- ✅ **Certificaciones industriales** (CE, FCC, RoHS)
- ✅ **Conectividad múltiple** (Ethernet, WiFi, 4G)

### ❌ Desventajas Críticas
- ❌ **NO ejecuta Ubuntu IoT** (requisito inicial del proyecto)
- ❌ **NO es ARM Cortex** - Es Xtensa ESP32-S3
- ❌ **Requiere desarrollo embebido** - No Python/Linux estándar
- ❌ **Stack CANopen manual** - Mayor complejidad de desarrollo

### 🎯 Recomendación Final

**SI tu proyecto puede adaptarse a ESP32 sin Ubuntu IoT:**
- ✅ Compra el EdgeBox-ESP-100 ($139)
- ✅ Desarrolla con ESP-IDF + biblioteca CANopen

**SI necesitas Ubuntu IoT obligatoriamente:**
- ⭐ **Raspberry Pi CM4 + CAN HAT** (~$150-200)
- ⭐ **Revolution Pi Connect+ SE** (~$390)
- ⭐ **WAGO PFC200** (~$545)

Ver comparación completa en: [docs/hardware_gateways_comparison.md](./hardware_gateways_comparison.md)

---

*Documento generado: 13 de octubre de 2025*  
*Proyecto: Sistema de parada de emergencia puente grúa*  
*⚠️ Actualizado con especificaciones correctas del ESP32-S3*</content>
<parameter name="filePath">/Users/arturo/puente_grua/docs/edgebox_esp100_quote.md