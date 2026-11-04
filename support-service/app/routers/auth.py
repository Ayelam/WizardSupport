#Importaciones
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, decode_access_token
from app.models import Usuario
from app.schemas import LoginRequest, TokenResponse, UsuarioResponse

#Esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

#Router de autenticacion
router = APIRouter(prefix="/auth", tags=["Auth"])

#Login
@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.matricula == request.matricula).first()
    if not usuario or not verify_password(request.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Matricula o contrasena incorrecta")
    token = create_access_token({"sub": usuario.matricula, "rol": usuario.rol.value, "sede_id": usuario.sede_id})
    return TokenResponse(access_token=token)

#Obtener usuario actual (dependencia reutilizable)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido")
    usuario = db.query(Usuario).filter(Usuario.matricula == payload["sub"]).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario

#Perfil del usuario actual
@router.get("/me", response_model=UsuarioResponse)
async def me(usuario: Usuario = Depends(get_current_user)):
    return usuario