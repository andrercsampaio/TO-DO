from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importação dos roteadores
from app.rotas.autenticacao_rotas import router as auth_router
from app.rotas.usuarios_rotas import router as usuarios_router
from app.rotas.tarefas_rotas import router as tarefas_router

app = FastAPI(title="To-Do API", version="1.0.0")

# Configuração de CORS para permitir requisições de outras origens (Front-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, substitua "*" pelo domínio/IP exato do front-end
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas na instância da aplicação
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(tarefas_router)