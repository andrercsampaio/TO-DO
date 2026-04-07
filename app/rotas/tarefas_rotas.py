from typing import Annotated, Literal

from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.modelos.tarefas import TarefaCriar, TarefaResponse
from app.banco_de_dados.usuarios_repositorio import UsuarioRepositorio
from app.banco_de_dados.tarefas_repositorio import TarefasRepositorio
from app.dependencias import obter_tarefas_repositorio, obter_usuario_logado, obter_usuario_repositorio

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
    

    
# ==========================================
# ROTAS FRONT - TAREFAS
# ==========================================
  
@front_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    usuario_id: Annotated[int, Depends(obter_usuario_logado)],
    repo: Annotated[TarefasRepositorio, Depends(obter_tarefas_repositorio)],
    user_repo: Annotated[UsuarioRepositorio, Depends(obter_usuario_repositorio)],
    ano: str | None = None,
    mes: str | None = None,
    dia: str | None = None
):
    # Busca o nome do usuário para a Sidebar
    usuario = await user_repo.buscar_por_id(usuario_id)
    nome_exibicao = usuario.nome_usuario if usuario else "Usuário"

    if ano:
        tarefas = await repo.listar_tarefas_data(usuario_id, ano, mes, dia)
    else:
        tarefas = await repo.listar_tarefas_usuario(usuario_id)
    
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html", 
        context={
            "tarefas": tarefas, 
            "usuario_nome": nome_exibicao # Passando o nome real
        }
    )

# Modelo auxiliar para receber APENAS o status no PATCH
class AtualizarStatusRequest(BaseModel):
    status: Literal["concluida", "em progresso", "em progresso (aguardando terceiros)", "não iniciada"]

# Nova rota API para atualização rápida de status via AJAX
@router.patch("/atualizar-status/{id_tarefa}", response_model=TarefaResponse)
@router.patch("/atualizar-status/{id_tarefa}", response_model=TarefaResponse)
async def atualizar_status_rapido(
    id_tarefa: int,
    dados: AtualizarStatusRequest,
    usuario_id: Annotated[int, Depends(obter_usuario_logado)],
    repo: Annotated[TarefasRepositorio, Depends(obter_tarefas_repositorio)]
):
    tarefa_existente = await repo.obter_tarefa(id_tarefa)
    if not tarefa_existente or tarefa_existente.id_usuario != usuario_id:
        raise HTTPException(status_code=403, detail="Acesso negado ou tarefa inexistente.")

    # Criamos o objeto completo mantendo os dados antigos e mudando apenas o status
    tarefa_atualizada_obj = TarefaCriar(
        id_usuario=usuario_id,
        descricao=tarefa_existente.descricao,
        categoria=tarefa_existente.categoria,
        prioridade=tarefa_existente.prioridade,
        hora=tarefa_existente.hora,
        data=tarefa_existente.data,
        status=dados.status
    )
    
    return await repo.atualizar_tarefa(id_tarefa, tarefa_atualizada_obj)