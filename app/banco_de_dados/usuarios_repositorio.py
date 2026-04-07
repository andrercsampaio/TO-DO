import sqlite3
from app.banco_de_dados.local import BancoDeDadosLocal
from app.modelos.usuarios import UsuarioResponse, UsuarioCriar
from app.seguranca import obter_hash_senha, verificar_senha

class UsuarioRepositorio:
    def __init__(self, db: BancoDeDadosLocal):
        self.db = db

    async def criar_usuarios(self, usuario: UsuarioCriar) -> UsuarioResponse:
        senha_criptografada = obter_hash_senha(usuario.senha)
        
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO usuarios (nome_usuario, nome_completo, email, senha)
                    VALUES (?, ?, ?, ?)
                    """, (usuario.nome_usuario, usuario.nome_completo, usuario.email, senha_criptografada)
                )
                usuario_id = cursor.lastrowid
                dados_usuario = usuario.model_dump()
                return UsuarioResponse(id=usuario_id, **dados_usuario)
            except sqlite3.IntegrityError:
                raise Exception("Nome de usuário ou e-mail já existente.")
            
    async def atualizar_usuario(self, usuario_id: int, usuario: UsuarioCriar) -> UsuarioResponse | None:
        senha_criptografada = obter_hash_senha(usuario.senha)
        
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE usuarios 
                    SET nome_usuario = ?, nome_completo = ?, email = ?, senha = ?
                    WHERE id = ?
                    """,
                    (usuario.nome_usuario, usuario.nome_completo, usuario.email, senha_criptografada, usuario_id)
                )
                
                if cursor.rowcount == 0:
                    return None
                    
                return UsuarioResponse(id=usuario_id, **usuario.model_dump())
            except sqlite3.IntegrityError:
                raise Exception("As novas credenciais (e-mail/usuário) já estão em uso.")

    async def deletar_usuario(self, usuario_id: int) -> bool:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM usuarios WHERE id = ?", (usuario_id,)
            )
            return cursor.rowcount > 0

    async def buscar_por_email(self, email: str) -> UsuarioResponse | None:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, nome_usuario, nome_completo, email FROM usuarios WHERE email = ?", 
                (email,)
            )
            linha = cursor.fetchone()
            
            if linha:
                return UsuarioResponse(
                    id=linha[0],
                    nome_usuario=linha[1],
                    nome_completo=linha[2],
                    email=linha[3]
                )
            return None
        
    async def buscar_por_nome_usuario(self, nome_usuario: str) -> UsuarioResponse | None:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, nome_usuario, nome_completo, email FROM usuarios WHERE nome_usuario = ?", (nome_usuario,)
            )
            linha = cursor.fetchone()

            if linha: 
                return UsuarioResponse(
                    id=linha[0],
                    nome_usuario=linha[1],
                    nome_completo=linha[2],
                    email=linha[3]
                )
            return None
        
    async def buscar_usuario_por_email_senha(self, email: str, senha_plana: str) -> UsuarioResponse | None:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, nome_usuario, nome_completo, email, senha FROM usuarios WHERE email = ?", 
                (email,)
            )
            linha = cursor.fetchone()
            
            # Valida se o usuário existe e se o hash da senha confere
            if linha and verificar_senha(senha_plana, linha[4]):
                return UsuarioResponse(
                    id=linha[0],
                    nome_usuario=linha[1],
                    nome_completo=linha[2],
                    email=linha[3]
                )
            return None
        
    async def buscar_por_id(self, usuario_id: int) -> UsuarioResponse | None:
        with self.db.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, nome_usuario, nome_completo, email FROM usuarios WHERE id = ?", (usuario_id,)
            )
            linha = cursor.fetchone()
            if linha:
                return UsuarioResponse(id=linha[0], nome_usuario=linha[1], nome_completo=linha[2], email=linha[3])
            return None