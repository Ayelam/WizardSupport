#Importaciones
from abc import ABC, abstractmethod
from typing import Optional

#Interfaz del puerto de ticketing
class TicketingPort(ABC):

    @abstractmethod
    async def crear_ticket(self, titulo: str, descripcion: str, urgencia: str, usuario_glpi_id: int) -> int:
        """Crea un ticket y devuelve el ID de GLPI"""
        pass

    @abstractmethod
    async def obtener_estado(self, glpi_ticket_id: int) -> Optional[str]:
        """Consulta el estado de un ticket en GLPI"""
        pass

    @abstractmethod
    async def agregar_seguimiento(self, glpi_ticket_id: int, contenido: str) -> int:
        """Agrega un seguimiento y devuelve el ID de GLPI"""
        pass

    @abstractmethod
    async def resolver_usuario(self, matricula: str) -> Optional[int]:
        """Busca un usuario en GLPI por matricula y devuelve su ID"""
        pass