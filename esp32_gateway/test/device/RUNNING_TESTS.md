# 🧪 Cómo Ejecutar los Tests del ESP32 Gateway

📅 **Actualizado:** 2 de Noviembre de 2025  
🎯 **Proyecto:** K13 Puente Grúa - ESP32 Gateway

---

## 🚀 **MÉTODO RÁPIDO (Recomendado)**

### **1. Preparar entorno**

```bash
# Activar ESP-IDF
. ~/esp/esp-idf/export.sh

# Ir al directorio de tests
cd esp32_gateway/test/device
```

### **2. Ejecutar un test**

```bash
# Usar el script helper
./run_test.sh <nombre_del_test>
```

### **3. Ejemplos**

```bash
# Test más simple (no requiere hardware externo)
./run_test.sh test_auth_manager

# Test de configuración
./run_test.sh test_config_manager

# Test de Ethernet (requiere W5500 + cable + router)
./run_test.sh test_ethernet_manager

# Test de Web Server
./run_test.sh test_web_server

# Test de SD Logger (requiere SD card)
./run_test.sh test_sd_logger
```

---

## 📋 **TESTS DISPONIBLES**

| Test | Hardware Requerido | Nivel |
|------|-------------------|-------|
| `test_auth_manager` | Solo ESP32 ⚡ | FÁCIL |
| `test_config_manager` | Solo ESP32 (SD opcional) | FÁCIL |
| `test_can_bus_init` | Solo ESP32 | FÁCIL |
| `test_sd_logger` | ESP32 + SD card 💾 | MEDIO |
| `test_ota_manager` | Solo ESP32 | MEDIO |
| `test_w5500_spi_init` | ESP32 + W5500 🌐 | MEDIO |
| `test_ethernet_manager` | ESP32 + W5500 + Cable + Router 🌐 | DIFÍCIL |
| `test_web_server` | ESP32 + Ethernet funcionando 🌐 | DIFÍCIL |
| `test_digital_io` | ESP32 (wire para loopback) | MEDIO |

---

## 🔧 **MÉTODO MANUAL**

Si prefieres hacerlo paso a paso:

### **1. Limpiar build anterior**

```bash
cd esp32_gateway
idf.py fullclean
```

### **2. Compilar test específico**

Edita `test/device/CMakeLists.txt` y cambia la línea:

```cmake
set(TEST_COMPONENT "test_can_bus_init")  # Cambiar aquí
```

Por el test que quieres ejecutar, ejemplo:

```cmake
set(TEST_COMPONENT "test_auth_manager")
```

### **3. Compilar**

```bash
idf.py build
```

### **4. Flashear y monitorear**

```bash
# Ver puertos disponibles
ls /dev/tty.usbserial-*

# Flashear y abrir monitor
idf.py -p /dev/tty.usbserial-XXXXXX flash monitor
```

Presiona `Ctrl+]` para salir del monitor.

---

## 📊 **INTERPRETANDO LOS RESULTADOS**

### **✅ Test Exitoso**

```
========================================
Starting Auth Manager Device Tests
========================================

Running test_auth_init...
I (1234) TEST_AUTH: Setting up Auth Manager test...
I (1235) TEST_AUTH: Test: Auth Manager Initialization
I (1240) TEST_AUTH: ✓ Auth manager initialized

1 Tests 0 Failures 0 Ignored
OK
========================================
All Auth Manager tests completed!
========================================
```

**Significado:** Todo funcionó correctamente ✅

---

### **⚠️ Test Ignorado (Hardware Faltante)**

```
Running test_ethernet_dhcp...
I (5678) TEST_ETH: Test: DHCP Configuration
W (15678) TEST_ETH: ⚠ Could not get IP via DHCP (no router?)

1 Tests 0 Failures 1 Ignored
OK
```

**Significado:** Test se saltó porque falta hardware (normal) ⚠️

Esto NO es un error - solo indica que ese hardware no está disponible.

---

### **❌ Test Fallido**

```
Running test_sd_init...
E (2345) TEST_SD: SD card initialization failed!

esp32_gateway/test/device/test_sd_logger.cpp:78:test_sd_init:
FAIL: SD card should initialize

-----------------------
1 Tests 1 Failures 0 Ignored
FAIL
```

**Significado:** Algo está mal ❌

Posibles causas:
- Hardware no conectado correctamente
- Pines mal configurados en `hardware_config.h`
- Voltaje incorrecto
- Cable defectuoso

---

## 🐛 **TROUBLESHOOTING**

### **Problema: No se detecta ESP32**

```
Error: No se detectó ningún ESP32 conectado
```

**Solución:**
1. Conecta el ESP32-S3 por USB
2. Verifica drivers:
   ```bash
   ls /dev/tty.usbserial-*
   # o en Linux:
   ls /dev/ttyUSB*
   ```
3. Instala drivers si es necesario (CP210x o CH340)

---

### **Problema: Error de compilación**

```
fatal error: auth_manager.h: No such file or directory
```

**Solución:**
1. Verifica que estás en el directorio correcto:
   ```bash
   pwd
   # Debe ser: .../esp32_gateway
   ```
2. Verifica que `CMakeLists.txt` tiene los `INCLUDE_DIRS` correctos
3. Ejecuta `idf.py fullclean` y recompila

---

### **Problema: Test falla inmediatamente**

```
Guru Meditation Error: Core 0 panic'ed (LoadProhibited)
```

**Solución:**
1. Puede ser un **nullptr** - revisa el código del test
2. Puede ser **stack overflow** - aumenta stack size en `sdkconfig`
3. Ejecuta con debugger: `idf.py gdb`

---

### **Problema: DHCP timeout**

```
W (15000) TEST_ETH: ⚠ Could not get IP via DHCP
```

**Solución:**
1. Verifica que el **cable Ethernet está conectado**
2. Verifica que hay un **router con DHCP** en la red
3. Prueba con IP estática: `test_ethernet_static_ip`

---

## 🔍 **VERIFICACIÓN DE HARDWARE**

Antes de ejecutar tests complejos, verifica el hardware:

### **1. Verificar SD Card**

```bash
./run_test.sh test_sd_logger
```

Deberías ver:
```
✓ SD card mounted successfully
✓ Write test passed
Total: XXXX MB, Used: XXX MB
```

---

### **2. Verificar W5500 (Ethernet)**

```bash
./run_test.sh test_w5500_spi_init
```

Deberías ver:
```
✓ SPI bus initialized
✓ W5500 reset complete
W5500 Version Register: 0x04
✓ W5500 is responding correctly!
```

Si ves `0x00` o `0xFF` → Revisa conexiones SPI

---

### **3. Verificar CAN Bus**

```bash
./run_test.sh test_can_bus_init
```

Deberías ver:
```
✓ TWAI driver installed successfully
✓ TWAI driver started successfully
```

---

## 📁 **ESTRUCTURA DE ARCHIVOS**

```
esp32_gateway/test/device/
├── run_test.sh              ← Script para ejecutar tests
├── RUNNING_TESTS.md         ← Este archivo
├── FILOSOFIA_TESTS.md       ← Explicación de los tests
├── TEST_SUMMARY.md          ← Resumen de cobertura
├── CMakeLists.txt           ← Configuración de build
│
├── test_auth_manager.cpp    ← 10 tests de autenticación
├── test_config_manager.cpp  ← 10 tests de configuración
├── test_web_server.cpp      ← 8 tests de servidor web
├── test_ethernet_manager.cpp ← 10 tests de Ethernet
├── test_sd_logger.cpp       ← 13 tests de SD logging
├── test_ota_manager.cpp     ← 8 tests de OTA updates
├── test_can_bus_init.cpp    ← 2 tests de CAN bus
├── test_w5500_spi_init.cpp  ← 3 tests de W5500 SPI
└── test_digital_io.cpp      ← 5 tests de I/O digital
```

---

## 🎯 **ORDEN RECOMENDADO DE TESTS**

Para validar el hardware progresivamente:

### **Fase 1: Software Puro (no requiere hardware extra)**

```bash
./run_test.sh test_auth_manager      # ✅ Más simple
./run_test.sh test_config_manager    # ✅ Simple
./run_test.sh test_can_bus_init      # ✅ Solo driver
```

### **Fase 2: Hardware Individual**

```bash
./run_test.sh test_sd_logger         # 💾 Requiere SD
./run_test.sh test_w5500_spi_init    # 🌐 Requiere W5500
./run_test.sh test_digital_io        # 🔌 Requiere wire
```

### **Fase 3: Hardware Complejo**

```bash
./run_test.sh test_ethernet_manager  # 🌐 Requiere red completa
./run_test.sh test_web_server        # 🌐 Requiere Ethernet OK
./run_test.sh test_ota_manager       # 📡 Requiere red (opcional)
```

---

## 📊 **CHECKLIST DE HARDWARE**

Antes de testear, verifica que tienes:

```
Hardware Básico:
☐ ESP32-S3 EdgeBox-Lite conectado por USB
☐ Cable USB-C funcional
☐ Drivers CP210x o CH340 instalados

Hardware Opcional (según test):
☐ SD card insertada (FAT32 recomendado)
☐ Módulo W5500 conectado por SPI
☐ Cable Ethernet CAT5/CAT6
☐ Router o switch con DHCP
☐ LEDs para tests de I/O (opcional)
☐ Wire para loopback tests (DO0 → DI0)

Software:
☐ ESP-IDF 5.1.5 instalado
☐ ESP-IDF exportado (. ~/esp/esp-idf/export.sh)
☐ Python 3.11 con esptool
```

---

## 💡 **TIPS ÚTILES**

### **1. Ver solo errores**

```bash
./run_test.sh test_auth_manager 2>&1 | grep -E "(FAIL|Error|error)"
```

### **2. Guardar log completo**

```bash
./run_test.sh test_ethernet_manager 2>&1 | tee test_log.txt
```

### **3. Test rápido sin monitor**

```bash
cd esp32_gateway
idf.py build flash
# No abre monitor - útil para CI/CD
```

### **4. Ver tamaño del binario**

```bash
idf.py size
```

---

## 🚀 **SIGUIENTE PASO**

Una vez que todos los tests pasen:

1. ✅ Hardware validado
2. 🔄 Integrar en aplicación principal
3. 🧪 Tests end-to-end
4. 🚀 Deploy a producción

---

## 📞 **SOPORTE**

Si tienes problemas:

1. Lee `FILOSOFIA_TESTS.md` para entender el diseño
2. Lee `TEST_SUMMARY.md` para ver cobertura
3. Revisa logs con `idf.py monitor`
4. Verifica pines en `main/hardware_config.h`

---

**Autor:** Arturo  
**Fecha:** 2 de Noviembre de 2025  
**Proyecto:** K13 Puente Grúa - ESP32 Gateway
