"""
Chain 0 — Document Parser  (OpenAI Vision)

PDF handling strategy (in order):
  1. pdf2image + poppler  → best quality JPEG
  2. PyMuPDF (fitz)       → no poppler needed, good quality
  3. Raise clear error    → never send raw PDF to OpenAI (it rejects it)
"""

import base64
import io
import json
import os
import re

from openai import OpenAI

SYSTEM_PROMPT = """You are a mortgage document data extractor.

Your ONLY job is to read the uploaded mortgage or escrow analysis statement image
and extract specific dollar amounts. Return ONLY a valid JSON object.
No markdown fences, no explanation, no preamble — just raw JSON.

Extract these fields (use 0 if genuinely not found):
{
  "previous_payment":          <number>,
  "current_payment":           <number>,
  "previous_annual_tax":       <number>,
  "current_annual_tax":        <number>,
  "previous_annual_insurance": <number>,
  "current_annual_insurance":  <number>,
  "escrow_balance":            <number>,
  "extraction_notes":          "<string>"
}

Rules:
- If the document shows monthly tax or insurance amounts, multiply by 12 for annual.
- If escrow shortage is listed as a positive number under "shortage", store it as negative.
- Do NOT guess. Use 0 for any field not found and note it in extraction_notes.
- Return ONLY the JSON object. Nothing else.
"""


def _to_b64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def _is_pdf(data: bytes) -> bool:
    return data[:4] == b"%PDF"


def _pdf_to_jpeg_b64(pdf_bytes: bytes) -> str:
    """
    Convert first page of PDF to JPEG base64.
    Tries pdf2image first, falls back to PyMuPDF.
    Raises RuntimeError if neither works.
    """

    # Option 1: pdf2image (requires poppler)
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=180)
        if images:
            buf = io.BytesIO()
            images[0].save(buf, format="JPEG", quality=90)
            print("  [Chain 0] PDF rendered via pdf2image")
            return _to_b64(buf.getvalue())
    except Exception as e:
        print(f"  [Chain 0] pdf2image unavailable: {e} — trying PyMuPDF ...")

    # Option 2: PyMuPDF / fitz (no poppler needed)
    try:
        import fitz
        doc  = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        mat  = fitz.Matrix(2.0, 2.0)
        pix  = page.get_pixmap(matrix=mat, alpha=False)
        buf  = io.BytesIO(pix.tobytes("jpeg"))
        doc.close()
        print("  [Chain 0] PDF rendered via PyMuPDF")
        return _to_b64(buf.getvalue())
    except Exception as e:
        print(f"  [Chain 0] PyMuPDF unavailable: {e}")

    raise RuntimeError(
        "Could not convert PDF to image. "
        "Please run:  pip install pymupdf"
    )


def extract_from_document(file_bytes: bytes, filename: str) -> dict:
    """
    Send the file to GPT-4o Vision and return extracted financial data.
    Always sends an image — never raw PDF bytes.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

    fname = filename.lower()

    # Convert to image URL
    if _is_pdf(file_bytes) or fname.endswith(".pdf"):
        img_b64   = _pdf_to_jpeg_b64(file_bytes)
        image_url = f"data:image/jpeg;base64,{img_b64}"
    elif fname.endswith(".png"):
        image_url = f"data:image/png;base64,{_to_b64(file_bytes)}"
    else:
        image_url = f"data:image/jpeg;base64,{_to_b64(file_bytes)}"

    # Call GPT-4o Vision
    response = client.chat.completions.create(
        model       = "gpt-4o",
        max_tokens  = 1024,
        temperature = 0,
        messages    = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type":      "image_url",
                        "image_url": {"url": image_url, "detail": "high"},
                    },
                    {
                        "type": "text",
                        "text": "Extract the mortgage/escrow payment data from this document and return it as JSON.",
                    },
                ],
            },
        ],
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$",       "", raw).strip()

    data = json.loads(raw)

    if not data.get("current_payment") and not data.get("previous_payment"):
        raise ValueError(
            "Could not extract payment data from this document. "
            "Please ensure it is a mortgage statement or escrow analysis letter."
        )

    for field in [
        "previous_payment", "current_payment",
        "previous_annual_tax", "current_annual_tax",
        "previous_annual_insurance", "current_annual_insurance",
        "escrow_balance",
    ]:
        data[field] = float(data.get(field) or 0)

    data.setdefault("extraction_notes", "")
    return data