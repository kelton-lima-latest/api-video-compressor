import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import videos

app = FastAPI(title="Video Compressor API")

# 1. Configuração de CORS Dinâmica
# Em Kubernetes, o frontend acessa a API via DNS/IP do Cluster ou Ingress.
# Buscamos as origens de uma variável de ambiente, com fallback para localhost.
allowed_origins = ["*"] # os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173").split(",")

# Para testes iniciais no cluster, você também pode usar ["*"], 
# mas listar as origens é a melhor prática de segurança.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas da API
app.include_router(videos.router, prefix="/api/v1/videos", tags=["videos"])

@app.get("/")
async def root():
    """Rota de Health Check utilizada pelas Probes do Kubernetes"""
    return {
        "status": "up",
        "message": "Video Compressor API is running",
        "environment": os.getenv("ENV", "development")
    }

# 2. Entrypoint para evitar o CrashLoopBackOff (Exit Code: 0)
# Este bloco garante que o Uvicorn inicie o servidor e mantenha o processo vivo.
if __name__ == "__main__":
    port = int(os.getenv("PORT", 9000))
    # log_level "info" é o padrão de mercado para observabilidade inicial
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, log_level="info")