#Importaciones
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

#Ajustar URL para usar psycopg3
def get_url():
    url = settings.DATABASE_URL
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

#Motor de base de datos
engine = create_engine(get_url())

#Fabrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Dependencia para obtener sesion de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()