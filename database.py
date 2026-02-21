from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos
class Paciente(Base):
    __tablename__ = "pacientes"
    
    id = Column(Integer, primary_key=True, index=True)
    telefono = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(100))
    email = Column(String(100))
    fecha_nacimiento = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    citas = relationship("Cita", back_populates="paciente")

class Doctor(Base):
    __tablename__ = "doctores"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    especialidad = Column(String(100))
    activo = Column(String(10), default="true")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    citas = relationship("Cita", back_populates="doctor")

class Servicio(Base):
    __tablename__ = "servicios"
    
    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String(100), nullable=False)
    nombre = Column(String(200), nullable=False)
    duracion_minutos = Column(Integer, nullable=False)
    descripcion = Column(Text)
    activo = Column(String(10), default="true")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    citas = relationship("Cita", back_populates="servicio")

class Cita(Base):
    __tablename__ = "citas"
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctores.id", ondelete="CASCADE"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicios.id", ondelete="CASCADE"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False, index=True)
    estado = Column(String(20), default="agendada", index=True)
    notas = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    paciente = relationship("Paciente", back_populates="citas")
    doctor = relationship("Doctor", back_populates="citas")
    servicio = relationship("Servicio", back_populates="citas")

class Conversacion(Base):
    __tablename__ = "conversaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    telefono = Column(String(20), unique=True, nullable=False, index=True)
    estado = Column(String(50), nullable=False)
    contexto = Column(JSON, default={})
    ultima_interaccion = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
