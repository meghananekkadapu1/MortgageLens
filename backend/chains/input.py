"""
Chain 1 — Input Processing
Validates extracted figures and computes derived monthly deltas.
"""

from pydantic import BaseModel, Field, model_validator


class MortgageInput(BaseModel):
    previous_payment:          float = Field(..., gt=0)
    current_payment:           float = Field(..., gt=0)
    previous_annual_tax:       float = Field(..., ge=0)
    current_annual_tax:        float = Field(..., ge=0)
    previous_annual_insurance: float = Field(..., ge=0)
    current_annual_insurance:  float = Field(..., ge=0)
    escrow_balance:            float = Field(0.0)

    @model_validator(mode="after")
    def sanity_check(self):
        if self.current_payment < self.previous_payment * 0.3:
            raise ValueError("Current payment appears unrealistically low.")
        return self


class ProcessedInput(BaseModel):
    previous_payment:          float
    current_payment:           float
    previous_annual_tax:       float
    current_annual_tax:        float
    previous_annual_insurance: float
    current_annual_insurance:  float
    escrow_balance:            float
    # Derived
    total_monthly_increase:  float
    tax_monthly_delta:       float
    insurance_monthly_delta: float
    unexplained_delta:       float
    has_increase:            bool


def process_input(raw: MortgageInput) -> ProcessedInput:
    total  = round(raw.current_payment - raw.previous_payment, 2)
    tax_d  = round((raw.current_annual_tax - raw.previous_annual_tax) / 12, 2)
    ins_d  = round((raw.current_annual_insurance - raw.previous_annual_insurance) / 12, 2)
    unexpl = round(total - tax_d - ins_d, 2)

    return ProcessedInput(
        previous_payment          = raw.previous_payment,
        current_payment           = raw.current_payment,
        previous_annual_tax       = raw.previous_annual_tax,
        current_annual_tax        = raw.current_annual_tax,
        previous_annual_insurance = raw.previous_annual_insurance,
        current_annual_insurance  = raw.current_annual_insurance,
        escrow_balance            = raw.escrow_balance,
        total_monthly_increase    = total,
        tax_monthly_delta         = tax_d,
        insurance_monthly_delta   = ins_d,
        unexplained_delta         = unexpl,
        has_increase              = total > 0,
    )
