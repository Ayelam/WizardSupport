#Importaciones
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime, timezone
import enum

#Base de SQLAlchemy
class Base(DeclarativeBase):
    pass

#Enums
class Rol(str, enum.Enum):
    solicitante = "solicitante"
    coordinador_sede = "coordinador_sede"
    administrador = "administrador"

class EstadoEnvio(str, enum.Enum):
    pendiente_envio = "pendiente_envio"
    enviado = "enviado"
    error = "error"

class Urgencia(str, enum.Enum):
    baja = "baja"
    media = "media"
    alta = "alta"

#Tabla sedes
class Sede(Base):
    __tablename__ = "sedes"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)

    usuarios = relationship("Usuario", back_populates="sede")
    tickets = relationship("Ticket", back_populates="sede")

#Tabla usuarios
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    rol = Column(Enum(Rol), nullable=False, default=Rol.solicitante)
    password_hash = Column(String(255), nullable=False)

    sede = relationship("Sede", back_populates="usuarios")
    tickets = relationship("Ticket", back_populates="solicitante")
    seguimientos = relationship("Seguimiento", back_populates="autor")

#Tabla tickets
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    solicitante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    titulo = Column(String(300), nullable=False)
    descripcion = Column(Text, nullable=False)
    urgencia = Column(Enum(Urgencia), nullable=False, default=Urgencia.media)
    estudio_ref = Column(String(100), nullable=True)
    idempotency_key = Column(String(100), unique=True, nullable=False)
    estado_envio = Column(Enum(EstadoEnvio), nullable=False, default=EstadoEnvio.pendiente_envio)
    estado_glpi = Column(String(50), nullable=True)
    glpi_ticket_id = Column(Integer, nullable=True)
    intentos = Column(Integer, default=0)
    proximo_reintento = Column(DateTime, nullable=True)
    ultimo_error = Column(Text, nullable=True)
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    solicitante = relationship("Usuario", back_populates="tickets")
    sede = relationship("Sede", back_populates="tickets")
    seguimientos = relationship("Seguimiento", back_populates="ticket")

#Tabla seguimientos
class Seguimiento(Base):
    __tablename__ = "seguimientos"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    contenido = Column(Text, nullable=False)
    estado_envio = Column(Enum(EstadoEnvio), nullable=False, default=EstadoEnvio.pendiente_envio)
    glpi_followup_id = Column(Integer, nullable=True)
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ticket = relationship("Ticket", back_populates="seguimientos")
    autor = relationship("Usuario", back_populates="seguimientos")

#Tabla cache de usuarios GLPI
class UserGlpiMapping(Base):
    __tablename__ = "user_glpi_mapping"

    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(50), unique=True, nullable=False)
    glpi_user_id = Column(Integer, nullable=False)
    actualizado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))