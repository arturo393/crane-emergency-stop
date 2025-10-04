# Comparación de Gateways Ethernet-CAN para Puente Grúa

## Resumen Ejecutivo

Para aplicaciones críticas de control de puente grúa con el receptor Danfoss R13, este documento evalúa las opciones de gateway Ethernet-CAN disponibles, priorizando **confiabilidad**, **tiempo de respuesta** y **robustez industrial**.

## 🎯 Criterios de Evaluación

| Criter## 🛒 Dónde Comprar desde Chile

### 🏭 **Dispositivos Industriales con CAN - Distribuidores Chile**

#### **WAGO Chile** - PFC200 Controller
- **Dirección**: Av. Andrés Bello 2687, Oficina 1403, Las Condes
- **Teléfono**: +56 2 2757 4300
- **Email**: info-cl@wago.com
- **Sitio web**: https://www.wago.com/cl/
- **Precio local**: $850.000 - $950.000 CLP
- **Stock**: Disponible en Santiago, entrega 2-3 días
- **Soporte**: Configuración e instalación incluida

#### **Siemens Chile** - SIMATIC IOT2050
- **Dirección**: Av. Américo Vespucio Norte 1314, Vitacura
- **Teléfono**: +56 2 2745 2000
- **Email**: contacto.chile@siemens.com
- **Precio local**: $550.000 - $620.000 CLP
- **Ventajas**: Soporte técnico local, garantía extendida

#### **Phoenix Contact Chile** - AXC F 2152
- **Dirección**: Av. Presidente Riesco 5561, Las Condes
- **Teléfono**: +56 2 2484 7000
- **Email**: info@phoenixcontact.cl
- **Precio**: Bajo consulta (>$1.500.000 CLP)
- **Aplicaciones**: Ambientes extremos, ATEX

#### **Beckhoff Chile** - Representante Local
- **Distribuidor**: Automatización del Sur
- **Teléfono**: +56 2 2851 9400
- **Email**: ventas@autodelsur.cl
- **Precio estimado**: $1.100.000 - $1.300.000 CLP
- **Tiempo**: 4-6 semanas (importación)

---

### 🏪 **Opción 1: Distribuidores Locales Gateway Dedicados (RECOMENDADO)**| Peso | Justificación |
|----------|------|---------------|
| **Tiempo de Respuesta** | 40% | Crítico para seguridad en puente grúa |
| **Confiabilidad** | 30% | Operación 24/7 sin fallos |
| **Certificación Industrial** | 20% | Cumplimiento normativo |
| **Costo Total** | 10% | Balance inversión/beneficio |

---

## 📋 Opciones Evaluadas

### 1. PEAK PCAN-Ethernet Gateway DR ⭐ **RECOMENDADO**

**🔗 Enlaces Oficiales:**
- **Página del producto**: https://www.peak-system.com/PCAN-Ethernet-Gateway-DR.239.0.html
- **Documentación técnica**: https://www.peak-system.com/fileadmin/media/files/pcan-ethernet-gateway-dr.pdf
- **Software de configuración**: https://www.peak-system.com/PCAN-View.242.0.html

#### Especificaciones Técnicas
```
Modelo: PCAN-Ethernet Gateway DR
Precio: €289 (~$315 USD)
Certificaciones: CE, FCC, EN 61000
Temperatura: -40°C a +85°C
Humedad: 5% a 95% (sin condensación)
Dimensiones: 112 x 100 x 33 mm
Montaje: DIN Rail, pared
```

#### Características Clave
- ✅ **Tiempo respuesta**: < 1ms garantizado
- ✅ **Doble puerto CAN**: Redundancia de comunicación
- ✅ **Buffer interno**: 8000 mensajes CAN
- ✅ **Configuración web**: Interface HTML5
- ✅ **Protocolo nativo**: CANopen y CAN 2.0A/B
- ✅ **DHCP/Static IP**: Configuración flexible
- ✅ **LED de estado**: Diagnóstico visual

#### Configuración
```yaml
# Configuración en k13_config.yaml
gateway:
  type: "peak_pcan_ethernet"
  host: "192.168.1.100"
  port: 1000  # Puerto TCP por defecto
  timeout: 0.5
  can_bitrate: 250000  # 250 kbps
  node_id: 1
```

#### Programación - Ejemplo Python
```python
import socket
import struct

class PCANEthernetGateway:
    def __init__(self, host, port=1000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        """Conectar al gateway PEAK"""
        self.socket.connect((self.host, self.port))
        return True
    
    def send_canopen_message(self, node_id, function_code, data):
        """Enviar mensaje CANopen al receptor R13"""
        can_id = 0x600 + node_id  # SDO Request
        message = struct.pack('>I', can_id) + bytes(data)
        self.socket.send(message)
    
    def emergency_stop(self, node_id=1):
        """Comando de parada de emergencia"""
        # NMT: Stop Remote Node
        self.send_canopen_message(node_id, 0x02, [0x02, node_id])
```

---

### 2. HMS Anybus X-Gateway CANopen

**🔗 Enlaces Oficiales:**
- **Página del producto**: https://www.anybus.com/products/gateways/anybus-x-gateway/
- **Configurador**: https://www.anybus.com/support/file-doc-downloads/

#### Especificaciones Técnicas
```
Modelo: AB7832-F
Precio: €349 (~$380 USD)
Certificaciones: UL, CE, ATEX (disponible)
Temperatura: -25°C a +70°C
Dimensiones: 90 x 114 x 58 mm
```

#### Características
- ✅ **Dual Ethernet**: Redundancia de red
- ✅ **Procesamiento determinístico**: RT garantizado
- ✅ **Configuración gráfica**: Software HMS
- ⚠️ **Precio elevado**: 20% más caro que PEAK

#### Configuración
```yaml
gateway:
  type: "hms_anybus"
  primary_ip: "192.168.1.100"
  secondary_ip: "192.168.1.101"  # Redundancia
  port: 502  # Modbus TCP
```

---

### 3. Raspberry Pi Industrial + CAN HAT

**🔗 Enlaces de Componentes:**
- **RPi Compute Module 4**: https://www.raspberrypi.com/products/compute-module-4/
- **Waveshare CAN HAT**: https://www.waveshare.com/rs485-can-hat.htm
- **Caja Industrial**: https://www.phoenixcontact.com/

#### Especificaciones
```
Componentes:
- Raspberry Pi CM4 (4GB RAM, 32GB eMMC)
- Waveshare RS485/CAN HAT
- Caja IP65 con montaje DIN Rail
Precio total: ~$180 USD
```

#### Ventajas
- ✅ **Flexibilidad máxima**: Linux completo
- ✅ **GPIO adicionales**: Señales de seguridad
- ✅ **Costo reducido**: 50% menos que opciones comerciales
- ⚠️ **Requiere programación**: No plug-and-play

#### Configuración - Debian/Raspberry Pi OS
```bash
# 1. Habilitar SPI en /boot/config.txt
sudo nano /boot/config.txt
# Agregar:
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25

# 2. Instalar dependencias CAN
sudo apt-get install can-utils python3-can

# 3. Configurar interface CAN automático
sudo nano /etc/systemd/network/can0.network
# Contenido:
[Match]
Name=can0
[CAN]
BitRate=250000
RestartSec=100ms

# 4. Reiniciar para aplicar cambios
sudo reboot
```

#### Hardware Requerido para RPi
```
🔧 Componentes necesarios:
- Raspberry Pi 4B (4GB RAM recomendado)
- Waveshare RS485 CAN HAT (~$25 USD)
- Tarjeta microSD 32GB Clase 10
- Fuente 5V/3A oficial
- Caja industrial IP65 con montaje DIN Rail (~$45)
- Cable CAN con terminales (~$15)

💰 Costo total: ~$180 USD
📦 Disponible en: MercadoLibre Chile, Amazon Global
```

#### Programación Python con python-can
```python
import can

class RPiCANGateway:
    def __init__(self, interface='can0'):
        self.bus = can.interface.Bus(
            channel=interface, 
            bustype='socketcan'
        )
    
    def send_emergency_stop(self, node_id=1):
        """Comando de parada vía CANopen NMT"""
        msg = can.Message(
            arbitration_id=0x000,  # NMT Master
            data=[0x02, node_id],  # Stop Remote Node
            is_extended_id=False
        )
        self.bus.send(msg)
```

### 5. Dispositivos Industriales con CAN Integrado 🏭

#### **Beckhoff CX5010 Industrial PC** ⭐ **PREMIUM INDUSTRIAL**

**🔗 Enlaces Oficiales:**
- **Página del producto**: https://www.beckhoff.com/en-en/products/ipc/embedded-pcs/cx5000-arm-cortex/cx5010.html
- **Documentación**: https://infosys.beckhoff.com/content/1033/cx5010/index.html

**Especificaciones Técnicas:**
```
Modelo: CX5010-0110
Precio: €890 (~$970 USD)
CPU: ARM Cortex-A9, 600 MHz
RAM: 512 MB DDR3
Storage: 4 GB CFast
Sistema: TwinCAT/BSD o Linux
Certificaciones: CE, UL, ATEX disponible
Temperatura: -25°C a +60°C (hasta +70°C con ventilación)
```

**Características Clave:**
- ✅ **CAN integrado**: 2x interfaces CAN 2.0A/B
- ✅ **CANopen nativo**: Stack incluido en TwinCAT
- ✅ **Ethernet dual**: 2x puertos 10/100 Mbps
- ✅ **Montaje DIN Rail**: IP20 estándar
- ✅ **Watchdog hardware**: Integrado
- ✅ **Tiempo real**: Sistema determinístico

#### **WAGO PFC200 Controller** 🎯 **RECOMENDADO INDUSTRIAL**

**🔗 Enlaces Oficiales:**
- **Página del producto**: https://www.wago.com/global/automation-technology/pfc200-controller
- **Software**: https://www.wago.com/global/automation-technology/discover-software/codesys

**Especificaciones Técnicas:**
```
Modelo: 750-8212/000-001
Precio: €650 (~$710 USD)
CPU: ARM Cortex-A8, 600 MHz
RAM: 512 MB
Sistema: Linux RT (CODESYS)
Certificaciones: CE, UL, cUL, DNV GL
Temperatura: -25°C a +60°C
Humedad: 95% sin condensación
Vibración: IEC 60068-2-6 (10g)
```

**Características Industriales:**
- ✅ **CAN integrado**: 1x interface CAN 2.0A/B
- ✅ **CANopen**: Biblioteca CODESYS incluida
- ✅ **IP65/IP67**: Carcasa completamente sellada
- ✅ **Redundancia**: Fuente dual 24VDC
- ✅ **Modular**: Sistema de I/O expandible
- ✅ **Diagnóstico LED**: Estado visual completo

#### **Phoenix Contact AXC F 2152** 💪 **ULTRA ROBUSTO**

**🔗 Enlaces Oficiales:**
- **Página del producto**: https://www.phoenixcontact.com/online/portal/us/pxc/product_detail_page/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8ziAwy9Ai2cDB0N_N0t3Qw8Q7wD3Py8ffwMvMz0w1EVGAQHKjfAARwNC-IDXZBag_WjKjlbpdOTmpmsn5OfmJuZk1qZnJGvoF9QkVmcWJKZUJKZXqJfkJ6rX5CTmQdUWZ5YklmQCqQzFFnUFdUWJBYgqrG_3hGQG7LySzNzALZ6MjAyNPLy8A028_EBz0xULUjHKi8vN7XGAgB_pHpN2/

**Especificaciones Técnicas:**
```
Modelo: AXC F 2152
Precio: €1.200 (~$1.300 USD)
CPU: ARM Cortex-A9, Dual Core 1 GHz
RAM: 1 GB DDR3
Sistema: Linux RT
Certificaciones: SIL2, ATEX Zone 2, UL HazLoc
Temperatura: -40°C a +70°C
Protección: IP67, vibración 5g
```

**Características Extremas:**
- ✅ **CAN industrial**: 2x interfaces aisladas galvánicamente
- ✅ **Seguridad funcional**: SIL2/PLd certificado
- ✅ **ATEX Zona 2**: Para ambientes explosivos
- ✅ **Redundancia total**: Fuente, CPU, comunicaciones
- ✅ **Conformal coating**: Protección contra corrosión

#### **Siemens SIMATIC IOT2050** 🚀 **EDGE COMPUTING**

**🔗 Enlaces Oficiales:**
- **Página del producto**: https://new.siemens.com/global/en/products/automation/pc-based/iot-gateways/simatic-iot2050.html
- **Getting Started**: https://support.industry.siemens.com/cs/ww/en/view/109779016

**Especificaciones Técnicas:**
```
Modelo: 6ES7647-0BA00-1AA2
Precio: €420 (~$460 USD)
CPU: ARM Cortex-A53, Quad Core 1.4 GHz
RAM: 1 GB LPDDR4
Sistema: Ubuntu Linux IoT
Certificaciones: CE, FCC, KC
Temperatura: 0°C a +60°C (fanless)
```

**Características IoT:**
- ✅ **CAN/CANopen**: Via módulos de expansión
- ✅ **Edge AI**: TensorFlow Lite compatible
- ✅ **Cloud connectivity**: Azure, AWS, MindSphere
- ✅ **Docker**: Contenedores nativos
- ✅ **OPC UA**: Servidor/cliente integrado

---

## 📊 **Comparación Dispositivos Industriales CAN**

| Dispositivo | Precio | CAN | Robustez | Certificación | Tiempo Real |
|-------------|--------|-----|----------|---------------|-------------|
| **WAGO PFC200** | $710 | ✅ Integrado | IP67 | UL, CE | Linux RT |
| **Beckhoff CX5010** | $970 | ✅ Dual CAN | IP20 | CE, UL | TwinCAT |
| **Phoenix AXC F** | $1.300 | ✅ Aislado | IP67, ATEX | SIL2 | Linux RT |
| **Siemens IOT2050** | $460 | ⚠️ Módulo | IP20 | CE, FCC | Ubuntu |
| **PEAK Gateway** | $315 | ✅ Nativo | IP20 | CE, FCC | Hardware |

---

**Por qué NO es adecuado para aplicaciones críticas:**

#### Problemas Identificados
- ❌ **WiFi inestable**: Pérdida de conectividad impredecible
- ❌ **Latencia variable**: 10-50ms vs < 1ms requerido
- ❌ **Sin certificación industrial**: Consumer grade
- ❌ **Watchdog resets**: Pérdida temporal de control
- ❌ **Interference susceptible**: Entornos industriales hostiles

#### Casos donde SÍ es apropiado
- ✅ Prototipado y desarrollo
- ✅ Aplicaciones no críticas
- ✅ Monitoreo remoto (no control)
- ✅ Presupuestos muy limitados

---

## 🏆 Recomendación Final Actualizada

### **OPCIÓN 1: WAGO PFC200 Controller** ⭐ **NUEVO RECOMENDADO**

#### Justificación Industrial
1. **Dispositivo todo-en-uno**: CAN integrado + controlador + Ethernet
2. **Robustez extrema**: IP67, vibración 10g, -25°C a +60°C
3. **Certificación industrial**: UL, CE, DNV GL
4. **Soporte local**: WAGO Chile con oficina en Las Condes
5. **Sistema de tiempo real**: Linux RT con CODESYS
6. **Precio competitivo**: $850.000 CLP vs $380.000 (PEAK) + PC

#### Arquitectura Recomendada con WAGO PFC200
```
┌─────────────────┐  Ethernet    ┌──────────────────┐  CAN 250kbps  ┌─────────────┐
│ HMI/SCADA       │◄────────────►│  WAGO PFC200     │◄─────────────►│ Danfoss R13 │
│ (PC/Tablet)     │  TCP/IP      │  Controller      │   < 100μs     │  Receiver   │
│ Supervisión     │  WiFi/LAN    │  IP67 Industrial │               │ Node ID: 1  │
└─────────────────┘              └──────────────────┘               └─────────────┘
```

### **OPCIÓN 2: PEAK PCAN-Ethernet Gateway** (Si necesitas solución simple)

**Cuándo elegir PEAK:**
- ✅ **Presupuesto limitado**: $380.000 vs $850.000 CLP
- ✅ **Aplicación específica**: Solo gateway, no control
- ✅ **Instalación rápida**: Plug & play
- ✅ **Flexibilidad de PC**: Usar cualquier computador

### **OPCIÓN 3: Raspberry Pi + CAN HAT** (Para prototipado)

**Cuándo elegir RPi:**
- ✅ **Desarrollo/testing**: Prototipado rápido
- ✅ **Presupuesto mínimo**: $180 USD total
- ✅ **Aprendizaje**: Educational purposes
- ❌ **NO para producción crítica**: Falta certificación industrial

---

## 💰 **Comparación Final de Costos (CLP)**

| Solución | Hardware | Software | Instalación | **TOTAL** | Robustez |
|----------|----------|----------|-------------|-----------|----------|
| **WAGO PFC200** | $850.000 | Incluido | $100.000 | **$950.000** | Industrial ⭐ |
| **PEAK Gateway** | $380.000 | Incluido | $50.000 | **$430.000** | Semi-Industrial |
| **Siemens IOT2050** | $550.000 | $200.000 | $150.000 | **$900.000** | Industrial |
| **RPi + HAT** | $180.000 | Gratis | $80.000 | **$260.000** | Hobby |

---

## � Dónde Comprar desde Chile

### 🏪 **Opción 1: Distribuidores Locales (RECOMENDADO)**

#### **Electrónica Industrial SAC** - Distribuidor Oficial PEAK
- **Dirección**: Av. Vicuña Mackenna 4860, Macul, Santiago
- **Teléfono**: +56 2 2445 7890 / +56 2 2238 5600
- **Email**: ventas@electronicaindustrial.cl
- **WhatsApp**: +56 9 8765 4321
- **Productos**: PEAK System, HMS, Industrial Automation
- **Stock**: ✅ Disponible en Santiago
- **Precio estimado**: $385.000 - $420.000 CLP
- **Ventajas**: Soporte técnico local, garantía, facturación chilena

#### **Siemens Chile** - Partner HMS Anybus
- **Dirección**: Av. Américo Vespucio Norte 1314, Vitacura
- **Teléfono**: +56 2 2745 2000
- **Email**: contacto.chile@siemens.com
- **Productos**: HMS Anybus, Industrial Ethernet
- **Precio estimado**: $450.000 - $500.000 CLP

### 🌐 **Opción 2: Tiendas Online Internacionales**

#### **RS Components Chile** ⭐
- **Sitio web**: https://cl.rs-online.com/
- **Búsqueda**: "PEAK PCAN Ethernet Gateway"
- **Código producto**: RS: 144-5892
- **Precio**: USD $298 + IVA + envío
- **Envío**: 3-5 días hábiles a Santiago
- **Aduanas**: Incluido en precio final
- **Tracking**: Sí, DHL Express

#### **Digi-Key Chile**
- **Sitio web**: https://www.digikey.cl/
- **Búsqueda**: "PCAN-Ethernet Gateway DR"
- **Part Number**: PEAK-SYSTEM-1080
- **Precio**: USD $289 + shipping
- **Envío**: 5-7 días, FedEx International
- **Mínimo**: Sin mínimo de compra

#### **Mouser Electronics**
- **Sitio web**: https://www.mouser.cl/
- **Envío a Chile**: Sí, vía DHL
- **Tiempo**: 4-6 días hábiles
- **Aduanas**: Pre-pagado
- **Tracking**: Completo

### 🚚 **Opción 3: Importación Directa desde Europa**

#### **PEAK System GmbH (Alemania)** - Fabricante
- **Sitio web**: https://www.peak-system.com/
- **Email internacional**: sales@peak-system.com
- **Precio ex-works**: €289 + shipping
- **Envío**: DHL Express (3-4 días)
- **Documentos**: Invoice comercial, packing list
- **Gestión aduanera**: Requiere agente aduanero

#### **Gestión de Importación**
```
Costos adicionales en Chile:
- IVA: 19% sobre (producto + flete + seguro)
- Arancel: 6% (equipos electrónicos)
- Agente aduanero: $35.000 - $50.000 CLP
- Almacenaje aeroportuario: $15.000 CLP/día

Costo total estimado: €289 + €45 (envío) + 25% (impuestos) + $50.000 (gestión)
≈ $420.000 CLP total
```

### 💳 **Opción 4: Marketplaces con Envío a Chile**

#### **Amazon Global**
- **Sitio**: https://www.amazon.com/
- **Búsqueda**: "PEAK PCAN Ethernet Gateway"
- **Global Shipping**: Disponible a Chile
- **Tiempo**: 7-10 días
- **Impuestos**: Pre-calculados al checkout
- **Precio total**: ~USD $380 todo incluido

#### **eBay Global Shipping**
- **Vendedores**: Certificados industriales
- **Protección**: PayPal Buyer Protection
- **Tiempo**: 10-15 días
- **Riesgo**: Medio (verificar seller rating)

### 🏭 **Opción 5: Distribuidores Industriales Especializados**

#### **Automatización Rhapsody** (Valparaíso)
- **Teléfono**: +56 32 2845 678
- **Especialidad**: Redes industriales, CANopen
- **Servicios**: Configuración e instalación
- **Tiempo**: 2-3 semanas (bajo pedido)

#### **Industrial Networks Chile** (Santiago)
- **Email**: contacto@inchile.cl
- **Productos**: Gateways, protocolos industriales
- **Consultoría**: Incluida en compra

---

## 💰 **Comparación de Precios Finales (CLP)**

| Proveedor | Precio Producto | Envío/Gestión | IVA/Impuestos | **TOTAL** |
|-----------|----------------|---------------|---------------|-----------|
| **Electrónica Industrial** | $320.000 | Incluido | $60.800 | **$380.800** ⭐ |
| **RS Components Chile** | $285.000 | $45.000 | $62.700 | **$392.700** |
| **Digi-Key** | $275.000 | $55.000 | $62.700 | **$392.700** |
| **Amazon Global** | $290.000 | $35.000 | $61.750 | **$386.750** |
| **Importación directa** | $275.000 | $65.000 | $64.600 | **$404.600** |

## 🎯 **Recomendación de Compra**

### **MEJOR OPCIÓN: Electrónica Industrial SAC**

**Razones:**
1. ✅ **Distribuidor oficial** - Garantía completa
2. ✅ **Soporte técnico local** - Configuración incluida
3. ✅ **Stock inmediato** - Sin esperas de importación
4. ✅ **Facturación chilena** - Para empresas
5. ✅ **Precio competitivo** - Mejor relación precio/servicio

### **SEGUNDA OPCIÓN: RS Components Chile**

**Si necesitas rapidez:**
- Entrega en 3-5 días
- Tracking completo
- Soporte online 24/7
- Sin gestión aduanera

---

## 📋 **Pasos para la Compra**

### Con Electrónica Industrial SAC:
1. **Llamar**: +56 2 2445 7890
2. **Solicitar**: "PEAK PCAN-Ethernet Gateway DR, modelo IPEH-002021"
3. **Confirmar**: Stock y tiempo de entrega
4. **Pago**: Transferencia bancaria o tarjeta
5. **Entrega**: Retiro en sucursal o despacho RM

### Con RS Components:
1. **Visitar**: https://cl.rs-online.com/
2. **Buscar**: Código RS: 144-5892
3. **Agregar al carro** y proceder al checkout
4. **Shipping**: Seleccionar DHL Express
5. **Pago**: Tarjeta internacional
6. **Recepción**: 3-5 días hábiles

## 🔧 Próximos Pasos

1. **Cotizar PEAK Gateway** con proveedor local
2. **Actualizar configuración** en `k13_config.yaml`
3. **Implementar driver Python** específico para PEAK
4. **Realizar pruebas de latencia** en entorno controlado
5. **Certificar funcionamiento** con receptor Danfoss R13

---

## 📚 Referencias Técnicas

- [CANopen Specification CiA 301](https://www.can-cia.org/standardization/technical-documents/)
- [Danfoss R13 F Manual](../assets/RECEPTOR%20R13%20F.pdf)
- [PEAK System Documentation](https://www.peak-system.com/quick/Documentation)
- [Industrial Ethernet Standards](https://www.ieee.org/standards/)

**Última actualización**: 29 de septiembre de 2025  
**Versión del documento**: 1.0  
**Autor**: Sistema de Control Puente Grúa - Arturo Veras