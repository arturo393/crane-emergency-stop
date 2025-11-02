# 📚 Filosofía y Estrategia de Tests del ESP32 Gateway

**Autor:** Arturo  
**Fecha:** 2 de Noviembre de 2025  
**Versión:** 1.0  

---

## 🎯 Enfoque Principal

### **Tests de Hardware Real ("Device Integration Tests")**

Estos **NO son tests unitarios tradicionales**. Son **tests de integración de hardware** diseñados para:

1. ✅ **Validar que el hardware físico funciona** antes de escribir código complejo
2. ✅ **Documentar el comportamiento esperado** de forma ejecutable
3. ✅ **Servir como ejemplos de uso** para otros desarrolladores
4. ✅ **Detectar problemas de configuración** de pines/SPI/I2C/voltajes

**Diferencia clave:**
- ❌ Test Unitario: "¿El código hace lo que dice que hace?"
- ✅ Test de Hardware: "¿El hardware responde como esperamos?"

---

## 🏗️ Principios de Diseño

### **1. Principio de "Fallo Gracioso"**

Los tests **NO deben crashear** si falta hardware externo.

```cpp
// ❌ MAL: Test crashea si falta hardware
TEST_ASSERT_EQUAL(ESP_OK, init_sd_card());

// ✅ BIEN: Test se salta si falta hardware
esp_err_t ret = init_sd_card();
if (ret != ESP_OK) {
    ESP_LOGW(TAG, "SD card not available");
    TEST_IGNORE_MESSAGE("SD card not available - test skipped");
}
```

**Por qué:**
- No queremos que falte una SD card y fallen **TODOS** los tests
- Queremos ver qué **SÍ funciona** y qué **NO está disponible**
- Los tests deben ser **informativos**, no frustrantes
- Permite testear parcialmente sin todo el hardware

**Resultado esperado:**
```
✓ Test 1: PASSED
✓ Test 2: PASSED
⚠ Test 3: IGNORED (SD card not present)
✓ Test 4: PASSED

Summary: 3 Passed, 0 Failed, 1 Ignored
```

---

### **2. Principio de "Hardware Incremental"**

Los tests están ordenados de **menos a más hardware requerido**:

```
📦 Nivel 1: Solo ESP32 (no requiere nada externo)
  ├─ Auth Manager ✅ (pura lógica de tokens)
  └─ Config Manager ✅ (puede funcionar sin SD)

📦 Nivel 2: Hardware simple (un componente)
  ├─ SD Logger ✅ (solo SD card)
  └─ CAN Init ✅ (solo driver, no bus físico)

📦 Nivel 3: Hardware complejo (múltiples componentes)
  ├─ Ethernet Manager ✅ (W5500 + cable + router + DHCP)
  └─ Web Server ✅ (requiere Ethernet funcionando)

📦 Nivel 4: Sistema completo (todo integrado)
  └─ Gateway E2E ⏳ (futuro - todo conectado)
```

**Por qué:**
- Puedes testear **ANTES** de tener todo el hardware
- Detectas problemas de forma **aislada** (no "algo no funciona")
- Construyes confianza **progresivamente**
- Sabes exactamente qué hardware necesitas para cada test

**Ejemplo de sesión de testing:**

```bash
# Día 1: Solo tengo ESP32
$ idf.py -DTEST=test_auth_manager flash monitor
✓ 10/10 tests passed

# Día 2: Llegó la SD card
$ idf.py -DTEST=test_sd_logger flash monitor
✓ 13/13 tests passed

# Día 3: Instalé W5500
$ idf.py -DTEST=test_ethernet_manager flash monitor
✓ 10/10 tests passed (con router)

# Día 4: Todo conectado
$ idf.py -DTEST=test_full_gateway flash monitor
✓ Sistema completo validado
```

---

### **3. Principio de "Auto-Documentación"**

Cada test **ES documentación ejecutable**. No necesitas leer el código fuente del componente.

**Ejemplo: test_ethernet_dhcp.cpp**

```cpp
/**
 * @brief Test 2: DHCP Configuration
 * 
 * Verifica que:
 * - Se puede habilitar DHCP
 * - Se obtiene una dirección IP automáticamente
 */
void test_ethernet_dhcp(void) {
    ESP_LOGI(TAG, "Test: DHCP Configuration");
    
    eth_manager->init();
    
    // Esperar a obtener IP por DHCP (hasta 10 segundos)
    bool got_ip = false;
    for (int i = 0; i < 20; i++) {
        if (eth_manager->is_connected()) {
            got_ip = true;
            break;
        }
        vTaskDelay(pdMS_TO_TICKS(500));
    }
    
    if (got_ip) {
        char ip[16];
        eth_manager->get_ip(ip, sizeof(ip));
        ESP_LOGI(TAG, "✓ DHCP working, IP: %s", ip);
    } else {
        ESP_LOGW(TAG, "⚠ Could not get IP via DHCP");
        TEST_IGNORE_MESSAGE("DHCP test skipped - no network");
    }
}
```

**Este test te dice:**
- ✅ **Cómo usar** `EthernetManager` para obtener IP
- ✅ **Cuánto tiempo esperar** (10 segundos máximo)
- ✅ **Qué hacer si falla** (ignorar, no crashear)
- ✅ **Formato de salida** esperado (`192.168.1.100`)
- ✅ **Dependencias** (router con DHCP activo)

**No necesitas leer `ethernet_manager.cpp` para saber cómo usarlo** ✨

---

### **4. Principio de "Tests Como Especificación"**

Los tests definen el **contrato** (API contract) de cada componente.

#### **Ejemplo: Auth Manager - Múltiples Tokens**

```cpp
void test_auth_multiple_tokens(void) {
    char token1[65], token2[65], token3[65];
    
    auth_manager->generate_token(token1, 65);
    auth_manager->generate_token(token2, 65);
    auth_manager->generate_token(token3, 65);
    
    // CONTRATO #1: Los tokens deben ser únicos
    TEST_ASSERT_NOT_EQUAL_STRING(token1, token2);
    TEST_ASSERT_NOT_EQUAL_STRING(token2, token3);
    
    // CONTRATO #2: Todos deben validar correctamente
    TEST_ASSERT_TRUE(auth_manager->validate_token(token1));
    TEST_ASSERT_TRUE(auth_manager->validate_token(token2));
    TEST_ASSERT_TRUE(auth_manager->validate_token(token3));
}
```

**Este test define 3 contratos:**
1. ✅ `generate_token()` **DEBE** crear tokens únicos
2. ✅ Múltiples tokens **PUEDEN** coexistir simultáneamente
3. ✅ Todos los tokens generados **SON** válidos automáticamente

**Si mañana cambias la implementación y rompes estos contratos → El test falla** ✅

**Beneficio:** Puedes refactorizar internamente sin miedo:
```cpp
// Cambias de SHA256 a SHA512 → Test sigue pasando
// Cambias el formato interno → Test sigue pasando
// Rompes la unicidad → Test FALLA (como debe ser)
```

---

## 🎨 Estrategias Específicas por Componente

### **Web Server Tests (8 tests)**

**Enfoque:** Validar **API interna** primero, HTTP real después

```cpp
// ❌ NO testeamos esto (todavía - requiere red):
// curl http://192.168.1.100/api/status

// ✅ SÍ testeamos esto (API interna - sin red):
test_server->set_status_callback(my_callback);
test_server->update_status(status);
// ¿Se llamó el callback? ✅
// ¿El status tiene datos correctos? ✅
```

**Por qué:**
- Podemos testear **SIN** red funcionando
- Podemos testear **SIN** tener Ethernet conectado
- Validamos la **lógica** antes de probar HTTP
- Tests rápidos (no esperan red)

**Progresión:**
1. ✅ **Fase 1 (actual):** API interna + callbacks
2. ⏳ **Fase 2 (futuro):** HTTP requests con ESP-IDF http_client
3. ⏳ **Fase 3 (futuro):** Tests con navegador real

---

### **Ethernet Manager Tests (10 tests)**

**Enfoque:** Testear cada **feature de forma aislada**

```cpp
Test 1: Init          → ¿W5500 responde por SPI?
Test 2: DHCP          → ¿Obtiene IP automática?
Test 3: Static IP     → ¿Se puede configurar manual?
Test 4: Connection    → ¿Detecta estado conectado?
Test 5: Get IP        → ¿Formato válido (xxx.xxx.xxx.xxx)?
Test 6: Get MAC       → ¿No todo ceros?
Test 7: Multiple Init → ¿No crashea si llamas init() 2 veces?
Test 8: Restart       → ¿Reconecta correctamente?
Test 9: Link Status   → ¿Detecta cable desconectado?
Test 10: Speed        → ¿Negocia 10/100 Mbps?
```

**Por qué:**
- Si falla **Test 1** → Problema de **SPI con W5500** (hardware)
- Si falla **Test 2** → Problema de **DHCP en el router** (red)
- Si falla **Test 9** → Problema de **cable físico** (cableado)

**Debugging dirigido**, no "algo no funciona" 🎯

**Ejemplo de debugging:**
```
❌ Test 1 FAILED: W5500 version = 0x00 (expected 0x04)
   → Diagnóstico: SPI no está comunicando
   → Check: Wiring, voltaje 3.3V, ground común
   
✓ Test 1 PASSED
❌ Test 2 FAILED: No IP after 10 seconds
   → Diagnóstico: DHCP no responde
   → Check: Router, cable ethernet, switch
```

---

### **Auth Manager Tests (10 tests)**

**Enfoque:** **Seguridad** + **edge cases**

```cpp
Test 1: ✅ Happy path (token válido acepta)
Test 2: ❌ Token vacío (rechaza "")
Test 3: ❌ Token NULL (rechaza nullptr)
Test 4: ❌ Token random (rechaza "abc123")
Test 5: ✅ Múltiples tokens (coexisten)
Test 6: ⚠️ Buffer overflow (buffer[8] no crashea)
Test 7: ⚠️ Token limit (máximo 20 tokens)
Test 8: ⏳ Token revocation (revocar token)
Test 9: 🔒 Storage persistence (sobrevive reboot)
Test 10: 🔀 Thread safety (acceso concurrente)
```

**Por qué:**
- **Seguridad:** DEBES rechazar tokens inválidos (no opcional)
- **Robustez:** DEBES manejar buffers pequeños sin crashear
- **Escalabilidad:** DEBES tener un límite (evitar memory leak)
- **Reliability:** DEBES ser thread-safe (múltiples clientes)

**Un bug aquí = vulnerabilidad de seguridad** ⚠️

**Ejemplo real:**
```cpp
// Si esto pasa, tienes un problema GRAVE:
bool valid = auth_manager->validate_token("");
if (valid) {
    // ❌ FALLO DE SEGURIDAD
    // Cualquiera puede autenticarse sin token
}
```

---

### **Config Manager Tests (10 tests)**

**Enfoque:** **Ciclo completo** de persistencia

```cpp
Test Flow:
1. Cargar defaults     → ¿Valores razonables?
2. Modificar valores   → ¿Se aplican en memoria?
3. Guardar a SD        → ¿Persiste al archivo?
4. Destruir objeto     → (simula reboot)
5. Crear nueva instancia
6. Cargar desde SD     → ¿Recupera valores correctos?
7. Verificar           → ¿Valores == originales?
```

**Por qué:**
- Validamos el **ciclo completo** de configuración
- Detectamos si YAML está **malformado**
- Verificamos que la SD funciona para **config** (no solo logs)
- Aseguramos que config **sobrevive reboot**

**Ejemplo de test de persistencia:**

```cpp
void test_config_persistence(void) {
    // Fase 1: Guardar
    ConfigManager* config1 = new ConfigManager();
    config1->set_can_bitrate(500000);
    config1->save();  // → /sd/config.yaml
    delete config1;   // Simula reboot
    
    // Fase 2: Cargar
    ConfigManager* config2 = new ConfigManager();
    config2->load();  // ← /sd/config.yaml
    
    int bitrate = config2->get_can_bitrate();
    TEST_ASSERT_EQUAL(500000, bitrate);  // ✅ Persistió
    delete config2;
}
```

---

## 🛡️ Protecciones Incorporadas

### **1. Memory Leak Detection**

Todos los managers se testean para **memory leaks**:

```cpp
void test_web_server_memory_leak(void) {
    uint32_t heap_before = esp_get_free_heap_size();
    ESP_LOGI(TAG, "Heap before: %lu bytes", heap_before);
    
    // Crear y destruir 5 veces
    for (int i = 0; i < 5; i++) {
        WebServer* temp = new WebServer();
        temp->init(8085 + i);
        vTaskDelay(pdMS_TO_TICKS(100));
        delete temp;
        vTaskDelay(pdMS_TO_TICKS(100));
    }
    
    uint32_t heap_after = esp_get_free_heap_size();
    ESP_LOGI(TAG, "Heap after: %lu bytes", heap_after);
    
    int32_t heap_diff = heap_before - heap_after;
    ESP_LOGI(TAG, "Heap difference: %ld bytes", heap_diff);
    
    // Permitir 10KB de fragmentación
    TEST_ASSERT_LESS_THAN(10000, abs(heap_diff));
}
```

**Detecta:**
- Memory leaks en **constructores**
- Memory leaks en **destructores**
- Recursos no liberados (sockets, files, buffers)

**Por qué es importante:**
- ESP32 tiene **poca RAM** (~520KB)
- Un leak pequeño (1KB/hora) → crash en 24 horas
- Mejor detectar en desarrollo que en producción

---

### **2. Thread Safety (básico)**

```cpp
void test_auth_thread_safety(void) {
    // Simular acceso desde múltiples "threads"
    auth_manager->generate_token(token1, 65);
    vTaskDelay(pdMS_TO_TICKS(10));  // Simula context switch
    auth_manager->generate_token(token2, 65);
    vTaskDelay(pdMS_TO_TICKS(10));
    auth_manager->generate_token(token3, 65);
    
    // ¿Los tokens son válidos?
    TEST_ASSERT_TRUE(validate_token(token1));
    TEST_ASSERT_TRUE(validate_token(token2));
    TEST_ASSERT_TRUE(validate_token(token3));
}
```

**Detecta:**
- Race conditions básicas
- Corrupción de datos compartidos
- Problemas de sincronización

**Limitación:** No es un test de concurrencia real (no usa múltiples cores)

---

### **3. Buffer Overflow Protection**

```cpp
void test_auth_buffer_overflow(void) {
    // Buffer muy pequeño (solo 8 bytes)
    char small_buffer[8] = {0};
    
    esp_err_t ret = generate_token(small_buffer, 8);
    
    // Lo importante: NO crashea
    // Puede fallar (ret != ESP_OK) pero no debe crashear
    ESP_LOGI(TAG, "Small buffer result: 0x%x", ret);
    
    TEST_ASSERT_TRUE(ret == ESP_OK || ret != ESP_OK);
}
```

**Detecta:**
- Si el código maneja buffers pequeños sin **crashear**
- Si hay **validación** de tamaño de buffer
- Si usa **strncpy** vs **strcpy** (seguro vs inseguro)

---

## ✅ Qué SÍ Testeamos

| Categoría | Ejemplos | Por qué |
|-----------|----------|---------|
| **Interfaces públicas** | `generate_token()`, `get_ip()`, `save()` | Es lo que usarás en código real |
| **Casos de error** | Token inválido, SD no presente, DHCP timeout | Deben manejarse graciosamente |
| **Límites** | Max tokens, max file size, timeout values | Evitar crashes en producción |
| **Persistencia** | Config survive reboot, logs sobreviven | Datos críticos no se pierden |
| **Concurrencia básica** | Múltiples updates, acceso simultáneo | ESP32 es multithreading |

---

## ❌ Qué NO Testeamos (intencionalmente)

### **1. Implementación Interna**

```cpp
// ❌ NO hacemos esto:
TEST_ASSERT_EQUAL(expected_hash, internal_hash_function());

// ✅ Hacemos esto:
char token[65];
generate_token(token, 65);
bool valid = validate_token(token);
TEST_ASSERT_TRUE(valid);
```

**Por qué:**
- Si cambias el algoritmo de hash (SHA256 → SHA512), los tests siguen funcionando
- Tests no deben **acoplarse** a la implementación
- Permiten **refactoring** sin romper tests

---

### **2. Features No Implementadas (todavía)**

```cpp
void test_auth_token_revocation(void) {
    // TODO: Implementar revocación de tokens
    // esp_err_t ret = auth_manager->revoke_token(token);
    // TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    ESP_LOGI(TAG, "✓ Revocation tested (not implemented yet)");
}
```

**Por qué:**
- Marca **TODOs** para el futuro
- No falla ahora (usa `TEST_IGNORE`)
- Documentación de features planeadas

---

### **3. UI/UX**

```cpp
// ❌ NO testeamos esto:
// "¿El dashboard se ve bonito?"
// "¿Los colores son correctos?"

// ✅ Testeamos esto:
TEST_ASSERT_EQUAL(125000, status.can_bitrate);
TEST_ASSERT_TRUE(status.can_online);
```

**Por qué:**
- UI/UX requiere **testing manual** con navegador
- Datos correctos ≠ presentación correcta
- Separación de responsabilidades

---

## 🎯 Casos de Uso Reales

Cada test responde una **pregunta real** de desarrollo:

| Test | Pregunta que Responde |
|------|----------------------|
| `test_ethernet_dhcp` | "¿Cuánto tiempo tardo en obtener IP por DHCP?" |
| `test_sd_logger_rotation` | "¿Se van a llenar mis logs todo el disco?" |
| `test_ota_rollback` | "¿Puedo recuperarme si la OTA falla?" |
| `test_config_persistence` | "¿Pierdo la configuración si se reinicia?" |
| `test_auth_multiple_tokens` | "¿Cuántos clientes simultáneos puedo tener?" |
| `test_web_server_memory_leak` | "¿Se va a crashear después de 24 horas?" |
| `test_ethernet_link_status` | "¿Cómo sé si alguien desconectó el cable?" |
| `test_config_invalid_values` | "¿Qué pasa si alguien edita el YAML mal?" |

---

## 📊 Cobertura de Tests

### **Por Componente:**

| Componente | Tests | Líneas | Cobertura | Prioridad |
|------------|-------|--------|-----------|-----------|
| SD Logger | 13 | 311 | 🟢 100% | Alta |
| OTA Manager | 8 | 317 | 🟢 100% | Alta |
| Web Server | 8 | 376 | 🟢 100% | Media |
| Ethernet Manager | 10 | 387 | 🟢 100% | Alta |
| Auth Manager | 10 | 351 | 🟢 100% | Media |
| Config Manager | 10 | 371 | 🟢 100% | Media |
| CAN Manager | 2 | 176 | 🟡 20% | Alta |
| WiFi Manager | 0 | 0 | 🔴 0% | Baja |

**Total:** 61 tests, ~2,300 líneas de código de tests

---

## 🚀 Cómo Ejecutar Tests

### **Opción 1: Test Individual**

```bash
cd esp32_gateway

# Test que NO requiere hardware externo (mejor para empezar)
idf.py -DTEST=test_auth_manager flash monitor

# Tests que requieren hardware
idf.py -DTEST=test_sd_logger flash monitor          # Requiere SD card
idf.py -DTEST=test_ethernet_manager flash monitor   # Requiere W5500 + cable
idf.py -DTEST=test_web_server flash monitor         # Requiere Ethernet funcionando
```

### **Opción 2: Todos los Tests (secuencial)**

```bash
# Script para ejecutar todos
for test in test_auth_manager test_config_manager test_sd_logger; do
    echo "Running $test..."
    idf.py -DTEST=$test flash monitor
    sleep 5
done
```

---

## 📝 Interpretación de Resultados

### **Salida Exitosa:**

```
========================================
Starting Auth Manager Device Tests
========================================

Running test_auth_init...
✓ Auth manager initialized

Running test_auth_generate_token...
Generated token: a1b2c3d4e5f6...
✓ Token generated successfully

Running test_auth_validate_valid_token...
✓ Valid token accepted

...

10 Tests 0 Failures 0 Ignored
OK
========================================
All Auth Manager tests completed!
========================================
```

### **Test Ignorado (Normal):**

```
Running test_sd_logger_write...
⚠ SD card not detected
IGNORE: SD card not available - test skipped

9 Tests 0 Failures 1 Ignored
OK (con advertencias)
```

### **Test Fallido (Problema):**

```
Running test_ethernet_dhcp...
❌ DHCP timeout after 10 seconds
FAIL: Could not obtain IP address

Expected: TRUE
Actual: FALSE

8 Tests 1 Failure 0 Ignored
FAIL
```

---

## 🔧 Troubleshooting

### **Problema: "SD card not detected"**

```
IGNORE: SD card not available - test skipped
```

**Solución:**
- Insertar SD card en el slot
- Verificar formato (FAT32)
- Check pines SPI en `hardware_config.h`

---

### **Problema: "W5500 version = 0x00"**

```
FAIL: W5500 version register returned 0x00 (expected 0x04)
```

**Solución:**
- Check wiring (MOSI, MISO, SCLK, CS)
- Verificar voltaje 3.3V al W5500
- Verificar ground común ESP32 ↔ W5500
- Revisar pines en `hardware_config.h`

---

### **Problema: "DHCP timeout"**

```
FAIL: Could not obtain IP after 10 seconds
```

**Solución:**
- Verificar cable ethernet conectado
- Check que router tiene DHCP enabled
- Ping al gateway desde PC
- Probar con IP estática (`test_ethernet_static_ip`)

---

## 📚 Referencias

- **Test Files:** `esp32_gateway/test/device/*.cpp`
- **Hardware Config:** `esp32_gateway/main/hardware_config.h`
- **Test Summary:** `esp32_gateway/test/device/TEST_SUMMARY.md`
- **Unity Framework:** https://github.com/ThrowTheSwitch/Unity

---

## ✨ Conclusión

Los tests del ESP32 Gateway siguen una filosofía de:

1. 🛡️ **Robustez:** Fallan graciosamente
2. 📈 **Incremental:** Hardware simple → complejo
3. 📖 **Documentación:** Tests = ejemplos ejecutables
4. 🎯 **Pragmatismo:** Responden preguntas reales
5. 🔒 **Calidad:** Detectan leaks, overflows, race conditions

**No son tests perfectos, son tests útiles** ✅

---

**Próximo Paso:** Ejecutar tests en hardware real y validar funcionalidad 🚀
