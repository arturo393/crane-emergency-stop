"""
Unit Tests for Web UI
FastAPI TestClient para tests rápidos sin Docker
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import json

from src.web_ui.main import WebUIApp


@pytest.fixture
def app():
    """Create Web UI app instance"""
    return WebUIApp(gateway_host="localhost", gateway_port=9999)


@pytest.fixture
def client(app):
    """Create FastAPI test client"""
    return TestClient(app.app)


class TestDashboard:
    """Tests for dashboard page"""
    
    def test_dashboard_loads(self, client):
        """Test dashboard page loads successfully"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Sistema de Parada de Emergencia" in response.content
        assert b"Alpine.js" in response.content
        assert b"HTMX" in response.content
    
    def test_dashboard_has_emergency_button(self, client):
        """Test dashboard has emergency stop button"""
        response = client.get("/")
        assert b"PARADA DE EMERGENCIA" in response.content
        assert b"emergencyStop()" in response.content
    
    def test_dashboard_has_reset_button(self, client):
        """Test dashboard has reset button"""
        response = client.get("/")
        assert b"REINICIAR" in response.content
        assert b"resetSystem()" in response.content
    
    def test_dashboard_shows_status_cards(self, client):
        """Test dashboard displays status cards"""
        response = client.get("/")
        assert b"Estado del Sistema" in response.content
        assert b"Tiempo Activo" in response.content
        assert b"Mensajes" in response.content
        assert b"Errores" in response.content


class TestAPIEndpoints:
    """Tests for REST API endpoints"""
    
    def test_get_status(self, client, app):
        """Test GET /api/status returns system state"""
        response = client.get("/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "connected" in data
        assert "uptime" in data
        assert "messages" in data
        assert "errors" in data
    
    @patch('src.web_ui.main.WebUIApp._send_gateway_command')
    def test_emergency_stop_success(self, mock_send, client):
        """Test POST /api/emergency-stop with successful response"""
        # Mock gateway response
        mock_send.return_value = {"status": "success", "message": "Emergency stop activated"}
        
        response = client.post("/api/emergency-stop")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        mock_send.assert_called_once()
    
    @patch('src.web_ui.main.WebUIApp._send_gateway_command')
    def test_emergency_stop_failure(self, mock_send, client):
        """Test POST /api/emergency-stop with gateway error"""
        # Mock gateway error
        mock_send.side_effect = Exception("Gateway timeout")
        
        response = client.post("/api/emergency-stop")
        assert response.status_code == 500
        
        data = response.json()
        assert data["status"] == "error"
        assert "Gateway timeout" in data["message"]
    
    @patch('src.web_ui.main.WebUIApp._send_gateway_command')
    def test_reset_system_success(self, mock_send, client):
        """Test POST /api/reset with successful response"""
        mock_send.return_value = {"status": "success", "message": "System reset"}
        
        response = client.post("/api/reset")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
    
    def test_get_recent_events(self, client):
        """Test GET /api/events returns event list"""
        response = client.get("/api/events")
        assert response.status_code == 200
        
        events = response.json()
        assert isinstance(events, list)
        if len(events) > 0:
            assert "timestamp" in events[0]
            assert "type" in events[0]
            assert "message" in events[0]


class TestWebSocketCommunication:
    """Tests for WebSocket real-time updates"""
    
    @patch('src.web_ui.main.WebUIApp._get_gateway_status')
    def test_websocket_connection(self, mock_status, client, app):
        """Test WebSocket connection and initial state"""
        mock_status.return_value = {
            "status": "operational",
            "connected": True,
            "uptime": "120s"
        }
        
        with client.websocket_connect("/ws") as websocket:
            # Receive initial state
            data = websocket.receive_json()
            
            assert "status" in data
            assert "connected" in data
            assert "uptime" in data
    
    @patch('src.web_ui.main.WebUIApp._get_gateway_status')
    def test_websocket_receives_updates(self, mock_status, client, app):
        """Test WebSocket receives periodic status updates"""
        mock_status.return_value = {
            "status": "operational",
            "connected": True,
            "uptime": "125s",
            "messages": 42
        }
        
        with client.websocket_connect("/ws") as websocket:
            # Skip initial state
            websocket.receive_json()
            
            # Receive update (after 2s polling)
            data = websocket.receive_json()
            
            assert data["status"] == "operational"
            assert data["connected"] == True
            assert "last_update" in data


class TestGatewayCommunication:
    """Tests for BL335 Gateway communication"""
    
    @patch('socket.socket')
    @pytest.mark.asyncio
    async def test_send_gateway_command_success(self, mock_socket_class, app):
        """Test successful command send to gateway"""
        # Mock socket
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Mock response
        response_data = {"status": "success", "value": 42}
        mock_socket.recv.return_value = json.dumps(response_data).encode('utf-8')
        
        # Send command
        result = await app._send_gateway_command({"command": "test"})
        
        # Verify
        assert result == response_data
        mock_socket.connect.assert_called_once_with(("localhost", 9999))
        mock_socket.send.assert_called_once()
        mock_socket.close.assert_called_once()
    
    @patch('socket.socket')
    @pytest.mark.asyncio
    async def test_send_gateway_command_timeout(self, mock_socket_class, app):
        """Test gateway command timeout handling"""
        # Mock socket timeout
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.side_effect = TimeoutError("Connection timeout")
        
        # Should raise exception
        with pytest.raises(TimeoutError):
            await app._send_gateway_command({"command": "test"})
        
        # Socket should still be closed
        mock_socket.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_gateway_status(self, app):
        """Test get_gateway_status calls send_command correctly"""
        with patch.object(app, '_send_gateway_command') as mock_send:
            mock_send.return_value = {"status": "ok"}
            
            result = await app._get_gateway_status()
            
            assert result == {"status": "ok"}
            mock_send.assert_called_once_with({"command": "get_status"})


class TestBroadcastSystem:
    """Tests for WebSocket broadcast functionality"""
    
    @pytest.mark.asyncio
    async def test_broadcast_to_all_clients(self, app):
        """Test message broadcast to multiple WebSocket clients"""
        # Mock WebSocket connections
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws3 = AsyncMock()
        
        app.active_connections = [ws1, ws2, ws3]
        
        # Broadcast message
        message = {"type": "test", "data": "hello"}
        await app._broadcast_update(message)
        
        # All should receive message
        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)
        ws3.send_json.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_broadcast_removes_disconnected(self, app):
        """Test broadcast removes failed connections"""
        # Mock connections (ws2 will fail)
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws2.send_json.side_effect = Exception("Connection lost")
        ws3 = AsyncMock()
        
        app.active_connections = [ws1, ws2, ws3]
        
        # Broadcast
        await app._broadcast_update({"type": "test"})
        
        # ws2 should be removed
        assert ws2 not in app.active_connections
        assert ws1 in app.active_connections
        assert ws3 in app.active_connections


class TestSystemState:
    """Tests for system state management"""
    
    def test_initial_state(self, app):
        """Test initial system state is correct"""
        assert app.system_state["status"] == "disconnected"
        assert app.system_state["connected"] == False
        assert app.system_state["messages"] == 0
        assert app.system_state["errors"] == 0
    
    def test_state_updates(self, app):
        """Test system state can be updated"""
        new_state = {
            "status": "operational",
            "connected": True,
            "messages": 10,
            "errors": 0
        }
        
        app.system_state.update(new_state)
        
        assert app.system_state["status"] == "operational"
        assert app.system_state["connected"] == True
        assert app.system_state["messages"] == 10


class TestConfiguration:
    """Tests for app configuration"""
    
    def test_custom_gateway_config(self):
        """Test custom gateway host/port configuration"""
        app = WebUIApp(gateway_host="192.168.1.100", gateway_port=8888)
        
        assert app.gateway_host == "192.168.1.100"
        assert app.gateway_port == 8888
    
    def test_default_gateway_config(self):
        """Test default gateway configuration"""
        app = WebUIApp()
        
        assert app.gateway_host == "localhost"
        assert app.gateway_port == 9999


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
