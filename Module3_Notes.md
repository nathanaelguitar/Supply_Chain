# Supply Chain Analytics — Short Lifecycle Products & Capacity Decisions
Cornell MSBA — BANA 6420 Learning Notes

---

## Overview

This module focuses on how firms make production and inventory decisions under demand uncertainty, especially for short-lifecycle products such as food, fashion, and consumer electronics. The central framework is the **Newsvendor Model**, extended to multi-product settings, capacity constraints, risk sequencing, and reactive supply strategies. The goal is to determine optimal production quantities that balance lost sales risk against excess inventory risk while accounting for real operational limits.

---

## 1. Short-Lifecycle Product Decisions

Short-lifecycle products have limited selling windows and uncertain demand, forcing firms to make **one-shot production decisions** before demand is realized.

Examples:
- Fresh food (daily)
- Fashion (seasonal)
- Consumer electronics (months)

Key characteristics:

- Unsold inventory often has low or zero salvage value
- Stockouts create lost profit opportunities
- Production cannot be easily adjusted later

This environment creates the classic trade-off:

**Underage cost (u)**  
Lost profit when demand exceeds supply

**Overage cost (o)**  
Waste from unsold inventory

---

## 2. Newsvendor Model

### Critical Fractile Rule

Optimal service level:

```

CF = u / (u + o)

```

Where:

- u = selling price − unit cost
- o = unit cost − salvage value

### Optimal Production Quantity (Normal Demand)

```

Q* = μ + zσ

```

- μ = demand mean
- σ = demand standard deviation
- z = inverse normal of CF

Interpretation:

- High underage cost → produce more
- High overage cost → produce less

---

## 3. Multi-Item Newsvendor with Capacity Limits

Real systems often produce multiple products with shared capacity.

### Problem

You cannot produce each item’s standalone optimal quantity because total production exceeds capacity.

### Solution Concept: Shadow Price of Capacity (θ)

θ represents the marginal value of one extra unit of capacity.

Adjust costs:

```

Adjusted underage: u_i − θ
Adjusted overage:  o_i + θ

```

New critical fractile:

```

CF_i = (u_i − θ) / (u_i + o_i)

```

Procedure:

1. Guess θ
2. Compute optimal quantities
3. Adjust θ until total production equals capacity

---

## 4. Two-Stage Production: Speculative vs Reactive Capacity

When production can occur in two periods:

### Speculative Capacity
- Used before accurate demand information
- Based on forecasts
- Higher risk

### Reactive Capacity
- Used after demand signals arrive
- Based on actual demand
- Lower risk
- More valuable

Goal: Shift capacity toward reactive production whenever possible.

---

## 5. Risk-Based Production Sequencing

Not all products carry the same risk.

### Risk Ranking Index

```

Risk_i = (u_i + o_i) * σ_i / μ_i

```

Higher risk if:

- Larger cost consequences
- Higher demand uncertainty
- Lower demand volume

When costs are identical across items:

```

Risk ≈ σ / μ

```

(the coefficient of variation)

### Strategy

Produce low-risk items first using speculative capacity  
Delay high-risk items until demand is known

---

## 6. Capacity Allocation Strategy

Steps:

1. Rank products by risk index
2. Select low-risk items for early production
3. Allocate capacity using shadow price method
4. Use reactive capacity to produce high-risk items later

This improves supply chain efficiency by reducing forecast error exposure.

---

## 7. Make-to-Stock vs Make-to-Order

### Make-to-Stock (MTS)

- Produce based on forecasts
- Inventory available immediately
- Required when customers will not wait

Examples:
- Retail goods
- Fashion
- Consumer electronics

### Make-to-Order (MTO)

- Produce after customer order
- Eliminates inventory risk
- Requires long lead times acceptable to customers

Example:
- Aircraft manufacturing

Increasing reactive capacity moves a system closer to make-to-order efficiency.

---

## 8. Increasing Reactive Capacity

Three primary strategies:

### 1. Add Temporary Capacity
- Overtime
- Subcontracting

### 2. Reduce Lead Times
- Faster production
- Faster shipping
- Faster procurement

### 3. Obtain Earlier Demand Signals
- Advance orders
- Marketing intelligence
- Pre-sales campaigns

Earlier demand information effectively increases reactive capacity without physical expansion.

---

## 9. Global Supply Chain Simulation Insights

The simulation demonstrates real-world decision complexity beyond textbook models.

Key lessons:

### Product Design Trade-Off
Higher feature complexity may increase demand variability, reducing profitability.

### Dual Supply Strategy
Optimal supply chains combine:

- Low-cost, long-lead suppliers (speculative capacity)
- Flexible, zero-lead suppliers (reactive capacity)

### Model Limitations
The newsvendor model is a starting point, but real systems involve:

- Multi-period decisions
- Dynamic demand
- Strategic adjustments during the season

No single formula solves all supply chain problems.

---

## 10. Practical Takeaways

### Decision Framework

When facing uncertain demand:

1. Estimate underage and overage costs
2. Compute service level target
3. Adjust for capacity constraints
4. Prioritize low-risk items early
5. Preserve flexibility for high-risk items
6. Invest in earlier demand information

---

## Key Mental Model

**Capacity + Information = Risk Control**

You can reduce uncertainty by:

- Increasing capacity
- Improving forecasts
- Delaying decisions
- Designing flexible supply chains

---

## Value for Data Scientists & Analysts

Your role is not to blindly apply formulas but to:

- Adapt models to real constraints
- Quantify trade-offs
- Design decision frameworks
- Integrate data with operations strategy

This is where analytics creates competitive advantage.

---

## End of Module Summary

Optimal supply chain decisions balance:

- Profit vs risk
- Cost vs flexibility
- Forecast vs real demand
- Efficiency vs responsiveness

The best systems delay irreversible decisions until information improves.
