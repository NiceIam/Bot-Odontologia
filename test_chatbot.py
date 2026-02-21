"""
Script de prueba para el chatbot
Simula conversaciones sin necesidad de WhatsApp
"""

from database import SessionLocal, Paciente, Doctor, Servicio, Cita, Conversacion
from chatbot_logic import ChatbotLogic
from datetime import datetime

def test_conversation():
    """Simula una conversación completa"""
    db = SessionLocal()
    chatbot = ChatbotLogic(db)
    
    telefono = "5511999999999"
    
    print("=" * 60)
    print("SIMULACIÓN DE CONVERSACIÓN CON EL CHATBOT")
    print("=" * 60)
    print()
    
    # Mensaje inicial
    print("Usuario: Hola")
    respuesta = chatbot.process_message(telefono, "Hola")
    print(f"Bot: {respuesta}")
    print()
    
    # Agendar cita
    print("Usuario: 1")
    respuesta = chatbot.process_message(telefono, "1")
    print(f"Bot: {respuesta}")
    print()
    
    # Nombre (si es usuario nuevo)
    if "nombre" in respuesta.lower():
        print("Usuario: Juan Pérez")
        respuesta = chatbot.process_message(telefono, "Juan Pérez")
        print(f"Bot: {respuesta}")
        print()
    
    # Seleccionar servicio
    print("Usuario: 1")
    respuesta = chatbot.process_message(telefono, "1")
    print(f"Bot: {respuesta}")
    print()
    
    # Fecha
    print("Usuario: 24/02/2026")
    respuesta = chatbot.process_message(telefono, "24/02/2026")
    print(f"Bot: {respuesta}")
    print()
    
    # Hora
    print("Usuario: 10:00")
    respuesta = chatbot.process_message(telefono, "10:00")
    print(f"Bot: {respuesta}")
    print()
    
    # Confirmar
    print("Usuario: sí")
    respuesta = chatbot.process_message(telefono, "sí")
    print(f"Bot: {respuesta}")
    print()
    
    db.close()

def list_appointments():
    """Lista todas las citas agendadas"""
    db = SessionLocal()
    
    print("=" * 60)
    print("CITAS AGENDADAS EN EL SISTEMA")
    print("=" * 60)
    print()
    
    citas = db.query(Cita).filter(Cita.estado == "agendada").order_by(Cita.fecha_hora).all()
    
    if not citas:
        print("No hay citas agendadas.")
    else:
        for cita in citas:
            paciente = db.query(Paciente).filter(Paciente.id == cita.paciente_id).first()
            doctor = db.query(Doctor).filter(Doctor.id == cita.doctor_id).first()
            servicio = db.query(Servicio).filter(Servicio.id == cita.servicio_id).first()
            
            print(f"ID: {cita.id}")
            print(f"Paciente: {paciente.nombre} ({paciente.telefono})")
            print(f"Doctor: {doctor.nombre}")
            print(f"Servicio: {servicio.nombre} ({servicio.duracion_minutos} min)")
            print(f"Fecha/Hora: {cita.fecha_hora.strftime('%d/%m/%Y %H:%M')}")
            print(f"Estado: {cita.estado}")
            print("-" * 60)
    
    db.close()

def list_services():
    """Lista todos los servicios disponibles"""
    db = SessionLocal()
    
    print("=" * 60)
    print("CATÁLOGO DE SERVICIOS")
    print("=" * 60)
    print()
    
    servicios = db.query(Servicio).filter(Servicio.activo == "true").order_by(Servicio.categoria, Servicio.nombre).all()
    
    categoria_actual = None
    for servicio in servicios:
        if servicio.categoria != categoria_actual:
            print(f"\n📋 {servicio.categoria}:")
            categoria_actual = servicio.categoria
        print(f"  - {servicio.nombre} ({servicio.duracion_minutos} min)")
    
    print()
    db.close()

def list_doctors():
    """Lista todos los doctores"""
    db = SessionLocal()
    
    print("=" * 60)
    print("DOCTORES DISPONIBLES")
    print("=" * 60)
    print()
    
    doctores = db.query(Doctor).filter(Doctor.activo == "true").all()
    
    for doctor in doctores:
        print(f"👨‍⚕️ {doctor.nombre}")
        print(f"   Especialidad: {doctor.especialidad}")
        print()
    
    db.close()

def check_availability():
    """Verifica disponibilidad para una fecha"""
    db = SessionLocal()
    chatbot = ChatbotLogic(db)
    
    print("=" * 60)
    print("VERIFICAR DISPONIBILIDAD")
    print("=" * 60)
    print()
    
    fecha_str = "24/02/2026"
    from dateutil import parser
    fecha = parser.parse(fecha_str, dayfirst=True)
    
    print(f"Fecha: {fecha.strftime('%d/%m/%Y')}")
    print()
    
    # Servicios de 30 minutos
    print("Horarios disponibles para servicios de 30 minutos:")
    slots_30 = chatbot.get_available_slots(fecha, 30, limit=10)
    for slot in slots_30:
        print(f"  ✓ {slot}")
    print()
    
    # Servicios de 60 minutos
    print("Horarios disponibles para servicios de 60 minutos:")
    slots_60 = chatbot.get_available_slots(fecha, 60, limit=10)
    for slot in slots_60:
        print(f"  ✓ {slot}")
    
    db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "test":
            test_conversation()
        elif comando == "citas":
            list_appointments()
        elif comando == "servicios":
            list_services()
        elif comando == "doctores":
            list_doctors()
        elif comando == "disponibilidad":
            check_availability()
        else:
            print("Comandos disponibles:")
            print("  python test_chatbot.py test           - Simular conversación")
            print("  python test_chatbot.py citas          - Listar citas agendadas")
            print("  python test_chatbot.py servicios      - Listar servicios")
            print("  python test_chatbot.py doctores       - Listar doctores")
            print("  python test_chatbot.py disponibilidad - Ver disponibilidad")
    else:
        print("Comandos disponibles:")
        print("  python test_chatbot.py test           - Simular conversación")
        print("  python test_chatbot.py citas          - Listar citas agendadas")
        print("  python test_chatbot.py servicios      - Listar servicios")
        print("  python test_chatbot.py doctores       - Listar doctores")
        print("  python test_chatbot.py disponibilidad - Ver disponibilidad")
