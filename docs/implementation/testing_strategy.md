# Estrategia de Testing con Testcontainers

## Problema a Resolver

El proyecto K13 requiere testing de comunicaciones CAN usando SocketCAN, que es específico de Linux. Esto presenta desafíos:

- ❌ macOS no soporta SocketCAN nativamente
- ❌ Windows no soporta SocketCAN
- ❌ Tests fallan en ambiente de desarrollo local
- ❌ CI/CD requiere configuración especial

## Solución: Testcontainers

Usar **Testcontainers** para ejecutar contenedores Docker con Linux durante los tests.

### Ventajas

✅ **Multi-plataforma**: Funciona en macOS, Windows y Linux  
✅ **Ambiente real**: Container Linux con SocketCAN configurado  
✅ **Aislamiento**: No modifica el sistema host  
✅ **CI/CD ready**: Compatible con GitHub Actions, GitLab CI  
✅ **Reproducible**: Mismo ambiente en todos lados  
✅ **Cleanup automático**: Containers se eliminan al terminar tests

## Arquitectura de Testing

```
┌─────────────────────────────────────────────────┐
│  Host (macOS / Windows / Linux)                 │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │  Pytest + Testcontainers                  │  │
│  │                                            │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │  Docker Container (Linux)            │ │  │
│  │  │                                       │ │  │
│  │  │  ┌────────────────────────────────┐  │ │  │
│  │  │  │  BL335 Gateway Process         │  │ │  │
│  │  │  │  - python-canopen              │  │ │  │
│  │  │  │  - SocketCAN (vcan0)           │  │ │  │
│  │  │  │  - TCP Server (9999)           │  │ │  │
│  │  │  └────────────────────────────────┘  │ │  │
│  │  │                                       │ │  │
│  │  │  ┌────────────────────────────────┐  │ │  │
│  │  │  │  K13 Simulator Process         │  │ │  │
│  │  │  │  - Virtual CAN device          │  │ │  │
│  │  │  │  - CANopen heartbeat           │  │ │  │
│  │  │  └────────────────────────────────┘  │ │  │
│  │  │                                       │ │  │
│  │  │  Port Mapping: 9999 -> Host          │ │  │
│  │  └───────────────────────────────────────┘ │  │
│  │                                            │  │
│  │  Test assertions & validations            │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Implementación

### 1. Dependencias

```bash
pip install testcontainers[docker]
```

### 2. Dockerfile para Testing

Crear imagen Docker con:
- Ubuntu/Debian base
- Python 3.12
- SocketCAN kernel modules
- python-canopen, python-can
- Nuestro código BL335 Gateway

### 3. Fixtures de Pytest

```python
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_strategies import Wait

@pytest.fixture(scope="session")
def bl335_container():
    """Container Linux con BL335 Gateway y vcan0"""
    container = (
        DockerContainer("bl335-gateway:test")
        .with_exposed_ports(9999)
        .with_env("CAN_INTERFACE", "vcan0")
        .with_command("python /app/main.py")
    )
    
    container.start()
    yield container
    container.stop()
```

### 4. Tests

```python
def test_bl335_gateway_tcp(bl335_container):
    """Test conexión TCP al gateway en container"""
    host = bl335_container.get_container_host_ip()
    port = bl335_container.get_exposed_port(9999)
    
    # Conectar y probar
    sock = socket.socket()
    sock.connect((host, port))
    # ... assertions
```

## Tipos de Tests

### Tests Unitarios (Sin Container)

- Lógica de negocio pura
- Parsing de protocolos
- Validaciones
- **Rápidos, no requieren Docker**

### Tests de Integración (Con Container)

- Comunicación CAN real
- Servidor TCP
- Protocolo CANopen end-to-end
- **Requieren Testcontainers**

### Tests E2E (Con Múltiples Containers)

- Gateway + Simulador K13 + Cliente Monitor
- **Orquestación completa**

## Configuración del Container

### Dockerfile de Testing

```dockerfile
FROM python:3.12-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    iproute2 \
    can-utils \
    linux-modules-extra-$(uname -r) || true \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar código
COPY src/ /app/src/
COPY tools/ /app/tools/

WORKDIR /app

# Script de inicialización CAN
RUN echo '#!/bin/bash\n\
modprobe vcan || true\n\
ip link add dev vcan0 type vcan || true\n\
ip link set up vcan0\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "src/bl335_gateway/main.py", "--can", "vcan0"]
```

### docker-compose.yml (Alternativa)

```yaml
version: '3.8'

services:
  bl335-gateway:
    build:
      context: .
      dockerfile: Dockerfile.test
    ports:
      - "9999:9999"
    environment:
      - CAN_INTERFACE=vcan0
    cap_add:
      - NET_ADMIN
    privileged: true
    
  k13-simulator:
    build:
      context: .
      dockerfile: Dockerfile.test
    command: python tools/can_simulator.py
    environment:
      - CAN_INTERFACE=vcan0
    cap_add:
      - NET_ADMIN
    privileged: true
```

## Estructura de Archivos

```
puente_grua/
├── Dockerfile.test              # Dockerfile para testing
├── docker-compose.test.yml      # Compose para tests
├── tests/
│   ├── conftest.py             # Fixtures compartidos
│   ├── unit/                   # Tests sin container
│   │   ├── test_protocol.py
│   │   └── test_utils.py
│   ├── integration/            # Tests con container
│   │   ├── test_bl335_gateway.py
│   │   ├── test_can_communication.py
│   │   └── test_tcp_server.py
│   └── e2e/                    # Tests end-to-end
│       └── test_full_system.py
```

## Comandos

### Ejecutar Tests Localmente

```bash
# Tests unitarios (rápidos, sin Docker)
pytest tests/unit/ -v

# Tests de integración (con Testcontainers)
pytest tests/integration/ -v

# Tests completos
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html
```

### CI/CD (GitHub Actions)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      docker:
        image: docker:dind
        
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install testcontainers[docker]
    
    - name: Run unit tests
      run: pytest tests/unit/ -v
    
    - name: Run integration tests
      run: pytest tests/integration/ -v
```

## Ventajas Específicas para K13

1. **Testing pre-hardware**: Podemos desarrollar y probar todo antes de recibir el K13 F
2. **Simulación realista**: SocketCAN virtual se comporta como el real
3. **Debugging fácil**: Logs del container accesibles
4. **Desarrollo paralelo**: Múltiples devs pueden trabajar sin interferir
5. **Validación CI/CD**: Pull requests se validan automáticamente

## Próximos Pasos

1. ✅ Instalar testcontainers
2. ✅ Crear Dockerfile.test
3. ✅ Reorganizar tests en unit/integration/e2e
4. ✅ Implementar fixtures con containers
5. ✅ Configurar GitHub Actions
6. ✅ Documentar uso para equipo

## Referencias

- [Testcontainers Python](https://testcontainers-python.readthedocs.io/)
- [Docker CAN Support](https://www.kernel.org/doc/html/latest/networking/can.html)
- [pytest-docker-compose](https://github.com/pytest-docker-compose/pytest-docker-compose)

## Alternativas Consideradas

| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| Mock completo | Rápido | No prueba CAN real | ❌ No |
| VM Linux local | Control total | Setup manual complicado | ❌ No |
| CI/CD solo | Gratis | No testing local | ❌ No |
| **Testcontainers** | ✅ Multi-plataforma<br>✅ Real<br>✅ Fácil | Requiere Docker | ✅ **Seleccionado** |

## Estimación

- **Setup inicial**: 2-3 horas
- **Migración de tests**: 1-2 horas
- **Documentación**: 1 hora
- **Total**: ~4-6 horas

**ROI**: Inversión única que permite desarrollo continuo en cualquier plataforma.
