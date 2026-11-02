# 🎓 StudyEngine: Elite University Exam Prep & Lecture Synthesizer

> Transform messy YouTube degree lectures into textbook-grade notes, exact LaTeX mathematical derivations, timed MCQs (-0.25 negative marking), and typed subjective mock exams with rubrics.

![StudyEngine Clean Modern Ledger](https://img.shields.io/badge/UI-Clean%20Modern%20Ledger-171717?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square)

---

## ⚡ The Problem It Solves

Online degree students typically have 4–5 subjects per semester, each organized into 4 or 8 modules with 20–30 video lectures per module. Existing tools either:
- Rely on basic summaries that miss formulas and derivations.
- Fail on missing or non-English YouTube transcripts (`429 Too Many Requests`).
- Overwhelm LLMs with messy context windows, leading to hallucinated formulas and superficial notes.

**StudyEngine** solves this with a **3-tier fail-safe ingestion pipeline** and an **academic examination synthesizer**:
1. **Multi-tier Transcript Pipeline:** Immediate YouTube transcript extraction with automatic fallback to `yt-dlp` captions and on-device **Faster-Whisper** audio transcription. Zero failed lectures.
2. **Textbook-Grade Lecture Notes:** Full theoretical exposition, explicit KaTeX LaTeX block (`$$...$$`) equations, exhaustive variable definition tables, step-by-step worked numerical examples, comparative matrices, and Mermaid decision flowcharts.
3. **Timed Exam Testing Room:** Timed MCQ assessments (-0.25 negative marking) with comprehensive distractor traps, plus typed subjective questions with official university rubrics.
4. **Hierarchical Knowledge Vault:** Organized systematically by Course $\rightarrow$ Module (4 or 8 modules) $\rightarrow$ Lecture Topics with real video titles.

---

## 🛠️ Tech Stack & Architecture

- **Backend:** FastAPI, Python 3.11+, Uvicorn, SQLite (`study_vault.db`), Pydantic
- **Speech-to-Text & Ingestion:** `youtube-transcript-api`, `yt-dlp`, `faster-whisper` (int8 on CPU/Neural Engine), `curl-cffi`
- **Inference & LLM:** NVIDIA NIM API (Nemotron 3.5 Bolt / Mistral Large) with built-in token-bucket rate limiter ($\le 35$ req/min cap)
- **Frontend:** Clean Modern Ledger design language, Tailwind CSS, Geist Sans typography, KaTeX for math rendering, Mermaid.js for diagrams, Lucide icons

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Gupta-Garv/study-engine.git
cd study-engine

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file:
```env
NVIDIA_API_KEY=your_nvidia_nim_key_here
PORT=8000
HOST=0.0.0.0
```

### 3. Run the Server
```bash
uvicorn app.server:app --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in your browser.

---

## ☁️ 1-Click Deployment (Get Rid of Localhost)

### Option A: Hugging Face Spaces (Free 24/7 Cloud Hosting)
1. Go to [Hugging Face Spaces](https://huggingface.co/new-space).
2. Choose **Docker** SDK and select **Blank**.
3. Push or connect this GitHub repository.
4. In Space Settings $\rightarrow$ **Variables and secrets**, add `NVIDIA_API_KEY`.
5. Your app is live with a permanent URL `https://<your-username>-study-engine.hf.space`!

### Option B: Render / Railway
1. Click **New Web Service** $\rightarrow$ connect this GitHub repository.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.server:app --host 0.0.0.0 --port 8000`
4. Add environment variable `NVIDIA_API_KEY`.

---

## 📄 License
MIT License. Built for university students preparing for online degree exams.

