"""
Mortgage Knowledge Base Documents
These five documents are embedded into FAISS and retrieved via RAG.
"""

ESCROW_SHORTAGE = """
Title: Escrow Shortage Explanation

An escrow shortage occurs when the amount collected in your escrow account during
the past year was not enough to cover the actual bills paid for property taxes and
homeowner's insurance.

How it happens:
- At the start of each year your lender estimates how much taxes and insurance will cost.
- They divide that total by 12 and collect it monthly as part of your mortgage payment.
- If the actual bills come in higher than estimated, there is a shortfall — an escrow shortage.

Impact on your payment:
- Your lender recalculates the monthly escrow amount based on the new, higher bills.
- The prior shortfall is spread over 12 months, so your new payment covers both the
  higher ongoing escrow AND repayment of last year's shortfall.

Example:
- Estimated taxes: $3,600/year ($300/month)
- Actual taxes:    $4,200/year ($350/month)
- Shortfall: $600 ÷ 12 = $50/month extra
- Total escrow increase: $50 (higher estimate) + $50 (shortage repayment) = $100/month more

What you can do:
- Pay the shortage in one lump sum to avoid the monthly spread.
- Review your escrow analysis statement carefully.
- Contact your lender's escrow department if you believe any numbers are wrong.
"""

PROPERTY_TAX_INCREASE = """
Title: Property Tax Increase and Mortgage Impact

Property taxes are levied by local governments (city, county, school district) and
are based on the assessed value of your home.

Why taxes increase:
- Your home's assessed value rose (reassessment cycle, home improvements, rising market).
- Local tax rates (millage rates) increased due to budget needs.
- Special assessments added (new infrastructure, school bonds).
- Tax exemptions expired (e.g., homestead exemption lapse).

How it affects your mortgage:
- Property taxes are paid through your escrow account.
- When taxes rise, your lender raises the escrow portion of your monthly payment.
- Even a $1,200/year tax increase means $100/month more in your payment.

How to fight a tax increase:
- File a property tax appeal with your local assessor's office.
- Appeal deadlines vary — typically 30–90 days after the assessment notice.
- Provide comparable home sales data to support a lower valuation.
- Check if you qualify for exemptions: senior, veteran, homestead, disability.

Typical timeline:
- Jan–Mar: Assessment notices mailed.
- Apr–Jun: Appeal period open.
- Fall: Tax bills issued.
- Winter: Lender pays from escrow; escrow adjusted next year.
"""

INSURANCE_PREMIUM_INCREASE = """
Title: Homeowner's Insurance Premium Increase

Homeowner's insurance protects your home from damage, theft, and liability.
If your premium rises, it directly increases your escrow payment.

Common reasons for increase:
- Inflation in construction and repair costs.
- Claims history (yours or your neighborhood's).
- Changes in your coverage at renewal.
- Insurer pulling back from high-risk areas (wildfire, flood, hurricane zones).
- Rising reinsurance costs passed to consumers.
- Your home's replacement-cost value was updated upward.

How it affects your mortgage:
- Insurance is paid from escrow just like taxes.
- A $600/year premium increase means $50/month more in your payment.

What you can do:
- Shop competing insurance quotes — you can switch carriers at renewal.
- Ask about discounts: bundling, security systems, claims-free history, newer roof.
- Review coverage limits — ensure they match actual replacement cost, not market value.
- Raise your deductible to lower your premium (weigh the risk tradeoff).
"""

ESCROW_HOW_IT_WORKS = """
Title: How Escrow Works in a Mortgage

An escrow account is managed by your lender to hold funds for property taxes
and homeowner's insurance, paying them on your behalf when they come due.

Why lenders require escrow:
- Ensures taxes and insurance are always paid, protecting their collateral.
- Spreads large annual bills into manageable monthly amounts.
- Required by most loan types (FHA, VA, USDA); often required for conventional
  loans with less than 20% down.

Monthly payment breakdown:
  Total Payment = Principal + Interest + Escrow
  Escrow = (Annual Taxes + Annual Insurance) ÷ 12 + Cushion

Escrow cushion:
- Lenders may hold up to 2 months of estimated payments as a buffer.
- If the cushion is depleted, your payment rises to rebuild it.

Annual escrow review:
- Every year your lender compares estimated vs. actual bills.
- Projects next year's costs and recalculates your monthly contribution.
- Surplus → you receive a refund check.
- Shortage → your monthly payment increases.

When changes take effect:
- Typically 30–45 days after the annual Escrow Analysis Statement is mailed.
- You may request a new escrow analysis at any time.
"""

PAYMENT_INCREASE_OVERVIEW = """
Title: Why Your Monthly Mortgage Payment Increased

Your payment can increase even with a fixed interest rate.

Main reasons:
1. Property tax increase — local government raised your assessment.
2. Insurance premium increase — your carrier raised your annual premium.
3. Escrow shortage — prior year's bills exceeded estimates; shortfall is now spread
   over 12 months while also collecting more going forward.
4. Escrow cushion adjustment — lender rebuilds the reserve buffer.
5. Combined causes — two or more factors occur simultaneously.

What does NOT change in a fixed-rate mortgage:
- Your principal and interest (P&I) stays the same for the life of the loan.
- Only the escrow portion changes.

What to do:
- Read the Escrow Analysis Statement from your lender.
- Verify tax and insurance amounts match your actual bills.
- Contact the escrow department if you spot errors.
- Consider a lump-sum shortage payment to minimize monthly increases.
- Check whether you still qualify for property tax exemptions.
"""
