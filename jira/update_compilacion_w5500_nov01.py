#!/usr/bin/env python3
"""
Actualización JIRA - Compilación W5500 + Renombre D13
======================================================
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
    print("🔄 Actualizando JIRA - Compilación W5500 + Renombre D13")
    print("=" * 60)
    
    try:
        # Conectar
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
        
        # Worklog (2 horas reales)
        worklog_comment = """✅ Compilación W5500 + Renombre D13 (1 nov 2025)

**Problemas Resueltos**:
• Driver W5500 no habilitado en ESP-IDF
• Headers faltantes (esp_eth_mac.h, esp_eth_phy.h)
• Config W5500 deshabilitada en sdkconfig

**Soluciones**:
• sdkconfig.defaults: CONFIG_ETH_SPI_ETHERNET_W5500=y
• ethernet_manager.cpp: Includes corregidos
• Reconfiguración completa del proyecto

**Cambios Adicionales**:
• Renombre K13 → D13 en código y tags
• main.cpp: D13_GATEWAY tag actualizado

**Resultado**:
✅ Compilación exitosa: 387 KB binary
✅ Flash usage: 37% (63% libre)
✅ Soporte W5500 completo habilitado
✅ Listo para flashear a ESP32-S3

**Archivos**:
• sdkconfig.defaults
• ethernet_manager.cpp  
• main.cpp

**Próximo**: Flashear firmware y validar con hardware EdgeBox-Lite"""
        
        # Fecha: hoy 1 nov 2025, 2 horas
        work_date = datetime(2025, 11, 1, 14, 0, 0)
        
        worklog = jira.add_worklog(
            issue=task_key,
            timeSpent='2h',
            comment=worklog_comment,
            started=work_date
        )
        
        print(f"✅ Worklog agregado: {worklog.id}")
        print(f"   Tiempo: 2 horas")
        
        # Comentario
        comment = """🎯 **Gateway ESP32 - Compilación W5500 Exitosa**

El proyecto ahora compila correctamente con soporte completo para **Ethernet W5500**:

✅ Drivers W5500 habilitados
✅ Binary size: 387 KB (63% espacio libre)
✅ Código actualizado: K13 → D13
✅ Listo para EdgeBox-Lite

**Hardware Target**: ESP32-S3 + W5500 + CAN transceiver

**Next**: Flash y pruebas con hardware real"""
        
        jira.add_comment(task_key, comment)
        print("✅ Comentario agregado")
        
        print("\n" + "=" * 60)
        print(f"✅ Actualización completa: {task_key}")
        print(f"⏱️  +2h worklog")
        print(f"🔗 {os.getenv('JIRA_URL')}/browse/{task_key}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
