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

def transcribe_chunk(chunk_path: str) -> str:
    model = _get_whisper_model()
    result = model.transcribe(chunk_path)
    return result["text"].strip()

def transcribe_all(chunks: list[str]) -> str:
    return " ".join(transcribe_chunk(chunk) for chunk in chunks)