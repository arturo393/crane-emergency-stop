"""
Web UI Main Application
FastAPI server for crane emergency stop monitoring and control
"""

import asyncio
import json
from datetime import datetime
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Import BL335 Gateway client
import socket


class WebUIApp:
    """Web UI Application"""
    
    def __init__(self, gateway_host="localhost", gateway_port=9999):
        self.app = FastAPI(title="Crane Emergency Stop Monitor", version="0.1.0")
        self.gateway_host = gateway_host
        self.gateway_port = gateway_port
        
        # Setup paths
        base_dir = Path(__file__).parent
        static_dir = base_dir / "static"
        templates_dir = base_dir / "templates"
        
        # Mount static files
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Setup templates
        self.templates = Jinja2Templates(directory=str(templates_dir))
        
        # Active WebSocket connections
        self.active_connections: list[WebSocket] = []
        
        # System state
        self.system_state = {
            "status": "disconnected",
            "connected": False,
            "uptime": "0s",
            "messages": 0,
            "errors": 0,
            "last_update": None
        }
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Main dashboard page"""
            return self.templates.TemplateResponse(
                "dashboard.html",
                {
                    "request": request,
                    "title": "Crane Emergency Stop Monitor",
                    "system_state": self.system_state
                }
            )
        
        @self.app.get("/api/status")
        async def get_status():
            """Get current system status"""
            return JSONResponse(self.system_state)
        
        @self.app.post("/api/emergency-stop")
        async def emergency_stop():
            """Trigger emergency stop"""
            try:
                result = await self._send_gateway_command({"command": "emergency_stop"})
                await self._broadcast_update({
                    "type": "emergency_stop",
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                })
                return JSONResponse(result)
            except Exception as e:
                return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
        
        @self.app.post("/api/reset")
        async def reset_system():
            """Reset system"""
            try:
                result = await self._send_gateway_command({"command": "reset"})
                await self._broadcast_update({
                    "type": "reset",
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                })
                return JSONResponse(result)
            except Exception as e:
                return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
        
        @self.app.get("/api/events")
        async def get_recent_events():
            """Get recent system events"""
            # TODO: Implement event log storage
            events = [
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "info",
                    "message": "System initialized"
                }
            ]
            return JSONResponse(events)
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                # Send initial state
                await websocket.send_json(self.system_state)
                
                # Keep connection alive and send updates
                while True:
                    # Poll gateway status every 2 seconds
                    await asyncio.sleep(2)
                    
                    try:
                        status = await self._get_gateway_status()
                        self.system_state.update(status)
                        self.system_state["last_update"] = datetime.now().isoformat()
                        await websocket.send_json(self.system_state)
                    except Exception as e:
                        self.system_state["status"] = "error"
                        self.system_state["connected"] = False
                        await websocket.send_json(self.system_state)
                        
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
    
    async def _send_gateway_command(self, command: dict) -> dict:
        """Send command to BL335 Gateway"""
        loop = asyncio.get_event_loop()
        
        def _send():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            try:
                sock.connect((self.gateway_host, self.gateway_port))
                sock.send(json.dumps(command).encode('utf-8'))
                response = sock.recv(4096)
                return json.loads(response.decode('utf-8'))
            finally:
                sock.close()
        
        return await loop.run_in_executor(None, _send)
    
    async def _get_gateway_status(self) -> dict:
        """Get status from BL335 Gateway"""
        return await self._send_gateway_command({"command": "get_status"})
    
    async def _broadcast_update(self, message: dict):
        """Broadcast update to all connected WebSocket clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)
    
    def run(self, host="0.0.0.0", port=8000):
        """Run the web server"""
        print("=" * 60)
        print("🌐 Crane Emergency Stop - Web UI")
        print("=" * 60)
        print(f"Server: http://{host}:{port}")
        print(f"Gateway: {self.gateway_host}:{self.gateway_port}")
        print("\nPresiona Ctrl+C para detener")
        print("=" * 60)
        
        uvicorn.run(self.app, host=host, port=port)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Crane Emergency Stop Web UI')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind (default: 8000)')
    parser.add_argument('--gateway-host', default='localhost', help='BL335 Gateway host')
    parser.add_argument('--gateway-port', type=int, default=9999, help='BL335 Gateway port')
    
    args = parser.parse_args()
    
    app = WebUIApp(gateway_host=args.gateway_host, gateway_port=args.gateway_port)
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
