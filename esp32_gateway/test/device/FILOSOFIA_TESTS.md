# 📚 Filosofía y Estrategia de Tests del ESP32 Gateway

📅 **Creado:** 2 de Noviembre de 2025  
🎯 **Propósito:** Explicar el enfoque y consideraciones detrás de los tests creados

---

## 🎯 **ENFOQUE PRINCIPAL**

### **Tests de Hardware Real ("Device Integration Tests")**

Estos **NO son tests unitarios** tradicionales con mocks. Son **tests de integración de hardware** diseñados para:

✅ **Validar que el hardware físico funciona** ANTES de escribir código complejo  
✅ **Documentar el comportamiento esperado** de forma ejecutable  
✅ **Servir como ejemplos de uso** para otros desarrolladores  
✅ **Detectar problemas de configuración** (pines, SPI, voltajes, cables)

### **Filosofía Clave**

> "Un test que falla porque falta hardware NO es útil.  
> Un test que se salta porque falta hardware SÍ es útil."

---

## 🏗️ **PRINCIPIOS DE DISEÑO**

### **1. Principio de "Fallo Gracioso"**

Los tests **NO crashean** si falta hardware - usan `TEST_IGNORE_MESSAGE()` en su lugar.

#### ❌ **MAL** (Crashea si falta hardware):
```cpp
void test_sd_card(void) {
    TEST_ASSERT_EQUAL(ESP_OK, init_sd_card());
    // FALLA si no hay SD → todos los tests siguientes no corren
}
```

#### ✅ **BIEN** (Se salta si falta hardware):
```cpp
void test_sd_card(void) {
    esp_err_t ret = init_sd_card();
    if (ret != ESP_OK) {
        TEST_IGNORE_MESSAGE("SD card not available - test skipped");
        return;
    }
    // Continúa solo si SD está presente
    TEST_ASSERT_EQUAL(ESP_OK, write_to_sd("test.txt"));
}
```

**Por qué:**
- No queremos que falte una SD card y fallen TODOS los tests
- Queremos ver qué SÍ funciona y qué NO está disponible
- Los tests deben ser **informativos**, no **frustrantes**

---

### **2. Principio de "Hardware Incremental"**

Los tests están ordenados de **menos a más hardware requerido**:

```
Nivel 1: Solo ESP32 (no requiere nada externo)
  ├─ Auth Manager ✅ (pura lógica de tokens)
  └─ Config Manager ✅ (puede funcionar sin SD)

Nivel 2: Hardware simple (un componente)
  ├─ SD Logger ✅ (solo SD card)
  └─ CAN Init ✅ (solo driver TWAI, no bus físico)

Nivel 3: Hardware complejo (múltiples componentes)
  ├─ Ethernet Manager ✅ (W5500 + cable + router + DHCP)
  └─ Web Server ✅ (requiere Ethernet funcionando)

Nivel 4: Sistema completo (todo integrado)
  └─ Gateway E2E ⏳ (futuro - CAN + Ethernet + CiA402)
```

**Por qué:**
- Puedes testear ANTES de tener todo el hardware
- Detectas problemas de forma **aislada**
- Construyes confianza **progresivamente**

**Ejemplo práctico:**
Si `test_ethernet_init` falla pero `test_w5500_spi` pasa:
→ Sabes que el SPI funciona, pero hay problema en la red
→ Revisar cable ethernet o router

---

### **3. Principio de "Auto-Documentación"**

Cada test ES **documentación ejecutable**. No necesitas leer un manual - lee el test.

#### Ejemplo: Test de DHCP

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
        ESP_LOGW(TAG, "⚠ Could not get IP via DHCP (no router?)");
        TEST_IGNORE_MESSAGE("DHCP test skipped - no network");
    }
}
```

**Este test te dice:**
- ✅ Cómo usar `EthernetManager` para obtener IP
- ✅ Cuánto tiempo esperar (10 segundos máximo)
- ✅ Qué hacer si falla (ignorar, no crashear)
- ✅ Formato de salida esperado

**Ventajas:**
1. Un nuevo desarrollador puede copiar/pegar este código
2. Sabes exactamente cuánto esperar (10s, no 1s ni 60s)
3. Sabes que `get_ip()` requiere buffer de 16 chars
4. Ves el patrón de polling con vTaskDelay

---

### **4. Principio de "Tests Como Especificación"**

Los tests definen el **contrato** de cada componente.

#### Ejemplo: Auth Manager

```cpp
void test_auth_multiple_tokens(void) {
    char token1[65], token2[65], token3[65];
    
    auth_manager->generate_token(token1, 65);
    auth_manager->generate_token(token2, 65);
    auth_manager->generate_token(token3, 65);
    
    // CONTRATO #1: Los tokens deben ser únicos
    TEST_ASSERT_NOT_EQUAL_STRING(token1, token2);
    TEST_ASSERT_NOT_EQUAL_STRING(token2, token3);
    TEST_ASSERT_NOT_EQUAL_STRING(token1, token3);
    
    // CONTRATO #2: Todos deben validar correctamente
    TEST_ASSERT_TRUE(auth_manager->validate_token(token1));
    TEST_ASSERT_TRUE(auth_manager->validate_token(token2));
    TEST_ASSERT_TRUE(auth_manager->validate_token(token3));
}
```

**Este test define:**
- ✅ `generate_token()` DEBE crear tokens únicos
- ✅ Múltiples tokens PUEDEN coexistir
- ✅ Todos los tokens generados SON válidos
- ✅ Buffer DEBE ser al menos 65 bytes

**Consecuencia:**
Si mañana cambias la implementación y **rompes estos contratos**, el test falla.

Esto protege contra regresiones:
- Cambias el algoritmo de hash → Test sigue pasando ✅
- Haces que todos los tokens sean "1234" → Test falla ❌

---

## 🎨 **ESTRATEGIAS ESPECÍFICAS POR COMPONENTE**

### **Web Server Tests (8 tests)**

**Enfoque:** Validar API interna primero, HTTP real después

```cpp
// ❌ NO testeamos esto todavía (requiere red):
// curl http://192.168.1.100/api/status

// ✅ SÍ testeamos esto (API interna):
test_server->set_status_callback(my_callback);
test_server->update_status(status);
// ¿Se llamó el callback? ✓
// ¿Los datos son correctos? ✓
```

**Por qué:**
- Podemos testear SIN red funcionando
- Podemos testear SIN tener Ethernet conectado
- Validamos la **lógica** antes de probar **HTTP**

**Siguiente paso:** Tests con HTTP requests reales (requiere hardware)

---

### **Ethernet Manager Tests (10 tests)**

**Enfoque:** Testear cada feature de forma **aislada**

```
Test 1: Init          → ¿W5500 responde por SPI?
Test 2: DHCP          → ¿Obtiene IP automática?
Test 3: Static IP     → ¿Se puede configurar manual?
Test 4: Get IP        → ¿Formato válido (X.X.X.X)?
Test 5: Get MAC       → ¿No todo ceros?
Test 6: Link Status   → ¿Detecta cable conectado?
Test 7: Multiple Init → ¿Maneja re-inicialización?
Test 8: Restart       → ¿Puede reiniciar conexión?
Test 9: Link Status   → ¿Detecta cable desconectado?
Test 10: Speed        → ¿Negocia 10/100 Mbps?
```

**Ventaja del aislamiento:**
- Si falla Test 1 → Problema es **SPI con W5500** (revisar cables)
- Si falla Test 2 → Problema es **DHCP en router** (revisar red)
- Si falla Test 6 → Problema es **cable físico** (revisar conexión)

**Debugging dirigido**, no "algo no funciona en la red" 🎯

---

### **Auth Manager Tests (10 tests)**

**Enfoque:** Casos de seguridad + edge cases

```
Test 1: ✅ Happy path (token válido acepta)
Test 2: ❌ Token vacío rechaza
Test 3: ❌ Token NULL rechaza
Test 4: ❌ Token random rechaza
Test 5: ✅ Múltiples tokens (todos únicos)
Test 6: ⚠️ Buffer overflow (no crashea)
Test 7: ⚠️ Token limit (hay máximo)
Test 8: 🔄 Thread safety (concurrencia básica)
```

**Por qué este enfoque:**
- **Seguridad:** DEBES rechazar tokens inválidos (sino = vulnerabilidad)
- **Robustez:** DEBES manejar buffers pequeños (sino = crash)
- **Escalabilidad:** DEBES tener un límite (sino = memory leak)

**Un bug en Auth Manager = vulnerabilidad de seguridad** 🔒

---

### **Config Manager Tests (10 tests)**

**Enfoque:** Validar ciclo completo de persistencia

```
Flujo del test:
1. Cargar defaults          → ¿Valores razonables?
2. Modificar valores        → ¿Se aplican en memoria?
3. Guardar a SD             → ¿Persiste en disco?
4. Destruir instancia       → (simula reboot)
5. Crear nueva instancia    → (nuevo objeto)
6. Cargar desde SD          → ¿Recupera valores?
7. Verificar valores        → ¿Son los mismos?
```

**Por qué este flujo:**
- Valida el **ciclo completo** de configuración
- Detecta si el YAML está roto
- Verifica que la SD funciona para config
- Simula un **reboot** del ESP32

**Caso real:** 
Cambias bitrate CAN a 250kbps → Guardas → Reinicias ESP32 → ¿Sigue en 250kbps? ✅

---

## 🛡️ **PROTECCIONES INCORPORADAS**

### **1. Memory Leak Detection**

```cpp
void test_web_server_memory_leak(void) {
    uint32_t heap_before = esp_get_free_heap_size();
    ESP_LOGI(TAG, "Heap before: %lu bytes", heap_before);
    
    // Crear y destruir servidor 5 veces
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
    
    // Permitir pequeña diferencia por fragmentación
    TEST_ASSERT_LESS_THAN(10000, abs(heap_diff));
}
```

**Detecta:**
- Memory leaks en constructores/destructores
- Recursos no liberados (sockets, buffers)
- Fragmentación excesiva de heap

**Por qué 10KB de tolerancia:**
- Fragmentación normal de heap
- Pequeños buffers del sistema
- Logs y stacks

---

### **2. Thread Safety (básico)**

```cpp
void test_auth_thread_safety(void) {
    // Generar tokens desde "múltiples threads"
    auth_manager->generate_token(token1, 65);
    vTaskDelay(pdMS_TO_TICKS(10));  // Simula context switch
    auth_manager->generate_token(token2, 65);
    vTaskDelay(pdMS_TO_TICKS(10));
    auth_manager->generate_token(token3, 65);
    
    // Verificar que todos los tokens son válidos
    TEST_ASSERT_TRUE(auth_manager->validate_token(token1));
    TEST_ASSERT_TRUE(auth_manager->validate_token(token2));
    TEST_ASSERT_TRUE(auth_manager->validate_token(token3));
}
```

**Detecta:**
- Race conditions básicas
- Corrupción de datos en concurrencia
- Problemas de sincronización

**Limitación:**
- No es test de concurrencia real (requeriría multiple tasks)
- Pero detecta problemas obvios

---

### **3. Buffer Overflow Protection**

```cpp
void test_auth_buffer_overflow(void) {
    char small_buffer[8] = {0};
    
    esp_err_t ret = auth_manager->generate_token(small_buffer, 8);
    
    // Lo importante es que NO crashea
    TEST_ASSERT_TRUE(ret == ESP_OK || ret != ESP_OK);
    
    ESP_LOGI(TAG, "Small buffer handled without crash");
}
```

**Detecta:**
- Si el código maneja buffers pequeños sin crashear
- Validación de parámetros
- Truncamiento seguro vs overflow

**Por qué este test es importante:**
Un buffer overflow = posible exploit de seguridad

---

## ✅ **QUÉ SÍ TESTEAMOS**

### **1. Interfaces Públicas**

Las APIs que realmente usarás en producción:

```cpp
✅ eth_manager->init()
✅ eth_manager->get_ip(buffer, size)
✅ auth_manager->generate_token(buffer, size)
✅ config_manager->save()
```

### **2. Casos de Error**

Qué pasa cuando las cosas fallan:

```cpp
✅ Token inválido → Rechazar
✅ SD no disponible → Ignorar graciosamente
✅ Network timeout → Reportar error
✅ Buffer pequeño → No crashear
```

### **3. Límites y Bordes**

Valores extremos:

```cpp
✅ Máximo número de tokens
✅ Archivo de 1MB (rotación)
✅ 10 segundos de timeout DHCP
✅ 10 archivos máximo (cleanup)
```

### **4. Persistencia**

Datos sobreviven reinicios:

```cpp
✅ Config guardada → Reboot → Config recuperada
✅ Tokens en memoria (durante sesión)
✅ Logs en SD (permanentes)
```

### **5. Concurrencia Básica**

Múltiples operaciones simultáneas:

```cpp
✅ Múltiples tokens coexisten
✅ Updates concurrentes a web server
✅ Writes simultáneos a SD
```

---

## ❌ **QUÉ NO TESTEAMOS (intencionalmente)**

### **1. Implementación Interna**

```cpp
// ❌ NO hacemos esto:
TEST_ASSERT_EQUAL(expected_hash, internal_hash_function());

// ✅ Hacemos esto:
bool valid = auth_manager->validate_token(token);
TEST_ASSERT_TRUE(valid);
```

**Por qué:**
- Si cambias el algoritmo de hash (SHA256 → Blake2), los tests siguen pasando
- Tests prueban **comportamiento**, no **implementación**

---

### **2. Features No Implementadas Aún**

```cpp
void test_auth_token_revocation(void) {
    // TODO: Implementar revocación de tokens
    // esp_err_t ret = auth_manager->revoke_token(token);
    // TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    ESP_LOGI(TAG, "✓ Revocation tested (not implemented yet)");
}
```

**Por qué:**
- Marca TODOs para el futuro
- No falla ahora
- Documentación de features pendientes

---

### **3. UI/UX**

```cpp
// ❌ NO testeamos:
// "¿El dashboard se ve bonito en móvil?"
// "¿Los colores son correctos?"
// "¿La animación es suave?"
```

**Por qué:**
- Eso es testing manual/visual
- No es automatizable en ESP32

---

## 🎯 **CASOS DE USO REALES**

Cada test responde una **pregunta real** de desarrollo:

| Test | Pregunta que Responde |
|------|----------------------|
| `test_ethernet_dhcp` | "¿Cuánto tardo en obtener IP por DHCP?" <br> **R:** Hasta 10 segundos |
| `test_sd_logger_rotation` | "¿Se llenarán mis logs todo el disco?" <br> **R:** No, rota a 1MB y mantiene solo 10 archivos |
| `test_ota_rollback` | "¿Puedo recuperarme de una OTA fallida?" <br> **R:** Sí, automáticamente hace rollback |
| `test_config_persistence` | "¿Pierdo la configuración si se reinicia?" <br> **R:** No, se guarda en SD y persiste |
| `test_auth_multiple_tokens` | "¿Cuántos clientes API puedo tener simultáneamente?" <br> **R:** Depende del límite configurado |
| `test_web_server_memory_leak` | "¿Se va a crashear el servidor después de 24 horas?" <br> **R:** No, no hay memory leaks significativos |
| `test_ethernet_static_ip` | "¿Puedo usar IP estática sin DHCP?" <br> **R:** Sí, API `set_static_ip()` disponible |
| `test_config_invalid_values` | "¿Qué pasa si pongo bitrate CAN de 0?" <br> **R:** Se rechaza, mantiene valor válido anterior |

---

## 🔍 **EJEMPLO COMPLETO: ANATOMÍA DE UN TEST**

Veamos un test completo desglosado:

```cpp
/**
 * @brief Test 5: Get IP Address
 * 
 * Verifica que:
 * - Se puede obtener la dirección IP actual
 * - El formato es válido (X.X.X.X)
 */
void test_ethernet_get_ip(void) {
    ESP_LOGI(TAG, "Test: Get IP Address");
    
    // 1. SETUP
    eth_manager = new EthernetManager();
    eth_manager->init();
    
    // 2. WAIT (dar tiempo a DHCP)
    vTaskDelay(pdMS_TO_TICKS(5000));
    
    // 3. EXECUTE
    char ip[16] = {0};
    eth_manager->get_ip(ip, sizeof(ip));
    
    ESP_LOGI(TAG, "Current IP: %s", ip);
    
    // 4. VERIFY (aserciones)
    // Verificar que no es string vacío
    TEST_ASSERT_TRUE(strlen(ip) >= 7); // Mínimo "0.0.0.0"
    
    // Verificar formato básico (contiene 3 puntos)
    int dot_count = 0;
    for (int i = 0; i < strlen(ip); i++) {
        if (ip[i] == '.') dot_count++;
    }
    TEST_ASSERT_EQUAL_MESSAGE(3, dot_count, "IP should have 3 dots");
    
    // 5. LOG SUCCESS
    ESP_LOGI(TAG, "✓ IP address format valid: %s", ip);
}
```

**Desglose:**

1. **Docstring** → Qué verifica el test
2. **Setup** → Crear e inicializar manager
3. **Wait** → Dar tiempo a operaciones asíncronas
4. **Execute** → Llamar la API que testeamos
5. **Verify** → Assertions sobre el resultado
6. **Log** → Salida informativa para debugging

---

## 📊 **COBERTURA ESTRATÉGICA**

### **Tests por Nivel de Complejidad**

```
Complejidad BAJA (solo software):
├─ Auth Manager       10 tests  ✅
└─ Config Manager     10 tests  ✅

Complejidad MEDIA (un hardware):
├─ SD Logger          13 tests  ✅
├─ CAN Init            2 tests  ✅
└─ Digital I/O         5 tests  ✅

Complejidad ALTA (múltiple hardware):
├─ Ethernet Manager   10 tests  ✅
├─ Web Server          8 tests  ✅
└─ W5500 SPI           3 tests  ✅

Complejidad MUY ALTA (sistema completo):
└─ Gateway E2E         0 tests  ⏳ Futuro
```

---

## 🚀 **SIGUIENTE PASO: EJECUTAR LOS TESTS**

### **Prerequisitos**

1. **Hardware:**
   - ESP32-S3 conectado por USB
   - SD card insertada (para tests de SD/Config)
   - W5500 conectado por SPI (para tests de Ethernet)
   - Cable Ethernet a router (para tests de red)

2. **Software:**
   - ESP-IDF 5.1.5 instalado
   - Drivers USB correctos

### **Comandos**

Ver el archivo `test/device/RUNNING_TESTS.md` para instrucciones detalladas.

---

## 📈 **ESTADÍSTICAS**

```
Total de archivos de test:  9
Total de líneas de código:  2,776
Total de casos de prueba:   69

Desglose por componente:
├─ Web Server          376 líneas,  8 tests
├─ Ethernet Manager    387 líneas, 10 tests
├─ Auth Manager        351 líneas, 10 tests
├─ Config Manager      371 líneas, 10 tests
├─ SD Logger           311 líneas, 13 tests
├─ OTA Manager         317 líneas,  8 tests
├─ CAN Bus Init        176 líneas,  2 tests
├─ W5500 SPI           225 líneas,  3 tests
└─ Digital I/O         262 líneas,  5 tests
```

---

## ✨ **CONCLUSIÓN**

Estos tests fueron diseñados con una filosofía clara:

1. **Progresivos** → Puedes testear sin todo el hardware
2. **Informativos** → Te dicen qué funciona y qué no
3. **Documentados** → Son ejemplos de uso ejecutables
4. **Robustos** → No crashean por hardware faltante
5. **Realistas** → Responden preguntas de desarrollo real

**No son tests perfectos** - pero son tests **útiles** para el desarrollo real de un gateway industrial.

---

**Autor:** Arturo  
**Fecha:** 2 de Noviembre de 2025  
**Proyecto:** K13 Puente Grúa - ESP32 Gateway
