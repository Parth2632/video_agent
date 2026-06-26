import whisper
import os 

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

_model = None

def load_model():
    global _model
    if _model is None:
        print(f"Loading whisper model ({WHISPER_MODEL})...")
        _model = whisper.load_model(WHISPER_MODEL)
    return _model


def transcribe_chunk(chunk_path: str, translate:bool = False) -> str:
    """
    Transcribe a single chunk using Whisper
    """
    model = load_model()
    task = "translate" if translate else "transcribe"
    print(f"Transcribing {chunk_path}...")
    result = model.transcribe(chunk_path, task=task)
    return result["text"].strip()