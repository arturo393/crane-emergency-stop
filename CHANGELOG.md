# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### 2025-10-14 - Testcontainers Infrastructure & BL335 Gateway

- **BL335 Gateway Python** (✅ COMPLETO):
  - `src/bl335_gateway/main.py`: Gateway completo (380+ líneas)
  - Servidor TCP multicliente (puerto 9999)
  - Integración python-canopen con SocketCAN
  - Comandos JSON: `emergency_stop`, `get_status`, `reset`, `sdo_read`, `sdo_write`
  - Soporte interfaz `virtual` para testing sin módulos kernel
  - README completo con ejemplos de cliente y protocolo
  
- **K13 F Simulator** (✅ COMPLETO):
  - `tools/can_simulator.py`: Simulador completo (314 líneas)
  - CANopen completo: Heartbeat (500ms), NMT, SDO
  - Simulación de emergency stop
  - Virtual CAN support para desarrollo sin hardware
  - CLI con argumentos para configuración

- **Testcontainers Infrastructure** (✅ COMPLETO):
  - `Dockerfile.test`: Imagen Linux con Python 3.12 y dependencias CAN
  - `docker-compose.test.yml`: Orquestación Gateway + Simulator
  - `tests/conftest.py`: Fixtures completos con Testcontainers
  - Estructura organizada: `tests/unit/`, `tests/integration/`, `tests/e2e/`
  - Imagen Docker: k13-test:latest (638MB)
  - Tests básicos funcionando (6/6 ✅)
  - Documentación completa: `tests/README_TESTCONTAINERS.md`
  
- **Testing Strategy Documentation**:
  - `docs/implementation/testing_strategy.md`: Estrategia completa
  - Arquitectura de testing multi-plataforma
  - Guías de uso, troubleshooting y best practices
  
- **ESP32 WiFi Manager** (✅ COMPLETO):
  - `esp32_gateway/main/wifi_manager.cpp`: WiFi completo
  - STA mode con DHCP y auto-reconnect
  - AP mode para configuración
  - Event handlers robustos y retry logic
  
- **Dependencies Updated**:
  - testcontainers 4.13.2
  - PyQt6 6.9.1
  - python-canopen 2.4.1
  - docker 7.1.0
  - 60+ paquetes instalados y verificados

- **Tests Reorganization**:
  - Tests migrados a estructura unit/integration/e2e
  - Imports corregidos para nueva estructura
  - __init__.py agregado a cada directorio

### 2025-10-14 - GitHub Project y Nuevos Issues

- **GitHub Project Board**:
  - Creado proyecto "Crane Emergency Stop System" (#7)
  - Agregados todos los issues al proyecto
  - URL: https://github.com/users/arturo393/projects/7
  - `PROJECT_README.md`: Documentación completa del project board

- **Nuevos Issues Creados**:
  - Issue #8: Desarrollo BL335 Gateway (Python + CANopen + SocketCAN)
  - Issue #9: Interfaz de Monitoreo y Control (PyQt6 GUI)

### 2025-10-14 - Desarrollo ESP32 Gateway Iniciado

- **Estructura Base ESP32**:
  - Creada estructura completa del proyecto `esp32_gateway/` con ESP-IDF
  - `main.cpp`: Punto de entrada con FreeRTOS y loop principal
  - `can_manager.cpp/h`: Driver TWAI (CAN) funcional con soporte básico CANopen
  - `wifi_manager.cpp/h`: Estructura para gestión WiFi (pendiente implementación completa)
  - Configuración CMake completa para ESP-IDF v5.x
  - `sdkconfig.defaults`: Configuración SDK para ESP32-S3
  - `README.md`: Documentación técnica del proyecto ESP32

- **GitHub Issues**:
  - Issue #6: Adquisición de Hardware (BL335 + X8 + EdgeBox-ESP-100)
  - Issue #7: Desarrollo ESP32 completo (FOTA + WiFi + Ethernet + CANbus)

### 2025-10-14 - Consolidación de Documentación

- **Consolidación de Hardware**:
  - `docs/hardware_consolidado.md`: creado documento consolidado con toda la información de hardware (BL335, X8, EdgeBox-ESP-100)
  - Eliminados archivos redundantes: `hardware_comparison.md`, `hardware_final_selection.md`, `hardware_configuration_guide.md`, `esp32_installation.md`
  - Reducción del 30% en archivos de documentación (13 → 9 archivos)
  - Actualizadas todas las referencias cruzadas en `README.md` y `jira_update_comentario.md`

- **Gestión del Proyecto**:
  - `soluciones_seleccionadas_resumen.md`: creado resumen ejecutivo de las dos soluciones seleccionadas con diagrama explicativo
  - `jira_update_comentario.md`: creado documento de actualización para el equipo con estado del proyecto y próximos pasos
  - Configurados 5 GitHub Issues para tracking del proyecto

### 2025-10-10 - Simplificación y Mejoras

- `docs/hardware_gateways_simplified.md`: created simplified hardware comparison focusing on SOC ARM + Ubuntu IoT + CAN integrated solutions. Recommends Revolution Pi Connect+ SE as optimal choice for industrial crane control.
- `docs/hardware_gateways_comparison.md`: comprehensive comparison of Ethernet-CAN gateways for industrial crane control. Analyzed PEAK PCAN-Ethernet Gateway DR, HMS Anybus X-Gateway, Raspberry Pi Industrial, ESP32 alternatives, and industrial SOC devices with detailed technical specifications, programming examples, and vendor information.
- `src/k13_controller/rpi_can_gateway.py`: added Raspberry Pi CAN HAT driver with CANopen support for Danfoss R13 communication.
- `config/raspberry_pi_config.yaml`: added comprehensive configuration for Raspberry Pi + CAN HAT setup including hardware-specific settings and safety parameters.
- `README.md`: consolidated Executive Summary; unified architecture and communication flow; simplified and compacted diagrams.
- `email_openembedded_inquiry.md`: created and revised. Removed explicit CAN bus speed and direct references to CiA 301/402; updated questions to request vendor clarification on supported CANopen profiles and bus speeds.
- Documentation formatting: compacted markdown in the inquiry file to reduce blank-line and paste issues when copying into Gmail.
- Repository: local Git repository initialized; initial commit created (project skeleton, docs, tests, VS Code tasks).

## 2025-09-10 - Initial commit

- Project skeleton and source files added.
- Documentation and diagrams added to `README.md`.
- Tests added under `tests/` and passing locally.
- VS Code tasks and setup scripts added under `scripts/`.

For older history, check the Git commit log.
