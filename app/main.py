from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import videos

app = FastAPI(title="Video Compressor API")

# 1. Defina as origens permitidas
# Em desenvolvimento, você pode usar ["*"] para permitir tudo, 
# mas o ideal é listar as portas comuns de frontend:
origins = [
    "http://localhost:3000",  # React padrão
    "http://localhost:5173",  # Vite (React/Vue moderno) padrão
    "http://127.0.0.1:5173",
]

# 2. Adicione o Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os headers
)

# Inclui as rotas
app.include_router(videos.router, prefix="/api/v1/videos", tags=["videos"])

@app.get("/")
async def root():
    return {"message": "Video Compressor API is running"}