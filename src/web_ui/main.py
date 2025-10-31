"""
Web UI Main Application
FastAPI server for crane emergency stop monitoring and control
Updated to support integrated system (Simulator + Gateway)
"""

import asyncio
import json
from datetime import datetime
from typing import Optional
from pathlib import Path
import sys
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Import BL335 Gateway client
import socket

# Añadir rutas al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.bl335_gateway.simulator_adapter import IntegratedSystem


class WebUIApp:
    """Web UI Application with Integrated System support"""
    
    def __init__(self, gateway_host="localhost", gateway_port=9999, use_integrated=True):
        self.app = FastAPI(title="K13 Puente Grúa - Control Center", version="1.0.0")
        self.gateway_host = gateway_host
        self.gateway_port = gateway_port
        self.use_integrated = use_integrated
        
        # Sistema integrado (Simulador + Gateway)
        self.integrated_system: Optional[IntegratedSystem] = None
        
        # Setup paths
        base_dir = Path(__file__).parent
        static_dir = base_dir / "static"
        templates_dir = base_dir / "templates"
        
        # Mount static files
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Setup templates
        self.templates = Jinja2Templates(directory=str(templates_dir))
        
        # Active WebSocket connections
        self.active_connections: list[WebSocket] = []
        
        # CAN message buffer (circular buffer, últimos 100 mensajes)
        self.can_messages = []
        self.max_can_messages = 100
        self.can_message_counter = 0
        
        # System state
        self.system_state = {
            "status": "initializing",
            "connected": False,
            "uptime": "0s",
            "messages": 0,
            "errors": 0,
            "last_update": None,
            "device_state": "UNKNOWN",
            "velocity": 0,
            "position": 0
        }
        
        # Setup routes
        self._setup_routes()
        
        # Setup lifecycle events
        if self.use_integrated:
            @self.app.on_event("startup")
            async def startup():
                await self._start_integrated_system()
            
            @self.app.on_event("shutdown")
            async def shutdown():
                await self._stop_integrated_system()
    
    async def _start_integrated_system(self):
        """Iniciar sistema integrado al arranque"""
        print("\n🚀 Iniciando sistema integrado...")
        self.integrated_system = IntegratedSystem(node_id=1, tcp_port=self.gateway_port)
        
        if self.integrated_system.start():
            print("✅ Sistema integrado iniciado")
            self.system_state["status"] = "running"
            self.system_state["connected"] = True
            
            # Iniciar tarea de actualización periódica
            asyncio.create_task(self._periodic_update())
        else:
            print("❌ Error iniciando sistema integrado")
            self.system_state["status"] = "error"
            self.system_state["connected"] = False
    
    async def _stop_integrated_system(self):
        """Detener sistema integrado"""
        if self.integrated_system:
            print("\n⏹️  Deteniendo sistema integrado...")
            self.integrated_system.stop()
            print("✅ Sistema detenido")
    
    async def _periodic_update(self):
        """Actualizar estado periódicamente y enviar a clientes WebSocket"""
        while True:
            try:
                if self.integrated_system:
                    status = self.integrated_system.get_status()
                    
                    # Actualizar system_state
                    if status.get('simulator'):
                        self.system_state.update({
                            "device_state": status['simulator']['device_state'],
                            "velocity": status['simulator']['actual_velocity'],
                            "position": status['simulator']['actual_position'],
                            "status_word": status['simulator'].get('status_word', 0)
                        })
                    
                    if status.get('gateway'):
                        self.system_state.update({
                            "connected": status['gateway']['connected']
                        })
                    
                    # Capturar mensajes CAN recientes
                    await self._capture_can_messages()
                    
                    self.system_state["last_update"] = datetime.now().isoformat()
                    self.system_state["can_message_count"] = len(self.can_messages)
                    
                    # Broadcast a clientes WebSocket
                    await self._broadcast_update(self.system_state)
            
            except Exception as e:
                print(f"Error en actualización periódica: {e}")
            
            await asyncio.sleep(0.5)  # Actualizar cada 500ms
    
    async def _capture_can_messages(self):
        """Capturar mensajes CAN del simulador/gateway"""
        try:
            if not self.integrated_system:
                return
            
            # Obtener mensajes recientes del simulador
            simulator = self.integrated_system.simulator
            if hasattr(simulator, 'message_history') and simulator.message_history:
                # Tomar últimos mensajes que no hayamos procesado
                for msg in simulator.message_history[-10:]:  # Últimos 10
                    can_msg = {
                        "id": self.can_message_counter,
                        "timestamp": datetime.now().isoformat(),
                        "cob_id": f"0x{msg.arbitration_id:03X}",
                        "dlc": msg.dlc,
                        "data": msg.data.hex().upper(),
                        "data_bytes": ' '.join([f'{b:02X}' for b in msg.data]),
                        "type": self._get_message_type(msg.arbitration_id),
                        "direction": "RX" if msg.is_rx else "TX"
                    }
                    
                    # Agregar al buffer circular
                    self.can_messages.append(can_msg)
                    self.can_message_counter += 1
                    
                    # Mantener tamaño máximo
                    if len(self.can_messages) > self.max_can_messages:
                        self.can_messages.pop(0)
        except Exception as e:
            print(f"Error capturando mensajes CAN: {e}")
    
    def _get_message_type(self, cob_id: int) -> str:
        """Determinar tipo de mensaje CANopen por COB-ID"""
        function_code = (cob_id >> 7) & 0x0F
        
        message_types = {
            0x0: "NMT",
            0x1: "SYNC/EMCY",
            0x2: "TIME",
            0x3: "TPDO1",
            0x4: "RPDO1",
            0x5: "TPDO2",
            0x6: "RPDO2",
            0x7: "TPDO3",
            0x8: "RPDO3",
            0x9: "TPDO4",
            0xA: "RPDO4",
            0xB: "SDO_TX",
            0xC: "SDO_RX",
            0xE: "NMT_ERROR"
        }
        
        # Casos especiales
        if cob_id == 0x000:
            return "NMT"
        elif cob_id == 0x080:
            return "SYNC"
        elif 0x081 <= cob_id <= 0x0FF:
            return "EMCY"
        elif 0x180 <= cob_id <= 0x1FF:
            return "TPDO1"
        elif 0x200 <= cob_id <= 0x27F:
            return "RPDO1"
        elif 0x280 <= cob_id <= 0x2FF:
            return "TPDO2"
        elif 0x300 <= cob_id <= 0x37F:
            return "RPDO2"
        elif 0x380 <= cob_id <= 0x3FF:
            return "TPDO3"
        elif 0x400 <= cob_id <= 0x47F:
            return "RPDO3"
        elif 0x480 <= cob_id <= 0x4FF:
            return "TPDO4"
        elif 0x500 <= cob_id <= 0x57F:
            return "RPDO4"
        elif 0x580 <= cob_id <= 0x5FF:
            return "SDO_TX"
        elif 0x600 <= cob_id <= 0x67F:
            return "SDO_RX"
        elif 0x700 <= cob_id <= 0x77F:
            return "HEARTBEAT"
        
        return message_types.get(function_code, "UNKNOWN")
    
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
        
        @self.app.get("/can-monitor", response_class=HTMLResponse)
        async def can_monitor_page(request: Request):
            """CAN Monitor page"""
            return self.templates.TemplateResponse(
                "can_monitor.html",
                {
                    "request": request,
                    "title": "CAN Bus Monitor"
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
                if self.use_integrated and self.integrated_system:
                    result = self.integrated_system.gateway.emergency_stop()
                else:
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
                if self.use_integrated and self.integrated_system:
                    result = self.integrated_system.gateway.reset()
                else:
                    result = await self._send_gateway_command({"command": "reset"})
                
                await self._broadcast_update({
                    "type": "reset",
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                })
                return JSONResponse(result)
            except Exception as e:
                return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
        
        @self.app.post("/api/enable-operation")
        async def enable_operation():
            """Enable operation (Control Word 0x000F)"""
            try:
                if self.use_integrated and self.integrated_system:
                    # Control Word = 0x000F (Enable Operation)
                    data = bytes([0x0F, 0x00, 0x00, 0x00])
                    result = self.integrated_system.gateway.pdo_write(1, data)
                else:
                    result = await self._send_gateway_command({
                        "command": "pdo_write",
                        "pdo_number": 1,
                        "data": "0F000000"
                    })
                
                await self._broadcast_update({
                    "type": "enable_operation",
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                })
                return JSONResponse(result)
            except Exception as e:
                return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
        
        @self.app.post("/api/switch-on")
        async def switch_on():
            """Switch On (Control Word 0x0007)"""
            try:
                if self.use_integrated and self.integrated_system:
                    # Control Word = 0x0007 (Switch On)
                    data = bytes([0x07, 0x00, 0x00, 0x00])
                    result = self.integrated_system.gateway.pdo_write(1, data)
                else:
                    result = await self._send_gateway_command({
                        "command": "pdo_write",
                        "pdo_number": 1,
                        "data": "07000000"
                    })
                
                await self._broadcast_update({
                    "type": "switch_on",
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                })
                return JSONResponse(result)
            except Exception as e:
                return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
        
        @self.app.post("/api/set-velocity")
        async def set_velocity(request: Request):
            """Set target velocity"""
            try:
                data = await request.json()
                velocity = int(data.get('velocity', 0))
                
                if self.use_integrated and self.integrated_system:
                    # Escribir velocidad objetivo (0x6081)
                    result = self.integrated_system.gateway.sdo_write(0x6081, 0, velocity)
                else:
                    result = await self._send_gateway_command({
                        "command": "sdo_write",
                        "index": 0x6081,
                        "subindex": 0,
                        "value": velocity
                    })
                
                await self._broadcast_update({
                    "type": "set_velocity",
                    "velocity": velocity,
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
        
        @self.app.get("/api/can-messages")
        async def get_can_messages(limit: int = 100):
            """Get recent CAN messages"""
            # Retornar últimos 'limit' mensajes
            messages = self.can_messages[-limit:] if len(self.can_messages) > limit else self.can_messages
            return JSONResponse({
                "messages": messages,
                "total": len(self.can_messages),
                "counter": self.can_message_counter
            })
        
        @self.app.delete("/api/can-messages")
        async def clear_can_messages():
            """Clear CAN message buffer"""
            self.can_messages.clear()
            self.can_message_counter = 0
            return JSONResponse({"status": "ok", "message": "Buffer cleared"})
        
        @self.app.get("/api/can-statistics")
        async def get_can_statistics():
            """Get CAN bus statistics"""
            stats = {
                "total_messages": self.can_message_counter,
                "buffer_size": len(self.can_messages),
                "messages_by_type": {},
                "messages_by_direction": {"TX": 0, "RX": 0}
            }
            
            # Calcular estadísticas
            for msg in self.can_messages:
                msg_type = msg.get("type", "UNKNOWN")
                stats["messages_by_type"][msg_type] = stats["messages_by_type"].get(msg_type, 0) + 1
                
                direction = msg.get("direction", "UNKNOWN")
                if direction in stats["messages_by_direction"]:
                    stats["messages_by_direction"][direction] += 1
            
            return JSONResponse(stats)
        
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
        print("=" * 70)
        print("� K13 PUENTE GRÚA - WEB CONTROL CENTER")
        print("=" * 70)
        print(f"\n🌐 Servidor Web: http://{host}:{port}")
        print(f"📡 WebSocket: ws://{host}:{port}/ws")
        
        if self.use_integrated:
            print(f"🔌 Sistema Integrado: Simulador + Gateway")
            print(f"📡 Gateway TCP: puerto {self.gateway_port}")
        else:
            print(f"🔌 Gateway externo: {self.gateway_host}:{self.gateway_port}")
        
        print("\nAbre tu navegador y accede a:")
        print(f"  → http://localhost:{port}")
        print("\nPresiona Ctrl+C para detener")
        print("=" * 70)
        
        uvicorn.run(self.app, host=host, port=port)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='K13 Puente Grúa - Web Control Center')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind (default: 8000)')
    parser.add_argument('--gateway-host', default='localhost', help='BL335 Gateway host (si --no-integrated)')
    parser.add_argument('--gateway-port', type=int, default=9999, help='BL335 Gateway port')
    parser.add_argument('--no-integrated', action='store_true', 
                       help='No usar sistema integrado (conectar a gateway externo)')
    
    args = parser.parse_args()
    
    app = WebUIApp(
        gateway_host=args.gateway_host, 
        gateway_port=args.gateway_port,
        use_integrated=not args.no_integrated
    )
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
