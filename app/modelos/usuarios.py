from pydantic import BaseModel, EmailStr, Field

class UsuarioBase(BaseModel):
    nome_usuario: str = Field(..., min_length=3, max_length=20)
    nome_completo: str = Field(..., min_length=3, max_length=150)
    email: EmailStr

class UsuarioCriar(UsuarioBase):
    # A senha só aparece na criação, nunca na resposta (segurança básica)
    senha: str = Field(..., min_length=6)

class UsuarioResponse(UsuarioBase):
    # O ID é devolvido pelo banco após a criação
    id: int