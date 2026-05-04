import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base

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

class ApostadorDB(Base):
    __tablename__ = "apostadores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    idade = Column(Integer)
    chave_pix = Column(String)

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

app = FastAPI(title="API de Apostadores")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/apostadores/", response_model=ApostadorResponse)
def criar_apostador(apostador: ApostadorCreate, db: Session = Depends(get_db)):
    db_apostador = ApostadorDB(**apostador.model_dump())
    db.add(db_apostador)
    db.commit()
    db.refresh(db_apostador)
    return db_apostador

@app.get("/apostadores/", response_model=list[ApostadorResponse])
def listar_apostadores(db: Session = Depends(get_db)):
    return db.query(ApostadorDB).all()

@app.get("/apostadores/{apostador_id}", response_model=ApostadorResponse)
def buscar_apostador(apostador_id: int, db: Session = Depends(get_db)):
    apostador = db.query(ApostadorDB).filter(ApostadorDB.id == apostador_id).first()
    if not apostador:
        raise HTTPException(status_code=404, detail="Apostador não encontrado")
    return apostador

@app.put("/apostadores/{apostador_id}", response_model=ApostadorResponse)
def atualizar_apostador(apostador_id: int, apostador_atualizado: ApostadorCreate, db: Session = Depends(get_db)):
    db_apostador = db.query(ApostadorDB).filter(ApostadorDB.id == apostador_id).first()
    if not db_apostador:
        raise HTTPException(status_code=404, detail="Apostador não encontrado")

    for key, value in apostador_atualizado.model_dump().items():
        setattr(db_apostador, key, value)

    db.commit()
    db.refresh(db_apostador)
    return db_apostador

@app.delete("/apostadores/{apostador_id}")
def deletar_apostador(apostador_id: int, db: Session = Depends(get_db)):
    db_apostador = db.query(ApostadorDB).filter(ApostadorDB.id == apostador_id).first()
    if not db_apostador:
        raise HTTPException(status_code=404, detail="Apostador não encontrado")

    db.delete(db_apostador)
    db.commit()
    return {"mensagem": "Apostador deletado com sucesso"}