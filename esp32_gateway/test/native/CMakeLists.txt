# --- CMakeLists para Test Nativos ---
cmake_minimum_required(VERSION 3.16)
project(NativeTests CXX)

# --- Compilador y Flags ---
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- Incluir directorios ---
# 1. Directorio de componentes reales
include_directories(
    ../../main
    ../../components/canopen
)
# 2. Directorio de mocks para simular el entorno ESP-IDF
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/mocks
)

# --- Fuentes ---
# 1. Código real a probar
set(REAL_SOURCES
    ../../main/can_manager.cpp
    ../../components/canopen/cia402.cpp
)
# 2. Mocks
set(MOCK_SOURCES
    mocks/esp_err.cpp
    mocks/driver/twai.cpp
)
# 3. Ficheros de Test
set(TEST_SOURCES
    test_cia402.cpp
    test_can_manager.cpp
)

# --- Crear el ejecutable de test ---
add_executable(
    native_tests
    ${TEST_SOURCES}
    ${REAL_SOURCES}
    ${MOCK_SOURCES}
)

# --- Mensaje final ---
message(STATUS "Configuración de tests nativos completada.")
message(STATUS "Ejecutable: native_tests")
