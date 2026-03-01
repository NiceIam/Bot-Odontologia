from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # === PostgreSQL DESACTIVADO ===
    # database_url: str
    
    # Evolution API
    evolution_api_url: str
    evolution_api_key: str
    evolution_instance_name: str
    
    # FastAPI
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Clínica
    clinic_name: str = "Clínica Dental"
    clinic_phone: str = ""
    
    # Google Sheets (nueva fuente de datos)
    spreadsheet_id: str
    sheet_name: str = "Citas"
    calendar_id: str = "primary"
    google_credentials: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
