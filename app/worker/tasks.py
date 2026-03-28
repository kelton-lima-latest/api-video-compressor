import os
import subprocess
from app.worker.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.video import Video, VideoStatus

# Constantes do seu script original
TARGET_MB = 200
MARGIN_MB = 5
AUDIO_BITRATE = 128000

def get_duration(input_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", input_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 0.0

@celery_app.task(name="compress_video_task")
def compress_video_task(video_id: str):
    db = SessionLocal()
    video = db.query(Video).filter(Video.id == video_id).first()
    
    if not video:
        db.close()
        return "Video not found"

    try:
        # 1. Atualiza status para PROCESSING
        video.status = VideoStatus.PROCESSING
        db.commit()

        duration = get_duration(video.input_path)
        if duration <= 0:
            raise Exception("Não foi possível obter a duração do vídeo.")

        # 2. Lógica de Bitrate
        target_bits = (TARGET_MB - MARGIN_MB) * 1024 * 1024 * 8
        bitrate_total = target_bits / duration
        video_bitrate_k = int((bitrate_total - AUDIO_BITRATE) // 1000)

        # 3. Execução FFmpeg (2-pass)
        common_args = ["-vf", "scale=-2:-2", "-c:v", "libx264", "-preset", "veryfast", "-b:v", f"{video_bitrate_k}k"]
        
        # Pass 1
        subprocess.run(["ffmpeg", "-y", "-i", video.input_path] + common_args + ["-pass", "1", "-an", "-f", "null", "/dev/null"], check=True)
        # Pass 2
        subprocess.run(["ffmpeg", "-y", "-i", video.input_path] + common_args + ["-pass", "2", "-c:a", "aac", "-b:a", "128k", video.output_path], check=True)

        # 4. Sucesso!
        video.status = VideoStatus.COMPLETED
        video.final_size_mb = os.path.getsize(video.output_path) / (1024 * 1024)
        
    except Exception as e:
        video.status = VideoStatus.FAILED
        print(f"Erro no processamento do vídeo {video_id}: {str(e)}")
    
    db.commit()
    db.close()
    return f"Task finished for {video_id}"