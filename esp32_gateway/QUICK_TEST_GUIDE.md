# 🧪 Guía Rápida de Ejecución de Tests

## 📝 Resumen

Has creado **69 tests** en 9 archivos que validan el ESP32 Gateway.

## 🚀 Ejecución Rápida

### **Opción 1: Script Automático** (Recomendado)

```bash
cd esp32_gateway

# Ver lista de tests disponibles
./run_tests.sh

# Ejecutar test específico por nombre
./run_tests.sh auth          # Auth Manager (no requiere hardware)
./run_tests.sh config        # Config Manager (opcional SD)
./run_tests.sh sd            # SD Logger (requiere SD card)
./run_tests.sh eth           # Ethernet (requiere W5500 + cable)
./run_tests.sh web           # Web Server (requiere Ethernet)

# Ejecutar por número
./run_tests.sh 1             # Primer test de la lista

# Ejecutar TODOS los tests en orden recomendado
./run_tests.sh all
```

### **Opción 2: Manual**

```bash
cd esp32_gateway

# Compilar test específico
idf.py build -DTEST_COMPONENT=test_auth_manager

# Flashear (reemplaza PORT con tu puerto)
idf.py -p /dev/cu.usbserial-XXXX flash

# Monitorear salida
idf.py -p /dev/cu.usbserial-XXXX monitor

# Ctrl+] para salir del monitor
```

---

## 📊 Tests Disponibles

| # | Test | Hardware Requerido | Prioridad |
|---|------|-------------------|-----------|
| 1 | **Auth Manager** | Ninguno ✅ | START HERE |
| 2 | **Config Manager** | SD opcional | START HERE |
| 3 | **OTA Manager** | Ninguno ✅ | Alta |
| 4 | **CAN Bus Init** | Ninguno ✅ | Alta |
| 5 | **SD Logger** | SD card 💾 | Alta |
| 6 | **W5500 SPI** | W5500 module 🔌 | Alta |
| 7 | **Ethernet Manager** | W5500 + Cable + Router 🌐 | Alta |
| 8 | **Web Server** | Ethernet working 🌐 | Media |
| 9 | **Digital I/O** | LEDs/wires (opcional) 💡 | Baja |

---

## 🎯 Orden Recomendado

### **Fase 1: Solo ESP32** (empieza aquí)
```bash
./run_tests.sh auth       # 10 tests - ~30 segundos
./run_tests.sh config     # 10 tests - ~1 minuto
./run_tests.sh ota        #  8 tests - ~1 minuto
./run_tests.sh can        #  2 tests - ~10 segundos
```

**Total: 30 tests sin hardware externo** ✅

### **Fase 2: Con SD Card**
```bash
# Insertar SD card (FAT32)
./run_tests.sh sd         # 13 tests - ~2 minutos
```

**Total: +13 tests** 💾

### **Fase 3: Con W5500**
```bash
# Conectar W5500 via SPI
./run_tests.sh test_w5500_spi_init    # 3 tests - ~30 segundos
```

**Total: +3 tests** 🔌

### **Fase 4: Con Red Completa**
```bash
# W5500 + cable ethernet + router
./run_tests.sh eth        # 10 tests - ~30 segundos
./run_tests.sh web        #  8 tests - ~1 minuto
```

**Total: +18 tests** 🌐

---

## 📖 Interpretación de Resultados

### ✅ **Test Exitoso**
```
Running test_auth_init...
✓ Auth manager initialized

10 Tests 0 Failures 0 Ignored
OK
```

### ⚠️ **Test Ignorado** (Normal si falta hardware)
```
Running test_sd_logger_write...
⚠ SD card not detected
IGNORE: SD card not available

9 Tests 0 Failures 1 Ignored
OK
```

### ❌ **Test Fallido** (Requiere fix)
```
Running test_ethernet_dhcp...
FAIL: Could not obtain IP

Expected: TRUE
Actual: FALSE

8 Tests 1 Failure 0 Ignored
FAIL
```

---

## 🔧 Troubleshooting

### No detecta puerto ESP32
```bash
# macOS
ls /dev/cu.*

# Linux  
ls /dev/ttyUSB*

# Si no aparece: instalar drivers CP210x o CH340
```

### Compilación falla
```bash
# Limpiar build
idf.py fullclean

# Re-compilar
idf.py build -DTEST_COMPONENT=test_auth_manager
```

### Test crashea
```bash
# Ver stack trace completo
idf.py -p PORT monitor

# Buscar en logs:
# - "Guru Meditation Error"
# - "Exception occurred"
# - Dirección de crash
```

---

## 📚 Documentación Completa

- **Filosofía de Tests:** `test/device/TEST_PHILOSOPHY.md` ⭐ **LEER PRIMERO**
- **Resumen de Tests:** `test/device/TEST_SUMMARY.md`
- **README Tests:** `test/device/README.md`

---

## 🎉 Quick Win

**Empieza con el test más simple:**

```bash
cd esp32_gateway
./run_tests.sh auth
```

Deberías ver:
```
✅ 10/10 tests passed
No hardware required!
```

**Toma ~30 segundos** y te da confianza que todo funciona 🚀

---

## 💡 Tips

1. **Empieza simple:** Auth → Config → OTA (no requieren hardware)
2. **Lee los logs:** Cada test imprime info útil
3. **Tests ignorados son OK:** Si no tienes SD, test se salta
4. **Un fallo = un problema específico:** Tests aislados facilitan debug
5. **Ejecuta después de cambios:** Valida que no rompiste nada

---

**¿Listo para empezar?** Conecta tu ESP32 y ejecuta `./run_tests.sh` 🚀
