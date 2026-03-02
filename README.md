# Chatbot Clínica Odontológica - WhatsApp

Sistema completo de gestión de citas odontológicas vía WhatsApp usando FastAPI, PostgreSQL, Google Sheets y Evolution API.

## ⚠️ IMPORTANTE - Migración Reciente (28/02/2026)

El sistema ha sido migrado parcialmente:
- **Agendamiento:** Ahora redirige a sistema externo
- **Reagendamiento, Cancelación, Consulta:** Migrados a Google Sheets
- **Código legacy:** Preservado y comentado para posible rollback

📖 **Ver documentación completa de migración:**
- `CAMBIOS_REALIZADOS.md` - Resumen ejecutivo
- `MIGRATION_GUIDE.md` - Guía completa con instrucciones de rollback
- `CHECKLIST_DEPLOYMENT.md` - Checklist de deployment

## 📋 Requisitos Previos

- Python 3.8 o superior
- PostgreSQL (para conversaciones y pacientes)
- Google Sheets (para citas)
- Evolution API (ya desplegado)
- Cuenta de servicio de Google Cloud con acceso a Sheets API
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd chatbot-clinica-dental
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y completa con tus credenciales:

```bash
copy .env.example .env
```

Edita el archivo `.env` con tus datos:

```env
# PostgreSQL - Reemplaza con tus credenciales
DATABASE_URL=postgresql://tu_usuario:tu_password@tu_host:5432/tu_base_datos

# Evolution API - Reemplaza con tus credenciales
EVOLUTION_API_URL=http://tu-servidor:8080
EVOLUTION_API_KEY=tu_api_key_aqui
EVOLUTION_INSTANCE_NAME=nombre_de_tu_instancia

# FastAPI
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Clínica
CLINIC_NAME=Clínica Dental Sonrisa
CLINIC_PHONE=+1234567890

# Google Sheets (NUEVO - Requerido)
SPREADSHEET_ID=[TU_SPREADSHEET_ID]
SHEET_NAME=Citas
CALENDAR_ID=primary
GOOGLE_CREDENTIALS={"type":"service_account","project_id":"[TU_PROJECT_ID]",...}
```

**Nota:** Las credenciales de Google deben ser un JSON completo de service account.

### 5. Crear el schema en PostgreSQL

Ejecuta el archivo `schema.sql` en tu base de datos PostgreSQL:

```bash
# Opción 1: Usando psql
psql -h tu_host -U tu_usuario -d tu_base_datos -f schema.sql

# Opción 2: Copiar y pegar el contenido en tu cliente SQL favorito (pgAdmin, DBeaver, etc.)
```

## ▶️ Ejecutar el Proyecto

### Modo desarrollo (con auto-reload)

```bash
python main.py
```

O usando uvicorn directamente:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Modo producción

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

El servidor estará disponible en: `http://localhost:8000`

## 🔧 Configurar Evolution API

### 1. Configurar el webhook en Evolution API

Tu servidor FastAPI expone el endpoint `/webhook` que debe ser configurado en Evolution API.

**URL del webhook:** `http://tu-servidor-fastapi:8000/webhook`

Configura el webhook usando este comando:

```bash
curl -X POST "http://tu-evolution-api:8080/webhook/set/tu_instancia" \
  -H "apikey: tu_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://tu-servidor-fastapi:8000/webhook",
    "webhook_by_events": true,
    "events": ["messages.upsert"]
  }'
```

Ver `WEBHOOK_SETUP.md` para instrucciones detalladas y troubleshooting.

### 2. Verificar que Evolution API esté conectado

Asegúrate de que tu instancia de Evolution API esté conectada a WhatsApp y funcionando correctamente.

## 📱 Flujos de Conversación

### 1. Agendar Cita (NUEVO FLUJO - Migrado 28/02/2026)

**Flujo actual:**
1. Usuario: Selecciona opción 1 (Agendar)
2. Bot: Envía enlace al sistema externo de agendamiento
3. Usuario: Accede a https://XXXXXXXXXXXXront.dtbfmw.XXXXXXXX.host/
4. Usuario: Completa agendamiento en sistema externo

**Nota:** El flujo interno de agendamiento fue desactivado pero preservado en el código (comentado) para posible reactivación futura.

### 2. Reagendar Cita (MIGRADO A GOOGLE SHEETS)

### 2. Reagendar Cita (MIGRADO A GOOGLE SHEETS)

1. Bot: Muestra lista de citas agendadas desde Google Sheets
2. Usuario: Selecciona número de cita
3. Bot: Solicita nueva fecha y hora (formato: DD/MM/AAAA HH:MM)
4. Usuario: Ingresa nueva fecha/hora
5. Bot: Muestra resumen del cambio
6. Bot: Solicita confirmación
7. Bot: Actualiza en Google Sheets y confirma

**Validaciones:**
- Fecha debe ser futura
- Solo días laborales (Lunes a Viernes)
- Horario: 8:00 - 17:00
- Hora de almuerzo bloqueada: 12:00 - 13:00

**Fuente de datos:** Google Sheets (NO PostgreSQL)

### 3. Cancelar Cita (MIGRADO A GOOGLE SHEETS)

1. Bot: Muestra lista de citas agendadas desde Google Sheets
2. Usuario: Selecciona número de cita
3. Bot: Muestra cita completa y solicita confirmación
4. Bot: Marca como "cancelada" en Google Sheets (NO elimina la fila)

**Fuente de datos:** Google Sheets (NO PostgreSQL)

### 4. Consultar Citas (MIGRADO A GOOGLE SHEETS)

1. Bot: Muestra todas las citas agendadas del paciente desde Google Sheets
2. Bot: Vuelve al menú principal

**Fuente de datos:** Google Sheets (NO PostgreSQL)

### 5. Hablar con Profesional (SIN CAMBIOS)

Funciona igual que antes - activa handoff a humano.

## 🧪 Testing

### Verificar que el servidor está funcionando

```bash
curl http://localhost:8000/health
```

### Probar el chatbot sin WhatsApp

Usa el script de prueba incluido:

```bash
# Simular una conversación completa
python test_chatbot.py test

# Listar todas las citas agendadas
python test_chatbot.py citas

# Ver catálogo de servicios
python test_chatbot.py servicios

# Ver doctores disponibles
python test_chatbot.py doctores

# Ver disponibilidad para una fecha
python test_chatbot.py disponibilidad
```

### Enviar mensaje de prueba vía API

```bash
curl -X POST "http://localhost:8000/send-message?phone=5511999999999&message=Hola"
```

### Consultar citas de un paciente

```bash
curl http://localhost:8000/appointments/5511999999999
```

### Probar el webhook manualmente

```bash
curl -X POST "http://localhost:8000/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "clinica-dental",
    "data": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": false,
        "id": "test123"
      },
      "message": {
        "conversation": "Hola"
      },
      "messageTimestamp": "1234567890",
      "pushName": "Test User"
    }
  }'
```

## 📊 Estructura de la Base de Datos

### PostgreSQL (Conversaciones y Pacientes)

#### Tabla: pacientes
- `id`: ID único
- `telefono`: Número de WhatsApp (único)
- `nombre`: Nombre completo
- `email`: Email (opcional)
- `fecha_nacimiento`: Fecha de nacimiento (opcional)
- `created_at`, `updated_at`: Timestamps

#### Tabla: conversaciones
- `id`: ID único
- `telefono`: Número de WhatsApp (único)
- `estado`: Estado actual de la conversación
- `contexto`: Datos temporales en JSON
- `modo_humano`: Indica si está en modo humano
- `fecha_modo_humano`: Timestamp de activación de modo humano
- `ultima_interaccion`: Timestamp de última interacción
- `created_at`: Timestamp de creación

**Nota:** Las tablas `doctores`, `servicios` y `citas` siguen existiendo en PostgreSQL pero ya NO se usan para operaciones de citas. Se mantienen para posible rollback.

### Google Sheets (Citas - NUEVA FUENTE DE DATOS)

**Spreadsheet ID:** `[TU_SPREADSHEET_ID]`  
**Sheet Name:** `Citas`

#### Estructura de columnas:

| Columna | Nombre | Descripción |
|---------|--------|-------------|
| A | id | ID único de la cita |
| B | telefono | Número de teléfono del paciente |
| C | nombre | Nombre del paciente |
| D | servicio | Nombre del servicio |
| E | fecha | Fecha de la cita (DD/MM/AAAA) |
| F | hora | Hora de la cita (HH:MM) |
| G | estado | Estado: agendada, cancelada |
| H | notas | Notas adicionales (opcional) |

**Ejemplo de datos:**
```
1 | 5551234567 | Juan Pérez | Limpieza | 05/03/2026 | 14:30 | agendada | 
2 | 5559876543 | María López | Ortodoncia | 06/03/2026 | 10:00 | agendada |
```

**Importante:**
- La fila 1 debe contener los headers
- Las citas canceladas se marcan con estado "cancelada" (NO se eliminan)
- El sistema lee y escribe directamente en este Sheet

## 🔍 Logs y Debugging

Los logs se muestran en la consola. Para ver más detalles, puedes ajustar el nivel de logging en `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)  # Para más detalle
```

## 🛠️ Solución de Problemas

### Error de conexión a PostgreSQL
- Verifica que PostgreSQL esté corriendo
- Verifica las credenciales en `.env`
- Verifica que la base de datos exista

### Error de conexión a Evolution API
- Verifica que Evolution API esté corriendo
- Verifica la URL y API key en `.env`
- Verifica que la instancia esté conectada a WhatsApp

### Webhook no recibe mensajes
- Verifica que el webhook esté configurado en Evolution API
- Verifica que tu servidor FastAPI sea accesible desde Evolution API
- Revisa los logs de ambos servicios

### Mensajes no se envían
- Verifica que el nombre de la instancia sea correcto
- Verifica que la instancia esté conectada
- Revisa los logs de Evolution API

## 📝 Notas Adicionales

- El bot mantiene el estado de conversación por número de teléfono
- Las conversaciones se reinician automáticamente después de cada flujo
- **Horarios de atención:** Lunes a Viernes, 8:00 - 17:00
- **Hora de almuerzo:** 12:00 - 13:00 (bloqueada para citas)
- **Agendamiento:** Redirige a sistema externo ([URL_SISTEMA_EXTERNO])
- **Citas:** Almacenadas en Google Sheets (NO en PostgreSQL)
- **Conversaciones y Pacientes:** Siguen en PostgreSQL
- **Código legacy:** Preservado y comentado para posible rollback

## 🔄 Migración y Rollback

### Archivos de Documentación
- `CAMBIOS_REALIZADOS.md` - Resumen ejecutivo de cambios
- `MIGRATION_GUIDE.md` - Guía completa con instrucciones de rollback
- `CHECKLIST_DEPLOYMENT.md` - Checklist de deployment

### Código Legacy
Todo el código anterior fue comentado (NO eliminado) en `chatbot_logic.py`:
- Lógica de agendamiento interno (~líneas 700-1100)
- Métodos de disponibilidad y servicios (~líneas 288-387)
- Consultas PostgreSQL de citas (~líneas 387-420)

### Reactivar Sistema Anterior
Ver `MIGRATION_GUIDE.md` sección "Instrucciones de Rollback" para pasos detallados.

## 🔐 Seguridad

- Nunca subas el archivo `.env` a repositorios públicos
- Usa variables de entorno en producción
- Considera agregar autenticación al webhook si es público
- Usa HTTPS en producción

## 📞 Soporte

Para problemas o preguntas, revisa los logs del servidor y de Evolution API.
