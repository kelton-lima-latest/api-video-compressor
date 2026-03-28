import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.video import Video, VideoStatus
from app.worker.tasks import compress_video_task

from fastapi.responses import FileResponse

router = APIRouter()
NFS_UPLOAD_DIR = "/mnt/nfs/uploads"

@router.post("/upload/", status_code=202)
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validação básica
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é um vídeo.")

    video_id = uuid.uuid4()
    ext = os.path.splitext(file.filename)[1] or ".mp4"
    
    input_path = os.path.join(NFS_UPLOAD_DIR, f"{video_id}_input{ext}")
    output_path = os.path.join(NFS_UPLOAD_DIR, f"{video_id}_output.mp4")

    # 1. Salva o arquivo no NFS
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no NFS: {str(e)}")

    # 2. Cria o registro no Banco de Dados (Status: PENDING)
    new_video = Video(
        id=video_id,
        filename=file.filename,
        status=VideoStatus.PENDING,
        input_path=input_path,
        output_path=output_path,
        original_size_mb=os.path.getsize(input_path) / (1024 * 1024)
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    # 3. Dispara a tarefa no Celery passando apenas o ID (String)
    compress_video_task.delay(str(video_id))

    return {
        "id": new_video.id,
        "status": new_video.status,
        "message": "Upload concluído. Processamento iniciado em background."
    }

@router.get("/{video_id}")
async def get_video_status(video_id: str, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado.")
    
    return {
        "id": video.id,
        "filename": video.filename,
        "status": video.status,
        "original_size": f"{video.original_size_mb:.2f} MB",
        "final_size": f"{video.final_size_mb:.2f} MB" if video.final_size_mb else None,
        "created_at": video.created_at,
        "updated_at": video.updated_at
    }

@router.get("/", response_model=list)
async def list_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de todos os vídeos e seus status.
    Inclui paginação simples (skip/limit).
    """
    videos = db.query(Video).offset(skip).limit(limit).all()
    return [
        {
            "id": v.id,
            "filename": v.filename,
            "status": v.status,
            "original_size": f"{v.original_size_mb:.2f} MB" if v.original_size_mb else None,
            "final_size": f"{v.final_size_mb:.2f} MB" if v.final_size_mb else None,
            "created_at": v.created_at
        } for v in videos
    ]

@router.get("/download/{video_id}")
async def download_video(video_id: str, db: Session = Depends(get_db)):
    """
    Busca o vídeo comprimido no NFS e inicia o download para o usuário.
    """
    # 1. Busca o registro no banco
    video = db.query(Video).filter(Video.id == video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado.")
    
    # 2. Verifica se o processamento já terminou
    if video.status != VideoStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"O vídeo ainda não está pronto para download. Status atual: {video.status}"
        )

    # 3. Verifica se o arquivo físico realmente existe no NFS
    if not os.path.exists(video.output_path):
        raise HTTPException(
            status_code=404, 
            detail="Arquivo físico não encontrado no servidor de armazenamento."
        )

    # 4. Define um nome amigável para o arquivo baixado
    # Ex: "compressed_meu_video.mp4"
    friendly_name = f"compressed_{video.filename}"

    return FileResponse(
        path=video.output_path,
        filename=friendly_name,
        media_type="video/mp4"
    )