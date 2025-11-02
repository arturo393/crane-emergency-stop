# 🧪 Testing Nativo del Código ESP32

## ✅ Solución Real: Compilar y Ejecutar Código C++ del ESP32 en tu Mac

Esta es la forma correcta de probar el código C++ del ESP32 sin hardware físico.

### 🎯 Qué Hace

- Compila el código **C++ REAL** del ESP32 como aplicación nativa de macOS
- Ejecuta tests del estado machine CiA 402
- **NO es una simulación**: Es el código exacto que correrá en el ESP32
- Tests pasan/fallan basados en la lógica real de tu firmware

---

## 🚀 Inicio Rápido

```bash
# Ir al directorio de tests nativos
cd esp32_gateway/test/native

# Compilar y ejecutar tests
./build.sh
```

**Output esperado**:
```
========================================
  Tests Nativos CiA 402 State Machine
  Ejecutando código C++ REAL del ESP32
========================================

▶ Test 1: Estado Inicial
  Estado inicial: NOT_READY_TO_SWITCH_ON
  Status Word: 0x0000
  ✅ Estado inicial debe ser NOT_READY_TO_SWITCH_ON

▶ Test 2: Transición Shutdown
  Enviando Control Word: 0x0006
  Nuevo estado: READY_TO_SWITCH_ON
  ✅ Después de Shutdown debe estar en READY_TO_SWITCH_ON

▶ Test 3: Transición Switch On
  Enviando Control Word: 0x0007
  Nuevo estado: SWITCHED_ON
  ✅ Después de Switch On debe estar en SWITCHED_ON

...

========================================
  RESUMEN DE TESTS
========================================
  ✅ Pasados: 9
  ❌ Fallidos: 0
  Total: 9
========================================

🎉 Todos los tests pasaron
```

---

## 📋 Requisitos

- ✅ macOS (o Linux)
- ✅ CMake 3.10+
- ✅ Compilador C++ con C++17
- ✅ El código ESP32 en `esp32_gateway/components/canopen/`

**Verificar**:
```bash
cmake --version    # Debe mostrar 3.10+
g++ --version      # O clang++ (viene con Xcode)
```

---

## 🔧 Comandos Disponibles

### Build Normal
```bash
./build.sh
```

### Build Limpio (desde cero)
```bash
./build.sh --clean
```

### Compilar sin Ejecutar
```bash
./build.sh --no-run
```

### Ejecutar Tests Manualmente
```bash
cd build
./test_cia402
```

---

## 📁 Estructura

```
test/native/
├── build.sh                 ← Script de build
├── CMakeLists.txt          ← Configuración CMake
├── test_cia402.cpp         ← Tests del state machine
├── README.md               ← Esta guía
└── build/                  ← Compilados (auto-generado)
    ├── test_cia402         ← Ejecutable de tests
    └── ...
```

---

## ✨ Ventajas de Esta Solución

### ✅ Es el Código REAL
```cpp
// Este es el MISMO código que ejecutará el ESP32
#include "cia402.h"  // ← components/canopen/cia402.cpp

Cia402Controller cia402;  // ← Exactamente igual que en el ESP32
cia402.process_control_word(0x0006);
```

### ✅ Rápido
- Compilación: ~2 segundos
- Ejecución: instantánea
- vs ESP32 real: build 5-10 min, flash 30 seg

### ✅ Debugging Fácil
```bash
# Debugging con lldb
lldb ./test_cia402
(lldb) b test_shutdown_transition
(lldb) run
(lldb) print cia402.state()
```

### ✅ CI/CD Ready
```yaml
# .github/workflows/test-esp32.yml
- name: Test ESP32 Code
  run: |
    cd esp32_gateway/test/native
    ./build.sh
```

---

## 🧪 Agregar Más Tests

### Crear Nuevo Test

```cpp
// test/native/test_pdo.cpp
#include <iostream>
#include <cassert>
#include "pdo.h"  // Tu código real

int main() {
    std::cout << "Testing PDO parsing...\n";
    
    // Test parsing RPDO1
    uint8_t data[8] = {0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
    uint16_t control_word = parse_control_word(data);
    
    assert(control_word == 0x0006);
    std::cout << "✅ PDO parsing works\n";
    
    return 0;
}
```

### Agregar a CMakeLists.txt

```cmake
add_executable(test_pdo
    test_pdo.cpp
    ../../components/canopen/pdo.cpp
)
target_link_libraries(test_pdo canopen_components)
```

### Recompilar

```bash
./build.sh --clean
```

---

## 🐛 Troubleshooting

### Error: "cmake: command not found"

```bash
# Instalar CMake
brew install cmake
```

### Error: "No such file or directory: cia402.h"

Verifica que existe el archivo:
```bash
ls ../../components/canopen/cia402.h
```

### Error: "undefined reference to..."

El código tiene dependencias de ESP-IDF que no están disponibles en macOS.

**Solución**: Separar código portable del código ESP32-specific:

```
components/canopen/
├── cia402.cpp      ← Portable (solo C++ estándar)
├── cia402.h
├── pdo.cpp         ← Portable
└── pdo.h

main/
├── can_manager.cpp ← ESP32-specific (usa TWAI driver)
└── can_manager.h
```

Para testear `can_manager.cpp`, necesitas mocks (ver abajo).

---

## 🔧 Testing con Mocks (Avanzado)

Para testear código que usa APIs de ESP-IDF (como TWAI):

### 1. Crear Mock

```cpp
// test/native/mocks/mock_twai.h
#pragma once
#include <cstdint>

// Mock del TWAI driver
typedef struct {
    uint32_t identifier;
    uint8_t data[8];
    uint8_t data_length_code;
} twai_message_t;

esp_err_t twai_transmit(const twai_message_t* message, uint32_t timeout);
esp_err_t twai_receive(twai_message_t* message, uint32_t timeout);
```

### 2. Implementar Mock

```cpp
// test/native/mocks/mock_twai.cpp
#include "mock_twai.h"
#include <vector>

// Buffer simulado de mensajes
static std::vector<twai_message_t> message_queue;

esp_err_t twai_transmit(const twai_message_t* message, uint32_t timeout) {
    message_queue.push_back(*message);
    return ESP_OK;
}

esp_err_t twai_receive(twai_message_t* message, uint32_t timeout) {
    if (message_queue.empty()) {
        return ESP_ERR_TIMEOUT;
    }
    *message = message_queue.front();
    message_queue.erase(message_queue.begin());
    return ESP_OK;
}
```

### 3. Testear con Mock

```cpp
// test/native/test_can_manager.cpp
#include "can_manager.h"
#include "mocks/mock_twai.h"

int main() {
    CANManager can;
    can.send_heartbeat();
    
    // Verificar que se envió el mensaje
    twai_message_t msg;
    assert(twai_receive(&msg, 100) == ESP_OK);
    assert(msg.identifier == 0x701);
    
    std::cout << "✅ CAN Manager works\n";
    return 0;
}
```

---

## 📊 Comparación: Native Tests vs ESP32 Real

| Aspecto | Native Tests | ESP32 Real |
|---------|--------------|------------|
| **Setup** | ./build.sh | idf.py build flash |
| **Tiempo build** | ~2 segundos | 5-10 minutos |
| **Debugging** | lldb/gdb | Serial monitor |
| **Iteración** | Instantánea | Lenta (flash cada vez) |
| **Hardware** | No necesario | ESP32 + CAN transceiver |
| **Cobertura** | Lógica (90%) | Todo (100%) |
| **Uso** | Desarrollo diario | Validación final |

---

## 🎯 Flujo de Trabajo Recomendado

```
1. Desarrollo
   ↓
   ./build.sh (tests nativos)
   ↓
   ¿Pasan? → No → Fix código → Repetir
   ↓ Sí
2. Commit código
   ↓
3. CI/CD ejecuta tests
   ↓
4. (Cuando tengas hardware)
   idf.py flash monitor
   ↓
5. Validación con K13 F real
```

---

## 💡 Tips

### Ejecutar Solo Un Test

Modifica `test_cia402.cpp`:
```cpp
int main() {
    // Comentar tests que no quieres ejecutar
    test_initial_state();
    // test_shutdown_transition();
    // test_switch_on_transition();
    // ...
}
```

### Ver Output Detallado

```bash
# Build con más info
cd build
cmake .. -DCMAKE_VERBOSE_MAKEFILE=ON
make
```

### Debugging con lldb

```bash
cd build
lldb ./test_cia402
(lldb) breakpoint set --name test_shutdown_transition
(lldb) run
(lldb) step
(lldb) print control_word
(lldb) continue
```

---

## 🚀 Próximos Pasos

1. ✅ Ejecutar tests existentes: `./build.sh`
2. 📝 Agregar tests para tus casos de uso
3. 🔧 Integrar en CI/CD
4. 🧪 Crear mocks para código ESP32-specific
5. 📦 Cuando tengas hardware: validar con ESP32 real

---

## ❓ FAQ

### ¿Puedo testear TODO el código del ESP32 así?

**No todo**. Puedes testear:
- ✅ Lógica de negocio (CiA 402, PDO, protocolos)
- ✅ Algoritmos
- ✅ State machines
- ✅ Parsing de datos

No puedes testear directamente (sin mocks):
- ❌ Driver TWAI/CAN
- ❌ WiFi/Ethernet
- ❌ GPIO hardware
- ❌ Timers específicos de ESP32

**Solución**: Usa mocks para esas partes.

### ¿Los tests garantizan que funcionará en ESP32 real?

**No al 100%**, pero sí ~90% de la lógica. Los tests nativos validan:
- Lógica correcta
- Transiciones de estado
- Parsing de datos
- Algoritmos

El 10% restante (hardware específico) se valida con el ESP32 real.

### ¿Necesito ESP-IDF instalado?

**No** para estos tests nativos. Solo necesitas:
- CMake
- Compilador C++

### ¿Puedo ejecutar en Linux/Windows?

**Sí**. El script `build.sh` funciona en:
- ✅ macOS
- ✅ Linux
- ⚠️ Windows (necesitas WSL o Git Bash)

---

**Autor**: SafetyMind Team  
**Fecha**: 31 de octubre de 2025  
**Última actualización**: Tests nativos para código ESP32 real
