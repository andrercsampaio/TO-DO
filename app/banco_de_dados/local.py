import sqlite3

from contextlib import contextmanager

class BancoDeDadosLocal():
    def __init__(self, nome_arquivo = 'to_do.db'):
        self.nome_arquivo = nome_arquivo
        self.inicializar_banco()

    #conexão com o banco
    @contextmanager
    def conectar(self):
        conexao = sqlite3.connect(self.nome_arquivo, check_same_thread=False)
        conexao.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conexao
            conexao.commit()

        except Exception as e:
            conexao.rollback()
            raise e
        
        finally:
            conexao.close()

    
    #inicializar/criar banco/tabelas
    def inicializar_banco(self):
        with self.conectar() as conexao:
        
            cursor = conexao.cursor()
            #tabela usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_usuario TEXT UNIQUE NOT NULL,
                    nome_completo TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Tarefas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_usuario INTEGER NOT NULL,
                    descricao TEXT,
                    categoria TEXT NOT NULL,
                    prioridade TEXT NOT NULL,
                    status TEXT NOT NULL,
                    hora TEXT NOT NULL, 
                    data TEXT NOT NULL, 
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_Tarefas_usuario ON Tarefas(id_usuario)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)')
        
        print("Banco de dados inicializado")