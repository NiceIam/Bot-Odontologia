import httpx
from config import get_settings
from typing import Optional

settings = get_settings()

class EvolutionAPIClient:
    def __init__(self):
        self.base_url = settings.evolution_api_url
        self.api_key = settings.evolution_api_key
        self.instance_name = settings.evolution_instance_name
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def send_message(self, phone: str, message: str) -> dict:
        """Envía un mensaje de texto a través de Evolution API"""
        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        
        # Limpiar número de teléfono
        phone_clean = phone.replace("+", "").replace("-", "").replace(" ", "")
        if not phone_clean.endswith("@s.whatsapp.net"):
            phone_clean = f"{phone_clean}@s.whatsapp.net"
        
        payload = {
            "number": phone_clean,
            "text": message
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def send_buttons(self, phone: str, message: str, buttons: list) -> dict:
        """Envía un mensaje con botones"""
        url = f"{self.base_url}/message/sendButtons/{self.instance_name}"
        
        phone_clean = phone.replace("+", "").replace("-", "").replace(" ", "")
        if not phone_clean.endswith("@s.whatsapp.net"):
            phone_clean = f"{phone_clean}@s.whatsapp.net"
        
        payload = {
            "number": phone_clean,
            "text": message,
            "buttons": buttons
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

evolution_client = EvolutionAPIClient()
