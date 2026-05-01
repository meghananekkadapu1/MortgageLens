"""
Mortgage Lens — FastAPI Backend
Uses OpenAI GPT-4o Vision to read uploaded statements and GPT-4o
to generate grounded plain-language explanations.
"""

import os
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError

from chains.document_parser import extract_from_document
from chains.input import MortgageInput, process_input
from chains.detection import detect_causes
from chains.retrieval import build_context
from chains.explanation import generate_explanation
from knowledge_base.vector_store import build_index
from utils.evaluation import grounding_score, hallucination_score, run_detection_eval

load_dotenv()

MAX_FILE_MB = 20
ALLOWED_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg")
ALLOWED_TYPES = {"application/pdf", "image/png",
                 "image/jpeg", "image/jpg", "image/webp"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up — building FAISS knowledge base index …")
    build_index()
    print("✓ Ready!  API docs → http://localhost:8000/docs")
    yield


app = FastAPI(
    title="Mortgage Lens",
    description=(
        "Upload a mortgage or escrow statement (PDF / image). "
        "GPT-4o Vision reads it, then GPT-4o explains why your payment changed."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Response model ─────────────────────────────────────────────────────────────
class ExplainResponse(BaseModel):
    increase_detected:       bool
    primary_reason:          str
    secondary_factors:       list[str]
    monthly_increase_amount: float
    explanation:             str
    recommendations:         list[str]
    confidence:              str
    sources:                 list[str]
    extracted_data:          dict[str, Any]
    metrics:                 dict[str, Any]


# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {
        "status":         "ok",
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.post("/explain/upload", response_model=ExplainResponse, tags=["Core"])
async def explain_from_upload(file: UploadFile = File(...)):
    """
    Main endpoint.
    Upload a PDF or image of a mortgage / escrow statement.
    Returns a structured JSON explanation of why the payment changed.
    """
    # ── Guards ─────────────────────────────────────────────────────────────────
    file_bytes = await file.read()
    mb = len(file_bytes) / (1024 * 1024)
    if mb > MAX_FILE_MB:
        raise HTTPException(
            413, f"File too large ({mb:.1f} MB). Max {MAX_FILE_MB} MB.")

    filename = file.filename or "upload"
    content_type = (file.content_type or "").lower()
    if not filename.lower().endswith(ALLOWED_EXTENSIONS) and content_type not in ALLOWED_TYPES:
        raise HTTPException(
            415, "Unsupported file type. Please upload a PDF, PNG, or JPEG.")

    # ── Chain 0: Document Parsing (GPT-4o Vision) ──────────────────────────────
    try:
        extracted = extract_from_document(file_bytes, filename)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    except Exception as exc:
        raise HTTPException(502, f"Document reading error: {exc}")

    # ── Chain 1: Input Processing ──────────────────────────────────────────────
    try:
        raw_input = MortgageInput(
            previous_payment=extracted["previous_payment"],
            current_payment=extracted["current_payment"],
            previous_annual_tax=extracted["previous_annual_tax"],
            current_annual_tax=extracted["current_annual_tax"],
            previous_annual_insurance=extracted["previous_annual_insurance"],
            current_annual_insurance=extracted["current_annual_insurance"],
            escrow_balance=extracted["escrow_balance"],
        )
        processed = process_input(raw_input)
    except (ValidationError, ValueError) as exc:
        raise HTTPException(422, f"Extracted data validation failed: {exc}")

    # ── Chain 2: Rule-Based Detection ─────────────────────────────────────────
    causes = detect_causes(processed)

    # ── Chain 3: RAG Retrieval ─────────────────────────────────────────────────
    context, sources = build_context(causes)

    # ── Chain 4: AI Explanation (GPT-4o) ──────────────────────────────────────
    try:
        result = generate_explanation(processed, causes, context, sources)
    except Exception as exc:
        raise HTTPException(502, f"AI explanation error: {exc}")

    # ── Metrics ────────────────────────────────────────────────────────────────
    explanation_text = result.get("explanation", "")
    result["metrics"] = {
        "grounding_score":     grounding_score(explanation_text, [context]),
        "hallucination_score": hallucination_score(explanation_text),
        "context_chunks_used": len(sources),
    }
    result["extracted_data"] = {
        "previous_payment":          extracted["previous_payment"],
        "current_payment":           extracted["current_payment"],
        "previous_annual_tax":       extracted["previous_annual_tax"],
        "current_annual_tax":        extracted["current_annual_tax"],
        "previous_annual_insurance": extracted["previous_annual_insurance"],
        "current_annual_insurance":  extracted["current_annual_insurance"],
        "escrow_balance":            extracted["escrow_balance"],
        "extraction_notes":          extracted.get("extraction_notes", ""),
    }

    return ExplainResponse(**result)


@app.get("/eval/detection", tags=["Evaluation"])
async def eval_detection():
    """Run the rule-based detection test suite. No API key needed."""
    return run_detection_eval()


@app.get("/knowledge-base", tags=["System"])
async def list_knowledge_base():
    from knowledge_base.documents import RAW_DOCS
    return {
        "count":     len(RAW_DOCS),
        "documents": [{"title": t, "chars": len(d)} for t, d in RAW_DOCS.items()],
    }
