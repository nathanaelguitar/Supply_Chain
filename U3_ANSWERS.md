# U3 Assignment Answers
## Finger Lakes Activewear — Optimizing Production Capacity Allocation
*Gill, Nathanael — BANA 6420*

---

## Part One — Optimal Production Quantity (No Capacity Limit)

### Solution Steps

The setup here is a classic single-period newsvendor. FLA makes a one-shot production decision before the season starts, then lives with whatever demand shows up. The two cost parameters the problem gives us are:

- **Overage cost (o)** = 10% of retail price — what it costs to have one unsold jacket at the end of the season
- **Underage cost (u)** = 30% of retail price — the lost margin from stocking out one unit

Since both are defined as a fixed percentage of price, the **critical fractile is identical for every product**:

$$CF = \frac{u}{u + o} = \frac{0.30}{0.30 + 0.10} = \frac{0.30}{0.40} = \mathbf{0.75}$$

This means FLA wants to satisfy demand 75% of the time. The logic: running out of a jacket is 3× more painful than being stuck with one, so we bias toward overproducing slightly.

Once we have CF, the optimal quantity under Normal demand is:

$$Q^* = \mu + z \cdot \sigma \quad \text{where } z = \Phi^{-1}(0.75) = 0.6745$$

Applying this to each of the 11 product lines:

| Product | Price | u | o | μ | σ | Q* |
|---|---|---|---|---|---|---|
| Conesus | $90 | $27.00 | $9.00 | 3,000 | 2,000 | **4,349.0** |
| Hemlock | $90 | $27.00 | $9.00 | 2,500 | 600 | **2,904.7** |
| Canadice | $150 | $45.00 | $15.00 | 2,000 | 1,400 | **2,944.3** |
| Honeoye | $170 | $51.00 | $17.00 | 2,000 | 800 | **2,539.6** |
| Canandaigua | $80 | $24.00 | $8.00 | 1,250 | 500 | **1,587.2** |
| Keuka | $110 | $33.00 | $11.00 | 1,000 | 400 | **1,269.8** |
| Seneca | $100 | $30.00 | $10.00 | 1,000 | 600 | **1,404.7** |
| Cayuga | $70 | $21.00 | $7.00 | 4,000 | 1,100 | **4,741.9** |
| Owasco | $130 | $39.00 | $13.00 | 1,000 | 1,000 | **1,674.5** |
| Skaneateles | $120 | $36.00 | $12.00 | 1,000 | 700 | **1,472.1** |
| Otisco | $100 | $30.00 | $10.00 | 1,250 | 750 | **1,755.9** |

**Total unconstrained capacity required: 26,643.7 units**

A few things worth noting: the critical fractile is the same across the board, but Q* still varies a lot between products — entirely driven by differences in μ and σ. Conesus and Cayuga end up with the highest Q* values because they have both large means and large standard deviations, so the z-buffer adds a lot of units. Keuka comes in lowest because it has a small mean and relatively tight demand spread.

---

## Part Two — Optimal Production Quantity with Capacity Limit (20,000 units)

### Solution Steps

The unconstrained total was ~26,644 units but we only have **20,000** to work with. That's a ~25% cut, so we can't just give each product its standalone Q*. We need to allocate capacity rationally.

The mechanism is the **shadow price of capacity, θ**. Think of θ as a tax on production — it gets added to the effective overage cost and subtracted from the effective underage cost for every product simultaneously, shifting all CFs down until total demand exactly equals 20,000. The adjusted critical fractile for each product becomes:

$$CF_i(\theta) = \frac{u_i - \theta}{u_i + o_i}$$

We solve for θ using bisection (same idea as Excel's Goal Seek, just not Excel). The result:

$$\boxed{\theta = 10.31}$$

This means one additional unit of capacity is worth about **$10.31** to FLA — that's the marginal value of relaxing the capacity constraint by one unit.

Optimal constrained quantities:

| Product | CF (unconstrained) | CF (constrained) | Q* (constrained) |
|---|---|---|---|
| Conesus | 0.7500 | 0.4637 | 2,817.9 |
| Hemlock | 0.7500 | 0.4637 | 2,445.4 |
| Canadice | 0.7500 | 0.5782 | 2,276.3 |
| Honeoye | 0.7500 | **0.5984** | 2,199.5 |
| Canandaigua | 0.7500 | 0.4279 | 1,159.2 |
| Keuka | 0.7500 | 0.5158 | 1,015.8 |
| Seneca | 0.7500 | 0.4924 | 988.5 |
| Cayuga | 0.7500 | **0.3819** | 3,669.6 |
| Owasco | 0.7500 | 0.5518 | 1,130.2 |
| Skaneateles | 0.7500 | 0.5353 | 1,062.0 |
| Otisco | 0.7500 | 0.4924 | 1,235.6 |
| **Total** | | | **20,000.0** ✓ |

### Highest CF: Honeoye (0.5984)

Honeoye has the highest retail price ($170), which means the highest absolute underage cost ($51). Even after subtracting θ = $10.31, its adjusted underage cost ($40.69) is still the largest of any product. The CF formula rewards products with high u relative to (u + o) — so Honeoye gets the most favorable service level under the constraint. Intuitively: if you're going to disappoint a customer, don't let it be the one buying your most expensive jacket.

### Lowest CF: Cayuga (0.3819)

Cayuga is the cheapest product ($70), giving it the lowest absolute underage cost ($21). After subtracting θ = $10.31, its adjusted u is only $10.69 — the smallest of the group. The capacity tax hits cheap products disproportionately hard because their underage cost doesn't have as much cushion. The model is essentially telling us: when capacity is tight, don't over-invest in your cheapest SKU.

---

## Part Three — Risk Ranking & Speculative Capacity

### Solution Steps

Now we split the problem in time. FLA places an **initial (speculative) order** before demand is known, then can follow up with a **reactive order** once early-season signals come in. The question is: which products should get the early order?

The answer comes from the **risk ranking index**:

$$R_i = (u_i + o_i) \cdot \frac{\sigma_i}{\mu_i}$$

High R = high risk from producing early (either the cost consequences are large, or demand is highly uncertain relative to its mean, or both). Low R = safe to produce speculatively. Since u and o are proportional to price across all products here, the ranking is largely driven by the **coefficient of variation (CV = σ/μ)**.

Full risk ranking:

| Rank | Product | Risk Index | CV (σ/μ) |
|---|---|---|---|
| 1 | **Cayuga** | 7.70 | 0.275 |
| 2 | **Hemlock** | 8.64 | 0.240 |
| 3 | **Canandaigua** | 12.80 | 0.400 |
| 4 | **Keuka** | 17.60 | 0.400 |
| 5 | Conesus | 24.00 | 0.667 |
| 6 | Seneca | 24.00 | 0.600 |
| 7 | Otisco | 24.00 | 0.600 |
| 8 | Honeoye | 27.20 | 0.400 |
| 9 | Skaneateles | 33.60 | 0.700 |
| 10 | Canadice | 42.00 | 0.700 |
| 11 | **Owasco** | 52.00 | 1.000 |

Owasco is the riskiest by a wide margin — its demand std equals its mean (CV = 1.0). That's a coin-flip on demand at every scale. Definitely not producing that one speculatively.

---

### 3A — Speculative Capacity = 10,000 units

**Recommended products for speculative production: Cayuga, Hemlock, Canandaigua, Keuka**

These are the four lowest-risk products. The first three (Cayuga, Hemlock, Canandaigua) sum to ~9,234 standalone Q* — under the 10,000 cap. But leaving ~766 units of capacity unused is wasteful, so we include the next-safest product (Keuka, risk index 17.60). Their combined standalone Q* would be ~10,504, which exceeds 10,000 — so the shadow-price solver trims all four products down to exactly fill the constraint.

| Product | Risk Index | CF (Part 2) | CF (Speculative) | Q_spec |
|---|---|---|---|---|
| Cayuga | 7.70 | 0.3819 | 0.6747 | 4,498.2 |
| Hemlock | 8.64 | 0.4637 | 0.6914 | 2,800.0 |
| Canandaigua | 12.80 | 0.4279 | 0.6841 | 1,489.6 |
| Keuka | 17.60 | 0.5158 | 0.7021 | 1,212.2 |
| **Total** | | | | **10,000.0** ✓ |

**Shadow price θ = 2.11** — capacity is now binding. Each additional unit of speculative capacity would be worth ~$2.11.

Compared to Part 2: all four products have *higher* CFs here than they did under the full 20,000-unit constraint. That makes sense — in Part 2 they were competing with 7 other products for a tight budget; here they only share with 3 other low-risk items. The speculative CFs (0.67–0.70) are lower than the unconstrained 0.75 but substantially better than the Part 2 values (0.38–0.52). Producing a smaller, curated set of safe SKUs lets us give each one a more generous service level.

The remaining **7 products** (Conesus, Seneca, Otisco, Honeoye, Skaneateles, Canadice, Owasco) get deferred to reactive capacity — produced only after early-season demand signals reduce uncertainty.

---

### 3B — Speculative Capacity = 5,000 units

When the speculative cap drops to 5,000, Cayuga alone (Q* = 4,742) fits but doesn't fill the budget. Adding Hemlock (Q* = 2,905) pushes the combined total to ~7,647, exceeding 5,000 — so the shadow-price solver trims both products to exactly 5,000.

| Product | Risk Index | CF (Part 2) | CF (Speculative) | Q_spec |
|---|---|---|---|---|
| Cayuga | 7.70 | 0.3819 | 0.1474 | 2,847.4 |
| Hemlock | 8.64 | 0.4637 | 0.2813 | 2,152.6 |
| **Total** | | | | **5,000.0** ✓ |

**Shadow price θ = 16.87** — capacity is extremely tight. Each additional unit of speculative capacity is now worth ~$16.87, far higher than in 3A. The CFs have been crushed well below 0.50, meaning we're actually producing *less* than the mean demand for both products. This is a sign the constraint is severely binding.

The remaining **9 products** are all reserved for reactive production.

**How does the decision change?** We go from 4 products to 2, and the shadow price jumps from $2.11 to $16.87. The tighter the speculative budget, the more selective we have to be — but now the constraint also bites *within* the selected set, compressing CFs and reducing per-product quantities significantly. This forces more of the portfolio into reactive mode, which actually *reduces risk* at the cost of needing more operational flexibility (faster sourcing, overtime, etc.) to fill orders reactively. The high θ also signals that investing in additional speculative capacity would be highly valuable.

---

## Part Four — Capacity Management Recommendations

A few concrete recommendations for FLA, ranked roughly by impact:

**1. Build a reactive capacity channel — don't rely on a single overseas factory**

The numbers in Part 3 make it clear: the speculative window can only absorb the safest products. For everything else, FLA needs a fast-response supply option. This could be a domestic cut-and-sew partner, a near-shore supplier, or even reserved capacity at the existing factory on a premium schedule. The shadow price θ ≈ $10.31 from Part 2 tells us each additional unit of capacity is worth over $10 in margin — paying a premium for reactive flexibility is almost certainly justified.

**2. Produce the low-risk, high-volume SKUs early and commit**

Cayuga (μ = 4,000, CV = 0.275) and Hemlock (μ = 2,500, CV = 0.240) are good bets even before the season. Their demand distributions are tight relative to their means — forecast errors are unlikely to be catastrophic. Committing to these speculatively frees up the reactive channel for riskier, lower-volume SKUs.

**3. Invest in earlier demand signals for high-CV products**

Owasco (CV = 1.0), Canadice (CV = 0.70), and Skaneateles (CV = 0.70) are essentially unpredictable from a forecast-only standpoint. Pre-season retailer commitments, early-bird consumer pre-orders, or even soft launch campaigns for these lines would compress σ significantly — and a smaller σ directly reduces required Q* buffers and improves expected profit.

**4. Reduce overseas lead times where possible**

Shorter lead times widen the reactive window. If FLA can shave 3–4 weeks off its overseas factory cycle, more of the portfolio shifts from "must decide now" to "can wait for data." This doesn't require a new supplier — it could be as simple as earlier fabric sourcing, pre-positioned materials, or streamlined customs/logistics.

**5. Reassess Owasco's product positioning**

A CV of 1.0 means demand is as uncertain as it gets. Unless Owasco commands a substantial premium that justifies the risk, FLA should consider whether this SKU is worth carrying at all, or whether it can be redesigned to reduce demand variance (e.g., fewer variants, simpler colorways, tighter distribution).

---

*All calculations computed in `u3_inventory_optimization.py` using the Finger Lakes dataset loaded via `u3_ingestion.py`.*
