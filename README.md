# 🎙️ AI Video & Meeting Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GPU Required](https://img.shields.io/badge/GPU-NVIDIA_CUDA-green.svg)]()

An AI-powered terminal application that transforms YouTube videos and local video/audio files into structured meeting insights. It generates transcripts, meeting summaries, action items, key decisions, and enables semantic question answering over transcripts using Retrieval-Augmented Generation (RAG).

---

## 📸 Demo

*(Placeholder: Add your terminal recording or `asciinema` GIF here)*
![Terminal Demo](https://via.placeholder.com/800x400?text=Terminal+Demo+GIF+Placeholder)

---

# ✨ Features

### 🎥 Media Processing
* Supports both YouTube URLs and raw local video/audio files (e.g. `.mkv`, `.mp4`).
* Uses `youtube-transcript-api` to fetch YouTube transcripts when available.
* Streams and decodes media natively on-the-fly, bypassing the need for intermediate `.wav` conversions.

### ⚡ Optimized Local Speech-to-Text
* Powered by **faster-whisper** (CTranslate2 engine) for highly efficient, local GPU transcription.
* Configured by default to use the `tiny` model with `int8` quantization for maximum performance and minimal VRAM usage.
* Features built-in Voice Activity Detection (VAD) to skip silent parts and avoid manual chunking.

### 🧠 AI Meeting Analysis
Uses Mistral AI (or any LLM of your choice) via LangChain to automatically generate:
* Meeting title
* Summary
* Action items
* Key decisions
* Open questions

### 🔍 Retrieval-Augmented Generation (RAG)
* Splits transcripts into semantic chunks.
* Generates vector embeddings using HuggingFace Sentence Transformers.
* Stores embeddings in ChromaDB (optimized for batch processing).
* Features **Conversational Memory** to understand follow-up questions and pronouns based on chat history.
* Retrieves relevant transcript sections with LangChain to answer user queries right in your terminal.

---

# 🚀 Performance Tuning & Optimization Journey

This project was optimized to run efficiently on consumer hardware (specifically tested on an NVIDIA RTX A2000 GPU). Here is how we reduced the processing time for a 22-minute video from **54 minutes** down to **2 minutes**:

1. **The Starting Point (54 minutes):** The original architecture used the standard OpenAI `whisper` library with the `large-v2` model, and manually sliced audio into chunks using `pydub`. It was highly accurate but prohibitively slow and prone to memory overhead.
2. **Switching Engines (3 min 21 sec):** We replaced standard Whisper with `faster-whisper`, switched to the multilingual `base` model, and enabled `int8` quantization. This dropped the transcription time drastically.
3. **Removing Bottlenecks (2 min 5 sec):** We realized `pydub` was unnecessarily converting video files into intermediate `.wav` files on the hard drive. By passing the raw `.mkv` files directly into `faster-whisper` (which uses PyAV to stream audio into memory on-the-fly) and dropping the model size to `tiny`, we shaved off another 22 seconds and eliminated all manual audio chunking. 

*(Note: Of the final 2 minutes, roughly 45-60 seconds is network time waiting for the Mistral API to generate the summary. The actual GPU transcription takes barely a minute.)*

---

# 🛠️ Tech Stack

| Category         | Technologies                      |
| ---------------- | --------------------------------- |
| Language         | Python 3                          |
| UI               | Interactive Terminal CLI          |
| Speech-to-Text   | Faster-Whisper, YouTube API       |
| LLM              | Mistral AI / LangChain            |
| Vector Database  | ChromaDB                          |
| Embeddings       | HuggingFace Sentence Transformers |
| Media Decoding   | PyAV, FFmpeg                      |
| Machine Learning | PyTorch                           |

---

# 🚀 Setup

## Prerequisites

* Python 3.10+
* FFmpeg installed and available in your system PATH
* A CUDA-compatible NVIDIA GPU (highly recommended for performance)

Create a `.env` file:

```env
WHISPER_MODEL="tiny"
MISTRAL_API_KEY="your_mistral_api_key"
```

## Key Dependencies
While a full `requirements.txt` is provided, the core libraries powering this tool include:
- `faster-whisper` (Transcription)
- `langchain` & `langchain-community` (LLM orchestration and RAG)
- `chromadb` (Vector storage)
- `youtube-transcript-api` (Native YouTube caption extraction)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 💻 Usage

### Interactive Mode
Launch the application in your terminal to process a video and enter an interactive Q&A session:
```bash
python main.py
```

### Headless / Batch Mode
If you just want the transcription and summary generated without entering the interactive Q&A loop, run the headless version. This is ideal for background tasks or batch processing multiple videos:
```bash
python run_headless.py
```

---

# 🧠 System Architecture

```text
             YouTube URL / Local Video File
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
    YouTube API              Direct Streaming
 (Instant Transcript)        (PyAV / FFmpeg)
          │                         │
          │                         ▼
          │               Faster-Whisper (INT8)
          │               (Local GPU Inference)
          └────────────┬────────────┘
                       ▼
 Meeting Analysis            Transcript Chunking
   (Mistral AI)                       │
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

# 🤝 Contributing

Contributions are welcome! If you have ideas for optimization, new features, or bug fixes:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

# 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
