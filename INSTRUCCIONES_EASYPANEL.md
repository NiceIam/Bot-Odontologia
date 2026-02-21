# Desplegar en Easypanel

## 📦 Pasos para Desplegar

### 1. Preparar el Proyecto

Asegúrate de tener todos estos archivos:
- ✅ Dockerfile
- ✅ requirements.txt
- ✅ main.py
- ✅ chatbot_logic.py
- ✅ database.py
- ✅ evolution_client.py
- ✅ config.py
- ✅ .dockerignore

### 2. Subir a GitHub (Recomendado)

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tu-usuario/chatbot-clinica.git
git push -u origin main
```

### 3. Crear Aplicación en Easypanel

1. Ve a tu panel de Easypanel
2. Click en "Create" → "App"
3. Selecciona "From GitHub" (o sube el código directamente)
4. Configura:
   - **Name:** chatbot-clinica
   - **Port:** 8000
   - **Build Method:** Dockerfile

### 4. Configurar Variables de Entorno

En Easypanel, agrega estas variables de entorno:

```
DATABASE_URL=postgresql://postgres:Olinky2025@n8n_postgres_odontologia:5432/chatbot?sslmode=disable

EVOLUTION_API_URL=http://tu-evolution-api:8080
EVOLUTION_API_KEY=tu_api_key_aqui
EVOLUTION_INSTANCE_NAME=tu_instancia

HOST=0.0.0.0
PORT=8000
DEBUG=False

CLINIC_NAME=Clínica Dental Sonrisa
CLINIC_PHONE=+1234567890
```

**IMPORTANTE:** Reemplaza los valores de Evolution API con los reales.

### 5. Ejecutar el Schema SQL

Antes de iniciar la app, ejecuta el schema en PostgreSQL:

**Opción A: Desde tu máquina local**
```bash
psql "postgresql://postgres:Olinky2025@n8n_postgres_odontologia:5432/chatbot?sslmode=disable" -f schema.sql
```

**Opción B: Desde Easypanel Terminal**
1. Abre terminal en el contenedor de PostgreSQL
2. Copia el contenido de schema.sql
3. Ejecuta: `psql -U postgres -d chatbot`
4. Pega el contenido del schema

### 6. Desplegar

1. Click en "Deploy"
2. Espera a que se construya la imagen
3. La app estará disponible en: `https://chatbot-clinica-XXXXX.easypanel.host`

### 7. Verificar que Funciona

```bash
# Health check
curl https://chatbot-clinica-XXXXX.easypanel.host/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "database": "connected",
  "evolution_api": "http://..."
}
```

### 8. Configurar Webhook en Evolution API

Una vez desplegado, configura el webhook en Evolution API:

```bash
curl -X POST "http://TU_EVOLUTION_API:8080/webhook/set/TU_INSTANCIA" \
  -H "apikey: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://chatbot-clinica-XXXXX.easypanel.host/webhook",
    "webhook_by_events": true,
    "events": ["messages.upsert"]
  }'
```

### 9. Probar

Envía un mensaje de WhatsApp al número conectado a Evolution API:
```
Hola
```

El bot debería responder con el menú principal.

---

## 🔧 Troubleshooting

### Error de conexión a PostgreSQL
- Verifica que el host `n8n_postgres_odontologia` sea accesible desde el contenedor
- Si están en la misma red de Docker en Easypanel, debería funcionar
- Si no, usa la IP interna del contenedor de PostgreSQL

### Error "Module not found"
- Verifica que requirements.txt esté completo
- Reconstruye la imagen en Easypanel

### Webhook no recibe mensajes
- Verifica que la URL del webhook sea accesible públicamente
- Verifica que Evolution API pueda alcanzar tu dominio de Easypanel
- Revisa los logs en Easypanel

### Ver Logs
En Easypanel:
1. Ve a tu app "chatbot-clinica"
2. Click en "Logs"
3. Verás los logs en tiempo real

---

## ✅ Checklist Final

- [ ] Código subido a GitHub o Easypanel
- [ ] Variables de entorno configuradas
- [ ] Schema SQL ejecutado en PostgreSQL
- [ ] App desplegada en Easypanel
- [ ] Health check responde OK
- [ ] Webhook configurado en Evolution API
- [ ] Bot responde en WhatsApp

---

**¡Listo! Tu chatbot estará funcionando en producción** 🚀
