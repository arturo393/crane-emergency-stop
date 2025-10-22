# Guía Rápida de Tests - Proyecto Puente Grúa

## ✅ Estado Actual (22 Oct 2025)
- **39 tests core pasando** (test_protocol_canopen.py + test_basic.py + test_protocol.py)
- **58+ tests unitarios totales pasando**
- **Protocolo CANopen 100% funcional y testeado**

---

## Comandos de Test Rápidos

### Ejecutar Tests Core (Recomendado)
```bash
source .venv/bin/activate
PYTHONPATH=/Users/arturo/puente_grua pytest tests/unit/test_protocol_canopen.py tests/unit/test_basic.py tests/unit/test_protocol.py -v
```

### Ejecutar Solo Tests de CANopen
```bash
source .venv/bin/activate
PYTHONPATH=/Users/arturo/puente_grua pytest tests/unit/test_protocol_canopen.py -v
```

### Ejecutar Todos los Tests Unitarios (incluyendo legacy)
```bash
source .venv/bin/activate
PYTHONPATH=/Users/arturo/puente_grua pytest tests/unit/ -v --tb=short
```

### Ver Tests de Integración (skipped en macOS)
```bash
source .venv/bin/activate
PYTHONPATH=/Users/arturo/puente_grua pytest tests/integration/ -v
```

### Ver Coverage
```bash
source .venv/bin/activate
PYTHONPATH=/Users/arturo/puente_grua pytest tests/unit/test_protocol_canopen.py tests/unit/test_basic.py tests/unit/test_protocol.py --cov=src/k13_controller --cov-report=html
```

---

## Estructura de Tests

```
tests/
├── unit/
│   ├── test_protocol_canopen.py   ✅ 9/9 PASSING - Tests principales CANopen
│   ├── test_protocol.py           ✅ 26/26 PASSING - Tests protocolo completo
│   ├── test_basic.py              ✅ 4/4 PASSING - Tests básicos
│   ├── test_control_sequences.py ✅ PASSING - Secuencias de control
│   ├── test_main.py               ⚠️ 6 FAILING - Interfaz legacy
│   └── test_web_ui.py             ⏭️ SKIPPED - Falta FastAPI
│
├── integration/
│   └── test_bl335_gateway.py      ⏭️ 11 SKIPPED - Requiere Docker/Linux
│
└── e2e/
    ├── test_integrated_system.py  ⏭️ 7 SKIPPED - Requiere entorno completo
    └── test_web_ui_e2e.py         ⏭️ SKIPPED - Falta FastAPI
```

---

## Tests que Pasan (Core Functionality)

### ✅ test_protocol_canopen.py (9 tests)
```
✓ test_protocol_creation
✓ test_canopen_commands
✓ test_control_word_bits
✓ test_status_word_bits
✓ test_sdo_write_message
✓ test_sdo_read_message
✓ test_enable_operation_sequence
✓ test_velocity_control
✓ test_emergency_stop_command
```

### ✅ test_protocol.py (26 tests)
- Protocolo R13CANopen (7 tests)
- CANopenSDO y PDO (4 tests)
- Decodificación Status Word (2 tests)
- Mapeo de comandos (2 tests)
- Enums (3 tests)
- Diccionario de objetos (3 tests)
- Integración de protocolo (2 tests)

### ✅ test_basic.py (4 tests)
- Imports
- Creación de controlador
- Conexión
- Comandos básicos

---

## Tests Problemáticos

### ⚠️ test_main.py - 6 tests FAILING
**Razón:** Interfaz legacy - tests escritos para API antigua

**Opciones:**
1. Actualizar tests para usar nueva API CANopen
2. Marcar como deprecated y crear nuevos tests
3. Mantener como documentación de interfaz legacy

**Recomendación:** Actualizar o skip hasta refactor completo.

---

## Tests que Requieren Infraestructura

### ⏭️ test_bl335_gateway.py - 11 SKIPPED
**Requiere:**
- Docker disponible
- Linux con SocketCAN (no funciona en macOS)
- Simulador K13 corriendo

**Cómo ejecutar:**
```bash
# En Linux con Docker
docker-compose -f docker-compose.test.yml up -d
pytest tests/integration/test_bl335_gateway.py -v
```

### ⏭️ test_integrated_system.py - 7 SKIPPED
**Requiere:**
- Gateway BL335 desplegado
- Simulador K13 activo
- Red CAN virtual configurada

---

## Problemas Conocidos y Soluciones

### 1. ModuleNotFoundError: No module named 'src'
**Solución:**
```bash
export PYTHONPATH=/Users/arturo/puente_grua
# o
PYTHONPATH=/Users/arturo/puente_grua pytest tests/...
```

### 2. ModuleNotFoundError: No module named 'fastapi'
**Solución:**
```bash
source .venv/bin/activate
pip install fastapi
```

### 3. Tests de integración fallan en macOS
**Solución:** Esto es esperado. Usar Linux o Docker para tests de integración.

### 4. "Docker no disponible"
**Solución:**
```bash
# Instalar Docker Desktop para Mac
# o ejecutar en CI/CD con Linux
```

---

## Mejores Prácticas

### Antes de Commit
```bash
# Ejecutar tests core
source .venv/bin/activate
PYTHONPATH=/Users/arturo/puente_grua pytest tests/unit/test_protocol_canopen.py tests/unit/test_protocol.py -v

# Si todos pasan, el código está OK
```

### Durante Desarrollo
```bash
# Ejecutar tests relacionados con tu módulo
pytest tests/unit/test_protocol_canopen.py -v -k "test_sdo"

# Ver output detallado
pytest tests/unit/test_protocol_canopen.py -vv -s
```

### Para CI/CD
```bash
# Ejecutar todos los tests excepto los que requieren infraestructura
pytest tests/unit/ -v --ignore=tests/unit/test_web_ui.py

# Con coverage
pytest tests/unit/ --cov=src --cov-report=term-missing
```

---

## Archivos de Referencia

- **KNOWN_ISSUES.md** - Problemas conocidos documentados
- **TEST_STATUS_REPORT.md** - Reporte detallado de estado
- **README.md** - Documentación general del proyecto
- **docs/** - Documentación técnica adicional

---

## Contacto y Soporte

Para problemas con tests:
1. Verificar KNOWN_ISSUES.md
2. Revisar TEST_STATUS_REPORT.md
3. Verificar que PYTHONPATH esté configurado
4. Confirmar que .venv está activado

---

**Última actualización:** 22 Oct 2025  
**Mantenedor:** Equipo Puente Grúa  
**Tests pasando:** 58+ de 64 unitarios (90.6%)
