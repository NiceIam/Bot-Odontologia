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
                range=self._get_range(self.sheet_citas, 'A2:H')
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return []
            
            appointments = []
            for row in values:
                while len(row) < 8:
                    row.append('')
                
                appointments.append({
                    'id': row[0],
                    'telefono': row[1],
                    'nombre': row[2],
                    'servicio': row[3],
                    'fecha': row[4],
                    'hora': row[5],
                    'estado': row[6],
                    'notas': row[7]
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
            if apt['telefono'] == telefono and apt['estado'].lower() != 'cancelada'
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
            
            if 'fecha' in updates:
                current_row['fecha'] = updates['fecha']
            if 'hora' in updates:
                current_row['hora'] = updates['hora']
            if 'servicio' in updates:
                current_row['servicio'] = updates['servicio']
            if 'estado' in updates:
                current_row['estado'] = updates['estado']
            if 'notas' in updates:
                current_row['notas'] = updates['notas']
            
            values = [[
                current_row['id'],
                current_row['telefono'],
                current_row['nombre'],
                current_row['servicio'],
                current_row['fecha'],
                current_row['hora'],
                current_row['estado'],
                current_row['notas']
            ]]
            
            body = {'values': values}
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=self._get_range(self.sheet_citas, f'A{row_index}:H{row_index}'),
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
        return self.update_appointment(appointment_id, {'estado': 'cancelada'})
    
    def format_appointment(self, appointment: Dict) -> str:
        """Formatea una cita para mostrar al usuario"""
        return f"""📅 {appointment['fecha']} a las {appointment['hora']}
💼 Servicio: {appointment['servicio']}
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
