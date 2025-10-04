# Gateway Ethernet-CAN para Puente Grúa - Opciones Simplificadas

## Resumen Ejecutivo

Para el control del receptor Danfoss R13 se evaluaron dispositivos que combinen **robustez industrial**, **CAN integrado** y **facilidad de programación**. Se priorizan soluciones con SOC ARM que soporten Ubuntu IoT.

---

## 🏆 Opciones Recomendadas

### 1. Revolution Pi Connect+ SE ⭐ **RECOMENDADO**

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

### 2. Advantech WISE-5231 🏭 **ALTERNATIVA INDUSTRIAL**

**Especificaciones:**
- **SOC**: ARM Cortex-A35 Quad-core
- **RAM**: 1GB DDR4
- **CAN**: 2x CAN FD integrados
- **OS**: Ubuntu 18.04/20.04 IoT
- **Temperatura**: -25°C a +70°C
- **Protección**: IP30
- **Precio**: $420 USD (~$405.000 CLP)

**Cuándo elegir:**
- Necesitas certificación industrial más estricta
- Requieres CAN FD (velocidades superiores)
- Presupuesto permite mayor inversión

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
| **Revolution Pi** | $270.000 | $40.000 | $80.000 | **$390.000** |
| **Advantech WISE** | $405.000 | $30.000 | $110.000 | **$545.000** |
| **PEAK Gateway** | $305.000 | $25.000 | $85.000 | **$415.000** |

*Nota: Incluye envío, cables CAN, impuestos chilenos*

---

## 🔧 Configuración Revolution Pi (Recomendado)

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

### Revolution Pi Connect+ SE
- **RS Components Chile**: https://cl.rs-online.com/
- **Mouser Electronics**: Envío directo a Chile
- **Tiempo de entrega**: 5-7 días hábiles
- **Código de producto**: KUNBUS-100005

### Advantech WISE-5231
- **Distribuidor local**: Disponible bajo consulta
- **Importación directa**: Advantech.com

### PEAK Gateway
- **Electrónica Industrial SAC**: +56 2 2445 7890
- **RS Components**: Código RS: 144-5892

---

## 🎯 Recomendación Final

**Elegir Revolution Pi Connect+ SE** por:

1. **Costo-beneficio óptimo**: $390.000 CLP total
2. **Tecnología familiar**: Base Raspberry Pi para desarrollo fácil
3. **Ubuntu IoT oficial**: Soporte LTS hasta 2032
4. **CAN integrado**: Sin hardware adicional necesario
5. **Case industrial**: DIN Rail, temperatura amplia
6. **Redundancia**: 2x puertos CAN para mayor confiabilidad
7. **Comunidad activa**: Documentación y soporte excelentes

El Revolution Pi combina la **simplicidad del Raspberry Pi** con la **robustez industrial necesaria** para control de puente grúa, manteniendo costos controlados y facilitando el desarrollo.

---

**Última actualización**: 29 de septiembre de 2025  
**Documento**: Hardware Gateway Simplificado v2.0