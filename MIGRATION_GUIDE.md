# Guía de Migración - Sistema de Agendamiento

**Fecha de migración:** 28 de febrero de 2026  
**Responsable:** Equipo de Desarrollo  
**Estado:** Completado

## Resumen de Cambios

Este documento describe la migración del sistema de agendamiento de citas desde una implementación interna con PostgreSQL hacia un sistema externo y Google Sheets como fuente de datos.

## Cambios Realizados

### 1. Agendamiento de Citas

#### Antes
- El chatbot manejaba todo el flujo de agendamiento internamente
- Consultaba disponibilidad en PostgreSQL
- Creaba citas directamente en la base de datos

#### Después
- El chatbot redirige al usuario a un sistema externo de agendamiento
- URL del sistema: https://n8n-orthodontofront.dtbfmw.easypanel.host/
- No se ejecuta ninguna lógica interna de agendamiento

#### Código Afectado
- `chatbot_logic.py`: Método `handle_menu()` - Opción 1 (Agendar)
- Todos los métodos `handle_agendar_*` fueron comentados (NO eliminados)
- Métodos de disponibilidad y servicios comentados

### 2. Reagendamiento de Citas

#### Antes
- Consultaba citas desde PostgreSQL
- Verificaba disponibilidad de horarios
- Actualizaba directamente en la base de datos

#### Después
- Consulta citas desde Google Sheets
- Permite al usuario ingresar nueva fecha/hora directamente
- Actualiza en Google Sheets (NO en PostgreSQL)

#### Código Afectado
- `chatbot_logic.py`: Métodos `handle_reagendar_*`
- Nuevo cliente: `google_sheets_client.py`

### 3. Cancelación de Citas

#### Antes
- Consultaba citas desde PostgreSQL
- Marcaba como cancelada en la base de datos

#### Después
- Consulta citas desde Google Sheets
- Marca como cancelada en Google Sheets (NO elimina la fila)

#### Código Afectado
- `chatbot_logic.py`: Métodos `handle_cancelar_*`

### 4. Consulta de Citas

#### Antes
- Consultaba citas desde PostgreSQL

#### Después
- Consulta citas desde Google Sheets

#### Código Afectado
- `chatbot_logic.py`: Método `handle_consultar()`

## Archivos Nuevos

### `google_sheets_client.py`
Cliente para interactuar con Google Sheets como base de datos de citas.

**Funcionalidades:**
- `get_all_appointments()`: Obtiene todas las citas
- `get_appointments_by_phone(telefono)`: Obtiene citas de un paciente
- `get_appointment_by_id(id)`: Obtiene una cita específica
- `update_appointment(id, updates)`: Actualiza una cita
- `cancel_appointment(id)`: Marca una cita como cancelada
- `format_appointment(appointment)`: Formatea una cita para mostrar

## Archivos Modificados

### `chatbot_logic.py`
- **Líneas 1-10**: Agregado import de `google_sheets_client`
- **Líneas 288-387**: Métodos legacy de disponibilidad y servicios comentados
- **Líneas 387-420**: Métodos legacy de PostgreSQL comentados
- **Líneas 700-1100**: Lógica de agendamiento comentada
- **Líneas 1100-1200**: Métodos legacy de reagendamiento comentados
- **Método `handle_menu()`**: Opción 1 ahora envía enlace externo
- **Métodos `handle_reagendar_*`**: Migrados a Google Sheets
- **Métodos `handle_cancelar_*`**: Migrados a Google Sheets
- **Método `handle_consultar()`**: Migrado a Google Sheets

### `config.py`
Agregadas nuevas variables de configuración:
```python
spreadsheet_id: str
sheet_name: str = "Citas"
calendar_id: str = "primary"
google_credentials: str
```

### `requirements.txt`
Agregadas dependencias de Google Sheets:
```
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.116.0
```

### `.env.example`
Agregadas variables de ejemplo para Google Sheets.

## Configuración Requerida

### Variables de Entorno

Agregar al archivo `.env`:

```bash
# Google Sheets Configuration
SPREADSHEET_ID=1F8MG-UU0af0aEj87TcUpPmP4kcp3-GTddKOSJd2pIKw
SHEET_NAME=Citas
CALENDAR_ID=primary
GOOGLE_CREDENTIALS={"type":"service_account","project_id":"odontologica-n8n",...}
```

### Estructura del Google Sheet

El Google Sheet debe tener las siguientes columnas (fila 1):

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| id | telefono | nombre | servicio | fecha | hora | estado | notas |

**Ejemplo de datos:**
```
1 | 5551234567 | Juan Pérez | Limpieza | 05/03/2026 | 14:30 | agendada | 
2 | 5559876543 | María López | Ortodoncia | 06/03/2026 | 10:00 | agendada |
```

## Código Legacy Preservado

Todo el código anterior fue comentado (NO eliminado) para permitir rollback si es necesario.

### Ubicación del Código Legacy

1. **Agendamiento completo**: `chatbot_logic.py` líneas ~700-1100
2. **Disponibilidad y servicios**: `chatbot_logic.py` líneas ~288-387
3. **Consultas PostgreSQL**: `chatbot_logic.py` líneas ~387-420
4. **Reagendamiento legacy**: `chatbot_logic.py` líneas ~1100-1400

### Marcadores de Código Legacy

Todos los bloques comentados tienen encabezados como:
```python
# ============================================================================
# === LÓGICA DE AGENDAMIENTO DESACTIVADA ===
# Fecha de congelación: 28/02/2026
# Motivo: Migración a sistema de agendamiento externo
# IMPORTANTE: NO ELIMINAR ESTE CÓDIGO
# ============================================================================
```

## Instrucciones de Rollback

Si se necesita volver al sistema anterior:

### 1. Reactivar Agendamiento Interno

En `chatbot_logic.py`, método `handle_menu()`:

```python
# Reemplazar:
if "1" in mensaje or "agendar" in mensaje:
    self.update_conversation(telefono, self.ESTADO_MENU, {})
    return """Para agendar tu cita, por favor usa nuestro sistema..."""

# Por:
if "1" in mensaje or "agendar" in mensaje:
    paciente = self.db.query(Paciente).filter(Paciente.telefono == telefono).first()
    if paciente and paciente.nombre:
        return self.show_servicios(telefono)
    else:
        self.update_conversation(telefono, self.ESTADO_AGENDAR_NOMBRE, {})
        return "Perfecto, vamos a agendar tu cita..."
```

### 2. Descomentar Métodos Legacy

Descomentar todos los bloques marcados con:
- `=== LÓGICA DE AGENDAMIENTO DESACTIVADA ===`
- `=== MÉTODOS LEGACY DE DISPONIBILIDAD Y SERVICIOS ===`
- `=== MÉTODOS LEGACY DE POSTGRESQL ===`
- `=== MÉTODOS LEGACY DE REAGENDAMIENTO ===`

### 3. Revertir Reagendamiento, Cancelación y Consulta

Reemplazar los métodos actuales que usan Google Sheets por las versiones comentadas que usan PostgreSQL.

### 4. Remover Dependencias de Google Sheets

```bash
pip uninstall google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 5. Eliminar Archivo

```bash
rm google_sheets_client.py
```

## Testing

### Pruebas Recomendadas

1. **Agendamiento**
   - Verificar que el enlace se envía correctamente
   - Confirmar que el usuario puede acceder al sistema externo

2. **Reagendamiento**
   - Probar con diferentes formatos de fecha/hora
   - Verificar actualización en Google Sheets
   - Confirmar validaciones de horario

3. **Cancelación**
   - Verificar que marca como "cancelada" (no elimina)
   - Confirmar que la fila permanece en el Sheet

4. **Consulta**
   - Verificar que muestra solo citas activas
   - Confirmar formato de visualización

### Comandos de Testing

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
python test_chatbot.py

# Verificar conexión a Google Sheets
python -c "from google_sheets_client import get_sheets_client; client = get_sheets_client(); print(client.get_all_appointments())"
```

## Notas Importantes

1. **PostgreSQL sigue activo**: La base de datos PostgreSQL NO fue eliminada y sigue almacenando conversaciones y pacientes.

2. **Handoff a humano**: Esta funcionalidad NO fue modificada y sigue funcionando igual.

3. **Compatibilidad**: El sistema mantiene compatibilidad con el flujo de conversación existente.

4. **Seguridad**: Las credenciales de Google están en variables de entorno, NO en el código.

## Contacto y Soporte

Para preguntas sobre esta migración:
- Revisar este documento
- Consultar comentarios en el código
- Verificar logs del sistema

## Historial de Cambios

| Fecha | Cambio | Responsable |
|-------|--------|-------------|
| 28/02/2026 | Migración inicial completada | Equipo Dev |

---

**Última actualización:** 28 de febrero de 2026
