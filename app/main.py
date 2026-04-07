from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importação dos roteadores
from app.rotas.autenticacao_rotas import router as auth_router
from app.rotas.usuarios_rotas import router as usuarios_router
# Correção: Importar também o front_router
from app.rotas.tarefas_rotas import router as tarefas_router, front_router as tarefas_front_router 

app = FastAPI(title="To-Do API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas na instância da aplicação
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(tarefas_router)
app.include_router(tarefas_front_router) # Correção: Registrando as rotas HTML