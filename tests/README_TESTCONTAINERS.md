# Testing con Testcontainers 🐳

## ¿Por qué Testcontainers?

El proyecto K13 requiere **SocketCAN** (Linux específico) para comunicación CAN. Testcontainers nos permite:

✅ **Desarrollar en cualquier plataforma** (macOS, Windows, Linux)  
✅ **Tests reproducibles** con ambiente Linux real  
✅ **No contaminar el sistema** host  
✅ **CI/CD listo** desde el día 1

## Quick Start

### 1. Requisitos Previos

```bash
# Docker Desktop debe estar instalado y corriendo
docker --version  # Verificar instalación
```

### 2. Instalar Dependencias

```bash
# Activar entorno virtual
source .venv/bin/activate  # macOS/Linux
# o
.venv\Scripts\activate     # Windows

# Instalar testcontainers
pip install testcontainers
```

### 3. Construir Imagen de Testing

```bash
# Construir imagen Docker con SocketCAN
docker build -f Dockerfile.test -t k13-test:latest .
```

### 4. Ejecutar Tests

```bash
# Tests unitarios (rápidos, sin Docker)
pytest tests/unit/ -v

# Tests de integración (con Testcontainers)
pytest tests/integration/ -v -m integration

# Tests completos
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html
```

## Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidos (Testcontainers)
│
├── unit/                    # Tests unitarios
│   ├── test_protocol.py     # - Sin Docker
│   └── test_utils.py        # - Rápidos
│                            # - Lógica pura
│
├── integration/             # Tests de integración
│   ├── test_bl335_gateway.py   # - Con Testcontainers
│   ├── test_can_comm.py        # - SocketCAN real
│   └── test_tcp_server.py      # - Ambiente Linux
│
└── e2e/                     # Tests end-to-end
    └── test_full_system.py  # - Sistema completo
                             # - Gateway + Simulator
```

## Uso de Fixtures

### Fixture: `bl335_container`

Container con BL335 Gateway corriendo:

```python
@pytest.mark.integration
def test_gateway_status(gateway_client):
    """Test conexión al gateway en container"""
    sock, host, port = gateway_client
    
    # Enviar comando
    command = json.dumps({'command': 'get_status'})
    sock.send(command.encode())
    
    # Recibir respuesta
    response = json.loads(sock.recv(4096).decode())
    
    assert response['status'] == 'ok'
    assert response['connected'] is True
```

### Fixture: `gateway_client`

Socket TCP pre-conectado al gateway:

```python
@pytest.mark.integration
def test_emergency_stop(gateway_client):
    sock, host, port = gateway_client
    
    command = json.dumps({'command': 'emergency_stop'})
    sock.send(command.encode())
    
    response = json.loads(sock.recv(4096).decode())
    assert 'status' in response
```

### Fixture: `k13_simulator_container`

Simulador K13 F corriendo en container:

```python
@pytest.mark.e2e
def test_full_system(bl335_container, k13_simulator_container):
    """Test sistema completo: Gateway + Simulador"""
    # Ambos containers corriendo y comunicándose
    # ...
```

## Markers de Pytest

Organizamos tests con markers:

```python
@pytest.mark.unit
def test_parse_message():
    """Test rápido sin Docker"""
    pass

@pytest.mark.integration
def test_can_communication(bl335_container):
    """Test con Testcontainers"""
    pass

@pytest.mark.e2e
@pytest.mark.slow
def test_complete_workflow():
    """Test completo del sistema"""
    pass
```

### Ejecutar por Marker

```bash
# Solo tests unitarios
pytest -m unit -v

# Solo tests de integración
pytest -m integration -v

# Excluir tests lentos
pytest -m "not slow" -v
```

## Docker Compose para Tests

Para tests complejos con múltiples servicios:

```bash
# Levantar stack completo
docker-compose -f docker-compose.test.yml up -d

# Ver logs
docker-compose -f docker-compose.test.yml logs -f

# Ejecutar tests contra stack
pytest tests/e2e/ -v

# Limpiar
docker-compose -f docker-compose.test.yml down -v
```

## Troubleshooting

### Error: "Cannot connect to Docker daemon"

```bash
# Verificar que Docker Desktop esté corriendo
docker ps

# En macOS/Windows: Reiniciar Docker Desktop
```

### Error: "Image not found"

```bash
# Reconstruir imagen
docker build -f Dockerfile.test -t k13-test:latest .

# Verificar imagen
docker images | grep k13-test
```

### Error: "Container start timeout"

```bash
# Ver logs del container
docker logs <container_id>

# Aumentar timeout en conftest.py
# max_retries = 60  # En lugar de 30
```

### Tests lentos

```bash
# Reusar containers entre tests (scope="session" en conftest.py)
# Ya configurado por defecto

# Verificar que imagen esté en cache
docker images

# Limpiar containers huérfanos
docker system prune -f
```

## CI/CD con GitHub Actions

Los tests se ejecutan automáticamente en CI:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src
```

## Comandos Útiles

```bash
# Ver containers activos
docker ps

# Ver logs de un container específico
docker logs <container_id> -f

# Entrar a un container corriendo
docker exec -it <container_id> bash

# Verificar vcan0 dentro del container
docker exec <container_id> ip link show vcan0

# Limpiar todo
docker system prune -a -f --volumes
```

## Debugging Tests

### Ver logs del container durante test

```python
@pytest.mark.integration
def test_with_logs(bl335_container):
    # ... test code ...
    
    # Si falla, ver logs
    logs = bl335_container.get_logs()
    print(logs[0].decode('utf-8'))
```

### Mantener container vivo después del test

```python
@pytest.fixture
def debug_container(docker_image_built):
    container = DockerContainer("k13-test:latest")
    container.start()
    
    # No hacer cleanup automático
    yield container
    
    # Comentar esto para debugging
    # container.stop()
```

Luego conectarse manualmente:

```bash
docker ps  # Ver container ID
docker exec -it <container_id> bash
```

## Best Practices

1. **Tests unitarios primero**: Escribe tests sin Docker cuando sea posible
2. **Scope session**: Reutiliza containers entre tests (ya configurado)
3. **Cleanup automático**: Testcontainers limpia solo
4. **Timeouts razonables**: Configura timeouts para evitar tests colgados
5. **Logs útiles**: Imprime logs del container si falla un test
6. **Markers claros**: Usa markers para organizar tests

## Performance

| Tipo | Tiempo | Docker | Uso |
|------|--------|--------|-----|
| Unit | ~0.1s | ❌ No | Desarrollo continuo |
| Integration | ~5s | ✅ Sí | Pre-commit, CI |
| E2E | ~15s | ✅ Sí | Pre-push, releases |

## Referencias

- [Testcontainers Python Docs](https://testcontainers-python.readthedocs.io/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Docker CAN Utils](https://github.com/linux-can/can-utils)

## Soporte

¿Problemas? Revisa:

1. ✅ Docker Desktop corriendo
2. ✅ Imagen construida: `docker images | grep k13-test`
3. ✅ Tests unitarios funcionan: `pytest tests/unit/ -v`
4. ✅ Logs del container: `docker logs <container_id>`

Si persiste el problema, abre un issue en GitHub.
