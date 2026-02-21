# Chatbot Clínica Odontológica - WhatsApp

Sistema completo de gestión de citas odontológicas vía WhatsApp usando FastAPI, PostgreSQL y Evolution API.

## 📋 Requisitos Previos

- Python 3.8 o superior
- PostgreSQL (ya desplegado)
- Evolution API (ya desplegado)
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
```

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

### 1. Agendar Cita

**Usuario nuevo:**
1. Bot: Solicita nombre completo
2. Bot: Muestra catálogo de servicios (17 servicios en 9 categorías)
3. Usuario: Selecciona servicio por número
4. Bot: Solicita fecha (DD/MM/AAAA)
5. Bot: Muestra horarios disponibles según duración del servicio
6. Usuario: Selecciona hora
7. Bot: Muestra resumen con doctor asignado automáticamente
8. Bot: Solicita confirmación
9. Bot: Confirma cita agendada con todos los detalles

**Usuario recurrente:**
1. Bot: Muestra catálogo de servicios
2. Usuario: Selecciona servicio
3. Bot: Solicita fecha
4. Bot: Muestra horarios disponibles
5. Usuario: Selecciona hora
6. Bot: Muestra resumen con doctor asignado
7. Bot: Solicita confirmación
8. Bot: Confirma cita agendada

**Validaciones:**
- Fecha debe ser futura
- Solo días laborales (Lunes a Viernes)
- Horario: 8:00 - 17:00
- Hora de almuerzo bloqueada: 12:00 - 13:00
- Citas cada 30 minutos
- Verifica disponibilidad de al menos 1 de los 3 doctores
- Respeta duración del servicio (30 o 60 minutos)
- No permite solapamiento de citas del mismo doctor

**Casos edge:**
- Horario no disponible: Muestra otros horarios disponibles
- Sin horarios ese día: Solicita otra fecha
- Fecha inválida: Explica formato correcto
- Todos los doctores ocupados: Muestra siguiente horario disponible
- Servicio de 60 min cerca del cierre: Solo muestra horarios válidos
- Horario ocupado al confirmar: Notifica y vuelve al menú

### 2. Reagendar Cita

1. Bot: Muestra lista de citas agendadas con doctor y servicio
2. Usuario: Selecciona número de cita
3. Bot: Pregunta si desea cambiar el servicio
4. Usuario: Mantiene o cambia servicio
5. Bot: Solicita nueva fecha
6. Bot: Muestra horarios disponibles según duración
7. Usuario: Selecciona hora
8. Bot: Muestra comparación (cita actual vs nueva) con nuevo doctor
9. Bot: Solicita confirmación
10. Bot: Confirma reagendamiento

**Validaciones:**
- Mismas validaciones que agendar
- Verifica que la cita exista
- Verifica que sea cita futura
- Asigna doctor disponible para nuevo horario

**Casos edge:**
- Sin citas para reagendar: Vuelve al menú
- Número de cita inválido: Solicita número válido
- Horario no disponible: Muestra alternativas
- Cambio de servicio a uno más largo: Verifica disponibilidad

### 3. Cancelar Cita

1. Bot: Muestra lista de citas agendadas
2. Usuario: Selecciona número de cita
3. Bot: Muestra cita completa y solicita confirmación
4. Bot: Confirma cancelación

**Validaciones:**
- Verifica que la cita exista
- Solo citas futuras

**Casos edge:**
- Sin citas para cancelar: Vuelve al menú
- Número inválido: Solicita número válido
- Usuario dice NO: Mantiene cita activa

### 4. Consultar Citas

1. Bot: Muestra todas las citas agendadas del paciente con doctor y servicio
2. Bot: Vuelve al menú principal

**Casos edge:**
- Sin citas: Ofrece agendar una

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

### Tabla: pacientes
- `id`: ID único
- `telefono`: Número de WhatsApp (único)
- `nombre`: Nombre completo
- `email`: Email (opcional)
- `fecha_nacimiento`: Fecha de nacimiento (opcional)
- `created_at`, `updated_at`: Timestamps

### Tabla: doctores
- `id`: ID único
- `nombre`: Nombre del doctor
- `especialidad`: Especialidad médica
- `activo`: Estado (activo/inactivo)
- `created_at`, `updated_at`: Timestamps

**Doctores precargados:**
1. Dr. Juan Pérez - Ortodoncia
2. Dra. María González - Odontología General
3. Dr. Carlos Rodríguez - Cirugía Maxilofacial

### Tabla: servicios
- `id`: ID único
- `categoria`: Categoría del servicio
- `nombre`: Nombre del servicio
- `duracion_minutos`: Duración (30 o 60 minutos)
- `descripcion`: Descripción (opcional)
- `activo`: Estado (activo/inactivo)
- `created_at`, `updated_at`: Timestamps

**Catálogo de servicios precargado (17 servicios):**

1. **Ortodoncia**
   - Valoración de Ortodoncia (30 min)
   - Control de Ortodoncia (30 min)
   - Montaje de Brackets (60 min)

2. **Ortopedia Maxilar**
   - Valoración de Ortopedia (30 min)
   - Procedimiento de Ortopedia (60 min)

3. **Odontología General**
   - Valoración General (30 min)
   - Procedimiento General (60 min)

4. **Odontología Estética**
   - Valoración Estética (30 min)
   - Procedimiento Estético (60 min)

5. **Blanqueamiento**
   - Blanqueamiento Dental (30 min)

6. **Diseño de Sonrisa**
   - Valoración de Diseño de Sonrisa (30 min)
   - Diseño de Sonrisa (60 min)

7. **Rehabilitación Oral**
   - Valoración de Rehabilitación (30 min)
   - Procedimiento de Rehabilitación (60 min)

8. **Periodoncia**
   - Valoración de Periodoncia (30 min)
   - Procedimiento de Periodoncia (60 min)

9. **Profilaxis**
   - Profilaxis Dental (30 min)

### Tabla: citas
- `id`: ID único
- `paciente_id`: Referencia a paciente
- `doctor_id`: Referencia a doctor
- `servicio_id`: Referencia a servicio
- `fecha_hora`: Fecha y hora de la cita
- `estado`: agendada, cancelada, completada, reagendada
- `notas`: Notas adicionales
- `created_at`, `updated_at`: Timestamps
- **Constraint único:** (doctor_id, fecha_hora) - Un doctor no puede tener dos citas al mismo tiempo

### Tabla: conversaciones
- `id`: ID único
- `telefono`: Número de WhatsApp (único)
- `estado`: Estado actual de la conversación
- `contexto`: Datos temporales en JSON
- `ultima_interaccion`: Timestamp de última interacción
- `created_at`: Timestamp de creación

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
- Las citas son cada 30 minutos
- **3 doctores disponibles** que atienden simultáneamente
- El sistema asigna automáticamente el doctor disponible
- El sistema previene solapamiento de citas del mismo doctor
- **17 servicios** en 9 categorías con duraciones de 30 o 60 minutos
- Los servicios de 60 minutos requieren 2 slots consecutivos disponibles

## 🔐 Seguridad

- Nunca subas el archivo `.env` a repositorios públicos
- Usa variables de entorno en producción
- Considera agregar autenticación al webhook si es público
- Usa HTTPS en producción

## 📞 Soporte

Para problemas o preguntas, revisa los logs del servidor y de Evolution API.
