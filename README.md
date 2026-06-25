# SmartEdu AI - Student Learning Hub

SmartEdu AI is an advanced educational workspace that helps students digest long lecture notes, textbooks, and syllabus files. Powered by Google Gemini and Streamlit, it provides interactive AI-driven summaries, concept simplifications with real-world analogies, custom practice quizzes with auto-grading, interactive 3D flashcard decks, and a personalized study planner.

---

## 🌟 Key Features

1. **📄 PDF Notes Upload**:
   - Automated text extraction using `pypdf`.
   - Text segmentation into overlapping semantic chunks.
2. **📊 AI Summarization**:
   - Provides a concise overview alongside a chapter-by-chapter/section-by-section breakdown of topics.
3. **💡 Concept Simplifier**:
   - Converts advanced topics into beginner-friendly explanations with custom examples, real-world analogies, and terminology definitions.
4. **🎯 Quiz Zone**:
   - Automatically formulates Multiple-Choice (MCQ), True/False, and short-answer questions from note content. Includes instant grading, score trackers, and AI-powered explanations.
5. **🎴 Flashcard Deck**:
   - Generates double-sided revision cards with a custom CSS 3D-flipping effect on hover/tap.
6. **💬 AI Doubt Solver**:
   - Chat directly with your uploaded documents using RAG (Retrieval-Augmented Generation).
   - Includes **browser-based voice recognition** allowing you to speak your questions out-of-the-box.
7. **📅 Personalized Study Planner**:
   - Computes daily revision metrics and builds a custom day-by-day roadmap based on exam dates, syllabus completion rates, and weak topics.

---

## 🏗️ Project Architecture

```
Student (User)
   │
   ▼
Streamlit Frontend ◄── [Injected Custom CSS & 3D CSS Flip Decks]
   │
   ▼
PDF Text Extraction (pypdf) ──► Text Chunking (LangChain Splitter)
   │
   ▼
Gemini Embeddings (text-embedding-004)
   │
   ▼
Vector DB (FAISS / NumPy Cosine-Similarity Fallback)
   │
   ▼
Gemini API (gemini-1.5-flash) ──► Summaries / Quizzes / Q&A / Study Plans
```

---

## 📁 Codebase Structure

```
SmartBuddy/
├── app.py                      # Main Streamlit Application interface
├── requirements.txt            # Python environment dependencies
├── src/                        # Platform source packages
│   ├── __init__.py             # Package init
│   ├── ai_engine.py            # Gemini Client wrappers (google-genai SDK)
│   ├── pdf_processor.py        # PDF text parsing, cleaning, and chunking
│   ├── vector_store.py         # FAISS vector store with local NumPy fallback
│   ├── study_planner.py        # Custom study schedule prompt builders
│   ├── ui_components.py        # Custom CSS & HTML generators (3D flip cards, Concept cards)
│   └── voice_helper.py         # Browser SpeechRecognition component integration
└── README.md                   # Setup guide
```

---

## 🚀 Getting Started

### 📋 Prerequisites
- Python 3.11, 3.12, or 3.13 installed.
- A **Gemini API Key** (Get one for free at [Google AI Studio](https://aistudio.google.com/)).

### 🔧 Installation

1. **Clone/Open the workspace** in your terminal:
   ```bash
   cd c:\Users\RAKESH\OneDrive\Attachments\Desktop\SmartBuddy
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your Gemini API Key** (Optional environment setup; can also be input directly into the app sidebar):
   * **Windows Command Prompt**:
     ```cmd
     set GEMINI_API_KEY="your-api-key"
     ```
   * **Windows PowerShell**:
     ```powershell
     $env:GEMINI_API_KEY="your-api-key"
     ```
   * **Linux/macOS**:
     ```bash
     export GEMINI_API_KEY="your-api-key"
     ```

### 🏃 Running the Application

Start the Streamlit application:
```bash
streamlit run app.py
```
A browser window should automatically open at `http://localhost:8501`.

---

## 🛠️ Verification & Testing
To run the automated verification suite to test cleaning, chunking, and mock vector search ranking:
```bash
$env:PYTHONPATH="."; python C:\Users\RAKESH\.gemini\antigravity\brain\4d77e6fa-8503-43b5-811f-c4e7dc946e87\scratch\test_pipeline.py
```
