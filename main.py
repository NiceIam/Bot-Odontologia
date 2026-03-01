from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
# === POSTGRESQL COMPLETAMENTE DESACTIVADO ===
# Fecha: 28/02/2026
# from sqlalchemy.orm import Session
# from database import get_db, engine, Base
from chatbot_logic import ChatbotLogic
from evolution_client import evolution_client
from config import get_settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# === POSTGRESQL DESACTIVADO ===
# Ya no intentamos conectar a PostgreSQL
# Todo se maneja en Google Sheets
logger.info("✅ Sistema configurado para usar Google Sheets (sin PostgreSQL)")

app = FastAPI(
    title="Chatbot Clínica Odontológica",
    description="Sistema de gestión de citas vía WhatsApp",
    version="2.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Aplicación iniciada correctamente")
    logger.info(f"📊 Configuración:")
    logger.info(f"   - Google Sheets: Activo")
    logger.info(f"   - PostgreSQL: Desactivado")
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
    return {
        "status": "healthy",
        "database": "Google Sheets (PostgreSQL desactivado)",
        "evolution_api": settings.evolution_api_url
    }

@app.post("/webhook")
async def webhook(request: Request):
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
        
        # Ignorar mensajes vacíos o muy cortos (posibles eventos duplicados)
        if not mensaje or len(mensaje.strip()) == 0:
            logger.warning("Mensaje vacío recibido, ignorando")
            return {"status": "ignored", "reason": "empty message"}
        
        # Limpiar el mensaje
        mensaje = mensaje.strip()
        
        # Verificar si es un mensaje propio (fromMe)
        is_from_me = key.get("fromMe", False)
        
        # Si es mensaje propio, solo procesar si es para reactivar el bot
        if is_from_me:
            logger.info(f"Mensaje propio detectado de {telefono}: {mensaje}")
            
            # Crear instancia del chatbot para verificar modo humano
            chatbot = ChatbotLogic()
            
            # Verificar si hay modo humano activo
            if chatbot.is_human_mode_active(telefono):
                logger.info(f"Modo humano activo para {telefono}, verificando frase de reactivación")
                
                # Verificar si es una frase de reactivación
                if chatbot.detect_bot_reactivation(mensaje):
                    logger.info(f"Frase de reactivación detectada: '{mensaje}'")
                    chatbot.deactivate_human_mode(telefono)
                    
                    # Enviar mensaje de confirmación
                    await evolution_client.send_message(
                        telefono,
                        "Bot reactivado. Escribe 'hola' para ver el menú de opciones."
                    )
                    
                    return {
                        "status": "success",
                        "phone": telefono,
                        "action": "bot_reactivated_by_human",
                        "message": mensaje
                    }
                else:
                    logger.info(f"Mensaje propio sin frase de reactivación, ignorando")
                    return {"status": "ignored", "reason": "message from human, no reactivation phrase"}
            else:
                logger.info("No hay modo humano activo, ignorando mensaje propio")
                return {"status": "ignored", "reason": "message from bot, no human mode"}
        
        logger.info(f"Procesando mensaje de {telefono}: {mensaje}")
        
        # Procesar mensaje con la lógica del chatbot (SIN PostgreSQL)
        chatbot = ChatbotLogic()
        respuesta = chatbot.process_message(telefono, mensaje)
        
        # Manejar señales especiales
        if respuesta == "handoff_to_human":
            # Activar modo humano
            chatbot.activate_human_mode(telefono)
            
            # Enviar mensaje al paciente
            await evolution_client.send_message(
                telefono,
                "Un momento por favor, te estamos conectando con un profesional. En breve alguien continuará la conversación contigo."
            )
            
            # Enviar webhook de notificación
            paciente = chatbot.get_or_create_patient(telefono)
            await chatbot.send_human_handoff_webhook(
                telefono,
                mensaje,
                paciente['nombre'] if paciente else None
            )
            
            logger.info(f"Handoff a humano activado para {telefono}")
            
            return {
                "status": "success",
                "phone": telefono,
                "action": "handoff_to_human",
                "message_received": mensaje
            }
        
        elif respuesta == "human_mode_active":
            # No responder, el humano está atendiendo
            logger.info(f"Modo humano activo para {telefono}, mensaje registrado pero no respondido")
            
            return {
                "status": "success",
                "phone": telefono,
                "action": "human_mode_active",
                "message_received": mensaje,
                "response_sent": False
            }
        
        elif respuesta == "bot_reactivated":
            # Bot reactivado
            await evolution_client.send_message(
                telefono,
                "Bot reactivado. Escribe 'hola' para ver el menú de opciones."
            )
            
            logger.info(f"Bot reactivado para {telefono}")
            
            return {
                "status": "success",
                "phone": telefono,
                "action": "bot_reactivated",
                "message_received": mensaje
            }
        
        else:
            # Respuesta normal del bot
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
async def get_appointments(phone: str):
    """
    Endpoint para consultar citas de un paciente (útil para testing)
    """
    try:
        chatbot = ChatbotLogic()
        sheets_client = chatbot.sheets_client
        citas = sheets_client.get_appointments_by_phone(phone)
        
        return {
            "phone": phone,
            "appointments": citas
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
