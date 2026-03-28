import os
import subprocess
from app.worker.celery_app import celery_app

TARGET_MB = 200
MARGIN_MB = 5
AUDIO_BITRATE = 128000

def get_duration(input_path: str) -> float:
    """Usa ffprobe para pegar a duração do vídeo em segundos."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", input_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    output = result.stdout.strip()
    
    # Se o output estiver vazio, printamos o erro real que o ffprobe gerou
    if not output:
        print(f"🚨 ERRO REAL DO FFPROBE: {result.stderr.strip()}")
        return 0.0
        
    try:
        return float(output)
    except ValueError:
        print(f"🚨 FFPROBE retornou um valor que não é número: '{output}'")
        return 0.0

@celery_app.task(bind=True, name="compress_video_task")
def compress_video_task(self, input_path: str, output_path: str):
    print(f"\n🎬 Iniciando tarefa de compressão...")
    print(f"📥 Input: {input_path}")
    print(f"📤 Output: {output_path}")
    
    # 1. Obter duração
    duration = get_duration(input_path)
    if duration <= 0:
        print("❌ Erro ao obter duração do vídeo.")
        return {"status": "error", "error": "Invalid duration"}

    print(f"⏱ Duração: {duration:.2f}s")

    # 2. Calcular Bitrate (Sua mesma lógica do Bash)
    target_bits = (TARGET_MB - MARGIN_MB) * 1024 * 1024 * 8
    bitrate_total = target_bits / duration
    video_bitrate = int(bitrate_total - AUDIO_BITRATE)
    video_bitrate_k = video_bitrate // 1000

    if video_bitrate_k <= 0:
        print("❌ Bitrate inválido (vídeo muito longo para 200MB).")
        return {"status": "error", "error": "Bitrate calculation failed"}

    print(f"🎯 Bitrate de vídeo calculado: {video_bitrate_k}k")

    # Comandos do FFmpeg (Original, scale=-2:-2)
    pass1_cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", "scale=-2:-2",
        "-c:v", "libx264", "-preset", "veryfast", "-b:v", f"{video_bitrate_k}k",
        "-pass", "1", "-an", "-f", "null", "/dev/null"
    ]
    
    pass2_cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", "scale=-2:-2",
        "-c:v", "libx264", "-preset", "veryfast", "-b:v", f"{video_bitrate_k}k",
        "-pass", "2", "-c:a", "aac", "-b:a", "128k", output_path
    ]

    try:
        # 3. Executar Passo 1
        print("▶ Passo 1/2 executando... (Aguarde)")
        subprocess.run(pass1_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 4. Executar Passo 2
        print("▶ Passo 2/2 executando... (Aguarde)")
        subprocess.run(pass2_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 5. Checar resultado
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Sucesso! Tamanho final do arquivo: {size_mb:.2f} MB")
        
        return {"status": "success", "final_size_mb": size_mb, "output_path": output_path}
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro fatal no FFmpeg: {e}")
        return {"status": "error", "error": str(e)}