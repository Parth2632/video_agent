import os

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")

_whisper_model = None

def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        print(f"Loading Faster-Whisper model ({WHISPER_MODEL})...")
        _whisper_model = WhisperModel(WHISPER_MODEL, device="cuda", compute_type="int8")
    return _whisper_model

def transcribe_audio(audio_path: str, language_code: str = None) -> str:
    model = _get_whisper_model()
    
    segments, info = model.transcribe(
        audio_path,
        language=language_code,
        task="translate",
        condition_on_previous_text=False
    )
    
    transcript = " ".join(f"[{int(segment.start)//60:02d}:{int(segment.start)%60:02d}] {segment.text.strip()}" for segment in segments)
    return transcript.strip()