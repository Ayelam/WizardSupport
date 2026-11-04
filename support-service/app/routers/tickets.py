#Importaciones
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models import Usuario, Ticket, Seguimiento, EstadoEnvio
from app.schemas import TicketCreate, TicketResponse, TicketListResponse, SeguimientoCreate, SeguimientoResponse, ResumenResponse

#Router de tickets
router = APIRouter(prefix="/tickets", tags=["Tickets"])

#Crear ticket (H1)
@router.post("", response_model=TicketResponse)
async def crear_ticket(data: TicketCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = Ticket(
        solicitante_id=usuario.id,
        sede_id=usuario.sede_id,
        titulo=data.titulo,
        descripcion=data.descripcion,
        urgencia=data.urgencia,
        estudio_ref=data.estudio_ref,
        idempotency_key=str(uuid4())
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

#Listar tickets del usuario (H2)
@router.get("", response_model=List[TicketListResponse])
async def listar_tickets(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Ticket)
    if usuario.rol.value == "solicitante":
        query = query.filter(Ticket.solicitante_id == usuario.id)
    elif usuario.rol.value == "coordinador_sede":
        query = query.filter(Ticket.sede_id == usuario.sede_id)
    tickets = query.order_by(Ticket.creado_en.desc()).all()
    return tickets

#Resumen de estados de envio (H4) - ANTES de {ticket_id} para que no choque
@router.get("/resumen/envio", response_model=ResumenResponse)
async def resumen_envio(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Ticket)
    if usuario.rol.value == "solicitante":
        query = query.filter(Ticket.solicitante_id == usuario.id)
    elif usuario.rol.value == "coordinador_sede":
        query = query.filter(Ticket.sede_id == usuario.sede_id)
    pendientes = query.filter(Ticket.estado_envio == EstadoEnvio.pendiente_envio).count()
    enviados = query.filter(Ticket.estado_envio == EstadoEnvio.enviado).count()
    errores = query.filter(Ticket.estado_envio == EstadoEnvio.error).count()
    return ResumenResponse(pendiente_envio=pendientes, enviado=enviados, error=errores)

#Detalle de ticket (H3)
@router.get("/{ticket_id}", response_model=TicketResponse)
async def detalle_ticket(ticket_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if usuario.rol.value == "solicitante" and ticket.solicitante_id != usuario.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este ticket")
    if usuario.rol.value == "coordinador_sede" and ticket.sede_id != usuario.sede_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este ticket")
    return ticket

#Agregar seguimiento (H5)
@router.post("/{ticket_id}/seguimientos", response_model=SeguimientoResponse)
async def agregar_seguimiento(ticket_id: int, data: SeguimientoCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    seguimiento = Seguimiento(
        ticket_id=ticket_id,
        autor_id=usuario.id,
        contenido=data.contenido
    )
    db.add(seguimiento)
    db.commit()
    db.refresh(seguimiento)
    return seguimiento

#Listar seguimientos de un ticket
@router.get("/{ticket_id}/seguimientos", response_model=List[SeguimientoResponse])
async def listar_seguimientos(ticket_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    seguimientos = db.query(Seguimiento).filter(Seguimiento.ticket_id == ticket_id).order_by(Seguimiento.creado_en.asc()).all()
    return seguimientos