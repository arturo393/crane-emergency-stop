# SD Logger - Implementación Completa

**Fecha:** 1 de Noviembre de 2025  
**Gateway:** D13 ESP32-S3  
**Versión Firmware:** 465 KB (compilación exitosa)

---

## ✅ Características Implementadas

### 1. **Sistema de Logging Persistente**
- **Formato de archivo:** `gateway_YYYYMMDD_HHMMSS.log`
- **Ubicación:** `/sdcard/` (punto de montaje SD)
- **Formato de log:** `[YYYY-MM-DD HH:MM:SS.mmm] [LEVEL] TAG: mensaje`
- **Niveles:** DEBUG, INFO, WARN, ERROR

### 2. **Auto-Rotación de Archivos**
- **Umbral:** 1 MB por archivo
- **Mecanismo:** Verifica tamaño después de cada escritura
- **Acción:** Crea nuevo archivo cuando se alcanza el límite
- **Timestamp:** Cada archivo tiene timestamp único en el nombre

### 3. **Auto-Limpieza de Archivos Antiguos**
- **Límite:** Mantiene solo los últimos 10 archivos
- **Algoritmo:**
  1. Cuenta archivos de log en el directorio
  2. Si hay más de 10, encuentra el más antiguo (por mtime)
  3. Elimina el más antiguo
  4. Repite hasta tener ≤ 10 archivos
- **Protección:** Previene que la SD se llene completamente

### 4. **Thread-Safety (Seguridad Multi-hilo)**
- **Mutex FreeRTOS:** Protege escrituras concurrentes
- **Múltiples tareas:** Pueden escribir simultáneamente sin corrupción
- **Timeout:** 100ms para adquirir mutex

### 5. **Degradación Elegante**
- **Sin SD:** El sistema continúa funcionando normalmente
- **Fallo de montaje:** No bloquea el inicio del gateway
- **Macros de log:** No causan crash si SD no disponible
- **Logging:** Mensajes de error informativos en consola

### 6. **Información de Disco**
```cpp
bool get_disk_info(uint32_t* total_mb, uint32_t* used_mb);
```
- Retorna espacio total y usado en MB
- Útil para monitoreo de capacidad

---

## 📊 Puntos de Logging Integrados

### **1. Bus CAN**
```cpp
SD_LOGI(TAG, "CAN bus inicializado correctamente (TX:%d, RX:%d, 250kbps)", ...);
SD_LOGE(TAG, "Error al inicializar CAN bus: %s", esp_err_to_name(ret));
```

### **2. Autenticación TCP**
```cpp
SD_LOGI(TAG, "Cliente autenticado desde %lu.%lu.%lu.%lu", ...);
SD_LOGW(TAG, "Token incorrecto desde %lu.%lu.%lu.%lu", ...);
SD_LOGW(TAG, "IP bloqueada: %lu.%lu.%lu.%lu (demasiados intentos)", ...);
```

### **3. Comandos de Red**
```cpp
SD_LOGI(TAG, "Comando ejecutado: ENABLE desde 192.168.1.100", ...);
SD_LOGW(TAG, "Comando desconocido recibido: INVALID_CMD");
```

### **4. Transiciones CiA402**
```cpp
SD_LOGI(TAG, "Transición CiA402: State 2->3, Status 0x0021->0x0023, CW=0x000F");
SD_LOGW(TAG, "Mutex CiA402 bloqueado, comando 1 no procesado");
```

---

## 🧪 Tests Implementados

### **Tests de Dispositivo** (`test/device/test_sd_logger.cpp`)
Requieren hardware ESP32 + SD card

1. **test_sd_init**: Inicialización de SD card
2. **test_sd_basic_logging**: Escritura básica de logs
3. **test_sd_log_rotation**: Rotación al alcanzar 1MB
4. **test_sd_auto_cleanup**: Limpieza automática (mantiene 10 archivos)
5. **test_sd_disk_info**: Información de espacio en disco
6. **test_sd_thread_safety**: Escritura concurrente desde múltiples tareas
7. **test_sd_graceful_failure**: Comportamiento sin SD card

### **Tests Nativos** (`test/native/test_sd_logger_unit.cpp`)
Se ejecutan en host (sin hardware)

1. **test_log_level_to_string**: Conversión de niveles a strings
2. **test_configuration_constants**: Valores de configuración
3. **test_file_naming_pattern**: Patrón de nombres de archivo
4. **test_rotation_threshold**: Umbral de rotación (1MB)
5. **test_max_files_limit**: Límite de archivos (10)
6. **test_class_size**: Tamaño de clase SDLogger

---

## 📋 Configuración Hardware

### **Pines SD Card (EdgeBox-Lite)**
```cpp
#define PIN_SD_MOSI   33
#define PIN_SD_MISO   34
#define PIN_SD_CLK    35
#define PIN_SD_CS     36
```

### **Bus SPI**
- **Modo:** SPI2_HOST
- **Frecuencia:** 20 MHz
- **Sistema de archivos:** FAT32

---

## 🔧 Uso del Sistema

### **Inicialización**
```cpp
// En app_main()
sd_logger = new SDLogger();
if (sd_logger->init()) {
    ESP_LOGI(TAG, "SD logger inicializado");
} else {
    ESP_LOGW(TAG, "SD logger no disponible, continuando sin logging persistente");
}
```

### **Logging**
```cpp
SD_LOGI(TAG, "Mensaje informativo: %d", value);
SD_LOGW(TAG, "Advertencia: %s", warning);
SD_LOGE(TAG, "Error crítico: 0x%04X", error_code);
SD_LOGD(TAG, "Debug detallado: %f", debug_value);
```

### **Rotación Manual**
```cpp
sd_logger->rotate_log(); // Fuerza creación de nuevo archivo
```

### **Información de Disco**
```cpp
uint32_t total_mb, used_mb;
if (sd_logger->get_disk_info(&total_mb, &used_mb)) {
    printf("SD: %lu MB total, %lu MB usados\n", total_mb, used_mb);
}
```

---

## 📈 Tamaño del Firmware

| Componente | Tamaño | Notas |
|-----------|--------|-------|
| **Firmware base** | ~390 KB | Gateway sin SD logger |
| **SD Logger** | ~75 KB | Sistema completo de logging |
| **Total** | **465 KB** | 37% de 1.25 MB flash |
| **Espacio libre** | 785 KB | Suficiente para OTA y web panel |

---

## ⏭️ Próximos Pasos

### **1. Validación en Hardware** (1-2 horas)
- [ ] Flashear firmware a ESP32-S3
- [ ] Insertar SD card (FAT32, ≥ 1GB)
- [ ] Ejecutar tests de dispositivo
- [ ] Verificar rotación con datos reales
- [ ] Validar auto-limpieza

### **2. Actualización Jira** (30 min)
- [ ] Worklog: 3 horas
  - Diseño e implementación SD logger (1.5h)
  - Integración en puntos críticos (1h)
  - Creación de tests (0.5h)
- [ ] Comentario: "SD logging con auto-rotación (1MB) y auto-limpieza (10 archivos) completado"
- [ ] Adjuntar: Resumen de implementación

### **3. OTA Updates** (3-4 horas) - SIGUIENTE FEATURE
**Prioridad:** ALTA (permite actualizaciones remotas)

**Características a implementar:**
- [ ] HTTP/HTTPS OTA endpoint
- [ ] Verificación de firma digital
- [ ] Rollback automático en caso de fallo
- [ ] Preservación de configuración durante actualización
- [ ] SD logging de proceso OTA

**Componentes ESP-IDF:**
```cpp
#include "esp_https_ota.h"
#include "esp_ota_ops.h"
```

**Implementación:**
1. Endpoint HTTP para recibir firmware (`/api/ota/upload`)
2. Verificación SHA256 del firmware
3. Escritura a partición OTA inactiva
4. Validación de imagen
5. Marcado como booteable
6. Rollback si falla el primer arranque

### **4. Web Panel de Monitoreo** (4-5 horas) - BAJA PRIORIDAD
**Características:**
- [ ] WebSocket server para datos en tiempo real
- [ ] Dashboard HTML/CSS/JS
- [ ] Visualización de estado CAN, Ethernet, SD
- [ ] Gráficos de Status Word / State
- [ ] Configuración de parámetros
- [ ] Visor de logs en tiempo real

---

## 📝 Notas Técnicas

### **Limitaciones Conocidas**
1. **Timestamp:** Requiere sincronización NTP para fechas correctas (actualmente usa RTC interno)
2. **Formato FAT32:** Máximo 4GB por archivo (no es problema con rotación a 1MB)
3. **Escritura síncrona:** Puede agregar latencia (~10ms por write)

### **Optimizaciones Futuras**
1. **Buffer circular:** Escrituras asíncronas en batch
2. **Compresión:** Archivos .log.gz para ahorrar espacio
3. **Upload remoto:** Subir logs a servidor via HTTPS
4. **Niveles dinámicos:** Cambiar nivel de log sin recompilar

---

## ✅ Checklist de Compilación

- [x] Código compila sin errores
- [x] Warnings de struct initialization (no críticos)
- [x] Binario: 465 KB (dentro de límites)
- [x] Integración en main.cpp completa
- [x] Tests device creados
- [x] Tests native creados
- [ ] Validación en hardware (pendiente)

---

## 🎯 Resumen Ejecutivo

El **sistema de SD logging** ha sido implementado completamente con:

✅ **Auto-rotación** a 1 MB  
✅ **Auto-limpieza** manteniendo 10 archivos  
✅ **Thread-safety** con mutex FreeRTOS  
✅ **Degradación elegante** sin SD  
✅ **Integración** en todos los puntos críticos  
✅ **Tests** device y native  

El firmware compila exitosamente a **465 KB** (aumento de 75 KB). El sistema está listo para validación en hardware real.

**Próximo paso:** Actualizar Jira y continuar con **OTA Updates**.
