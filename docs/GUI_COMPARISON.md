# Comparación de Interfaces de Usuario

## Resumen Ejecutivo

El proyecto **K13 Puente Grúa** ofrece **dos interfaces complementarias**:

1. **Web UI** (FastAPI) - Control remoto basado en navegador
2. **Desktop GUI** (PyQt6) - Aplicación nativa de escritorio

---

## 🌐 Web UI - FastAPI

### Características

- **Tecnología**: FastAPI + Jinja2 + WebSocket
- **Ubicación**: `src/web_ui/main.py`
- **Puerto**: 8000 (configurable)
- **Acceso**: http://localhost:8000

### Ventajas

✅ **Multiplataforma**: Funciona en cualquier navegador  
✅ **Acceso remoto**: Control desde cualquier dispositivo en la red  
✅ **Sin instalación**: Solo necesita navegador web  
✅ **Responsive**: Adaptable a diferentes pantallas  
✅ **Liviano**: Bajo consumo de recursos del cliente  

### Desventajas

❌ **Requiere red**: Necesita conectividad  
❌ **Seguridad**: Necesita configuración adicional (HTTPS, autenticación)  
❌ **Latencia**: Depende de la red  
❌ **Limitado offline**: No funciona sin servidor activo  

### Casos de Uso Ideales

- **Monitoreo remoto**: Supervisión desde oficina
- **Dashboard central**: Múltiples operadores viendo mismo sistema
- **Dispositivos móviles**: Tablets, smartphones
- **Integración web**: Embebido en sistemas más grandes
- **Desarrollo/Testing**: Rápida iteración sin compilar

### Arquitectura

```
┌─────────────┐          ┌─────────────┐          ┌─────────────┐
│   Browser   │──HTTP───▶│  FastAPI    │──Python─▶│  Integrated │
│  (Cliente)  │◀─WS────▶│   Server    │          │   System    │
└─────────────┘          └─────────────┘          └─────────────┘
                              │                          │
                              ▼                          ▼
                         Templates/                  BL335 + K13
                         Static Files                 Simulator
```

### Ejecución

```bash
# Terminal 1
cd /Users/arturo/puente_grua
source .venv/bin/activate
python src/web_ui/main.py

# Terminal 2 (alternativa usando task)
# Opción desde VS Code: Run Task → "Iniciar Web UI"
```

---

## 🖥️ Desktop GUI - PyQt6

### Características

- **Tecnología**: PyQt6 (nativo Qt6)
- **Ubicación**: `src/web_ui/desktop_gui.py`
- **Interfaz**: Aplicación de escritorio nativa
- **Threading**: Actualización asíncrona sin bloqueo

### Ventajas

✅ **Rendimiento nativo**: Máxima velocidad y responsividad  
✅ **Offline completo**: No requiere red  
✅ **Seguridad industrial**: Sin exposición de red  
✅ **Latencia mínima**: Comunicación directa con sistema  
✅ **Aspecto profesional**: Look & feel nativo del OS  
✅ **Recursos avanzados**: Gráficos, multimedia, threads nativos  

### Desventajas

❌ **Solo local**: No permite acceso remoto  
❌ **Instalación requerida**: PyQt6 + dependencias  
❌ **Mayor consumo**: Más recursos del sistema  
❌ **Un usuario**: Solo un operador a la vez  

### Casos de Uso Ideales

- **Control local**: Operador en planta
- **Entorno industrial**: Seguridad y confiabilidad crítica
- **Máxima performance**: Latencia mínima
- **Diagnóstico avanzado**: Herramientas de debugging
- **Operación offline**: Sin dependencias de red

### Arquitectura

```
┌──────────────────────────────────────┐
│        PyQt6 Main Window             │
├──────────────┬───────────────────────┤
│  Dashboard   │   CANMonitor Tab      │
│  Widget      │   - Tabla mensajes    │
│              │   - Filtros           │
│  Control     │                       │
│  Panel       │   Logs Tab            │
│  Widget      │   - Event log         │
└──────┬───────┴───────────────────────┘
       │
       │ Qt Thread (StatusUpdateThread)
       ▼
┌─────────────────────┐
│  IntegratedSystem   │
│  - BL335Gateway     │
│  - K13Simulator     │
└─────────────────────┘
```

### Widgets Principales

#### 1. **DashboardWidget**
- Estado del dispositivo (con color coding)
- Status Word / Control Word
- Velocidad objetivo y actual
- Posición objetivo y actual
- Estadísticas (uptime, mensajes, errores)

#### 2. **CANMonitorWidget**
- Tabla de mensajes CAN en tiempo real
- COB-ID, tipo, datos, timestamp
- Filtros y pausar/reanudar
- Máximo 100 mensajes (rolling buffer)

#### 3. **ControlPanelWidget**
- 🚨 Emergency Stop (botón rojo grande)
- ▶️ Arrancar sistema
- ⏹️ Apagar sistema
- Control de velocidad con SpinBox

#### 4. **LogWidget**
- Log de eventos con timestamps
- Color coding por nivel (INFO, WARNING, ERROR, SUCCESS)
- Botón limpiar log

### Ejecución

```bash
# Instalar PyQt6 (primera vez)
source .venv/bin/activate
pip install PyQt6>=6.4.0

# Ejecutar GUI
python src/web_ui/desktop_gui.py
```

---

## 📊 Comparación Directa

| Característica          | Web UI (FastAPI)      | Desktop GUI (PyQt6)   |
|-------------------------|------------------------|------------------------|
| **Acceso remoto**       | ✅ Sí                  | ❌ No                  |
| **Latencia**            | 🟡 Media (red)         | ✅ Mínima (local)      |
| **Seguridad industrial**| 🟡 Requiere config     | ✅ Nativa              |
| **Instalación**         | ✅ Solo navegador      | 🟡 PyQt6 requerido     |
| **Multiplataforma**     | ✅ Cualquier browser   | ✅ Linux/Mac/Windows   |
| **Múltiples usuarios**  | ✅ Sí                  | ❌ No                  |
| **Rendimiento**         | 🟡 Bueno               | ✅ Excelente           |
| **Offline**             | ❌ No                  | ✅ Sí                  |
| **Integración HMI**     | ✅ Fácil               | 🟡 Moderado            |
| **Mobile-friendly**     | ✅ Sí                  | ❌ No                  |

---

## 🎯 Recomendaciones de Uso

### Escenario 1: **Planta Industrial Grande**
**Solución**: Ambas interfaces
- **Desktop GUI**: Operador en cabina de control (acceso local)
- **Web UI**: Supervisores en oficina (monitoreo remoto)
- **Beneficio**: Máxima flexibilidad

### Escenario 2: **Taller Pequeño**
**Solución**: Desktop GUI únicamente
- Control directo desde PC industrial
- Sin exposición de red
- Máxima confiabilidad

### Escenario 3: **Desarrollo y Testing**
**Solución**: Web UI + Browser DevTools
- Iteración rápida
- Fácil debugging
- Múltiples ventanas de monitoreo

### Escenario 4: **Integración con SCADA**
**Solución**: Web UI como backend
- Endpoints REST API disponibles
- WebSocket para datos en tiempo real
- JSON para interoperabilidad

---

## 🔧 Estado de Implementación

| Componente                  | Web UI | Desktop GUI | Notas                              |
|-----------------------------|--------|-------------|------------------------------------|
| Dashboard de estado         | ✅     | ✅          | Ambos implementados                |
| Monitor CAN                 | 🟡     | ✅          | Web UI por implementar             |
| Control de velocidad        | ✅     | ✅          |                                    |
| Emergency Stop              | ✅     | ✅          |                                    |
| Secuencias de control       | ✅     | ✅          | startup/shutdown                   |
| WebSocket real-time         | ✅     | N/A         | Web UI específico                  |
| Threading asíncrono         | ✅     | ✅          | FastAPI + Qt Thread                |
| Logs y eventos              | 🟡     | ✅          | Desktop GUI más completo           |
| Configuración              | 🟡     | ⬜          | Por implementar en ambos           |
| Gráficos históricos         | ⬜     | ⬜          | Roadmap futuro                     |

**Leyenda**: ✅ Completo | 🟡 Parcial | ⬜ Pendiente

---

## 📦 Dependencias

### Web UI
```
fastapi>=0.100.0
uvicorn>=0.23.0
jinja2>=3.1.0
python-multipart>=0.0.6
```

### Desktop GUI
```
PyQt6>=6.4.0
```

### Ambas
```
pyserial>=3.5
pyyaml>=6.0
numpy>=1.24.0
```

---

## 🚀 Próximos Pasos

### Web UI - Mejoras Pendientes
1. Implementar monitor CAN en frontend
2. Agregar gráficos históricos (Chart.js)
3. Sistema de autenticación (OAuth2/JWT)
4. HTTPS con certificados
5. Rate limiting y seguridad

### Desktop GUI - Mejoras Pendientes
1. Gráficos de velocidad/posición en tiempo real (PyQtGraph)
2. Exportar logs a CSV/JSON
3. Configuración persistente (QSettings)
4. Temas claro/oscuro
5. Atajos de teclado (QShortcut)
6. Indicadores visuales de estado (LEDs animados)

### Integración
1. Desktop GUI como "fat client" con Web UI backend
2. Modo híbrido: Desktop GUI + REST API calls
3. Dashboard consolidado con ambas fuentes de datos

---

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- [Qt Signals & Slots](https://doc.qt.io/qt-6/signalsandslots.html)

---

**Fecha**: 24 de octubre de 2025  
**Versión**: 1.0  
**Proyecto**: K13 Puente Grúa - Sistema de Control CANopen
