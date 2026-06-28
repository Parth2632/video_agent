# 🎙️ AI Video & Meeting Assistant

An intelligent, terminal-based AI pipeline that processes YouTube videos or local audio files to generate transcripts, comprehensive summaries, action items, and a fully interactive Q&A session using Retrieval-Augmented Generation (RAG).

## ✨ Features

- **Robust Audio Extraction**: Bypasses YouTube's bot-detection mechanisms via user-agent spoofing and encrypted cookie fallback (Chrome/Edge DPAPI parsing).
- **Local AI Transcription**: Uses OpenAI's **Whisper** (tiny/base models) to securely and privately transcribe audio directly on your CPU without relying on external transcription APIs.
- **Memory-Safe Audio Processing**: Leverages `pydub` to process audio files entirely in-memory, avoiding common Windows `ffmpeg` sub-process crashes when bridging to PyTorch.
- **Automated Intelligence**: Integrates **Mistral AI** to instantly generate an intelligent meeting title, concise summary, action items, and key decisions.
- **Interactive Q&A Engine**: Uses `ChromaDB` and `HuggingFaceEmbeddings` to vectorize the transcript, allowing you to ask semantic questions about the meeting right from the terminal.

## 🛠️ Tech Stack

- **Core & Extraction**: `Python 3`, `yt-dlp`, `pydub`, `ffmpeg`
- **Machine Learning**: `PyTorch`, `OpenAI Whisper`
- **LLM & RAG**: `Mistral AI`, `LangChain`, `ChromaDB`, `HuggingFace sentence-transformers`

## 🚀 Setup Instructions

### 1. System Requirements
- Python 3.10+
- **FFmpeg** must be installed and added to your Windows system PATH (or placed in the `.venv/Scripts/` directory).

### 2. Environment Variables
Create a `.env` file in the root directory with the following variables:
```env
MISTRAL_API_KEY="your_mistral_api_key_here"
WHISPER_MODEL="tiny" # Options: tiny, base, small
HF_TOKEN="your_huggingface_token" # Used to authenticate vector embeddings
SARVAM_API_KEY="your_sarvam_api_key" # Optional STT fallback
SARVAM_STT_MODEL="saaras:v3"
```

### 3. Installation
Install the required dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

Run the main pipeline directly from your terminal:

```bash
python main.py
```

1. **Input**: The script will prompt you for a YouTube URL or a local file path.
2. **Processing**: It will securely download, chunk, and locally transcribe the audio.
3. **Report**: You will receive a structured output of the Summary, Action Items, and Open Questions.
4. **Q&A**: You will drop into an interactive chat mode where you can ask specific questions about the transcript. Type `exit` to quit.

## 🧠 Architecture Overview

1. `utils/audio_processor.py`: Securely downloads the target video using `yt-dlp` and chunk-processes it into raw WAV format.
2. `core/transcriber.py`: Loads the raw audio frames directly into `numpy` memory blocks and feeds them into the Whisper model.
3. `core/extractor.py` & `core/summarizer.py`: Prompts the Mistral LLM to analyze the finalized transcript and extract structured data points.
4. `core/vector_store.py`: Slices the transcript into embeddings and stores them in an ephemeral `Chroma` instance.
5. `core/rag_engine.py`: Takes the user's interactive prompts, retrieves the most relevant transcript nodes, and synthesizes a context-aware answer.
