from typing import Annotated

from fastapi import Request, HTTPException, status, Depends
from app.seguranca import decodificar_token_acesso

from app.banco_de_dados.local import BancoDeDadosLocal
from app.banco_de_dados.tarefas_repositorio import TarefasRepositorio
from app.banco_de_dados.usuarios_repositorio import UsuarioRepositorio

# Instância única da infraestrutura (Singleton)
banco_de_dados = BancoDeDadosLocal()

#Fornece a instância única do banco de dados.
def obter_banco_de_dados() -> BancoDeDadosLocal:
    return banco_de_dados

#Injeta o banco no repositório 
def obter_usuario_repositorio(
        banco_de_dados_local: Annotated[BancoDeDadosLocal, Depends(obter_banco_de_dados)]
    ) -> UsuarioRepositorio:
    return UsuarioRepositorio(banco_de_dados_local)

# tarefas repositorio
def obter_tarefas_repositorio (
        banco_de_dados_local: Annotated[BancoDeDadosLocal, Depends(obter_banco_de_dados)]
 ) -> TarefasRepositorio:
    return TarefasRepositorio(banco_de_dados_local)


# obter_usuario_logado
def obter_usuario_logado(request: Request) -> int:
    token_cookie = request.cookies.get("access_token")
    
    if not token_cookie or not token_cookie.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado."
        )
    
    token_limpo = token_cookie.split(" ")[1]
    payload = decodificar_token_acesso(token_limpo)
    
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado. Faça login novamente."
        )
        
    return int(payload["sub"])