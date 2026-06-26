from langchain_community.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader
from pydub import AudioSegment
import os

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """
    Downloads audio from a YouTube URL using YoutubeAudioLoader.
    Returns the local path to the downloaded audio file.
    """
    loader = YoutubeAudioLoader([url], DOWNLOAD_DIR)
    loader.yield_blobs()  # triggers the download

    files = os.listdir(DOWNLOAD_DIR)

    for file in files:
        if file.endswith(".m4a") or file.endswith(".webm"):
            return os.path.join(DOWNLOAD_DIR, file)


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