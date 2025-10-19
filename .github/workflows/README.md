# 🤖 Automatización de Issues y Progreso

Este directorio contiene workflows de GitHub Actions para automatizar el seguimiento del progreso de implementación del proyecto.

## 📁 Workflows Disponibles

### 1. `eds-progress-tracker.yml`
**Propósito**: Rastrear automáticamente el progreso de implementación del EDS (Electronic Data Sheet).

**Triggers**:
- Push a `clean-main` o `main` con cambios en:
  - `config/danfoss_r13f*.eds`
  - `src/bl335_gateway/main.py`
  - `tests/e2e/**`
- Pull requests
- Manual (`workflow_dispatch`)

**Acciones**:
1. ✅ Verifica existencia del archivo EDS
2. ✅ Valida sintaxis del EDS (secciones obligatorias)
3. ✅ Ejecuta tests E2E automáticamente
4. ✅ Calcula porcentaje de progreso
5. ✅ Actualiza el issue con comentario automático
6. ✅ Genera badge de progreso (JSON)
7. ✅ Crea resumen en GitHub Actions UI

**Output**:
```
📊 Test Results
Tests: 4/7 passing
Failed: 3
Success Rate: 57%

Progress: [█████░░░░░] 57%

📋 Implementation Checklist
✅ Eds File Created
✅ Gateway Loads Eds
✅ Sdo Implemented
⬜ Pdo Configured
✅ Cia402 Objects
⬜ Tests Passing
```

### 2. `auto-update-issue.yml`
**Propósito**: Actualizar automáticamente los checkboxes del issue de EDS.

**Triggers**:
- Push a `clean-main` o `main` con cambios en:
  - `config/*.eds`
  - `src/bl335_gateway/**`
  - `tests/e2e/**`
- Manual (`workflow_dispatch`)

**Acciones**:
1. ✅ Analiza archivos del proyecto
2. ✅ Determina estado de cada tarea
3. ✅ Actualiza checkboxes en el issue automáticamente
4. ✅ Añade comentario con progreso

**Ejemplo de actualización**:
```diff
- [ ] Crear archivo `.eds` con Object Dictionary completo
+ [x] Crear archivo `.eds` con Object Dictionary completo

- [ ] Definir objetos obligatorios CiA 301
+ [x] Definir objetos obligatorios CiA 301
```

## 🎯 Integración con Issues

### Labels Automáticos

Los workflows buscan issues con las siguientes combinaciones de labels:
- `enhancement` + `documentation` (eds-progress-tracker)
- `eds-implementation` (auto-update-issue)

### Template del Issue

El template en `.github/ISSUE_TEMPLATE/crear_eds_r13f.md` incluye:
```yaml
labels: enhancement, eds-implementation, canopen, documentation
```

Esto permite que los workflows detecten automáticamente el issue correcto.

## 📊 Badge de Progreso

El workflow `eds-progress-tracker.yml` genera un badge JSON en:
```
.github/badges/eds-progress.json
```

Puedes usarlo con shields.io o servicios similares:
```markdown
![EDS Progress](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/arturo393/crane-emergency-stop/clean-main/.github/badges/eds-progress.json)
```

## 🚀 Uso Manual

### Ejecutar tracker manualmente:
```bash
gh workflow run eds-progress-tracker.yml
```

### Ejecutar actualización de checkboxes:
```bash
gh workflow run auto-update-issue.yml
```

### Ver resultados:
```bash
gh run list --workflow=eds-progress-tracker.yml
gh run view <run-id>
```

## 🔧 Configuración

### Permisos Requeridos

Los workflows necesitan estos permisos (ya configurados):
```yaml
permissions:
  issues: write
  contents: read
```

### Secretos

- `GITHUB_TOKEN`: Automáticamente proporcionado por GitHub Actions

### Variables de Entorno

Los workflows usan estas variables:
- `TESTS_PASSED`: Número de tests pasados
- `TESTS_FAILED`: Número de tests fallados
- `TESTS_TOTAL`: Total de tests
- `TEST_PERCENTAGE`: Porcentaje de éxito

## 📝 Personalización

### Añadir nuevas verificaciones

Edita el script de Python en `eds-progress-tracker.yml`:

```python
# Añadir nueva verificación
checklist = {
    # ... existentes ...
    'nueva_verificacion': False
}

# Lógica de verificación
if condition:
    checklist['nueva_verificacion'] = True
```

### Modificar thresholds

Cambiar el umbral de tests pasando:

```yaml
if tests_total > 0 and tests_passed >= tests_total * 0.7:  # 70%
    checklist['tests_passing'] = True
```

### Cambiar colores del badge

```yaml
if [ "$TEST_PERCENTAGE" -ge 80 ]; then
  COLOR="brightgreen"
elif [ "$TEST_PERCENTAGE" -ge 60 ]; then
  COLOR="yellow"
else
  COLOR="red"
fi
```

## 🐛 Troubleshooting

### Workflow no se ejecuta

1. Verificar que el issue tenga los labels correctos
2. Verificar permisos en Settings → Actions → General → Workflow permissions
3. Revisar logs en Actions tab

### Tests fallan en CI

1. Los tests E2E requieren `vcan` (virtual CAN)
2. CI usa `sudo modprobe vcan` pero puede fallar
3. Los tests tienen `continue-on-error: true` para no bloquear

### Checkboxes no se actualizan

1. Verificar que el issue esté `open`
2. Verificar formato de los checkboxes en el issue: `- [ ] Texto`
3. Ver logs del workflow para errores

## 📚 Referencias

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [actions/github-script](https://github.com/actions/github-script)
- [Issue Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)

---

**Última actualización**: 2025-10-19  
**Mantenedor**: @arturo393
