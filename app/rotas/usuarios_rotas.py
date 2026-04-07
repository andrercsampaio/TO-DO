from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.modelos.usuarios import UsuarioCriar, UsuarioResponse
from app.banco_de_dados.usuarios_repositorio import UsuarioRepositorio
from app.dependencias import obter_usuario_repositorio, obter_usuario_logado

# 'tags' agrupa estas rotas na documentação automática (Swagger/Docs).
router = APIRouter(prefix="/usuarios", tags=["Usuários"])

# Rota para criação de usuário
@router.post("/criar", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_novo_usuario(
    usuario: UsuarioCriar,
    repo: Annotated[UsuarioRepositorio, Depends(obter_usuario_repositorio)]
):
    try:
        return await repo.criar_usuarios(usuario)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )

#rota para buscar usuário por email
@router.get("/{email}", response_model=UsuarioResponse)
async def buscar_usuario_por_email(
    email: str,
    repo: Annotated[UsuarioRepositorio, Depends(obter_usuario_repositorio)]
):
    usuario = await repo.buscar_por_email(email)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado."
        )
    return usuario

#rota para buscar usuário por nome_usuario
@router.get("/username/{nome_usuario}", response_model=UsuarioResponse)
async def buscar_usuario_por_nome_usuario(
    nome_usuario: str,
    repo: Annotated[UsuarioRepositorio, Depends(obter_usuario_repositorio)]
):
    usuario = await repo.buscar_por_nome_usuario(nome_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado."
        )
    return usuario

#rota para atualizar usuário
@router.put("/atualizar", response_model=UsuarioResponse)
async def atualizar_usuario(
    usuario: UsuarioCriar,
    usuario_id: Annotated[int, Depends(obter_usuario_logado)], # <-- ID extraído do token
    repo: Annotated[UsuarioRepositorio, Depends(obter_usuario_repositorio)]
):
    usuario_atualizado = await repo.atualizar_usuario(usuario_id, usuario)
    if not usuario_atualizado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado!")
    
    return usuario_atualizado

#rota para deletar usuário
@router.delete("/deletar", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_usuario(
    usuario_id: Annotated[int, Depends(obter_usuario_logado)], # <-- ID extraído do token
    repo: Annotated[UsuarioRepositorio, Depends(obter_usuario_repositorio)]
):
    sucesso = await repo.deletar_usuario(usuario_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado!")