from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# O motor de conexão (Engine)
engine = create_engine(settings.DATABASE_URL)

# A fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A classe Base que todos os seus Models vão herdar
Base = declarative_base()

# Função auxiliar para o FastAPI injetar o banco nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()