import streamlit as st
import os
import html
import tempfile
from dotenv import load_dotenv

load_dotenv()

from utils.audio_processor import process_input, clear_downloads
from core.transcriber import transcribe_audio
from core.summarizer import summarize, create_title
from core.extractor import extract_insights
from core.rag_engine import build_rag_chain, ask_question

st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLES  —  "studio console" theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-base: #0b0c10;
    --bg-panel: #15171c;
    --bg-panel-2: #1b1e24;
    --ink: #ECEAE4;
    --ink-dim: rgba(236,234,228,0.55);
    --line: rgba(236,234,228,0.08);
    --amber: #F2A65A;
    --cyan: #5EEAD4;
    --rose: #FF8FA3;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

#MainMenu, footer {
    visibility: hidden;
}

[data-testid="stHeader"] {
    background-color: transparent !important;
}

.stAppDeployButton {
    display: none !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(255,255,255,0.03), transparent 32%),
        radial-gradient(circle at bottom right, rgba(255,255,255,0.02), transparent 30%),
        #0f1115;
    color: var(--ink);
    background-attachment: fixed;
}

.block-container {
    padding-top: 0.8rem;
    padding-bottom: 1.5rem;
    max-width: 1320px;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* ---------- Header console ---------- */

.console {
    position: relative;
    padding: 1.1rem 1.4rem;
    border-radius: 18px;
    background: rgba(22,24,29,0.72);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid var(--line);
    box-shadow: 0 6px 24px rgba(0,0,0,0.22);
    margin-bottom: 1.6rem;
    overflow: hidden;
}

.console::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(242,166,90,0.55), transparent);
}

.console-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 1.4rem;
}

.console-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    color: var(--cyan);
    text-transform: uppercase;
    margin: 0 0 0.5rem 0;
}

.console-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0;
    letter-spacing: -0.01em;
}

.console-subtitle {
    color: var(--ink-dim);
    margin-top: 0.5rem;
    font-size: 0.95rem;
}

.status-panel {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    background: rgba(0,0,0,0.25);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 0.55rem 0.95rem;
    white-space: nowrap;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--cyan);
    animation: pulse-dot 2s infinite;
    flex-shrink: 0;
}

.status-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    color: var(--ink-dim);
}

@keyframes pulse-dot {
    0% { box-shadow: 0 0 0 0 rgba(94,234,212,0.55); }
    70% { box-shadow: 0 0 0 6px rgba(94,234,212,0); }
    100% { box-shadow: 0 0 0 0 rgba(94,234,212,0); }
}

.waveform {
    display: flex;
    align-items: center;
    gap: 3px;
    height: 24px;
    margin-top: 0.9rem;
}

.waveform span {
    width: 3px;
    border-radius: 2px;
    background: var(--amber);
    animation: wave 1.1s ease-in-out infinite;
    transform-origin: center;
}

.waveform span:nth-child(odd) { background: var(--cyan); }
.waveform span:nth-child(1)  { height: 40%; animation-delay: 0.0s; }
.waveform span:nth-child(2)  { height: 75%; animation-delay: 0.1s; }
.waveform span:nth-child(3)  { height: 55%; animation-delay: 0.2s; }
.waveform span:nth-child(4)  { height: 95%; animation-delay: 0.3s; }
.waveform span:nth-child(5)  { height: 35%; animation-delay: 0.4s; }
.waveform span:nth-child(6)  { height: 70%; animation-delay: 0.5s; }
.waveform span:nth-child(7)  { height: 50%; animation-delay: 0.6s; }
.waveform span:nth-child(8)  { height: 85%; animation-delay: 0.7s; }
.waveform span:nth-child(9)  { height: 45%; animation-delay: 0.8s; }
.waveform span:nth-child(10) { height: 65%; animation-delay: 0.9s; }
.waveform span:nth-child(11) { height: 30%; animation-delay: 1.0s; }
.waveform span:nth-child(12) { height: 60%; animation-delay: 1.1s; }

@keyframes wave {
    0%, 100% { transform: scaleY(0.45); }
    50% { transform: scaleY(1); }
}

@media (prefers-reduced-motion: reduce) {
    .waveform span, .status-dot { animation: none; }
}

/* ---------- Panels / cards ---------- */

.panel {
    background: rgba(22,24,29,0.72);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 22px;
    padding: 1.15rem 1.3rem;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    margin-bottom: 1.1rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 10px 28px rgba(0,0,0,0.25);
}

.step-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    color: var(--amber);
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.08rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 1rem 0;
}

.empty-panel {
    border: 1px dashed var(--line);
    border-radius: 18px;
    padding: 2.2rem;
    text-align: center;
    color: var(--ink-dim);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 0.03em;
}

.insight-card {
    background: rgba(24,26,32,0.82);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 1.2rem 1.25rem;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    margin-bottom: 1rem;
    transition: all 0.22s ease;
    box-shadow: 0 8px 22px rgba(0,0,0,0.22);
}

.insight-card:hover {
    transform: translateY(-4px);
    border-color: rgba(255,255,255,0.12);
    background: rgba(28,30,36,0.94);
}

.insight-card.hero {
    border-left: 3px solid var(--amber);
}

.grid-card {
    min-height: 220px;
}

.led {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 0.5rem;
    position: relative;
    top: -1px;
}

.led-cyan  { background: var(--cyan);  box-shadow: 0 0 8px var(--cyan); }
.led-amber { background: var(--amber); box-shadow: 0 0 8px var(--amber); }
.led-rose  { background: var(--rose);  box-shadow: 0 0 8px var(--rose); }

.card-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-dim);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
}

.card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1.4;
    color: var(--ink);
    margin: 0;
}

.card-body {
    color: rgba(236,234,228,0.86);
    line-height: 1.75;
    font-size: 0.94rem;
    white-space: pre-wrap;
    margin: 0;
}

.hr {
    border: none;
    border-top: 1px solid var(--line);
    margin: 2.2rem 0;
}

/* ---------- AI Loading UI ---------- */
.ai-loading-card {
    background: linear-gradient(145deg, var(--bg-panel), var(--bg-panel-2));
    border: 1px solid rgba(94,234,212,0.15);
    border-radius: 16px;
    padding: 1.8rem 2rem;
    box-shadow: 0 12px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.ai-loading-card::before {
    content: "";
    position: absolute;
    top: 0; left: -100%; width: 50%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    animation: scanline 2s infinite linear;
}

@keyframes scanline {
    0% { left: -50%; }
    100% { left: 100%; }
}

.ai-loading-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1.2rem;
}

.ai-spinner {
    width: 18px;
    height: 18px;
    border: 2px solid var(--line);
    border-top-color: var(--cyan);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin { 100% { transform: rotate(360deg); } }

.ai-loading-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--ink);
    margin: 0;
    letter-spacing: 0.02em;
}

.ai-loading-steps {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

.ai-step {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: var(--ink-dim);
    transition: all 0.3s ease;
}

.ai-step.active {
    color: var(--cyan);
}

.ai-step.done {
    color: var(--ink);
}

.ai-step-icon {
    font-size: 0.9rem;
    width: 16px;
    text-align: center;
}

.ai-step.active .ai-step-icon {
    animation: pulse 1.5s infinite;
}

/* ---------- Inputs ---------- */

.stTextInput input, .stChatInput textarea {
    background: var(--bg-panel-2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    color: var(--ink) !important;
    font-family: 'JetBrains Mono', monospace !important;
    padding: 0.7rem 0.9rem !important;
}

.stTextInput input:focus, .stChatInput textarea:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px rgba(242,166,90,0.18) !important;
}

[data-testid="stFileUploader"] {
    border: 1px dashed var(--line);
    border-radius: 14px;
    padding: 0.8rem;
    background: rgba(0,0,0,0.18);
}

[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex;
    gap: 4px;
    background: var(--bg-panel-2);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 4px;
}

[data-testid="stRadio"] label {
    flex: 1;
    justify-content: center;
    margin: 0 !important;
    padding: 0.55rem 0.8rem !important;
    border-radius: 9px;
    transition: all 0.15s ease;
}

[data-testid="stRadio"] label p {
    color: var(--ink-dim) !important;
    font-size: 0.86rem !important;
    margin: 0 !important;
}

[data-testid="stRadio"] label:has(input:checked) {
    background: var(--amber);
}

[data-testid="stRadio"] label:has(input:checked) p {
    color: #0f1115 !important;
    font-weight: 600 !important;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #f5f5f5, #dddddd) !important;
    color: #0f1115 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 1.2rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0.04em !important;
    font-size: 0.85rem !important;
    transition: all 0.18s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(242,166,90,0.25);
}

[data-testid="stChatMessage"] {
    background: var(--bg-panel-2);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 0.5rem;
    margin-bottom: 1rem;
}

[data-testid="stStatus"] {
    background: var(--bg-panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: 16px !important;
}

.log-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--ink-dim);
    margin: 0.2rem 0;
}

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: var(--bg-panel-2); border-radius: 10px; }

:focus-visible {
    outline: 2px solid var(--cyan) !important;
    outline-offset: 2px !important;
}

@media (max-width: 640px) {
    .console-title { font-size: 1.6rem; }
    .console-row { align-items: flex-start; }
}



/* ---------- Notion-style polish ---------- */

* {
    transition:
        background 0.18s ease,
        border-color 0.18s ease,
        transform 0.18s ease;
}

.console-title {
    letter-spacing: -0.04em;
}

.console-subtitle {
    max-width: 680px;
    line-height: 1.6;
}

.status-panel {
    background: rgba(255,255,255,0.03);
    border-radius: 999px;
}

.insight-card.hero {
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.05),
            rgba(255,255,255,0.02)
        );
    border-left: none;
}

.card-body {
    color: rgba(255,255,255,0.78);
    margin-top: 0.55rem;
}

[data-testid="stChatMessage"] {
    background: rgba(26,28,34,0.85);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 0.9rem;
    backdrop-filter: blur(14px);
}

.stChatInput {
    position: sticky;
    bottom: 1rem;
}

[data-testid="stFileUploader"] {
    border-radius: 18px;
    border: 1px dashed rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.02);
}

[data-testid="stRadio"] > div[role="radiogroup"] {
    background: rgba(255,255,255,0.03);
    border-radius: 14px;
}

[data-testid="stRadio"] label {
    border: 1px solid transparent;
}

[data-testid="stRadio"] label:hover {
    border-color: rgba(255,255,255,0.08);
}

.ai-loading-card {
    padding: 1.1rem 1.3rem;
    border-radius: 22px;
}

.empty-panel {
    background: rgba(255,255,255,0.02);
    border-radius: 22px;
    padding: 3rem 2rem;
    text-align: center;
    color: rgba(255,255,255,0.4);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    border: 1px dashed rgba(255,255,255,0.1);
}

@media (max-width: 768px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .console {
        padding: 1rem;
    }

    .console-title {
        font-size: 1.45rem;
    }

    .panel {
        padding: 1rem;
    }

    .status-panel {
        width: 100%;
        justify-content: center;
    }

    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }

    .insight-card {
        min-height: auto;
    }
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def insight_card_html(label, body, led_class):
    return f"""
    <div class="insight-card grid-card">
        <p class="card-label"><span class="led {led_class}"></span>{html.escape(label)}</p>
        <p class="card-body">{html.escape(str(body))}</p>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
bars = "".join("<span></span>" for _ in range(12))

header_html = (
    '<div class="console">'
    '<div class="console-row">'
    '<div>'
    '<p class="console-eyebrow">Meeting intelligence</p>'
    '<p class="console-title">🎙️ AI Meeting Assistant</p>'
    '<p class="console-subtitle">Transcribe · Summarize · Extract insights · Chat with any meeting</p>'
    f'<div class="waveform">{bars}</div>'
    '</div>'
    '<div class="status-panel">'
    '<span class="status-dot"></span>'
    '<span class="status-text">WHISPER + RAG ENGINE · READY</span>'
    '</div>'
    '</div>'
    '</div>'
)

st.markdown(header_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CACHED FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def process_and_transcribe(source, is_file=False, file_bytes=None, language_choice=None, file_suffix=".mp4", user_context=None):
    clear_downloads()

    transcript = ""
    is_youtube = False
    metadata_str = ""

    if not is_file:
        is_youtube = source.startswith("http://") or source.startswith("https://")

        if is_youtube:
            try:
                import yt_dlp
                ydl_opts = {'quiet': True, 'skip_download': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(source, download=False)
                    v_title = info.get('title', '')
                    channel = info.get('uploader', '')
                    description = info.get('description', '')
                    if v_title or channel or description:
                        metadata_str = f"Video Title: {v_title}\nChannel: {channel}\nDescription: {description}\n\n---\n\nTranscript:\n"
            except Exception:
                pass

            from youtube_transcript_api import YouTubeTranscriptApi

            if "v=" in source:
                video_id = source.split("v=")[1].split("&")[0]
            elif "youtu.be/" in source:
                video_id = source.split("youtu.be/")[1].split("?")[0]
            else:
                video_id = source

            try:
                transcript_list = YouTubeTranscriptApi().list(video_id)

                try:
                    transcript_obj = transcript_list.find_transcript(['en'])
                    transcript_data = transcript_obj.fetch()
                    transcript = " ".join(f"[{int(chunk['start'])//60:02d}:{int(chunk['start'])%60:02d}] {chunk['text']}" for chunk in transcript_data)

                except Exception:
                    transcript_obj = transcript_list.find_transcript(['hi'])

                    try:
                        translated_obj = transcript_obj.translate('en')
                        transcript_data = translated_obj.fetch()
                        transcript = " ".join(f"[{int(chunk['start'])//60:02d}:{int(chunk['start'])%60:02d}] {chunk['text']}" for chunk in transcript_data)

                    except Exception:
                        pass # Fallback to Whisper which will translate it locally very fast

            except Exception:
                pass

    if not transcript:
        if is_file and file_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp_file:
                tmp_file.write(file_bytes)
                media_path = tmp_file.name
                
            if file_suffix.lower() != ".wav":
                import subprocess
                wav_path = media_path + ".wav"
                try:
                    subprocess.run(["ffmpeg", "-y", "-i", media_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav_path], check=True, capture_output=True)
                    os.remove(media_path)
                    media_path = wav_path
                except Exception as e:
                    print(f"FFmpeg conversion failed: {e}")
        else:
            media_path = process_input(source)

        transcript = transcribe_audio(
            media_path,
            language_code=language_choice
        )

        if is_file and file_bytes:
            try:
                os.remove(media_path)
            except Exception:
                pass

    if metadata_str and transcript:
        transcript = metadata_str + transcript

    if user_context and transcript:
        transcript = f"User Provided Context:\n{user_context}\n\n---\n\n" + transcript

    return transcript


@st.cache_resource(show_spinner=False)
def analyze_transcript(transcript):
    # Run sequentially to prevent local Ollama/GPU from thrashing or OOMing
    # by attempting to process multiple heavy LLM prompts simultaneously.
    summary = summarize(transcript)
    title = create_title(summary)
    insights = extract_insights(transcript)
    rag_chain = build_rag_chain(transcript)
        
    return title, summary, insights, rag_chain


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for key, default in [
    ("chat_history", []),
    ("transcript", None),
    ("analysis", None),
    ("rag_chain", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<p class="step-eyebrow">Step 01 — Source</p>'
        '<p class="section-title">📥 Choose your source</p>',
        unsafe_allow_html=True,
    )

    input_type = st.radio(
        "Input source",
        ["YouTube URL", "Upload File"],
        horizontal=False,
        label_visibility="collapsed",
    )

    source_url = ""
    uploaded_file = None

    if input_type == "YouTube URL":
        source_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload video or audio file",
            type=["mp4", "mkv", "mp3", "wav", "m4a"],
            label_visibility="collapsed",
        )
        
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        '<p class="step-eyebrow">Step 02 — Language</p>'
        '<p class="section-title">🌐 Language mode</p>',
        unsafe_allow_html=True,
    )

    lang_option = st.radio(
        "Language mode",
        ["Auto-detect (English default)", "Hindi / Hinglish"],
        horizontal=False,
        label_visibility="collapsed",
    )

    language_choice = "hi" if "Hindi" in lang_option else None

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        '<p class="step-eyebrow">Step 03 — Context (Optional)</p>'
        '<p class="section-title">📝 Additional info</p>',
        unsafe_allow_html=True,
    )
    
    user_context = st.text_area(
        "Context",
        placeholder="e.g. This is a weekly standup for the engineering team. John is the PM.",
        label_visibility="collapsed"
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        '<p class="step-eyebrow">Step 04 — Run</p>'
        '<p class="section-title">▶️ Process the meeting</p>',
        unsafe_allow_html=True,
    )

    process_clicked = st.button("▶  PROCESS MEETING")

# ─────────────────────────────────────────────────────────────────────────────
# PROCESSING
# ─────────────────────────────────────────────────────────────────────────────
if process_clicked:

    if input_type == "YouTube URL" and not source_url:
        st.error("Please enter a YouTube URL.")

    elif input_type == "Upload File" and not uploaded_file:
        st.error("Please upload a file.")

    else:
        st.session_state.chat_history = []

        with st.status("Processing meeting…", expanded=True) as status:

            st.write("fetching transcript…")

            is_file = (input_type == "Upload File")
            file_bytes = uploaded_file.read() if is_file else None
            file_suffix = os.path.splitext(uploaded_file.name)[1] if (is_file and uploaded_file and uploaded_file.name) else ".mp4"
            source = source_url if not is_file else ""

            transcript = process_and_transcribe(
                source,
                is_file=is_file,
                file_bytes=file_bytes,
                language_choice=language_choice,
                file_suffix=file_suffix,
                user_context=user_context,
            )

            st.session_state.transcript = transcript

            st.write("generating AI insights…")

            title, summary, insights, rag_chain = analyze_transcript(transcript)

            st.session_state.analysis = {
                "title": title,
                "summary": summary,
                "insights": insights,
            }

            st.session_state.rag_chain = rag_chain

            st.session_state.media = {
                "type": input_type,
                "source_url": source_url,
                "file_bytes": file_bytes,
                "file_suffix": file_suffix
            }

            status.update(
                label="✅ Analysis complete",
                state="complete",
                expanded=False
            )

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<hr class="hr">', unsafe_allow_html=True)

if st.session_state.analysis:

    a = st.session_state.analysis

    st.markdown(
        '<p class="step-eyebrow">Output</p>'
        '<p class="section-title">📊 Meeting insights</p>',
        unsafe_allow_html=True,
    )

    # MEDIA PLAYER
    if st.session_state.get("media"):
        m = st.session_state.media
        st.markdown(
            '<div class="insight-card">'
            '<p class="card-label">Original Media</p>',
            unsafe_allow_html=True,
        )
        if m["type"] == "YouTube URL":
            st.video(m["source_url"])
        else:
            if m["file_suffix"].lower() in [".mp4", ".mkv", ".mov"]:
                st.video(m["file_bytes"])
            else:
                st.audio(m["file_bytes"])
        st.markdown('</div>', unsafe_allow_html=True)

    # TITLE CARD
    st.markdown(
        f'<div class="insight-card hero">'
        f'<p class="card-label">Meeting title</p>'
        f'<p class="card-title">{html.escape(str(a["title"]))}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # SUMMARY CARD
    st.markdown(
        f'<div class="insight-card">'
        f'<p class="card-label">Summary</p>'
        f'<p class="card-body">{html.escape(str(a["summary"]))}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # INSIGHT GRID
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            insight_card_html(
                "Action items",
                a["insights"].get("action_items", "None identified."),
                "led-cyan",
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            insight_card_html(
                "Key decisions",
                a["insights"].get("key_decisions", "None identified."),
                "led-amber",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            insight_card_html(
                "Open questions",
                a["insights"].get("questions", "None identified."),
                "led-rose",
            ),
            unsafe_allow_html=True,
        )

    # CHAT SECTION
    st.markdown('<hr class="hr">', unsafe_allow_html=True)

    st.markdown(
        '<p class="step-eyebrow">Ask away</p>'
        '<p class="section-title">💬 Chat with this meeting</p>',
        unsafe_allow_html=True,
    )

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything about the meeting..."):

        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            formatted_history = str([
                (m["role"], m["content"])
                for m in st.session_state.chat_history[:-1]
            ])

            with st.spinner("Thinking..."):

                response = ask_question(
                    st.session_state.rag_chain,
                    prompt,
                    formatted_history
                )

            st.markdown(response)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

else:
    st.markdown(
        '<div class="empty-panel">STANDING BY — paste a YouTube link or upload a recording above, '
        'then hit Process Meeting to see the transcript, summary, and insights here.</div>',
        unsafe_allow_html=True,
    )