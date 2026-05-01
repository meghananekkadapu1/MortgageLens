# 🏡 Mortgage Lens— OpenAI Edition

Upload your escrow analysis or mortgage payment-change letter (PDF or image).
**GPT-4o Vision** reads it and extracts all the numbers automatically.
**GPT-4o** then explains in plain English exactly why your monthly payment changed —
grounded in a FAISS RAG knowledge base, with zero hallucination goals.

---

## 📁 Complete Project Structure

```
mortgagelens/
│
├── sample_escrow_statement.pdf        ← Ready-to-use test document
│
├── backend/
│   ├── main.py                        ← FastAPI app — all API endpoints
│   ├── requirements.txt               ← Python dependencies
│   ├── .env.example                   ← Copy to .env, add OPENAI_API_KEY
│   │
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── document_parser.py        ← GPT-4o Vision reads PDF/image → JSON
│   │   ├── input.py                  ← Validates data, computes deltas
│   │   ├── detection.py              ← Rule engine identifies causes (no LLM)
│   │   ├── retrieval.py              ← FAISS RAG retrieval
│   │   └── explanation.py            ← GPT-4o generates grounded explanation
│   │
│   ├── knowledge_base/
│   │   ├── __init__.py
│   │   ├── documents.py               ← 5 mortgage knowledge documents
│   │   └── vector_store.py            ← FAISS index builder + retriever
│   │
│   └── utils/
│       ├── __init__.py
│       └── evaluation.py              ← Accuracy, grounding & hallucination metrics
│
└── frontend/
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── App.js                     ← Root component, upload → result flow
        ├── index.js
        ├── index.css                  ← All styles
        └── components/
            ├── UploadForm.js          ← Drag-and-drop file upload
            ├── ResultPanel.js         ← Full result display with metrics
            └── LoadingCard.js         ← Loading state
```

---

## 🔧 Prerequisites

| Tool | Minimum Version | How to check |
|------|----------------|--------------|
| Python | 3.11 | `python3 --version` |
| pip | any | `pip --version` |
| Node.js | 18 | `node --version` |
| npm | 9 | `npm --version` |

You need an **OpenAI API key** with access to `gpt-4o`.
Get one at: https://platform.openai.com/api-keys

---

## 🚀 Step-by-Step Local Setup

### STEP 1 — Download / unzip the project

```
mortgagelens/
├── backend/
├── frontend/
├── sample_escrow_statement.pdf
└── README.md
```

Open a terminal and `cd` into the project folder:

```bash
cd mortgagelens
```

---

### STEP 2 — Set up the Python backend

```bash
cd backend
```

**Create a virtual environment:**

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows — Command Prompt
python -m venv venv
venv\Scripts\activate.bat

# Windows — PowerShell
python -m venv venv
venv\Scripts\Activate.ps1
```

Your terminal prompt will show `(venv)` when active.

**Install dependencies:**

```bash
pip install -r requirements.txt
```

> First run downloads the sentence-transformers embedding model (~90 MB). Cached after that.

**Create your `.env` file:**

```bash
# macOS / Linux
cp .env.example .env

# Windows
copy .env.example .env
```

Open `.env` in any text editor and add your key:

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

---

### STEP 3 — Start the backend

```bash
# Still inside backend/ with (venv) active
uvicorn main:app --reload --port 8000
```

You should see:

```
Starting up — building FAISS knowledge base index …
  Building FAISS index …
  → 47 chunks indexed across 5 documents.
✓ Ready!  API docs → http://localhost:8000/docs
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Leave this terminal open.**

---

### STEP 4 — Set up and start the frontend

Open a **second terminal window**:

```bash
cd mortgagelens/frontend

npm install
```

```bash
npm start
```

Your browser opens **http://localhost:3000** automatically.

---

## ✅ Test It Immediately

1. Go to **http://localhost:3000**
2. Click the upload zone (or drag a file onto it)
3. Select **`sample_escrow_statement.pdf`** from the project root
4. Click **Analyze Statement**
5. Wait ~10–15 seconds
6. See the full explanation, causes, recommendations, and quality metrics

The sample PDF is a realistic escrow analysis for "Jane & John Homeowner"
showing a **+$145.84/month** increase driven by property tax and insurance rises.

---

## 🧪 Run the Evaluation Suite

In a third terminal (with venv active):

```bash
cd backend
python -m utils.evaluation
```

Expected output:
```
{
  "accuracy": 1.0,
  "total": 4,
  "correct": 4,
  "cases": [
    {"name": "Tax increase only",          "correct": true},
    {"name": "Insurance increase only",    "correct": true},
    {"name": "Escrow shortage",            "correct": true},
    {"name": "Combined tax + insurance",   "correct": true}
  ]
}

Detection accuracy: 100.0%
```

Or via the API:
```bash
curl http://localhost:8000/eval/detection
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Status + API key check |
| `POST` | `/explain/upload` | **Main** — upload PDF/image, get explanation |
| `GET` | `/eval/detection` | Detection accuracy test suite |
| `GET` | `/knowledge-base` | List knowledge base documents |
| `GET` | `/docs` | Swagger interactive UI |

**Test with curl:**
```bash
curl -X POST http://localhost:8000/explain/upload \
  -F "file=@sample_escrow_statement.pdf"
```

---

## 🧠 5-Chain Pipeline

```
User uploads PDF or image
          │
          ▼
┌──────────────────────────────────────────────┐
│ Chain 0: Document Parser                      │
│ GPT-4o Vision reads the statement,            │
│ extracts 7 financial figures → JSON           │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│ Chain 1: Input Processing                     │
│ Validates numbers, computes monthly deltas:   │
│ tax_delta, insurance_delta, total_delta       │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│ Chain 2: Rule-Based Detection  (no LLM)       │
│ Pure Python — identifies primary cause        │
│ and secondary factors deterministically       │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│ Chain 3: RAG Retrieval                        │
│ FAISS similarity search across 5 knowledge   │
│ base docs → top 8 relevant text chunks       │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│ Chain 4: AI Explanation  (GPT-4o)             │
│ Uses ONLY retrieved context to generate      │
│ structured JSON explanation                   │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
         JSON response + quality metrics
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Document reading | OpenAI GPT-4o Vision |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| Vector database | FAISS (CPU) |
| AI explanation | OpenAI GPT-4o |
| Frontend | React 18 |
| Styling | Pure CSS |

---

## 🛠️ Troubleshooting

**`ModuleNotFoundError: No module named 'faiss'`**
```bash
pip install faiss-cpu
```

**`ModuleNotFoundError: No module named 'multipart'`**
```bash
pip install python-multipart
```

**`openai.AuthenticationError`**
- Check `.env` is inside the `backend/` directory
- Key must start with `sk-proj-` or `sk-`
- No quotes or spaces around the key in `.env`

**`openai.PermissionDeniedError` / model not found**
- Ensure your OpenAI account has `gpt-4o` access
- Check your usage tier at https://platform.openai.com/account/limits

**React "Network Error"**
- Backend must be running on port 8000
- `"proxy": "http://localhost:8000"` in `frontend/package.json` handles routing

**Port already in use**
```bash
# Backend on different port
uvicorn main:app --reload --port 8001

# React pointing to new port
REACT_APP_API_URL=http://localhost:8001 npm start
```

**PDF not being read correctly**
- Install `pdf2image` + poppler for best results:
  ```bash
  pip install pdf2image
  # macOS:   brew install poppler
  # Ubuntu:  sudo apt-get install poppler-utils
  # Windows: download poppler from https://github.com/oschwartz10612/poppler-windows
  ```
- Without poppler, the raw PDF bytes are sent directly to GPT-4o Vision (still works for most PDFs)

  **for Alternative pdf converter use PyMuPDF -> pip install pymupdf

**FAISS index needs rebuilding** (after editing knowledge base docs):
```bash
rm backend/knowledge_base/faiss_index.bin
rm backend/knowledge_base/faiss_meta.pkl
# Restarts automatically on next server start
```

---

## 📊 Quality Metrics Explained

| Metric | What it measures |
|--------|----------------|
| Grounding Score | % of explanation sentences that share key terms with the retrieved KB context |
| Hallucination Score | Fraction of hedging phrases detected (lower = more confident, grounded) |
| Factual Reliability | `1 − hallucination_score` displayed as a percentage |
| KB Sources Used | Number of distinct knowledge base documents cited |
