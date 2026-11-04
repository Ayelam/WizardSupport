#Importaciones
import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models import Ticket, Seguimiento, EstadoEnvio, UserGlpiMapping
from app.adapters.glpi_adapter import GlpiAdapter

#Procesar tickets pendientes
async def procesar_tickets(adapter: GlpiAdapter, db: Session):
    ahora = datetime.now(timezone.utc)
    tickets = db.query(Ticket).filter(
        Ticket.estado_envio == EstadoEnvio.pendiente_envio,
        (Ticket.proximo_reintento == None) | (Ticket.proximo_reintento <= ahora)
    ).all()
    for ticket in tickets:
        try:
            #Resolver usuario en GLPI
            mapping = db.query(UserGlpiMapping).filter(
                UserGlpiMapping.matricula == ticket.solicitante.matricula
            ).first()
            if mapping:
                glpi_user_id = mapping.glpi_user_id
            else:
                glpi_user_id = await adapter.resolver_usuario(ticket.solicitante.matricula)
                if glpi_user_id:
                    db.add(UserGlpiMapping(matricula=ticket.solicitante.matricula, glpi_user_id=glpi_user_id))
                else:
                    raise Exception(f"Usuario {ticket.solicitante.matricula} no encontrado en GLPI")
            #Enviar ticket
            glpi_id = await adapter.crear_ticket(ticket.titulo, ticket.descripcion, ticket.urgencia.value, glpi_user_id)
            ticket.glpi_ticket_id = glpi_id
            ticket.estado_envio = EstadoEnvio.enviado
            ticket.estado_glpi = "Nuevo"
            ticket.ultimo_error = None
            db.commit()
            print(f"Ticket {ticket.id} enviado a GLPI como {glpi_id}")
        except Exception as e:
            ticket.intentos += 1
            ticket.ultimo_error = str(e)
            if ticket.intentos >= settings.MAX_RETRIES:
                ticket.estado_envio = EstadoEnvio.error
            else:
                delay = settings.RETRY_BASE_DELAY * (2 ** ticket.intentos)
                ticket.proximo_reintento = ahora + timedelta(seconds=delay)
            db.commit()
            print(f"Error en ticket {ticket.id}: {e}")

#Procesar seguimientos pendientes
async def procesar_seguimientos(adapter: GlpiAdapter, db: Session):
    seguimientos = db.query(Seguimiento).filter(
        Seguimiento.estado_envio == EstadoEnvio.pendiente_envio
    ).all()
    for seg in seguimientos:
        try:
            if not seg.ticket.glpi_ticket_id:
                continue
            glpi_followup_id = await adapter.agregar_seguimiento(seg.ticket.glpi_ticket_id, seg.contenido)
            seg.glpi_followup_id = glpi_followup_id
            seg.estado_envio = EstadoEnvio.enviado
            db.commit()
            print(f"Seguimiento {seg.id} enviado a GLPI")
        except Exception as e:
            seg.estado_envio = EstadoEnvio.error
            db.commit()
            print(f"Error en seguimiento {seg.id}: {e}")

#Loop principal del worker
async def run_worker():
    print("Worker iniciado")
    adapter = GlpiAdapter()
    while True:
        db = SessionLocal()
        try:
            await procesar_tickets(adapter, db)
            await procesar_seguimientos(adapter, db)
        except Exception as e:
            print(f"Error general del worker: {e}")
        finally:
            db.close()
        await asyncio.sleep(30)

#Punto de entrada
if __name__ == "__main__":
    asyncio.run(run_worker())