from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel, EmailStr

from app.banco_de_dados.usuarios_repositorio import UsuarioRepositorio
from app.dependencias import obter_usuario_repositorio
from app.seguranca import criar_token_acesso

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# Modelo de validação apenas para o request de login
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

@router.post("/login")
async def login(
    dados_login: LoginRequest,
    response: Response,
    repo: Annotated[UsuarioRepositorio, Depends(obter_usuario_repositorio)]
):
    usuario = await repo.buscar_usuario_por_email_senha(dados_login.email, dados_login.senha)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    # Cria o token contendo o ID do usuário no payload (sub = subject)
    token = criar_token_acesso(dados={"sub": str(usuario.id)})

    # Injeta o token em um cookie HttpOnly (protege contra ataques XSS no front-end)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=False, # Mudar para True em produção (exige HTTPS)
        samesite="lax",
        max_age=3600 # 1 hora
    )

    return {"mensagem": "Login realizado com sucesso!", "usuario": usuario.nome_completo}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"mensagem": "Logout realizado com sucesso!"}