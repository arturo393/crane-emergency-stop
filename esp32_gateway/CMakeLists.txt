# ESP32 Gateway - CMakeLists.txt Principal
# Proyecto de Gateway Ethernet-CAN para Danfoss R13 F

cmake_minimum_required(VERSION 3.16)

# Incluir componentes de ESP-IDF
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Nombre del proyecto
project(esp32_gateway)

# Configuración del proyecto
set(EXTRA_COMPONENT_DIRS components)
