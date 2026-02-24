# python_tools.md
# Supply Chain Analytics in Python
Replace the Excel “tools” with reproducible Python formulas and functions.

---

## Setup

```python
import math
from dataclasses import dataclass
from typing import List, Callable, Tuple, Optional
from itertools import combinations

# If available (recommended)
from scipy.stats import norm

# If you do not have SciPy, install it:
# pip install scipy
```

## Core: Newsvendor (single item) 

### Costs

**Underage cost:** `u = price - unit_cost_effective`

**Overage cost:** `o = unit_cost_effective - salvage_value`

```python
def underage_cost(price: float, unit_cost: float) -> float:
    return price - unit_cost

def overage_cost(unit_cost: float, salvage: float) -> float:
    return unit_cost - salvage
```

### Critical fractile

```python
def critical_fractile(u: float, o: float) -> float:
    if u <= 0 or o < 0:
        raise ValueError("Need u>0 and o>=0.")
    return u / (u + o)
```

### Optimal quantity (Normal demand)

Excel: `Q* = μ + zσ` with `z = NORMSINV(CF)`

```python
def newsvendor_q_normal(mu: float, sigma: float, u: float, o: float) -> float:
    cf = critical_fractile(u, o)
    z = norm.ppf(cf)
    return mu + z * sigma
```

### Handling shipping and salvage correctly

**If customers pay shipping**
> shipping does not affect your unit economics: do not add it to cost.

**If you offer free shipping**
> shipping is a real unit cost you pay: add it to unit cost.

```python
def effective_unit_cost(production_cost: float, shipping_cost: float, free_shipping: bool) -> float:
    return production_cost + (shipping_cost if free_shipping else 0.0)
```

**Example:**
```python
price = 100
prod = 30
ship = 10
salvage = 0
unit_cost = effective_unit_cost(prod, ship, free_shipping=True)  # 40
u = underage_cost(price, unit_cost)  # 60
o = overage_cost(unit_cost, salvage) # 40
cf = critical_fractile(u, o)         # 0.6
```

---

## Multi-item newsvendor with capacity limit (shadow price method)

### Model you are using

For each item i (Normal demand):

- **Adjusted underage:** `u_i - θ`
- **Adjusted overage:** `o_i + θ`

But the CF simplifies to:

> `CF_i(θ) = (u_i - θ) / (u_i + o_i)`

Then:

> `Q_i(θ) = μ_i + z_i(θ) σ_i`

Choose `θ` so that `sum_i Q_i(θ) = Capacity`

### Data structure

```python
@dataclass
class Item:
    name: str
    mu: float
    sigma: float
    u: float
    o: float
```

### Quantity given θ

Clamp CF into (0,1) to avoid infinities when θ pushes it out of bounds.

```python
def cf_with_theta(item: Item, theta: float, eps: float = 1e-9) -> float:
    cf = (item.u - theta) / (item.u + item.o)
    return min(max(cf, eps), 1 - eps)

def q_with_theta(item: Item, theta: float) -> float:
    cf = cf_with_theta(item, theta)
    z = norm.ppf(cf)
    return item.mu + z * item.sigma
```

### Solve for θ by bisection (Excel Goal Seek replacement)

Monotonicity: increasing θ reduces CF and reduces Q, so sum Q decreases as θ increases.

```python
def solve_theta_for_capacity(
    items: List[Item],
    capacity: float,
    theta_low: float = 0.0,
    theta_high: float = 1e6,
    tol: float = 1e-6,
    max_iter: int = 200
) -> float:
    
    def total_q(theta: float) -> float:
        return sum(q_with_theta(it, theta) for it in items)

    # Expand theta_high until total_q(theta_high) <= capacity
    # If using shadow price, theta effectively reduces CF.
    # Higher theta -> lower CF -> lower Q.
    # We need to find a theta high enough that Total Q <= Capacity.
    
    # Safety check for initial high
    limit_check = 0
    while total_q(theta_high) > capacity:
        theta_high *= 2
        limit_check += 1
        if limit_check > 50: # Avoid infinite loop if capacity too low for any theta
             raise RuntimeError("Could not bracket theta. Capacity may be too low vs demand/cost setup.")

    lo, hi = theta_low, theta_high
    for _ in range(max_iter):
        mid = (lo + hi) / 2
        tq = total_q(mid)
        if abs(tq - capacity) <= tol:
            return mid
        if tq > capacity:
            lo = mid  # need larger theta to reduce total Q
        else:
            hi = mid
    return (lo + hi) / 2
```

### Compute optimal allocation

```python
def allocate_with_capacity(items: List[Item], capacity: float) -> Tuple[float, List[Tuple[str, float]]]:
    theta = solve_theta_for_capacity(items, capacity)
    alloc = [(it.name, q_with_theta(it, theta)) for it in items]
    return theta, alloc
```

---

## Risk ranking index (production sequencing)

**Risk index:**
> `R_i = (u_i + o_i) * (σ_i / μ_i)`

If all items have same u and o, risk ranking reduces to coefficient of variation `σ/μ`.

```python
def risk_index(item: Item) -> float:
    return (item.u + item.o) * (item.sigma / item.mu)

def coefficient_of_variation(mu: float, sigma: float) -> float:
    return sigma / mu
```

---

## Speculative vs reactive capacity planning (practical workflow)

**Typical workflow you can code:**

1. Compute risk indices and rank items.
2. Select low-risk set for speculative production.
3. Allocate speculative capacity among selected items using shadow price solver.
4. Leave high-risk items for reactive production once demand signal arrives.

**Brute-force selection (small number of SKUs):**

```python
def best_selection_by_risk_gap(items: List[Item], capacity: float, max_k: Optional[int] = None):
    # This is a placeholder heuristic: pick subsets and compute feasibility/allocation.
    # For real optimization, you’d define an objective (expected profit) and solve properly.
    best = None
    n = len(items)
    ks = range(1, n+1) if max_k is None else range(1, max_k+1)

    for k in ks:
        for subset in combinations(items, k):
            try:
                theta, alloc = allocate_with_capacity(list(subset), capacity)
                # Example heuristic objective: minimize average risk of produced items (lower is “safer”)
                obj = sum(risk_index(it) for it in subset) / k
                if best is None or obj < best["obj"]:
                    best = {"obj": obj, "subset": [it.name for it in subset], "theta": theta, "alloc": alloc}
            except Exception:
                pass
    return best
```

---

## Quick “quiz problem” helpers

### Solve salvage value from target CF

Given price, unit cost, and CF target, solve salvage.
`CF = u/(u+o)`, where `u = p - c`, `o = c - s`
=> `CF = (p-c)/(p - s)` (algebra)
=> `s = p - (p-c)/CF`

```python
def salvage_from_cf(price: float, unit_cost: float, cf: float) -> float:
    if cf <= 0 or cf >= 1:
        raise ValueError("cf must be in (0,1)")
    return price - (price - unit_cost) / cf
```

### Solve shadow price θ from CF with capacity limit

Given `u`, `o`, and `CF` under capacity:
`CF = (u - θ)/(u + o)` => `θ = u - CF*(u+o)`

```python
def theta_from_cf(u: float, o: float, cf: float) -> float:
    return u - cf * (u + o)
```

---

## Sanity checks you should always do

1. If CF > 0.5 then z should be positive and Q* should exceed μ.
2. If u increases, CF increases, Q* increases.
3. If salvage increases, o decreases, CF increases, Q* increases.
4. In capacity model, increasing capacity should decrease θ.

### Minimal end-to-end example

```python
items = [
    Item("A", mu=100, sigma=10, u=4, o=1),
    Item("B", mu=300, sigma=10, u=4, o=1),
]
theta, alloc = allocate_with_capacity(items, capacity=404)
print("theta:", theta)
print(alloc)
```
