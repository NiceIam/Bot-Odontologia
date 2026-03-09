# Actualización de Horarios por Doctora

**Fecha:** 09/03/2026  
**Cambio:** Implementación de horarios diferenciados por doctora según la cita existente

---

## Resumen del Cambio

El sistema ahora ajusta los horarios disponibles según la doctora asignada en la cita existente que se está reagendando. Los horarios se calculan dinámicamente basándose en:
1. Los nuevos horarios de atención (mañana y tarde con pausa de almuerzo)
2. Los horarios específicos de cada doctora
3. El día de la semana seleccionado

**IMPORTANTE:** El chatbot NO agenda citas nuevas (redirige a sistema externo). Solo reagenda y cancela citas existentes.

---

## Nuevos Horarios de Atención

### Horario General
- **Mañana:** 8:00 AM - 12:00 PM (última cita 11:30 AM)
- **Almuerzo:** 12:00 PM - 2:00 PM (cerrado)
- **Tarde:** 2:00 PM - 5:00 PM (varía según doctora)

### Horarios por Doctora

#### Doctora Sandra
- **Lunes, Martes, Miércoles:**
  - Mañana: 8:00 - 12:00 (última cita 11:30)
  - Tarde: 14:00 - 17:00 (última cita 16:30)
  - Sale a las 17:00

- **Jueves, Viernes:**
  - Mañana: 8:00 - 12:00 (última cita 11:30)
  - Tarde: 14:00 - 17:30 (última cita 17:00)
  - Sale a las 17:30

#### Doctora Zaida
- **Todos los días laborables:**
  - Mañana: 8:00 - 12:00 (última cita 11:30)
  - Tarde: 14:00 - 17:30 (última cita 17:00)
  - Sale a las 17:30

### Sábados (ambas doctoras)
- **Horario:** 8:00 - 12:00 (última cita 11:30)
- Sin atención en la tarde

---

## Cómo Funciona

### Flujo de Reagendar

1. **Cédula** → Usuario ingresa cédula
2. **Seleccionar cita** → Usuario elige qué cita reagendar
3. **Sistema obtiene doctora** → El sistema lee la doctora asignada en la cita existente (campo `doctora` del sheet)
4. **Fecha** → Usuario selecciona de catálogo de 8 días
5. **Hora** → Sistema muestra horarios según la doctora de la cita y el día seleccionado
6. **Confirmar** → Usuario confirma el cambio

### Lógica de Horarios

El sistema:
1. Lee la cita existente del Google Sheet
2. Extrae el campo `doctora` (puede ser "Sandra" o "Zaida")
3. Cuando el usuario selecciona una fecha, calcula los horarios disponibles usando:
   - La doctora de la cita original
   - El día de la semana de la fecha seleccionada
   - Las reglas de horario específicas de cada doctora

---

## Ejemplo de Interacción

### Reagendar Cita Existente

```
Usuario: 2 (reagendar)
Bot: Por favor, ingresa tu número de cédula para buscar tus citas:

Usuario: 1029400483
Bot: Encontré 2 cita(s) con la cédula 1029400483:

     1. 📅 20/02/2026 a las 8:00
        💼 Servicio: Ortodoncia
        👩‍⚕️ Doctora: Sandra
        � Estado: Agendada
     
     2. 📅 25/02/2026 a las 14:00
        💼 Servicio: Limpieza
        👩‍⚕️ Doctora: Zaida
        📝 Estado: Agendada
     
     ¿Cuál cita deseas reagendar? Responde con el número.

Usuario: 1
Bot: Vas a reagendar esta cita:
     
     📅 20/02/2026 a las 8:00
     💼 Servicio: Ortodoncia
     👩‍⚕️ Doctora: Sandra
     📝 Estado: Agendada
     
     📅 Selecciona una nueva fecha (próximos días disponibles):
     
     1. Lunes 10/03/2026
     2. Martes 11/03/2026
     3. Miércoles 12/03/2026
     4. Jueves 13/03/2026
     5. Viernes 14/03/2026
     ...
     
     Responde con el número de la fecha que prefieres.

Usuario: 3 (Miércoles)
Bot: Perfecto! Has seleccionado:
     📅 Miércoles 12/03/2026
     
     🕐 Ahora selecciona la hora:
     
     🌅 MAÑANA:
     1. 08:00   2. 08:30   3. 09:00   4. 09:30
     5. 10:00   6. 10:30   7. 11:00   8. 11:30
     
     🌆 TARDE:
     9. 14:00   10. 14:30  11. 15:00  12. 15:30
     13. 16:00  14. 16:30  ← Última cita (Miércoles con Sandra)
     
     Responde con el número de la hora que prefieres.

Usuario: 14
Bot: Perfecto! Nueva fecha y hora:
     
     📅 Miércoles 12/03/2026
     🕐 16:30
     
     ¿Confirmas el cambio? Responde SÍ o NO.
```

**Nota:** Si la cita fuera con Doctora Zaida, o si fuera Jueves/Viernes con Sandra, también aparecería la opción "15. 17:00"

---

## Archivos Modificados

### 1. `google_sheets_client.py`

**Función modificada:** `get_available_hours_for_date(fecha_str, doctora=None)`

**Cambios:**
- Agregado parámetro `doctora` (opcional: "Sandra" o "Zaida")
- Horarios de mañana: 8:00-12:00 (última cita 11:30)
- Horarios de tarde: 14:00-17:00+ (ajustable según doctora y día)
- Lógica para Doctora Sandra:
  - Lunes-Miércoles: última cita 16:30
  - Jueves-Viernes: última cita 17:00
- Lógica para Doctora Zaida: última cita 17:00 todos los días
- Sábados: solo mañana (8:00-11:30) para ambas doctoras

**Código clave:**
```python
def get_available_hours_for_date(self, fecha_str: str, doctora: str = None) -> List[str]:
    # Parsear fecha y obtener día de la semana
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
    dia_numero = fecha.weekday()  # 0=Lunes, 1=Martes, etc.
    
    # Determinar hora de cierre según doctora y día
    if doctora:
        doctora_lower = doctora.lower()
        if doctora_lower == "sandra":
            if dia_numero in [0, 1, 2]:  # Lunes-Miércoles
                hora_cierre = 17  # última cita 16:30
            else:  # Jueves-Viernes
                hora_cierre = 17.5  # última cita 17:00
        elif doctora_lower == "zaida":
            hora_cierre = 17.5  # última cita 17:00
```

### 2. `chatbot_logic.py`

**Función modificada:** `handle_reagendar_seleccionar(telefono, mensaje)`

**Cambios:**
- Ahora extrae la doctora de la cita existente: `doctora = cita.get('doctora', '')`
- Guarda la doctora en el contexto: `contexto["doctora"] = doctora`
- Ya NO pregunta al usuario por la doctora
- Pasa directamente a mostrar el catálogo de fechas

**Código clave:**
```python
def handle_reagendar_seleccionar(self, telefono: str, mensaje: str) -> str:
    # ... validaciones ...
    
    cita = citas[indice]
    
    # Obtener doctora de la cita existente
    doctora = cita.get('doctora', '')
    
    # ... obtener días laborales ...
    
    contexto["cita_id"] = cita['id']
    contexto["doctora"] = doctora  # Guardar doctora de la cita existente
    contexto["dias_disponibles"] = dias_serializables
    self.update_conversation(telefono, self.ESTADO_REAGENDAR_FECHA, contexto)
```

**Función modificada:** `handle_reagendar_fecha(telefono, mensaje)`

**Cambios:**
- Obtiene la doctora del contexto: `doctora = contexto.get("doctora", None)`
- Pasa la doctora a `get_available_hours_for_date()`: `horas_disponibles = sheets_client.get_available_hours_for_date(fecha_str, doctora)`

---

## Validaciones Implementadas

1. **Extracción de doctora:** Lee el campo `doctora` de la cita existente en Google Sheets
2. **Horarios de mañana:** Siempre hasta 11:30 (para que termine a las 12:00)
3. **Horarios de tarde:** Varían según doctora y día de la semana:
   - Sandra + Lunes/Martes/Miércoles: hasta 16:30
   - Sandra + Jueves/Viernes: hasta 17:00
   - Zaida + cualquier día: hasta 17:00
4. **Sábados:** Solo horarios de mañana (8:00-11:30)
5. **Domingos:** No disponibles (filtrado por calendario)

---

## Contexto Guardado

Durante el flujo de reagendar, se guarda en el contexto:

```python
{
    "cedula": "1029400483",
    "cita_id": "...",
    "doctora": "Sandra",  # ← Extraída de la cita existente
    "dias_disponibles": {
        "1": {"fecha": "2026-03-10", "dia_semana": "Lunes", ...},
        "2": {"fecha": "2026-03-11", "dia_semana": "Martes", ...},
        ...
    },
    "fecha_seleccionada": "2026-03-12",
    "fecha_formato": "12/03/2026",
    "dia_semana": "Miércoles",
    "horas_disponibles": {
        "1": "08:00",
        "2": "08:30",
        ...
        "14": "16:30"  # Última hora para Sandra en Miércoles
    },
    "nueva_fecha": "12/03/2026",
    "nueva_hora": "16:30"
}
```

---

## Testing

Para probar el nuevo sistema:

### Reagendar con Doctora Sandra
1. Selecciona opción 2 (Reagendar)
2. Ingresa cédula con cita de Doctora Sandra
3. Selecciona la cita
4. Selecciona una fecha (Miércoles)
5. Verifica que la última hora sea 16:30
6. Selecciona una fecha (Jueves)
7. Verifica que la última hora sea 17:00

### Reagendar con Doctora Zaida
1. Selecciona opción 2 (Reagendar)
2. Ingresa cédula con cita de Doctora Zaida
3. Selecciona la cita
4. Selecciona cualquier fecha
5. Verifica que la última hora sea 17:00

### Verificar Horarios de Mañana
1. Para cualquier doctora y día
2. Verifica que los horarios de mañana sean: 08:00, 08:30, 09:00, 09:30, 10:00, 10:30, 11:00, 11:30
3. Verifica que NO aparezca 12:00

### Verificar Sábados
1. Selecciona un sábado
2. Verifica que solo aparezcan horarios de mañana (08:00 - 11:30)
3. Verifica que NO aparezcan horarios de tarde

---

## Notas Importantes

- **El chatbot NO agenda citas nuevas:** El flujo de agendar redirige a un sistema externo
- **Solo reagenda citas existentes:** La doctora ya está asignada en la cita original
- **Horarios dinámicos:** Se calculan en tiempo real según doctora y día
- **Respeta horarios de salida:** La última cita siempre es 30 minutos antes del cierre
- **Validación en Google Sheets:** El sistema debe verificar disponibilidad real en el sheet "Citas"

---

## Próximos Pasos (Recomendado)

Para completar la implementación, se recomienda:

1. **Validar disponibilidad real:** Antes de mostrar horarios, verificar en el sheet "Citas" qué horas ya están ocupadas
2. **Filtrar horarios ocupados:** No mostrar horarios que ya tienen citas agendadas
3. **Considerar duración del servicio:** Algunos servicios pueden requerir más de 30 minutos

---

**Estado:** ✅ COMPLETADO  
**Última actualización:** 09 de marzo de 2026
