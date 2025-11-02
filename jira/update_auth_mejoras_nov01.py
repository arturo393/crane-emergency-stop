#!/usr/bin/env python3
"""
Actualización JIRA - Mejoras Gateway: Auth + OTA + SD Logging
==============================================================
Fecha: 1 de noviembre de 2025
Tarea: GAT-37 - ESP32 Gateway
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

def main():
    print("🚀 Actualizando JIRA - Mejoras Gateway (Auth, OTA, Logging)")
    print("=" * 60)
    
    try:
        jira = JIRA(
            server=os.getenv('JIRA_URL'),
            basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
        )
        
        # Buscar tarea
        task_key = None
        for key in ['GAT-37', 'GAT-6']:
            try:
                task = jira.issue(key)
                task_key = key
                break
            except:
                continue
        
        if not task:
            print("❌ Tarea no encontrada")
            return 1
        
        print(f"✅ Tarea: {task_key}")
        
        # Worklog (3 horas)
        worklog_comment = """🔒 Mejoras Gateway ESP32 (1 nov 2025)

**1. Sistema de Autenticación TCP** ✅
• AuthManager con token-based auth
• Rate limiting (3 intentos, 5 min bloqueo)
• Protección timing attacks
• Prompt de autenticación al conectar

**Implementación**:
• auth_manager.h/cpp: Gestor completo
• Integración en network_task
• Token por defecto: D13-SECURE-2025
• Generador de tokens aleatorios

**Protocolo**:
```
Cliente → "AUTH: Ingrese token"
Cliente → <token>
Servidor → "AUTH: OK" / "AUTH: ERROR"
```

**Archivos**:
• main/auth_manager.h (nuevo)
• main/auth_manager.cpp (nuevo)
• main/main.cpp (integración)
• main/CMakeLists.txt

**Compilación**:
✅ Binary: 390 KB (63% libre)
✅ Seguridad mejorada
✅ Listo para producción

**Próximo**: OTA updates + SD logging"""
        
        # 3 horas trabajo
        work_date = datetime(2025, 11, 1, 16, 30, 0)
        
        worklog = jira.add_worklog(
            issue=task_key,
            timeSpent='3h',
            comment=worklog_comment,
            started=work_date
        )
        
        print(f"✅ Worklog agregado: {worklog.id}")
        print(f"   Tiempo: 3 horas")
        
        # Comentario
        comment = """🔐 **Seguridad Implementada - Autenticación TCP**

Gateway ahora requiere **autenticación token-based** para acceso:

✅ Sistema completo en AuthManager
✅ Rate limiting anti-brute force
✅ Protección timing attacks
✅ Token configurable

**Uso**:
```bash
nc 192.168.1.100 5000
> D13-SECURE-2025
< AUTH: OK - Autenticado
> ENABLE
< OK: Status=0x0007, State=4
```

**Next**: OTA updates + SD card logging"""
        
        jira.add_comment(task_key, comment)
        print("✅ Comentario agregado")
        
        print("\n" + "=" * 60)
        print(f"✅ Actualización completa: {task_key}")
        print(f"⏱️  +3h worklog (autenticación)")
        print(f"🔗 {os.getenv('JIRA_URL')}/browse/{task_key}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
