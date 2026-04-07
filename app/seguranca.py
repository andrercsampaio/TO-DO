import jwt
import bcrypt
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configurações do JWT
SECRET_KEY = os.getenv("SECRET_KEY", "SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180

def obter_hash_senha(senha: str) -> str:
    """Gera o salt e o hash da senha usando bcrypt nativo."""
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return hash_bytes.decode('utf-8')

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Valida a senha em texto plano contra o hash armazenado no banco."""
    return bcrypt.checkpw(senha_plana.encode('utf-8'), senha_hash.encode('utf-8'))

def criar_token_acesso(dados: dict) -> str:
    copia_dados = dados.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    copia_dados.update({"exp": expiracao})
    
    token_jwt = jwt.encode(copia_dados, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

def decodificar_token_acesso(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None # Token expirou
    except jwt.InvalidTokenError:
        return None # Token inválido