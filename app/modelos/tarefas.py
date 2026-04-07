from pydantic import BaseModel, Field
from datetime import date, time
from typing import Literal

class TarefaBase(BaseModel):
    descricao: str = Field(..., min_length=3, max_length=150)
    categoria: Literal["trabalho", "pessoal", "estudos", "finanças", "saúde", "fitness", "habitos", "casa"]
    prioridade: Literal["baixa", "média", "alta"]
    status: Literal["concluida", "em progresso", "em progresso (aguardando terceiros)", "não iniciada"]
    hora: time = Field(default=time(0, 0))
    data: date

class TarefaCriar(TarefaBase):
    id_usuario: int | None = None

class TarefaResponse(TarefaBase):
    id: int
    id_usuario: int

