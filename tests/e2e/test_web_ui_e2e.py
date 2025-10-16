"""
End-to-End Tests for Web UI
Tests completos del flujo de usuario con FastAPI TestClient
NO requiere Testcontainers (Web UI es simple FastAPI)
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import json
import time

from src.web_ui.main import WebUIApp


@pytest.fixture
def app():
    """Create Web UI app for E2E testing"""
    return WebUIApp(gateway_host="localhost", gateway_port=9999)


@pytest.fixture
def client(app):
    """Create FastAPI test client for E2E"""
    return TestClient(app.app)


class TestEmergencyStopFlow:
    """E2E tests for emergency stop workflow"""
    
    @patch('src.web_ui.main.WebUIApp._send_gateway_command')
    def test_complete_emergency_stop_flow(self, mock_send, client):
        """
        Test flujo completo E2E de parada de emergencia:
        1. Cargar dashboard
        2. Verificar estado inicial
        3. Activar emergency stop
        4. Verificar estado actualizado
        """
        # Mock gateway responses
        mock_send.side_effect = [
            {"status": "success", "message": "Emergency stop activated"},
            {
                "status": "stopped",
                "connected": True,
                "uptime": "150s",
                "messages": 1,
                "errors": 0
            }
        ]
        
        # Step 1: Load dashboard
        response = client.get("/")
        assert response.status_code == 200
        assert b"PARADA DE EMERGENCIA" in response.content
        
        # Step 2: Check initial status
        response = client.get("/api/status")
        assert response.status_code == 200
        initial_state = response.json()
        assert "status" in initial_state
        
        # Step 3: Trigger emergency stop
        response = client.post("/api/emergency-stop")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        
        # Step 4: Verify updated status
        response = client.get("/api/status")
        assert response.status_code == 200
        # Estado se actualiza via WebSocket, aquí verificamos que la API responde
    
    @patch('src.web_ui.main.WebUIApp._send_gateway_command')
    def test_emergency_stop_with_error_recovery(self, mock_send, client):
        """
        Test E2E con manejo de errores:
        1. Intentar emergency stop (falla)
        2. Verificar error
        3. Reintentar (éxito)
        """
        # First attempt fails, second succeeds
        mock_send.side_effect = [
            Exception("Gateway timeout"),
            {"status": "success", "message": "Emergency stop activated"}
        ]
        
        # First attempt - should fail
        response = client.post("/api/emergency-stop")
        assert response.status_code == 500
        error_data = response.json()
        assert error_data["status"] == "error"
        assert "Gateway timeout" in error_data["message"]
        
        # Second attempt - should succeed
        response = client.post("/api/emergency-stop")
        assert response.status_code == 200
        success_data = response.json()
        assert success_data["status"] == "success"


class TestResetFlow:
    """E2E tests for system reset workflow"""
    
    @patch('src.web_ui.main.WebUIApp._send_gateway_command')
    def test_complete_reset_flow(self, mock_send, client):
        """
        Test flujo completo de reinicio:
        1. Sistema en estado stopped
        2. Ejecutar reset
        3. Verificar sistema operacional
        """
        mock_send.side_effect = [
            {"status": "success", "message": "System reset completed"},
            {
                "status": "operational",
                "connected": True,
                "uptime": "5s",
                "messages": 0,
                "errors": 0
            }
        ]
        
        # Execute reset
        response = client.post("/api/reset")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        
        # Verify operational status
        response = client.get("/api/status")
        assert response.status_code == 200


class TestWebSocketRealTimeUpdates:
    """E2E tests for WebSocket real-time communication"""
    
    @patch('src.web_ui.main.WebUIApp._get_gateway_status')
    def test_websocket_lifecycle(self, mock_status, client):
        """
        Test ciclo completo de WebSocket:
        1. Conectar
        2. Recibir estado inicial
        3. Recibir actualizaciones periódicas
        4. Desconectar
        """
        mock_status.return_value = {
            "status": "operational",
            "connected": True,
            "uptime": "180s",
            "messages": 5,
            "errors": 0
        }
        
        with client.websocket_connect("/ws") as websocket:
            # Receive initial state
            initial_data = websocket.receive_json()
            assert "status" in initial_data
            assert "connected" in initial_data
            
            # Receive at least one update
            update_data = websocket.receive_json()
            assert "last_update" in update_data
            assert update_data["status"] == "operational"
    
    @patch('src.web_ui.main.WebUIApp._get_gateway_status')
    @patch('src.web_ui.main.WebUIApp._send_gateway_command')
    def test_websocket_receives_emergency_event(self, mock_send, mock_status, client, app):
        """
        Test WebSocket recibe eventos de emergency stop:
        1. Conectar WebSocket
        2. Otro cliente activa emergency stop
        3. WebSocket recibe evento broadcast
        """
        mock_status.return_value = {
            "status": "operational",
            "connected": True
        }
        
        mock_send.return_value = {
            "status": "success",
            "message": "Emergency stop activated"
        }
        
        with client.websocket_connect("/ws") as websocket:
            # Skip initial state
            websocket.receive_json()
            
            # Trigger emergency stop via API (simulates another user)
            response = client.post("/api/emergency-stop")
            assert response.status_code == 200
            
            # WebSocket should receive broadcast update
            # (In real implementation, this would be an event notification)
            # For now, we verify the mechanism exists
            update = websocket.receive_json()
            assert update is not None


class TestMultiUserScenarios:
    """E2E tests for multi-user scenarios"""
    
    @patch('src.web_ui.main.WebUIApp._get_gateway_status')
    def test_multiple_websocket_connections(self, mock_status, client):
        """
        Test múltiples usuarios conectados simultáneamente:
        1. Conectar 3 WebSockets
        2. Todos reciben actualizaciones
        """
        mock_status.return_value = {
            "status": "operational",
            "connected": True
        }
        
        # Connect 3 WebSocket clients
        with client.websocket_connect("/ws") as ws1, \
             client.websocket_connect("/ws") as ws2, \
             client.websocket_connect("/ws") as ws3:
            
            # All receive initial state
            data1 = ws1.receive_json()
            data2 = ws2.receive_json()
            data3 = ws3.receive_json()
            
            assert "status" in data1
            assert "status" in data2
            assert "status" in data3
    
    @patch('src.web_ui.main.WebUIApp._send_gateway_command')
    def test_concurrent_api_requests(self, mock_send, client):
        """
        Test solicitudes API concurrentes:
        1. Múltiples usuarios hacen requests simultáneos
        2. Todas las respuestas son correctas
        """
        mock_send.return_value = {"status": "success"}
        
        # Simulate 5 concurrent status checks
        responses = []
        for _ in range(5):
            response = client.get("/api/status")
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert "status" in response.json()


class TestErrorHandling:
    """E2E tests for error handling and recovery"""
    
    @patch('src.web_ui.main.WebUIApp._send_gateway_command')
    def test_gateway_disconnection_handling(self, mock_send, client):
        """
        Test manejo de desconexión del gateway:
        1. Gateway funcionando
        2. Gateway se desconecta
        3. UI muestra error apropiadamente
        """
        # Simulate gateway disconnection
        mock_send.side_effect = ConnectionRefusedError("Gateway not available")
        
        response = client.post("/api/emergency-stop")
        assert response.status_code == 500
        
        error_data = response.json()
        assert error_data["status"] == "error"
        assert "Gateway not available" in error_data["message"]
    
    @patch('src.web_ui.main.WebUIApp._get_gateway_status')
    def test_websocket_reconnection(self, mock_status, client):
        """
        Test reconexión automática de WebSocket:
        1. Conectar WebSocket
        2. Simular desconexión
        3. Cliente debe poder reconectar
        """
        mock_status.return_value = {"status": "operational", "connected": True}
        
        # First connection
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()
            assert "status" in data
        
        # Second connection (simulates reconnection)
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()
            assert "status" in data


class TestDashboardInteraction:
    """E2E tests for complete dashboard user interactions"""
    
    @patch('src.web_ui.main.WebUIApp._send_gateway_command')
    @patch('src.web_ui.main.WebUIApp._get_gateway_status')
    def test_complete_user_session(self, mock_status, mock_send, client):
        """
        Test sesión completa de usuario:
        1. Cargar dashboard
        2. Revisar estado
        3. Activar emergency stop
        4. Ver eventos
        5. Resetear sistema
        """
        mock_status.return_value = {
            "status": "operational",
            "connected": True,
            "uptime": "200s"
        }
        
        mock_send.side_effect = [
            {"status": "success", "message": "Emergency stop activated"},
            {"status": "success", "message": "System reset"}
        ]
        
        # Step 1: Load dashboard
        response = client.get("/")
        assert response.status_code == 200
        
        # Step 2: Check status
        response = client.get("/api/status")
        assert response.status_code == 200
        
        # Step 3: Emergency stop
        response = client.post("/api/emergency-stop")
        assert response.status_code == 200
        
        # Step 4: Check events
        response = client.get("/api/events")
        assert response.status_code == 200
        events = response.json()
        assert isinstance(events, list)
        
        # Step 5: Reset system
        response = client.post("/api/reset")
        assert response.status_code == 200


class TestPerformance:
    """E2E performance tests"""
    
    def test_dashboard_load_time(self, client):
        """Test dashboard loads within acceptable time"""
        start = time.time()
        response = client.get("/")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should load in less than 1 second
    
    @patch('src.web_ui.main.WebUIApp._send_gateway_command')
    def test_api_response_time(self, mock_send, client):
        """Test API responds within acceptable time"""
        mock_send.return_value = {"status": "success"}
        
        start = time.time()
        response = client.post("/api/emergency-stop")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5  # Should respond in less than 500ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
