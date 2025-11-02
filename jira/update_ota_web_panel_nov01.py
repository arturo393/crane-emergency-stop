#!/usr/bin/env python3
"""
Script para actualizar Jira con progreso de OTA Manager + Web Panel
Fecha: 01 de Noviembre de 2025
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Agregar directorio padre al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from jira import JIRA
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def main():
    """Actualizar Jira con worklog de OTA Manager + Web Panel"""
    
    print("=" * 70)
    print("ACTUALIZACIÓN JIRA - OTA MANAGER + WEB PANEL")
    print("01 de Noviembre de 2025")
    print("=" * 70)
    
    # Conectar a Jira
    try:
        jira = JIRA(
            server=os.getenv('JIRA_URL'),
            basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
        )
        print(f"\n✅ Conectado a Jira: {os.getenv('JIRA_URL')}")
    except Exception as e:
        print(f"\n❌ Error conectando a Jira: {e}")
        return 1
    
    # Buscar tarea ESP32 Gateway
    print("\n🔍 Buscando tarea ESP32 Gateway...")
    try:
        issues = jira.search_issues(
            'project=GAT AND summary ~ "ESP32 Gateway"',
            maxResults=5
        )
        
        if not issues:
            print("❌ No se encontró tarea ESP32 Gateway")
            return 1
        
        esp32_task = issues[0]
        print(f"✅ Tarea encontrada: {esp32_task.key} - {esp32_task.fields.summary}")
        print(f"   Estado actual: {esp32_task.fields.status.name}")
        
    except Exception as e:
        print(f"❌ Error buscando tarea: {e}")
        return 1
    
    # Preparar comentario detallado
    comment = """✅ **COMPLETADO: OTA Manager + Web Panel**

---

## 🔄 OTA Manager

**Archivos implementados:**
• `main/ota_manager.h` (147 líneas)
• `main/ota_manager.cpp` (~350 líneas)
• `test/device/test_ota_manager.cpp` (330 líneas)

**Funcionalidades:**
✅ Actualización desde URL (HTTP/HTTPS)
✅ Actualización desde buffer en memoria
✅ Validación automática de firmware (30 segundos)
✅ Rollback a versión anterior
✅ Verificación SHA256
✅ Comandos TCP: `OTA_INFO`, `OTA_VALIDATE`, `OTA_ROLLBACK`
✅ Integración con SD Logger

**Tests:** 8 tests completos cubriendo todos los casos de uso

---

## 🌐 Web Panel

**Archivos implementados:**
• `main/web_server.h` (150 líneas)
• `main/web_server.cpp` (~600 líneas con HTML embebido)

**Características:**
✅ Servidor HTTP en puerto 80
✅ Dashboard responsive con 6 tarjetas de información
✅ API REST `/api/status` con JSON completo
✅ Actualización automática cada 2 segundos (polling)
✅ Controles CiA402: Shutdown, Switch On, Enable, Disable, Quick Stop
✅ Monitoreo en tiempo real: CAN, CiA402, Network, System, SD Logger, OTA

---

## 📊 Métricas

**Tamaño de binario:**
```
Base (SD Logger):    482 KB
+ OTA Manager:       482 KB (+0 KB - optimizado)
+ Web Server:        531 KB (+49 KB)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL FINAL:         531 KB
Espacio libre:       517 KB (49%)
```

**Código:**
• Archivos nuevos: 5
• Archivos modificados: 2 (`main.cpp`, `CMakeLists.txt`)
• Líneas totales: ~1,697
• Tests: 8 tests OTA

---

## 📦 Integración

**`main/main.cpp`:**
• Auto-validación OTA después de 30 segundos
• Actualización periódica del panel web (1 segundo)
• Comandos TCP para OTA integrados

**`main/CMakeLists.txt`:**
• Dependencias: `app_update`, `esp_https_ota`, `esp_http_server`

---

## 📝 Documentación

Documentos generados:
• `SESION_01NOV2025_OTA_WEB_PANEL.txt` (reporte técnico completo)
• `JIRA_UPDATE_01NOV2025.md` (resumen para Jira)

---

## ✅ Estado

**Compilación:** ✅ Exitosa (531 KB, 49% espacio libre)
**Tests:** ✅ 8/8 tests OTA implementados
**Integración:** ✅ Funcional con SD Logger y sistema existente
**Listo para:** Testing en hardware ESP32-S3 real

---

**Tiempo invertido:** 7 horas
**Fecha:** 01 de Noviembre de 2025"""
    
    # Agregar worklog
    print("\n⏰ Agregando worklog de 7 horas...")
    try:
        worklog_date = datetime(2025, 11, 1, 9, 0, tzinfo=timezone.utc)
        
        jira.add_worklog(
            issue=esp32_task,
            timeSpent='7h',
            comment=comment,
            started=worklog_date
        )
        
        print("✅ Worklog agregado exitosamente")
        print(f"   • Tiempo registrado: 7h")
        print(f"   • Fecha: 2025-11-01 09:00 UTC")
        print(f"   • Issue: {esp32_task.key}")
        
    except Exception as e:
        print(f"❌ Error agregando worklog: {e}")
        return 1
    
    # Verificar worklogs actuales
    print("\n📊 Verificando worklogs registrados...")
    try:
        worklogs = jira.worklogs(esp32_task)
        total_time = sum(w.timeSpentSeconds for w in worklogs)
        total_hours = total_time / 3600
        
        print(f"✅ Total de worklogs: {len(worklogs)}")
        print(f"   • Tiempo total registrado: {total_hours:.1f} horas")
        print(f"   • Último worklog: {worklogs[-1].comment[:100]}..." if worklogs else "")
        
    except Exception as e:
        print(f"⚠️  No se pudo verificar worklogs: {e}")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("✅ ACTUALIZACIÓN DE JIRA COMPLETADA")
    print("=" * 70)
    print(f"\n📋 Resumen:")
    print(f"   • Issue actualizado: {esp32_task.key}")
    print(f"   • Tiempo agregado: 7h")
    print(f"   • Componentes: OTA Manager + Web Panel")
    print(f"   • Estado: {esp32_task.fields.status.name}")
    print(f"\n🔗 Ver en Jira:")
    print(f"   {os.getenv('JIRA_URL')}/browse/{esp32_task.key}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
