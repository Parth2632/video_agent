import os
import sys
import yt_dlp
from pydub import AudioSegment

# Ensure ffmpeg/ffprobe (copied into Scripts) are in PATH
os.environ["PATH"] += os.pathsep + os.path.join(sys.prefix, "Scripts")

DOWNLOAD_DIR = "downloads"
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
        # Try to pull cookies from browser to avoid YouTube bot detection
        'cookiesfrombrowser': ('chrome',), 
        'extractor_args': {
            'youtube': {'player_client': ['android', 'web']}
        },
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except yt_dlp.utils.DownloadError as e:
            err_msg = str(e).lower()
            if "cookie" in err_msg or "database" in err_msg or "permission" in err_msg or "dpapi" in err_msg:
                # Fallback to edge
                ydl_opts['cookiesfrombrowser'] = ('edge',)
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_edge:
                        info = ydl_edge.extract_info(url, download=True)
                except yt_dlp.utils.DownloadError as e2:
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


def convert_to_wav(input_path: str) -> str:
    """
    Converts an audio file to WAV format using pydub.
    Returns the path to the converted WAV file.
    """
    output_path = os.path.splitext(input_path)[0] + "__converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # mono audio at 16kHz
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    """
    Splits a WAV file into chunks of given duration.
    Returns a list of file paths to the chunks.
    """
    audio = AudioSegment.from_wav(wav_path)
    chunk_len_ms = chunk_minutes * 60 * 1000
    chunks = []
    for i in range(0, len(audio), chunk_len_ms):
        chunk = audio[i:i + chunk_len_ms]
        chunk_path = os.path.join(DOWNLOAD_DIR, f"chunk_{i // chunk_len_ms + 1}.wav")
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Downloading audio from YouTube...")
        raw_path = download_youtube_audio(source)
    else:
        print("Using local file...")
        raw_path = source

    print("Converting audio to WAV format...")
    wav_path = convert_to_wav(raw_path)

    print("Chunking audio into manageable segments...")
    chunks = chunk_audio(wav_path)
    return chunks