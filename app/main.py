from fastapi import FastAPI

# Inicializa o app FastAPI
app = FastAPI(
    title="Video Compressor API",
    description="API para upload e compressão de vídeos usando Celery e FFmpeg",
    version="1.0.0"
)

# Rota de teste básica (Healthcheck)
@app.get("/", tags=["Health"])
def read_root():
    return {
        "status": "online",
        "message": "Video Compressor API está rodando perfeitamente!"
    }