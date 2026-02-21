from datetime import datetime, timedelta, time
from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session
from database import Paciente, Cita, Conversacion, Doctor, Servicio
from dateutil import parser
import re

class ChatbotLogic:
    # Estados de conversación
    ESTADO_INICIAL = "inicial"
    ESTADO_MENU = "menu"
    
    # Agendar
    ESTADO_AGENDAR_NOMBRE = "agendar_nombre"
    ESTADO_AGENDAR_SERVICIO = "agendar_servicio"
    ESTADO_AGENDAR_FECHA = "agendar_fecha"
    ESTADO_AGENDAR_HORA = "agendar_hora"
    ESTADO_AGENDAR_CONFIRMAR = "agendar_confirmar"
    
    # Reagendar
    ESTADO_REAGENDAR_SELECCIONAR = "reagendar_seleccionar"
    ESTADO_REAGENDAR_SERVICIO = "reagendar_servicio"
    ESTADO_REAGENDAR_FECHA = "reagendar_fecha"
    ESTADO_REAGENDAR_HORA = "reagendar_hora"
    ESTADO_REAGENDAR_CONFIRMAR = "reagendar_confirmar"
    
    # Cancelar
    ESTADO_CANCELAR_SELECCIONAR = "cancelar_seleccionar"
    ESTADO_CANCELAR_CONFIRMAR = "cancelar_confirmar"
    
    # Consultar
    ESTADO_CONSULTAR = "consultar"
    
    # Horarios
    HORA_INICIO = 8  # 8:00 AM
    HORA_FIN = 17    # 5:00 PM
    HORA_ALMUERZO_INICIO = 12  # 12:00 PM
    HORA_ALMUERZO_FIN = 13     # 1:00 PM
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_conversation(self, telefono: str) -> Conversacion:
        """Obtiene o crea una conversación"""
        conv = self.db.query(Conversacion).filter(Conversacion.telefono == telefono).first()
        if not conv:
            conv = Conversacion(
                telefono=telefono,
                estado=self.ESTADO_INICIAL,
                contexto={}
            )
            self.db.add(conv)
            self.db.commit()
            self.db.refresh(conv)
        return conv
    
    def update_conversation(self, telefono: str, estado: str, contexto: dict = None):
        """Actualiza el estado de la conversación"""
        conv = self.get_or_create_conversation(telefono)
        conv.estado = estado
        if contexto:
            conv.contexto = contexto
        conv.ultima_interaccion = datetime.utcnow()
        self.db.commit()
    
    def get_or_create_patient(self, telefono: str, nombre: str = None) -> Paciente:
        """Obtiene o crea un paciente"""
        paciente = self.db.query(Paciente).filter(Paciente.telefono == telefono).first()
        if not paciente:
            paciente = Paciente(telefono=telefono, nombre=nombre)
            self.db.add(paciente)
            self.db.commit()
            self.db.refresh(paciente)
        elif nombre and not paciente.nombre:
            paciente.nombre = nombre
            self.db.commit()
        return paciente
    
    def is_valid_date(self, fecha_str: str) -> Tuple[bool, Optional[datetime]]:
        """Valida si una fecha es válida y está en el futuro"""
        try:
            # Intentar parsear diferentes formatos
            fecha = parser.parse(fecha_str, dayfirst=True)
            
            # Verificar que sea fecha futura
            if fecha.date() < datetime.now().date():
                return False, None
            
            # Verificar que sea día laboral (Lunes a Viernes)
            if fecha.weekday() >= 5:  # 5=Sábado, 6=Domingo
                return False, None
            
            return True, fecha
        except:
            return False, None
    
    def is_valid_time(self, hora_str: str) -> Tuple[bool, Optional[time]]:
        """Valida si una hora es válida (8:00 - 17:00, excluyendo 12:00-13:00)"""
        try:
            # Parsear hora
            hora = parser.parse(hora_str).time()
            
            # Verificar horario de atención (8:00 - 17:00)
            if hora.hour < self.HORA_INICIO or hora.hour >= self.HORA_FIN:
                return False, None
            
            # Verificar hora de almuerzo (12:00 - 13:00)
            if hora.hour >= self.HORA_ALMUERZO_INICIO and hora.hour < self.HORA_ALMUERZO_FIN:
                return False, None
            
            # Verificar que sea en punto o media hora
            if hora.minute not in [0, 30]:
                return False, None
            
            return True, hora
        except:
            return False, None
    
    def get_servicios_por_categoria(self) -> Dict[str, List[Servicio]]:
        """Obtiene servicios agrupados por categoría"""
        servicios = self.db.query(Servicio).filter(Servicio.activo == "true").order_by(Servicio.categoria, Servicio.nombre).all()
        
        categorias = {}
        for servicio in servicios:
            if servicio.categoria not in categorias:
                categorias[servicio.categoria] = []
            categorias[servicio.categoria].append(servicio)
        
        return categorias
    
    def get_servicio_by_id(self, servicio_id: int) -> Optional[Servicio]:
        """Obtiene un servicio por ID"""
        return self.db.query(Servicio).filter(Servicio.id == servicio_id, Servicio.activo == "true").first()
    
    def is_slot_available(self, fecha_hora: datetime, duracion_minutos: int) -> Tuple[bool, Optional[int]]:
        """
        Verifica si hay al menos un doctor disponible para el horario
        Retorna (disponible, doctor_id)
        """
        doctores = self.db.query(Doctor).filter(Doctor.activo == "true").all()
        
        for doctor in doctores:
            # Verificar si el doctor tiene alguna cita que se solape
            citas_doctor = self.db.query(Cita).filter(
                Cita.doctor_id == doctor.id,
                Cita.estado == "agendada",
                Cita.fecha_hora < fecha_hora + timedelta(minutes=duracion_minutos),
                Cita.fecha_hora >= fecha_hora - timedelta(hours=2)  # Buscar en ventana de 2 horas
            ).all()
            
            # Verificar solapamiento
            disponible = True
            for cita in citas_doctor:
                fin_cita_existente = cita.fecha_hora + timedelta(minutes=cita.servicio.duracion_minutos)
                fin_nueva_cita = fecha_hora + timedelta(minutes=duracion_minutos)
                
                # Hay solapamiento si:
                # - La nueva cita empieza antes de que termine la existente Y
                # - La nueva cita termina después de que empiece la existente
                if fecha_hora < fin_cita_existente and fin_nueva_cita > cita.fecha_hora:
                    disponible = False
                    break
            
            if disponible:
                return True, doctor.id
        
        return False, None
    
    def get_available_slots(self, fecha: datetime, duracion_minutos: int, limit: int = 5) -> List[str]:
        """Obtiene horarios disponibles para una fecha y duración específica"""
        slots = []
        hora_inicio = datetime.combine(fecha.date(), time(hour=self.HORA_INICIO))
        hora_fin = datetime.combine(fecha.date(), time(hour=self.HORA_FIN))
        
        current = hora_inicio
        while current < hora_fin and len(slots) < limit:
            # Saltar hora de almuerzo
            if current.hour >= self.HORA_ALMUERZO_INICIO and current.hour < self.HORA_ALMUERZO_FIN:
                current += timedelta(minutes=30)
                continue
            
            # Verificar que la cita no se extienda más allá del horario de cierre
            fin_cita = current + timedelta(minutes=duracion_minutos)
            if fin_cita.hour > self.HORA_FIN or (fin_cita.hour == self.HORA_FIN and fin_cita.minute > 0):
                current += timedelta(minutes=30)
                continue
            
            # Verificar que la cita no se solape con hora de almuerzo
            if current.hour < self.HORA_ALMUERZO_INICIO and fin_cita.hour >= self.HORA_ALMUERZO_INICIO:
                current += timedelta(minutes=30)
                continue
            
            disponible, _ = self.is_slot_available(current, duracion_minutos)
            if disponible:
                slots.append(current.strftime("%H:%M"))
            
            current += timedelta(minutes=30)
        
        return slots
    
    def get_patient_appointments(self, telefono: str, solo_futuras: bool = True) -> List[Cita]:
        """Obtiene las citas de un paciente"""
        paciente = self.db.query(Paciente).filter(Paciente.telefono == telefono).first()
        if not paciente:
            return []
        
        query = self.db.query(Cita).filter(
            Cita.paciente_id == paciente.id,
            Cita.estado == "agendada"
        )
        
        if solo_futuras:
            query = query.filter(Cita.fecha_hora >= datetime.now())
        
        return query.order_by(Cita.fecha_hora).all()
    
    def format_appointment(self, cita: Cita) -> str:
        """Formatea una cita para mostrar"""
        doctor = self.db.query(Doctor).filter(Doctor.id == cita.doctor_id).first()
        servicio = self.db.query(Servicio).filter(Servicio.id == cita.servicio_id).first()
        
        return f"""📅 {cita.fecha_hora.strftime('%d/%m/%Y')} a las {cita.fecha_hora.strftime('%H:%M')}
👨‍⚕️ Doctor: {doctor.nombre if doctor else 'N/A'}
💼 Servicio: {servicio.nombre if servicio else 'N/A'} ({servicio.duracion_minutos if servicio else 0} min)"""
    
    def process_message(self, telefono: str, mensaje: str) -> str:
        """Procesa un mensaje y retorna la respuesta"""
        conv = self.get_or_create_conversation(telefono)
        mensaje = mensaje.strip().lower()
        
        # Estado inicial o menú
        if conv.estado in [self.ESTADO_INICIAL, self.ESTADO_MENU]:
            return self.handle_menu(telefono, mensaje)
        
        # Flujo de agendar
        elif conv.estado == self.ESTADO_AGENDAR_NOMBRE:
            return self.handle_agendar_nombre(telefono, mensaje)
        elif conv.estado == self.ESTADO_AGENDAR_SERVICIO:
            return self.handle_agendar_servicio(telefono, mensaje)
        elif conv.estado == self.ESTADO_AGENDAR_FECHA:
            return self.handle_agendar_fecha(telefono, mensaje)
        elif conv.estado == self.ESTADO_AGENDAR_HORA:
            return self.handle_agendar_hora(telefono, mensaje)
        elif conv.estado == self.ESTADO_AGENDAR_CONFIRMAR:
            return self.handle_agendar_confirmar(telefono, mensaje)
        
        # Flujo de reagendar
        elif conv.estado == self.ESTADO_REAGENDAR_SELECCIONAR:
            return self.handle_reagendar_seleccionar(telefono, mensaje)
        elif conv.estado == self.ESTADO_REAGENDAR_SERVICIO:
            return self.handle_reagendar_servicio(telefono, mensaje)
        elif conv.estado == self.ESTADO_REAGENDAR_FECHA:
            return self.handle_reagendar_fecha(telefono, mensaje)
        elif conv.estado == self.ESTADO_REAGENDAR_HORA:
            return self.handle_reagendar_hora(telefono, mensaje)
        elif conv.estado == self.ESTADO_REAGENDAR_CONFIRMAR:
            return self.handle_reagendar_confirmar(telefono, mensaje)
        
        # Flujo de cancelar
        elif conv.estado == self.ESTADO_CANCELAR_SELECCIONAR:
            return self.handle_cancelar_seleccionar(telefono, mensaje)
        elif conv.estado == self.ESTADO_CANCELAR_CONFIRMAR:
            return self.handle_cancelar_confirmar(telefono, mensaje)
        
        # Flujo de consultar
        elif conv.estado == self.ESTADO_CONSULTAR:
            return self.handle_consultar(telefono, mensaje)
        
        return self.show_menu(telefono)
    
    def show_menu(self, telefono: str) -> str:
        """Muestra el menú principal"""
        paciente = self.db.query(Paciente).filter(Paciente.telefono == telefono).first()
        nombre = f" {paciente.nombre}" if paciente and paciente.nombre else ""
        
        self.update_conversation(telefono, self.ESTADO_MENU, {})
        
        return f"""¡Hola{nombre}! 👋 Bienvenido a la Clínica Dental Sonrisa.

¿En qué puedo ayudarte hoy?

1️⃣ Agendar una cita
2️⃣ Reagendar una cita
3️⃣ Cancelar una cita
4️⃣ Consultar mis citas

Por favor, responde con el número de la opción que deseas."""
    
    def handle_menu(self, telefono: str, mensaje: str) -> str:
        """Maneja la selección del menú"""
        if "1" in mensaje or "agendar" in mensaje:
            paciente = self.db.query(Paciente).filter(Paciente.telefono == telefono).first()
            if paciente and paciente.nombre:
                return self.show_servicios(telefono)
            else:
                self.update_conversation(telefono, self.ESTADO_AGENDAR_NOMBRE, {})
                return "Perfecto, vamos a agendar tu cita. 📅\n\nPrimero, ¿cuál es tu nombre completo?"
        
        elif "2" in mensaje or "reagendar" in mensaje:
            citas = self.get_patient_appointments(telefono)
            if not citas:
                return "No tienes citas agendadas para reagendar. 😔\n\n" + self.show_menu(telefono)
            
            self.update_conversation(telefono, self.ESTADO_REAGENDAR_SELECCIONAR, {})
            respuesta = "Estas son tus citas agendadas:\n\n"
            for i, cita in enumerate(citas, 1):
                respuesta += f"{i}. {self.format_appointment(cita)}\n\n"
            respuesta += "¿Cuál cita deseas reagendar? Responde con el número."
            return respuesta
        
        elif "3" in mensaje or "cancelar" in mensaje:
            citas = self.get_patient_appointments(telefono)
            if not citas:
                return "No tienes citas agendadas para cancelar. 😔\n\n" + self.show_menu(telefono)
            
            self.update_conversation(telefono, self.ESTADO_CANCELAR_SELECCIONAR, {})
            respuesta = "Estas son tus citas agendadas:\n\n"
            for i, cita in enumerate(citas, 1):
                respuesta += f"{i}. {self.format_appointment(cita)}\n\n"
            respuesta += "¿Cuál cita deseas cancelar? Responde con el número."
            return respuesta
        
        elif "4" in mensaje or "consultar" in mensaje:
            return self.handle_consultar(telefono, mensaje)
        
        else:
            return "No entendí tu respuesta. Por favor, elige una opción del 1 al 4."
    
    def show_servicios(self, telefono: str) -> str:
        """Muestra el catálogo de servicios"""
        categorias = self.get_servicios_por_categoria()
        
        respuesta = "Perfecto! Selecciona el servicio que necesitas:\n\n"
        
        contador = 1
        servicios_map = {}
        
        for categoria, servicios in categorias.items():
            respuesta += f"📋 {categoria}:\n"
            for servicio in servicios:
                respuesta += f"{contador}. {servicio.nombre} ({servicio.duracion_minutos} min)\n"
                servicios_map[contador] = servicio.id
                contador += 1
            respuesta += "\n"
        
        respuesta += "Responde con el número del servicio que deseas."
        
        self.update_conversation(telefono, self.ESTADO_AGENDAR_SERVICIO, {"servicios_map": servicios_map})
        return respuesta
    
    # === FLUJO AGENDAR ===
    def handle_agendar_nombre(self, telefono: str, mensaje: str) -> str:
        """Maneja el nombre en el flujo de agendar"""
        if len(mensaje) < 3:
            return "Por favor, ingresa tu nombre completo (mínimo 3 caracteres)."
        
        # Guardar nombre
        self.get_or_create_patient(telefono, mensaje.title())
        
        return self.show_servicios(telefono)
    
    def handle_agendar_servicio(self, telefono: str, mensaje: str) -> str:
        """Maneja la selección de servicio en el flujo de agendar"""
        try:
            numero = int(mensaje)
            conv = self.get_or_create_conversation(telefono)
            contexto = conv.contexto or {}
            servicios_map = contexto.get("servicios_map", {})
            
            # Convertir keys de string a int
            servicios_map = {int(k): v for k, v in servicios_map.items()}
            
            if numero not in servicios_map:
                return "Número inválido. Por favor, elige un número de la lista."
            
            servicio_id = servicios_map[numero]
            servicio = self.get_servicio_by_id(servicio_id)
            
            if not servicio:
                return "Servicio no encontrado. Por favor, intenta nuevamente."
            
            contexto["servicio_id"] = servicio_id
            contexto["duracion_minutos"] = servicio.duracion_minutos
            self.update_conversation(telefono, self.ESTADO_AGENDAR_FECHA, contexto)
            
            return f"Excelente! Has seleccionado: {servicio.nombre} ({servicio.duracion_minutos} min)\n\n¿Qué día te gustaría venir? Por favor indica la fecha en formato DD/MM/AAAA (ejemplo: 25/02/2026).\n\nRecuerda que atendemos de Lunes a Viernes."
        
        except ValueError:
            return "Por favor, responde con el número del servicio."
    
    def handle_agendar_fecha(self, telefono: str, mensaje: str) -> str:
        """Maneja la fecha en el flujo de agendar"""
        valida, fecha = self.is_valid_date(mensaje)
        
        if not valida:
            return "❌ Fecha inválida. Por favor verifica:\n\n• Usa formato DD/MM/AAAA\n• La fecha debe ser futura\n• Solo atendemos Lunes a Viernes\n\nIntenta nuevamente."
        
        conv = self.get_or_create_conversation(telefono)
        contexto = conv.contexto or {}
        duracion = contexto.get("duracion_minutos", 30)
        
        # Verificar horarios disponibles
        slots = self.get_available_slots(fecha, duracion)
        if not slots:
            return f"😔 Lo siento, no hay horarios disponibles para el {fecha.strftime('%d/%m/%Y')}.\n\nPor favor, elige otra fecha."
        
        contexto["fecha"] = fecha.isoformat()
        self.update_conversation(telefono, self.ESTADO_AGENDAR_HORA, contexto)
        
        respuesta = f"Perfecto! Para el {fecha.strftime('%d/%m/%Y')} tenemos disponibles:\n\n"
        for slot in slots:
            respuesta += f"• {slot}\n"
        respuesta += "\n¿A qué hora prefieres? (formato HH:MM, ejemplo: 14:30)\n\n⏰ Horario: 8:00 - 17:00 (Almuerzo: 12:00 - 13:00)"
        
        return respuesta
    
    def handle_agendar_hora(self, telefono: str, mensaje: str) -> str:
        """Maneja la hora en el flujo de agendar"""
        valida, hora = self.is_valid_time(mensaje)
        
        if not valida:
            return "❌ Hora inválida. Por favor verifica:\n\n• Usa formato HH:MM\n• Horario: 8:00 a 17:00\n• Almuerzo: 12:00 a 13:00 (no disponible)\n• Solo en punto o media hora (ej: 10:00, 10:30)\n\nIntenta nuevamente."
        
        conv = self.get_or_create_conversation(telefono)
        contexto = conv.contexto
        fecha = parser.parse(contexto["fecha"])
        fecha_hora = datetime.combine(fecha.date(), hora)
        duracion = contexto.get("duracion_minutos", 30)
        
        # Verificar disponibilidad
        disponible, doctor_id = self.is_slot_available(fecha_hora, duracion)
        if not disponible:
            slots = self.get_available_slots(fecha, duracion)
            if not slots:
                return "😔 Ese horario ya no está disponible y no quedan más espacios ese día.\n\nPor favor, elige otra fecha."
            
            respuesta = "😔 Ese horario ya está ocupado. Horarios disponibles:\n\n"
            for slot in slots:
                respuesta += f"• {slot}\n"
            respuesta += "\n¿Cuál prefieres?"
            return respuesta
        
        contexto["hora"] = hora.isoformat()
        contexto["fecha_hora"] = fecha_hora.isoformat()
        contexto["doctor_id"] = doctor_id
        self.update_conversation(telefono, self.ESTADO_AGENDAR_CONFIRMAR, contexto)
        
        servicio = self.get_servicio_by_id(contexto["servicio_id"])
        doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        
        return f"""Perfecto! Por favor confirma los datos de tu cita:

📅 Fecha: {fecha_hora.strftime('%d/%m/%Y')}
🕐 Hora: {fecha_hora.strftime('%H:%M')}
💼 Servicio: {servicio.nombre} ({servicio.duracion_minutos} min)
👨‍⚕️ Doctor: {doctor.nombre}

¿Es correcto? Responde SÍ para confirmar o NO para cancelar."""
    
    def handle_agendar_confirmar(self, telefono: str, mensaje: str) -> str:
        """Maneja la confirmación en el flujo de agendar"""
        if "si" in mensaje or "sí" in mensaje or "confirmar" in mensaje:
            conv = self.get_or_create_conversation(telefono)
            contexto = conv.contexto
            
            paciente = self.get_or_create_patient(telefono)
            fecha_hora = parser.parse(contexto["fecha_hora"])
            duracion = contexto.get("duracion_minutos", 30)
            
            # Verificar disponibilidad nuevamente
            disponible, doctor_id = self.is_slot_available(fecha_hora, duracion)
            if not disponible:
                self.update_conversation(telefono, self.ESTADO_MENU, {})
                return "😔 Lo siento, ese horario acaba de ser ocupado.\n\n" + self.show_menu(telefono)
            
            # Crear cita
            cita = Cita(
                paciente_id=paciente.id,
                doctor_id=doctor_id,
                servicio_id=contexto["servicio_id"],
                fecha_hora=fecha_hora,
                estado="agendada"
            )
            self.db.add(cita)
            self.db.commit()
            self.db.refresh(cita)
            
            self.update_conversation(telefono, self.ESTADO_MENU, {})
            
            servicio = self.get_servicio_by_id(contexto["servicio_id"])
            doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
            
            return f"""✅ ¡Cita agendada exitosamente!

📅 {fecha_hora.strftime('%d/%m/%Y')} a las {fecha_hora.strftime('%H:%M')}
💼 {servicio.nombre} ({servicio.duracion_minutos} min)
👨‍⚕️ {doctor.nombre}

Te esperamos! Si necesitas reagendar o cancelar, escríbeme cuando quieras.

{self.show_menu(telefono)}"""
        
        else:
            self.update_conversation(telefono, self.ESTADO_MENU, {})
            return "Cita cancelada. No hay problema! 😊\n\n" + self.show_menu(telefono)
    
    # === FLUJO REAGENDAR ===
    def handle_reagendar_seleccionar(self, telefono: str, mensaje: str) -> str:
        """Maneja la selección de cita para reagendar"""
        try:
            indice = int(mensaje) - 1
            citas = self.get_patient_appointments(telefono)
            
            if indice < 0 or indice >= len(citas):
                return "Número inválido. Por favor, elige un número de la lista."
            
            cita = citas[indice]
            contexto = {"cita_id": cita.id}
            self.update_conversation(telefono, self.ESTADO_REAGENDAR_SERVICIO, contexto)
            
            return f"Vas a reagendar esta cita:\n\n{self.format_appointment(cita)}\n\n¿Deseas cambiar el servicio?\n\n1. Mantener el mismo servicio\n2. Cambiar servicio\n\nResponde 1 o 2."
        
        except ValueError:
            return "Por favor, responde con el número de la cita."
    
    def handle_reagendar_servicio(self, telefono: str, mensaje: str) -> str:
        """Maneja si se cambia el servicio al reagendar"""
        conv = self.get_or_create_conversation(telefono)
        contexto = conv.contexto
        cita = self.db.query(Cita).filter(Cita.id == contexto["cita_id"]).first()
        
        if "1" in mensaje or "mantener" in mensaje or "mismo" in mensaje:
            # Mantener el mismo servicio
            contexto["servicio_id"] = cita.servicio_id
            contexto["duracion_minutos"] = cita.servicio.duracion_minutos
            self.update_conversation(telefono, self.ESTADO_REAGENDAR_FECHA, contexto)
            
            return f"Perfecto, mantendremos el servicio: {cita.servicio.nombre}\n\n¿Para qué nueva fecha? (formato DD/MM/AAAA)\n\nRecuerda que atendemos de Lunes a Viernes."
        
        elif "2" in mensaje or "cambiar" in mensaje:
            # Cambiar servicio
            return self.show_servicios_reagendar(telefono)
        
        else:
            return "Por favor, responde 1 para mantener el servicio o 2 para cambiarlo."
    
    def show_servicios_reagendar(self, telefono: str) -> str:
        """Muestra servicios para reagendar"""
        categorias = self.get_servicios_por_categoria()
        
        respuesta = "Selecciona el nuevo servicio:\n\n"
        
        contador = 1
        servicios_map = {}
        
        for categoria, servicios in categorias.items():
            respuesta += f"📋 {categoria}:\n"
            for servicio in servicios:
                respuesta += f"{contador}. {servicio.nombre} ({servicio.duracion_minutos} min)\n"
                servicios_map[contador] = servicio.id
                contador += 1
            respuesta += "\n"
        
        respuesta += "Responde con el número del servicio."
        
        conv = self.get_or_create_conversation(telefono)
        contexto = conv.contexto
        contexto["servicios_map"] = servicios_map
        contexto["cambiar_servicio"] = True
        self.update_conversation(telefono, self.ESTADO_REAGENDAR_SERVICIO, contexto)
        
        return respuesta
    
    def handle_reagendar_fecha(self, telefono: str, mensaje: str) -> str:
        """Maneja la nueva fecha en el flujo de reagendar"""
        conv = self.get_or_create_conversation(telefono)
        contexto = conv.contexto
        
        # Si está en modo de cambiar servicio, primero procesar la selección
        if contexto.get("cambiar_servicio"):
            try:
                numero = int(mensaje)
                servicios_map = contexto.get("servicios_map", {})
                servicios_map = {int(k): v for k, v in servicios_map.items()}
                
                if numero not in servicios_map:
                    return "Número inválido. Por favor, elige un número de la lista."
                
                servicio_id = servicios_map[numero]
                servicio = self.get_servicio_by_id(servicio_id)
                
                if not servicio:
                    return "Servicio no encontrado. Por favor, intenta nuevamente."
                
                contexto["servicio_id"] = servicio_id
                contexto["duracion_minutos"] = servicio.duracion_minutos
                contexto["cambiar_servicio"] = False
                self.update_conversation(telefono, self.ESTADO_REAGENDAR_FECHA, contexto)
                
                return f"Excelente! Nuevo servicio: {servicio.nombre}\n\n¿Para qué fecha? (formato DD/MM/AAAA)\n\nRecuerda que atendemos de Lunes a Viernes."
            
            except ValueError:
                return "Por favor, responde con el número del servicio."
        
        # Procesar fecha
        valida, fecha = self.is_valid_date(mensaje)
        
        if not valida:
            return "❌ Fecha inválida. Por favor verifica:\n\n• Usa formato DD/MM/AAAA\n• La fecha debe ser futura\n• Solo atendemos Lunes a Viernes\n\nIntenta nuevamente."
        
        duracion = contexto.get("duracion_minutos", 30)
        slots = self.get_available_slots(fecha, duracion)
        if not slots:
            return f"😔 No hay horarios disponibles para el {fecha.strftime('%d/%m/%Y')}.\n\nPor favor, elige otra fecha."
        
        contexto["nueva_fecha"] = fecha.isoformat()
        self.update_conversation(telefono, self.ESTADO_REAGENDAR_HORA, contexto)
        
        respuesta = f"Para el {fecha.strftime('%d/%m/%Y')} tenemos:\n\n"
        for slot in slots:
            respuesta += f"• {slot}\n"
        respuesta += "\n¿A qué hora? (formato HH:MM)\n\n⏰ Horario: 8:00 - 17:00 (Almuerzo: 12:00 - 13:00)"
        
        return respuesta
    
    def handle_reagendar_hora(self, telefono: str, mensaje: str) -> str:
        """Maneja la nueva hora en el flujo de reagendar"""
        valida, hora = self.is_valid_time(mensaje)
        
        if not valida:
            return "❌ Hora inválida. Por favor verifica:\n\n• Usa formato HH:MM\n• Horario: 8:00 a 17:00\n• Almuerzo: 12:00 a 13:00 (no disponible)\n• Solo en punto o media hora\n\nIntenta nuevamente."
        
        conv = self.get_or_create_conversation(telefono)
        contexto = conv.contexto
        fecha = parser.parse(contexto["nueva_fecha"])
        fecha_hora = datetime.combine(fecha.date(), hora)
        duracion = contexto.get("duracion_minutos", 30)
        
        disponible, doctor_id = self.is_slot_available(fecha_hora, duracion)
        if not disponible:
            slots = self.get_available_slots(fecha, duracion)
            if not slots:
                return "😔 Ese horario ya no está disponible y no quedan más espacios.\n\nPor favor, elige otra fecha."
            
            respuesta = "😔 Ese horario ya está ocupado. Disponibles:\n\n"
            for slot in slots:
                respuesta += f"• {slot}\n"
            return respuesta
        
        contexto["nueva_fecha_hora"] = fecha_hora.isoformat()
        contexto["nuevo_doctor_id"] = doctor_id
        self.update_conversation(telefono, self.ESTADO_REAGENDAR_CONFIRMAR, contexto)
        
        cita_actual = self.db.query(Cita).filter(Cita.id == contexto["cita_id"]).first()
        nuevo_servicio = self.get_servicio_by_id(contexto["servicio_id"])
        nuevo_doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        
        return f"""Confirma el cambio:

CITA ACTUAL:
{self.format_appointment(cita_actual)}

NUEVA CITA:
📅 {fecha_hora.strftime('%d/%m/%Y')} a las {fecha_hora.strftime('%H:%M')}
💼 {nuevo_servicio.nombre} ({nuevo_servicio.duracion_minutos} min)
👨‍⚕️ {nuevo_doctor.nombre}

¿Confirmas el cambio? Responde SÍ o NO."""
    
    def handle_reagendar_confirmar(self, telefono: str, mensaje: str) -> str:
        """Maneja la confirmación en el flujo de reagendar"""
        if "si" in mensaje or "sí" in mensaje or "confirmar" in mensaje:
            conv = self.get_or_create_conversation(telefono)
            contexto = conv.contexto
            
            nueva_fecha_hora = parser.parse(contexto["nueva_fecha_hora"])
            duracion = contexto.get("duracion_minutos", 30)
            
            disponible, doctor_id = self.is_slot_available(nueva_fecha_hora, duracion)
            if not disponible:
                self.update_conversation(telefono, self.ESTADO_MENU, {})
                return "😔 Ese horario acaba de ser ocupado.\n\n" + self.show_menu(telefono)
            
            cita = self.db.query(Cita).filter(Cita.id == contexto["cita_id"]).first()
            cita.fecha_hora = nueva_fecha_hora
            cita.doctor_id = doctor_id
            cita.servicio_id = contexto["servicio_id"]
            cita.estado = "agendada"
            self.db.commit()
            
            self.update_conversation(telefono, self.ESTADO_MENU, {})
            
            servicio = self.get_servicio_by_id(contexto["servicio_id"])
            doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
            
            return f"""✅ ¡Cita reagendada exitosamente!

📅 {nueva_fecha_hora.strftime('%d/%m/%Y')} a las {nueva_fecha_hora.strftime('%H:%M')}
💼 {servicio.nombre} ({servicio.duracion_minutos} min)
👨‍⚕️ {doctor.nombre}

Te esperamos! 😊

{self.show_menu(telefono)}"""
        
        else:
            self.update_conversation(telefono, self.ESTADO_MENU, {})
            return "Reagendamiento cancelado.\n\n" + self.show_menu(telefono)
    
    # === FLUJO CANCELAR ===
    def handle_cancelar_seleccionar(self, telefono: str, mensaje: str) -> str:
        """Maneja la selección de cita para cancelar"""
        try:
            indice = int(mensaje) - 1
            citas = self.get_patient_appointments(telefono)
            
            if indice < 0 or indice >= len(citas):
                return "Número inválido. Por favor, elige un número de la lista."
            
            cita = citas[indice]
            contexto = {"cita_id": cita.id}
            self.update_conversation(telefono, self.ESTADO_CANCELAR_CONFIRMAR, contexto)
            
            return f"Vas a cancelar esta cita:\n\n{self.format_appointment(cita)}\n\n¿Estás seguro? Responde SÍ para confirmar o NO para volver al menú."
        
        except ValueError:
            return "Por favor, responde con el número de la cita."
    
    def handle_cancelar_confirmar(self, telefono: str, mensaje: str) -> str:
        """Maneja la confirmación en el flujo de cancelar"""
        if "si" in mensaje or "sí" in mensaje or "confirmar" in mensaje:
            conv = self.get_or_create_conversation(telefono)
            contexto = conv.contexto
            
            cita = self.db.query(Cita).filter(Cita.id == contexto["cita_id"]).first()
            cita.estado = "cancelada"
            self.db.commit()
            
            self.update_conversation(telefono, self.ESTADO_MENU, {})
            
            return f"""✅ Cita cancelada exitosamente.

Si deseas agendar nuevamente, estoy aquí para ayudarte. 😊

{self.show_menu(telefono)}"""
        
        else:
            self.update_conversation(telefono, self.ESTADO_MENU, {})
            return "Cancelación abortada. Tu cita sigue activa.\n\n" + self.show_menu(telefono)
    
    # === FLUJO CONSULTAR ===
    def handle_consultar(self, telefono: str, mensaje: str) -> str:
        """Maneja la consulta de citas"""
        citas = self.get_patient_appointments(telefono)
        
        if not citas:
            return "No tienes citas agendadas. 📅\n\n¿Deseas agendar una?\n\n" + self.show_menu(telefono)
        
        respuesta = "📋 Tus citas agendadas:\n\n"
        for i, cita in enumerate(citas, 1):
            respuesta += f"{i}. {self.format_appointment(cita)}\n\n"
        
        respuesta += self.show_menu(telefono)
        return respuesta
