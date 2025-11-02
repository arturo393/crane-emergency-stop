#!/usr/bin/env python3
"""
Script para generar reporte automático de progreso desde JIRA
Se ejecuta en GitHub Actions para mantener sincronizado el estado del proyecto
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar directorio padre al path para importar jira_manager
sys.path.insert(0, str(Path(__file__).parent.parent))

from jira import JIRA
from dotenv import load_dotenv

load_dotenv()

def get_jira_connection():
    """Conectar a JIRA"""
    return JIRA(
        server=os.getenv('JIRA_URL'),
        basic_auth=(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
    )

def generate_report():
    """Generar reporte de progreso en Markdown"""
    project_key = os.getenv('JIRA_PROJECT_KEY', 'GAT')
    jira = get_jira_connection()
    
    # Obtener todas las tareas
    all_issues = jira.search_issues(
        f'project={project_key} ORDER BY key ASC',
        maxResults=100
    )
    
    # Separar épicos y tareas
    epics = [i for i in all_issues if i.fields.issuetype.name == 'Epic']
    tasks = [i for i in all_issues if i.fields.issuetype.name == 'Task']
    
    # Clasificar por estado
    done = [t for t in tasks if t.fields.status.name == 'Done']
    in_progress = [t for t in tasks if t.fields.status.name == 'In Progress']
    to_do = [t for t in tasks if t.fields.status.name == 'To Do']
    blocked = [t for t in tasks if 'blocked' in [l.lower() for l in (t.fields.labels or [])]]
    
    # Generar markdown
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""# 📊 Reporte de Progreso JIRA - Proyecto K13 Puente Grúa

**Última actualización:** {now}  
**Proyecto:** {project_key}

---

## 📈 Resumen Ejecutivo

| Métrica | Valor | Porcentaje |
|---------|-------|------------|
| **Tareas Totales** | {len(tasks)} | 100% |
| **✅ Completadas** | {len(done)} | {len(done)/len(tasks)*100:.1f}% |
| **🔄 En Progreso** | {len(in_progress)} | {len(in_progress)/len(tasks)*100:.1f}% |
| **⏸️ Por Hacer** | {len(to_do)} | {len(to_do)/len(tasks)*100:.1f}% |
| **⚠️ Bloqueadas** | {len(blocked)} | {len(blocked)/len(tasks)*100:.1f}% |
| **📋 Épicos** | {len(epics)} | - |

---

## 🎯 Progreso por Épico

"""
    
    # Desglose por épico
    tasks_by_epic = {}
    for task in tasks:
        epic_key = getattr(task.fields.parent, 'key', 'Sin épico') if hasattr(task.fields, 'parent') and task.fields.parent else 'Sin épico'
        if epic_key not in tasks_by_epic:
            tasks_by_epic[epic_key] = []
        tasks_by_epic[epic_key].append(task)
    
    for epic in epics:
        epic_tasks = tasks_by_epic.get(epic.key, [])
        epic_done = [t for t in epic_tasks if t.fields.status.name == 'Done']
        epic_progress = len(epic_done) / len(epic_tasks) * 100 if epic_tasks else 0
        
        status_emoji = '✅' if epic_progress == 100 else ('🔄' if epic_progress > 0 else '⏸️')
        
        report += f"""
### {status_emoji} {epic.key}: {epic.fields.summary}

- **Tareas:** {len(epic_tasks)}
- **Completadas:** {len(epic_done)} ({epic_progress:.0f}%)
- **Progreso:** {'█' * int(epic_progress/10)}{'░' * (10-int(epic_progress/10))} {epic_progress:.0f}%

"""
    
    # Tareas en progreso
    if in_progress:
        report += """
---

## 🔄 Tareas En Progreso

| Tarea | Resumen | Due Date |
|-------|---------|----------|
"""
        for task in in_progress:
            due = task.fields.duedate or 'Sin fecha'
            report += f"| {task.key} | {task.fields.summary[:50]} | {due} |\n"
    
    # Tareas bloqueadas
    if blocked:
        report += """
---

## ⚠️ Tareas Bloqueadas (Requieren Atención)

| Tarea | Resumen | Estado |
|-------|---------|--------|
"""
        for task in blocked:
            report += f"| {task.key} | {task.fields.summary[:50]} | {task.fields.status.name} |\n"
    
    # Próximas tareas (ordenadas por due date)
    upcoming = sorted([t for t in to_do if t.fields.duedate], 
                     key=lambda x: x.fields.duedate)[:5]
    
    if upcoming:
        report += """
---

## 📅 Próximas Tareas (Top 5)

| Tarea | Resumen | Due Date |
|-------|---------|----------|
"""
        for task in upcoming:
            report += f"| {task.key} | {task.fields.summary[:50]} | {task.fields.duedate} |\n"
    
    # Recomendaciones
    report += """
---

## 💡 Recomendaciones

"""
    
    if blocked:
        report += f"- ⚠️ **Atención:** {len(blocked)} tarea(s) bloqueada(s) requieren resolución inmediata\n"
    
    if len(in_progress) > 5:
        report += f"- 🎯 **Foco:** {len(in_progress)} tareas en progreso - considerar reducir WIP (Work In Progress)\n"
    
    if len(done) / len(tasks) >= 0.8:
        report += f"- 🎉 **Excelente:** {len(done)/len(tasks)*100:.0f}% de tareas completadas - proyecto avanzando muy bien\n"
    
    deadline = datetime(2025, 12, 5)
    days_left = (deadline - datetime.now()).days
    report += f"\n- 📅 **Deadline:** 5 de diciembre de 2025 ({days_left} días restantes)\n"
    
    report += """
---

*Reporte generado automáticamente por GitHub Actions*  
*Para ver detalles completos: [JIRA Project](https://safetymind-team-ogsoj2pu.atlassian.net)*
"""
    
    return report

if __name__ == '__main__':
    try:
        report = generate_report()
        print(report)
    except Exception as e:
        print(f"Error generando reporte: {e}", file=sys.stderr)
        sys.exit(1)
