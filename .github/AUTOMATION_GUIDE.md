# Automatización GitHub - Guía Rápida

## ✅ Workflows Activos

### 1. ESP32 Progress Tracker
- **Qué hace**: Actualiza issue con progreso de ESP32
- **Trigger**: Push a main, manual
- **Issue**: Se crea/actualiza automáticamente

### 2. Auto-close Issues
- **Qué hace**: Cierra issues cuando marques [x] en README
- **Trigger**: Push a main

### 3. Auto-assign
- **Qué hace**: Te asigna issues que creas
- **Trigger**: Nuevo issue

### 4. Auto-labeler
- **Qué hace**: Agrega labels según contenido
- **Trigger**: Nuevo issue

### 5. GitHub Projects
- **Qué hace**: Sincroniza con Projects
- **Trigger**: Issues abiertos/cerrados

### 6. Welcome Bot
- **Qué hace**: Saluda en nuevos issues
- **Trigger**: Nuevo issue

## 🚀 Activar GitHub Projects

1. Ve a tu repo → Projects → New project
2. Nombre: "ESP32 Development"
3. Copiar Project ID del URL
4. Actualizar en workflows

## 📝 Issue Templates

Ubicación: `.github/ISSUE_TEMPLATE/`
- `esp32-bug.yml` - Reportar bugs
- `esp32-feature.yml` - Nuevas funcionalidades

## ⚡ Comandos Rápidos

```bash
# Activar workflow manual
gh workflow run esp32-tracker.yml

# Ver workflows
gh workflow list

# Ver runs
gh run list
```
