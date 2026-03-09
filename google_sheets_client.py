"""
Google Sheets Client para gestión de citas, conversaciones y pacientes
Fecha de creación: 28/02/2026
Propósito: Reemplazar PostgreSQL completamente como fuente de datos
"""

from datetime import datetime
from typing import Optional, List, Dict
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import get_settings

settings = get_settings()


class GoogleSheetsClient:
    """Cliente para interactuar con Google Sheets como base de datos completa"""
    
    def __init__(self):
        """Inicializa el cliente de Google Sheets con las credenciales"""
        try:
            # Cargar credenciales desde config
            credentials_dict = json.loads(settings.google_credentials)
            
            self.credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            self.service = build('sheets', 'v4', credentials=self.credentials)
            self.spreadsheet_id = settings.spreadsheet_id
            
            # Nombres de las hojas
            self.sheet_citas = settings.sheet_name  # "Citas"
            self.sheet_conversaciones = "Conversaciones"
            self.sheet_pacientes = "Pacientes"
            self.sheet_calendario = "Calendario"
            
            print(f"✅ Google Sheets Client inicializado correctamente")
            print(f"   Spreadsheet ID: {self.spreadsheet_id}")
            print(f"   Sheets: {self.sheet_citas}, {self.sheet_conversaciones}, {self.sheet_pacientes}")
            
        except Exception as e:
            print(f"❌ Error inicializando Google Sheets Client: {str(e)}")
            raise
    
    def _get_range(self, sheet_name: str, range_name: str) -> str:
        """Construye el rango completo con el nombre de la hoja"""
        return f"{sheet_name}!{range_name}"
    
    # ============================================================================
    # === GESTIÓN DE CITAS ===
    # ============================================================================
    
    def get_all_appointments(self) -> List[Dict]:
        """
        Obtiene todas las citas del Google Sheet
        
        Returns:
            Lista de diccionarios con los datos de las citas
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self._get_range(self.sheet_citas, 'A2:N')  # A-N = 14 columnas
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return []
            
            appointments = []
            for row in values:
                # Asegurar que la fila tenga suficientes columnas
                while len(row) < 14:
                    row.append('')
                
                appointments.append({
                    'id': row[0],  # ID
                    'nombre': row[1],  # Nombre
                    'email': row[2],  # Correo
                    'telefono': row[3],  # Teléfono
                    'fecha': row[4],  # Fecha
                    'hora': row[5],  # Hora
                    'estado': row[6],  # Estado
                    'accion': row[7],  # Acción
                    'servicio': row[8],  # Servicio
                    'hora_fin': row[9],  # Hora fin
                    'duracion': row[10],  # Duración
                    'doctora': row[11],  # Doctora
                    'fecha_creacion': row[12],  # FechaCreación
                    'fecha_actualizacion': row[13]  # FechaActualización
                })
            
            return appointments
            
        except HttpError as e:
            print(f"❌ Error obteniendo citas: {str(e)}")
            return []
    
    def get_appointments_by_phone(self, telefono: str) -> List[Dict]:
        """Obtiene las citas de un paciente específico por teléfono"""
        all_appointments = self.get_all_appointments()
        
        patient_appointments = [
            apt for apt in all_appointments 
            if apt['telefono'] == telefono and apt['estado'].lower() not in ['cancelada', 'atendida']
        ]
        
        return patient_appointments
    
    def get_appointments_by_id(self, cedula: str) -> List[Dict]:
        """Obtiene las citas de un paciente específico por cédula (ID)"""
        all_appointments = self.get_all_appointments()
        
        patient_appointments = [
            apt for apt in all_appointments 
            if apt['id'] == cedula and apt['estado'].lower() not in ['cancelada', 'atendida']
        ]
        
        return patient_appointments
    
    def get_appointment_by_id(self, appointment_id: str) -> Optional[Dict]:
        """Obtiene una cita específica por ID"""
        all_appointments = self.get_all_appointments()
        
        for apt in all_appointments:
            if apt['id'] == appointment_id:
                return apt
        
        return None
    
    def update_appointment(self, appointment_id: str, updates: Dict) -> bool:
        """Actualiza una cita existente"""
        try:
            all_appointments = self.get_all_appointments()
            
            row_index = None
            for i, apt in enumerate(all_appointments):
                if apt['id'] == appointment_id:
                    row_index = i + 2
                    break
            
            if row_index is None:
                print(f"❌ Cita con ID {appointment_id} no encontrada")
                return False
            
            current_row = all_appointments[row_index - 2]
            
            # Aplicar actualizaciones
            if 'fecha' in updates:
                current_row['fecha'] = updates['fecha']
            if 'hora' in updates:
                current_row['hora'] = updates['hora']
            if 'servicio' in updates:
                current_row['servicio'] = updates['servicio']
            if 'estado' in updates:
                current_row['estado'] = updates['estado']
            if 'hora_fin' in updates:
                current_row['hora_fin'] = updates['hora_fin']
            
            # Actualizar fecha de actualización
            current_row['fecha_actualizacion'] = datetime.utcnow().isoformat()
            
            # Preparar valores para actualizar
            values = [[
                current_row['id'],
                current_row['nombre'],
                current_row['email'],
                current_row['telefono'],
                current_row['fecha'],
                current_row['hora'],
                current_row['estado'],
                current_row['accion'],
                current_row['servicio'],
                current_row['hora_fin'],
                current_row['duracion'],
                current_row['doctora'],
                current_row['fecha_creacion'],
                current_row['fecha_actualizacion']
            ]]
            
            body = {'values': values}
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=self._get_range(self.sheet_citas, f'A{row_index}:N{row_index}'),
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ Cita {appointment_id} actualizada correctamente")
            return True
            
        except HttpError as e:
            print(f"❌ Error actualizando cita: {str(e)}")
            return False
    
    def cancel_appointment(self, appointment_id: str) -> bool:
        """Marca una cita como cancelada (NO la elimina)"""
        return self.update_appointment(appointment_id, {'estado': 'Cancelada'})
    
    def format_appointment(self, appointment: Dict) -> str:
        """Formatea una cita para mostrar al usuario"""
        return f"""📅 {appointment['fecha']} a las {appointment['hora']}
💼 Servicio: {appointment['servicio']}
👩‍⚕️ Doctora: {appointment['doctora']}
📝 Estado: {appointment['estado']}"""
    
    # ============================================================================
    # === GESTIÓN DE CONVERSACIONES ===
    # ============================================================================
    
    def get_conversation(self, telefono: str) -> Optional[Dict]:
        """Obtiene la conversación de un usuario"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self._get_range(self.sheet_conversaciones, 'A2:F')
            ).execute()
            
            values = result.get('values', [])
            
            for row in values:
                while len(row) < 6:
                    row.append('')
                
                if row[0] == telefono:
                    return {
                        'telefono': row[0],
                        'estado': row[1],
                        'contexto': json.loads(row[2]) if row[2] else {},
                        'modo_humano': row[3],
                        'fecha_modo_humano': row[4],
                        'ultima_interaccion': row[5]
                    }
            
            return None
            
        except HttpError as e:
            print(f"❌ Error obteniendo conversación: {str(e)}")
            return None
    
    def create_or_update_conversation(self, telefono: str, estado: str, contexto: Dict = None, modo_humano: str = "false") -> bool:
        """Crea o actualiza una conversación"""
        try:
            # Buscar si existe
            existing = self.get_conversation(telefono)
            
            contexto_json = json.dumps(contexto if contexto else {})
            ultima_interaccion = datetime.utcnow().isoformat()
            
            if existing:
                # Actualizar existente
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=self._get_range(self.sheet_conversaciones, 'A2:F')
                ).execute()
                
                values = result.get('values', [])
                row_index = None
                
                for i, row in enumerate(values):
                    if row[0] == telefono:
                        row_index = i + 2
                        break
                
                if row_index:
                    fecha_modo_humano = existing.get('fecha_modo_humano', '')
                    if modo_humano == "true" and existing.get('modo_humano') != "true":
                        fecha_modo_humano = ultima_interaccion
                    
                    values = [[telefono, estado, contexto_json, modo_humano, fecha_modo_humano, ultima_interaccion]]
                    
                    body = {'values': values}
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=self._get_range(self.sheet_conversaciones, f'A{row_index}:F{row_index}'),
                        valueInputOption='RAW',
                        body=body
                    ).execute()
            else:
                # Crear nueva
                values = [[telefono, estado, contexto_json, modo_humano, '', ultima_interaccion]]
                
                body = {'values': values}
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=self._get_range(self.sheet_conversaciones, 'A2:F'),
                    valueInputOption='RAW',
                    body=body
                ).execute()
            
            return True
            
        except HttpError as e:
            print(f"❌ Error creando/actualizando conversación: {str(e)}")
            return False
    
    def is_human_mode_active(self, telefono: str) -> bool:
        """Verifica si el modo humano está activo"""
        conv = self.get_conversation(telefono)
        if not conv:
            return False
        
        modo = conv.get('modo_humano', 'false')
        return modo.lower() in ["true", "1", "yes"]
    
    def activate_human_mode(self, telefono: str) -> bool:
        """Activa el modo humano"""
        conv = self.get_conversation(telefono)
        estado = conv['estado'] if conv else 'inicial'
        contexto = conv['contexto'] if conv else {}
        
        return self.create_or_update_conversation(telefono, estado, contexto, modo_humano="true")
    
    def deactivate_human_mode(self, telefono: str) -> bool:
        """Desactiva el modo humano"""
        conv = self.get_conversation(telefono)
        contexto = conv['contexto'] if conv else {}
        
        return self.create_or_update_conversation(telefono, 'menu', contexto, modo_humano="false")
    
    # ============================================================================
    # === GESTIÓN DE PACIENTES ===
    # ============================================================================
    
    def get_patient(self, telefono: str) -> Optional[Dict]:
        """Obtiene un paciente por teléfono"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self._get_range(self.sheet_pacientes, 'A2:E')
            ).execute()
            
            values = result.get('values', [])
            
            for row in values:
                while len(row) < 5:
                    row.append('')
                
                if row[0] == telefono:
                    return {
                        'telefono': row[0],
                        'nombre': row[1],
                        'email': row[2],
                        'fecha_nacimiento': row[3],
                        'created_at': row[4]
                    }
            
            return None
            
        except HttpError as e:
            print(f"❌ Error obteniendo paciente: {str(e)}")
            return None
    
    def create_or_update_patient(self, telefono: str, nombre: str = None, email: str = None, fecha_nacimiento: str = None) -> bool:
        """Crea o actualiza un paciente"""
        try:
            existing = self.get_patient(telefono)
            
            if existing:
                # Actualizar solo si hay nuevos datos
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=self._get_range(self.sheet_pacientes, 'A2:E')
                ).execute()
                
                values = result.get('values', [])
                row_index = None
                
                for i, row in enumerate(values):
                    if row[0] == telefono:
                        row_index = i + 2
                        break
                
                if row_index:
                    nombre_final = nombre if nombre else existing.get('nombre', '')
                    email_final = email if email else existing.get('email', '')
                    fecha_nac_final = fecha_nacimiento if fecha_nacimiento else existing.get('fecha_nacimiento', '')
                    created_at = existing.get('created_at', datetime.utcnow().isoformat())
                    
                    values = [[telefono, nombre_final, email_final, fecha_nac_final, created_at]]
                    
                    body = {'values': values}
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=self._get_range(self.sheet_pacientes, f'A{row_index}:E{row_index}'),
                        valueInputOption='RAW',
                        body=body
                    ).execute()
            else:
                # Crear nuevo
                created_at = datetime.utcnow().isoformat()
                values = [[telefono, nombre or '', email or '', fecha_nacimiento or '', created_at]]
                
                body = {'values': values}
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=self._get_range(self.sheet_pacientes, 'A2:E'),
                    valueInputOption='RAW',
                    body=body
                ).execute()
            
            return True
            
        except HttpError as e:
            print(f"❌ Error creando/actualizando paciente: {str(e)}")
            return False
    
    # ============================================================================
    # === GESTIÓN DE CALENDARIO ===
    # ============================================================================
    
    def get_next_working_days(self, limit: int = 8) -> List[Dict]:
        """
        Obtiene los próximos días laborales desde el sheet Calendario
        
        Args:
            limit: Número de días laborales a retornar (default: 8)
            
        Returns:
            Lista de diccionarios con fecha, dia_semana, es_laborable
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self._get_range(self.sheet_calendario, 'A2:D')
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return []
            
            today = datetime.now().date()
            working_days = []
            
            for row in values:
                while len(row) < 4:
                    row.append('')
                
                fecha_str = row[0]  # fecha
                dia_semana = row[1]  # dia_semana
                es_laborable = row[2]  # es_laborable
                festivo = row[3]  # festivo
                
                # Parsear fecha
                try:
                    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                except:
                    continue
                
                # Solo fechas futuras
                if fecha <= today:
                    continue
                
                # Excluir sábados (no se puede reagendar los sábados)
                if fecha.weekday() == 5:  # 5 = Sábado
                    continue
                
                # Solo días laborables (es_laborable = TRUE)
                if es_laborable.upper() == 'TRUE':
                    working_days.append({
                        'fecha': fecha_str,
                        'fecha_obj': fecha,
                        'dia_semana': dia_semana,
                        'es_laborable': es_laborable,
                        'festivo': festivo
                    })
                    
                    if len(working_days) >= limit:
                        break
            
            return working_days
            
        except HttpError as e:
            print(f"❌ Error obteniendo días laborales: {str(e)}")
            return []
    
    def get_available_hours_for_date(self, fecha_str: str, doctora: str = None) -> List[str]:
        """
        Obtiene las horas disponibles para una fecha específica
        
        Args:
            fecha_str: Fecha en formato YYYY-MM-DD
            doctora: Nombre de la doctora (opcional: "Sandra" o "Zaida")
            
        Returns:
            Lista de horas disponibles en formato HH:MM
        """
        try:
            # Parsear fecha
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
            dia_semana = fecha.strftime('%A')  # Monday, Tuesday, etc.
            dia_numero = fecha.weekday()  # 0=Monday, 1=Tuesday, etc.
            
            # Determinar horarios según día de la semana
            if dia_semana == 'Saturday':
                # Sábados: 8:00 - 12:00 (última cita 11:30)
                horas = []
                for hora in range(8, 12):
                    horas.append(f"{hora:02d}:00")
                    horas.append(f"{hora:02d}:30")
                return horas
            
            # Lunes a Viernes: 8:00 - 12:00 y 14:00 - 17:00
            horas = []
            
            # Mañana: 8:00 - 12:00 (última cita 11:30)
            for hora in range(8, 12):
                horas.append(f"{hora:02d}:00")
                horas.append(f"{hora:02d}:30")
            
            # Tarde: 14:00 - 17:00+
            # Determinar última hora según doctora y día
            ultima_hora = "17:00"  # Por defecto
            
            if doctora:
                doctora_lower = doctora.lower()
                if doctora_lower == "sandra":
                    # Doctora Sandra
                    if dia_numero in [0, 1, 2]:  # Lunes, Martes, Miércoles
                        # Sale a las 17:00, última cita 16:30
                        ultima_hora = "16:30"
                    else:  # Jueves, Viernes
                        # Sale a las 17:30, última cita 17:00
                        ultima_hora = "17:00"
                elif doctora_lower == "zaida":
                    # Doctora Zaida: sale a las 17:30, última cita 17:00
                    ultima_hora = "17:00"
            
            # Agregar horarios de tarde hasta la última hora permitida
            for hora in range(14, 18):
                hora_str = f"{hora:02d}:00"
                if hora_str <= ultima_hora:
                    horas.append(hora_str)
                
                hora_media_str = f"{hora:02d}:30"
                if hora_media_str <= ultima_hora:
                    horas.append(hora_media_str)
            
            return horas
            
        except Exception as e:
            print(f"❌ Error obteniendo horas disponibles: {str(e)}")
            return []


# Instancia global del cliente
_sheets_client = None


def get_sheets_client() -> GoogleSheetsClient:
    """
    Obtiene la instancia global del cliente de Google Sheets
    
    Returns:
        Instancia de GoogleSheetsClient
    """
    global _sheets_client
    if _sheets_client is None:
        _sheets_client = GoogleSheetsClient()
    return _sheets_client
