# Sistema de Catálogo de Fechas y Horas para Reagendar

**Fecha:** 28/02/2026  
**Cambio:** Implementación de catálogo visual para selección de fechas y horas

---

## Resumen del Cambio

El sistema ahora consulta el sheet "Calendario" para mostrar un catálogo de los próximos 8 días laborales disponibles, y luego muestra las horas disponibles según el día seleccionado.

---

## Flujo Nuevo (Paso a Paso)

### Paso 1: Solicitar Cédula
```
Usuario: 2 (reagendar)
Bot: Por favor, ingresa tu número de cédula para buscar tus citas:
```

### Paso 2: Mostrar Citas
```
Usuario: 1029400483
Bot: Encontré 2 cita(s) con la cédula 1029400483:

1. 📅 20/02/2026 a las 8:00
   💼 Servicio: Ortodoncia
   ...

¿Cuál cita deseas reagendar? Responde con el número.
```

### Paso 3: Catálogo de Fechas
```
Usuario: 1
Bot: Vas a reagendar esta cita:

📅 20/02/2026 a las 8:00
💼 Servicio: Ortodoncia
👩‍⚕️ Doctora: Sandra
📝 Estado: Agendada

📅 Selecciona una nueva fecha (próximos días disponibles):

1. Lunes 03/03/2026
2. Martes 04/03/2026
3. Miércoles 05/03/2026
4. Jueves 06/03/2026
5. Viernes 07/03/2026
6. Sábado 08/03/2026
7. Lunes 10/03/2026
8. Martes 11/03/2026

Responde con el número de la fecha que prefieres.
```

### Paso 4: Catálogo de Horas (según doctora de la cita)
```
Usuario: 3 (Miércoles)
Bot: Perfecto! Has seleccionado:
📅 Miércoles 05/03/2026

🕐 Ahora selecciona la hora:

🌅 MAÑANA:
1. 08:00   2. 08:30   3. 09:00   4. 09:30
5. 10:00   6. 10:30   7. 11:00   8. 11:30

🌆 TARDE:
9. 14:00   10. 14:30  11. 15:00  12. 15:30
13. 16:00  14. 16:30

Responde con el número de la hora que prefieres.

Nota: Como la cita es con Doctora Sandra y es Miércoles, 
la última hora disponible es 16:30
```

### Paso 5: Confirmación
```
Usuario: 14
Bot: Perfecto! Nueva fecha y hora:

📅 Miércoles 05/03/2026
🕐 16:30

¿Confirmas el cambio? Responde SÍ o NO.
```

---

## Estructura del Sheet "Calendario"

El bot consulta el sheet "Calendario" con la siguiente estructura:

| Columna A | Columna B | Columna C | Columna D |
|-----------|-----------|-----------|-----------|
| fecha | dia_semana | es_laborable | festivo |
| 2026-01-01 | Jueves | FALSE | Año Nuevo |
| 2026-01-02 | Viernes | TRUE | |
| 2026-01-03 | Sábado | TRUE | |
| 2026-01-04 | Domingo | FALSE | Domingo |

### Reglas de Filtrado:

1. **Solo fechas futuras:** `fecha > hoy`
2. **Solo días laborables:** `es_laborable = TRUE`
3. **Límite:** Primeros 8 días que cumplan las condiciones

---

## Horarios Disponibles por Día

### Lunes a Viernes
- **Horario Mañana:** 8:00 - 12:00 (última cita 11:30)
- **Horario Tarde:** 14:00 - 17:00
- **Intervalos:** Cada 30 minutos

#### Doctora Sandra
- **Lunes, Martes, Miércoles:** última cita 16:30 (sale a las 17:00)
- **Jueves, Viernes:** última cita 17:00 (sale a las 17:30)

#### Doctora Zaida
- **Todos los días:** última cita 17:00 (sale a las 17:30)

### Sábados
- **Horario:** 8:00 - 12:00 (última cita 11:30)
- **Intervalos:** Cada 30 minutos
- **Total:** 8 opciones de hora

### Domingos
- **No se trabaja** (filtrado automáticamente por `es_laborable = FALSE`)

---

## Funciones Nuevas Creadas

### En `google_sheets_client.py`:

#### 1. `get_next_working_days(limit=8)`
Obtiene los próximos días laborales desde el sheet "Calendario"

**Parámetros:**
- `limit`: Número de días a retornar (default: 8)

**Retorna:**
```python
[
    {
        'fecha': '2026-03-03',
        'fecha_obj': date(2026, 3, 3),
        'dia_semana': 'Lunes',
        'es_laborable': 'TRUE',
        'festivo': ''
    },
    ...
]
```

#### 2. `get_available_hours_for_date(fecha_str, doctora=None)`
Obtiene las horas disponibles para una fecha específica y doctora

**Parámetros:**
- `fecha_str`: Fecha en formato 'YYYY-MM-DD'
- `doctora`: Nombre de la doctora (opcional: "Sandra" o "Zaida")

**Retorna:**
```python
# Lunes-Viernes (sin doctora especificada o Zaida)
['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
 '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00']

# Lunes-Miércoles con Doctora Sandra
['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
 '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']

# Jueves-Viernes con Doctora Sandra
['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
 '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00']

# Sábados
['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30']
```

---

### En `chatbot_logic.py`:

#### 1. `handle_reagendar_seleccionar(telefono, mensaje)`
Maneja la selección de cita y extrae la doctora de la cita existente

**Flujo:**
1. Valida número seleccionado
2. Obtiene cita del contexto
3. Extrae doctora de la cita: `doctora = cita.get('doctora', '')`
4. Guarda doctora en contexto
5. Obtiene próximos 8 días laborales
6. Muestra catálogo de fechas
7. Cambia estado a `ESTADO_REAGENDAR_FECHA`

#### 2. `handle_reagendar_fecha(telefono, mensaje)`
Maneja la selección de fecha del catálogo

**Flujo:**
1. Valida número seleccionado
2. Obtiene fecha del contexto
3. Obtiene doctora del contexto
4. Consulta horas disponibles para esa fecha y doctora
5. Muestra catálogo de horas
6. Cambia estado a `ESTADO_REAGENDAR_HORA`

#### 3. `handle_reagendar_hora(telefono, mensaje)`
Maneja la selección de hora del catálogo

**Flujo:**
1. Valida número seleccionado
2. Obtiene hora del contexto
3. Muestra confirmación con fecha y hora
4. Cambia estado a `ESTADO_REAGENDAR_CONFIRMAR`

---

## Estados Modificados

### Antes:
```
ESTADO_REAGENDAR_CEDULA
ESTADO_REAGENDAR_SELECCIONAR
ESTADO_REAGENDAR_SERVICIO  ← Eliminado
ESTADO_REAGENDAR_FECHA
ESTADO_REAGENDAR_HORA
ESTADO_REAGENDAR_CONFIRMAR
```

### Ahora:
```
ESTADO_REAGENDAR_CEDULA
ESTADO_REAGENDAR_SELECCIONAR  ← Modificado (extrae doctora de cita)
ESTADO_REAGENDAR_FECHA         ← Modificado (usa doctora de cita)
ESTADO_REAGENDAR_HORA          ← Modificado (muestra catálogo)
ESTADO_REAGENDAR_CONFIRMAR
```

**Nota:** Ya NO hay estado `ESTADO_REAGENDAR_DOCTORA` porque la doctora se obtiene automáticamente de la cita existente.

---

## Contexto Guardado

Durante el flujo, se guarda en el contexto:

```python
{
    "cedula": "1029400483",
    "cita_id": "1029400483",
    
    # Después de seleccionar cita (doctora extraída automáticamente):
    "doctora": "Sandra",  # ← Extraída de la cita existente
    "dias_disponibles": {
        "1": {"fecha": "2026-03-03", "dia_semana": "Lunes", ...},
        "2": {"fecha": "2026-03-04", "dia_semana": "Martes", ...},
        ...
    },
    
    # Después de seleccionar fecha específica:
    "fecha_seleccionada": "2026-03-05",
    "fecha_formato": "05/03/2026",
    "dia_semana": "Miércoles",
    "horas_disponibles": {
        "1": "08:00",
        "2": "08:30",
        ...
        "14": "16:30"  # Última hora para Sandra en Miércoles
    },
    
    # Para confirmación:
    "nueva_fecha": "05/03/2026",
    "nueva_hora": "16:30"
}
```

---

## Ventajas del Nuevo Sistema

✅ **Más fácil para el usuario:** No tiene que escribir fechas manualmente
✅ **Menos errores:** Validación automática de días laborables
✅ **Respeta festivos:** Consulta el calendario real
✅ **Horarios correctos:** Sábados automáticamente muestran 8-12h
✅ **Horarios por doctora:** Respeta los horarios específicos de cada doctora automáticamente
✅ **Sin preguntas innecesarias:** La doctora se obtiene de la cita existente
✅ **Visual y claro:** Catálogo numerado fácil de leer
✅ **Paso a paso:** Primero fecha, luego hora (no todo junto)

---

## Configuración Requerida

### Sheet "Calendario" debe existir con:

**Headers (fila 1):**
```
fecha | dia_semana | es_laborable | festivo
```

**Formato de datos:**
- `fecha`: YYYY-MM-DD (texto o fecha)
- `dia_semana`: Texto (Lunes, Martes, etc.)
- `es_laborable`: TRUE o FALSE (texto)
- `festivo`: Texto opcional (nombre del festivo)

**Ejemplo de datos:**
```
2026-03-01 | Domingo | FALSE | Domingo
2026-03-02 | Lunes | TRUE | 
2026-03-03 | Martes | TRUE | 
2026-03-04 | Miércoles | TRUE | 
2026-03-05 | Jueves | TRUE | 
2026-03-06 | Viernes | TRUE | 
2026-03-07 | Sábado | TRUE | 
2026-03-08 | Domingo | FALSE | Domingo
```

---

## Archivos Modificados

1. **google_sheets_client.py**
   - Agregado `self.sheet_calendario = "Calendario"`
   - Nueva función `get_next_working_days()`
   - Nueva función `get_available_hours_for_date()`

2. **chatbot_logic.py**
   - Eliminado estado `ESTADO_REAGENDAR_SERVICIO`
   - Modificada función `handle_reagendar_seleccionar()` - ahora muestra catálogo de fechas
   - Reescrita función `handle_reagendar_fecha()` - ahora procesa selección de fecha
   - Reescrita función `handle_reagendar_hora()` - ahora procesa selección de hora
   - Funciones antiguas comentadas como legacy

---

## Testing

Para probar el nuevo sistema:

1. Asegúrate de que el sheet "Calendario" existe y tiene datos
2. Selecciona opción 2 (Reagendar)
3. Ingresa una cédula válida
4. Selecciona una cita
5. Verifica que aparezca el catálogo de 8 fechas
6. Selecciona una fecha
7. Verifica que aparezcan las horas correctas (16 para L-V, 8 para sábado)
8. Selecciona una hora
9. Confirma el cambio

---

**Estado:** ✅ COMPLETADO  
**Última actualización:** 28 de febrero de 2026
