import os
import base64
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# DATABASE SETUP
# ==========================================
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = DATABASE_URL or "sqlite:///./apostadores.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# RSA SECURITY SETUP (FAIL-FAST)
# ==========================================
PRIVATE_KEY_STR = os.environ.get("PRIVATE_KEY")
PUBLIC_KEY_STR = os.environ.get("PUBLIC_KEY")

if not PRIVATE_KEY_STR or not PUBLIC_KEY_STR:
    raise ValueError("ERRO CRÍTICO: As chaves RSA (PRIVATE_KEY e PUBLIC_KEY) não foram configuradas!")

# Carregamento das chaves na memória
private_key = serialization.load_pem_private_key(PRIVATE_KEY_STR.encode(), password=None)
public_key = serialization.load_pem_public_key(PUBLIC_KEY_STR.encode())

def encrypt_data(data: str) -> str:
    ciphertext = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(ciphertext).decode()

def decrypt_data(data: str) -> str:
    try:
        plaintext = private_key.decrypt(
            base64.b64decode(data.encode()),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode()
    except Exception:
        return "Erro: Falha na descriptografia"

# ==========================================
# MODELOS E ROTAS (MANTIDOS)
# ==========================================
class ApostadorDB(Base):
    __tablename__ = "apostadores"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    idade = Column(Integer)
    chave_pix = Column(String)

Base.metadata.create_all(bind=engine)

class ApostadorCreate(BaseModel):
    nome: str
    idade: int
    chave_pix: str

class ApostadorResponse(ApostadorCreate):
    id: int
    class Config: from_attributes = True

app = FastAPI(title="API Apostadores - RSA")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/apostadores/", response_model=ApostadorResponse)
def criar(apostador: ApostadorCreate, db: Session = Depends(get_db)):
    dados = apostador.model_dump()
    dados["chave_pix"] = encrypt_data(dados["chave_pix"]) # Tranca com Pública
    db_obj = ApostadorDB(**dados)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return {**dados, "id": db_obj.id, "chave_pix": decrypt_data(db_obj.chave_pix)}

@app.get("/apostadores/", response_model=list[ApostadorResponse])
def listar(db: Session = Depends(get_db)):
    lista = db.query(ApostadorDB).all()
    return [{"id": a.id, "nome": a.nome, "idade": a.idade, "chave_pix": decrypt_data(a.chave_pix)} for a in lista]