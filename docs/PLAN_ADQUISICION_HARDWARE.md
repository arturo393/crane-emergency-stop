# 📦 Plan de Adquisición de Hardware - K13 Puente Grúa

**Fecha**: 24 de octubre de 2025  
**Presupuesto**: ~$150 USD  
**Timeline**: 15-20 días envío

---

## 🎯 Objetivo

Adquirir hardware necesario para validar sistema de control K13 Puente Grúa con equipamiento real y migrar de simulación a producción.

---

## 📋 Lista de Compra Priorizada

### Prioridad ALTA - Esenciales (Total: ~$107 USD)

#### 1. BL335 Gateway - $35 USD
**Descripción**: Industrial Embedded Computer, Ethernet-CAN gateway  
**Especificaciones**:
- Procesador: ARM Cortex-A7
- RAM: 512MB
- Ethernet: 10/100 Mbps
- CAN Bus: ISO 11898-2 compliant
- Sistema: Linux embebido
- Alimentación: 12-24V DC

**Proveedor**: AliExpress / Alibaba  
**Enlace**: Buscar "BL335 Industrial Gateway"  
**Tiempo envío**: 15-20 días  
**Uso**: Gateway principal Ethernet→CAN para producción

**Validaciones necesarias**:
- ✅ Configuración SocketCAN en Linux
- ✅ Comunicación CANopen con K13 F
- ✅ Latencia < 100ms para emergency stop
- ✅ Estabilidad 24/7

---

#### 2. EdgeBox-ESP-100 - $45 USD
**Descripción**: ESP32-S3 Industrial IoT Gateway  
**Especificaciones**:
- MCU: ESP32-S3 Dual-core 240MHz
- RAM: 8MB PSRAM
- Flash: 16MB
- WiFi: 802.11 b/g/n
- Ethernet: 10/100 Mbps (W5500)
- CAN: SN65HVD230 transceiver
- Alimentación: 5V DC (USB-C)

**Proveedor**: Seeed Studio / AliExpress  
**Enlace**: https://www.seeedstudio.com/EdgeBox-ESP-100-p-5490.html  
**Tiempo envío**: 10-15 días  
**Uso**: Gateway alternativo WiFi/Ethernet→CAN

**Validaciones necesarias**:
- ✅ Compilar firmware ESP-IDF
- ✅ TCP/IP server funcionando
- ✅ CAN bus communication
- ✅ Comparar performance vs BL335

---

#### 3. X8 Development Board - $8 USD
**Descripción**: ESP32-S3 DevKit básico  
**Especificaciones**:
- MCU: ESP32-S3-WROOM-1
- USB: Type-C para programación
- Pines: GPIO expuestos
- Display: Opcional (algunos modelos)

**Proveedor**: AliExpress  
**Enlace**: Buscar "X8 ESP32-S3 Development Board"  
**Tiempo envío**: 15-20 días  
**Uso**: Prototipado rápido, testing firmware

**Nota**: Alternativa económica al EdgeBox para testing inicial

---

#### 4. Cables y Conectores - $19 USD

##### Cable CAN Bus DB9 (2 unidades) - $10
- Longitud: 3 metros cada uno
- Conectores: DB9 macho/hembra
- Especificación: Twisted pair shielded
- Uso: Conectar gateway ↔ K13 F

##### Terminadores CAN 120Ω (2 unidades) - $3
- Resistencia: 120Ω ±1%
- Conector: DB9
- Uso: Terminación de bus CAN (extremos)

##### Fuente de Alimentación 12V/2A - $6
- Salida: 12V DC, 2A
- Conector: Barrel jack 5.5mm
- Uso: Alimentar BL335

---

### Prioridad MEDIA - Complementarios (Total: ~$25 USD)

#### 5. Multímetro Digital - $12 USD
**Uso**: Verificar voltajes, continuidad de cables CAN
**Características**: DC/AC voltage, resistance, continuity

#### 6. Analizador Lógico USB - $8 USD
**Uso**: Debugging señales CAN (opcional)
**Características**: 8 canales, compatible con Sigrok/PulseView

#### 7. Case para BL335 - $5 USD
**Uso**: Protección del gateway en entorno industrial

---

### Prioridad BAJA - Opcionales (Total: ~$50 USD)

#### 8. Raspberry Pi 4 (4GB) - $45 USD
**Uso**: Gateway Linux alternativo con más recursos
**Nota**: Solo si BL335 no cumple requisitos

#### 9. CAN-USB Adapter - $15 USD (ya tenemos simulador virtual)
**Uso**: Debugging directo del bus CAN desde PC

---

## 💰 Presupuesto Final

### Escenario Mínimo (Esenciales)
```
BL335 Gateway          $35
EdgeBox-ESP-100        $45
X8 Development Board   $8
Cables y Conectores    $19
────────────────────────
Subtotal              $107
Envío estimado        $15-25
────────────────────────
TOTAL                 $122-132 USD
```

### Escenario Completo (Esenciales + Complementarios)
```
Esenciales            $107
Complementarios       $25
────────────────────────
Subtotal              $132
Envío estimado        $20-30
────────────────────────
TOTAL                 $152-162 USD
```

---

## 📅 Timeline de Adquisición

### Semana 1-2 (25 oct - 8 nov)
- [x] Documentar plan de compra (este documento)
- [ ] Investigar proveedores específicos
- [ ] Comparar precios en AliExpress/Alibaba/Seeed
- [ ] Verificar stock disponible
- [ ] Preparar cuenta de pago (PayPal/Tarjeta)

### Semana 2 (8-15 nov)
- [ ] **Comprar**: BL335 + cables básicos (prioridad #1)
- [ ] **Comprar**: EdgeBox-ESP-100 (prioridad #2)
- [ ] **Comprar**: X8 DevBoard (opcional, bajo costo)
- [ ] Obtener números de tracking
- [ ] Documentar pedidos en proyecto

### Semana 3-4 (15 nov - 1 dic)
- [ ] Seguimiento de envíos
- [ ] Recepción de paquetes
- [ ] Inspección física de hardware
- [ ] Inventario de componentes recibidos

### Semana 5 (1-8 dic)
- [ ] Unboxing y documentación fotográfica
- [ ] Testing inicial de hardware
- [ ] Configuración de BL335 (Linux + SocketCAN)
- [ ] Programación de EdgeBox (ESP-IDF firmware)

---

## 🔍 Criterios de Selección de Proveedores

### AliExpress
**Ventajas**:
- ✅ Precios más bajos
- ✅ Variedad de vendedores
- ✅ Protección del comprador
- ✅ Envío gratis frecuente

**Desventajas**:
- ❌ Tiempo de envío largo (20-30 días)
- ❌ Calidad variable
- ❌ Soporte técnico limitado

**Recomendado para**: Cables, conectores, X8, multímetro

---

### Seeed Studio
**Ventajas**:
- ✅ Hardware certificado
- ✅ Documentación completa
- ✅ Soporte técnico
- ✅ Envío más rápido (10-15 días)

**Desventajas**:
- ❌ Precios más altos
- ❌ Stock limitado

**Recomendado para**: EdgeBox-ESP-100

---

### Alibaba (Compra al por mayor)
**Ventajas**:
- ✅ Precios al por mayor
- ✅ Contacto directo con fabricantes
- ✅ Personalización posible

**Desventajas**:
- ❌ MOQ (Minimum Order Quantity) alto
- ❌ Negociación requerida
- ❌ No apto para 1-2 unidades

**Recomendado para**: BL335 si compramos 5+ unidades (proyecto futuro)

---

## 📝 Checklist de Compra

### Antes de Comprar
- [ ] Verificar voltajes de alimentación (12V/24V/5V)
- [ ] Confirmar conectores CAN (DB9 vs terminal block)
- [ ] Revisar reviews de vendedores (>95% rating, 1000+ ventas)
- [ ] Verificar tiempo de envío estimado
- [ ] Confirmar política de devolución
- [ ] Calcular costo total con envío + impuestos

### Al Comprar
- [ ] Guardar número de orden
- [ ] Obtener tracking number
- [ ] Documentar fecha de compra
- [ ] Contactar vendedor para confirmar stock
- [ ] Solicitar factura (si aplica)

### Al Recibir
- [ ] Inspeccionar paquete (daños externos)
- [ ] Verificar contenido vs orden
- [ ] Testing básico (continuidad, alimentación)
- [ ] Fotografías de componentes
- [ ] Confirmar recepción con vendedor
- [ ] Dejar review (si satisfactorio)

---

## 🛠️ Plan de Validación de Hardware

### BL335 Gateway

#### Fase 1: Configuración Inicial (1 día)
- [ ] Conectar alimentación 12V
- [ ] Conectar Ethernet a PC
- [ ] Acceder vía SSH (IP por defecto o DHCP)
- [ ] Verificar sistema operativo (uname -a)
- [ ] Actualizar firmware (si disponible)

#### Fase 2: Configuración SocketCAN (1 día)
- [ ] Instalar can-utils (apt-get install can-utils)
- [ ] Configurar interfaz CAN (ip link set can0 type can bitrate 250000)
- [ ] Probar loopback (candump can0 & cansend can0 123#DEADBEEF)
- [ ] Verificar estadísticas (ip -details -statistics link show can0)

#### Fase 3: Integración CANopen (2-3 días)
- [ ] Instalar python-canopen
- [ ] Cargar EDS Danfoss R13 F
- [ ] Probar NMT commands
- [ ] Validar SDO read/write
- [ ] Testear PDO mapping
- [ ] Medir latencia emergency stop

#### Fase 4: Pruebas de Estrés (1 día)
- [ ] Test 24 horas continuos
- [ ] Verificar memory leaks
- [ ] Monitoring de temperatura
- [ ] Log de errores CAN

---

### EdgeBox-ESP-100

#### Fase 1: Setup Development (1 día)
- [ ] Instalar ESP-IDF v5.1
- [ ] Compilar firmware básico
- [ ] Flashear con esptool.py
- [ ] Verificar boot correcto (serial monitor)

#### Fase 2: Testing Componentes (2 días)
- [ ] Test WiFi (connect to AP, get IP)
- [ ] Test Ethernet (W5500, ping gateway)
- [ ] Test CAN (send/receive frames)
- [ ] Test TCP server (accept connections)

#### Fase 3: Integración Completa (2-3 días)
- [ ] Compilar firmware del proyecto (esp32_gateway/)
- [ ] Configurar TCP→CAN bridge
- [ ] Probar comandos JSON
- [ ] Validar emergency stop
- [ ] Medir latencia vs BL335

---

## 📊 Matriz de Decisión Final

### Criterios de Evaluación (1-10)

| Criterio | BL335 | EdgeBox | Raspberry Pi 4 |
|----------|-------|---------|----------------|
| **Costo** | 9 ($35) | 7 ($45) | 5 ($45+) |
| **Performance** | 7 | 8 | 9 |
| **Confiabilidad** | 8 | 7 | 8 |
| **Facilidad Setup** | 6 | 8 | 9 |
| **Soporte Industrial** | 8 | 7 | 5 |
| **Consumo Energía** | 8 | 9 | 6 |
| **Documentación** | 6 | 8 | 10 |
| **Certificaciones** | 7 | 6 | 4 |
| **TOTAL** | **59/80** | **60/80** | **56/80** |

**Recomendación**: 
1. **EdgeBox-ESP-100** (60 pts) - Balance ideal
2. **BL335** (59 pts) - Mejor costo
3. **Raspberry Pi 4** (56 pts) - Solo si los anteriores fallan

**Estrategia**: Comprar EdgeBox + BL335 para tener respaldo y comparar performance real.

---

## 🔗 Enlaces de Referencia

### Proveedores
- **AliExpress**: https://www.aliexpress.com/
- **Seeed Studio**: https://www.seeedstudio.com/
- **Mouser Electronics**: https://www.mouser.com/ (más rápido, más caro)
- **DigiKey**: https://www.digikey.com/ (distribución global)

### Documentación Técnica
- BL335: `docs/hardware_consolidado.md`
- EdgeBox: `docs/edgebox_esp100_quote.md`
- CAN Bus Wiring: `docs/hardware/k13_hardware_specs.md`
- ESP32 Gateway: `esp32_gateway/README.md`

### Scripts de Configuración
- BL335 Setup: `scripts/edgebox_setup.py`
- CAN Gateway RPi: `scripts/canopen_gateway_rpi.py`
- ESP32 Build: `esp32_gateway/build/README.md`

---

## 📞 Contactos de Vendedores (Actualizar tras compra)

### BL335
- Vendedor: TBD
- Email: TBD
- Número de orden: TBD
- Fecha compra: TBD

### EdgeBox-ESP-100
- Vendedor: Seeed Studio
- Email: order@seeed.cc
- Número de orden: TBD
- Fecha compra: TBD

---

## ✅ Próximos Pasos Inmediatos

1. **HOY (24 oct)**:
   - [x] Crear este plan de adquisición
   - [ ] Investigar vendedores en AliExpress/Seeed
   - [ ] Comparar precios finales con envío

2. **MAÑANA (25 oct)**:
   - [ ] Decidir configuración final de compra
   - [ ] Preparar método de pago
   - [ ] Realizar pedidos (BL335 + EdgeBox + cables)

3. **ESTA SEMANA**:
   - [ ] Obtener tracking numbers
   - [ ] Actualizar este documento con detalles de compra
   - [ ] Preparar ambiente de desarrollo para recepción

4. **PRÓXIMAS 3 SEMANAS**:
   - [ ] Seguimiento de envíos
   - [ ] Recepción y unboxing
   - [ ] Testing inicial
   - [ ] Integración con proyecto

---

**Documento vivo**: Este plan se actualizará conforme avance el proceso de compra y recepción de hardware.

**Última actualización**: 24 de octubre de 2025  
**Responsable**: Arturo  
**Estado**: 📋 Plan listo, esperando aprobación para compra
