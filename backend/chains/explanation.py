"""
Chain 4 — AI Explanation Generator  (OpenAI GPT-4o)
Calls GPT-4o with a strict grounding prompt and structured-output
response_format to produce a JSON explanation.
"""

import json
import os
import re

from openai import OpenAI

from chains.input import ProcessedInput
from chains.detection import DetectedCauses

SYSTEM_PROMPT = """You are a helpful mortgage assistant explaining payment changes to homeowners.

STRICT RULES you must always follow:
1. Use ONLY the information inside the <context> block. Do NOT use outside knowledge.
2. Do NOT guess or infer anything not supported by the context.
3. If context does not cover something, say "I don't have specific information about that."
4. Write in plain, friendly language any homeowner can understand. Avoid jargon.
5. Aim for 3–5 sentences in the explanation field.
6. Respond with ONLY valid JSON — no markdown fences, no preamble.

Required JSON format:
{
  "increase_detected":       boolean,
  "primary_reason":          "string",
  "secondary_factors":       ["string"],
  "monthly_increase_amount": number,
  "explanation":             "string — 3 to 5 plain-language sentences",
  "recommendations":         ["string — actionable, 2 to 4 items"],
  "confidence":              "high | medium | low",
  "sources":                 ["string"]
}"""


def _user_message(
    processed: ProcessedInput,
    causes:    DetectedCauses,
    context:   str,
    sources:   list[str],
) -> str:
    return f"""A homeowner's mortgage payment changed. Here are the details:

PAYMENT DETAILS:
  Previous monthly payment:     ${processed.previous_payment:,.2f}
  Current monthly payment:      ${processed.current_payment:,.2f}
  Total monthly increase:       ${processed.total_monthly_increase:,.2f}
  Tax change (monthly):         ${processed.tax_monthly_delta:,.2f}
  Insurance change (monthly):   ${processed.insurance_monthly_delta:,.2f}
  Unexplained delta (monthly):  ${processed.unexplained_delta:,.2f}
  Escrow balance:               ${processed.escrow_balance:,.2f}

DETECTED CAUSES (already determined by rule engine — do not re-derive):
  Primary reason:    {causes.primary_reason}
  Secondary factors: {', '.join(causes.secondary_factors) if causes.secondary_factors else 'None'}
  Confidence:        {causes.confidence}

RETRIEVED KNOWLEDGE BASE CONTEXT:
<context>
{context}
</context>

SOURCES: {json.dumps(sources)}

Using ONLY the context above, generate the JSON explanation for this homeowner."""


def generate_explanation(
    processed: ProcessedInput,
    causes:    DetectedCauses,
    context:   str,
    sources:   list[str],
) -> dict:
    """Call GPT-4o and return the parsed structured output dict."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": _user_message(
                processed, causes, context, sources)},
        ],
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$",       "", raw).strip()

    result = json.loads(raw)

    # Defensive defaults
    result.setdefault("increase_detected",       causes.increase_detected)
    result.setdefault("primary_reason",          causes.primary_reason)
    result.setdefault("secondary_factors",       causes.secondary_factors)
    result.setdefault("monthly_increase_amount", causes.monthly_increase)
    result.setdefault("confidence",              causes.confidence)
    result.setdefault("sources",                 sources)

    return result
