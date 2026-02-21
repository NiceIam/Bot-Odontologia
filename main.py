from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from chatbot_logic import ChatbotLogic
from evolution_client import evolution_client
from config import get_settings
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Intentar conectar a la base de datos con reintentos
max_retries = 5
retry_delay = 2

for attempt in range(max_retries):
    try:
        logger.info(f"Intentando conectar a la base de datos (intento {attempt + 1}/{max_retries})...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Conexión a base de datos exitosa")
        break
    except Exception as e:
        logger.error(f"❌ Error conectando a base de datos: {str(e)}")
        if attempt < max_retries - 1:
            logger.info(f"Reintentando en {retry_delay} segundos...")
            time.sleep(retry_delay)
        else:
            logger.error("❌ No se pudo conectar a la base de datos después de varios intentos")
            # Continuar de todas formas para que el health check responda

app = FastAPI(
    title="Chatbot Clínica Odontológica",
    description="Sistema de gestión de citas vía WhatsApp",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Aplicación iniciada correctamente")
    logger.info(f"📊 Configuración:")
    logger.info(f"   - Database: {settings.database_url[:30]}...")
    logger.info(f"   - Evolution API: {settings.evolution_api_url}")
    logger.info(f"   - Instance: {settings.evolution_instance_name}")
    logger.info(f"   - Port: {settings.port}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.warning("⚠️ Aplicación cerrándose...")

@app.get("/")
async def root():
    """Endpoint de health check"""
    return {
        "status": "online",
        "service": "Chatbot Clínica Odontológica",
        "version": "1.0.0",
        "message": "API funcionando correctamente"
    }

@app.get("/health")
async def health_check():
    """Verifica el estado del servicio"""
    db_status = "unknown"
    try:
        # Verificar conexión a base de datos
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check DB error: {str(e)}")
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "evolution_api": settings.evolution_api_url
    }

@app.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint webhook para recibir mensajes de Evolution API
    """
    try:
        body = await request.json()
        logger.info(f"Webhook recibido: {body}")
        
        # Verificar que sea un mensaje entrante
        event = body.get("event")
        if event != "messages.upsert":
            logger.info(f"Evento ignorado: {event}")
            return {"status": "ignored", "reason": "not a message event"}
        
        data = body.get("data", {})
        key = data.get("key", {})
        
        # Ignorar mensajes enviados por nosotros
        if key.get("fromMe", False):
            logger.info("Mensaje propio ignorado")
            return {"status": "ignored", "reason": "message from bot"}
        
        # Extraer información del mensaje
        remote_jid = key.get("remoteJid", "")
        telefono = remote_jid.replace("@s.whatsapp.net", "")
        
        # Obtener el texto del mensaje
        message_obj = data.get("message", {})
        mensaje = (
            message_obj.get("conversation") or
            message_obj.get("extendedTextMessage", {}).get("text") or
            ""
        )
        
        if not mensaje:
            logger.warning("Mensaje sin texto recibido")
            return {"status": "ignored", "reason": "no text content"}
        
        logger.info(f"Procesando mensaje de {telefono}: {mensaje}")
        
        # Procesar mensaje con la lógica del chatbot
        chatbot = ChatbotLogic(db)
        
        # Verificar si necesita enviar servicios primero
        conv = chatbot.get_or_create_conversation(telefono)
        mensaje_lower = mensaje.strip().lower()
        
        # Si está en estado AGENDAR_NOMBRE y da un nombre válido, enviar servicios primero
        if conv.estado == "agendar_nombre" and len(mensaje.strip()) >= 3:
            # Enviar lista de servicios
            categorias = chatbot.get_servicios_por_categoria()
            mensaje_servicios = "📋 Servicios disponibles:\n\n"
            contador = 1
            
            for categoria, servicios in categorias.items():
                for servicio in servicios:
                    mensaje_servicios += f"{contador}. {servicio.nombre}\n"
                    contador += 1
            
            await evolution_client.send_message(telefono, mensaje_servicios)
            import asyncio
            await asyncio.sleep(0.5)  # Pequeña pausa entre mensajes
        
        # Procesar el mensaje normalmente
        respuesta = chatbot.process_message(telefono, mensaje)
        
        # Enviar respuesta a través de Evolution API
        await evolution_client.send_message(telefono, respuesta)
        
        logger.info(f"Respuesta enviada a {telefono}")
        
        return {
            "status": "success",
            "phone": telefono,
            "message_received": mensaje,
            "response_sent": True
        }
    
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-message")
async def send_message(phone: str, message: str):
    """
    Endpoint para enviar mensajes manualmente (útil para testing)
    """
    try:
        result = await evolution_client.send_message(phone, message)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error enviando mensaje: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/appointments/{phone}")
async def get_appointments(phone: str, db: Session = Depends(get_db)):
    """
    Endpoint para consultar citas de un paciente (útil para testing)
    """
    try:
        chatbot = ChatbotLogic(db)
        citas = chatbot.get_patient_appointments(phone)
        
        return {
            "phone": phone,
            "appointments": [
                {
                    "id": cita.id,
                    "fecha_hora": cita.fecha_hora.isoformat(),
                    "motivo": cita.motivo,
                    "estado": cita.estado
                }
                for cita in citas
            ]
        }
    except Exception as e:
        logger.error(f"Error consultando citas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
