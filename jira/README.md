# SafetyMind Jira Manager

Herramienta unificada para gestión completa de proyectos Jira del sistema de monitoreo SafetyMind.

## 🚀 Características

- **Gestión unificada**: Un solo script para todas las operaciones de Jira
- **Importación completa**: Estructura de épicos y tareas con cronograma
- **Limpieza automática**: Eliminación de duplicados y reorganización
- **Asignación inteligente**: Tareas asignadas a épicos por contenido
- **Cronograma detallado**: Fechas y estimaciones de tiempo
- **Diagnóstico completo**: Verificación de conexión y permisos

## 📋 Requisitos

```bash
pip install -r requirements-jira.txt
```

## ⚙️ Configuración

Crear archivo `.env` con:

```env
JIRA_URL=https://tu-instancia.atlassian.net
JIRA_EMAIL=tu-email@domain.com
JIRA_API_TOKEN=tu-api-token
JIRA_PROJECT_KEY=IM
```

## 🛠️ Uso

### Comandos principales

```bash
# Importar estructura completa del proyecto
python3 jira_manager.py --action import

# Limpiar épicos duplicados
python3 jira_manager.py --action cleanup

# Asignar tareas a épicos
python3 jira_manager.py --action assign

# Actualizar cronograma y fechas
python3 jira_manager.py --action schedule

# Verificar estado del proyecto
python3 jira_manager.py --action check

# Diagnóstico completo
python3 jira_manager.py --action diagnose
```

### Flujo de trabajo típico

1. **Diagnóstico inicial**:
   ```bash
   python3 jira_manager.py --action diagnose
   ```

2. **Importar proyecto**:
   ```bash
   python3 jira_manager.py --action import
   ```

3. **Verificar resultado**:
   ```bash
   python3 jira_manager.py --action check
   ```

## 📊 Estructura del Proyecto

### Épicos

1. **Fundación y Desarrollo Local** (96h, 2.4 semanas)
   - Entorno de desarrollo con Docker
   - Sistema de simulación completo
   - Agente local containerizado
   - Documentación de migración

2. **Infraestructura Cloud y Agente Distribuido** (176h, 4.4 semanas)
   - Servidor cloud con orquestación
   - Base de datos PostgreSQL en cloud
   - Icinga2 Master e IcingaWeb2 cloud
   - Package Debian del agente
   - APIs REST y seguridad
   - Testing end-to-end

3. **Cliente Piloto y Escalamiento SaaS** (112h, 2.8 semanas)
   - Onboarding y documentación cliente
   - Instalación en cliente piloto
   - Go-live del primer cliente
   - Arquitectura multi-tenant
   - RBAC y onboarding automatizado

### Cronograma

- **Inicio**: 3 Noviembre 2025 (lunes)
- **Fin**: 22 Diciembre 2025 (lunes)
- **Duración**: 7 semanas (49 días)
- **Total horas**: 384h (48 días laborales)

## 🔧 Funcionalidades

### Importación (`--action import`)
- Crea estructura completa de épicos y tareas
- Asigna fechas de entrega automáticamente
- Incluye estimaciones de tiempo en descripciones
- Etiquetas automáticas por categoría

### Limpieza (`--action cleanup`)
- Identifica y elimina épicos duplicados
- Mantiene la versión más reciente
- Reorganiza estructura del proyecto

### Asignación (`--action assign`)
- Asigna tareas a épicos basado en contenido
- Utiliza palabras clave inteligentes
- Mapeo automático por categorías

### Cronograma (`--action schedule`)
- Actualiza fechas de entrega (due dates)
- Calcula cronograma basado en dependencias
- Formato de estimaciones estándar

### Verificación (`--action check`)
- Resumen de épicos y tareas
- Estado de asignaciones
- Fechas de entrega configuradas

### Diagnóstico (`--action diagnose`)
- Test de conexión a Jira
- Verificación de permisos
- Validación de configuración

## 📝 Archivos

- `jira_manager.py` - Script principal unificado
- `.env` - Configuración de conexión
- `requirements-jira.txt` - Dependencias Python
- `README.md` - Esta documentación

## 🎯 Roadmap

- [x] Unificación de scripts existentes
- [x] Estructura de épicos y tareas completa
- [x] Cronograma detallado con fechas
- [x] Sistema de limpieza automática
- [ ] Integración con CI/CD
- [ ] Reportes automáticos
- [ ] Sincronización bidireccional

## 🐛 Troubleshooting

### Error de conexión
```bash
python3 jira_manager.py --action diagnose
```

### Campos no válidos
- Algunos campos pueden no estar disponibles según configuración de Jira
- El script se adapta automáticamente a campos disponibles

### Permisos insuficientes
- Verificar que el API token tenga permisos de escritura
- Confirmar acceso al proyecto especificado

---

**Versión**: 2.0.0  
**Autor**: SafetyMind Team  
**Fecha**: Octubre 2025