"""
Google Sheets Client para gestión de citas
Fecha de creación: 28/02/2026
Propósito: Reemplazar PostgreSQL como fuente de datos para citas
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
    """Cliente para interactuar con Google Sheets como base de datos de citas"""
    
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
            self.sheet_name = settings.sheet_name
            
            print(f"✅ Google Sheets Client inicializado correctamente")
            print(f"   Spreadsheet ID: {self.spreadsheet_id}")
            print(f"   Sheet Name: {self.sheet_name}")
            
        except Exception as e:
            print(f"❌ Error inicializando Google Sheets Client: {str(e)}")
            raise
    
    def _get_range(self, range_name: str) -> str:
        """Construye el rango completo con el nombre de la hoja"""
        return f"{self.sheet_name}!{range_name}"
    
    def get_all_appointments(self) -> List[Dict]:
        """
        Obtiene todas las citas del Google Sheet
        
        Returns:
            Lista de diccionarios con los datos de las citas
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self._get_range('A2:H')  # Asumiendo headers en fila 1
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return []
            
            # Convertir a lista de diccionarios
            appointments = []
            for row in values:
                # Asegurar que la fila tenga suficientes columnas
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
        """
        Obtiene las citas de un paciente específico por teléfono
        
        Args:
            telefono: Número de teléfono del paciente
            
        Returns:
            Lista de citas del paciente
        """
        all_appointments = self.get_all_appointments()
        
        # Filtrar por teléfono y estado activo
        patient_appointments = [
            apt for apt in all_appointments 
            if apt['telefono'] == telefono and apt['estado'].lower() != 'cancelada'
        ]
        
        return patient_appointments
    
    def get_appointment_by_id(self, appointment_id: str) -> Optional[Dict]:
        """
        Obtiene una cita específica por ID
        
        Args:
            appointment_id: ID de la cita
            
        Returns:
            Diccionario con los datos de la cita o None si no existe
        """
        all_appointments = self.get_all_appointments()
        
        for apt in all_appointments:
            if apt['id'] == appointment_id:
                return apt
        
        return None
    
    def update_appointment(self, appointment_id: str, updates: Dict) -> bool:
        """
        Actualiza una cita existente
        
        Args:
            appointment_id: ID de la cita a actualizar
            updates: Diccionario con los campos a actualizar
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Obtener todas las citas para encontrar la fila
            all_appointments = self.get_all_appointments()
            
            row_index = None
            for i, apt in enumerate(all_appointments):
                if apt['id'] == appointment_id:
                    row_index = i + 2  # +2 porque: +1 por header, +1 por índice 0
                    break
            
            if row_index is None:
                print(f"❌ Cita con ID {appointment_id} no encontrada")
                return False
            
            # Obtener la fila actual
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
            if 'notas' in updates:
                current_row['notas'] = updates['notas']
            
            # Preparar valores para actualizar
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
            
            # Actualizar en Google Sheets
            body = {'values': values}
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=self._get_range(f'A{row_index}:H{row_index}'),
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ Cita {appointment_id} actualizada correctamente")
            return True
            
        except HttpError as e:
            print(f"❌ Error actualizando cita: {str(e)}")
            return False
    
    def cancel_appointment(self, appointment_id: str) -> bool:
        """
        Marca una cita como cancelada (NO la elimina)
        
        Args:
            appointment_id: ID de la cita a cancelar
            
        Returns:
            True si se canceló correctamente, False en caso contrario
        """
        return self.update_appointment(appointment_id, {'estado': 'cancelada'})
    
    def format_appointment(self, appointment: Dict) -> str:
        """
        Formatea una cita para mostrar al usuario
        
        Args:
            appointment: Diccionario con los datos de la cita
            
        Returns:
            String formateado con la información de la cita
        """
        return f"""📅 {appointment['fecha']} a las {appointment['hora']}
💼 Servicio: {appointment['servicio']}
📝 Estado: {appointment['estado']}"""


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
