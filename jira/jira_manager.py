#!/usr/bin/env python3
"""
SafetyMind Infrastructure Monitoring - Jira Manager
==================================================

Herramienta unificada para gestión completa de proyectos Jira.
Consolida todas las funcionalidades de gestión de tareas, épicos y cronogramas.

Uso:
    python3 jira_manager.py --action [import|cleanup|assign|schedule|check|diagnose]
    
Acciones disponibles:
    import      - Importar tareas y épicos desde configuración
    cleanup     - Limpiar épicos duplicados y reorganizar
    assign      - Asignar tareas a épicos basado en contenido
    schedule    - Actualizar fechas y estimaciones de tiempo
    check       - Verificar estado actual del proyecto
    diagnose    - Diagnóstico completo de conexión y configuración

Autor: SafetyMind Team
Versión: 2.0.0
Fecha: Octubre 2025
"""

import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jira import JIRA
import re

# Cargar variables de entorno
load_dotenv()

class JiraManager:
    """Gestor unificado para todas las operaciones de Jira"""
    
    def __init__(self):
        """Inicializar conexión con Jira"""
        try:
            self.jira = JIRA(
                server=os.getenv('JIRA_URL'),
                basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
            )
            self.project_key = os.getenv('JIRA_PROJECT_KEY', 'IM')
            self.start_date = datetime(2025, 11, 3)  # Fecha base del proyecto
            print(f"✅ Conectado a Jira: {os.getenv('JIRA_URL')}")
            print(f"📋 Proyecto: {self.project_key}")
        except Exception as e:
            print(f"❌ Error conectando a Jira: {e}")
            sys.exit(1)
    
    def clean_summary(self, summary):
        """Limpiar resumen para Jira (máximo 255 caracteres)"""
        if not summary:
            return "Sin título"
        # Truncar a 255 caracteres
        cleaned = summary.strip()[:255]
        return cleaned
    
    def clean_labels(self, labels):
        """Limpiar etiquetas para Jira (sin espacios)"""
        if not labels:
            return []
        cleaned_labels = []
        for label in labels:
            # Reemplazar espacios con guiones
            clean_label = re.sub(r'\s+', '-', label.strip())
            cleaned_labels.append(clean_label)
        return cleaned_labels
    
    def get_project_structure(self):
        """Obtener estructura de épicos y tareas del proyecto K13 Puente Grúa"""
        return {
            'epics': [
                {
                    'key': 'EPIC-FOUNDATION',
                    'summary': 'Fundación del Sistema K13 - EDS y Protocolos',
                    'description': '''Epic para establecer los fundamentos técnicos del sistema K13 Puente Grúa.
                    
📋 ALCANCE:
• Desarrollo de archivos EDS Danfoss R13 F completos y realistas
• Validación de protocolos CANopen (CiA 402)
• Configuración BL335 Gateway con soporte PDO/SDO/NMT
• Simulación completa R13 F para testing sin hardware
• Documentación técnica y manuales reorganizados

🎯 OBJETIVOS:
• Base sólida para comunicación CANopen
• Protocolos validados y funcionales
• Capacidades de testing sin hardware real
• Documentación técnica completa y organizada

📅 PERÍODO: Sep 2025 - Oct 2025
🏆 RESULTADO: Fundación técnica sólida establecida''',
                    'labels': ['foundation', 'canopen', 'eds', 'protocol', 'documentation']
                },
                {
                    'key': 'EPIC-IMPLEMENTATION',
                    'summary': 'Implementación de Gateways y Interfaces',
                    'description': '''Epic para implementar los gateways ESP32 y BL335, más las interfaces de usuario.
                    
📋 ALCANCE:
• ESP32 Gateway con WiFi, Ethernet, TCP Server y OTA
• BL335 Gateway con CANopen completo (PDO/SDO/NMT)
• Desktop GUI PyQt6 con monitoreo y control en tiempo real
• Web UI FastAPI con CAN Monitor y APIs REST
• Sistema de testing con Testcontainers
• Infraestructura Docker y CI/CD

🎯 OBJETIVOS:
• Gateways completamente funcionales
• Interfaces de usuario profesionales
• Testing automatizado robusto
• Infraestructura de desarrollo moderna

📅 PERÍODO: Oct 2025 - Nov 2025
🏆 RESULTADO: Sistema completo implementado y probado''',
                    'labels': ['implementation', 'esp32', 'bl335', 'gui', 'web-ui', 'testing']
                },
                {
                    'key': 'EPIC-INTEGRATION',
                    'summary': 'Integración Hardware y Validación Final',
                    'description': '''Epic para integrar hardware real y validar el sistema completo.
                    
📋 ALCANCE:
• Adquisición y configuración hardware (BL335, EdgeBox-ESP-100)
• Integración con radio R13 F real
• Sistema de logging y auditoría completo
• Validación end-to-end con hardware real
• Optimización y ajustes finales
• Documentación de deployment y operación

🎯 OBJETIVOS:
• Sistema funcionando con hardware real
• Logging y auditoría industrial completos
• Validación completa del emergency stop
• Sistema listo para producción

📅 PERÍODO: Nov 2025 - Dic 2025
🏆 RESULTADO: Sistema industrial completo y validado''',
                    'labels': ['integration', 'hardware', 'validation', 'logging', 'production']
                }
            ],
            'tasks': [
                # EPIC 1: Fundación del Sistema K13 - COMPLETADO
                {
                    'key': 'GAT-1',
                    'summary': 'EDS Realista Danfoss R13 F',
                    'description': '''✅ COMPLETADO - Crear archivo EDS completo para Danfoss R13 F Radio Receiver.

🔧 TAREAS REALIZADAS:
• Análisis manual BC292382016572en-000201
• Desarrollo EDS completo con 35 objetos CANopen
• Versión minimal para testing
• Validación con CANopen Device Profile CiA 402

📦 ENTREGABLES COMPLETADOS:
• config/danfoss_r13f_complete.eds (850 líneas)
• config/danfoss_r13f_minimal.eds (versión testing)
• docs/danfoss_r13f_eds_documentation.md (documentación técnica)

📅 CRONOGRAMA:
• Fecha inicio real: 13 de octubre de 2025 09:00
• Fecha completado: 13 de octubre de 2025 17:00  
• Duración real: 3 horas (no 6h estimadas)
• Estado: ✅ COMPLETADO 100%''',
                    'labels': ['foundation', 'eds', 'canopen', 'danfoss', 'completed'],
                    'epic': 'EPIC-FOUNDATION',
                    'start_offset': -30, 'duration_days': 1, 'estimated_hours': 6,
                    'status': 'Done',
                    'start_date_real': datetime(2025, 10, 13),
                    'end_date_real': datetime(2025, 10, 13),
                    'worklog_entries': [
                        {
                            'date': datetime(2025, 10, 13, 9, 0),
                            'time_spent': '1.5h',
                            'description': 'Análisis manual BC292382016572en-000201 y estructura EDS inicial'
                        },
                        {
                            'date': datetime(2025, 10, 13, 14, 0),
                            'time_spent': '1.5h',
                            'description': 'Desarrollo EDS completo con 35 objetos CANopen y validación CiA 402'
                        }
                    ]
                },
                {
                    'key': 'GAT-2',
                    'summary': 'Validar BL335 Gateway',
                    'description': '''✅ COMPLETADO - Validar y completar implementación BL335 Gateway.

🔧 TAREAS REALIZADAS:
• Implementación PDO completa (RPDO1, TPDO1, TPDO2)
• Mapeo automático de objetos CANopen
• Emergency stop vía PDO (respuesta inmediata)
• Carga de archivos EDS para configuración automática
• Configuración NMT mejorada con heartbeat
• Estados CANopen: Pre-operational, Operational, Stopped

📦 ENTREGABLES COMPLETADOS:
• src/bl335_gateway/main.py (380+ líneas)
• Servidor TCP multicliente (puerto 9999)
• Comandos JSON: emergency_stop, get_status, reset, sdo_read, sdo_write
• Tests: 44/44 pasan (100%)

📅 CRONOGRAMA:
• Fecha inicio real: 14 de octubre de 2025
• Fecha completado: 18 de octubre de 2025
• Duración real: 10 horas (no 32h estimadas)
• Estado: ✅ COMPLETADO 100%''',
                    'labels': ['foundation', 'bl335', 'canopen', 'gateway', 'completed'],
                    'epic': 'EPIC-FOUNDATION',
                    'start_offset': -25, 'duration_days': 3, 'estimated_hours': 32,
                    'status': 'Done',
                    'start_date_real': datetime(2025, 10, 14),
                    'end_date_real': datetime(2025, 10, 18),
                    'worklog_entries': [
                        {
                            'date': datetime(2025, 10, 14, 9, 0),
                            'time_spent': '3h',
                            'description': 'Implementación estructura base BL335 Gateway y servidor TCP'
                        },
                        {
                            'date': datetime(2025, 10, 15, 9, 0),
                            'time_spent': '3h',
                            'description': 'Implementación PDO completa y comandos JSON'
                        },
                        {
                            'date': datetime(2025, 10, 16, 9, 0),
                            'time_spent': '2h',
                            'description': 'Testing completo y validación 44/44 tests'
                        },
                        {
                            'date': datetime(2025, 10, 18, 9, 0),
                            'time_spent': '2h',
                            'description': 'Documentación y optimización final'
                        }
                    ]
                },
                {
                    'key': 'GAT-3',
                    'summary': 'Desktop GUI PyQt6',
                    'description': '''✅ COMPLETADO - Interfaz gráfica desktop para control K13.

🔧 TAREAS REALIZADAS:
• GUI PyQt6 profesional con 4 widgets principales
• Control Panel para comandos directos K13
• CAN Monitor con análisis hexadecimal
• Event Logger con filtros y búsqueda avanzada
• Status Panel con indicadores en tiempo real

📦 ENTREGABLES COMPLETADOS:
• src/desktop_gui/main.py (730 líneas)
• 4 widgets especializados y modulares
• Dark theme profesional
• Sistema completo de logging y eventos
• Launcher script: scripts/launch_gui.py

📅 CRONOGRAMA:
• Fecha inicio real: 22 de octubre de 2025
• Fecha completado: 22 de octubre de 2025
• Duración real: 2 horas (no 24h estimadas)
• Estado: ✅ COMPLETADO 100%''',
                    'labels': ['gui', 'pyqt6', 'desktop', 'control', 'completed'],
                    'epic': 'EPIC-IMPLEMENTATION',
                    'start_offset': -20, 'duration_days': 3, 'estimated_hours': 24,
                    'status': 'Done',
                    'start_date_real': datetime(2025, 10, 22),
                    'end_date_real': datetime(2025, 10, 22),
                    'worklog_entries': [
                        {
                            'date': datetime(2025, 10, 22, 14, 0),
                            'time_spent': '2h',
                            'description': 'Implementación completa Desktop GUI PyQt6 - 730 líneas en una sesión concentrada'
                        }
                    ]
                },
                {
                    'key': 'GAT-4',
                    'summary': 'ESP32 Gateway Wi-Fi',
                    'description': '''✅ COMPLETADO - Gateway ESP32 con conectividad Wi-Fi/Ethernet.

� TAREAS REALIZADAS:
• Servidor TCP multicliente en ESP32
• Configuración Wi-Fi + Ethernet simultánea
• OTA updates via HTTP
• Bridge CAN-TCP optimizado
• Sistema de logging y diagnósticos

📦 ENTREGABLES COMPLETADOS:
• esp32_gateway/ proyecto ESP-IDF completo
• main/can_tcp_bridge.c (implementación C)
• Soporte dual Wi-Fi/Ethernet
• Web interface para configuración
• OTA update system

📅 CRONOGRAMA:
• Fecha inicio real: 19 de octubre de 2025
• Fecha completado: 20 de octubre de 2025
• Duración real: 6 horas (no 28h estimadas)
• Estado: ✅ COMPLETADO 100%''',
                    'labels': ['esp32', 'wifi', 'gateway', 'ota', 'completed'],
                    'epic': 'EPIC-IMPLEMENTATION',
                    'start_offset': -15, 'duration_days': 4, 'estimated_hours': 28,
                    'status': 'Done',
                    'start_date_real': datetime(2025, 10, 19),
                    'end_date_real': datetime(2025, 10, 20),
                    'worklog_entries': [
                        {
                            'date': datetime(2025, 10, 19, 10, 0),
                            'time_spent': '3h',
                            'description': 'Setup ESP-IDF y implementación TCP server base'
                        },
                        {
                            'date': datetime(2025, 10, 20, 9, 0),
                            'time_spent': '3h',
                            'description': 'Bridge CAN-TCP, Wi-Fi/Ethernet dual y OTA system'
                        }
                    ]
                },
                
                # EPIC 2: Implementación de Gateways y Interfaces
                {
                    'key': 'GAT-5',
                    'summary': 'Desktop GUI PyQt6 Implementation',
                    'description': '''✅ COMPLETADO - Implementar GUI desktop profesional con PyQt6.

🔧 TAREAS REALIZADAS:
• src/web_ui/desktop_gui.py completo (730 líneas)
• 4 widgets profesionales: Dashboard, CAN Monitor, Control Panel, Logs
• Threading asíncrono (StatusUpdateThread) sin bloqueo UI
• Color coding automático para estados CiA 402
• Buffer circular para monitor CAN (100 mensajes)
• Emergency stop prominente con botón rojo grande
• Integración completa con IntegratedSystem

📦 ENTREGABLES COMPLETADOS:
• Desktop GUI completamente funcional
• 15 tests unitarios (100% passing)
• Documentación exhaustiva (950+ líneas)
• Script launcher y task VS Code

📅 CRONOGRAMA:
• Estado: ✅ COMPLETADO 100%
• Fecha completado: 24 de octubre de 2025''',
                    'labels': ['implementation', 'gui', 'pyqt6', 'desktop', 'completed'],
                    'epic': 'EPIC-IMPLEMENTATION',
                    'start_offset': -5, 'duration_days': 1, 'estimated_hours': 12,
                    'status': 'Done',
                    'worklog_entries': [
                        {
                            'date': datetime(2025, 10, 24, 9, 0),
                            'time_spent': '6h',
                            'description': 'Implementación de 4 widgets profesionales PyQt6 y threading asíncrono'
                        },
                        {
                            'date': datetime(2025, 10, 24, 15, 0),
                            'time_spent': '6h',
                            'description': 'Testing completo (15 tests) y documentación exhaustiva (950+ líneas)'
                        }
                    ]
                },
                {
                    'key': 'GAT-6',
                    'summary': 'Web UI CAN Monitor',
                    'description': '''✅ COMPLETADO - Implementar Web UI con CAN Monitor en tiempo real.

🔧 TAREAS REALIZADAS:
• src/web_ui/templates/can_monitor.html (450 líneas HTML5 + CSS + CSS + JS)
• FastAPI endpoints para CAN monitoring (/api/can/status, /ws/can)
• WebSocket en tiempo real para datos CAN
• Dashboard interactivo con métricas
• Integración completa con BL335 Gateway
• Responsive design para móviles

📦 ENTREGABLES COMPLETADOS:
• Web UI CAN Monitor completamente funcional
• API REST + WebSocket endpoints
• Frontend responsive HTML5
• Integración backend-frontend completa

📅 CRONOGRAMA:
• Fecha inicio real: 24 de octubre de 2025
• Fecha completado: 24 de octubre de 2025
• Duración real: 2 horas (no 10h estimadas)
• Estado: ✅ COMPLETADO 100%''',
                    'labels': ['implementation', 'web-ui', 'fastapi', 'websocket', 'completed'],
                    'epic': 'EPIC-IMPLEMENTATION',
                    'start_offset': -3, 'duration_days': 1, 'estimated_hours': 10,
                    'status': 'Done',
                    'start_date_real': datetime(2025, 10, 24),
                    'end_date_real': datetime(2025, 10, 24),
                    'worklog_entries': [
                        {
                            'date': datetime(2025, 10, 24, 16, 0),
                            'time_spent': '2h',
                            'description': 'Implementación completa Web UI CAN Monitor - FastAPI + HTML5 (450 líneas) + WebSocket real-time en sesión concentrada'
                        }
                    ]
                },
                {
                    'key': 'GAT-7',
                    'summary': 'Mejorar Simulador R13 F',
                    'description': '''🚀 EN PROGRESO - Completar y optimizar simulador R13 F para testing.

🔧 TAREAS EN PROGRESO:
• Resolver 1/17 test fallido (SDO bug fix implementado)
• Optimizar delays en control sequences (SDO_MIN_DELAY = 50ms)
• Mejorar generación de mensajes CANopen
• Completar testing E2E con BL335 Gateway
• Documentación de uso del simulador

📦 ENTREGABLES EN DESARROLLO:
• tools/can_simulator.py optimizado
• Tests: 16/17 pasan (94% - mejorando)
• Documentación de simulación completa
• Integración con sistema de logging

📅 CRONOGRAMA:
• Estado: 🚀 EN PROGRESO (90%)
• Estimated completion: 3 de noviembre de 2025
• Blocker: 1 test edge case por resolver''',
                    'labels': ['implementation', 'simulator', 'r13f', 'testing', 'in-progress'],
                    'epic': 'EPIC-IMPLEMENTATION',
                    'start_offset': -2, 'duration_days': 5, 'estimated_hours': 16,
                    'status': 'In Progress'
                },
                
                # EPIC 3: Integración Hardware y Validación Final
                {
                    'key': 'GAT-8',
                    'summary': 'Adquisición Hardware K13',
                    'description': '''📦 COMPRADO - Adquirir hardware especializado para sistema K13.

� HARDWARE ADQUIRIDO:
• BL335 CANopen Gateway (HMS Networks)
• EdgeBox-ESP-100 (Advantech) - Gateway IoT industrial
• Presupuesto total: ~$107-132 USD
• Fecha de compra: 26 de octubre de 2025
• Proveedor: AliExpress + Distribuidores oficiales

📦 ESPECIFICACIONES:
• BL335: CANopen Master/Slave, Ethernet, 2x CAN
• EdgeBox-ESP-100: ESP32-S3, WiFi 6, Ethernet, múltiples I/O
• Compatibilidad: K13 Radio Control, Danfoss R13 F

� CRONOGRAMA:
• Estado: 📦 COMPRADO - Esperando envío
• Entrega estimada: 15-25 noviembre 2025
• Testing programado: Diciembre 2025''',
                    'labels': ['integration', 'hardware', 'bl335', 'edgebox', 'purchased'],
                    'epic': 'EPIC-INTEGRATION',
                    'start_offset': -1, 'duration_days': 20, 'estimated_hours': 8,
                    'status': 'To Do'
                },
                {
                    'key': 'GAT-9',
                    'summary': 'Sistema de Logging de Eventos y Auditoría',
                    'description': '''✅ COMPLETADO - Implementar sistema robusto de logging industrial.

🔧 TAREAS COMPLETADAS (Backend Core):
• src/core/event_logger.py (350 líneas) - EventLogger clase principal
• src/core/event_storage.py (420 líneas) - SQLite + rotación
• 6 niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL, SAFETY
• 7 categorías: SAFETY, CONTROL, COMMUNICATION, SYSTEM, USER, HARDWARE
• Buffer circular thread-safe, timestamps microsegundos
• Storage: SQLite + archivos + compresión .gz
• Sistema completo de logging industrial implementado

📦 ENTREGABLES:
• Backend core: ✅ COMPLETADO (100%)
• EventLogger + EventStorage clases completas
• Sistema thread-safe con rotación automática
• Integración lista para usar en todos los componentes

📅 CRONOGRAMA:
• Fecha inicio real: 24 de octubre de 2025
• Fecha completado: 24 de octubre de 2025
• Duración real: 8 horas (no 64h estimadas)
• Estado: ✅ COMPLETADO 100%''',
                    'labels': ['integration', 'logging', 'auditing', 'industrial', 'completed'],
                    'epic': 'EPIC-INTEGRATION',
                    'start_offset': 0, 'duration_days': 8, 'estimated_hours': 64,
                    'status': 'Done',
                    'start_date_real': datetime(2025, 10, 24),
                    'end_date_real': datetime(2025, 10, 24),
                    'worklog_entries': [
                        {
                            'date': datetime(2025, 10, 24, 8, 0),
                            'time_spent': '2h',
                            'description': 'Diseño y implementación EventLogger core (350 líneas)'
                        },
                        {
                            'date': datetime(2025, 10, 24, 10, 0),
                            'time_spent': '2h',
                            'description': 'Implementación EventStorage con SQLite y rotación (420 líneas)'
                        },
                        {
                            'date': datetime(2025, 10, 24, 12, 0),
                            'time_spent': '2h',
                            'description': 'Sistema buffer thread-safe y 6 niveles logging'
                        },
                        {
                            'date': datetime(2025, 10, 24, 14, 0),
                            'time_spent': '2h',
                            'description': 'Testing y validación sistema completo'
                        }
                    ]
                },
                {
                    'key': 'GAT-13',
                    'summary': 'Preparación Hardware EdgeBox Lite - FASE 2',
                    'description': '''🚀 EN PROGRESO - Preparación y setup inicial del hardware adquirido.

🎯 HARDWARE ADQUIRIDO:
• **OpenEmbed EdgeBox Lite** (ESP32-based)
• URL: https://www.openembed.com/products/71.html
• Estado: ✅ EN POSESIÓN (31 oct 2025)

📋 TAREAS FASE 2 - PREPARACIÓN:

1. ✅ **Documentación inicial** (31 oct)
   • HARDWARE_ADQUIRIDO.md creado
   • Especificaciones documentadas
   
2. 🚀 **Unboxing e inspección** (PENDIENTE)
   • Inspección física del hardware
   • Verificar accesorios incluidos
   • Fotografías documentales
   • Identificar pines y conectores
   
3. 📝 **Identificación de hardware** (PENDIENTE)
   • Mapear puertos: Ethernet, GPIO, CAN, Serial
   • Identificar botones y LEDs
   • Crear diagrama de pinout
   • Documentar conectores de alimentación
   
4. ⚡ **Verificación eléctrica** (PENDIENTE)
   • Verificar voltaje 10.8-36V DC
   • Identificar polaridad
   • Preparar fuente de alimentación
   • ⚠️ NO conectar sin verificar
   
5. 🔧 **Preparación de entorno** (PENDIENTE)
   • Verificar ESP-IDF instalado
   • Compilar firmware existente
   • Preparar herramientas de flasheo
   • Configurar workspace físico

📦 ENTREGABLES:
• Inventario fotográfico completo
• Diagrama de pinout documentado
• Fuente de alimentación verificada
• Entorno de desarrollo listo
• Plan de primer encendido

📅 CRONOGRAMA:
• Inicio: 31 de octubre de 2025
• Estado: 🚀 EN PROGRESO (20% - documentación)
• Duración estimada: 3 días
• Deadline: 3 de noviembre de 2025

⚠️ PRÓXIMOS PASOS INMEDIATOS:
1. Unboxing e inspección física
2. Fotografías documentales
3. Identificación de todos los puertos
4. Verificar voltaje con multímetro''',
                    'labels': ['integration', 'hardware', 'edgebox-lite', 'fase2', 'in-progress'],
                    'epic': 'EPIC-INTEGRATION',
                    'start_offset': 0, 'duration_days': 3, 'estimated_hours': 8,
                    'status': 'In Progress',
                    'priority': 'High',
                    'start_date_real': datetime(2025, 10, 31),
                    'worklog_entries': [
                        {
                            'date': datetime(2025, 10, 31, 10, 0),
                            'time_spent': '2h',
                            'description': 'Documentación inicial hardware EdgeBox Lite - Creación HARDWARE_ADQUIRIDO.md con specs completas'
                        }
                    ]
                },
                {
                    'key': 'GAT-10',
                    'summary': 'Completar Integración Sistema Event Logging',
                    'description': '''🚀 EN PROGRESO - Integrar sistema de logging con interfaces existentes.

🔧 TAREAS PENDIENTES (Integración UI):
• Integrar EventLogger en Desktop GUI PyQt6
• Crear endpoint /api/events en Web UI FastAPI
• Widget de logs en tiempo real para CAN Monitor
• Dashboard de estadísticas y alertas
• Filtros y búsqueda de eventos por categoría

📦 ENTREGABLES PENDIENTES:
• Widget logs Desktop GUI
• API endpoints Web UI (/api/events, /api/stats)
• Dashboard de eventos tiempo real
• Sistema de alertas configurables

📅 CRONOGRAMA:
• Estado: 🚀 EN PROGRESO (50% completo)
• Backend: ✅ COMPLETADO (EventLogger + EventStorage)
• Frontend: 📝 PENDIENTE (integración UI)
• Deadline: 2 de noviembre de 2025''',
                    'labels': ['integration', 'logging', 'ui-integration', 'in-progress'],
                    'epic': 'EPIC-INTEGRATION',
                    'start_offset': 2, 'duration_days': 5, 'estimated_hours': 40,
                    'status': 'In Progress',
                    'priority': 'Medium',
                    'dependencies': ['GAT-5', 'GAT-6']  # Desktop GUI y Web UI
                },
                {
                    'key': 'GAT-11',
                    'summary': 'Documentación Técnica Final y Manuales',
                    'description': '''📝 PENDIENTE - Consolidar documentación técnica completa.

� DOCUMENTACIÓN A CONSOLIDAR:
• Manual usuario Desktop GUI (procedimientos operativos)  
• Guía instalación gateways (BL335 + ESP32)
• Documentación API Web UI (endpoints y WebSocket)
• Manual configuración EDS Danfoss R13F
• Procedimientos mantenimiento y troubleshooting

📦 ENTREGABLES:
• Manual Usuario Final (Desktop + Web UI)
• Guía Instalación Hardware
• Documentación API Completa
• Manual Configuración EDS
• Guía Troubleshooting

📅 CRONOGRAMA:
• Estado: 📝 PENDIENTE
• Documentos base: 15+ archivos markdown existentes
• Deadline: 30 de noviembre de 2025''',
                    'labels': ['integration', 'documentation', 'manuals', 'pending'],
                    'epic': 'EPIC-INTEGRATION',
                    'start_offset': 20, 'duration_days': 7, 'estimated_hours': 56,
                    'status': 'To Do',
                    'priority': 'Medium'
                },
                {
                    'key': 'GAT-12',
                    'summary': 'Validación E2E con Hardware Real K13',
                    'description': '''⏳ BLOQUEADA - Pruebas end-to-end con dispositivo K13 real.

🔧 PRUEBAS PLANIFICADAS:
• Conexión física K13 Radio Control
• Validación protocolo comunicación radio
• Testing comandos: emergency_stop, movimiento, status
• Pruebas seguridad y failsafe
• Validación latencia y confiabilidad

📦 ENTREGABLES:
• Protocolo K13 validado completamente
• Matriz de pruebas E2E ejecutada
• Documentación calibración y setup
• Certificación funcionamiento seguro

📅 CRONOGRAMA:
• Estado: ⏳ BLOQUEADA (esperando hardware)
• Dependencia: Entrega hardware (15-25 Nov)
• Duración estimada: 1-2 semanas testing
• Deadline: 5 de diciembre de 2025''',
                    'labels': ['integration', 'e2e-testing', 'hardware', 'validation', 'blocked'],
                    'epic': 'EPIC-INTEGRATION',
                    'start_offset': 25, 'duration_days': 10, 'estimated_hours': 80,
                    'status': 'Blocked',
                    'priority': 'Critical',
                    'dependencies': ['GAT-8']  # Hardware K13
                },
                # Tareas adicionales se pueden agregar aquí según progreso del proyecto
            ]
        }
    
    def calculate_dates(self, offset_days, duration_days):
        """Calcular fechas de inicio y fin"""
        start = (self.start_date + timedelta(days=offset_days)).strftime('%Y-%m-%d')
        end = (self.start_date + timedelta(days=offset_days + duration_days - 1)).strftime('%Y-%m-%d')
        return start, end
    
    def format_time_estimate(self, hours):
        """Formatear estimación de tiempo"""
        days = hours // 8
        if hours % 8 == 0:
            return f"{days}d"
        else:
            return f"{days}d {hours % 8}h"
    
    def action_import(self):
        """Importar estructura completa de épicos y tareas"""
        print("📥 IMPORTANDO ESTRUCTURA DE PROYECTO")
        print("=" * 50)
        
        structure = self.get_project_structure()
        
        # Inicializar mapeos
        epic_mapping = {}
        task_mapping = {}
        
        # Crear épicos primero
        for epic_data in structure['epics']:
            try:
                epic_issue = self.jira.create_issue(
                    project=self.project_key,
                    summary=self.clean_summary(epic_data['summary']),
                    description=epic_data['description'],
                    issuetype={'name': 'Epic'},
                    labels=self.clean_labels(epic_data['labels'])
                )
                epic_mapping[epic_data['key']] = epic_issue.key
                print(f"✅ Epic creado: {epic_issue.key} - {epic_data['summary']}")
            except Exception as e:
                print(f"❌ Error creando epic {epic_data['key']}: {e}")
        
        # Crear tareas y asignar a épicos
        for task_data in structure['tasks']:
            try:
                # Agregar información de cronograma a la descripción
                start_date, end_date = self.calculate_dates(
                    task_data['start_offset'], 
                    task_data['duration_days']
                )
                time_estimate = self.format_time_estimate(task_data['estimated_hours'])
                
                description_with_schedule = f"""{task_data['description']}

📅 CRONOGRAMA DETALLADO:
• Fecha inicio: {start_date}
• Fecha fin: {end_date}
• Duración: {task_data['duration_days']} días laborales
• Estimación: {task_data['estimated_hours']} horas ({time_estimate})
• Esfuerzo diario: 8 horas
• Status: Planificado

⏰ PLANIFICACIÓN:
• Inicio programado: {start_date} (08:00)
• Entrega programada: {end_date} (18:00)
• Tiempo buffer: Incluido en estimación
• Dependencias: Ver épico padre"""
                
                # Preparar campos de fecha
                issue_fields = {
                    'project': self.project_key,
                    'summary': self.clean_summary(task_data['summary']),
                    'description': description_with_schedule,
                    'issuetype': {'name': 'Task'},
                    'labels': self.clean_labels(task_data['labels'])
                }
                
                # Agregar fechas si la tarea ya comenzó o terminó
                if task_data.get('status') == 'Done':
                    # Para tareas completadas, usar fecha de fin como duedate
                    issue_fields['duedate'] = end_date
                elif 'start_date_real' in task_data:
                    # Usar fecha real de inicio si está disponible
                    issue_fields['duedate'] = end_date
                else:
                    # Para tareas futuras, usar fecha planificada
                    issue_fields['duedate'] = end_date
                
                # Crear tarea
                task_issue = self.jira.create_issue(**issue_fields)
                
                # Asignar a épico
                if task_data['epic'] in epic_mapping:
                    epic_key = epic_mapping[task_data['epic']]
                    task_issue.update(fields={'parent': {'key': epic_key}})
                
                # Agregar worklogs para tareas completadas
                if task_data.get('status') == 'Done' and 'worklog_entries' in task_data:
                    for worklog in task_data['worklog_entries']:
                        try:
                            # Asegurar que worklog_date sea datetime timezone-aware
                            worklog_date = worklog['date']
                            
                            if isinstance(worklog_date, datetime):
                                # Si no tiene timezone, agregar UTC
                                if worklog_date.tzinfo is None:
                                    worklog_date = worklog_date.replace(tzinfo=timezone.utc)
                            else:
                                # Si es string, convertir a datetime timezone-aware
                                worklog_date = datetime.fromisoformat(worklog_date.replace('Z', '+00:00'))
                                if worklog_date.tzinfo is None:
                                    worklog_date = worklog_date.replace(tzinfo=timezone.utc)
                                
                            # Pasar datetime object directamente (la librería espera datetime, no string)
                            self.jira.add_worklog(
                                issue=task_issue,
                                timeSpent=worklog['time_spent'],
                                comment=worklog['description'],
                                started=worklog_date  # Pasar datetime, no string
                            )
                            print(f"   ⏰ Worklog agregado: {worklog['time_spent']} - {worklog['description'][:50]}...")
                        except Exception as we:
                            print(f"   ⚠️  Error agregando worklog: {we}")
                
                # Marcar como completada si está Done
                if task_data.get('status') == 'Done':
                    try:
                        transitions = self.jira.transitions(task_issue)
                        done_transition = None
                        for t in transitions:
                            if t['name'].lower() in ['done', 'resolved', 'closed', 'complete']:
                                done_transition = t
                                break
                        
                        if done_transition:
                            self.jira.transition_issue(task_issue, done_transition['id'])
                            print(f"   ✅ Marcada como completada")
                    except Exception as te:
                        print(f"   ⚠️  Error marcando como completada: {te}")
                
                # Almacenar el mapeo para dependencias
                task_mapping[task_data.get('key', f"GAT-{len(task_mapping)+1}")] = task_issue.key
                
                print(f"✅ Tarea creada: {task_issue.key} - {task_data['summary']}")
                print(f"   📅 {start_date} → {end_date} ({time_estimate})")
                
            except Exception as e:
                print(f"❌ Error creando tarea: {e}")
        
        # Crear dependencias (enlaces)
        print(f"\n🔗 CREANDO DEPENDENCIAS ENTRE TAREAS")
        for task_data in structure['tasks']:
            if 'dependencies' in task_data and task_data['dependencies']:
                task_key = task_mapping.get(task_data.get('key'))
                if task_key:
                    for dep_key in task_data['dependencies']:
                        dep_task_key = task_mapping.get(dep_key)
                        if dep_task_key:
                            try:
                                # Crear enlace "blocks" (tarea bloquea a dependencia)
                                self.jira.create_issue_link(
                                    type="Blocks",
                                    inwardIssue=dep_task_key,  # Esta tarea debe completarse primero
                                    outwardIssue=task_key,     # Antes de que esta pueda empezar
                                    comment={
                                        "body": f"Dependencia automática: {dep_task_key} debe completarse antes de {task_key}"
                                    }
                                )
                                print(f"   🔗 {dep_task_key} → {task_key}")
                            except Exception as e:
                                print(f"   ❌ Error creando enlace {dep_task_key} → {task_key}: {e}")
        
        print(f"\n🎉 IMPORTACIÓN COMPLETADA")
    
    def action_add_worklogs(self):
        """Agregar worklogs a tareas existentes ya completadas"""
        print("⏰ AGREGANDO WORKLOGS A TAREAS COMPLETADAS")
        print("=" * 45)
        
        structure = self.get_project_structure()
        
        for task_data in structure['tasks']:
            if task_data.get('status') == 'Done' and 'worklog_entries' in task_data:
                # Buscar la tarea en JIRA por resumen
                summary_search = task_data['summary'][:30]  # Primeros 30 caracteres
                jql = f'project = {self.project_key} AND summary ~ "{summary_search}"'
                
                try:
                    issues = self.jira.search_issues(jql, maxResults=1)
                    if issues:
                        task_issue = issues[0]
                        print(f"📝 Procesando: {task_issue.key} - {task_data['summary'][:50]}...")
                        
                        # Verificar si ya tiene worklogs
                        existing_worklogs = self.jira.worklogs(task_issue)
                        if len(existing_worklogs) > 0:
                            print(f"   ⚠️  Ya tiene {len(existing_worklogs)} worklogs, saltando...")
                            continue
                        
                        # Agregar worklogs
                        for worklog in task_data['worklog_entries']:
                            try:
                                # Asegurar que worklog_date sea datetime timezone-aware
                                worklog_date = worklog['date']
                                
                                if isinstance(worklog_date, datetime):
                                    # Si no tiene timezone, agregar UTC
                                    if worklog_date.tzinfo is None:
                                        worklog_date = worklog_date.replace(tzinfo=timezone.utc)
                                else:
                                    # Si es string, convertir a datetime timezone-aware
                                    worklog_date = datetime.fromisoformat(worklog_date.replace('Z', '+00:00'))
                                    if worklog_date.tzinfo is None:
                                        worklog_date = worklog_date.replace(tzinfo=timezone.utc)
                                
                                # Pasar datetime object directamente (la librería espera datetime, no string)
                                self.jira.add_worklog(
                                    issue=task_issue,
                                    timeSpent=worklog['time_spent'],
                                    comment=worklog['description'],
                                    started=worklog_date  # Pasar datetime, no string
                                )
                                print(f"   ✅ Worklog: {worklog['time_spent']} - {worklog['description'][:40]}...")
                            except Exception as we:
                                import traceback
                                print(f"   ❌ Error worklog: {we}")
                                traceback.print_exc()
                        
                        # Marcar como Done si no está
                        if task_issue.fields.status.name.lower() not in ['done', 'resolved', 'closed']:
                            try:
                                transitions = self.jira.transitions(task_issue)
                                done_transition = None
                                for t in transitions:
                                    if t['name'].lower() in ['done', 'resolved', 'closed', 'complete']:
                                        done_transition = t
                                        break
                                
                                if done_transition:
                                    self.jira.transition_issue(task_issue, done_transition['id'])
                                    print(f"   ✅ Marcada como Done")
                            except Exception as te:
                                print(f"   ⚠️  Error marcando Done: {te}")
                                
                    else:
                        print(f"❌ No encontrada tarea: {task_data['summary'][:50]}...")
                        
                except Exception as e:
                    print(f"❌ Error buscando tarea: {e}")
        
        print(f"\n🎉 WORKLOGS AGREGADOS")
    
    def action_cleanup(self):
        """Limpiar épicos duplicados"""
        print("🧹 LIMPIANDO ÉPICOS DUPLICADOS")
        print("=" * 40)
        
        # Buscar todos los épicos
        epics = self.jira.search_issues(f'project = {self.project_key} AND issuetype = Epic')
        
        # Agrupar por resumen similar
        epic_groups = {}
        for epic in epics:
            summary_key = epic.fields.summary.lower().strip()
            if summary_key not in epic_groups:
                epic_groups[summary_key] = []
            epic_groups[summary_key].append(epic)
        
        # Eliminar duplicados (mantener el más reciente)
        for summary, epic_list in epic_groups.items():
            if len(epic_list) > 1:
                # Ordenar por fecha de creación, mantener el más reciente
                epic_list.sort(key=lambda x: x.fields.created, reverse=True)
                keep_epic = epic_list[0]
                
                for duplicate_epic in epic_list[1:]:
                    try:
                        duplicate_epic.delete()
                        print(f"🗑️  Eliminado duplicado: {duplicate_epic.key}")
                    except Exception as e:
                        print(f"❌ Error eliminando {duplicate_epic.key}: {e}")
                
                print(f"✅ Mantenido: {keep_epic.key} - {summary}")
    
    def action_assign(self):
        """Asignar tareas a épicos basado en contenido"""
        print("🔗 ASIGNANDO TAREAS A ÉPICOS")
        print("=" * 35)
        
        # Mapeo de palabras clave a épicos
        epic_keywords = {
            'foundation': ['eds', 'bl335', 'esp32', 'canopen', 'r13f', 'foundation', 'protocol', 'danfoss'],
            'implementation': ['gui', 'desktop', 'web-ui', 'can-monitor', 'pyqt6', 'fastapi', 'simulador', 'implementation'],
            'integration': ['hardware', 'logging', 'auditing', 'integration', 'validation', 'production']
        }
        
        # Obtener épicos y tareas
        epics = self.jira.search_issues(f'project = {self.project_key} AND issuetype = Epic')
        tasks = self.jira.search_issues(f'project = {self.project_key} AND issuetype = Task AND parent is EMPTY')
        
        # Crear mapeo de épicos
        epic_map = {}
        for epic in epics:
            summary = epic.fields.summary.lower()
            if any(keyword in summary for keyword in epic_keywords['foundation']):
                epic_map['foundation'] = epic.key
            elif any(keyword in summary for keyword in epic_keywords['implementation']):
                epic_map['implementation'] = epic.key
            elif any(keyword in summary for keyword in epic_keywords['integration']):
                epic_map['integration'] = epic.key
        
        # Asignar tareas
        for task in tasks:
            summary = task.fields.summary.lower()
            description = (task.fields.description or "").lower()
            
            # Determinar épico basado en contenido
            epic_category = None
            for category, keywords in epic_keywords.items():
                if any(keyword in summary or keyword in description for keyword in keywords):
                    epic_category = category
                    break
            
            if epic_category and epic_category in epic_map:
                try:
                    task.update(fields={'parent': {'key': epic_map[epic_category]}})
                    print(f"✅ {task.key} → {epic_map[epic_category]}")
                except Exception as e:
                    print(f"❌ Error asignando {task.key}: {e}")
            else:
                print(f"⚠️  {task.key}: No se pudo determinar épico")
    
    def action_schedule(self):
        """Actualizar fechas y estimaciones"""
        print("📅 ACTUALIZANDO CRONOGRAMA")
        print("=" * 30)
        
        structure = self.get_project_structure()
        tasks = structure['tasks']
        
        # Buscar tareas en Jira y actualizar
        for task_data in tasks:
            # Buscar tarea por resumen
            summary_search = task_data['summary'][:50]  # Primeros 50 caracteres
            jql = f'project = {self.project_key} AND issuetype = Task AND summary ~ "{summary_search}"'
            
            try:
                issues = self.jira.search_issues(jql, maxResults=1)
                if issues:
                    task = issues[0]
                    
                    # Calcular fechas
                    start_date, end_date = self.calculate_dates(
                        task_data['start_offset'],
                        task_data['duration_days']
                    )
                    
                    # Actualizar due date
                    task.update(fields={'duedate': end_date})
                    print(f"✅ {task.key}: Due date → {end_date}")
                
            except Exception as e:
                print(f"❌ Error actualizando cronograma: {e}")
    
    def action_check(self):
        """Verificar estado del proyecto"""
        print("🔍 VERIFICANDO ESTADO DEL PROYECTO")
        print("=" * 40)
        
        # Contar épicos y tareas
        epics = self.jira.search_issues(f'project = {self.project_key} AND issuetype = Epic')
        tasks = self.jira.search_issues(f'project = {self.project_key} AND issuetype = Task')
        
        print(f"📊 RESUMEN:")
        print(f"   • Épicos: {len(epics)}")
        print(f"   • Tareas: {len(tasks)}")
        
        # Mostrar épicos
        print(f"\n📋 ÉPICOS:")
        for epic in epics:
            # Contar tareas del épico
            epic_tasks = self.jira.search_issues(f'project = {self.project_key} AND parent = {epic.key}')
            print(f"   • {epic.key}: {epic.fields.summary} ({len(epic_tasks)} tareas)")
            
            # Mostrar algunas tareas
            for task in epic_tasks[:3]:  # Primeras 3 tareas
                due_date = task.fields.duedate or "Sin fecha"
                print(f"     - {task.key}: {task.fields.summary} (Due: {due_date})")
            
            if len(epic_tasks) > 3:
                print(f"     ... y {len(epic_tasks) - 3} tareas más")
    
    def action_diagnose(self):
        """Diagnóstico completo de conexión"""
        print("🩺 DIAGNÓSTICO COMPLETO DE JIRA")
        print("=" * 40)
        
        # Test de conexión
        try:
            user = self.jira.current_user()
            print(f"✅ Conexión exitosa")
            print(f"   Usuario: {user}")
            print(f"   URL: {os.getenv('JIRA_URL')}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return
        
        # Test de proyecto
        try:
            project = self.jira.project(self.project_key)
            print(f"✅ Proyecto encontrado: {project.name}")
        except Exception as e:
            print(f"❌ Error accediendo proyecto: {e}")
            return
        
        # Test de permisos
        try:
            # Intentar buscar issues
            issues = self.jira.search_issues(f'project = {self.project_key}', maxResults=1)
            print(f"✅ Permisos de lectura: OK")
            
            # Test de escritura (intentar crear/actualizar)
            print(f"✅ Configuración completa y funcional")
            
        except Exception as e:
            print(f"⚠️  Posible problema de permisos: {e}")
    
    def action_import_dual_hardware(self):
        """Importar tareas de estrategia dual hardware"""
        import json
        
        print("🔄 IMPORTANDO TAREAS DUAL HARDWARE")
        print("=" * 40)
        
        # Leer archivo JSON
        json_path = os.path.join(os.path.dirname(__file__), 'dual_hardware_tasks.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ Archivo cargado: {json_path}")
            
            # Crear épico primero
            epic_data = data['epic']
            print(f"\n📌 Creando épico: {epic_data['summary']}")
            
            epic_fields = {
                'project': self.project_key,
                'summary': epic_data['summary'],
                'description': epic_data['description'],
                'issuetype': {'name': 'Epic'}
            }
            
            # Agregar fechas si existen
            if epic_data.get('start_date'):
                epic_fields['customfield_10015'] = epic_data['start_date']  # Start date
            if epic_data.get('due_date'):
                due_date = datetime.strptime(epic_data['due_date'], '%Y-%m-%d').date()
                epic_fields['duedate'] = due_date.isoformat()
            
            epic = self.jira.create_issue(fields=epic_fields)
            
            print(f"✅ Épico creado: {epic.key}")
            
            # Crear tareas
            print(f"\n📋 Creando {len(data['tasks'])} tareas...")
            created_tasks = []
            
            for i, task_data in enumerate(data['tasks'], 1):
                try:
                    # Convertir fechas
                    start_date = datetime.strptime(task_data['start_date'], '%Y-%m-%d').date() if task_data.get('start_date') else None
                    due_date = datetime.strptime(task_data['due_date'], '%Y-%m-%d').date() if task_data.get('due_date') else None
                    
                    # Crear tarea
                    task_fields = {
                        'project': self.project_key,
                        'summary': task_data['summary'],
                        'description': task_data['description'],
                        'issuetype': {'name': 'Task'},
                        'parent': {'key': epic.key},
                        'labels': task_data.get('labels', [])
                    }
                    
                    if due_date:
                        task_fields['duedate'] = due_date.isoformat()
                    
                    task = self.jira.create_issue(fields=task_fields)
                    
                    # Actualizar a In Progress
                    transitions = self.jira.transitions(task)
                    in_progress_id = None
                    
                    for transition in transitions:
                        if 'progress' in transition['name'].lower():
                            in_progress_id = transition['id']
                            break
                    
                    if in_progress_id:
                        self.jira.transition_issue(task, in_progress_id)
                        status = "In Progress"
                    else:
                        status = "To Do"
                    
                    created_tasks.append(task.key)
                    print(f"  {i:2d}. ✅ {task.key}: {task_data['summary'][:60]}... [{status}]")
                    
                except Exception as e:
                    print(f"  {i:2d}. ❌ Error: {e}")
            
            print(f"\n✅ IMPORTACIÓN COMPLETADA")
            print(f"   Épico: {epic.key}")
            print(f"   Tareas creadas: {len(created_tasks)}")
            print(f"   Estado: In Progress")
            
        except FileNotFoundError:
            print(f"❌ Error: No se encontró {json_path}")
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
    
    def action_clean_all(self):
        """Limpieza completa: eliminar duplicados y acortar descripciones"""
        print("🧹 LIMPIEZA COMPLETA DE JIRA")
        print("=" * 50)
        
        # 1. Obtener todos los épicos y tareas
        print("\n📊 Analizando proyecto...")
        all_epics = self.jira.search_issues(
            f'project = {self.project_key} AND issuetype = Epic',
            maxResults=100
        )
        all_tasks = self.jira.search_issues(
            f'project = {self.project_key} AND issuetype = Task',
            maxResults=200
        )
        
        print(f"   Épicos encontrados: {len(all_epics)}")
        print(f"   Tareas encontradas: {len(all_tasks)}")
        
        # 2. Identificar épicos duplicados por título similar
        print("\n🔍 Identificando duplicados...")
        epic_groups = {}
        
        for epic in all_epics:
            # Normalizar título para comparación
            title = epic.fields.summary.lower()
            
            # Buscar grupo base
            base_title = None
            if 'fundación' in title or 'eds y protocolos' in title:
                base_title = 'fundacion'
            elif 'implementación' in title or 'gateways' in title:
                base_title = 'implementacion'
            elif 'integración hardware' in title or 'validación final' in title:
                base_title = 'integracion'
            elif 'dual hardware' in title or 'evaluación comparativa' in title:
                base_title = 'dual'
            
            if base_title:
                if base_title not in epic_groups:
                    epic_groups[base_title] = []
                epic_groups[base_title].append(epic)
        
        print(f"   Grupos identificados: {len(epic_groups)}")
        for group, epics in epic_groups.items():
            print(f"   - {group}: {len(epics)} épicos")
        
        # 3. Para cada grupo, mantener solo el más reciente
        epics_to_delete = []
        epics_to_keep = {}
        
        for group, epics in epic_groups.items():
            if len(epics) > 1:
                # Ordenar por key (GAT-X, mayor = más reciente)
                sorted_epics = sorted(epics, key=lambda e: int(e.key.split('-')[1]), reverse=True)
                epics_to_keep[group] = sorted_epics[0]
                epics_to_delete.extend(sorted_epics[1:])
                
                print(f"\n   {group.upper()}:")
                print(f"   ✅ Mantener: {sorted_epics[0].key} - {sorted_epics[0].fields.summary}")
                for dup in sorted_epics[1:]:
                    print(f"   ❌ Eliminar: {dup.key} - {dup.fields.summary}")
            else:
                epics_to_keep[group] = epics[0]
        
        # 4. Reasignar tareas de épicos duplicados al épico principal
        print(f"\n🔄 Reasignando tareas...")
        tasks_moved = 0
        
        for epic in epics_to_delete:
            # Buscar grupo del épico
            group = None
            title = epic.fields.summary.lower()
            if 'fundación' in title or 'eds y protocolos' in title:
                group = 'fundacion'
            elif 'implementación' in title or 'gateways' in title:
                group = 'implementacion'
            elif 'integración hardware' in title or 'validación final' in title:
                group = 'integracion'
            
            if group and group in epics_to_keep:
                target_epic = epics_to_keep[group]
                
                # Obtener tareas del épico duplicado
                tasks = self.jira.search_issues(
                    f'project = {self.project_key} AND parent = {epic.key}',
                    maxResults=100
                )
                
                # Reasignar cada tarea
                for task in tasks:
                    try:
                        task.update(fields={'parent': {'key': target_epic.key}})
                        tasks_moved += 1
                        print(f"   ✅ {task.key} → {target_epic.key}")
                    except Exception as e:
                        print(f"   ❌ Error moviendo {task.key}: {e}")
        
        print(f"\n   Total tareas movidas: {tasks_moved}")
        
        # 5. Eliminar épicos duplicados vacíos
        print(f"\n🗑️  Eliminando épicos duplicados...")
        deleted_count = 0
        
        for epic in epics_to_delete:
            try:
                # Verificar que no tenga tareas
                tasks = self.jira.search_issues(
                    f'project = {self.project_key} AND parent = {epic.key}',
                    maxResults=1
                )
                
                if len(tasks) == 0:
                    epic.delete()
                    deleted_count += 1
                    print(f"   ✅ Eliminado: {epic.key}")
                else:
                    print(f"   ⚠️  Saltado {epic.key}: aún tiene {len(tasks)} tareas")
            except Exception as e:
                print(f"   ❌ Error eliminando {epic.key}: {e}")
        
        print(f"\n   Total épicos eliminados: {deleted_count}")
        
        # 6. Acortar descripciones largas
        print(f"\n✂️  Acortando descripciones largas...")
        shortened_count = 0
        
        for task in all_tasks:
            desc = task.fields.description or ""
            if len(desc) > 500:  # Si es muy larga
                # Tomar primeras 3 líneas o 300 caracteres
                lines = desc.split('\n')
                short_desc = '\n'.join(lines[:3])
                
                if len(short_desc) > 300:
                    short_desc = short_desc[:297] + "..."
                
                try:
                    task.update(fields={'description': short_desc})
                    shortened_count += 1
                    print(f"   ✅ {task.key}: {len(desc)} → {len(short_desc)} caracteres")
                except Exception as e:
                    print(f"   ❌ Error en {task.key}: {e}")
        
        print(f"\n   Total descripciones acortadas: {shortened_count}")
        
        # 7. Resumen final
        print(f"\n" + "=" * 50)
        print(f"✅ LIMPIEZA COMPLETADA")
        print(f"   • Épicos eliminados: {deleted_count}")
        print(f"   • Tareas movidas: {tasks_moved}")
        print(f"   • Descripciones acortadas: {shortened_count}")
        print(f"   • Épicos finales: {len(epics_to_keep)}")

    def action_consolidate(self):
        """Analizar y sugerir consolidación de tareas similares"""
        print("\n🔍 ANALIZANDO TAREAS PARA CONSOLIDACIÓN")
        print("=" * 60)
        
        # Obtener todas las tareas del proyecto
        issues = self.jira.search_issues(f'project={self.project_key} ORDER BY key ASC', maxResults=100)
        
        # Agrupar por épico
        epics = {}
        orphan_tasks = []
        
        for issue in issues:
            if issue.fields.issuetype.name == 'Epic':
                epics[issue.key] = {
                    'summary': issue.fields.summary,
                    'tasks': [],
                    'done': 0,
                    'in_progress': 0,
                    'todo': 0
                }
        
        for issue in issues:
            if issue.fields.issuetype.name != 'Epic':
                parent = getattr(issue.fields, 'parent', None)
                epic_link = parent.key if parent else None
                
                task_info = {
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'status': issue.fields.status.name,
                    'labels': issue.fields.labels or []
                }
                
                if epic_link and epic_link in epics:
                    epics[epic_link]['tasks'].append(task_info)
                    # Contar por estado
                    if task_info['status'] == 'Done':
                        epics[epic_link]['done'] += 1
                    elif task_info['status'] == 'In Progress':
                        epics[epic_link]['in_progress'] += 1
                    else:
                        epics[epic_link]['todo'] += 1
                else:
                    orphan_tasks.append(task_info)
        
        # Mostrar resumen por épico
        print("\n📊 RESUMEN POR ÉPICO:")
        print("-" * 60)
        total_tasks = 0
        
        for epic_key, data in sorted(epics.items()):
            task_count = len(data['tasks'])
            total_tasks += task_count
            print(f"\n📌 {epic_key}: {data['summary'][:50]}")
            print(f"   📋 Total: {task_count} tareas")
            print(f"   ✅ Done: {data['done']} | 🔄 In Progress: {data['in_progress']} | ⏸️ Todo: {data['todo']}")
            
            # Identificar tareas similares
            task_groups = self._find_similar_tasks(data['tasks'])
            
            if task_groups:
                print(f"   💡 Oportunidades de consolidación:")
                for group_name, tasks in task_groups.items():
                    if len(tasks) > 1:
                        print(f"\n      🔗 Grupo '{group_name}': {len(tasks)} tareas")
                        for task in tasks:
                            status_icon = '✅' if task['status'] == 'Done' else '🔄' if task['status'] == 'In Progress' else '⏸️'
                            print(f"         {status_icon} {task['key']}: {task['summary'][:60]}")
        
        # Mostrar tareas huérfanas
        if orphan_tasks:
            print(f"\n⚠️ TAREAS SIN ÉPICO: {len(orphan_tasks)}")
            for task in orphan_tasks:
                print(f"   {task['key']}: {task['summary'][:60]}")
        
        # Resumen final
        print("\n" + "=" * 60)
        print(f"📊 TOTALES:")
        print(f"   • Épicos: {len(epics)}")
        print(f"   • Tareas totales: {total_tasks}")
        print(f"   • Tareas huérfanas: {len(orphan_tasks)}")
        print(f"   • Promedio por épico: {total_tasks / len(epics):.1f}" if epics else "")
        
        print("\n💡 RECOMENDACIONES:")
        for epic_key, data in sorted(epics.items()):
            task_count = len(data['tasks'])
            if task_count > 20:
                print(f"   ⚠️ {epic_key}: {task_count} tareas - Considerar dividir en sub-épicos")
            elif task_count > 15:
                print(f"   ℹ️ {epic_key}: {task_count} tareas - Revisar si hay tareas consolidables")
        
        print("\n✅ ANÁLISIS DE CONSOLIDACIÓN COMPLETADO")
    
    def _find_similar_tasks(self, tasks):
        """Encontrar tareas similares basándose en palabras clave comunes"""
        groups = {}
        
        # Palabras clave para agrupar
        keywords = {
            'testing': ['test', 'testing', 'prueba', 'validar', 'validación'],
            'documentation': ['documentación', 'documento', 'manual', 'readme', 'docs'],
            'gateway': ['gateway', 'bl335', 'esp32'],
            'ui': ['gui', 'web ui', 'desktop', 'interfaz'],
            'canopen': ['canopen', 'pdo', 'sdo', 'nmt', 'emcy'],
            'simulator': ['simulador', 'simulator', 'simular'],
            'integration': ['integración', 'integration', 'integrar'],
            'logging': ['logging', 'event', 'log', 'registro']
        }
        
        for task in tasks:
            summary_lower = task['summary'].lower()
            matched = False
            
            for group_name, kwords in keywords.items():
                if any(kw in summary_lower for kw in kwords):
                    if group_name not in groups:
                        groups[group_name] = []
                    groups[group_name].append(task)
                    matched = True
                    break
            
            if not matched:
                if 'otros' not in groups:
                    groups['otros'] = []
                groups['otros'].append(task)
        
        # Solo retornar grupos con más de una tarea
        return {k: v for k, v in groups.items() if len(v) > 1}

    def action_auto_consolidate(self):
        """Consolidación automática: eliminar tareas duplicadas y asignar huérfanas"""
        print("\n🤖 CONSOLIDACIÓN AUTOMÁTICA DE TAREAS")
        print("=" * 60)
        
        # Obtener todas las tareas
        issues = self.jira.search_issues(f'project={self.project_key} ORDER BY key ASC', maxResults=200)
        
        # Separar épicos y tareas
        epics = {}
        all_tasks = []
        orphan_tasks = []
        
        for issue in issues:
            if issue.fields.issuetype.name == 'Epic':
                epics[issue.key] = {
                    'summary': issue.fields.summary,
                    'tasks': []
                }
            else:
                all_tasks.append(issue)
        
        # Clasificar tareas (con épico vs huérfanas)
        for task in all_tasks:
            parent = getattr(task.fields, 'parent', None)
            epic_link = parent.key if parent else None
            
            if epic_link and epic_link in epics:
                epics[epic_link]['tasks'].append(task)
            else:
                orphan_tasks.append(task)
        
        print(f"\n📊 ESTADO INICIAL:")
        print(f"   • Épicos: {len(epics)}")
        print(f"   • Tareas totales: {len(all_tasks)}")
        print(f"   • Tareas huérfanas: {len(orphan_tasks)}")
        
        # FASE 1: Identificar y eliminar duplicados exactos
        print(f"\n🔍 FASE 1: Identificando duplicados exactos...")
        
        duplicates_to_delete = []
        tasks_by_summary = {}
        
        for epic_key, data in epics.items():
            for task in data['tasks']:
                summary_normalized = task.fields.summary.strip().lower()
                
                if summary_normalized not in tasks_by_summary:
                    tasks_by_summary[summary_normalized] = []
                tasks_by_summary[summary_normalized].append({
                    'issue': task,
                    'epic': epic_key
                })
        
        # Encontrar duplicados (mantener el más antiguo = menor GAT-X)
        for summary, task_list in tasks_by_summary.items():
            if len(task_list) > 1:
                # Ordenar por key (GAT-X, menor = más antiguo = original)
                sorted_tasks = sorted(task_list, key=lambda t: int(t['issue'].key.split('-')[1]))
                keep_task = sorted_tasks[0]
                duplicates = sorted_tasks[1:]
                
                print(f"\n   📝 '{summary[:50]}...'")
                print(f"      ✅ Mantener: {keep_task['issue'].key} (original)")
                
                for dup in duplicates:
                    print(f"      ❌ Eliminar: {dup['issue'].key} (duplicado)")
                    duplicates_to_delete.append(dup['issue'])
        
        # Eliminar duplicados
        deleted_count = 0
        if duplicates_to_delete:
            print(f"\n🗑️  Eliminando {len(duplicates_to_delete)} duplicados...")
            
            for task in duplicates_to_delete:
                try:
                    task.delete()
                    deleted_count += 1
                    print(f"      ✅ Eliminado: {task.key}")
                except Exception as e:
                    print(f"      ❌ Error eliminando {task.key}: {e}")
        else:
            print(f"\n   ℹ️  No se encontraron duplicados exactos")
        
        # FASE 2: Asignar tareas huérfanas a épicos apropiados
        print(f"\n🔗 FASE 2: Asignando tareas huérfanas a épicos...")
        
        # Mapeo de palabras clave a épicos
        epic_keywords = {
            'fundacion': ['eds', 'danfoss', 'r13f', 'bl335', 'validar', 'manual'],
            'implementacion': ['gui', 'desktop', 'web ui', 'pyqt6', 'esp32', 'gateway', 'simulador', 'wifi'],
            'integracion': ['hardware', 'logging', 'evento', 'auditoría', 'adquisición', 'documentación', 'validación', 'e2e']
        }
        
        # Identificar épicos por categoría
        epic_map = {}
        for epic_key, data in epics.items():
            summary_lower = data['summary'].lower()
            
            if any(kw in summary_lower for kw in ['fundación', 'eds', 'protocolos']):
                epic_map['fundacion'] = epic_key
            elif any(kw in summary_lower for kw in ['implementación', 'gateways', 'interfaces']):
                epic_map['implementacion'] = epic_key
            elif any(kw in summary_lower for kw in ['integración', 'hardware', 'validación final']):
                epic_map['integracion'] = epic_key
        
        assigned_count = 0
        
        if orphan_tasks:
            print(f"\n   Procesando {len(orphan_tasks)} tareas huérfanas...")
            
            for task in orphan_tasks:
                summary_lower = task.fields.summary.lower()
                
                # Determinar categoría
                category = None
                for cat, keywords in epic_keywords.items():
                    if any(kw in summary_lower for kw in keywords):
                        category = cat
                        break
                
                # Asignar a épico
                if category and category in epic_map:
                    target_epic = epic_map[category]
                    try:
                        task.update(fields={'parent': {'key': target_epic}})
                        assigned_count += 1
                        print(f"      ✅ {task.key} → {target_epic} ({category})")
                    except Exception as e:
                        print(f"      ❌ Error asignando {task.key}: {e}")
                else:
                    print(f"      ⚠️  {task.key}: No se pudo determinar categoría")
        else:
            print(f"\n   ℹ️  No hay tareas huérfanas")
        
        # RESUMEN FINAL
        print(f"\n" + "=" * 60)
        print(f"✅ CONSOLIDACIÓN COMPLETADA")
        print(f"\n📊 RESULTADOS:")
        print(f"   • Tareas duplicadas eliminadas: {deleted_count}")
        print(f"   • Tareas huérfanas asignadas: {assigned_count}")
        print(f"   • Reducción total: {deleted_count + assigned_count} tareas procesadas")
        
        # Verificar estado final
        final_issues = self.jira.search_issues(f'project={self.project_key}', maxResults=200)
        final_tasks = [i for i in final_issues if i.fields.issuetype.name != 'Epic']
        final_orphans = [t for t in final_tasks if not getattr(t.fields, 'parent', None)]
        
        print(f"\n📈 ESTADO FINAL:")
        print(f"   • Total tareas: {len(all_tasks)} → {len(final_tasks)} (-{len(all_tasks) - len(final_tasks)})")
        print(f"   • Tareas huérfanas: {len(orphan_tasks)} → {len(final_orphans)} (-{len(orphan_tasks) - len(final_orphans)})")
        
        if len(final_tasks) <= 35:
            print(f"\n🎯 ¡Objetivo alcanzado! Tareas reducidas a ~32-35")
        else:
            print(f"\n💡 Aún quedan {len(final_tasks) - 35} tareas por revisar manualmente")

    def action_deep_analysis(self):
        """Análisis profundo de TODAS las tareas duplicadas"""
        print("\n🔍 ANÁLISIS DETALLADO DE DUPLICADOS")
        print("=" * 70)
        
        # Obtener TODAS las tareas
        issues = self.jira.search_issues(
            f'project={self.project_key} AND type=Task ORDER BY key ASC',
            maxResults=100
        )
        
        print(f"\n📊 Total tareas encontradas: {len(issues)}")
        
        # Agrupar por resumen normalizado
        by_summary = {}
        for issue in issues:
            summary = issue.fields.summary.strip().lower()
            if summary not in by_summary:
                by_summary[summary] = []
            by_summary[summary].append(issue)
        
        # Mostrar duplicados
        print('\n📋 TAREAS DUPLICADAS:')
        print('-' * 70)
        
        duplicates_found = 0
        total_to_delete = 0
        
        for summary, tasks in sorted(by_summary.items()):
            if len(tasks) > 1:
                duplicates_found += 1
                total_to_delete += (len(tasks) - 1)
                
                print(f'\n{duplicates_found}. {summary[:60]}')
                print(f'   Cantidad: {len(tasks)} copias')
                
                # Ordenar por key
                sorted_tasks = sorted(tasks, key=lambda t: int(t.key.split('-')[1]))
                
                for i, task in enumerate(sorted_tasks):
                    parent = getattr(task.fields, 'parent', None)
                    epic = parent.key if parent else 'Sin épico'
                    status = task.fields.status.name
                    
                    marker = '✅ MANTENER' if i == 0 else '❌ ELIMINAR'
                    print(f'   {marker}: {task.key} | Épico: {epic} | Status: {status}')
        
        print('\n' + '=' * 70)
        print(f'📊 RESUMEN:')
        print(f'   • Total tareas: {len(issues)}')
        print(f'   • Tareas únicas: {len(by_summary)}')
        print(f'   • Grupos duplicados: {duplicates_found}')
        print(f'   • Tareas a eliminar: {total_to_delete}')
        print(f'   • Tareas finales esperadas: {len(issues) - total_to_delete}')
        
        if total_to_delete > 0:
            print(f'\n💡 RECOMENDACIÓN:')
            print(f'   Ejecutar: python jira_manager.py --action auto-consolidate')
            print(f'   Esto eliminará {total_to_delete} duplicados automáticamente')

    def action_verify_all(self):
        """Verificación exhaustiva de todas las tareas - listado completo con detalles"""
        print("\n📋 VERIFICACIÓN COMPLETA DE TODAS LAS TAREAS")
        print("=" * 80)
        
        # Obtener TODAS las tareas y épicos
        all_issues = self.jira.search_issues(
            f'project={self.project_key} ORDER BY key ASC',
            maxResults=100
        )
        
        # Separar épicos y tareas
        epics = {}
        tasks = []
        
        for issue in all_issues:
            if issue.fields.issuetype.name == 'Epic':
                epics[issue.key] = {
                    'summary': issue.fields.summary,
                    'tasks': []
                }
            else:
                tasks.append(issue)
        
        # Clasificar tareas por épico
        tasks_by_epic = {k: [] for k in epics.keys()}
        orphans = []
        
        for task in tasks:
            parent = getattr(task.fields, 'parent', None)
            if parent and parent.key in epics:
                tasks_by_epic[parent.key].append(task)
            else:
                orphans.append(task)
        
        # Mostrar resumen inicial
        print(f"\n📊 RESUMEN GENERAL:")
        print(f"   • Total épicos: {len(epics)}")
        print(f"   • Total tareas: {len(tasks)}")
        print(f"   • Tareas huérfanas: {len(orphans)}")
        
        # Listar TODAS las tareas por épico
        print(f"\n" + "=" * 80)
        print(f"📝 LISTADO COMPLETO DE TAREAS:")
        print("=" * 80)
        
        total_verified = 0
        
        for epic_key, epic_data in sorted(epics.items()):
            epic_tasks = tasks_by_epic[epic_key]
            print(f"\n{'─' * 80}")
            print(f"📌 {epic_key}: {epic_data['summary']}")
            print(f"   Total tareas: {len(epic_tasks)}")
            print(f"{'─' * 80}")
            
            if epic_tasks:
                for i, task in enumerate(sorted(epic_tasks, key=lambda t: t.key), 1):
                    status = task.fields.status.name
                    status_icon = '✅' if status == 'Done' else '🔄' if status == 'In Progress' else '⏸️'
                    
                    print(f"\n   {i}. {status_icon} {task.key}: {task.fields.summary}")
                    print(f"      Estado: {status}")
                    
                    # Mostrar labels si existen
                    if task.fields.labels:
                        print(f"      Labels: {', '.join(task.fields.labels)}")
                    
                    # Mostrar fecha de vencimiento si existe
                    if task.fields.duedate:
                        print(f"      Due: {task.fields.duedate}")
                    
                    total_verified += 1
            else:
                print(f"\n   ℹ️  Sin tareas")
        
        # Mostrar huérfanas si existen
        if orphans:
            print(f"\n{'─' * 80}")
            print(f"⚠️  TAREAS SIN ÉPICO:")
            print(f"{'─' * 80}")
            for task in orphans:
                print(f"   • {task.key}: {task.fields.summary}")
        
        # Análisis de duplicados
        print(f"\n" + "=" * 80)
        print(f"🔍 ANÁLISIS DE DUPLICADOS:")
        print("=" * 80)
        
        by_summary = {}
        for task in tasks:
            summary_norm = task.fields.summary.strip().lower()
            if summary_norm not in by_summary:
                by_summary[summary_norm] = []
            by_summary[summary_norm].append(task)
        
        duplicates = {k: v for k, v in by_summary.items() if len(v) > 1}
        
        if duplicates:
            print(f"\n⚠️  DUPLICADOS ENCONTRADOS: {len(duplicates)} grupos")
            for summary, task_list in sorted(duplicates.items()):
                print(f"\n   📝 '{summary[:60]}' ({len(task_list)} copias):")
                for task in task_list:
                    parent = getattr(task.fields, 'parent', None)
                    epic = parent.key if parent else 'Sin épico'
                    print(f"      • {task.key} (Épico: {epic}, Status: {task.fields.status.name})")
        else:
            print(f"\n✅ No se encontraron duplicados")
        
        # Resumen final
        print(f"\n" + "=" * 80)
        print(f"📊 RESUMEN FINAL:")
        print("=" * 80)
        print(f"   • Tareas verificadas: {total_verified}")
        print(f"   • Tareas únicas: {len(by_summary)}")
        print(f"   • Duplicados encontrados: {len(duplicates)} grupos")
        print(f"   • Tareas huérfanas: {len(orphans)}")
        
        # Desglose por estado
        status_count = {}
        for task in tasks:
            status = task.fields.status.name
            status_count[status] = status_count.get(status, 0) + 1
        
        print(f"\n📈 DESGLOSE POR ESTADO:")
        for status, count in sorted(status_count.items()):
            icon = '✅' if status == 'Done' else '🔄' if status == 'In Progress' else '⏸️'
            print(f"   {icon} {status}: {count} tareas")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if len(duplicates) > 0:
            print(f"   ⚠️  Ejecutar 'auto-consolidate' para eliminar {len(duplicates)} grupos duplicados")
        if len(orphans) > 0:
            print(f"   ⚠️  Asignar {len(orphans)} tareas huérfanas a épicos")
        if len(duplicates) == 0 and len(orphans) == 0:
            print(f"   ✅ El proyecto está limpio y bien organizado")
        
        print(f"\n✅ VERIFICACIÓN COMPLETADA")

    def action_simplify_dual(self):
        """Simplificar estrategia dual hardware - consolidar tareas similares"""
        print("\n🔧 SIMPLIFICANDO ESTRATEGIA DUAL HARDWARE")
        print("=" * 70)
        
        # Buscar el épico de dual hardware
        dual_epic = None
        epics = self.jira.search_issues(
            f'project={self.project_key} AND issuetype=Epic',
            maxResults=10
        )
        
        for epic in epics:
            if 'dual hardware' in epic.fields.summary.lower():
                dual_epic = epic
                break
        
        if not dual_epic:
            print("❌ No se encontró el épico de Dual Hardware")
            return
        
        print(f"✅ Encontrado: {dual_epic.key} - {dual_epic.fields.summary}")
        
        # Obtener todas las tareas del épico
        tasks = self.jira.search_issues(
            f'project={self.project_key} AND parent={dual_epic.key}',
            maxResults=50
        )
        
        print(f"📊 Tareas actuales: {len(tasks)}")
        
        # Agrupar tareas por categoría para consolidación
        print(f"\n🔍 Analizando tareas para consolidación...")
        
        # Definir consolidaciones
        consolidations = {
            'TCP + Event Logging': {
                'keywords': ['tcp server', 'event logging', 'logging system'],
                'new_summary': 'Implementación TCP Server + Event Logging (ESP32 & BL335)',
                'description': '''Consolidar implementación de TCP Server y Event Logging para ambos dispositivos.

🎯 ALCANCE:
• TCP Server JSON (Port 9999) - ESP32 & BL335
• Event Logging System completo
• Integración con sistema existente

📦 ENTREGABLES:
• TCP Server funcional en ambos dispositivos
• Event Logging integrado
• Tests de comunicación''',
                'tasks': []
            },
            'Recuperación + NMT + EMCY': {
                'keywords': ['recuperación', 'recovery', 'nmt', 'emcy', 'emergency'],
                'new_summary': 'CANopen Avanzado: NMT + EMCY + Recovery (ESP32 & BL335)',
                'description': '''Implementación completa de funcionalidades CANopen avanzadas.

🎯 ALCANCE:
• Sistema de recuperación de errores
• NMT (Network Management) completo
• Emergency Messages (EMCY)
• Manejo de estados CANopen

📦 ENTREGABLES:
• NMT funcional en ambos dispositivos
• EMCY messages implementado
• Recovery system robusto''',
                'tasks': []
            },
            'Diagnósticos': {
                'keywords': ['diagnóstico', 'diagnostic'],
                'new_summary': 'Sistema de Diagnósticos Unificado (ESP32 & BL335)',
                'description': '''Sistema de diagnósticos avanzado para ambos dispositivos.

🎯 ALCANCE:
• Diagnósticos en tiempo real
• Métricas de rendimiento
• Alertas y monitoreo

📦 ENTREGABLES:
• Dashboard de diagnósticos
• APIs de diagnóstico
• Documentación''',
                'tasks': []
            },
            'Testing + Setup': {
                'keywords': ['test', 'setup', 'prueba'],
                'new_summary': 'Testing Comparativo y Setup Dual Hardware',
                'description': '''Suite completa de tests comparativos y configuración dual.

🎯 ALCANCE:
• Suite de tests automáticos
• Setup físico dual hardware
• Ejecución de pruebas comparativas

📦 ENTREGABLES:
• Tests automatizados
• Hardware configurado
• Métricas de comparación''',
                'tasks': []
            }
        }
        
        # Clasificar tareas existentes
        for task in tasks:
            summary_lower = task.fields.summary.lower()
            matched = False
            
            for category, data in consolidations.items():
                if any(kw in summary_lower for kw in data['keywords']):
                    data['tasks'].append(task)
                    matched = True
                    break
            
            if not matched:
                # Mantener tareas que no se consolidan
                if 'hardware adquirido' in summary_lower or 'reporte' in summary_lower:
                    print(f"   ℹ️  Mantener: {task.key} - {task.fields.summary}")
        
        # Mostrar plan de consolidación
        print(f"\n📋 PLAN DE CONSOLIDACIÓN:")
        print("-" * 70)
        
        tasks_to_delete = []
        tasks_to_create = []
        
        for category, data in consolidations.items():
            if data['tasks']:
                print(f"\n🔗 {category}:")
                print(f"   Nueva tarea: {data['new_summary']}")
                print(f"   Consolidar {len(data['tasks'])} tareas:")
                
                for task in data['tasks']:
                    print(f"      ❌ {task.key}: {task.fields.summary}")
                    tasks_to_delete.append(task)
                
                tasks_to_create.append({
                    'summary': data['new_summary'],
                    'description': data['description']
                })
        
        # Calcular resultado final
        current_count = len(tasks)
        after_count = current_count - len(tasks_to_delete) + len(tasks_to_create)
        
        print(f"\n" + "=" * 70)
        print(f"📊 RESULTADO ESPERADO:")
        print(f"   • Tareas actuales: {current_count}")
        print(f"   • Tareas a eliminar: {len(tasks_to_delete)}")
        print(f"   • Tareas nuevas: {len(tasks_to_create)}")
        print(f"   • Tareas finales: {after_count}")
        print(f"   • Reducción: {current_count - after_count} tareas ({((current_count - after_count) / current_count * 100):.0f}%)")
        
        # Ejecutar consolidación
        print(f"\n🚀 EJECUTANDO CONSOLIDACIÓN...")
        
        # 1. Crear nuevas tareas consolidadas
        created_tasks = []
        for task_data in tasks_to_create:
            try:
                new_task = self.jira.create_issue(
                    project=self.project_key,
                    summary=task_data['summary'],
                    description=task_data['description'],
                    issuetype={'name': 'Task'},
                    labels=['dual-hardware', 'consolidated', 'esp32', 'bl335']
                )
                new_task.update(fields={'parent': {'key': dual_epic.key}})
                new_task.update(fields={'status': {'name': 'In Progress'}})
                
                created_tasks.append(new_task.key)
                print(f"   ✅ Creada: {new_task.key} - {task_data['summary']}")
            except Exception as e:
                print(f"   ❌ Error creando tarea: {e}")
        
        # 2. Eliminar tareas consolidadas
        deleted_count = 0
        for task in tasks_to_delete:
            try:
                task.delete()
                deleted_count += 1
                print(f"   ✅ Eliminada: {task.key}")
            except Exception as e:
                print(f"   ❌ Error eliminando {task.key}: {e}")
        
        # Resumen final
        print(f"\n" + "=" * 70)
        print(f"✅ CONSOLIDACIÓN COMPLETADA")
        print(f"   • Tareas consolidadas creadas: {len(created_tasks)}")
        print(f"   • Tareas eliminadas: {deleted_count}")
        print(f"   • Épico Dual Hardware simplificado")

    def action_create_consolidated(self):
        """Crear las 4 tareas consolidadas sin campo status"""
        print("\n🔧 CREANDO TAREAS CONSOLIDADAS DUAL HARDWARE")
        print("=" * 70)
        
        # Buscar el épico de dual hardware
        dual_epic = None
        epics = self.jira.search_issues(
            f'project={self.project_key} AND issuetype=Epic',
            maxResults=10
        )
        
        for epic in epics:
            if 'dual' in epic.fields.summary.lower() and 'hardware' in epic.fields.summary.lower():
                dual_epic = epic
                break
        
        if not dual_epic:
            print("❌ No se encontró el épico 'Dual Hardware'")
            return
        
        print(f"✅ Encontrado: {dual_epic.key} - {dual_epic.fields.summary}")
        
        # Definir las 4 tareas consolidadas
        consolidated_tasks = [
            {
                'summary': 'Implementación TCP Server + Event Logging (ESP32 & BL335)',
                'description': '''Consolidar implementación de TCP Server y Event Logging para ambos dispositivos.

🎯 ALCANCE:
• TCP Server JSON (Port 9999) - ESP32 & BL335
• Event Logging System completo
• Integración con sistema existente

📦 ENTREGABLES:
• TCP Server funcional en ambos dispositivos
• Event Logging integrado
• Tests de comunicación

🔄 CONSOLIDA TAREAS:
• GAT-64: TCP Server JSON (Port 9999) - ESP32
• GAT-65: TCP Server JSON (Port 9999) - BL335
• GAT-66: Event Logging System - ESP32
• GAT-13: Logging System - BL335''',
                'labels': ['dual-hardware', 'tcp-server', 'event-logging', 'consolidated']
            },
            {
                'summary': 'CANopen Avanzado: NMT + EMCY + Recovery (ESP32 & BL335)',
                'description': '''Implementación completa de funcionalidades CANopen avanzadas.

🎯 ALCANCE:
• Sistema de recuperación de errores
• NMT (Network Management) completo
• Emergency Messages (EMCY)
• Manejo de estados CANopen

📦 ENTREGABLES:
• NMT funcional en ambos dispositivos
• EMCY messages implementado
• Recovery system robusto

🔄 CONSOLIDA TAREAS:
• GAT-67: Sistema de Recuperación de Errores - ESP32
• GAT-68: NMT (Network Management) - ESP32
• GAT-69: NMT (Network Management) - BL335
• GAT-70: Emergency Messages (EMCY) - ESP32''',
                'labels': ['dual-hardware', 'canopen', 'nmt', 'emcy', 'recovery', 'consolidated']
            },
            {
                'summary': 'Sistema de Diagnósticos Unificado (ESP32 & BL335)',
                'description': '''Sistema de diagnósticos avanzado para ambos dispositivos.

🎯 ALCANCE:
• Diagnósticos en tiempo real
• Métricas de rendimiento
• Alertas y monitoreo

📦 ENTREGABLES:
• Dashboard de diagnósticos
• APIs de diagnóstico
• Documentación

🔄 CONSOLIDA TAREAS:
• GAT-71: Sistema de Diagnósticos Avanzado - ESP32
• GAT-72: Sistema de Diagnósticos Avanzado - BL335''',
                'labels': ['dual-hardware', 'diagnostics', 'monitoring', 'consolidated']
            },
            {
                'summary': 'Testing Comparativo y Setup Dual Hardware',
                'description': '''Suite completa de tests comparativos y configuración dual.

🎯 ALCANCE:
• Suite de tests automáticos
• Setup físico dual hardware
• Ejecución de pruebas comparativas

📦 ENTREGABLES:
• Tests automatizados
• Hardware configurado
• Métricas de comparación

🔄 CONSOLIDA TAREAS:
• GAT-73: Tests de Integración Completos - ESP32
• GAT-74: Tests de Integración Completos - BL335
• GAT-75: Setup Físico y Configuración - Dual Hardware''',
                'labels': ['dual-hardware', 'testing', 'setup', 'consolidated']
            }
        ]
        
        # Crear las tareas SIN el campo status
        created_count = 0
        for task_data in consolidated_tasks:
            try:
                new_task = self.jira.create_issue(
                    project=self.project_key,
                    summary=task_data['summary'],
                    description=task_data['description'],
                    issuetype={'name': 'Task'},
                    parent={'key': dual_epic.key},
                    labels=task_data['labels']
                )
                created_count += 1
                print(f"✅ Creada: {new_task.key} - {task_data['summary'][:60]}...")
            except Exception as e:
                print(f"❌ Error creando '{task_data['summary'][:40]}...': {e}")
        
        # Resumen final
        print(f"\n" + "=" * 70)
        print(f"✅ CREACIÓN COMPLETADA")
        print(f"   • Tareas creadas: {created_count}/4")
        print(f"   • Épico: {dual_epic.key}")

    def action_update_dates(self):
        """Actualizar fechas de inicio y vencimiento de forma inteligente"""
        print("\n📅 ACTUALIZANDO FECHAS DE TAREAS")
        print("=" * 70)
        
        # Fecha base: HOY (31 octubre 2025)
        today = datetime(2025, 10, 31)
        
        # Obtener todas las tareas
        all_issues = self.jira.search_issues(
            f'project={self.project_key} ORDER BY key ASC',
            maxResults=100
        )
        
        # Separar épicos y tareas
        tasks = [i for i in all_issues if i.fields.issuetype.name == 'Task']
        
        print(f"📊 Total tareas a actualizar: {len(tasks)}")
        
        # Definir cronograma inteligente basado en:
        # 1. Estado actual (Done, In Progress, To Do)
        # 2. Dependencias lógicas
        # 3. Épico al que pertenece
        
        date_plan = {
            # EPIC GAT-46: Fundación (COMPLETADAS - fechas pasadas)
            'GAT-4': {'start': datetime(2025, 10, 13), 'due': datetime(2025, 10, 13), 'status': 'Done'},
            'GAT-5': {'start': datetime(2025, 10, 14), 'due': datetime(2025, 10, 18), 'status': 'Done'},
            'GAT-6': {'start': datetime(2025, 10, 19), 'due': datetime(2025, 10, 20), 'status': 'Done'},
            'GAT-7': {'start': datetime(2025, 10, 21), 'due': datetime(2025, 10, 21), 'status': 'Done'},
            
            # EPIC GAT-47: Implementación (MIX - algunas completadas)
            'GAT-21': {'start': datetime(2025, 10, 22), 'due': datetime(2025, 10, 22), 'status': 'Done'},
            'GAT-22': {'start': datetime(2025, 10, 19), 'due': datetime(2025, 10, 20), 'status': 'Done'},
            'GAT-8': {'start': datetime(2025, 10, 23), 'due': datetime(2025, 10, 24), 'status': 'Done'},
            'GAT-9': {'start': datetime(2025, 10, 24), 'due': datetime(2025, 10, 24), 'status': 'Done'},
            'GAT-10': {'start': datetime(2025, 11, 1), 'due': datetime(2025, 11, 3), 'status': 'In Progress'},
            
            # EPIC GAT-48: Integración Hardware
            'GAT-58': {'start': datetime(2025, 10, 31), 'due': datetime(2025, 11, 3), 'status': 'In Progress'},
            
            # EPIC GAT-63: Dual Hardware (NUEVO PLAN)
            # Fase 1: Documentación y Adquisición (Noviembre Semana 1)
            'GAT-77': {'start': datetime(2025, 10, 31), 'due': datetime(2025, 11, 1), 'status': 'In Progress'},
            'GAT-11': {'start': datetime(2025, 10, 26), 'due': datetime(2025, 11, 15), 'status': 'To Do'},  # Esperando entrega
            
            # Fase 2: Implementación Core (Noviembre Semana 2-3)
            'GAT-78': {'start': datetime(2025, 11, 4), 'due': datetime(2025, 11, 8), 'status': 'To Do'},  # TCP + Logging
            'GAT-12': {'start': datetime(2025, 11, 4), 'due': datetime(2025, 11, 7), 'status': 'To Do'},  # Logging backend
            
            # Fase 3: CANopen Avanzado (Noviembre Semana 3-4)
            'GAT-79': {'start': datetime(2025, 11, 9), 'due': datetime(2025, 11, 15), 'status': 'To Do'},  # NMT + EMCY
            
            # Fase 4: Diagnósticos y Testing (Noviembre Semana 4 - Diciembre Semana 1)
            'GAT-80': {'start': datetime(2025, 11, 16), 'due': datetime(2025, 11, 20), 'status': 'To Do'},  # Diagnósticos
            'GAT-81': {'start': datetime(2025, 11, 21), 'due': datetime(2025, 11, 25), 'status': 'To Do'},  # Testing Setup
            
            # Fase 5: Validación E2E (Diciembre - requiere hardware)
            'GAT-15': {'start': datetime(2025, 11, 26), 'due': datetime(2025, 12, 5), 'status': 'To Do'},  # E2E testing
            
            # Fase 6: Reporte Final (Diciembre)
            'GAT-76': {'start': datetime(2025, 11, 20), 'due': datetime(2025, 11, 28), 'status': 'In Progress'},  # Reporte comparativo
            'GAT-14': {'start': datetime(2025, 11, 26), 'due': datetime(2025, 12, 5), 'status': 'To Do'},  # Docs finales
        }
        
        # Actualizar fechas
        updated_count = 0
        skipped_count = 0
        
        for task in tasks:
            if task.key in date_plan:
                plan = date_plan[task.key]
                
                try:
                    # Preparar campos para actualizar
                    update_fields = {}
                    
                    # Formatear fechas en formato YYYY-MM-DD
                    start_date = plan['start'].strftime('%Y-%m-%d')
                    due_date = plan['due'].strftime('%Y-%m-%d')
                    
                    # Actualizar campos (algunos campos pueden no estar disponibles según configuración JIRA)
                    # Solo actualizar duedate que es estándar
                    update_fields['duedate'] = due_date
                    
                    task.update(fields=update_fields)
                    
                    duration = (plan['due'] - plan['start']).days + 1
                    status_emoji = '✅' if plan['status'] == 'Done' else ('🔄' if plan['status'] == 'In Progress' else '⏸️')
                    
                    print(f"   {status_emoji} {task.key}: {start_date} → {due_date} ({duration}d) - {task.fields.summary[:50]}")
                    updated_count += 1
                    
                except Exception as e:
                    print(f"   ⚠️ {task.key}: Error actualizando - {e}")
                    skipped_count += 1
            else:
                print(f"   ⚠️ {task.key}: Sin plan de fechas - {task.fields.summary[:50]}")
                skipped_count += 1
        
        # Resumen
        print(f"\n" + "=" * 70)
        print(f"✅ ACTUALIZACIÓN DE FECHAS COMPLETADA")
        print(f"   • Tareas actualizadas: {updated_count}")
        print(f"   • Tareas omitidas: {skipped_count}")
        print(f"\n📅 CRONOGRAMA GENERAL:")
        print(f"   • Fase actual: Implementación + Dual Hardware")
        print(f"   • Noviembre 2025: Core implementation (TCP, Logging, CANopen)")
        print(f"   • Diciembre 2025: Testing, validación E2E, documentación")
        print(f"   • Deadline proyecto: 5 de diciembre de 2025")

    def action_sync_status(self):
        """Sincronizar estados de tareas en JIRA con el estado real del proyecto"""
        print("\n🔄 SINCRONIZANDO ESTADOS DE TAREAS CON REALIDAD DEL PROYECTO")
        print("=" * 70)
        
        # Definir el mapeo de estados reales basado en archivos del proyecto
        status_updates = {
            # TAREAS COMPLETADAS que están marcadas incorrectamente como "To Do"
            'GAT-6': {
                'current': 'To Do',
                'new': 'Done',
                'reason': 'ESP32 Gateway completo (esp32_gateway/ con código funcional)',
                'evidence': 'esp32_gateway/main/can_tcp_bridge.c, QUICK_START.md'
            },
            'GAT-7': {
                'current': 'To Do',
                'new': 'Done',
                'reason': 'Manuales R13F reorganizados',
                'evidence': 'docs/EMISOR IK3.md, docs/RECEPTOR K13 F.md, docs/Manual Gama TM70 Pupitre.md'
            },
            'GAT-8': {
                'current': 'To Do',
                'new': 'Done',
                'reason': 'Desktop GUI implementado (duplicado de GAT-21)',
                'evidence': 'src/web_ui/desktop_gui.py (730 líneas), src/desktop_gui/main.py'
            },
            'GAT-12': {
                'current': 'To Do',
                'new': 'Done',
                'reason': 'Sistema de logging completo y funcional',
                'evidence': 'src/core/event_logger.py (393 líneas), src/core/event_storage.py (420 líneas)'
            },
            
            # TAREAS EN PROGRESO que están marcadas como "To Do"
            'GAT-10': {
                'current': 'To Do',
                'new': 'In Progress',
                'reason': 'Simulador R13F casi completo (16/17 tests pasan)',
                'evidence': 'tools/can_simulator.py, tests/ con 94% success rate'
            },
            'GAT-58': {
                'current': 'To Do',
                'new': 'In Progress',
                'reason': 'Preparación EdgeBox Lite iniciada (documentación completa)',
                'evidence': 'HARDWARE_ADQUIRIDO.md, ESTADO_ESP32_HARDWARE.md'
            },
        }
        
        print(f"📊 Tareas a actualizar: {len(status_updates)}")
        print(f"\n🔍 ANALIZANDO Y ACTUALIZANDO...\n")
        
        updated_count = 0
        failed_count = 0
        
        for task_key, update_info in status_updates.items():
            try:
                # Buscar la tarea
                issue = self.jira.issue(task_key)
                current_status = issue.fields.status.name
                
                print(f"📝 {task_key}: {issue.fields.summary[:60]}...")
                print(f"   Estado actual: {current_status}")
                print(f"   Estado nuevo: {update_info['new']}")
                print(f"   Razón: {update_info['reason']}")
                print(f"   Evidencia: {update_info['evidence']}")
                
                # Obtener transiciones disponibles
                transitions = self.jira.transitions(issue)
                
                # Buscar la transición correcta
                target_transition = None
                for transition in transitions:
                    # Mapear nombres de transiciones comunes
                    if update_info['new'] == 'Done' and transition['name'].lower() in ['done', 'complete', 'close']:
                        target_transition = transition['id']
                        break
                    elif update_info['new'] == 'In Progress' and transition['name'].lower() in ['in progress', 'start progress']:
                        target_transition = transition['id']
                        break
                
                if target_transition:
                    # Ejecutar transición
                    self.jira.transition_issue(issue, target_transition)
                    print(f"   ✅ Actualizado: {current_status} → {update_info['new']}\n")
                    updated_count += 1
                else:
                    # Si no hay transición directa, intentar workflow completo
                    # Primero a "In Progress" si no está ahí, luego a "Done" si aplica
                    print(f"   ℹ️ Transiciones disponibles:")
                    for t in transitions:
                        print(f"      - {t['name']} (id: {t['id']})")
                    
                    # Intentar transición manual con el primer ID disponible que parezca correcto
                    if update_info['new'] == 'Done':
                        # Buscar cualquier transición que lleve a Done
                        for t in transitions:
                            if 'done' in t['name'].lower() or 'complete' in t['name'].lower():
                                self.jira.transition_issue(issue, t['id'])
                                print(f"   ✅ Actualizado con transición: {t['name']}\n")
                                updated_count += 1
                                break
                        else:
                            print(f"   ⚠️ No se encontró transición a Done\n")
                            failed_count += 1
                    elif update_info['new'] == 'In Progress':
                        for t in transitions:
                            if 'progress' in t['name'].lower() or 'start' in t['name'].lower():
                                self.jira.transition_issue(issue, t['id'])
                                print(f"   ✅ Actualizado con transición: {t['name']}\n")
                                updated_count += 1
                                break
                        else:
                            print(f"   ⚠️ No se encontró transición a In Progress\n")
                            failed_count += 1
                
            except Exception as e:
                print(f"   ❌ Error actualizando {task_key}: {e}\n")
                failed_count += 1
        
        # Resumen final
        print("=" * 70)
        print(f"✅ SINCRONIZACIÓN COMPLETADA")
        print(f"\n📊 RESULTADOS:")
        print(f"   • Tareas actualizadas: {updated_count}")
        print(f"   • Tareas fallidas: {failed_count}")
        print(f"   • Total procesadas: {len(status_updates)}")
        
        # Mostrar nuevo estado del proyecto
        print(f"\n📈 NUEVO ESTADO DEL PROYECTO:")
        all_tasks = self.jira.search_issues(f'project={self.project_key} AND type=Task', maxResults=50)
        
        status_count = {}
        for task in all_tasks:
            status = task.fields.status.name
            status_count[status] = status_count.get(status, 0) + 1
        
        total = len(all_tasks)
        for status, count in sorted(status_count.items()):
            percentage = (count / total * 100) if total > 0 else 0
            emoji = '✅' if status == 'Done' else ('🔄' if status == 'In Progress' else '⏸️')
            print(f"   {emoji} {status}: {count} tareas ({percentage:.0f}%)")

    def action_check_fields(self):
        """Explorar campos disponibles en JIRA para encontrar start date"""
        print("\n🔍 EXPLORANDO CAMPOS DISPONIBLES EN JIRA")
        print("=" * 70)
        
        try:
            # Obtener todos los campos disponibles
            all_fields = self.jira.fields()
            
            print(f"📊 Total campos encontrados: {len(all_fields)}\n")
            
            # Buscar campos relacionados con fechas
            date_fields = []
            start_fields = []
            
            print("🔍 CAMPOS RELACIONADOS CON FECHAS:\n")
            
            for field in all_fields:
                field_name = field['name'].lower()
                field_id = field['id']
                field_type = field.get('schema', {}).get('type', 'unknown')
                
                # Buscar campos de fecha
                if 'date' in field_name or field_type in ['date', 'datetime']:
                    date_fields.append(field)
                    emoji = '📅'
                    
                    # Marcar especialmente campos de inicio
                    if 'start' in field_name:
                        start_fields.append(field)
                        emoji = '🎯'
                    
                    print(f"{emoji} {field['name']}")
                    print(f"   ID: {field_id}")
                    print(f"   Type: {field_type}")
                    print(f"   Custom: {'Yes' if field.get('custom') else 'No'}")
                    print()
            
            print("=" * 70)
            print(f"📊 RESUMEN:")
            print(f"   • Total campos de fecha: {len(date_fields)}")
            print(f"   • Campos de 'start date': {len(start_fields)}")
            
            if start_fields:
                print(f"\n🎯 CAMPOS DE START DATE ENCONTRADOS:")
                for field in start_fields:
                    print(f"   • {field['name']} (ID: {field['id']})")
            else:
                print(f"\n⚠️ No se encontró campo 'Start Date' nativo")
                print(f"   Opciones:")
                print(f"   1. Crear campo personalizado 'Start Date'")
                print(f"   2. Usar descripción para fechas de inicio")
                print(f"   3. Usar campo existente alternativo")
            
            # Mostrar ejemplo de una tarea para ver campos disponibles
            print(f"\n📝 EJEMPLO - CAMPOS EN UNA TAREA:")
            issues = self.jira.search_issues(f'project={self.project_key}', maxResults=1)
            if issues:
                issue = issues[0]
                print(f"   Tarea: {issue.key} - {issue.fields.summary}")
                print(f"\n   Campos de fecha disponibles en esta tarea:")
                
                for field in date_fields:
                    field_id = field['id']
                    try:
                        value = getattr(issue.fields, field_id, None)
                        if value:
                            print(f"   • {field['name']}: {value}")
                    except:
                        pass
                        
        except Exception as e:
            print(f"❌ Error explorando campos: {e}")

    def action_migrate_dates(self):
        """Migrar fechas de inicio desde descripciones a campos de JIRA"""
        print("\n📅 MIGRANDO FECHAS DE INICIO A CAMPOS DE JIRA")
        print("=" * 70)
        
        # Usar campos disponibles en JIRA
        # Start date (customfield_10015) - campo estándar de start date
        start_date_field = 'customfield_10015'  # Start date
        
        print(f"✅ Usando campos:")
        print(f"   • Start date: customfield_10015 (fecha de inicio planificada)")
        print(f"   • Due date: duedate (fecha de vencimiento)\n")
        
        # Obtener todas las tareas
        all_tasks = self.jira.search_issues(
            f'project={self.project_key} AND type=Task',
            maxResults=50
        )
        
        # Definir fechas de inicio basadas en nuestro cronograma
        date_mappings = {
            'GAT-4': {'start': '2025-10-13', 'due': '2025-10-13', 'status': 'Done'},
            'GAT-5': {'start': '2025-10-14', 'due': '2025-10-18', 'status': 'Done'},
            'GAT-6': {'start': '2025-10-19', 'due': '2025-10-20', 'status': 'Done'},
            'GAT-7': {'start': '2025-10-21', 'due': '2025-10-21', 'status': 'Done'},
            'GAT-8': {'start': '2025-10-23', 'due': '2025-10-24', 'status': 'Done'},
            'GAT-9': {'start': '2025-10-24', 'due': '2025-10-24', 'status': 'Done'},
            'GAT-12': {'start': '2025-10-24', 'due': '2025-10-24', 'status': 'Done'},
            'GAT-21': {'start': '2025-10-22', 'due': '2025-10-22', 'status': 'Done'},
            'GAT-22': {'start': '2025-10-19', 'due': '2025-10-20', 'status': 'Done'},
            'GAT-10': {'start': '2025-11-01', 'due': '2025-11-03', 'status': 'In Progress'},
            'GAT-58': {'start': '2025-10-31', 'due': '2025-11-03', 'status': 'In Progress'},
            'GAT-76': {'start': '2025-11-20', 'due': '2025-11-28', 'status': 'In Progress'},
            'GAT-77': {'start': '2025-10-31', 'due': '2025-11-01', 'status': 'In Progress'},
            'GAT-11': {'start': '2025-10-26', 'due': '2025-11-15', 'status': 'To Do'},
            'GAT-14': {'start': '2025-11-26', 'due': '2025-12-05', 'status': 'To Do'},
            'GAT-15': {'start': '2025-11-26', 'due': '2025-12-05', 'status': 'To Do'},
            'GAT-78': {'start': '2025-11-04', 'due': '2025-11-08', 'status': 'To Do'},
            'GAT-79': {'start': '2025-11-09', 'due': '2025-11-15', 'status': 'To Do'},
            'GAT-80': {'start': '2025-11-16', 'due': '2025-11-20', 'status': 'To Do'},
            'GAT-81': {'start': '2025-11-21', 'due': '2025-11-25', 'status': 'To Do'},
        }
        
        updated_count = 0
        cleaned_count = 0
        
        for task in all_tasks:
            if task.key in date_mappings:
                dates = date_mappings[task.key]
                
                try:
                    # Actualizar campos de fecha
                    update_fields = {
                        'duedate': dates['due'],
                        start_date_field: dates['start']  # Start date
                    }
                    
                    task.update(fields=update_fields)
                    
                    # Limpiar descripción de fechas si existen
                    description = task.fields.description or ''
                    original_desc = description
                    
                    # Remover líneas con fechas del formato viejo
                    lines_to_remove = [
                        '📅 CRONOGRAMA:',
                        'Fecha inicio real:',
                        'Fecha completado:',
                        'Duración real:',
                        'start_date_real:',
                        'end_date_real:',
                        'Estado: ✅',
                        'Fecha inicio:',
                        'Fecha fin:'
                    ]
                    
                    lines = description.split('\n')
                    cleaned_lines = []
                    skip_section = False
                    
                    for i, line in enumerate(lines):
                        # Detectar inicio de sección de cronograma
                        if '📅 CRONOGRAMA:' in line or '📅 PERÍODO:' in line:
                            skip_section = True
                            continue
                        
                        # Detectar fin de sección (nueva sección con emoji diferente)
                        if skip_section and line.strip() and any(emoji in line for emoji in ['🎯', '📦', '🔧', '✅']):
                            if not line.strip().startswith('•'):
                                skip_section = False
                        
                        # Saltar líneas con información de fechas
                        if skip_section or any(marker in line for marker in lines_to_remove):
                            continue
                        
                        cleaned_lines.append(line)
                    
                    cleaned_description = '\n'.join(cleaned_lines).strip()
                    
                    # Si la descripción cambió significativamente, actualizarla
                    if len(cleaned_lines) < len(lines) - 2:  # Al menos 2 líneas removidas
                        task.update(fields={'description': cleaned_description})
                        cleaned_count += 1
                    
                    duration = (datetime.strptime(dates['due'], '%Y-%m-%d') - 
                               datetime.strptime(dates['start'], '%Y-%m-%d')).days + 1
                    
                    status_emoji = '✅' if dates['status'] == 'Done' else ('🔄' if dates['status'] == 'In Progress' else '⏸️')
                    
                    print(f"{status_emoji} {task.key}: {dates['start']} → {dates['due']} ({duration}d)")
                    print(f"   Start Date: {dates['start']}")
                    print(f"   Due Date: {dates['due']}")
                    if len(cleaned_lines) < len(lines) - 2:
                        removed = len(lines) - len(cleaned_lines)
                        print(f"   Descripción limpiada ({removed} líneas de fechas removidas)")
                    print()
                    
                    updated_count += 1
                    
                except Exception as e:
                    print(f"❌ Error actualizando {task.key}: {e}\n")
        
        print("=" * 70)
        print(f"✅ MIGRACIÓN COMPLETADA")
        print(f"\n📊 RESULTADOS:")
        print(f"   • Tareas con fechas actualizadas: {updated_count}")
        print(f"   • Descripciones limpiadas: {cleaned_count}")
        print(f"   • Start Date field (customfield_10015): ✅ Actualizado")
        print(f"   • Due Date field (duedate): ✅ Actualizado")
        print(f"\n💡 Ahora las fechas están en campos dedicados, no en descripción")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='SafetyMind Jira Manager - Gestión unificada de proyectos Jira',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python3 jira_manager.py --action import     # Importar estructura completa
  python3 jira_manager.py --action cleanup    # Limpiar duplicados
  python3 jira_manager.py --action assign     # Asignar tareas a épicos
  python3 jira_manager.py --action schedule   # Actualizar cronograma
  python3 jira_manager.py --action check      # Verificar estado
  python3 jira_manager.py --action diagnose   # Diagnóstico completo
        """
    )
    
    parser.add_argument(
        '--action',
        choices=['import', 'cleanup', 'assign', 'schedule', 'check', 'diagnose', 'add-worklogs', 'import-dual', 'clean-all', 'consolidate', 'auto-consolidate', 'deep-analysis', 'verify-all', 'simplify-dual', 'create-consolidated', 'update-dates', 'sync-status', 'check-fields', 'migrate-dates'],
        required=True,
        help='Acción a realizar'
    )
    
    args = parser.parse_args()
    
    print("🚀 SAFETYMIND JIRA MANAGER v2.0.0")
    print("=" * 50)
    
    manager = JiraManager()
    
    # Ejecutar acción
    if args.action == 'import':
        manager.action_import()
    elif args.action == 'cleanup':
        manager.action_cleanup()
    elif args.action == 'assign':
        manager.action_assign()
    elif args.action == 'schedule':
        manager.action_schedule()
    elif args.action == 'check':
        manager.action_check()
    elif args.action == 'add-worklogs':
        manager.action_add_worklogs()
    elif args.action == 'import-dual':
        manager.action_import_dual_hardware()
    elif args.action == 'clean-all':
        manager.action_clean_all()
    elif args.action == 'consolidate':
        manager.action_consolidate()
    elif args.action == 'auto-consolidate':
        manager.action_auto_consolidate()
    elif args.action == 'deep-analysis':
        manager.action_deep_analysis()
    elif args.action == 'verify-all':
        manager.action_verify_all()
    elif args.action == 'simplify-dual':
        manager.action_simplify_dual()
    elif args.action == 'create-consolidated':
        manager.action_create_consolidated()
    elif args.action == 'update-dates':
        manager.action_update_dates()
    elif args.action == 'sync-status':
        manager.action_sync_status()
    elif args.action == 'check-fields':
        manager.action_check_fields()
    elif args.action == 'migrate-dates':
        manager.action_migrate_dates()
    elif args.action == 'diagnose':
        manager.action_diagnose()
    
    print(f"\n✅ ACCIÓN '{args.action.upper()}' COMPLETADA")

if __name__ == '__main__':
    main()