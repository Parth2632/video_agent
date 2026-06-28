import streamlit as st
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, create_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question


# ----------------------------------------------------------------------------
# Theme
#
# Visual concept: a tape deck / studio control panel. Charcoal panels, brass
# and signal-red accents borrowed from VU meters and reel-to-reel hardware,
# a monospace face for anything that reads like a counter or log line.
# ----------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --ink: #14181A;
    --panel: #1B2023;
    --panel-soft: #20262A;
    --line: #333A3D;
    --paper: #EDE7DA;
    --paper-dim: #9C968D;
    --brass: #C99A4B;
    --brass-bright: #DDB36A;
    --signal: #C0524B;
    --sage: #7A9485;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: var(--ink) !important;
    color: var(--paper);
    font-family: 'IBM Plex Sans', sans-serif;
}

[data-testid="stHeader"] { background: transparent; }

[data-testid="stSidebar"] {
    background: var(--panel) !important;
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] * { color: var(--paper) !important; }

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.01em;
}

*:focus-visible { outline: 2px solid var(--brass); outline-offset: 2px; }

/* small typographic devices */
.eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--brass);
    margin-bottom: 0.3rem;
}
.subtle {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: var(--paper-dim);
}
.sprocket-rule {
    display: flex; align-items: center; gap: 7px;
    margin: 0.5rem 0 1.6rem 0;
}
.sprocket-rule .line { flex: 1; height: 1px; background: var(--line); }
.sprocket-rule .dot { width: 5px; height: 5px; border-radius: 50%; background: var(--line); flex-shrink: 0; }

/* inputs */
[data-testid="stTextInput"] input {
    background: var(--panel-soft) !important;
    border: 1px solid var(--line) !important;
    color: var(--paper) !important;
    font-family: 'IBM Plex Mono', monospace;
    border-radius: 8px;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--brass) !important;
    box-shadow: 0 0 0 1px var(--brass) !important;
}

/* buttons */
.stButton button {
    background: var(--brass) !important;
    color: var(--ink) !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    letter-spacing: 0.03em;
    padding: 0.55rem 1rem;
    transition: background 0.15s ease;
}
.stButton button:hover { background: var(--brass-bright) !important; }
.stButton button[kind="secondary"] {
    background: transparent !important;
    color: var(--paper-dim) !important;
    border: 1px solid var(--line) !important;
}
.stButton button[kind="secondary"]:hover { color: var(--paper) !important; border-color: var(--paper-dim) !important; }

/* chat input */
[data-testid="stChatInput"] textarea {
    background: var(--panel-soft) !important;
    border: 1px solid var(--line) !important;
    color: var(--paper) !important;
    border-radius: 8px;
}

/* alerts */
[data-testid="stAlert"] {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-left: 3px solid var(--brass) !important;
    border-radius: 6px !important;
    color: var(--paper) !important;
}

/* bordered containers used for insight cards */
[data-testid="stVerticalBlockBorderWrapper"], .stVerticalBlockBorderWrapper {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
}

.card-tab {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 2px 9px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 0.7rem;
}
.tab-summary    { background: rgba(201,154,75,0.15); color: var(--brass); }
.tab-questions  { background: rgba(122,148,133,0.15); color: var(--sage); }
.tab-actions    { background: rgba(122,148,133,0.15); color: var(--sage); }
.tab-decisions  { background: rgba(192,82,75,0.15); color: var(--signal); }

/* progress checklist */
.step-row {
    display: flex; align-items: baseline; gap: 10px;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.86rem;
    color: var(--paper-dim); padding: 4px 0;
}
.step-row .marker { width: 16px; display: inline-block; }
.step-row.done { color: var(--sage); }
.step-row.active { color: var(--brass); }
.step-row.active .marker { animation: pulse 1.3s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
@media (prefers-reduced-motion: reduce) { .step-row.active .marker { animation: none; } }

/* chat bubbles */
.bubble-row { display: flex; margin: 0.35rem 0; }
.bubble-row.user { justify-content: flex-end; }
.bubble {
    max-width: 78%;
    padding: 0.6rem 0.85rem;
    border-radius: 10px;
    font-size: 0.92rem;
    line-height: 1.5;
}
.bubble-user { background: var(--panel-soft); border: 1px solid var(--line); }
.bubble-assistant { background: rgba(201,154,75,0.08); border: 1px solid rgba(201,154,75,0.25); }
.bubble-meta {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    color: var(--paper-dim); margin-bottom: 3px; letter-spacing: 0.04em;
}
</style>
"""

STEP_LABELS = [
    "Reading source",
    "Transcribing audio",
    "Summarizing & titling",
    "Extracting insights",
    "Indexing for Q&A",
]


# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------

def initialize_session_state():
    defaults = {
        "rag_chain": None,
        "chat_history": [],
        "results": None,
        "session_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ----------------------------------------------------------------------------
# Small render helpers
# ----------------------------------------------------------------------------

def eyebrow(text: str):
    st.markdown(f'<div class="eyebrow">{text}</div>', unsafe_allow_html=True)


def sprocket_rule():
    st.markdown(
        '<div class="sprocket-rule"><span class="dot"></span><span class="line"></span>'
        '<span class="dot"></span></div>',
        unsafe_allow_html=True,
    )


def source_kind_label(source: str) -> str:
    s = source.strip().lower()
    if s.startswith("http://") or s.startswith("https://"):
        return "URL / YOUTUBE"
    if s:
        return "LOCAL FILE"
    return ""


def render_steps(box, current_index: int, total: int):
    rows = []
    for i, label in enumerate(STEP_LABELS):
        if i < current_index:
            cls, marker = "done", "✓"
        elif i == current_index:
            cls, marker = "active", "▸"
        else:
            cls, marker = "", "·"
        rows.append(
            f'<div class="step-row {cls}"><span class="marker">{marker}</span>{label}</div>'
        )
    box.markdown("".join(rows), unsafe_allow_html=True)


def insight_card(eyebrow_text: str, tab_class: str, content: str):
    with st.container(border=True):
        st.markdown(
            f'<span class="card-tab {tab_class}">{eyebrow_text}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(content if content else "_Nothing surfaced here._")


def render_chat_bubble(role: str, content: str, timestamp: str):
    row_cls = "user" if role == "user" else ""
    bubble_cls = "bubble-user" if role == "user" else "bubble-assistant"
    label = "YOU" if role == "user" else "ASSISTANT"
    st.markdown(
        f'<div class="bubble-row {row_cls}"><div class="bubble {bubble_cls}">'
        f'<div class="bubble-meta">{label} · {timestamp}</div>{content}</div></div>',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Pipeline
# ----------------------------------------------------------------------------

def run_pipeline_streamlit(source: str):
    step_box = st.empty()
    render_steps(step_box, 0, len(STEP_LABELS))

    transcript = ""
    is_youtube = source.strip().lower().startswith(("http://", "https://"))
    
    if is_youtube:
        import re
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Extract video ID
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", source)
        if match:
            video_id = match.group(1)
            # Try to fetch transcript, allowing translation/auto-gen fallback if needed
            try:
                transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=['en'])
                transcript = " ".join(chunk.text for chunk in transcript_list)
            except Exception as e:
                raise ValueError(f"Could not fetch YouTube transcript: {e}")
        else:
            raise ValueError("Invalid YouTube URL")
            
        render_steps(step_box, 2, len(STEP_LABELS)) # skip step 1 since it's instant
    else:
        chunks = process_input(source)
        render_steps(step_box, 1, len(STEP_LABELS))
        transcript = transcribe_all(chunks)

    render_steps(step_box, 2, len(STEP_LABELS))
    summary = summarize(transcript)
    title = create_title(summary)

    render_steps(step_box, 3, len(STEP_LABELS))
    actions = extract_action_items(transcript)
    questions = extract_questions(transcript)
    decisions = extract_key_decisions(transcript)

    render_steps(step_box, 4, len(STEP_LABELS))
    rag_chain = build_rag_chain(transcript)

    render_steps(step_box, len(STEP_LABELS), len(STEP_LABELS))

    return {
        "title": title,
        "summary": summary,
        "action_items": actions,
        "questions": questions,
        "key_decisions": decisions,
        "rag_chain": rag_chain,
    }


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="AI Meeting Assistant", page_icon="▮", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    initialize_session_state()

    st.markdown(
        '<div style="font-family:\'Space Grotesk\',sans-serif;font-weight:700;'
        'font-size:1.7rem;color:var(--paper);margin-bottom:0.1rem;">▮ Meeting Assistant</div>'
        '<div class="subtle" style="margin-bottom:1.6rem;">'
        'Turns recordings and YouTube links into transcripts, summaries, and a Q&amp;A line.</div>',
        unsafe_allow_html=True,
    )

    # ---------------- Sidebar ----------------
    with st.sidebar:
        eyebrow("New session")
        st.markdown("#### Drop in a source")
        source = st.text_input(
            "Source",
            placeholder="https://youtube.com/... or /path/to/file.mp4",
            label_visibility="collapsed",
        )
        if source.strip():
            st.markdown(f'<div class="subtle">{source_kind_label(source)}</div>', unsafe_allow_html=True)

        process_clicked = st.button("▸  Start transcription", type="primary", use_container_width=True)

        if st.session_state.results:
            if st.button("Clear session", type="secondary", use_container_width=True):
                st.session_state.results = None
                st.session_state.rag_chain = None
                st.session_state.chat_history = []
                st.rerun()

        st.markdown(
            '<div style="margin-top:1.5rem;" class="subtle">'
            'Accepts a YouTube URL or a path to a local audio/video file. One pass covers '
            'transcription, summary, and insight extraction.</div>',
            unsafe_allow_html=True,
        )

    # ---------------- Pipeline trigger ----------------
    if process_clicked:
        if source and source.strip():
            try:
                results = run_pipeline_streamlit(source.strip())
                st.session_state.results = results
                st.session_state.rag_chain = results["rag_chain"]
                st.session_state.chat_history = []
                st.session_state.session_count += 1
            except Exception as e:
                st.error(f"Couldn't process that source — {e}")
        else:
            st.warning("Add a source in the sidebar before starting.")

    # ---------------- Results ----------------
    if st.session_state.results:
        results = st.session_state.results
        eyebrow(f"Session {st.session_state.session_count:03d}")
        st.markdown(f"## {results['title']}")
        sprocket_rule()

        col1, col2 = st.columns(2)
        with col1:
            insight_card("Summary", "tab-summary", results["summary"])
            insight_card("Open questions", "tab-questions", results["questions"])
        with col2:
            insight_card("Action items", "tab-actions", results["action_items"])
            insight_card("Key decisions", "tab-decisions", results["key_decisions"])

        sprocket_rule()
        eyebrow("Q&A")
        st.markdown("#### Ask anything about this session")

        for message in st.session_state.chat_history:
            render_chat_bubble(message["role"], message["content"], message["time"])

        if prompt := st.chat_input("Ask a question..."):
            now = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append({"role": "user", "content": prompt, "time": now})
            render_chat_bubble("user", prompt, now)

            with st.spinner("Thinking..."):
                answer = ask_question(st.session_state.rag_chain, prompt)

            now = datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append({"role": "assistant", "content": answer, "time": now})
            render_chat_bubble("assistant", answer, now)

    else:
        eyebrow("Idle")
        st.markdown("#### No session yet")
        st.markdown(
            '<div class="subtle">Drop a YouTube link or a local file path into the sidebar '
            'and start transcription — the summary, action items, and Q&amp;A line will appear here.</div>',
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()