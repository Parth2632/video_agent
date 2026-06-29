import os
import sys
import yt_dlp

# Ensure ffmpeg/ffprobe (copied into Scripts) are in PATH
os.environ["PATH"] += os.pathsep + os.path.join(sys.prefix, "Scripts")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def clear_downloads():
    import shutil
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """
    Downloads audio from a YouTube URL using yt-dlp directly.
    Returns the local path to the downloaded audio file.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'ffmpeg_location': os.path.join(sys.prefix, 'Scripts'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'postprocessor_args': [
            '-ar', '16000',
            '-ac', '1',
            '-c:a', 'pcm_s16le'
        ],
        'extractor_args': {'youtube': ['player_client=android,ios,web']},
        'quiet': True,
    }
    
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = "cookies.txt"
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except yt_dlp.utils.DownloadError as e:
            err_msg = str(e).lower()
            if "cookie" in err_msg or "database" in err_msg or "permission" in err_msg or "dpapi" in err_msg or "forbidden" in err_msg or "403" in err_msg:
                # Fallback to Chrome cookies if standard spoofing fails
                ydl_opts['cookiesfrombrowser'] = ('chrome',)
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_edge:
                        info = ydl_edge.extract_info(url, download=True)
                except yt_dlp.utils.DownloadError:
                    # Last resort: try without cookies
                    del ydl_opts['cookiesfrombrowser']
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_no_cookies:
                        info = ydl_no_cookies.extract_info(url, download=True)
            else:
                raise
                
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        expected_file = base + '.wav'
        if os.path.exists(expected_file):
            return expected_file
        elif os.path.exists(filename):
            return filename
            
    raise ValueError(f"Failed to download audio from {url}.")


def ensure_wav(media_path: str) -> str:
    if media_path.lower().endswith(".wav"):
        return media_path
        
    import subprocess
    import time
    
    filename = os.path.basename(media_path)
    base, _ = os.path.splitext(filename)
    wav_path = os.path.join(DOWNLOAD_DIR, f"{base}_{int(time.time())}.wav")
    
    try:
        subprocess.run(["ffmpeg", "-y", "-i", media_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav_path], check=True, capture_output=True)
        return wav_path
    except Exception as e:
        print(f"FFmpeg conversion failed: {e}")
        return media_path


def process_input(source: str) -> str:
    if source.startswith("http://") or source.startswith("https://"):
        print("Downloading audio from YouTube...")
        raw_path = download_youtube_audio(source)
    else:
        print("Using local file...")
        raw_path = source
        
    return ensure_wav(raw_path)