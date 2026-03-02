# Configuración de Google Sheets

**Fecha:** 28/02/2026  
**Propósito:** Reemplazar PostgreSQL completamente con Google Sheets

## Spreadsheet Requerido

**Spreadsheet ID:** `[TU_SPREADSHEET_ID]`

Este spreadsheet debe contener 3 hojas (sheets) con las siguientes estructuras:

---

## 1. Hoja "Citas"

**Propósito:** Almacenar todas las citas de los pacientes

### Estructura de Columnas (Fila 1 - Headers):

| A | B | C | D | E | F | G | H | I | J | K | L | M | N |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ID | Nombre | Correo | Teléfono | Fecha | Hora | Estado | Acción | Servicio | Hora fin | Duracion | Doctora | FechaCreación | FechaActualización |

### Descripción de Columnas:

- **A - ID**: ID único de la cita (texto/número)
- **B - Nombre**: Nombre completo del paciente (texto)
- **C - Correo**: Email del paciente (texto)
- **D - Teléfono**: Número de teléfono del paciente (texto, ej: "3209855847")
- **E - Fecha**: Fecha de la cita en formato DD/MM/AAAA (texto, ej: "20/02/2026")
- **F - Hora**: Hora de inicio en formato H:MM (texto, ej: "8:00")
- **G - Estado**: Estado de la cita (texto: "Agendada", "Atendida", "Cancelada")
- **H - Acción**: Tipo de acción (texto, ej: "Agendamiento", "Reagendamiento")
- **I - Servicio**: Nombre completo del servicio (texto, ej: "Ortodoncia - Valoración de Ortodoncia")
- **J - Hora fin**: Hora de finalización (texto, ej: "8:30")
- **K - Duracion**: Duración en minutos (texto/número, ej: "30")
- **L - Doctora**: Nombre de la doctora (texto, ej: "Dra. Sandra Simancas")
- **M - FechaCreación**: Fecha/hora de creación ISO 8601 (texto, ej: "2026-02-13T21:16:25.359Z")
- **N - FechaActualización**: Fecha/hora de última actualización ISO 8601 (texto)

### Ejemplo de Datos:

```
1029400483 | Luis Zaida | zaida.mateus175@gmail.com | 3209855847 | 20/02/2026 | 8:00 | Atendida | Agendamiento | Ortodoncia - Valoración de Ortodoncia | 8:30 | 30 | Dra. Sandra Simancas | 2026-02-13T21:16:25.359Z | 2026-02-13T21:16:25.359Z
```

### Reglas Importantes:

- La fila 1 DEBE contener los headers exactamente como se muestra
- Las citas canceladas se marcan con estado "Cancelada" (NO se eliminan)
- Las citas atendidas tienen estado "Atendida"
- Las citas pendientes tienen estado "Agendada"
- El sistema lee desde la fila 2 en adelante
- El sistema filtra citas por teléfono (columna D)
- El sistema NO muestra citas con estado "Cancelada" o "Atendida" en consultas

---

## 2. Hoja "Conversaciones"

**Propósito:** Almacenar el estado de las conversaciones de cada usuario

### Estructura de Columnas (Fila 1 - Headers):

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| telefono | estado | contexto | modo_humano | fecha_modo_humano | ultima_interaccion |

### Descripción de Columnas:

- **A - telefono**: Número de teléfono del usuario (texto, único)
- **B - estado**: Estado actual de la conversación (texto, ej: "menu", "agendar_nombre", etc.)
- **C - contexto**: Datos temporales en formato JSON (texto)
- **D - modo_humano**: Indica si está en modo humano (texto: "true" o "false")
- **E - fecha_modo_humano**: Fecha/hora de activación del modo humano (texto ISO 8601)
- **F - ultima_interaccion**: Fecha/hora de última interacción (texto ISO 8601)

### Ejemplo de Datos:

```
5551234567 | menu | {} | false | | 2026-02-28T22:30:00.000Z
5559876543 | reagendar_seleccionar | {"cita_id":"2"} | false | | 2026-02-28T22:35:00.000Z
5551112222 | inicial | {} | true | 2026-02-28T22:40:00.000Z | 2026-02-28T22:40:00.000Z
```

### Reglas Importantes:

- La fila 1 DEBE contener los headers exactamente como se muestra
- El campo `contexto` debe ser un JSON válido (mínimo: `{}`)
- El campo `modo_humano` debe ser "true" o "false" (texto)
- Las fechas deben estar en formato ISO 8601

---

## 3. Hoja "Pacientes"

**Propósito:** Almacenar información básica de los pacientes

### Estructura de Columnas (Fila 1 - Headers):

| A | B | C | D | E |
|---|---|---|---|---|
| telefono | nombre | email | fecha_nacimiento | created_at |

### Descripción de Columnas:

- **A - telefono**: Número de teléfono del paciente (texto, único)
- **B - nombre**: Nombre completo del paciente (texto)
- **C - email**: Email del paciente (texto, opcional)
- **D - fecha_nacimiento**: Fecha de nacimiento (texto, opcional)
- **E - created_at**: Fecha/hora de creación (texto ISO 8601)

### Ejemplo de Datos:

```
5551234567 | Juan Pérez | juan@email.com | 15/05/1990 | 2026-02-28T20:00:00.000Z
5559876543 | María López | maria@email.com | | 2026-02-28T20:15:00.000Z
5551112222 | Carlos Ruiz | | | 2026-02-28T20:30:00.000Z
```

### Reglas Importantes:

- La fila 1 DEBE contener los headers exactamente como se muestra
- El teléfono es único (no puede haber duplicados)
- Los campos email y fecha_nacimiento son opcionales

---

## Pasos para Configurar

### 1. Crear las Hojas

En el spreadsheet `[TU_SPREADSHEET_ID]`:

1. ✅ Hoja "Citas" - YA EXISTE (no modificar estructura)
2. Crear hoja llamada exactamente "Conversaciones"
3. Crear hoja llamada exactamente "Pacientes"

### 2. Agregar Headers

**IMPORTANTE:** La hoja "Citas" ya tiene su estructura. NO la modifiques.

Solo necesitas agregar headers en:
- Hoja "Conversaciones" (nueva)
- Hoja "Pacientes" (nueva)

### 3. Permisos

Asegurarse de que la service account tenga permisos de edición:
- Email: `[TU_SERVICE_ACCOUNT_EMAIL]`
- Permisos: Editor

### 4. Verificar Configuración

Ejecutar este comando para verificar la conexión:

```bash
python -c "from google_sheets_client import get_sheets_client; client = get_sheets_client(); print('✅ Conexión exitosa')"
```

---

## Migración de Datos Existentes

Si tienes datos en PostgreSQL que quieres migrar:

### Citas

```sql
SELECT 
    id::text,
    (SELECT telefono FROM pacientes WHERE id = citas.paciente_id),
    (SELECT nombre FROM pacientes WHERE id = citas.paciente_id),
    (SELECT nombre FROM servicios WHERE id = citas.servicio_id),
    TO_CHAR(fecha_hora, 'DD/MM/YYYY'),
    TO_CHAR(fecha_hora, 'HH24:MI'),
    estado,
    notas
FROM citas
WHERE estado = 'agendada'
ORDER BY fecha_hora;
```

### Pacientes

```sql
SELECT 
    telefono,
    nombre,
    email,
    TO_CHAR(fecha_nacimiento, 'DD/MM/YYYY'),
    created_at::text
FROM pacientes
ORDER BY created_at;
```

Copia los resultados y pégalos en las hojas correspondientes.

---

## Troubleshooting

### Error: "Sheet not found"

- Verifica que las hojas se llamen exactamente: "Citas", "Conversaciones", "Pacientes"
- Los nombres son case-sensitive

### Error: "Permission denied"

- Verifica que la service account tenga permisos de Editor
- Comparte el spreadsheet con: `[TU_SERVICE_ACCOUNT_EMAIL]`

### Error: "Invalid JSON in contexto"

- El campo `contexto` debe ser un JSON válido
- Mínimo: `{}`
- Ejemplo válido: `{"cita_id":"123","fecha":"05/03/2026"}`

### Datos no se actualizan

- Verifica que los headers estén en la fila 1
- Verifica que no haya filas vacías entre los headers y los datos
- Refresca el spreadsheet

---

## Mantenimiento

### Limpieza de Conversaciones Antiguas

Puedes eliminar conversaciones de más de 30 días para mantener el sheet limpio:

1. Filtrar por `ultima_interaccion` < hace 30 días
2. Eliminar esas filas

### Backup

Recomendado hacer backup del spreadsheet semanalmente:

1. Archivo → Hacer una copia
2. Nombrar con fecha: "Backup_YYYY-MM-DD"

---

**Última actualización:** 28 de febrero de 2026
