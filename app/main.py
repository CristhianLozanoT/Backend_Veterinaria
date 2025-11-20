from fastapi import FastAPI
from app.routers import razas, usuarios, medicamentos, mascotas, facturas, consultas,clientes,citas,consulta_medicamentos
from app.auth import router as auth_router
from app.seeders.seed import seed_admin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes luego limitarlo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    seed_admin()
    

app.include_router(auth_router, prefix="/api")
app.include_router(usuarios.router, prefix="/api")
app.include_router(razas.router, prefix="/api")
app.include_router(medicamentos.router, prefix="/api")
app.include_router(mascotas.router, prefix="/api")
app.include_router(facturas.router, prefix="/api")
app.include_router(consultas.router, prefix="/api")
app.include_router(clientes.router, prefix="/api")
app.include_router(citas.router, prefix="/api")
app.include_router(consulta_medicamentos.router, prefix="/api")




