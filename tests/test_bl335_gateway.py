"""
Tests para BL335 Gateway

Pruebas unitarias usando canal virtual CAN (vcan0)

NOTA: Estos tests requieren Linux con SocketCAN.
En macOS se ejecutarán tests básicos sin inicialización completa.
"""

import pytest
import json
import socket
import time
import sys
from src.bl335_gateway.main import BL335Gateway


# Skip tests que requieren SocketCAN en macOS
requires_socketcan = pytest.mark.skipif(
    sys.platform == 'darwin',
    reason="SocketCAN solo disponible en Linux"
)


@pytest.fixture
def gateway():
    """Fixture que crea gateway con canal virtual"""
    if sys.platform == 'darwin':
        pytest.skip("SocketCAN no disponible en macOS")
    
    gw = BL335Gateway(can_channel='vcan0', node_id=1, tcp_port=19999, can_interface='virtual')
    
    # Iniciar gateway
    try:
        gw.start()
        yield gw
    finally:
        gw.stop()


def test_gateway_initialization():
    """Test: Inicialización del gateway"""
    gw = BL335Gateway(can_channel='vcan0', node_id=1, tcp_port=19999, can_interface='virtual')
    
    assert gw.can_channel == 'vcan0'
    assert gw.can_interface == 'virtual'
    assert gw.node_id == 1
    assert gw.tcp_port == 19999
    assert gw.connected is False


def test_gateway_start_stop(gateway):
    """Test: Iniciar y detener gateway"""
    assert gateway.connected is True
    assert gateway.network is not None
    assert gateway.k13_node is not None
    
    gateway.stop()
    assert gateway.connected is False


def test_tcp_server_connection(gateway):
    """Test: Conexión al servidor TCP"""
    time.sleep(0.5)  # Esperar inicialización
    
    # Conectar cliente
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 19999))
    
    # Enviar comando
    command = {'command': 'get_status'}
    client.send(json.dumps(command).encode('utf-8'))
    
    # Recibir respuesta
    response = client.recv(4096)
    data = json.loads(response.decode('utf-8'))
    
    assert data['status'] == 'ok'
    assert data['connected'] is True
    assert data['can_channel'] == 'vcan0'
    
    client.close()


def test_get_status_command(gateway):
    """Test: Comando get_status"""
    time.sleep(0.5)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 19999))
    
    command = {'command': 'get_status'}
    client.send(json.dumps(command).encode('utf-8'))
    
    response = client.recv(4096)
    data = json.loads(response.decode('utf-8'))
    
    assert 'status' in data
    assert 'connected' in data
    assert 'node_id' in data
    assert data['node_id'] == 1
    
    client.close()


def test_emergency_stop_command(gateway):
    """Test: Comando emergency_stop"""
    time.sleep(0.5)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 19999))
    
    command = {'command': 'emergency_stop'}
    client.send(json.dumps(command).encode('utf-8'))
    
    response = client.recv(4096)
    data = json.loads(response.decode('utf-8'))
    
    assert 'status' in data
    assert 'message' in data
    
    client.close()


def test_reset_command(gateway):
    """Test: Comando reset"""
    time.sleep(0.5)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 19999))
    
    command = {'command': 'reset'}
    client.send(json.dumps(command).encode('utf-8'))
    
    response = client.recv(4096)
    data = json.loads(response.decode('utf-8'))
    
    assert 'status' in data
    
    client.close()


def test_invalid_command(gateway):
    """Test: Comando inválido"""
    time.sleep(0.5)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 19999))
    
    command = {'command': 'invalid_cmd'}
    client.send(json.dumps(command).encode('utf-8'))
    
    response = client.recv(4096)
    data = json.loads(response.decode('utf-8'))
    
    assert 'error' in data
    assert 'Unknown command' in data['error']
    
    client.close()


def test_invalid_json(gateway):
    """Test: JSON inválido"""
    time.sleep(0.5)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 19999))
    
    # Enviar JSON inválido
    client.send(b'{"invalid json')
    
    response = client.recv(4096)
    data = json.loads(response.decode('utf-8'))
    
    assert 'error' in data
    assert 'Invalid JSON' in data['error']
    
    client.close()


def test_multiple_clients(gateway):
    """Test: Múltiples clientes simultáneos"""
    time.sleep(0.5)
    
    clients = []
    
    # Conectar 3 clientes
    for i in range(3):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 19999))
        clients.append(client)
    
    # Enviar comandos
    for client in clients:
        command = {'command': 'get_status'}
        client.send(json.dumps(command).encode('utf-8'))
    
    # Recibir respuestas
    for client in clients:
        response = client.recv(4096)
        data = json.loads(response.decode('utf-8'))
        assert data['status'] == 'ok'
    
    # Cerrar clientes
    for client in clients:
        client.close()


def test_process_command_direct():
    """Test: Procesar comando directamente"""
    gw = BL335Gateway(can_channel='vcan0', node_id=1, tcp_port=19999, can_interface='virtual')
    
    # Test get_status
    response = gw._process_command({'command': 'get_status'})
    assert 'status' in response
    
    # Test comando desconocido
    response = gw._process_command({'command': 'unknown'})
    assert 'error' in response


@pytest.mark.skipif(True, reason="Requiere simulador K13 corriendo")
def test_sdo_read_write():
    """Test: Lectura/escritura SDO (requiere simulador)"""
    gw = BL335Gateway(can_channel='vcan0', node_id=1, tcp_port=19999, can_interface='virtual')
    gw.start()
    
    time.sleep(1)  # Esperar inicialización
    
    # Test SDO read
    response = gw.sdo_read(0x1000, 0)
    assert 'status' in response
    
    # Test SDO write
    response = gw.sdo_write(0x1017, 0, 500)
    assert 'status' in response
    
    gw.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
