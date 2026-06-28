import os

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

_whisper_model = None

def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        print(f"Loading Whisper model ({WHISPER_MODEL})...")
        _whisper_model = whisper.load_model(WHISPER_MODEL)
    return _whisper_model

import numpy as np
from pydub import AudioSegment

def transcribe_chunk(chunk_path: str) -> str:
    model = _get_whisper_model()
    
    # Bypass whisper's ffmpeg subprocess by loading directly into memory
    audio = AudioSegment.from_file(chunk_path)
    
    # Ensure it's 16kHz mono (it should already be, but just in case)
    audio = audio.set_channels(1).set_frame_rate(16000)
    
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
    
    if len(samples) == 0:
        return ""
        
    result = model.transcribe(samples)
    return result.get("text", "").strip()

def transcribe_all(chunks: list[str]) -> str:
    return " ".join(transcribe_chunk(chunk) for chunk in chunks)