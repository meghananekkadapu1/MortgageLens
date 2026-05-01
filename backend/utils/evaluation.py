"""
Evaluation & Metrics
Run standalone:  cd backend && python -m utils.evaluation
"""

import re


def grounding_score(explanation: str, context_chunks: list[str]) -> float:
    """Fraction of explanation sentences sharing >= 2 words with retrieved context."""
    if not context_chunks:
        return 0.0
    context_words: set[str] = set()
    for chunk in context_chunks:
        context_words.update(re.findall(r"\b[a-zA-Z]{5,}\b", chunk.lower()))
    sentences = [s.strip() for s in re.split(
        r"[.!?]", explanation) if len(s.strip()) > 20]
    if not sentences:
        return 1.0
    grounded = sum(
        1 for s in sentences
        if len(set(re.findall(r"\b[a-zA-Z]{5,}\b", s.lower())) & context_words) >= 2
    )
    return round(grounded / len(sentences), 3)


_HEDGE_PHRASES = [
    "i believe", "i think", "probably", "maybe", "perhaps",
    "it's possible", "could be", "might be", "i'm not sure",
    "as far as i know", "typically around", "usually about",
]


def hallucination_score(explanation: str) -> float:
    """Fraction of hedging phrases in the explanation (lower = better)."""
    lower = explanation.lower()
    hits = sum(1 for p in _HEDGE_PHRASES if p in lower)
    return round(hits / len(_HEDGE_PHRASES), 3)


TEST_CASES = [
    {
        "name": "Tax increase only",
        "input": dict(previous_payment=2000, current_payment=2300,
                      previous_annual_tax=3600, current_annual_tax=4800,
                      previous_annual_insurance=1200, current_annual_insurance=1200,
                      escrow_balance=0),
        "expected_primary": "Property tax increase",
    },
    {
        "name": "Insurance increase only",
        "input": dict(previous_payment=1800, current_payment=1850,
                      previous_annual_tax=3000, current_annual_tax=3000,
                      previous_annual_insurance=1200, current_annual_insurance=1800,
                      escrow_balance=0),
        "expected_primary": "Insurance premium increase",
    },
    {
        "name": "Escrow shortage",
        "input": dict(previous_payment=2200, current_payment=2400,
                      previous_annual_tax=4000, current_annual_tax=4000,
                      previous_annual_insurance=1200, current_annual_insurance=1200,
                      escrow_balance=-800),
        "expected_primary": "Escrow shortage",
    },
    {
        "name": "Combined tax + insurance",
        "input": dict(previous_payment=2000, current_payment=2250,
                      previous_annual_tax=3600, current_annual_tax=4200,
                      previous_annual_insurance=1200, current_annual_insurance=1500,
                      escrow_balance=0),
        "expected_primary": "Property tax increase",
    },
]


def run_detection_eval() -> dict:
    from chains.input import MortgageInput, process_input
    from chains.detection import detect_causes

    results, correct = [], 0
    for case in TEST_CASES:
        detected = detect_causes(process_input(MortgageInput(**case["input"])))
        ok = detected.primary_reason == case["expected_primary"]
        correct += int(ok)
        results.append({
            "name":     case["name"],
            "expected": case["expected_primary"],
            "detected": detected.primary_reason,
            "correct":  ok,
        })
    return {
        "accuracy": round(correct / len(TEST_CASES), 3),
        "total":    len(TEST_CASES),
        "correct":  correct,
        "cases":    results,
    }


if __name__ == "__main__":
    import json
    report = run_detection_eval()
    print(json.dumps(report, indent=2))
    print(f"\nDetection accuracy: {report['accuracy'] * 100:.1f}%")
