"""
Chain 2 — Rule-Based Cause Detection
Deterministically identifies causes of a payment increase.
Pure Python — no LLM involved.
"""

from dataclasses import dataclass, field
from chains.input import ProcessedInput

THRESHOLD = 1.0   # $1/month minimum to flag a factor


@dataclass
class DetectedCauses:
    primary_reason:    str
    secondary_factors: list[str] = field(default_factory=list)
    rag_queries:       list[str] = field(default_factory=list)
    confidence:        str = "high"
    increase_detected: bool = True
    monthly_increase:  float = 0.0


def detect_causes(p: ProcessedInput) -> DetectedCauses:
    if not p.has_increase:
        return DetectedCauses(
            primary_reason="No increase detected",
            increase_detected=False,
            monthly_increase=p.total_monthly_increase,
            rag_queries=["why did my mortgage payment not change"],
            confidence="high",
        )

    causes: list[tuple[float, str, str]] = []  # (magnitude, label, rag_query)

    if p.tax_monthly_delta > THRESHOLD:
        causes.append((p.tax_monthly_delta,
                       "Property tax increase",
                       "property tax increase mortgage impact"))

    if p.insurance_monthly_delta > THRESHOLD:
        causes.append((p.insurance_monthly_delta,
                       "Insurance premium increase",
                       "insurance premium increase escrow"))

    shortage_signal = abs(
        p.unexplained_delta) > THRESHOLD or p.escrow_balance < 0
    if shortage_signal:
        magnitude = (abs(p.unexplained_delta) if abs(p.unexplained_delta) > THRESHOLD
                     else abs(p.escrow_balance / 12))
        causes.append((magnitude, "Escrow shortage",
                      "escrow shortage explanation"))

    if not causes:
        causes.append((p.total_monthly_increase,
                      "Escrow adjustment", "how escrow works"))

    causes.sort(key=lambda x: x[0], reverse=True)

    primary = causes[0][1]
    secondaries = [c[1] for c in causes[1:]]
    queries = list(dict.fromkeys(c[2] for c in causes))
    queries.append("why did my mortgage payment increase")

    return DetectedCauses(
        primary_reason=primary,
        secondary_factors=secondaries,
        rag_queries=queries,
        confidence="high" if len(causes) <= 2 else "medium",
        increase_detected=True,
        monthly_increase=p.total_monthly_increase,
    )
