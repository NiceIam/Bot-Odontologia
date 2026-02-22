# Sistema de Handoff a Atención Humana

## Resumen
Sistema completo para transferir conversaciones del chatbot a atención humana y viceversa.

## 1. Configuración de Base de Datos

Ejecuta el archivo `ADD_HUMAN_MODE.sql` para agregar los campos necesarios:
```sql
ALTER TABLE conversaciones ADD COLUMN IF NOT EXISTS modo_humano BOOLEAN DEFAULT false;
ALTER TABLE conversaciones ADD COLUMN IF NOT EXISTS fecha_modo_humano TIMESTAMP;
```

## 2. Activación del Modo Humano

### Opción A: Desde el menú principal
El usuario selecciona la opción **5️⃣ Hablar con un profesional**

### Opción B: Detección automática por palabras clave
El sistema detecta automáticamente cuando el usuario quiere hablar con una persona, incluso en medio de cualquier flujo.

**Palabras y frases detectadas:**
- "hablar con alguien", "hablar con una persona", "hablar con un humano"
- "persona real", "asesor", "operador", "recepción"
- "tengo una duda", "tengo dudas", "una pregunta"
- "necesito ayuda", "ayuda humana"
- "soporte", "atención", "asistencia"
- "no quiero bot", "no bot", "quiero persona"
- "me puedes pasar", "pásame con"
- Y muchas más variaciones...

## 3. Flujo cuando se activa

1. **Mensaje al paciente:**
   ```
   Un momento por favor, te estamos conectando con un profesional. 
   En breve alguien continuará la conversación contigo.
   ```

2. **Webhook enviado a n8n:**
   - URL: `https://n8n-n8n.dtbfmw.easypanel.host/webhook-test/bfaba3be-b713-49ff-812e-5a9cb27cf128`
   - Payload:
     ```json
     {
       "telefono": "573118563308",
       "nombre": "John Doe",
       "ultimo_mensaje": "quiero hablar con alguien",
       "fecha_hora": "2026-02-21T20:30:00",
       "estado_conversacion": "agendar_fecha",
       "contexto": {...},
       "tipo_evento": "solicitud_atencion_humana"
     }
     ```

3. **Bot pausado:**
   - El chatbot NO responde automáticamente
   - Solo registra los mensajes
   - El humano puede responder usando el mismo WhatsApp

## 4. Reactivación del Bot

El encargado humano puede reactivar el bot escribiendo cualquiera de estas frases:

- "te dejo con el bot"
- "el bot continuará"
- "seguimos con el asistente"
- "continúa con el bot"
- "vuelve al bot"
- "bot activo"
- "activar bot"

Cuando se detecta, el bot:
1. Se reactiva automáticamente
2. Envía: "Bot reactivado. Escribe 'hola' para ver el menú de opciones."
3. Vuelve al flujo normal

## 5. Estados del Sistema

### Modo Bot Activo (normal)
- `modo_humano = false`
- Bot responde automáticamente
- Detecta intención de handoff en cualquier momento

### Modo Humano Activo
- `modo_humano = true`
- Bot NO responde
- Humano atiende la conversación
- Bot solo registra mensajes

### Transición Bot → Humano
1. Detección de intención o selección de opción 5
2. Activar `modo_humano = true`
3. Enviar mensaje al paciente
4. Enviar webhook a n8n
5. Bot en pausa

### Transición Humano → Bot
1. Encargado escribe frase de reactivación
2. Desactivar `modo_humano = false`
3. Cambiar estado a `menu`
4. Enviar mensaje de confirmación
5. Bot activo nuevamente

## 6. Consultas SQL Útiles

### Ver conversaciones en modo humano
```sql
SELECT telefono, estado, modo_humano, fecha_modo_humano 
FROM conversaciones 
WHERE modo_humano = 'true';
```

### Reactivar bot manualmente para un usuario
```sql
UPDATE conversaciones 
SET modo_humano = 'false', estado = 'menu' 
WHERE telefono = '573118563308';
```

### Ver historial de handoffs
```sql
SELECT telefono, fecha_modo_humano, estado 
FROM conversaciones 
WHERE fecha_modo_humano IS NOT NULL 
ORDER BY fecha_modo_humano DESC;
```

## 7. Testing

### Probar handoff desde menú:
1. Escribe "hola"
2. Escribe "5"
3. Verifica que recibas el mensaje de conexión
4. Verifica que el webhook se envíe a n8n

### Probar detección automática:
1. En cualquier punto del flujo escribe "tengo una duda"
2. Verifica que se active el handoff inmediatamente

### Probar reactivación:
1. Desde el número del encargado escribe "te dejo con el bot"
2. Verifica que el bot se reactive
3. Escribe "hola" y verifica que muestre el menú

## 8. Logs Importantes

Los logs mostrarán:
- `Handoff a humano activado para {telefono}`
- `Modo humano activo para {telefono}, mensaje registrado pero no respondido`
- `Bot reactivado para {telefono}`
- `Webhook enviado: {status_code}`

## 9. Troubleshooting

**El bot no detecta la intención:**
- Verifica que la frase esté en la lista de keywords
- Revisa los logs para ver qué mensaje recibió

**El webhook no llega a n8n:**
- Verifica la URL del webhook
- Revisa los logs: "Webhook enviado: {status_code}"
- Verifica que n8n esté activo

**El bot no se reactiva:**
- Verifica que la frase de reactivación esté correcta
- Ejecuta manualmente la query SQL de reactivación

**El bot sigue respondiendo en modo humano:**
- Verifica en la BD: `SELECT modo_humano FROM conversaciones WHERE telefono = '...'`
- Debe ser 'true' para que el bot esté pausado
