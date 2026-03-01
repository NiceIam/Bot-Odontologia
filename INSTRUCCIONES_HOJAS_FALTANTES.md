# ⚠️ ACCIÓN REQUERIDA: Crear Hojas Faltantes en Google Sheets

**Fecha:** 28/02/2026  
**Estado:** URGENTE - El sistema no funcionará hasta completar estos pasos

---

## Problema Detectado

El sistema ha sido migrado completamente a Google Sheets, pero faltan 2 hojas en el spreadsheet:

**Spreadsheet ID:** `1F8MG-UU0af0aEj87TcUpPmP4kcp3-GTddKOSJd2pIKw`

---

## Hojas que DEBES Crear

### 1. Hoja "Conversaciones"

Esta hoja almacena el estado de las conversaciones de cada usuario.

**Pasos:**

1. Abre el spreadsheet: https://docs.google.com/spreadsheets/d/1F8MG-UU0af0aEj87TcUpPmP4kcp3-GTddKOSJd2pIKw
2. Haz clic en el botón "+" en la parte inferior para crear una nueva hoja
3. Nómbrala exactamente: `Conversaciones` (con mayúscula inicial)
4. En la fila 1 (headers), escribe exactamente estas columnas:

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| telefono | estado | contexto | modo_humano | fecha_modo_humano | ultima_interaccion |

**IMPORTANTE:** Los nombres deben ser exactamente como se muestran (sin tildes, sin mayúsculas).

---

### 2. Hoja "Pacientes"

Esta hoja almacena información básica de los pacientes.

**Pasos:**

1. En el mismo spreadsheet, crea otra hoja nueva
2. Nómbrala exactamente: `Pacientes` (con mayúscula inicial)
3. En la fila 1 (headers), escribe exactamente estas columnas:

| A | B | C | D | E |
|---|---|---|---|---|
| telefono | nombre | email | fecha_nacimiento | created_at |

**IMPORTANTE:** Los nombres deben ser exactamente como se muestran (sin tildes, sin mayúsculas).

---

## Verificación

Después de crear las hojas, verifica que:

✅ La hoja "Citas" ya existe (NO la modifiques)  
✅ La hoja "Conversaciones" existe con 6 columnas  
✅ La hoja "Pacientes" existe con 5 columnas  
✅ Los nombres de las hojas tienen mayúscula inicial  
✅ Los headers están en la fila 1  
✅ Los headers están escritos exactamente como se indica (sin espacios extra)

---

## Estructura Visual de las Hojas

### Hoja "Conversaciones"

```
| telefono    | estado | contexto | modo_humano | fecha_modo_humano | ultima_interaccion |
|-------------|--------|----------|-------------|-------------------|-------------------|
| 5551234567  | menu   | {}       | false       |                   | 2026-02-28T...    |
```

### Hoja "Pacientes"

```
| telefono    | nombre      | email           | fecha_nacimiento | created_at        |
|-------------|-------------|-----------------|------------------|-------------------|
| 5551234567  | Juan Pérez  | juan@email.com  | 15/05/1990       | 2026-02-28T...    |
```

---

## Después de Crear las Hojas

Una vez creadas las hojas, el sistema funcionará automáticamente. No necesitas hacer nada más.

El chatbot:
- Creará automáticamente registros cuando los usuarios interactúen
- Almacenará conversaciones en "Conversaciones"
- Guardará datos de pacientes en "Pacientes"
- Consultará y actualizará citas en "Citas"

---

## Troubleshooting

### Error: "Sheet not found"

- Verifica que las hojas se llamen exactamente: "Conversaciones" y "Pacientes"
- Los nombres son case-sensitive (mayúsculas/minúsculas importan)

### Error: "Permission denied"

- Verifica que la service account tenga permisos de Editor
- Email: `orthodonto-server@odontologica-n8n.iam.gserviceaccount.com`

### Los datos no se guardan

- Verifica que los headers estén en la fila 1
- Verifica que no haya espacios extra en los nombres de las columnas
- Refresca el spreadsheet

---

**Última actualización:** 28 de febrero de 2026
