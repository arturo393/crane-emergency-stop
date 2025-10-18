"""
Test End-to-End del Sistema Integrado
Prueba: Cliente TCP → Gateway BL335 → Simulador R13 F
"""

import pytest
import time
import socket
import json
import sys
import os

# Añadir rutas al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.bl335_gateway.simulator_adapter import IntegratedSystem


class TestEndToEnd:
    """Tests de integración end-to-end"""
    
    @pytest.fixture(scope="class")
    def integrated_system(self):
        """
        Fixture que inicia el sistema integrado completo
        y lo mantiene vivo durante todos los tests de la clase
        """
        print("\n🚀 Iniciando sistema integrado...")
        system = IntegratedSystem(node_id=1, tcp_port=19999)  # Puerto diferente para tests
        
        if not system.start():
            pytest.fail("No se pudo iniciar el sistema integrado")
        
        # Dar tiempo para que todo se estabilice
        time.sleep(2)
        
        yield system
        
        print("\n⏹️  Deteniendo sistema integrado...")
        system.stop()
    
    def test_01_system_startup(self, integrated_system):
        """Test 1: Verificar que el sistema inicie correctamente"""
        status = integrated_system.get_status()
        
        # Verificar que el simulador está funcionando
        assert status['simulator'] is not None
        assert status['simulator']['device_state'] == 'SWITCH_ON_DISABLED'
        
        # Verificar que el gateway está conectado
        assert status['gateway'] is not None
        assert status['gateway']['connected'] == True
        
        # Verificar que el bridge está activo
        assert status['bridge'] is not None
        assert status['bridge']['running'] == True
        
        print("✅ Sistema iniciado correctamente")
    
    def test_02_tcp_connection(self, integrated_system):
        """Test 2: Verificar conexión TCP al gateway"""
        # Conectar vía TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            sock.connect(('localhost', 19999))
            print("✅ Conexión TCP establecida")
        except Exception as e:
            pytest.fail(f"No se pudo conectar al gateway: {e}")
        finally:
            sock.close()
    
    def test_03_get_status_command(self, integrated_system):
        """Test 3: Comando get_status vía TCP"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            sock.connect(('localhost', 19999))
            
            # Enviar comando get_status
            command = {'command': 'get_status'}
            sock.send(json.dumps(command).encode('utf-8'))
            
            # Recibir respuesta
            response_data = sock.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            
            # Verificar respuesta
            assert response['status'] == 'ok'
            assert response['connected'] == True
            assert response['node_id'] == 1
            
            print(f"✅ Status recibido: {response['system_state']}")
        
        except Exception as e:
            pytest.fail(f"Error en comando get_status: {e}")
        
        finally:
            sock.close()
    
    def test_04_emergency_stop_command(self, integrated_system):
        """Test 4: Comando de parada de emergencia"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            sock.connect(('localhost', 19999))
            
            # Estado inicial
            status_before = integrated_system.get_status()
            initial_state = status_before['simulator']['device_state']
            print(f"   Estado inicial: {initial_state}")
            
            # Enviar comando emergency_stop
            command = {'command': 'emergency_stop'}
            sock.send(json.dumps(command).encode('utf-8'))
            
            # Recibir respuesta
            response_data = sock.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            
            # Verificar respuesta
            assert response['status'] == 'ok'
            print(f"✅ Emergency stop ejecutado: {response['message']}")
            
            # Dar tiempo para que el estado cambie
            time.sleep(0.5)
            
            # Verificar que el estado cambió
            status_after = integrated_system.get_status()
            final_state = status_after['simulator']['device_state']
            print(f"   Estado final: {final_state}")
            
            # El simulador debería estar en QUICK_STOP_ACTIVE
            assert final_state == 'QUICK_STOP_ACTIVE'
        
        except Exception as e:
            pytest.fail(f"Error en emergency stop: {e}")
        
        finally:
            sock.close()
    
    def test_05_pdo_communication(self, integrated_system):
        """Test 5: Comunicación PDO (Process Data Objects)"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            sock.connect(('localhost', 19999))
            
            # Leer TPDO1 (Status Word, Velocity, Position)
            command = {'command': 'pdo_read', 'pdo_number': 1}
            sock.send(json.dumps(command).encode('utf-8'))
            
            response_data = sock.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            
            assert response['status'] == 'ok'
            assert response['pdo_number'] == 1
            assert 'data' in response
            
            print(f"✅ TPDO1 leído: {response['data_hex']}")
            print(f"   COB-ID: 0x{response['cob_id']:03X}")
        
        except Exception as e:
            pytest.fail(f"Error en comunicación PDO: {e}")
        
        finally:
            sock.close()
    
    def test_06_state_transitions(self, integrated_system):
        """Test 6: Transiciones de estado CiA 402"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            sock.connect(('localhost', 19999))
            
            # Estado inicial
            status = integrated_system.get_status()
            initial_state = status['simulator']['device_state']
            print(f"   Estado inicial: {initial_state}")
            
            # Transición 1: SWITCH_ON_DISABLED → READY_TO_SWITCH_ON
            # Control Word = 0x0007 (Switch On + Enable Voltage + Quick Stop)
            command = {
                'command': 'pdo_write',
                'pdo_number': 1,
                'data': '07000000'  # Control Word 0x0007 en little-endian
            }
            sock.send(json.dumps(command).encode('utf-8'))
            response_data = sock.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            assert response['status'] == 'ok'
            
            time.sleep(0.3)  # Dar tiempo para transición
            
            status = integrated_system.get_status()
            state_1 = status['simulator']['device_state']
            print(f"   Después 0x0007: {state_1}")
            assert state_1 == 'READY_TO_SWITCH_ON'
            
            # Transición 2: READY_TO_SWITCH_ON → OPERATION_ENABLED
            # Control Word = 0x000F (+ Enable Operation)
            command = {
                'command': 'pdo_write',
                'pdo_number': 1,
                'data': '0F000000'  # Control Word 0x000F
            }
            sock.send(json.dumps(command).encode('utf-8'))
            response_data = sock.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            assert response['status'] == 'ok'
            
            time.sleep(0.3)
            
            status = integrated_system.get_status()
            state_2 = status['simulator']['device_state']
            print(f"   Después 0x000F: {state_2}")
            assert state_2 == 'OPERATION_ENABLED'
            
            print("✅ Transiciones de estado correctas")
        
        except Exception as e:
            pytest.fail(f"Error en transiciones de estado: {e}")
        
        finally:
            sock.close()
    
    def test_07_performance(self, integrated_system):
        """Test 7: Performance y latencia"""
        import statistics
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            sock.connect(('localhost', 19999))
            
            latencies = []
            num_requests = 50
            
            print(f"   Enviando {num_requests} comandos get_status...")
            
            for i in range(num_requests):
                start = time.time()
                
                command = {'command': 'get_status'}
                sock.send(json.dumps(command).encode('utf-8'))
                
                response_data = sock.recv(4096)
                response = json.loads(response_data.decode('utf-8'))
                
                end = time.time()
                latency_ms = (end - start) * 1000
                latencies.append(latency_ms)
                
                assert response['status'] == 'ok'
            
            # Calcular estadísticas
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18]  # P95
            
            print(f"✅ Performance test completado:")
            print(f"   • Latencia promedio: {avg_latency:.2f} ms")
            print(f"   • Latencia mínima: {min_latency:.2f} ms")
            print(f"   • Latencia máxima: {max_latency:.2f} ms")
            print(f"   • Latencia P95: {p95_latency:.2f} ms")
            
            # Verificar que la latencia promedio es razonable (<100ms)
            assert avg_latency < 100, f"Latencia demasiado alta: {avg_latency:.2f} ms"
        
        except Exception as e:
            pytest.fail(f"Error en test de performance: {e}")
        
        finally:
            sock.close()


def run_all_tests():
    """Ejecutar todos los tests manualmente (sin pytest)"""
    print("=" * 70)
    print("🧪 TEST SUITE E2E - Sistema Integrado")
    print("=" * 70)
    
    # Iniciar sistema
    print("\n🚀 Iniciando sistema integrado...")
    system = IntegratedSystem(node_id=1, tcp_port=19999)
    
    if not system.start():
        print("❌ Error iniciando sistema")
        return False
    
    time.sleep(2)
    
    try:
        # Test 1
        print("\n" + "=" * 70)
        print("TEST 1: Verificar startup del sistema")
        print("=" * 70)
        status = system.get_status()
        assert status['simulator']['device_state'] == 'SWITCH_ON_DISABLED'
        assert status['gateway']['connected'] == True
        assert status['bridge']['running'] == True
        print("✅ PASSED")
        
        # Test 2
        print("\n" + "=" * 70)
        print("TEST 2: Conexión TCP")
        print("=" * 70)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 19999))
        sock.close()
        print("✅ PASSED")
        
        # Test 3
        print("\n" + "=" * 70)
        print("TEST 3: Comando get_status")
        print("=" * 70)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 19999))
        command = {'command': 'get_status'}
        sock.send(json.dumps(command).encode('utf-8'))
        response_data = sock.recv(4096)
        response = json.loads(response_data.decode('utf-8'))
        assert response['status'] == 'ok'
        sock.close()
        print("✅ PASSED")
        
        # Test 4
        print("\n" + "=" * 70)
        print("TEST 4: Emergency Stop")
        print("=" * 70)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 19999))
        command = {'command': 'emergency_stop'}
        sock.send(json.dumps(command).encode('utf-8'))
        response_data = sock.recv(4096)
        response = json.loads(response_data.decode('utf-8'))
        assert response['status'] == 'ok'
        time.sleep(0.5)
        status = system.get_status()
        assert status['simulator']['device_state'] == 'QUICK_STOP_ACTIVE'
        sock.close()
        print("✅ PASSED")
        
        print("\n" + "=" * 70)
        print("🎉 TODOS LOS TESTS PASARON")
        print("=" * 70)
        
        return True
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n⏹️  Deteniendo sistema...")
        system.stop()


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
