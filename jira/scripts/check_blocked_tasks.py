#!/usr/bin/env python3
"""
Script para detectar tareas bloqueadas y crear GitHub Issues automáticamente
"""
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

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

def create_github_issue(title, body):
    """Crear issue en GitHub"""
    github_token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPOSITORY', 'arturo393/crane-emergency-stop')
    
    if not github_token:
        print("⚠️ GITHUB_TOKEN no disponible, saltando creación de issue")
        return
    
    url = f'https://api.github.com/repos/{repo}/issues'
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'title': title,
        'body': body,
        'labels': ['jira-sync', 'blocked', 'auto-generated']
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        print(f"✅ GitHub Issue creado: {response.json()['html_url']}")
    else:
        print(f"❌ Error creando issue: {response.status_code} - {response.text}")

def check_blocked_tasks():
    """Verificar tareas bloqueadas y crear issues si es necesario"""
    project_key = os.getenv('JIRA_PROJECT_KEY', 'GAT')
    jira = get_jira_connection()
    
    # Buscar tareas bloqueadas
    blocked_tasks = jira.search_issues(
        f'project={project_key} AND labels in (blocked) AND status != Done',
        maxResults=50
    )
    
    print(f"\n🔍 Verificando tareas bloqueadas...")
    print(f"   Tareas bloqueadas encontradas: {len(blocked_tasks)}")
    
    if not blocked_tasks:
        print("   ✅ No hay tareas bloqueadas")
        return
    
    # Verificar si ya existe issue en GitHub para cada tarea
    for task in blocked_tasks:
        issue_title = f"[JIRA-{task.key}] Tarea bloqueada: {task.fields.summary}"
        
        # Buscar si ya existe el issue
        github_token = os.getenv('GITHUB_TOKEN')
        repo = os.getenv('GITHUB_REPOSITORY', 'arturo393/crane-emergency-stop')
        
        if github_token:
            search_url = f'https://api.github.com/search/issues?q=repo:{repo}+{task.key}+in:title+is:open'
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            search_response = requests.get(search_url, headers=headers)
            
            if search_response.status_code == 200:
                existing_issues = search_response.json().get('total_count', 0)
                
                if existing_issues > 0:
                    print(f"   ℹ️ Issue ya existe para {task.key}, saltando...")
                    continue
        
        # Crear issue si no existe
        issue_body = f"""## Tarea Bloqueada en JIRA

**JIRA Task:** [{task.key}]({os.getenv('JIRA_URL')}/browse/{task.key})  
**Status:** {task.fields.status.name}  
**Due Date:** {task.fields.duedate or 'Sin fecha'}

### Descripción
{task.fields.description or 'Sin descripción'}

### Acción Requerida
Esta tarea está marcada como bloqueada en JIRA. Por favor:

1. Revisar el bloqueador en JIRA
2. Tomar acciones para desbloquear
3. Actualizar estado en JIRA
4. Cerrar este issue cuando se resuelva

---

*Issue generado automáticamente por GitHub Actions*  
*Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        create_github_issue(issue_title, issue_body)

def check_overdue_tasks():
    """Verificar tareas vencidas"""
    project_key = os.getenv('JIRA_PROJECT_KEY', 'GAT')
    jira = get_jira_connection()
    
    # Buscar tareas vencidas
    today = datetime.now().strftime('%Y-%m-%d')
    overdue_tasks = jira.search_issues(
        f'project={project_key} AND duedate < {today} AND status != Done',
        maxResults=50
    )
    
    print(f"\n📅 Verificando tareas vencidas...")
    print(f"   Tareas vencidas encontradas: {len(overdue_tasks)}")
    
    if overdue_tasks:
        print("\n⚠️ TAREAS VENCIDAS:")
        for task in overdue_tasks:
            print(f"   • {task.key}: {task.fields.summary} (Due: {task.fields.duedate})")

if __name__ == '__main__':
    try:
        check_blocked_tasks()
        check_overdue_tasks()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
