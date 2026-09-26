# 🎬 End-to-End YouTube AI Assistant (RAG Pipeline)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Groq API](https://img.shields.io/badge/Groq-API-f50.svg)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-green.svg)](https://www.trychroma.com/)

A modern, high-performance **Retrieval-Augmented Generation (RAG)** assistant that enables users to query, summarize, and auto-generate quizzes from YouTube videos in real time. 

Built with an adaptive transcription pipeline, **ChromaDB** vector database, Groq's high-speed **Whisper** model for audio processing, and **OpenAI GPT-OSS-120B** for inference, all wrapped inside a sleek **Glassmorphism Streamlit UI**.

---

## 🌟 Key Features

* **💬 Interactive Q&A (Context-Aware Chat):** Ask questions about any processed YouTube video and get precise, structured responses based strictly on video content.
* **📝 Executive Summary Generator:** Generates key takeaways, core messages, and structured bullet points.
* **🧩 Automated Practice Quiz Generator:** Automatically creates 3 multiple-choice questions (MCQs) with correct answers and explanations for self-assessment.
* **⚡ Adaptive Transcription Pipeline:** Uses official YouTube captions first (`en`, `hi`, `bn`). Falls back to downloading and slicing raw audio into lightweight chunks via `FFmpeg` and transcribing with `Groq Whisper` if captions are missing.
* **💎 Glassmorphism Dashboard UI:** Custom-styled dark-mode interface built using Streamlit and tailored CSS styling.

---

## 🏗️ System Architecture & Workflow

[ YouTube URL ]
│
▼
[ Ingestion Layer (ingest.py) ]
├── 1. Check YouTube Captions API (en/hi/bn -> English Translate)
└── 2. Fallback: Download via yt-dlp ──► Slice 5-min 64kbps MP3s (FFmpeg)
│
▼
Groq Whisper API (whisper-large-v3)
│
▼
[ Vector Database (vector_store.py) ] ◄── Full Transcript
└── Recursive Text Splitting (Chunk: 1000, Overlap: 200)
└── Store In-Memory ChromaDB Collection
│
▼
[ RAG Engine & LLM (rag_chain.py) ] ◄──── User Query / Action
├── Vector Similarity Search (Top-4 Retrieval)
└── Groq LLM Inference (openai/gpt-oss-120b)
│
▼
[ Interactive UI (app.py) ] ◄──────────── Formatted Response

## 📁 Repository File Structure & Functionalities

| File Name | Description & Usage |
| :--- | :--- |
| **`app.py`** | Main entry point for the Streamlit web app. Handles multi-tab UI navigation, session state management, and user interactions. |
| **`ingest.py`** | Audio downloading and speech-to-text pipeline. Integrates `youtube_transcript_api`, `yt-dlp`, `imageio-ffmpeg`, and Groq Whisper. |
| **`vector_store.py`** | Document processing module. Splits raw transcripts into character chunks and manages ChromaDB vector collection storage. |
| **`rag_chain.py`** | RAG inference logic. Executes vector context retrieval and prompts Groq's `openai/gpt-oss-120b` for Q&A, summaries, and quizzes. |
| **`style.css`** | Custom CSS stylesheet injecting dark glassmorphism effects, shadows, and rounded container designs into Streamlit. |
| **`requirements.txt`** | Dependency manifest containing precise Python library versions required to run the application. |
| **`.gitignore`** | Excludes sensitive environment variables (`.env`), Python caches, and temporary audio files from Git history. |

---

## 🛠️ Tech Stack & Dependencies

* **Frontend:** [Streamlit](https://streamlit.io/) + Custom CSS
* **Audio & Video Processing:** `yt-dlp`, `imageio-ffmpeg`, `youtube_transcript_api`
* **Embedding & Retrieval:** [ChromaDB](https://www.trychroma.com/), [LangChain Text Splitters](https://python.langchain.com/)
* **Speech-to-Text Model:** `whisper-large-v3` (via Groq)
* **LLM Model:** `openai/gpt-oss-120b` (via Groq)
* **Configuration:** `python-dotenv`

---

## 🚀 Getting Started

Follow these steps to set up and run the project locally on your machine.

### Prerequisites
* Python 3.10 or higher
* Git
* A free [Groq API Key](https://console.groq.com/)

### 1. Clone the Repository
```bash
git clone [https://github.com/dipjoydebnath/youtube-rag-assistant.git](https://github.com/dipjoydebnath/youtube-rag-assistant.git)
cd youtube-rag-assistant

2. Set Up Virtual Environment
Windows (PowerShell):

PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
macOS / Linux:

Bash
python3 -m venv venv
source venv/bin/activate
3. Install Required Dependencies
Bash
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file in the project root directory and add your Groq API key:

Ini, TOML
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
5. Launch the Streamlit Application
Bash
streamlit run app.py
After executing the command, Streamlit will open the application in your default web browser at http://localhost:8501.

💡 How to Use
Enter YouTube Video URL: Paste any valid YouTube video link into the sidebar input field.

Process Video: Click 🚀 Process Video. The pipeline will automatically extract captions or transcribe raw audio into ChromaDB.

Ask Questions: Navigate to 💬 Interactive Q&A and ask specific questions about the video content.

Generate Summary: Open 📝 Executive Summary tab to generate key takeaways and bullet points.

Practice Quiz: Open 🧩 Practice Quiz tab to auto-generate multiple-choice comprehension questions.
