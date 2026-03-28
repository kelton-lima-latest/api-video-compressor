from fastapi import FastAPI
# Importação explícita apenas do 'router'
from app.api.routes.videos import router as videos_router

app = FastAPI(
    title="Video Compressor API",
    description="API para upload e compressão de vídeos usando Celery e FFmpeg",
    version="1.0.0"
)

# Registra a rota usando a variável importada acima
app.include_router(videos_router, prefix="/api/v1/videos", tags=["Videos"])

@app.get("/", tags=["Health"])
def read_root():
    return {
        "status": "online",
        "message": "Video Compressor API está rodando perfeitamente!"
    }