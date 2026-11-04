#Importaciones
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

#Motor de base de datos
engine = create_engine(settings.DATABASE_URL)

#Fabrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Dependencia para obtener sesion de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()