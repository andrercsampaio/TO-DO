from typing import Annotated
from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.templating import Jinja2Templates

from app.modelos.tarefas import TarefaCriar, TarefaResponse
from app.banco_de_dados.tarefas_repositorio import TarefasRepositorio
from app.dependencias import obter_tarefas_repositorio, obter_usuario_logado

# Rotas API
router = APIRouter(prefix="/api/tarefas", tags=["Tarefas"])

# Rotas FRONT
front_router = APIRouter(prefix="/tarefas", tags=["front_tarefas"])
templates = Jinja2Templates(directory="app/templates")

# ==========================================
# ROTAS API - TAREFAS
# ==========================================

# criar
@router.post("/criar", response_model=TarefaResponse, status_code=status.HTTP_201_CREATED)
async def criar_nova_tarefa(
    tarefa: TarefaCriar,
    usuario_id: Annotated[int, Depends(obter_usuario_logado)],
    repo: Annotated[TarefasRepositorio, Depends(obter_tarefas_repositorio)]
) -> TarefaResponse:
    try:
        # Garante que a tarefa será criada para o usuário autenticado
        tarefa.id_usuario = usuario_id
        return await repo.criar_tarefa(tarefa)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Erro ao criar tarefa: {str(e)}"
        )

#listar
@router.get("/listar", response_model=list[TarefaResponse])
async def listar_tarefas( 
    usuario_id: Annotated[int, Depends(obter_usuario_logado)],
    repo: Annotated[TarefasRepositorio, Depends(obter_tarefas_repositorio)]
):
    try:
        return await repo.listar_tarefas_usuario(usuario_id)
    except Exception as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Erro interno ao processar a busca de tarefas."
        )
    
#listar por data   
@router.get("/listar/data", response_model=list[TarefaResponse])
async def listar_tarefas_por_data( 
    ano: str,
    usuario_id: Annotated[int, Depends(obter_usuario_logado)],
    repo: Annotated[TarefasRepositorio, Depends(obter_tarefas_repositorio)],
    mes: str | None = None,
    dia: str | None = None
):
    try:
        return await repo.listar_tarefas_data(usuario_id, ano, mes, dia)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar tarefas por data: {str(e)}"
        )

# atualizar
@router.put("/atualizar/{id_tarefa}", response_model=TarefaResponse)
async def atualizar_tarefa(
    id_tarefa: int,
    tarefa: TarefaCriar,
    usuario_id: Annotated[int, Depends(obter_usuario_logado)],
    repo: Annotated[TarefasRepositorio, Depends(obter_tarefas_repositorio)]
) -> TarefaResponse:
    
    # 1. Validação de existência e posse
    tarefa_existente = await repo.obter_tarefa(id_tarefa)
    if not tarefa_existente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada.")
    
    if tarefa_existente.id_usuario != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")

    # 2. Atualização
    try:
        tarefa.id_usuario = usuario_id # Mantém a integridade do ID
        tarefa_atualizada = await repo.atualizar_tarefa(id_tarefa, tarefa)
        return tarefa_atualizada
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar tarefa: {str(e)}"
        )

# deletar
@router.delete("/deletar/{id_tarefa}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_tarefa(
    id_tarefa: int,
    usuario_id: Annotated[int, Depends(obter_usuario_logado)],
    repo: Annotated[TarefasRepositorio, Depends(obter_tarefas_repositorio)]
):
    # 1. Validação de existência e posse
    tarefa_existente = await repo.obter_tarefa(id_tarefa)
    if not tarefa_existente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada.")
        
    if tarefa_existente.id_usuario != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")

    # 2. Deleção
    sucesso = await repo.deletar_tarefa(id_tarefa)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao deletar tarefa."
        )