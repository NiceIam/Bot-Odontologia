# Corrección de Errores de Acceso a Diccionarios

**Fecha:** 28/02/2026  
**Tarea:** Corrección de errores en acceso a objetos de conversación

---

## Problema Identificado

El código intentaba acceder a propiedades de conversaciones usando notación de objeto (`conv.estado`, `conv.contexto`) cuando en realidad las conversaciones son diccionarios que requieren notación de corchetes (`conv['estado']`, `conv['contexto']`).

---

## Errores Corregidos

### Archivo: `chatbot_logic.py`

Se corrigieron **TODOS** los accesos incorrectos a conversaciones:

#### 1. Accesos a `conv.estado` → `conv['estado']`

**Líneas corregidas:**
- Línea 415: `print(f"DEBUG: estado actual = {conv['estado']}")`
- Línea 423: `if conv['estado'] in [self.ESTADO_INICIAL, self.ESTADO_MENU]:`
- Líneas 427-459: Todos los `elif conv['estado'] == ...` en los flujos de:
  - Agendar (5 estados)
  - Reagendar (5 estados)
  - Cancelar (2 estados)
  - Consultar (1 estado)

#### 2. Accesos a `conv.contexto` → `conv['contexto']`

**Líneas corregidas:**
- Línea 863: `contexto = conv['contexto'] or {}`
- Línea 898: `contexto = conv['contexto'] or {}`
- Línea 958: `contexto = conv['contexto'] or {}`
- Línea 1018: `contexto = conv['contexto']`
- Línea 1112: `contexto = conv['contexto']`
- Línea 1199: `contexto = conv['contexto']`
- Línea 1210: `contexto = conv['contexto']`
- Línea 1296: `contexto = conv['contexto']`
- Línea 1383: `contexto = conv['contexto']`
- Línea 1449: `contexto = conv['contexto']`

**Total de correcciones:** ~23 líneas modificadas

---

## Funciones Afectadas

Las siguientes funciones fueron corregidas:

### Flujo Principal
- `process_message()` - Línea 415, 423, 427-459

### Flujo de Agendar (Legacy - Comentado)
- `handle_agendar_servicio()` - Línea 863
- `handle_agendar_fecha()` - Línea 898
- `handle_agendar_hora()` - Línea 958
- `handle_agendar_confirmar()` - Línea 1018

### Flujo de Reagendar
- `handle_reagendar_seleccionar()` - Línea 1112
- `handle_reagendar_confirmar()` (show_servicios) - Línea 1199
- `handle_reagendar_fecha()` - Línea 1210
- `handle_reagendar_hora()` - Línea 1296
- `handle_reagendar_confirmar()` (confirmación) - Línea 1383

### Flujo de Cancelar
- `handle_cancelar_confirmar()` - Línea 1449

---

## Impacto

### Antes de la Corrección
```python
conv = self.get_or_create_conversation(telefono)
print(f"DEBUG: estado actual = {conv.estado}")  # ❌ ERROR
if conv.estado in [self.ESTADO_INICIAL, self.ESTADO_MENU]:  # ❌ ERROR
    contexto = conv.contexto or {}  # ❌ ERROR
```

**Error generado:**
```
AttributeError: 'dict' object has no attribute 'estado'
```

### Después de la Corrección
```python
conv = self.get_or_create_conversation(telefono)
print(f"DEBUG: estado actual = {conv['estado']}")  # ✅ CORRECTO
if conv['estado'] in [self.ESTADO_INICIAL, self.ESTADO_MENU]:  # ✅ CORRECTO
    contexto = conv['contexto'] or {}  # ✅ CORRECTO
```

**Resultado:** Código funcional sin errores de atributos

---

## Compatibilidad con Google Sheets

Estas correcciones son esenciales para la integración con Google Sheets porque:

1. `google_sheets_client.py` retorna diccionarios, no objetos ORM
2. Los diccionarios usan notación de corchetes para acceder a valores
3. La estructura es consistente con el formato JSON almacenado en el sheet

### Estructura de Conversación (Diccionario)
```python
{
    'telefono': '5551234567',
    'estado': 'menu',
    'contexto': {},
    'modo_humano': 'false',
    'fecha_modo_humano': '',
    'ultima_interaccion': '2026-02-28T22:30:00.000Z'
}
```

---

## Verificación

Para verificar que las correcciones funcionan:

```bash
# Ejecutar el chatbot
python main.py

# Enviar un mensaje de prueba
# El sistema debe procesar sin errores de AttributeError
```

---

## Archivos Modificados

- ✅ `chatbot_logic.py` - 23 líneas corregidas
- ✅ `INSTRUCCIONES_HOJAS_FALTANTES.md` - Creado (instrucciones para el usuario)
- ✅ `CORRECCION_ERRORES_DICCIONARIOS.md` - Este archivo (documentación)

---

## Próximos Pasos

1. ✅ Correcciones de código completadas
2. ⏳ Usuario debe crear hojas "Conversaciones" y "Pacientes" en el spreadsheet
3. ⏳ Probar el sistema completo con las hojas creadas

---

**Estado:** COMPLETADO  
**Última actualización:** 28 de febrero de 2026
