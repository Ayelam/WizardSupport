#Importaciones
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#Crear aplicacion
app = FastAPI(title="Wizard Support API", version="1.0.0")

#CORS para permitir peticiones del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Ruta de salud
@app.get("/health")
async def health():
    return {"status": "ok"}