from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid
from app.worker.tasks import compress_video_task

router = APIRouter()

# O caminho absoluto onde o volume NFS será montado no Kubernetes
NFS_UPLOAD_DIR = "/mnt/nfs/uploads"

@router.post("/upload/", status_code=202)
async def upload_video(file: UploadFile = File(...)):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é um vídeo válido.")

    video_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1] or ".mp4"
    
    input_path = os.path.join(NFS_UPLOAD_DIR, f"{video_id}_input{ext}")
    output_path = os.path.join(NFS_UPLOAD_DIR, f"{video_id}_output.mp4")

    # Salva direto no ponto de montagem do NFS
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="O volume NFS não está montado no contêiner.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo no NFS: {e}")

    # Dispara a tarefa no Celery passando os caminhos do NFS
    compress_video_task.delay(input_path, output_path)

    return {
        "message": "Upload salvo no NFS com sucesso! Compressão iniciada.",
        "video_id": video_id,
        "status": "processing"
    }