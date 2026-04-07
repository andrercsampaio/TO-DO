import sqlite3
from datetime import date, time
from app.banco_de_dados.local import BancoDeDadosLocal
from app.modelos.tarefas import TarefaCriar, TarefaResponse


class TarefasRepositorio:
    def __init__(self, banco_de_dados: BancoDeDadosLocal):
        self.db = banco_de_dados

    #criar uma tarefa
    async def criar_tarefa(self, tarefa: TarefaCriar) -> TarefaResponse:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                """
                INSERT INTO tarefas (id_usuario, descricao, categoria, prioridade, status, hora, data) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (tarefa.id_usuario, tarefa.descricao, tarefa.categoria, tarefa.prioridade, tarefa.status, str(tarefa.hora), str(tarefa.data))
            )
            tarefa_id = cursor.lastrowid
            return TarefaResponse(id=tarefa_id, **tarefa.model_dump())
        
    #atualizar tarefa
    async def atualizar_tarefa(self, tarefa_id: int, tarefa:TarefaCriar) -> TarefaResponse:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE tarefas SET descricao = ?, categoria = ?, prioridade = ?, status = ?, hora = ?, data = ? WHERE id = ?",
                (tarefa.descricao, tarefa.categoria, tarefa.prioridade, tarefa.status, str(tarefa.hora), str(tarefa.data), tarefa_id)
            )
            if cursor.rowcount == 0:
                return None
            return TarefaResponse(id=tarefa_id, **tarefa.model_dump())
        
    #deletar tarefa
    async def deletar_tarefa(self, tarefa_id: int) -> bool:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM tarefas WHERE id = ?", (tarefa_id,)
            )
            return cursor.rowcount > 0
        
    #Busca uma tarefa por id. 
    async def obter_tarefa(self, tarefa_id: int) -> TarefaResponse | None:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id, id_usuario, descricao, categoria, prioridade, status, hora, data FROM tarefas WHERE id =? ", (tarefa_id,))
            linha = cursor.fetchone()
            if linha:
                return TarefaResponse(
                    id=linha[0], 
                    id_usuario=linha[1], 
                    descricao=linha[2], 
                    categoria=linha[3], 
                    prioridade=linha[4], 
                    status=linha[5],
                    hora = linha[6],
                    data = linha[7]
                )
            return None
        
    #buscar tarefas de usuário
    async def listar_tarefas_usuario(self, usuario_id: int) -> list[TarefaResponse]: 
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id, id_usuario, descricao, categoria, prioridade, status, hora, data FROM tarefas WHERE id_usuario =?", (usuario_id,))
            linhas = cursor.fetchall()
            
            return [
                TarefaResponse(
                    id=l[0], 
                    id_usuario=l[1], 
                    descricao=l[2], 
                    categoria=l[3], 
                    prioridade=l[4], 
                    status=l[5],
                    hora=l[6],
                    data=l[7]
                ) for l in linhas
            ]


    # Lógica: Listar tarefa por data.
    async def listar_tarefas_data(
        self, 
        usuario_id: int,
        ano: str,
        mes: str | None = None, 
        dia: str | None = None, 
    ) -> list[TarefaResponse]:
        
        query = "SELECT id, id_usuario, descricao, categoria, prioridade, status, hora, data FROM tarefas WHERE id_usuario = ?"
        params = [usuario_id]
        
        data_busca = ano
        if mes:
            data_busca += f"-{mes.zfill(2)}"
            if dia:
                data_busca += f"-{dia.zfill(2)}"
        
        query += " AND data LIKE ?"
        params.append(f"{data_busca}%")
        
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(query, params)
            linhas = cursor.fetchall()
            
            return [
                TarefaResponse(
                    id=l[0], id_usuario=l[1], descricao=l[2], 
                    categoria=l[3], prioridade=l[4], status=l[5],
                    hora=l[6], data=l[7]
                ) for l in linhas
            ]
                