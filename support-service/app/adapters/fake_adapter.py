#Importaciones
from typing import Optional
from app.ports import TicketingPort

#Adaptador falso para pruebas
class FakeAdapter(TicketingPort):
    def __init__(self):
        self.tickets = {}
        self.followups = {}
        self.users = {"TST001": 99}
        self.next_ticket_id = 1000
        self.next_followup_id = 2000

    async def crear_ticket(self, titulo: str, descripcion: str, urgencia: str, usuario_glpi_id: int) -> int:
        ticket_id = self.next_ticket_id
        self.tickets[ticket_id] = {
            "name": titulo,
            "content": descripcion,
            "urgency": urgencia,
            "status": 1,
            "user": usuario_glpi_id
        }
        self.next_ticket_id += 1
        return ticket_id

    async def obtener_estado(self, glpi_ticket_id: int) -> Optional[str]:
        estado_map = {1: "Nuevo", 2: "En curso", 5: "Resuelto", 6: "Cerrado"}
        ticket = self.tickets.get(glpi_ticket_id)
        if ticket:
            return estado_map.get(ticket["status"], "Desconocido")
        return None

    async def agregar_seguimiento(self, glpi_ticket_id: int, contenido: str) -> int:
        followup_id = self.next_followup_id
        self.followups[followup_id] = {
            "ticket_id": glpi_ticket_id,
            "content": contenido
        }
        self.next_followup_id += 1
        return followup_id

    async def resolver_usuario(self, matricula: str) -> Optional[int]:
        return self.users.get(matricula)