# 🎙️ AI Video & Meeting Assistant

An AI-powered application that transforms YouTube videos and local audio files into structured meeting insights. It generates transcripts, meeting summaries, action items, key decisions, and enables semantic question answering over transcripts using Retrieval-Augmented Generation (RAG).

---

# ✨ Features

### 🎥 Audio Extraction

* Supports both YouTube URLs and local audio/video files.
* Uses `yt-dlp` to download media from YouTube.
* Supports browser-cookie authentication for improved download reliability when required.

### 🎙️ Speech-to-Text

* Uses OpenAI Whisper for local speech-to-text transcription.
* Supports multiple Whisper models (`tiny`, `base`, `small`).
* Processes audio locally before transcript analysis.

### 🎵 Audio Preprocessing

* Converts audio to **mono, 16 kHz WAV** format using `pydub` for Whisper compatibility.
* Splits long recordings into fixed-duration chunks before transcription.
* Merges chunk-level transcriptions into a complete transcript.

### 🧠 AI Meeting Analysis

Uses Mistral AI to automatically generate:

* Meeting title
* Summary
* Action items
* Key decisions
* Open questions

### 🔍 Retrieval-Augmented Generation (RAG)

* Splits transcripts into semantic chunks.
* Generates vector embeddings using HuggingFace Sentence Transformers.
* Stores embeddings in ChromaDB.
* Retrieves relevant transcript sections with LangChain to answer user queries.

---

# 🎯 Use Cases

### 📋 Meeting Summarization

Generate concise meeting summaries, action items, and decisions from recorded meetings.

### 🎥 Content Analysis

Analyze YouTube videos, podcasts, interviews, and recorded discussions without manually searching through long recordings.

### 📚 Lecture & Research Assistant

Create searchable transcripts from lectures or seminars and ask natural language questions about the content.

---

# 🛠️ Tech Stack

| Category         | Technologies                      |
| ---------------- | --------------------------------- |
| Language         | Python 3                          |
| Speech-to-Text   | OpenAI Whisper                    |
| LLM              | Mistral AI                        |
| RAG Framework    | LangChain                         |
| Vector Database  | ChromaDB                          |
| Embeddings       | HuggingFace Sentence Transformers |
| Audio Processing | Pydub, FFmpeg                     |
| Video Download   | yt-dlp                            |
| Machine Learning | PyTorch                           |

---

# 🚀 Setup

## Prerequisites

* Python 3.10+
* FFmpeg installed and available in your system PATH

Create a `.env` file:

```env
MISTRAL_API_KEY="your_mistral_api_key"
WHISPER_MODEL="tiny"
HF_TOKEN="your_huggingface_token"
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

---

# 💻 Usage

1. Launch the application.

```bash
python main.py
```

2. Provide either:

* A YouTube URL
* A local audio/video file

3. The application will:

* Download or load the media
* Convert it to mono 16 kHz WAV
* Split the audio into manageable chunks
* Transcribe each chunk using Whisper
* Generate meeting insights using Mistral AI
* Build a vector database from the transcript

4. Ask questions about the transcript in the interactive terminal.

Type `exit` to leave the chat.

---

# 🧠 System Architecture

```text
             YouTube URL / Local File
                       │
                       ▼
              Audio Extraction
              (yt-dlp / Local File)
                       │
                       ▼
          Audio Preprocessing
      (Mono + 16 kHz Conversion)
                       │
                       ▼
             Audio Chunking
          (Fixed-Duration Segments)
                       │
                       ▼
          Whisper Transcription
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
 Meeting Analysis          Transcript Chunking
   (Mistral AI)                     │
                                    ▼
                  HuggingFace Embeddings
                                    │
                                    ▼
                              ChromaDB
                                    │
                                    ▼
                         LangChain Retriever
                                    │
                                    ▼
                        Interactive RAG Q&A
```

---

# 📂 Project Structure

```text
AI-Video-Meeting-Assistant/
│
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
│
├── utils/
│   └── audio_processor.py
│
├── main.py
├── requirements.txt
└── .env
```

---

# 🎯 Concepts Demonstrated

* Retrieval-Augmented Generation (RAG)
* Large Language Model (LLM) Integration
* OpenAI Whisper Integration
* Semantic Search
* Vector Databases (ChromaDB)
* Text Embeddings
* Prompt Engineering
* Audio Preprocessing
* Audio Processing
* Modular Software Architecture
