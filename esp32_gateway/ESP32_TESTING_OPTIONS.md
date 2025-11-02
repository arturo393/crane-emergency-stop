# Opciones para Probar Código ESP32 sin Hardware Físico

## 🎯 Problema
Queremos probar el código C++ real de `esp32_gateway/` sin tener un ESP32 físico.

## ✅ Opciones Reales (C++ Nativo)

### **Opción 1: QEMU para ESP32** ⭐ RECOMENDADO
Emulador oficial de Espressif que ejecuta el firmware ESP32 real.

#### Ventajas:
- ✅ Ejecuta el código C++ REAL compilado
- ✅ Emula el chip ESP32 completo
- ✅ Soportado oficialmente por Espressif
- ✅ Debugging con GDB
- ✅ Gratis y open source

#### Limitaciones:
- ⚠️ No emula periféricos CAN (TWAI)
- ⚠️ Solo GPIO, UART, SPI básicos
- ⚠️ Performance no es exacta

#### Setup:
```bash
# 1. Instalar QEMU para ESP32
brew install qemu

# O compilar versión Espressif
git clone https://github.com/espressif/qemu.git
cd qemu
./configure --target-list=xtensa-softmmu --enable-gcrypt --enable-slirp --disable-werror
make -j$(nproc)

# 2. Compilar firmware para QEMU
cd esp32_gateway
idf.py set-target esp32
idf.py build

# 3. Ejecutar en QEMU
qemu-system-xtensa -nographic \
    -machine esp32 \
    -drive file=build/esp32_gateway.bin,if=mtd,format=raw \
    -serial mon:stdio
```

**Estado**: Requiere configuración avanzada y no soporta CAN.

---

### **Opción 2: Unit Testing con ESP-IDF** ⭐⭐ MÁS PRÁCTICO

Usar el framework Unity integrado en ESP-IDF para tests unitarios que corren en tu PC.

#### Ventajas:
- ✅ Tests corren en host (Mac/Linux)
- ✅ Muy rápido (sin compilar firmware)
- ✅ Integración con CI/CD
- ✅ Framework Unity ya incluido
- ✅ Puedes mockear periféricos CAN

#### Cómo funciona:
```
┌─────────────────────────────────────┐
│  Código ESP32 (C++)                 │
│  ├── can_manager.cpp                │
│  ├── cia402.cpp                     │
│  └── pdo.cpp                        │
└──────────────┬──────────────────────┘
               │
               │ Extraer lógica
               ▼
┌─────────────────────────────────────┐
│  Tests Unitarios (host)             │
│  ├── test_cia402.cpp                │
│  ├── test_pdo.cpp                   │
│  └── mocks/ (CAN mocks)             │
└─────────────────────────────────────┘
```

#### Setup:
```bash
# 1. Crear directorio de tests
cd esp32_gateway
mkdir -p test

# 2. Crear archivo de test
cat > test/test_cia402.cpp << 'EOF'
#include "unity.h"
#include "../components/canopen/cia402.h"

void setUp(void) {
    // Setup antes de cada test
}

void tearDown(void) {
    // Cleanup después de cada test
}

void test_cia402_initial_state(void) {
    Cia402Controller cia402;
    TEST_ASSERT_EQUAL(CIA402_NOT_READY_TO_SWITCH_ON, cia402.get_state());
}

void test_cia402_state_transition(void) {
    Cia402Controller cia402;
    
    // Simular control word: Shutdown
    uint16_t control_word = 0x0006;
    cia402.process_control_word(control_word);
    
    TEST_ASSERT_EQUAL(CIA402_READY_TO_SWITCH_ON, cia402.get_state());
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_cia402_initial_state);
    RUN_TEST(test_cia402_state_transition);
    return UNITY_END();
}
EOF

# 3. Compilar y ejecutar tests
idf.py build
# Tests se ejecutan automáticamente
```

**Estado**: ✅ MEJOR OPCIÓN para tu caso

---

### **Opción 3: ESP32 Simulator (Wokwi)** 💰

Simulador online comercial con soporte para ESP32.

#### Ventajas:
- ✅ Simulación visual completa
- ✅ Soporta muchos periféricos
- ✅ Interfaz web fácil

#### Desventajas:
- ❌ De pago ($10-50/mes)
- ❌ No soporta CAN directamente
- ❌ Solo para proyectos simples

**URL**: https://wokwi.com/

**Estado**: ❌ No recomendado (costo y sin CAN)

---

### **Opción 4: Native Linux Build** ⭐⭐⭐ MEJOR PARA DESARROLLO

Compilar componentes como aplicación Linux nativa.

#### Ventajas:
- ✅ Ejecuta en tu Mac directamente
- ✅ Debugging con lldb/gdb normal
- ✅ Muy rápido (sin cross-compile)
- ✅ Ideal para lógica de negocio

#### Cómo:
```bash
# Estructura:
esp32_gateway/
├── components/
│   └── canopen/          ← Lógica CiA 402 (portable)
│       ├── cia402.cpp
│       └── pdo.cpp
├── main/                  ← ESP32-specific
│   └── can_manager.cpp
└── test/                  ← Linux native
    └── native/
        ├── test_main.cpp
        └── CMakeLists.txt
```

```cmake
# test/native/CMakeLists.txt
cmake_minimum_required(VERSION 3.10)
project(esp32_gateway_tests)

set(CMAKE_CXX_STANDARD 17)

# Incluir código de components
include_directories(../../components/canopen)

# Tests
add_executable(test_cia402
    test_cia402.cpp
    ../../components/canopen/cia402.cpp
    ../../components/canopen/pdo.cpp
)

# Unity (copiar de ESP-IDF)
target_include_directories(test_cia402 PRIVATE
    $ENV{IDF_PATH}/components/unity/include
)

# Ejecutar
add_custom_target(run_tests
    COMMAND ./test_cia402
    DEPENDS test_cia402
)
```

```bash
# Compilar y ejecutar
cd esp32_gateway/test/native
mkdir build && cd build
cmake ..
make
./test_cia402
```

**Estado**: ✅ EXCELENTE para testing de lógica

---

### **Opción 5: Mock Framework (CMock)** 🔧

Usar CMock para mockear periféricos ESP32.

#### Ventajas:
- ✅ Mocks automáticos de APIs ESP-IDF
- ✅ Testing de integración completo
- ✅ Ya incluido en ESP-IDF

#### Setup:
```bash
# ESP-IDF ya incluye CMock
cd esp32_gateway
mkdir -p test/mocks

# Generar mocks automáticos
python $IDF_PATH/tools/unit-test-app/gen_mock.py \
    components/driver/include/driver/twai.h \
    test/mocks/mock_twai.c
```

**Estado**: ⭐ Complementa otras opciones

---

## 🎯 Recomendación para tu Proyecto

### ✅ Estrategia Híbrida Óptima:

```
┌─────────────────────────────────────────────────────────┐
│ 1. LÓGICA DE NEGOCIO (CiA 402, PDO)                    │
│    → Native Linux Build                                 │
│    → Tests unitarios rápidos                            │
│    → 90% de tu código                                   │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 2. INTEGRACIÓN CAN                                      │
│    → Unit Tests con Mocks                               │
│    → Mockear TWAI driver                                │
│    → Validar llamadas correctas                         │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 3. HARDWARE FINAL                                       │
│    → Cuando recibas EdgeBox Lite                        │
│    → Testing con radio K13 F real                       │
│    → 1-2 semanas antes de producción                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Plan de Acción Inmediato

### Paso 1: Extraer Lógica Portable ✅
```bash
# Ya tienes esto organizado:
components/canopen/
├── cia402.h
├── cia402.cpp
├── pdo.h
└── pdo.cpp
```

### Paso 2: Crear Build Nativo
```bash
cd esp32_gateway
mkdir -p test/native
# (Ver setup arriba)
```

### Paso 3: Tests Unitarios
```bash
# Crear tests para:
- Estado inicial CiA 402
- Transiciones de estado
- PDO parsing
- Control/Status words
```

### Paso 4: CI/CD
```bash
# GitHub Actions
.github/workflows/test-esp32.yml
```

---

## 💡 Ejemplo Práctico Inmediato

Puedes empezar AHORA mismo sin esperar hardware:

```cpp
// test/native/test_cia402.cpp
#include <iostream>
#include <cassert>

// Incluir tu código real
#include "../../components/canopen/cia402.h"

int main() {
    std::cout << "Testing CiA 402 State Machine...\n";
    
    Cia402Controller cia402;
    
    // Test 1: Estado inicial
    assert(cia402.get_state() == CIA402_NOT_READY_TO_SWITCH_ON);
    std::cout << "✅ Initial state correct\n";
    
    // Test 2: Shutdown transition
    cia402.process_control_word(0x0006);
    assert(cia402.get_state() == CIA402_READY_TO_SWITCH_ON);
    std::cout << "✅ Shutdown transition works\n";
    
    // Test 3: Switch On
    cia402.process_control_word(0x0007);
    assert(cia402.get_state() == CIA402_SWITCHED_ON);
    std::cout << "✅ Switch On transition works\n";
    
    std::cout << "\n🎉 All tests passed!\n";
    return 0;
}
```

Compilar:
```bash
g++ -std=c++17 \
    -I../../components/canopen \
    test_cia402.cpp \
    ../../components/canopen/cia402.cpp \
    -o test_cia402

./test_cia402
```

---

## 📊 Comparación de Opciones

| Opción | Setup | Velocidad | Cobertura | Realismo | Costo |
|--------|-------|-----------|-----------|----------|-------|
| **QEMU ESP32** | Difícil | Lento | 50% | Alto | $0 |
| **Unit Tests (Unity)** | Fácil | Rápido | 80% | Medio | $0 |
| **Native Build** | Medio | Muy rápido | 90% | Medio | $0 |
| **Wokwi** | Fácil | Medio | 60% | Alto | $$ |
| **Mocks (CMock)** | Medio | Rápido | 70% | Bajo | $0 |

**Ganador**: 🏆 **Native Build + Unity Tests**

---

## 🚀 Próximos Pasos

1. **HOY**: Crear estructura de tests nativos
2. **MAÑANA**: Escribir primeros tests unitarios
3. **ESTA SEMANA**: 80% cobertura de lógica CiA 402
4. **CUANDO LLEGUE HARDWARE**: Validación final

---

**Archivo**: `esp32_gateway/ESP32_TESTING_OPTIONS.md`
**Fecha**: 31 de octubre de 2025
**Conclusión**: Usa Native Linux Build para probar lógica C++ real sin hardware
