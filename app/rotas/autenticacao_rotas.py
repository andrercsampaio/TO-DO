from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

from app.banco_de_dados.usuarios_repositorio import UsuarioRepositorio
from app.dependencias import obter_usuario_repositorio
from app.seguranca import criar_token_acesso

router = APIRouter(prefix="/auth", tags=["Autenticação"])
templates = Jinja2Templates(directory="app/templates")

# ==========================================
# ROTAS FRONT-END (HTML / FORM)
# ==========================================

@router.get("/login", response_class=HTMLResponse)
async def pagina_login(request: Request):
    """Renderiza a página de login."""
    # Correção: Passando request e name explicitamente
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login/form")
async def processar_login_front(
    email: Annotated[str, Form(...)],
    senha: Annotated[str, Form(...)],
    repo: Annotated[UsuarioRepositorio, Depends(obter_usuario_repositorio)]
):
    """Recebe os dados do HTML, valida e injeta o cookie redirecionando o usuário."""
    usuario = await repo.buscar_usuario_por_email_senha(email, senha)
    
    if not usuario:
        # Se falhar, redireciona de volta para o login (em produção, você injetaria uma mensagem de erro aqui)
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    # Gera o Token JWT
    token = criar_token_acesso(dados={"sub": str(usuario.id)})

    # Cria o redirecionamento para o Dashboard
    redirecionamento = RedirectResponse(url="/tarefas/dashboard", status_code=status.HTTP_302_FOUND)
    
    # Injeta o token HTTPOnly na resposta de redirecionamento
    redirecionamento.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=False, # Mudar para True em ambiente HTTPS
        samesite="lax",
        max_age=3600
    )
    
    return redirecionamento

# ==========================================
# ROTAS API (JSON) - Já existentes no seu código
# ==========================================

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

@router.post("/login/api") # Ajustei o path para evitar conflito com o GET
async def login_api(
    dados_login: LoginRequest,
    response: Response,
    repo: Annotated[UsuarioRepositorio, Depends(obter_usuario_repositorio)]
):
    usuario = await repo.buscar_usuario_por_email_senha(dados_login.email, dados_login.senha)
    
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos.")

    token = criar_token_acesso(dados={"sub": str(usuario.id)})

    response.set_cookie(
        key="access_token", value=f"Bearer {token}", httponly=True, secure=False, samesite="lax", max_age=3600
    )

    return {"mensagem": "Login realizado com sucesso!", "usuario": usuario.nome_completo}

@router.get("/logout") # Ajustado para GET para permitir o clique no botão do menu HTML
async def logout(response: Response):
    redirecionamento = RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    redirecionamento.delete_cookie("access_token")
    return redirecionamento