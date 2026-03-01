# Implementación de Solicitud de Cédula

**Fecha:** 28/02/2026  
**Cambio:** Solicitar cédula antes de reagendar, cancelar o consultar citas

---

## Cambios Realizados

### 1. Nuevos Estados Agregados

Se agregaron 3 nuevos estados en `chatbot_logic.py`:

```python
# Reagendar
ESTADO_REAGENDAR_CEDULA = "reagendar_cedula"

# Cancelar
ESTADO_CANCELAR_CEDULA = "cancelar_cedula"

# Consultar
ESTADO_CONSULTAR_CEDULA = "consultar_cedula"
```

---

### 2. Nuevas Funciones Creadas

#### En `chatbot_logic.py`:

**Reagendar:**
- `handle_reagendar_cedula()` - Solicita y valida la cédula, busca citas

**Cancelar:**
- `handle_cancelar_cedula()` - Solicita y valida la cédula, busca citas

**Consultar:**
- `handle_consultar_cedula()` - Solicita y valida la cédula, muestra citas

#### En `google_sheets_client.py`:

- `get_appointments_by_id(cedula)` - Busca citas por cédula (columna ID del sheet)

---

### 3. Flujo Modificado

#### Antes:
```
Usuario selecciona opción 2/3/4
  ↓
Bot busca citas por teléfono
  ↓
Muestra citas encontradas
```

#### Ahora:
```
Usuario selecciona opción 2/3/4
  ↓
Bot solicita cédula
  ↓
Usuario ingresa cédula
  ↓
Bot valida cédula (solo números, mínimo 6 dígitos)
  ↓
Bot busca citas por cédula en Google Sheets
  ↓
Muestra citas encontradas o mensaje de error
```

---

### 4. Validaciones Implementadas

La cédula debe cumplir:
- ✅ Solo números (sin letras ni caracteres especiales)
- ✅ Mínimo 6 dígitos
- ✅ Debe existir en la columna "ID" del sheet "Citas"

**Mensajes de error:**
- "❌ Por favor, ingresa solo números. Ejemplo: 1234567890"
- "❌ La cédula debe tener al menos 6 dígitos. Por favor, intenta nuevamente."
- "No encontré citas agendadas con la cédula {cedula}. 😔"

---

### 5. Ejemplo de Uso

**Reagendar una cita:**

```
Usuario: 2
Bot: Por favor, ingresa tu número de cédula para buscar tus citas:

Usuario: 1029400483
Bot: Encontré 2 cita(s) con la cédula 1029400483:

1. 📅 20/02/2026 a las 8:00
   💼 Servicio: Ortodoncia - Valoración de Ortodoncia
   👩‍⚕️ Doctora: Dra. Sandra Simancas
   📝 Estado: Agendada

2. 📅 25/02/2026 a las 14:00
   💼 Servicio: Limpieza Dental
   👩‍⚕️ Doctora: Dra. Sandra Simancas
   📝 Estado: Agendada

¿Cuál cita deseas reagendar? Responde con el número.

Usuario: 1
Bot: Vas a reagendar esta cita:
...
```

---

### 6. Búsqueda en Google Sheets

La búsqueda se realiza en la columna **"ID"** (columna A) del sheet "Citas".

**Estructura del sheet:**
```
| ID         | Nombre | Correo | Teléfono | Fecha | Hora | Estado | ...
|------------|--------|--------|----------|-------|------|--------|
| 1029400483 | Luis   | ...    | 320...   | ...   | ...  | ...    |
```

**Filtros aplicados:**
- Solo citas con estado diferente a "Cancelada" o "Atendida"
- Coincidencia exacta con la cédula ingresada

---

### 7. Archivos Modificados

**chatbot_logic.py:**
- 3 nuevos estados agregados
- 3 nuevas funciones creadas
- Modificado `handle_menu()` para solicitar cédula
- Modificado `process_message()` para manejar nuevos estados
- Modificadas funciones `handle_reagendar_seleccionar()` y `handle_cancelar_seleccionar()` para usar cédula del contexto

**google_sheets_client.py:**
- Nueva función `get_appointments_by_id(cedula)` agregada

---

### 8. Ventajas del Cambio

✅ Mayor seguridad: Verifica identidad del paciente
✅ Evita confusiones: Busca por cédula única en lugar de teléfono
✅ Mejor experiencia: Mensajes claros de validación
✅ Escalable: Fácil agregar más validaciones en el futuro

---

### 9. Compatibilidad

- ✅ Compatible con estructura actual del sheet "Citas"
- ✅ No afecta otros flujos (agendamiento, handoff humano)
- ✅ Mantiene código legacy comentado para rollback

---

**Estado:** ✅ COMPLETADO  
**Última actualización:** 28 de febrero de 2026
