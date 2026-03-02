# Checklist de Deployment - Migración Sistema de Agendamiento

**Fecha:** 28/02/2026  
**Versión:** 1.0

## ✅ Pre-Deployment

### Configuración
- [ ] Variables de entorno configuradas en `.env`
  - [ ] `SPREADSHEET_ID` configurado
  - [ ] `SHEET_NAME` configurado (default: "Citas")
  - [ ] `CALENDAR_ID` configurado (default: "primary")
  - [ ] `GOOGLE_CREDENTIALS` configurado con JSON completo

### Google Sheets
- [ ] Spreadsheet creado y accesible
- [ ] Service account tiene permisos de edición
- [ ] Estructura de columnas correcta:
  ```
  A: id | B: telefono | C: nombre | D: servicio | E: fecha | F: hora | G: estado | H: notas
  ```
- [ ] Fila 1 contiene los headers
- [ ] Datos de prueba agregados (opcional)

### Dependencias
- [ ] Ejecutar: `pip install -r requirements.txt`
- [ ] Verificar instalación de Google packages:
  ```bash
  python -c "import google.auth; print('✅ Google Auth OK')"
  python -c "from googleapiclient.discovery import build; print('✅ Google API Client OK')"
  ```

### Código
- [ ] Archivo `google_sheets_client.py` presente
- [ ] Archivo `chatbot_logic.py` modificado
- [ ] Archivo `config.py` actualizado
- [ ] Sin errores de sintaxis (ejecutar `getDiagnostics`)

## ✅ Testing Pre-Producción

### Test de Conexión
```bash
# Test 1: Verificar conexión a Google Sheets
python -c "from google_sheets_client import get_sheets_client; client = get_sheets_client(); print('✅ Conexión exitosa')"

# Test 2: Leer citas
python -c "from google_sheets_client import get_sheets_client; client = get_sheets_client(); citas = client.get_all_appointments(); print(f'✅ {len(citas)} citas encontradas')"
```

### Test de Flujos
- [ ] **Agendamiento (Opción 1)**
  - [ ] Enviar "hola" al chatbot
  - [ ] Seleccionar opción 1
  - [ ] Verificar que envía el enlace: [URL_SISTEMA_EXTERNO]
  - [ ] Confirmar que NO ejecuta lógica interna

- [ ] **Reagendamiento (Opción 2)**
  - [ ] Tener al menos 1 cita en Google Sheets
  - [ ] Seleccionar opción 2
  - [ ] Verificar que muestra citas desde Google Sheets
  - [ ] Seleccionar una cita
  - [ ] Ingresar nueva fecha/hora (formato: DD/MM/AAAA HH:MM)
  - [ ] Confirmar cambio
  - [ ] Verificar actualización en Google Sheets

- [ ] **Cancelación (Opción 3)**
  - [ ] Tener al menos 1 cita en Google Sheets
  - [ ] Seleccionar opción 3
  - [ ] Verificar que muestra citas desde Google Sheets
  - [ ] Seleccionar una cita
  - [ ] Confirmar cancelación
  - [ ] Verificar que en Google Sheets el estado cambió a "cancelada"
  - [ ] Verificar que la fila NO fue eliminada

- [ ] **Consulta (Opción 4)**
  - [ ] Tener al menos 1 cita activa en Google Sheets
  - [ ] Seleccionar opción 4
  - [ ] Verificar que muestra citas desde Google Sheets
  - [ ] Confirmar formato correcto

- [ ] **Hablar con Profesional (Opción 5)**
  - [ ] Seleccionar opción 5
  - [ ] Verificar que activa handoff a humano
  - [ ] Confirmar que funciona igual que antes

### Test de Validaciones
- [ ] Reagendamiento con fecha pasada (debe rechazar)
- [ ] Reagendamiento con fin de semana (debe rechazar)
- [ ] Reagendamiento con horario fuera de rango (debe rechazar)
- [ ] Reagendamiento con hora de almuerzo (debe rechazar)
- [ ] Formato de fecha incorrecto (debe pedir formato correcto)

## ✅ Deployment

### Backup
- [ ] Backup de base de datos PostgreSQL
- [ ] Backup de código anterior (git commit/tag)
- [ ] Backup de Google Sheet (hacer copia)

### Deploy
- [ ] Detener servicio actual
- [ ] Actualizar código
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Configurar variables de entorno
- [ ] Iniciar servicio
- [ ] Verificar logs de inicio

### Verificación Post-Deploy
- [ ] Servicio levantado correctamente
- [ ] Endpoint `/health` responde OK
- [ ] Logs sin errores críticos
- [ ] Conexión a PostgreSQL OK
- [ ] Conexión a Google Sheets OK
- [ ] Conexión a Evolution API OK

## ✅ Monitoreo Post-Deployment

### Primeras 2 Horas
- [ ] Monitorear logs cada 15 minutos
- [ ] Verificar que usuarios reciben el enlace de agendamiento
- [ ] Confirmar que reagendamiento funciona
- [ ] Confirmar que cancelación funciona
- [ ] Confirmar que consulta funciona

### Primeras 24 Horas
- [ ] Revisar logs cada 2 horas
- [ ] Verificar métricas de uso
- [ ] Confirmar que no hay errores de Google Sheets API
- [ ] Verificar que las actualizaciones se reflejan en el Sheet

### Primera Semana
- [ ] Revisar logs diariamente
- [ ] Recopilar feedback de usuarios
- [ ] Monitorear tasa de errores
- [ ] Verificar integridad de datos en Google Sheets

## ✅ Rollback (Si es necesario)

### Indicadores para Rollback
- [ ] Tasa de errores > 10%
- [ ] Google Sheets API no responde
- [ ] Usuarios reportan problemas críticos
- [ ] Pérdida de datos

### Procedimiento de Rollback
1. [ ] Detener servicio
2. [ ] Restaurar código anterior (git revert/checkout)
3. [ ] Restaurar dependencias anteriores
4. [ ] Iniciar servicio
5. [ ] Verificar funcionamiento
6. [ ] Notificar a usuarios (si aplica)

Ver `MIGRATION_GUIDE.md` sección "Instrucciones de Rollback" para detalles.

## ✅ Documentación

- [ ] `MIGRATION_GUIDE.md` revisado
- [ ] `CAMBIOS_REALIZADOS.md` revisado
- [ ] `CHECKLIST_DEPLOYMENT.md` (este archivo) completado
- [ ] Comentarios en código revisados
- [ ] README.md actualizado (si aplica)

## ✅ Comunicación

- [ ] Equipo técnico notificado
- [ ] Usuarios informados del nuevo flujo de agendamiento
- [ ] Documentación compartida con stakeholders
- [ ] Plan de rollback comunicado

## 📊 Métricas a Monitorear

### Técnicas
- Tiempo de respuesta del chatbot
- Tasa de errores de Google Sheets API
- Latencia de lectura/escritura en Sheet
- Uso de memoria/CPU

### Negocio
- Número de usuarios que usan el enlace de agendamiento
- Número de reagendamientos exitosos
- Número de cancelaciones
- Número de consultas de citas

## 🚨 Contactos de Emergencia

- **Equipo Técnico:** [Agregar contacto]
- **Responsable Google Sheets:** [Agregar contacto]
- **Responsable Sistema Externo:** [Agregar contacto]

## 📝 Notas Adicionales

- El sistema mantiene compatibilidad con PostgreSQL para conversaciones
- El código legacy está preservado y puede reactivarse
- Google Sheets es la única fuente de verdad para citas
- El sistema externo maneja nuevos agendamientos

---

**Checklist completado por:** _________________  
**Fecha:** _________________  
**Firma:** _________________

## ✅ Aprobación Final

- [ ] Checklist 100% completado
- [ ] Tests pasando
- [ ] Documentación completa
- [ ] Equipo notificado
- [ ] Listo para producción

**Aprobado por:** _________________  
**Fecha:** _________________
