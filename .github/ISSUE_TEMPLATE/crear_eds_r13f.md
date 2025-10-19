---
name: Crear archivo EDS para Danfoss R13 F
about: Implementar Electronic Data Sheet basado en documentación del receptor R13 F
title: '🔧 Crear EDS realista para Danfoss R13 F Receiver'
labels: enhancement, eds-implementation, canopen, documentation
assignees: ''
---

<!-- 
🤖 AUTOMATIZACIÓN ACTIVA
Este issue es rastreado automáticamente por GitHub Actions.
Los updates de progreso se publican automáticamente al hacer push.
Ver: .github/workflows/eds-progress-tracker.yml
-->

## 📋 Descripción

Crear un archivo **EDS (Electronic Data Sheet)** lo más cercano posible a la especificación real del receptor **Danfoss R13 F** para habilitar la comunicación CANopen completa en el gateway.

## 🎯 Objetivos

- [ ] Investigar especificación CANopen del R13 F desde documentación disponible
- [ ] Crear archivo `.eds` con Object Dictionary completo
- [ ] Definir objetos obligatorios CiA 301 (Device Type, Error Register, Identity)
- [ ] Definir objetos CiA 402 (Control Word, Status Word, Modes of Operation)
- [ ] Configurar mapeos PDO para comunicación en tiempo real
- [ ] Documentar cada objeto y su propósito
- [ ] Validar EDS con el gateway BL335
- [ ] Probar con simulador R13 F

## 📚 Referencias de Documentación

### Documentos del Proyecto
- `docs/RECEPTOR K13 F.md` - Especificaciones del receptor
- `docs/EMISOR IK3.md` - Especificaciones del emisor
- `docs/BC292382016572en-000201.md` - Documentación técnica
- `docs/research/k13_investigation.md` - Investigación del protocolo

### Estándares CANopen
- **CiA 301**: Application layer and communication profile
- **CiA 402**: CANopen device profile for drives and motion control
- **CiA 305**: Layer Setting Services and Protocol (LSS)

### Objetos Clave a Implementar

#### 1. Objetos Obligatorios (CiA 301)
```
0x1000 - Device Type
0x1001 - Error Register
0x1005 - COB-ID SYNC message
0x1014 - COB-ID EMCY
0x1017 - Producer Heartbeat Time
0x1018 - Identity Object
  - 0x01: Vendor ID (Danfoss = 0x57)
  - 0x02: Product Code
  - 0x03: Revision Number
  - 0x04: Serial Number
```

#### 2. Objetos CiA 402 (Drive Profile)
```
0x6040 - Control Word (16 bits)
0x6041 - Status Word (16 bits)
0x6060 - Modes of Operation
0x6061 - Modes of Operation Display
0x6064 - Position Actual Value (32 bits)
0x606C - Velocity Actual Value (32 bits)
0x6077 - Torque Actual Value (16 bits)
0x6081 - Profile Velocity (32 bits)
0x607A - Target Position (32 bits)
0x60FF - Target Velocity (32 bits)
```

#### 3. PDO Configuration
```
0x1400-0x1403 - RPDO Communication Parameters
0x1600-0x1603 - RPDO Mapping Parameters
0x1800-0x1803 - TPDO Communication Parameters
0x1A00-0x1A03 - TPDO Mapping Parameters
```

#### 4. SDO Configuration
```
0x1200 - SDO Server Parameters
```

## 🏗️ Estructura del Archivo EDS

```ini
[DeviceInfo]
VendorName=Danfoss
VendorNumber=0x00000057
ProductName=R13 F CANopen Receiver
ProductNumber=0x????????  ; A determinar
RevisionNumber=0x00010001
OrderCode=R13 F
BaudRate_10=1
BaudRate_20=1
BaudRate_50=1
BaudRate_125=1
BaudRate_250=1
BaudRate_500=1
BaudRate_800=0
BaudRate_1000=0
SimpleBootUpMaster=0
SimpleBootUpSlave=1
Granularity=8
CompactPDO=0x00
GroupMessaging=0
Features=0
LSS_Supported=1

[DummyUsage]
Dummy0001=0
Dummy0002=0
Dummy0003=0
Dummy0004=0
Dummy0005=1
Dummy0006=1
Dummy0007=1

[MandatoryObjects]
SupportedObjects=3
1=0x1000
2=0x1001
3=0x1018

[1000]
ParameterName=Device Type
ObjectType=0x7
DataType=0x0007
AccessType=ro
DefaultValue=0x00020192
PDOMapping=0

[6040]
ParameterName=Controlword
ObjectType=0x7
DataType=0x0005
AccessType=rw
DefaultValue=0x0000
PDOMapping=1

[6041]
ParameterName=Statusword
ObjectType=0x7
DataType=0x0005
AccessType=ro
DefaultValue=0x0000
PDOMapping=1

; ... más objetos ...
```

## ✅ Criterios de Aceptación

- [ ] Archivo `config/danfoss_r13f.eds` creado
- [ ] Incluye todos los objetos obligatorios de CiA 301
- [ ] Incluye objetos principales de CiA 402
- [ ] PDO mappings configurados (mínimo RPDO1, TPDO1)
- [ ] Comentarios explicativos en cada sección
- [ ] Archivo valida con herramientas EDS (ej: CANopen Magic)
- [ ] Gateway carga el EDS sin errores
- [ ] Tests E2E pasan usando el EDS
- [ ] Documentación actualizada con instrucciones de uso

## 🔧 Tareas Técnicas

### Fase 1: Investigación (2-4 horas)
- [ ] Revisar documentación técnica del R13 F disponible
- [ ] Identificar objetos CANopen mencionados en manuales
- [ ] Consultar con Danfoss para EDS oficial (email/soporte)
- [ ] Revisar implementaciones similares de otros receptores radio

### Fase 2: Implementación (4-6 horas)
- [ ] Crear estructura básica del EDS
- [ ] Implementar sección [DeviceInfo]
- [ ] Implementar objetos obligatorios
- [ ] Implementar objetos CiA 402
- [ ] Configurar PDO mappings
- [ ] Añadir manufacturer-specific objects si aplica

### Fase 3: Validación (2-3 horas)
- [ ] Validar sintaxis con parser EDS
- [ ] Probar carga en gateway BL335
- [ ] Ejecutar tests unitarios
- [ ] Ejecutar tests E2E
- [ ] Verificar comunicación con simulador

### Fase 4: Documentación (1-2 horas)
- [ ] Documentar cada objeto y su uso
- [ ] Crear guía de carga del EDS
- [ ] Actualizar README con información del EDS
- [ ] Añadir ejemplos de uso

## 📝 Notas Adicionales

### Información del R13 F conocida
- **Fabricante**: Danfoss (Vendor ID: 0x57)
- **Modelo**: R13 F (Receiver Radio para puente grúa)
- **Protocolo**: CANopen + Radio propietario
- **Baud rate**: 250 kbps típico
- **Node ID**: Configurable (default: 1)

### Objetos Críticos para Nuestro Proyecto
1. **Control Word (0x6040)**: Para comandos de control
2. **Status Word (0x6041)**: Para leer estado
3. **Emergency Stop**: Comando de parada inmediata
4. **Velocity Control**: Control de velocidad del puente grúa

### Alternativas si no hay EDS oficial
1. **Crear EDS mínimo funcional** con objetos esenciales
2. **Ingeniería inversa** mediante sniffing del bus CAN
3. **Contactar distribuidor Danfoss** en Chile para soporte técnico

## 🔗 Enlaces Relacionados

- **CiA Standards**: https://www.can-cia.org/standardization/specifications/
- **Danfoss Website**: https://www.danfoss.com/
- **CANopen EDS Editor**: https://www.systec-electronic.com/en/products/software/canopen-eds-editor
- **Online EDS Validator**: https://www.canopen-solutions.com/english/tools/eds_check.html

## 🚀 Impacto Esperado

Con el EDS implementado:
- ✅ Gateway funcionará con hardware real del R13 F
- ✅ Tests E2E pasarán completamente (actualmente 4/7)
- ✅ Botones de la Web UI funcionarán correctamente
- ✅ Comunicación PDO/SDO totalmente operativa
- ✅ Preparación para integración con sistema real de puente grúa

## 💡 Próximos Pasos Después del EDS

1. Calibración con hardware real
2. Ajuste de parámetros de comunicación
3. Pruebas de latencia y rendimiento
4. Integración con sistemas PLC
5. Certificación de seguridad industrial

---

**Prioridad**: 🔴 Alta  
**Complejidad**: ⚙️ Media  
**Tiempo estimado**: 10-15 horas  
**Bloqueante para**: Tests E2E completos, operación con hardware real
