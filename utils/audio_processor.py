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
        'format': 'm4a/bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'ffmpeg_location': os.path.join(sys.prefix, 'Scripts'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
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
        expected_file = base + '.m4a'
        if os.path.exists(expected_file):
            return expected_file
        elif os.path.exists(filename):
            return filename
            
    raise ValueError(f"Failed to download audio from {url}.")


def process_input(source: str) -> str:
    if source.startswith("http://") or source.startswith("https://"):
        print("Downloading audio from YouTube...")
        raw_path = download_youtube_audio(source)
    else:
        print("Using local file...")
        raw_path = source
        
    return raw_path