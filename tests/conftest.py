"""
Pytest Configuration and Shared Fixtures
Tests usando Testcontainers para ambiente Linux con SocketCAN
"""

import pytest
import socket
import time
import sys
from pathlib import Path
from testcontainers.core.container import DockerContainer


# Configuración
PROJECT_ROOT = Path(__file__).parent.parent
DOCKER_IMAGE = "k13-test:latest"


@pytest.fixture(scope="session")
def docker_image_built():
    """
    Fixture que asegura que la imagen Docker de testing esté construida
    
    Esta fixture se ejecuta una vez por sesión de testing.
    Construye la imagen Docker si no existe.
    """
    import subprocess
    
    print("\n🏗️  Verificando imagen Docker para testing...")
    
    try:
        # Verificar si la imagen existe
        result = subprocess.run(
            ["docker", "images", "-q", DOCKER_IMAGE],
            capture_output=True,
            text=True,
            check=True
        )
        
        if not result.stdout.strip():
            print(f"📦 Construyendo imagen {DOCKER_IMAGE}...")
            subprocess.run(
                ["docker", "build", "-f", "Dockerfile.test", "-t", DOCKER_IMAGE, "."],
                cwd=PROJECT_ROOT,
                check=True
            )
            print(f"✅ Imagen {DOCKER_IMAGE} construida")
        else:
            print(f"✅ Imagen {DOCKER_IMAGE} ya existe")
        
        return True
        
    except subprocess.CalledProcessError as e:
        pytest.skip(f"No se pudo construir imagen Docker: {e}")
    except FileNotFoundError:
        pytest.skip("Docker no está instalado o no está en PATH")


@pytest.fixture(scope="session")
def bl335_container(docker_image_built):
    """
    Fixture que proporciona un container con BL335 Gateway corriendo
    
    El container:
    - Tiene SocketCAN (vcan0) configurado
    - Ejecuta BL335 Gateway en puerto 9999
    - Se limpia automáticamente al finalizar
    
    Scope: session (se crea una vez para toda la sesión de tests)
    """
    if sys.platform == 'darwin' or sys.platform == 'win32':
        # En macOS/Windows, necesitamos privilegios para vcan
        privileged = True
    else:
        privileged = False
    
    print(f"\n🚀 Iniciando container BL335 Gateway...")
    
    container = (
        DockerContainer(DOCKER_IMAGE)
        .with_exposed_ports(9999)
        .with_env("CAN_INTERFACE", "vcan0")
        .with_env("PYTHONUNBUFFERED", "1")
        .with_command("python src/bl335_gateway/main.py --can vcan0 --interface virtual --port 9999 --node-id 1")
    )
    
    if privileged:
        container = container.with_kwargs(cap_add=["NET_ADMIN"])
    
    try:
        container.start()
        
        # Esperar a que el servidor TCP esté listo
        host = container.get_container_host_ip()
        port = int(container.get_exposed_port(9999))
        
        print(f"⏳ Esperando a que el servidor TCP esté listo en {host}:{port}...")
        
        max_retries = 30
        for i in range(max_retries):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((host, port))
                sock.close()
                print(f"✅ Container listo en {host}:{port}")
                break
            except (socket.error, ConnectionRefusedError):
                if i == max_retries - 1:
                    logs = container.get_logs()
                    print(f"❌ Container logs:\n{logs[0].decode('utf-8')}")
                    raise TimeoutError(f"Container no respondió después de {max_retries} intentos")
                time.sleep(1)
        
        yield container
        
    finally:
        print("\n🧹 Limpiando container...")
        try:
            container.stop()
        except Exception as e:
            print(f"⚠️  Error deteniendo container: {e}")


@pytest.fixture
def gateway_client(bl335_container):
    """
    Fixture que proporciona un cliente TCP conectado al gateway
    
    Retorna:
        tuple: (socket, host, port)
    """
    host = bl335_container.get_container_host_ip()
    port = int(bl335_container.get_exposed_port(9999))
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        sock.connect((host, port))
        yield sock, host, port
    finally:
        try:
            sock.close()
        except:
            pass


@pytest.fixture(scope="session")
def k13_simulator_container(docker_image_built):
    """
    Fixture que proporciona un container con el simulador K13 F
    
    El simulador:
    - Emula un receptor K13 F en vcan0
    - Envía heartbeats CANopen
    - Responde a comandos NMT y SDO
    """
    print(f"\n🎮 Iniciando container K13 Simulator...")
    
    container = (
        DockerContainer(DOCKER_IMAGE)
        .with_env("CAN_INTERFACE", "vcan0")
        .with_env("PYTHONUNBUFFERED", "1")
        .with_command("python tools/can_simulator.py --channel vcan0 --node-id 1 --verbose")
        .with_kwargs(cap_add=["NET_ADMIN"])
    )
    
    try:
        container.start()
        
        # Dar tiempo al simulador para inicializar
        time.sleep(2)
        
        print("✅ Simulador K13 F iniciado")
        
        yield container
        
    finally:
        print("\n🧹 Limpiando simulador...")
        try:
            container.stop()
        except Exception as e:
            print(f"⚠️  Error deteniendo simulador: {e}")


# Markers para categorizar tests
def pytest_configure(config):
    """Registrar markers personalizados"""
    config.addinivalue_line(
        "markers", "unit: Tests unitarios (rápidos, sin Docker)"
    )
    config.addinivalue_line(
        "markers", "integration: Tests de integración (con Testcontainers)"
    )
    config.addinivalue_line(
        "markers", "e2e: Tests end-to-end (sistema completo)"
    )
    config.addinivalue_line(
        "markers", "slow: Tests lentos"
    )
    config.addinivalue_line(
        "markers", "requires_docker: Tests que requieren Docker"
    )


# Skip automático si Docker no está disponible
def pytest_collection_modifyitems(config, items):
    """
    Modificar items de test según disponibilidad de Docker
    """
    try:
        import subprocess
        subprocess.run(["docker", "info"], capture_output=True, check=True)
        docker_available = True
    except:
        docker_available = False
    
    if not docker_available:
        skip_docker = pytest.mark.skip(reason="Docker no disponible")
        for item in items:
            if "integration" in item.keywords or "e2e" in item.keywords:
                item.add_marker(skip_docker)


@pytest.fixture
def mock_can_message():
    """Fixture que proporciona mensaje CAN de ejemplo para tests unitarios"""
    return {
        'arbitration_id': 0x181,
        'data': [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07],
        'is_extended_id': False,
        'is_error_frame': False,
        'is_remote_frame': False,
        'timestamp': 1234567890.123
    }


@pytest.fixture
def sample_json_command():
    """Fixture que proporciona comandos JSON de ejemplo"""
    def _make_command(cmd_type, **kwargs):
        command = {'command': cmd_type}
        command.update(kwargs)
        return command
    
    return _make_command
