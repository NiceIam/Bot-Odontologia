"""
Script de prueba para el flujo de reagendar con horarios por doctora
Fecha: 09/03/2026
"""

import sys
from datetime import datetime
from chatbot_logic import ChatbotLogic

def print_separator():
    print("\n" + "="*80 + "\n")

def simulate_reagendar_flow():
    """Simula el flujo completo de reagendar una cita"""
    
    print("🧪 PRUEBA DEL FLUJO DE REAGENDAR CON HORARIOS POR DOCTORA")
    print_separator()
    
    # Inicializar chatbot
    try:
        chatbot = ChatbotLogic()
        print("✅ Chatbot inicializado correctamente")
    except Exception as e:
        print(f"❌ Error inicializando chatbot: {e}")
        return
    
    # Número de teléfono de prueba
    telefono = "+573001234567"
    
    print_separator()
    print("PASO 1: Mostrar menú principal")
    print_separator()
    
    respuesta = chatbot.show_menu(telefono)
    print(f"Bot: {respuesta}")
    
    print_separator()
    print("PASO 2: Usuario selecciona opción 2 (Reagendar)")
    print_separator()
    
    mensaje_usuario = "2"
    print(f"Usuario: {mensaje_usuario}")
    respuesta = chatbot.process_message(telefono, mensaje_usuario)
    print(f"Bot: {respuesta}")
    
    print_separator()
    print("PASO 3: Usuario ingresa cédula")
    print_separator()
    
    # Solicitar cédula al usuario para la prueba
    cedula = input("Ingresa una cédula que tenga citas en el sistema: ").strip()
    print(f"Usuario: {cedula}")
    respuesta = chatbot.process_message(telefono, cedula)
    print(f"Bot: {respuesta}")
    
    if "No encontré citas" in respuesta:
        print("\n❌ No se encontraron citas con esa cédula. Prueba terminada.")
        return
    
    print_separator()
    print("PASO 4: Usuario selecciona cita a reagendar")
    print_separator()
    
    seleccion_cita = input("Selecciona el número de la cita a reagendar: ").strip()
    print(f"Usuario: {seleccion_cita}")
    respuesta = chatbot.process_message(telefono, seleccion_cita)
    print(f"Bot: {respuesta}")
    
    # Verificar que se muestre el catálogo de fechas
    if "Selecciona una nueva fecha" not in respuesta:
        print("\n❌ Error: No se mostró el catálogo de fechas")
        return
    
    # Verificar que se haya extraído la doctora
    conv = chatbot.get_or_create_conversation(telefono)
    contexto = conv['contexto']
    doctora = contexto.get('doctora', 'NO ENCONTRADA')
    print(f"\n✅ Doctora extraída de la cita: {doctora}")
    
    print_separator()
    print("PASO 5: Usuario selecciona fecha")
    print_separator()
    
    seleccion_fecha = input("Selecciona el número de la fecha: ").strip()
    print(f"Usuario: {seleccion_fecha}")
    respuesta = chatbot.process_message(telefono, seleccion_fecha)
    print(f"Bot: {respuesta}")
    
    # Verificar que se muestren los horarios
    if "Ahora selecciona la hora" not in respuesta:
        print("\n❌ Error: No se mostró el catálogo de horas")
        return
    
    # Analizar los horarios mostrados
    print(f"\n📊 ANÁLISIS DE HORARIOS MOSTRADOS:")
    print(f"   Doctora: {doctora}")
    
    # Obtener día de la semana de la fecha seleccionada
    dias_disponibles = contexto.get('dias_disponibles', {})
    dia_info = dias_disponibles.get(seleccion_fecha, {})
    dia_semana = dia_info.get('dia_semana', 'Desconocido')
    fecha_str = dia_info.get('fecha', 'Desconocida')
    
    print(f"   Día: {dia_semana} ({fecha_str})")
    
    # Verificar horarios según doctora y día
    if "MAÑANA" in respuesta:
        print("   ✅ Horarios de mañana mostrados")
    if "TARDE" in respuesta:
        print("   ✅ Horarios de tarde mostrados")
    
    # Verificar última hora según doctora y día
    if doctora.lower() == "sandra":
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
        dia_numero = fecha_obj.weekday()  # 0=Lunes
        
        if dia_numero in [0, 1, 2]:  # Lunes-Miércoles
            if "16:30" in respuesta and "17:00" not in respuesta.split("16:30")[1]:
                print(f"   ✅ Última hora correcta para Sandra en {dia_semana}: 16:30")
            else:
                print(f"   ⚠️  Verificar última hora para Sandra en {dia_semana} (debería ser 16:30)")
        else:  # Jueves-Viernes
            if "17:00" in respuesta:
                print(f"   ✅ Última hora correcta para Sandra en {dia_semana}: 17:00")
            else:
                print(f"   ⚠️  Verificar última hora para Sandra en {dia_semana} (debería ser 17:00)")
    
    elif doctora.lower() == "zaida":
        if "17:00" in respuesta:
            print(f"   ✅ Última hora correcta para Zaida: 17:00")
        else:
            print(f"   ⚠️  Verificar última hora para Zaida (debería ser 17:00)")
    
    print_separator()
    print("PASO 6: Usuario selecciona hora")
    print_separator()
    
    seleccion_hora = input("Selecciona el número de la hora: ").strip()
    print(f"Usuario: {seleccion_hora}")
    respuesta = chatbot.process_message(telefono, seleccion_hora)
    print(f"Bot: {respuesta}")
    
    # Verificar que se muestre la confirmación
    if "¿Confirmas el cambio?" not in respuesta:
        print("\n❌ Error: No se mostró la confirmación")
        return
    
    print_separator()
    print("PASO 7: Usuario confirma el cambio")
    print_separator()
    
    confirmacion = input("¿Confirmar el cambio? (si/no): ").strip().lower()
    print(f"Usuario: {confirmacion}")
    respuesta = chatbot.process_message(telefono, confirmacion)
    print(f"Bot: {respuesta}")
    
    # Verificar resultado
    if "reagendada exitosamente" in respuesta.lower():
        print("\n✅ ¡PRUEBA EXITOSA! La cita se reagendó correctamente")
        print(f"\n📋 Resumen:")
        print(f"   - Doctora: {doctora}")
        print(f"   - Nueva fecha: {contexto.get('nueva_fecha', 'N/A')}")
        print(f"   - Nueva hora: {contexto.get('nueva_hora', 'N/A')}")
    else:
        print("\n⚠️  Reagendamiento cancelado o error")
    
    print_separator()

if __name__ == "__main__":
    try:
        simulate_reagendar_flow()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
