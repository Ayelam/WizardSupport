#Importaciones
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Sede, Usuario, Rol

#Insertar datos iniciales
def seed():
    db = SessionLocal()
    try:
        #Verificar si ya hay datos
        if db.query(Sede).first():
            print("Ya hay datos, no se inserta nada")
            return
        #Sede de prueba
        sede = Sede(clave="SEDE-001", nombre="Sede Central")
        db.add(sede)
        db.flush()
        #Usuario solicitante
        u1 = Usuario(
            matricula="SOL001",
            nombre="Juan Perez",
            sede_id=sede.id,
            rol=Rol.solicitante,
            password_hash=hash_password("123456")
        )
        #Usuario coordinador
        u2 = Usuario(
            matricula="COORD001",
            nombre="Maria Lopez",
            sede_id=sede.id,
            rol=Rol.coordinador_sede,
            password_hash=hash_password("123456")
        )
        #Usuario administrador
        u3 = Usuario(
            matricula="ADMIN001",
            nombre="Carlos Garcia",
            sede_id=sede.id,
            rol=Rol.administrador,
            password_hash=hash_password("123456")
        )
        db.add_all([u1, u2, u3])
        db.commit()
        print("Datos de prueba insertados")
    finally:
        db.close()

if __name__ == "__main__":
    seed()