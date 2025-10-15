# 🏗️ Crane Emergency Stop System - Project Board

## 📊 Vista General del Proyecto

Proyecto para desarrollo del sistema de parada de emergencia de puente grúa con control remoto vía CANopen.

**Project Board**: https://github.com/users/arturo393/projects/7

## 🎯 Objetivos del Proyecto

1. **Hardware**: Adquirir e instalar gateways (BL335 + ESP32)
2. **Firmware ESP32**: Desarrollar gateway con FOTA, WiFi, Ethernet y CAN
3. **Software BL335**: Implementar gateway Python con CANopen
4. **Interfaz de Usuario**: Crear monitor y control del sistema

## 📋 Issues del Proyecto

### Issue #6: Adquisición de Hardware 🛒
- **Estado**: Abierto
- **Prioridad**: Alta
- **Hardware**: BL335 ($35) + X8 ($8) + EdgeBox-ESP-100 ($45)
- **Presupuesto**: $148 USD ≈ $143.000 CLP
- **Timeline**: 2 semanas + 15-20 días envío
- **Link**: https://github.com/arturo393/crane-emergency-stop/issues/6

### Issue #7: Desarrollo ESP32 Gateway 🚀
- **Estado**: En Progreso
- **Prioridad**: Alta
- **Funcionalidades**:
  - FOTA (Firmware Over-The-Air)
  - WiFi con DHCP
  - Ethernet con DHCP configurable
  - Envío de datos por CANbus
- **Stack**: ESP-IDF v5.x + C++ + FreeRTOS
- **Timeline**: 3-4 semanas
- **Link**: https://github.com/arturo393/crane-emergency-stop/issues/7

### Issue #8: Desarrollo BL335 Gateway 🐧
- **Estado**: Abierto
- **Prioridad**: Alta
- **Funcionalidades**:
  - Python + CANopen (python-canopen)
  - SocketCAN driver
  - Servidor TCP/IP en puerto 9999
  - Interface K13 F
- **Stack**: Ubuntu IoT + Python 3.8+ + SocketCAN
- **Timeline**: 2-3 semanas
- **Link**: https://github.com/arturo393/crane-emergency-stop/issues/8

### Issue #9: Interfaz de Monitoreo y Control 🖥️
- **Estado**: Abierto
- **Prioridad**: Media
- **Funcionalidades**:
  - Monitor CANbus en tiempo real
  - Dashboard estado K13 F
  - Panel de control de movimientos
  - Logs y diagnósticos
- **Stack**: PyQt6 + pyqtgraph
- **Timeline**: 2 semanas
- **Link**: https://github.com/arturo393/crane-emergency-stop/issues/9

## 📅 Timeline General

```
Semana 1-2:   Adquisición de Hardware (#6)
              └─ Compra + Envío

Semana 3-6:   Desarrollo ESP32 (#7) - En Progreso
              ├─ Semana 3: WiFi + Ethernet
              ├─ Semana 4: CANbus + CANopen
              ├─ Semana 5: FOTA + Testing
              └─ Semana 6: Documentación

Semana 4-6:   Desarrollo BL335 (#8)
              ├─ Semana 4: Setup + CANopen
              ├─ Semana 5: Interface K13 + TCP
              └─ Semana 6: Testing

Semana 7-8:   Interfaz Monitor (#9)
              ├─ Semana 7: UI + Monitor CAN
              └─ Semana 8: Dashboard + Control

Semana 9:     Integración y Testing Final
```

## 🔄 Workflow del Proyecto

### Columnas del Board
1. **📝 Backlog**: Issues pendientes de iniciar
2. **🏗️ In Progress**: Issues en desarrollo activo
3. **👀 Review**: Issues en revisión/testing
4. **✅ Done**: Issues completados

### Labels Utilizados
- `hardware`: Relacionado con hardware físico
- `firmware`: Código para ESP32
- `software`: Código para BL335/PC
- `ui`: Interfaz de usuario
- `documentation`: Documentación
- `testing`: Tests y validación
- `priority:high`: Prioridad alta
- `priority:medium`: Prioridad media
- `priority:low`: Prioridad baja

## 🎯 Hitos (Milestones)

### Milestone 1: Hardware Setup ✅
- Issue #6: Adquisición completada
- Hardware instalado y funcionando

### Milestone 2: Gateways Funcionales
- Issue #7: ESP32 operacional
- Issue #8: BL335 operacional
- Comunicación CAN establecida

### Milestone 3: Sistema Completo
- Issue #9: UI funcionando
- Integración end-to-end
- Testing completo
- Documentación finalizada

## 📊 Métricas del Proyecto

### Progreso Actual
- **Issues Totales**: 4
- **Completados**: 0
- **En Progreso**: 1 (ESP32)
- **Pendientes**: 3

### Commits
- Ver: https://github.com/arturo393/crane-emergency-stop/commits/clean-main

### Documentación
- `docs/hardware_consolidado.md`: Hardware completo
- `esp32_gateway/README.md`: Documentación ESP32
- `CHANGELOG.md`: Historial de cambios

## 🔗 Enlaces Importantes

- **Repositorio**: https://github.com/arturo393/crane-emergency-stop
- **Project Board**: https://github.com/users/arturo393/projects/7
- **Branch Principal**: `clean-main`
- **Documentación**: `/docs`

## 👥 Equipo

- **Desarrollador**: @arturo393
- **Revisión**: TBD

## 📞 Contacto

Para preguntas o sugerencias sobre el proyecto, abrir un issue en el repositorio.

---
*Última actualización: 14 de octubre de 2025*
