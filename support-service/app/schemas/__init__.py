#Importaciones
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re

#Auth
class LoginRequest(BaseModel):
    matricula: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UsuarioResponse(BaseModel):
    id: int
    matricula: str
    nombre: str
    sede_id: int
    rol: str

    class Config:
        from_attributes = True

#Tickets

class TicketCreate(BaseModel):
    titulo: str = Field(min_length=5, max_length=300)
    descripcion: str = Field(min_length=10)
    urgencia: str = Field(default="media")
    estudio_ref: Optional[str] = None

    #Validar que estudio_ref solo tenga letras, numeros y guiones
    @field_validator("estudio_ref")
    @classmethod
    def validar_estudio_ref(cls, v):
        if v is not None and not re.match(r"^[A-Za-z0-9\-]+$", v):
            raise ValueError("Solo se permiten letras, numeros y guiones")
        return v

    #Validar que la descripcion no contenga un NSS (11 digitos seguidos)
    @field_validator("descripcion")
    @classmethod
    def validar_sin_nss(cls, v):
        if re.search(r"\b\d{11}\b", v):
            raise ValueError("No se permiten datos personales (NSS) en la descripcion")
        return v

class TicketResponse(BaseModel):
    id: int
    titulo: str
    descripcion: str
    urgencia: str
    estudio_ref: Optional[str]
    estado_envio: str
    estado_glpi: Optional[str]
    glpi_ticket_id: Optional[int]
    creado_en: datetime
    solicitante: UsuarioResponse
    sede_id: int

    class Config:
        from_attributes = True

class TicketListResponse(BaseModel):
    id: int
    titulo: str
    urgencia: str
    estado_envio: str
    estado_glpi: Optional[str]
    creado_en: datetime

    class Config:
        from_attributes = True

#Seguimientos
class SeguimientoCreate(BaseModel):
    contenido: str = Field(min_length=5)

class SeguimientoResponse(BaseModel):
    id: int
    contenido: str
    estado_envio: str
    creado_en: datetime
    autor: UsuarioResponse

    class Config:
        from_attributes = True

#Resumen
class ResumenResponse(BaseModel):
    pendiente_envio: int = 0
    enviado: int = 0
    error: int = 0