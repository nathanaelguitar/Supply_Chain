"""
module4_assignment.py

Unit 4 Assignment: Employing a Holistic Approach to Supply Chain Design
Covers all three assignment parts:
  Part 1 - Measuring and Improving Supply Chain Cash Flow Efficiency
  Part 2 - Designing a Strategy to Achieve Supply Chain Coordination
  Part 3 - Designing a Strategy for Supply Chain Sustainability
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

DEFAULT_SEC_CSV = Path("data/u4_sec_api_results_2016_2021.csv")

DISPLAY_COLS = [
    "company",
    "year",
    "Accounts Receivable",
    "Inventory",
    "Accounts Payable",
    "Annual Sales",
    "Annual COGS",
    "Days of Accounts Receivable",
    "Days of Inventory",
    "Days of Accounts Payable",
    "Cash Conversion Cycle",
]

MONEY_COLS = [
    "Accounts Receivable",
    "Inventory",
    "Accounts Payable",
    "Annual Sales",
    "Annual COGS",
]

DAY_COLS = [
    "Days of Accounts Receivable",
    "Days of Inventory",
    "Days of Accounts Payable",
    "Cash Conversion Cycle",
]


def load_results(source: Path = DEFAULT_SEC_CSV) -> pd.DataFrame:
    """Load the default SEC API export used by the Unit 4 assignment."""
    if not source.exists():
        raise FileNotFoundError(
            f"{source} not found. Run sec_api_u4.py first to fetch and save the data."
        )
    df = pd.read_csv(source)
    missing_cols = [col for col in DISPLAY_COLS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"{source} is missing required columns: {', '.join(missing_cols)}"
        )
    # Convert raw dollar columns from raw USD to millions for display
    for col in MONEY_COLS:
        if col in df.columns:
            df[col] = df[col] / 1_000_000
    return df


# ---------------------------------------------------------------------------
# Part 1 helpers
# ---------------------------------------------------------------------------

DIVIDER = "=" * 100


def _section(title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def print_part1(df: pd.DataFrame) -> None:
    _section("PART ONE — Measuring and Improving Supply Chain Cash Flow Efficiency")

    # --- Solution steps ---
    print("""
SOLUTION STEPS
--------------
1. SOURCE: Financial statement data (Accounts Receivable, Inventory, Accounts Payable,
   Annual Sales, Annual COGS) for 3M, P&G, and Walmart was obtained directly from the
   SEC EDGAR XBRL API (https://data.sec.gov/api/xbrl/companyfacts/) for fiscal years
   2016-2021 using the sec_api_u4.py script. All dollar values are in USD millions.

2. FORMULAS:
   Days of Accounts Receivable (DAR) = (Accounts Receivable / Annual Sales) × 365
     → Measures how quickly the company collects cash from customers.

   Days of Inventory (DI) = (Inventory / Annual COGS) × 365
     → Measures how long goods sit in inventory before being sold.

   Days of Accounts Payable (DAP) = (Accounts Payable / Annual COGS) × 365
     → Measures how long the company takes to pay its suppliers.

   Cash Conversion Cycle (CCC) = DAR + DI − DAP
     → Net days of cash tied up in the operating cycle.
     → A lower (or negative) CCC is generally better for cash flow efficiency.

3. DATA QUALITY: Where a company reports under multiple XBRL tags for the same concept
   (e.g., SalesRevenueNet vs. RevenueFromContractWithCustomerExcludingAssessedTax),
   values are merged in priority order with the most recently filed 10-K row selected
   per fiscal year.
""")

    # --- Full computed table ---
    print("COMPUTED METRICS TABLE ($ millions | days)\n")
    for company, grp in df.groupby("company"):
        print(f"  {company}")
        sub = grp[["year"] + MONEY_COLS + DAY_COLS].copy()
        for col in MONEY_COLS:
            sub[col] = sub[col].map(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
        for col in DAY_COLS:
            sub[col] = sub[col].map(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        print(sub.to_string(index=False))
        print()

    # --- Day-metrics summary for quick reading ---
    print("DAY METRICS SUMMARY (days)\n")
    day_summary = df[["company", "year"] + DAY_COLS].copy()
    for col in DAY_COLS:
        day_summary[col] = day_summary[col].map(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
    print(day_summary.to_string(index=False))

    # --- Pattern analysis ---
    print("""
OBSERVED PATTERNS AND EXPLANATIONS
------------------------------------

Pattern 1 — 3M (Industrial/Diversified Manufacturer): HIGH and Gradually Declining CCC
  3M's CCC ranges from ~87 to ~104 days, peaking in 2017 before a gradual decline.
  - DAR (~48-57 days): 3M sells primarily to businesses (B2B), extending credit to
    distributors and industrial customers, resulting in multi-week collection periods.
  - DI (~82-97 days): Diversified manufacturing requires stocking thousands of SKUs
    across diverse product lines, leading to substantial inventory holdings.
  - DAP (~43-58 days): Growing over the period, indicating 3M has been extending
    payment terms with its own suppliers to offset some working capital burden.
  - The CCC decline after 2017 reflects 3M's working capital optimization initiatives
    and relatively faster growth in DAP compared to DAR/DI.

Pattern 2 — P&G (Consumer Goods): NEGATIVE and Worsening CCC
  P&G's CCC is negative throughout (-27 to -53 days) and becomes more negative each year.
  - DAR (~21-27 days): P&G sells primarily through large retail intermediaries (Walmart,
    Target, etc.) on short credit terms, so cash is collected relatively quickly.
  - DI (~50-59 days): Consumer packaged goods inventory turns moderately well, but P&G
    must maintain safety stock across a broad product portfolio globally.
  - DAP (~103-135 days): This is the dominant driver. P&G aggressively extends supplier
    payment terms — growing from ~103 days in 2016 to ~135 days in 2021. This reflects
    supply chain finance programs (e.g., dynamic discounting, reverse factoring) that let
    suppliers receive early payment via a financial intermediary while P&G pays later.
  - Explanation: P&G essentially uses its suppliers as a source of interest-free financing.
    Its scale and purchasing power allow it to dictate payment terms. The increasingly
    negative CCC means P&G collects from customers before it pays suppliers, providing a
    structural cash flow advantage and reducing dependence on external financing.

Pattern 3 — Walmart (Mass Retail): NEAR-ZERO and Declining CCC
  Walmart's CCC hovers between ~0.6 and ~10 days, declining over the period.
  - DAR (~4 days): Walmart is a consumer-facing retailer. Nearly all sales are cash or
    card-based (no credit extended to shoppers), so receivables are minimal — primarily
    credit card processor floats settled within a few days.
  - DI (~39-45 days): Walmart's supply chain and cross-docking infrastructure keeps
    inventory moving efficiently, though the scale of its inventory (>$44B) is enormous.
  - DAP (~39-45 days): Walmart also pays suppliers in roughly 40-45 days. The near-zero
    CCC means these roughly balance out.
  - Explanation: Walmart's business model inherently produces a near-zero CCC because
    it collects cash instantly from consumers while holding inventory about as long as it
    takes to pay suppliers. The slight decline in CCC over the period suggests incremental
    efficiency gains in inventory management and/or modest extension of payment terms.

Cross-Company Pattern — Universal Rise in Accounts Payable Days
  All three companies show increasing DAP over 2016-2021. This is a broad industry trend:
  large buyers have leveraged supply chain finance programs and negotiating power to extend
  supplier payment windows. Low interest rates during this period also made it economically
  attractive for suppliers to accept delayed payments (or use reverse-factoring programs),
  as the financing cost was minimal.

Cross-Company Pattern — COVID-19 Impact (2020)
  In 2020, P&G's DAR dropped sharply (26 → 21 days), suggesting faster collections or
  a favorable mix shift. Walmart's metrics remained stable, reflecting the resilience of
  essential retail demand. 3M's CCC dipped slightly, partly due to strong demand for
  PPE and safety products boosting sales faster than inventory build-up.
""")


# ---------------------------------------------------------------------------
# Part 2
# ---------------------------------------------------------------------------

def print_part2() -> None:
    _section("PART TWO — Designing a Strategy to Achieve Supply Chain Coordination")

    print("""
CHOSEN COMPANY: Walmart

CURRENT PRACTICES IN SUPPLY CHAIN COORDINATION
-----------------------------------------------
Walmart is widely regarded as a global benchmark for supply chain coordination. Its
approach combines several complementary strategies:

1. Every Day Low Prices (EDLP) and Every Day Low Cost (EDLC):
   Walmart's pricing philosophy is inherently a coordination tool. By committing to
   stable, low prices (no promotional spikes), Walmart reduces the demand variability
   it transmits upstream. Suppliers face smoother, more predictable order patterns,
   dampening the bullwhip effect that plagues supply chains driven by promotional
   pricing.

2. Vendor-Managed Inventory (VMI):
   Walmart pioneered VMI with major suppliers (most famously Procter & Gamble in the
   1980s). Under VMI, the supplier — not Walmart — monitors inventory levels at
   Walmart distribution centers and stores, and triggers replenishment orders. This
   eliminates the information delay caused by passing orders up the supply chain,
   giving the supplier direct visibility into actual consumer demand.

3. Retail Link and Real-Time Data Sharing:
   Walmart provides suppliers with access to its proprietary Retail Link platform,
   which shares point-of-sale (POS) data, inventory levels, and sell-through rates in
   near real time. This transparency significantly reduces the information asymmetry
   that causes incentive misalignment in decentralized supply chains. Suppliers can
   plan production based on actual consumer demand rather than lagged order signals.

4. Collaborative Planning, Forecasting, and Replenishment (CPFR):
   Walmart and many of its strategic suppliers participate in CPFR processes, jointly
   creating demand forecasts and replenishment plans. This moves beyond simple data
   sharing to active coordination of decisions between supply chain partners.

5. Cross-Docking Distribution Network:
   Walmart's distribution centers operate primarily as cross-docking hubs: inbound
   goods from suppliers are sorted and transferred directly to outbound trucks for
   specific stores, with minimal storage time. This reduces inventory in the system,
   lowers holding costs, and speeds the flow of goods to stores.

6. Supplier Scorecards and Performance Management:
   Walmart tracks and publishes supplier performance metrics (on-time delivery, fill
   rates, compliance). This creates accountability and strong incentives for supplier
   compliance with coordination agreements.

RECOMMENDATIONS FOR IMPROVED SUPPLY CHAIN COORDINATION
-------------------------------------------------------
Despite its strengths, several areas offer meaningful improvement:

1. Move from Price-Only Contracts to Revenue-Sharing or Buyback Arrangements:
   Most of Walmart's supplier contracts are wholesale-price based. Economic theory
   (Pasternack 1985; Cachon and Lariviere 2005) shows that revenue-sharing contracts
   achieve perfect supply chain coordination by aligning incentives across tiers. For
   perishable or fashion categories, Walmart should pilot revenue-sharing contracts
   where supplier and retailer jointly share the upside and downside of demand
   variability, inducing suppliers to offer higher service levels and optimal wholesale
   pricing.

2. Expand Quantity Flexibility and Option Contracts:
   For seasonal and trend-sensitive merchandise, Walmart could implement quantity
   flexibility contracts that allow a range of order quantities at a pre-agreed price.
   This reduces supplier over-production risk and Walmart's stockout exposure, improving
   coordinated outcomes for both parties.

3. Deepen AI-Driven Demand Sensing:
   While Retail Link is a strong foundation, Walmart should invest in machine learning
   demand-sensing models that incorporate external signals (social media trends, weather,
   local events) to produce more accurate short-horizon forecasts. Sharing these enhanced
   forecasts with suppliers further reduces the bullwhip effect.

4. Apply Blockchain for Multi-Tier Supply Chain Visibility:
   Walmart already uses blockchain for food traceability (IBM Food Trust). Expanding
   this to deeper supply chain tiers (Tier 2 and Tier 3 suppliers) would allow earlier
   detection of supply disruptions and better coordination of contingency responses,
   addressing the "hidden tiers" problem that contributed to vulnerabilities exposed
   during COVID-19.

5. Incentive-Aligned Sustainability Requirements:
   As Walmart pursues its "Project Gigaton" emissions reduction goals, it should
   structure supplier incentive programs (preferred placement, pricing advantages) for
   sustainability compliance rather than purely mandating compliance. This creates a
   positive incentive alignment for decarbonization rather than adversarial enforcement.
""")


# ---------------------------------------------------------------------------
# Part 3
# ---------------------------------------------------------------------------

def print_part3() -> None:
    _section("PART THREE — Designing a Strategy for Supply Chain Sustainability")

    print("""
CHOSEN COMPANY: Procter & Gamble (P&G)

CURRENT PRACTICES IN SUPPLY CHAIN SUSTAINABILITY
-------------------------------------------------
Procter & Gamble is one of the most scrutinized consumer goods companies on
sustainability, given the environmental footprint associated with producing billions of
household and personal care products globally. P&G's current sustainability approach is
anchored by its "Ambition 2030" framework, launched in 2021:

1. Renewable Energy and Carbon Reduction:
   P&G has committed to 100% renewable electricity across its manufacturing operations
   (achieved in North America and Europe) and a goal of net-zero greenhouse gas emissions
   (Scope 1 and 2) by 2040. Operationally, P&G has installed on-site solar and wind
   capacity at major plants and purchases renewable energy certificates (RECs) and
   power purchase agreements (PPAs) to offset remaining consumption.

2. Sustainable Sourcing:
   P&G sources large volumes of palm oil, pulp/paper, and petroleum-derived surfactants.
   It is a member of the Roundtable on Sustainable Palm Oil (RSPO) and has committed to
   100% certified sustainable palm oil sourcing. Paper and pulp sourcing is governed by
   supplier certification requirements (FSC, PEFC). Despite these commitments, supply
   chain deforestation associated with palm oil remains a material risk.

3. Packaging and Plastic Waste:
   P&G has committed to making 100% of its packaging recyclable or reusable by 2030 and
   to reducing virgin petroleum-based plastic by 50%. Programs include expanding
   concentrated refill formats (e.g., Downy Eco-Box), introducing post-consumer recycled
   (PCR) plastic content into bottles (Head & Shoulders ocean-plastic bottles), and
   participating in industry-wide recycling infrastructure investments.

4. Water Stewardship:
   P&G has implemented water reduction targets at manufacturing sites and has partnered
   with NGOs on water access programs in water-stressed regions. Its "Children's Safe
   Drinking Water" program has distributed over 20 billion liters of clean water since
   2004.

5. Supplier Sustainability Engagement:
   P&G uses a supplier sustainability scorecard to assess environmental and social
   performance of key suppliers and integrates sustainability criteria into its
   sourcing decisions.

RECOMMENDATIONS FOR IMPROVED SUPPLY CHAIN SUSTAINABILITY
---------------------------------------------------------
P&G's program is substantive, but significant gaps remain, especially in Scope 3
emissions and full value chain circularity:

1. Adopt Science-Based Targets for Scope 3 Emissions:
   P&G's net-zero commitment currently covers Scope 1 and 2 (direct operations). However,
   Scope 3 emissions — primarily from consumer product use (e.g., hot water for laundry)
   and raw material production — represent the vast majority of its carbon footprint. P&G
   should commit to Science-Based Targets initiative (SBTi)-validated Scope 3 reduction
   goals and set binding milestones. Achieving this requires reformulating products (cold-
   water detergents, concentrated formats) and working deeply with Tier 1-3 suppliers on
   decarbonization roadmaps.

2. Implement Extended Producer Responsibility (EPR) and Circular Design:
   Rather than incremental packaging improvements, P&G should adopt circular economy
   design principles systematically: designing all packaging for mono-material
   recyclability, investing in chemical recycling infrastructure for flexible plastics
   (currently largely unrecyclable), and supporting EPR legislation that funds collection
   and recycling systems. P&G's scale gives it the market power to drive industry-wide
   infrastructure change.

3. Deepen Supplier Decarbonization Programs:
   P&G's supplier scorecard should evolve into an active supplier decarbonization program
   that provides technical assistance, preferential contract terms, and access to
   renewable energy purchasing consortiums for smaller suppliers. This mirrors how
   Walmart's "Project Gigaton" attempts to reduce upstream Scope 3 emissions through
   supplier engagement, but with more binding performance requirements.

4. Eliminate Deforestation from Palm Oil and Paper Supply Chains:
   RSPO certification alone is insufficient to guarantee deforestation-free supply chains.
   P&G should implement satellite-based supply chain monitoring (using tools like Global
   Forest Watch Pro) to trace palm oil back to individual mill and plantation level,
   disqualifying non-compliant suppliers. A time-bound commitment to verified
   deforestation-free sourcing by 2025 would align with investor expectations and growing
   regulatory requirements (EU Deforestation Regulation).

5. Accelerate Water-Positive Operations in High-Stress Watersheds:
   P&G should identify all manufacturing sites in water-stressed basins and set site-level
   water replenishment targets that exceed consumption (i.e., become "water positive").
   This includes investing in on-site water recycling, working with local watershed
   restoration projects, and redesigning water-intensive manufacturing processes. The
   Alliance for Water Stewardship (AWS) standard provides a credible certification
   framework for this commitment.

6. Transparent Supply Chain Disclosure:
   P&G should publish supplier lists down to Tier 2 and commit to full raw material
   traceability disclosure. Transparency is increasingly demanded by investors, regulators
   (e.g., EU Corporate Sustainability Due Diligence Directive), and consumers, and it
   creates accountability that drives genuine sustainability improvements through the value
   chain.
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nBANA 6420 — Unit 4 Assignment")
    print("Employing a Holistic Approach to Supply Chain Design")
    print("Student: Gill, Nathanael\n")
    print(f"Source data: {DEFAULT_SEC_CSV}\n")

    df = load_results()
    print_part1(df)
    print_part2()
    print_part3()

    print(f"\n{DIVIDER}")
    print("  END OF ASSIGNMENT OUTPUT")
    print(DIVIDER)


if __name__ == "__main__":
    main()
