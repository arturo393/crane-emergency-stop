#!/usr/bin/env python3
"""
Actualización JIRA - SD Logger con Auto-rotación y Auto-limpieza
================================================================
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
    print("🚀 Actualizando JIRA - SD Logger Implementation")
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
        
        if not task_key:
            print("❌ Tarea no encontrada")
            return 1
        
        print(f"✅ Tarea: {task_key}")
        
        # Worklog (3 horas)
        worklog_comment = """💾 SD Card Logger con Auto-rotación/limpieza (1 nov 2025)

**Sistema de Logging Persistente** ✅

**Características**:
• Auto-rotación: Archivos de 1 MB máximo
• Auto-limpieza: Mantiene últimos 10 archivos
• Thread-safe: FreeRTOS mutex
• Degradación elegante: Continúa sin SD
• Formato: [YYYY-MM-DD HH:MM:SS.mmm] [LEVEL] TAG: mensaje

**Implementación**:
```cpp
class SDLogger {
    bool init();                    // Montar SD, crear archivo
    void log(...);                   // Thread-safe logging
    void rotate_log();               // Forzar rotación
    void cleanup_old_logs();         // Eliminar antiguos
    bool get_disk_info(...);         // Espacio disponible
}
```

**Puntos de Logging**:
✅ CAN bus: init, errores, baudrate
✅ Autenticación: OK/fail, IPs bloqueadas
✅ Comandos: ENABLE, SHUTDOWN, etc
✅ Transiciones CiA402: State changes
✅ Errores: Mutex, comunicación

**Archivos Creados**:
• main/sd_logger.h (nuevo - 120 líneas)
• main/sd_logger.cpp (nuevo - 313 líneas)
• main/hardware_config.h (pines SD)
• test/device/test_sd_logger.cpp (7 tests)
• test/native/test_sd_logger_unit.cpp (6 tests)

**Hardware Config**:
• Pines: MOSI=33, MISO=34, CLK=35, CS=36
• Bus: SPI2_HOST @ 20 MHz
• FS: FAT32
• Rotación: 1 MB/archivo
• Límite: 10 archivos

**Compilación**:
✅ Binary: 465 KB (56% libre)
✅ +75 KB (SD logger completo)
✅ Tests device + native
✅ Listo para validación hardware

**Ejemplo Logs**:
```
[2025-11-01 16:45:23.456] [INFO ] D13: CAN bus inicializado (TX:4, RX:5, 250kbps)
[2025-11-01 16:45:25.123] [INFO ] D13: Cliente autenticado desde 192.168.1.100
[2025-11-01 16:45:26.789] [INFO ] D13: Comando ejecutado: ENABLE desde 192.168.1.100
[2025-11-01 16:45:27.012] [INFO ] D13: Transición CiA402: State 2->3, Status 0x0021->0x0023
```

**Próximo**: Validación hardware + OTA updates"""
        
        # 3 horas trabajo (diseño 1.5h + implementación 1h + tests 0.5h)
        work_date = datetime(2025, 11, 1, 17, 30, 0)
        
        worklog = jira.add_worklog(
            issue=task_key,
            timeSpent='3h',
            comment=worklog_comment,
            started=work_date
        )
        
        print(f"✅ Worklog agregado: {worklog.id}")
        print(f"   Tiempo: 3 horas")
        
        # Comentario
        comment = """💾 **SD Card Logger - Implementación Completa**

Sistema de logging persistente con gestión automática de espacio:

**Features Implementadas**:
✅ **Auto-rotación**: Archivos limitados a 1 MB
✅ **Auto-limpieza**: Solo últimos 10 archivos (elimina más antiguos)
✅ **Thread-safe**: Mutex FreeRTOS para escrituras concurrentes
✅ **Graceful degradation**: Sistema continúa sin SD card
✅ **Logging completo**: CAN, Auth, Comandos, Estados

**Archivos de Log**:
```
/sdcard/gateway_20251101_164523.log  (1.0 MB)
/sdcard/gateway_20251101_164812.log  (0.8 MB)
/sdcard/gateway_20251101_165034.log  (0.3 MB)
... (máximo 10 archivos)
```

**Formato**:
```
[2025-11-01 16:45:23.456] [INFO ] D13: Mensaje de log
                         [WARN ]
                         [ERROR]
                         [DEBUG]
```

**Tests**:
• 7 tests de dispositivo (requiere ESP32 + SD)
• 6 tests unitarios (host)

**Tamaño Firmware**: 465 KB (+75 KB por SD logger)

**Pendiente**: Validación en hardware con SD card real

**Next**: OTA Updates para actualizaciones remotas"""
        
        jira.add_comment(task_key, comment)
        print("✅ Comentario agregado")
        
        print("\n" + "=" * 60)
        print(f"✅ Actualización completa: {task_key}")
        print(f"⏱️  +3h worklog (SD logger)")
        print(f"📦 Binary: 465 KB")
        print(f"🔗 {os.getenv('JIRA_URL')}/browse/{task_key}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
