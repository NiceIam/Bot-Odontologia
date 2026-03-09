# Guía de Prueba Manual - Flujo de Reagendar

**Fecha:** 09/03/2026  
**Propósito:** Verificar que el flujo de reagendar funcione correctamente con los nuevos horarios por doctora

---

## Pre-requisitos

1. Tener el bot corriendo (`python main.py`)
2. Tener citas en el Google Sheet con doctoras asignadas
3. Conocer una cédula que tenga citas agendadas

---

## Flujo de Prueba Completo

### PASO 1: Iniciar Conversación

**Usuario escribe:** `hola`

**Bot debe responder:**
```
¡Hola! 👋 Bienvenido a Orthodonto.

¿En qué puedo ayudarte hoy?

1️⃣ Agendar una cita
2️⃣ Reagendar una cita
3️⃣ Cancelar una cita
4️⃣ Consultar mis citas
5️⃣ Hablar con un profesional

Por favor, responde con el número de la opción que deseas.
```

---

### PASO 2: Seleccionar Reagendar

**Usuario escribe:** `2`

**Bot debe responder:**
```
Por favor, ingresa tu número de cédula para buscar tus citas:
```

---

### PASO 3: Ingresar Cédula

**Usuario escribe:** `[CÉDULA_CON_CITAS]` (ejemplo: 1029400483)

**Bot debe responder:**
```
Encontré X cita(s) con la cédula [CÉDULA]:

1. 📅 [FECHA] a las [HORA]
   💼 Servicio: [SERVICIO]
   👩‍⚕️ Doctora: [DOCTORA]
   📝 Estado: [ESTADO]

¿Cuál cita deseas reagendar? Responde con el número.
```

**✅ VERIFICAR:**
- Que se muestren las citas correctamente
- Que aparezca el campo "Doctora" con el nombre correcto

---

### PASO 4: Seleccionar Cita

**Usuario escribe:** `1`

**Bot debe responder:**
```
Vas a reagendar esta cita:

📅 [FECHA] a las [HORA]
💼 Servicio: [SERVICIO]
👩‍⚕️ Doctora: [DOCTORA]
📝 Estado: [ESTADO]

📅 Selecciona una nueva fecha (próximos días disponibles):

1. Lunes 10/03/2026
2. Martes 11/03/2026
3. Miércoles 12/03/2026
4. Jueves 13/03/2026
5. Viernes 14/03/2026
6. Sábado 15/03/2026
7. Lunes 17/03/2026
8. Martes 18/03/2026

Responde con el número de la fecha que prefieres.
```

**✅ VERIFICAR:**
- Que se muestre el catálogo de 8 fechas
- Que solo aparezcan días laborables
- Que NO se pregunte por la doctora (ya está asignada)

---

### PASO 5: Seleccionar Fecha

#### Caso A: Doctora Sandra + Miércoles

**Usuario escribe:** `3` (Miércoles)

**Bot debe responder:**
```
Perfecto! Has seleccionado:
📅 Miércoles 12/03/2026

🕐 Ahora selecciona la hora:

🌅 MAÑANA:
1. 08:00   2. 08:30   3. 09:00   4. 09:30
5. 10:00   6. 10:30   7. 11:00   8. 11:30

🌆 TARDE:
9. 14:00   10. 14:30  11. 15:00  12. 15:30
13. 16:00  14. 16:30

Responde con el número de la hora que prefieres.
```

**✅ VERIFICAR:**
- Horarios de mañana: 08:00 - 11:30 (8 opciones)
- Horarios de tarde: 14:00 - 16:30 (7 opciones)
- NO debe aparecer 12:00
- NO debe aparecer 17:00 (Sandra sale a las 17:00 los Miércoles)
- Última hora: 16:30

---

#### Caso B: Doctora Sandra + Jueves

**Usuario escribe:** `4` (Jueves)

**Bot debe responder:**
```
Perfecto! Has seleccionado:
📅 Jueves 13/03/2026

🕐 Ahora selecciona la hora:

🌅 MAÑANA:
1. 08:00   2. 08:30   3. 09:00   4. 09:30
5. 10:00   6. 10:30   7. 11:00   8. 11:30

🌆 TARDE:
9. 14:00   10. 14:30  11. 15:00  12. 15:30
13. 16:00  14. 16:30  15. 17:00

Responde con el número de la hora que prefieres.
```

**✅ VERIFICAR:**
- Horarios de mañana: 08:00 - 11:30 (8 opciones)
- Horarios de tarde: 14:00 - 17:00 (8 opciones)
- NO debe aparecer 12:00
- SÍ debe aparecer 17:00 (Sandra sale a las 17:30 los Jueves)
- Última hora: 17:00

---

#### Caso C: Doctora Zaida + Cualquier día

**Usuario escribe:** `2` (Martes)

**Bot debe responder:**
```
Perfecto! Has seleccionado:
📅 Martes 11/03/2026

🕐 Ahora selecciona la hora:

🌅 MAÑANA:
1. 08:00   2. 08:30   3. 09:00   4. 09:30
5. 10:00   6. 10:30   7. 11:00   8. 11:30

🌆 TARDE:
9. 14:00   10. 14:30  11. 15:00  12. 15:30
13. 16:00  14. 16:30  15. 17:00

Responde con el número de la hora que prefieres.
```

**✅ VERIFICAR:**
- Horarios de mañana: 08:00 - 11:30 (8 opciones)
- Horarios de tarde: 14:00 - 17:00 (8 opciones)
- NO debe aparecer 12:00
- SÍ debe aparecer 17:00 (Zaida sale a las 17:30 todos los días)
- Última hora: 17:00

---

#### Caso D: Sábado (cualquier doctora)

**Usuario escribe:** `6` (Sábado)

**Bot debe responder:**
```
Perfecto! Has seleccionado:
📅 Sábado 15/03/2026

🕐 Ahora selecciona la hora:

🌅 MAÑANA:
1. 08:00   2. 08:30   3. 09:00   4. 09:30
5. 10:00   6. 10:30   7. 11:00   8. 11:30

Responde con el número de la hora que prefieres.
```

**✅ VERIFICAR:**
- Solo horarios de mañana: 08:00 - 11:30 (8 opciones)
- NO debe aparecer sección "TARDE"
- NO debe aparecer 12:00
- Última hora: 11:30

---

### PASO 6: Seleccionar Hora

**Usuario escribe:** `14` (ejemplo: 16:30)

**Bot debe responder:**
```
Perfecto! Nueva fecha y hora:

📅 Miércoles 12/03/2026
🕐 16:30

¿Confirmas el cambio? Responde SÍ o NO.
```

**✅ VERIFICAR:**
- Que se muestre la fecha y hora seleccionadas correctamente
- Que se solicite confirmación

---

### PASO 7: Confirmar Cambio

**Usuario escribe:** `si`

**Bot debe responder:**
```
✅ ¡Cita reagendada exitosamente!

📅 12/03/2026 a las 16:30

Te esperamos! 😊
```

**✅ VERIFICAR:**
- Mensaje de éxito
- Fecha y hora correctas

---

### PASO 8: Verificar en Google Sheets

1. Abrir el Google Sheet de citas
2. Buscar la cita por cédula
3. Verificar que:
   - La fecha se haya actualizado correctamente
   - La hora se haya actualizado correctamente
   - La doctora siga siendo la misma
   - El servicio siga siendo el mismo
   - El estado siga siendo "Agendada"

---

## Tabla de Verificación de Horarios

| Doctora | Día | Última Hora Mañana | Última Hora Tarde | Total Opciones |
|---------|-----|-------------------|-------------------|----------------|
| Sandra | Lunes | 11:30 | 16:30 | 15 |
| Sandra | Martes | 11:30 | 16:30 | 15 |
| Sandra | Miércoles | 11:30 | 16:30 | 15 |
| Sandra | Jueves | 11:30 | 17:00 | 16 |
| Sandra | Viernes | 11:30 | 17:00 | 16 |
| Sandra | Sábado | 11:30 | - | 8 |
| Zaida | Lunes | 11:30 | 17:00 | 16 |
| Zaida | Martes | 11:30 | 17:00 | 16 |
| Zaida | Miércoles | 11:30 | 17:00 | 16 |
| Zaida | Jueves | 11:30 | 17:00 | 16 |
| Zaida | Viernes | 11:30 | 17:00 | 16 |
| Zaida | Sábado | 11:30 | - | 8 |

---

## Casos de Error a Probar

### Error 1: Cédula sin citas

**Usuario escribe:** `9999999999`

**Bot debe responder:**
```
No encontré citas agendadas con la cédula 9999999999. 😔

Verifica el número e intenta nuevamente, o escribe 'menu' para volver al inicio.
```

---

### Error 2: Número de cita inválido

**Usuario escribe:** `99` (cuando solo hay 2 citas)

**Bot debe responder:**
```
Número inválido. Por favor, elige un número de la lista.
```

---

### Error 3: Cancelar reagendamiento

En el paso de confirmación:

**Usuario escribe:** `no`

**Bot debe responder:**
```
Reagendamiento cancelado.
```

---

## Checklist de Prueba

- [ ] El bot muestra el menú correctamente
- [ ] Se puede seleccionar la opción 2 (Reagendar)
- [ ] Se solicita la cédula
- [ ] Se muestran las citas con la doctora asignada
- [ ] Se muestra el catálogo de 8 fechas
- [ ] NO se pregunta por la doctora
- [ ] Los horarios de mañana son correctos (08:00-11:30)
- [ ] NO aparece 12:00 en los horarios
- [ ] Los horarios de tarde son correctos según doctora y día
- [ ] Sandra Lunes-Miércoles: última hora 16:30
- [ ] Sandra Jueves-Viernes: última hora 17:00
- [ ] Zaida todos los días: última hora 17:00
- [ ] Sábados: solo horarios de mañana
- [ ] Se muestra la confirmación correctamente
- [ ] La cita se actualiza en Google Sheets
- [ ] La doctora NO cambia en la cita reagendada
- [ ] Los mensajes de error funcionan correctamente

---

## Notas Importantes

1. **La doctora NO se pregunta:** Se extrae automáticamente de la cita existente
2. **Los horarios son dinámicos:** Cambian según la doctora y el día de la semana
3. **Verificar en Sheets:** Siempre verificar que la actualización se haya guardado correctamente
4. **Formato de fecha:** En Sheets debe guardarse en formato DD/MM/YYYY
5. **Formato de hora:** En Sheets debe guardarse en formato HH:MM

---

**Estado:** ✅ LISTO PARA PRUEBAS  
**Última actualización:** 09 de marzo de 2026
