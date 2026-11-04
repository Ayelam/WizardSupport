#Importaciones
from pydantic_settings import BaseSettings

#Configuracion del servicio
class Settings(BaseSettings):
    #Base de datos
    DATABASE_URL: str = ""

    #JWT
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    #GLPI
    GLPI_URL: str = ""
    GLPI_APP_TOKEN: str = ""
    GLPI_USER_TOKEN: str = ""
    GLPI_CF_TOKEN: str = ""

    #Worker
    MAX_RETRIES: int = 5
    RETRY_BASE_DELAY: int = 30

    class Config:
        env_file = ".env"

#Instancia global
settings = Settings()