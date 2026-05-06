import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from cryptography.fernet import Fernet

# ==========================================
# CONFIGURAÇÃO DE BANCO DE DADOS
# ==========================================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = DATABASE_URL or "sqlite:///./apostadores.db"

if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# CONFIGURAÇÃO DE SEGURANÇA (CRIPTOGRAFIA)
# ==========================================
# No Render, crie a variável de ambiente ENCRYPTION_KEY com uma chave gerada.
# Se não houver, ele gera uma temporária (útil para testes locais, 
# mas em produção OS DADOS SERÃO PERDIDOS se a aplicação reiniciar sem uma chave fixa).
CHAVE_SECRETA = os.environ.get("ENCRYPTION_KEY")
if not CHAVE_SECRETA:
    CHAVE_SECRETA = Fernet.generate_key().decode()
    print(f"⚠️ AVISO: Usando chave temporária! Adicione isso ao .env ou Render: ENCRYPTION_KEY={CHAVE_SECRETA}")

fernet = Fernet(CHAVE_SECRETA.encode())

def encrypt_data(data: str) -> str:
    """Criptografa uma string."""
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    """Descriptografa uma string."""
    try:
        return fernet.decrypt(data.encode()).decode()
    except Exception:
        # Retorna um aviso ou levanta erro se a chave mudar e não conseguir descriptografar o banco
        return "Erro: Chave PIX ilegível (Chave de criptografia inválida)"

# ==========================================
# MODELOS DE BANCO E PYDANTIC
# ==========================================
class ApostadorDB(Base):
    __tablename__ = "apostadores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    idade = Column(Integer)
    chave_pix = Column(String) # Aqui será guardado o dado CRIPTOGRAFADO

Base.metadata.create_all(bind=engine)

class ApostadorBase(BaseModel):
    nome: str
    idade: int
    chave_pix: str

class ApostadorCreate(ApostadorBase):
    pass

class ApostadorResponse(ApostadorBase):
    id: int
    model_config = {"from_attributes": True}

# ==========================================
# APP E DEPENDÊNCIAS
# ==========================================
app = FastAPI(title="API de Apostadores")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# ROTAS / ENDPOINTS
# ==========================================

@app.post("/apostadores/", response_model=ApostadorResponse)
def criar_apostador(apostador: ApostadorCreate, db: Session = Depends(get_db)):
    # 1. Pegamos os dados e criptografamos a chave PIX
    dados = apostador.model_dump()
    dados["chave_pix"] = encrypt_data(dados["chave_pix"])
    
    # 2. Salvamos no banco
    db_apostador = ApostadorDB(**dados)
    db.add(db_apostador)
    db.commit()
    db.refresh(db_apostador)
    
    # 3. Retornamos um dicionário com a chave descriptografada (FastAPI converte para ApostadorResponse)
    return {
        "id": db_apostador.id,
        "nome": db_apostador.nome,
        "idade": db_apostador.idade,
        "chave_pix": decrypt_data(db_apostador.chave_pix)
    }

@app.get("/apostadores/", response_model=list[ApostadorResponse])
def listar_apostadores(db: Session = Depends(get_db)):
    apostadores = db.query(ApostadorDB).all()
    resultado = []
    
    # Descriptografamos a chave de todos os usuários da lista antes de retornar
    for a in apostadores:
        resultado.append({
            "id": a.id,
            "nome": a.nome,
            "idade": a.idade,
            "chave_pix": decrypt_data(a.chave_pix)
        })
        
    return resultado

@app.get("/apostadores/{apostador_id}", response_model=ApostadorResponse)
def buscar_apostador(apostador_id: int, db: Session = Depends(get_db)):
    apostador = db.query(ApostadorDB).filter(ApostadorDB.id == apostador_id).first()
    if not apostador:
        raise HTTPException(status_code=404, detail="Apostador não encontrado")
    
    # Retorna descriptografado
    return {
        "id": apostador.id,
        "nome": apostador.nome,
        "idade": apostador.idade,
        "chave_pix": decrypt_data(apostador.chave_pix)
    }

@app.put("/apostadores/{apostador_id}", response_model=ApostadorResponse)
def atualizar_apostador(apostador_id: int, apostador_atualizado: ApostadorCreate, db: Session = Depends(get_db)):
    db_apostador = db.query(ApostadorDB).filter(ApostadorDB.id == apostador_id).first()
    if not db_apostador:
        raise HTTPException(status_code=404, detail="Apostador não encontrado")

    dados_novos = apostador_atualizado.model_dump()
    
    # Criptografa a nova chave PIX antes de atualizar o banco
    if "chave_pix" in dados_novos:
        dados_novos["chave_pix"] = encrypt_data(dados_novos["chave_pix"])

    for key, value in dados_novos.items():
        setattr(db_apostador, key, value)

    db.commit()
    db.refresh(db_apostador)
    
    # Retorna descriptografado
    return {
        "id": db_apostador.id,
        "nome": db_apostador.nome,
        "idade": db_apostador.idade,
        "chave_pix": decrypt_data(db_apostador.chave_pix)
    }

@app.delete("/apostadores/{apostador_id}")
def deletar_apostador(apostador_id: int, db: Session = Depends(get_db)):
    db_apostador = db.query(ApostadorDB).filter(ApostadorDB.id == apostador_id).first()
    if not db_apostador:
        raise HTTPException(status_code=404, detail="Apostador não encontrado")

    db.delete(db_apostador)
    db.commit()
    return {"mensagem": "Apostador deletado com sucesso"}