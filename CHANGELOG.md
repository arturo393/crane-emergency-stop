# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### 2025-10-24 - Desktop GUI PyQt6 Implementation

- **Desktop GUI Complete** (✅ NUEVO):
  - `src/web_ui/desktop_gui.py`: 730 líneas de código PyQt6
  - 4 widgets profesionales: DashboardWidget, CANMonitorWidget, ControlPanelWidget, LogWidget
  - Threading asíncrono (StatusUpdateThread) sin bloqueo de UI
  - Color coding automático para estados CiA 402
  - Buffer circular para monitor CAN (100 mensajes)
  - Emergency stop prominente con botón rojo grande
  - Integración completa con IntegratedSystem

- **Testing Desktop GUI** (✅ 100%):
  - `tests/unit/test_desktop_gui.py`: 15 tests, todos pasando
  - Cobertura completa: widgets, señales Qt, threading
  - Validación de funcionalidad: dashboard, monitor, control, logs
  - Tests en 8.97s

- **Documentación Exhaustiva** (✅ 950+ líneas):
  - `docs/GUI_COMPARISON.md`: Comparación Web UI vs Desktop GUI (250 líneas)
  - `docs/DESKTOP_GUI_QUICKSTART.md`: Guía rápida de usuario (300 líneas)
  - `PROGRESS_GUI_24OCT2025.md`: Reporte completo de sesión (400 líneas)
  - Arquitectura detallada, casos de uso, roadmap de mejoras

- **Infraestructura**:
  - `scripts/launch_gui.py`: Script launcher para Desktop GUI
  - `.vscode/tasks.json`: Task "Iniciar Desktop GUI" agregado
  - `requirements.txt`: PyQt6>=6.4.0 agregado
  - PyQt6 6.9.1 instalado y validado

- **Decisión Estratégica**:
  - Mantener DOS interfaces complementarias:
    - Web UI (FastAPI + WebSocket) - Acceso remoto, dashboard central
    - Desktop GUI (PyQt6) - Control local, máxima performance
  - Cobertura completa de casos de uso industrial

- **Progreso del Proyecto**:
  - Tests totales: 53/54 (98%) - 31 unitarios + 15 GUI + 7 E2E
  - Progreso TODO: 87% → 88%
  - GUI: ⏸️ PENDIENTE → 🚀 EN PROGRESO (85% completado)

### 2025-10-24 - SDO Bug Fix & Delay Optimization

- **BL335 Gateway SDO Fix** (✅ COMPLETADO):
  - Bug corregido: `'SdoVariable' object is not subscriptable`
  - Solución: Acceso condicional basado en subindex
  - `subindex == 0`: acceso directo `sdo[index].raw`
  - `subindex != 0`: doble subscript `sdo[index][subindex].raw`
  - Tests mejorados: 12/17 → 16/17 (94%)

- **Control Sequences Optimization** (✅ COMPLETADO):
  - `src/k13_controller/control_sequences.py`: Delay adaptativo implementado
  - Constante SDO_MIN_DELAY = 0.05 (50ms mínimo entre SDO writes)
  - Prevención de saturación del simulador
  - Fórmula: `adjusted_step_time = max(step_time, SDO_MIN_DELAY)`

- **ESP32 Firmware Build** (✅ COMPLETADO):
  - SSL certificates resueltos: certifi 2025.10.5
  - ESP-IDF v5.1.5 compilación exitosa
  - 951/951 archivos compilados
  - Binarios generados: bootloader (20.97 KB), partition-table (3 KB), app (227.17 KB)

- **Documentation** (✅ COMPLETADO):
  - `docs/BC292382016572en-000201.md`: Manual Danfoss R13 F reorganizado (800 líneas)
  - Table of contents con navegación
  - CANopen protocol details (CiA 402)
  - Troubleshooting procedures mejoradas
  - `TODO.md`: 460 líneas de tracking completo
  - `PROGRESS_24OCT2025.md`: Reporte de sesión (300+ líneas)

### 2025-10-18 - ESP32 TCP Server & BL335 PDO Support Completion

- **ESP32 Gateway TCP Server** (✅ COMPLETO):
  - `esp32_gateway/components/tcp_server/tcp_server_manager.h`: Header completo
  - `esp32_gateway/components/tcp_server/tcp_server_manager.cpp`: Implementación TCP
  - Servidor multi-client con FreeRTOS tasks
  - Protocolo JSON para comandos: `emergency_stop`, `get_status`, `reset`
  - Callback system integrado en `main.cpp`
  - Estadísticas de conexión y manejo de errores

- **ESP32 Ethernet Manager** (✅ COMPLETO):
  - `esp32_gateway/components/ethernet/ethernet_manager.h`: Header completo
  - `esp32_gateway/components/ethernet/ethernet_manager.cpp`: Driver W5500/LAN8720
  - DHCP automático + IP estática opcional
  - Failover WiFi ↔ Ethernet
  - Configuración SPI integrada

- **ESP32 OTA Manager** (✅ COMPLETO):
  - `esp32_gateway/components/ota/ota_manager.h`: Header completo
  - `esp32_gateway/components/ota/ota_manager.cpp`: FOTA implementation
  - Actualización HTTP/HTTPS con verificación de firma
  - Rollback automático en caso de fallo
  - Progreso de actualización con logs

- **BL335 Gateway PDO Support** (✅ COMPLETO):
  - Soporte completo PDO: RPDO1, TPDO1, TPDO2
  - Mapeo automático de objetos CANopen
  - Emergency stop vía PDO (respuesta inmediata)
  - Carga de archivos EDS para configuración automática
  - Configuración NMT mejorada con heartbeat
  - Estados CANopen: Pre-operational, Operational, Stopped

- **Testing & Validation** (✅ COMPLETO):
  - 44/44 pruebas unitarias pasan
  - Protocolo CANopen 100% validado
  - Integración TCP/IP probada
  - Emergency stop funcional vía PDO

- **Issues Created**:
  - #17: ESP32 Gateway completion status
  - #18: BL335 Gateway completion status
  - #19: Pre-hardware work planning

- **Commit**: `298044f` - feat: Complete ESP32 TCP server and BL335 PDO support implementation

### 2025-10-14 - Testcontainers Infrastructure & BL335 Gateway

- **BL335 Gateway Python** (✅ COMPLETO):
  - `src/bl335_gateway/main.py`: Gateway completo (380+ líneas)
  - Servidor TCP multicliente (puerto 9999)
  - Integración python-canopen con SocketCAN
  - Comandos JSON: `emergency_stop`, `get_status`, `reset`, `sdo_read`, `sdo_write`
  - Soporte interfaz `virtual` para testing sin módulos kernel
  - README completo con ejemplos de cliente y protocolo
  
- **R13 F Simulator** (✅ COMPLETO):
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
