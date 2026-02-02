from typing import List, Iterable, Union, Optional, Dict
import math
import numpy as np
import pandas as pd

def moving_average(actuals: List[float], window: int) -> float:
    """Calculate moving average forecast for the next period."""
    if window <= 0:
        raise ValueError("window must be positive")
    if len(actuals) < window:
        raise ValueError("not enough data for the specified window")
    return sum(actuals[-window:]) / window


def exponential_smoothing(actual_prev: float, forecast_prev: float, alpha: float) -> float:
    """Calculate next period forecast using exponential smoothing."""
    if not 0 <= alpha <= 1:
        raise ValueError("alpha must be between 0 and 1")
    return alpha * actual_prev + (1 - alpha) * forecast_prev


def exponential_smoothing_series(actuals: List[float], alpha: float) -> List[float]:
    """Generate forecast series using exponential smoothing (assumes F1 = D1)."""
    if not actuals:
        raise ValueError("actuals cannot be empty")
    if not 0 <= alpha <= 1:
        raise ValueError("alpha must be between 0 and 1")
    
    forecasts = [actuals[0]]
    for t in range(1, len(actuals)):
        ft = alpha * actuals[t - 1] + (1 - alpha) * forecasts[t - 1]
        forecasts.append(ft)
    return forecasts


def mape(actuals: List[float], forecasts: List[float]) -> float:
    """Calculate Mean Absolute Percentage Error (MAPE) as a percentage."""
    if len(actuals) != len(forecasts):
        raise ValueError("actuals and forecasts must be the same length")
    
    ape_values = []
    for a, f in zip(actuals, forecasts):
        if a == 0:
            continue
        ape_values.append(abs(a - f) / abs(a))
    
    if not ape_values:
        raise ValueError("no valid periods to compute MAPE")
    
    return sum(ape_values) / len(ape_values) * 100


def deseasonalize(actuals: List[float], seasonal_index: List[float]) -> List[float]:
    """Remove seasonal component from actuals."""
    if len(actuals) != len(seasonal_index):
        raise ValueError("actuals and seasonal_index must be the same length")
    return [a / s for a, s in zip(actuals, seasonal_index)]


def reseasonalize(forecasts: List[float], seasonal_index: List[float]) -> List[float]:
    """Reapply seasonal component to forecasts."""
    if len(forecasts) != len(seasonal_index):
        raise ValueError("forecasts and seasonal_index must be the same length")
    return [f * s for f, s in zip(forecasts, seasonal_index)]


def sample_variance(x: Iterable[float], ddof: int = 1) -> float:
    """Calculate sample variance (matches Excel VAR.S with ddof=1 by default)."""
    vals = []
    for v in x:
        if v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if math.isnan(fv) or math.isinf(fv):
            continue
        vals.append(fv)
    
    n = len(vals)
    if n <= ddof:
        raise ValueError(f"Need at least {ddof + 1} valid observations; got {n}")
    
    mean = sum(vals) / n
    sse = sum((v - mean) ** 2 for v in vals)
    return sse / (n - ddof)


def bullwhip_ratio(shipment: Iterable[float], demand: Iterable[float], ddof: int = 1, epsilon: float = 0.0) -> float:
    """Calculate bullwhip ratio = Var(shipments) / Var(demand)."""
    var_ship = sample_variance(shipment, ddof=ddof)
    var_dem = sample_variance(demand, ddof=ddof)
    
    denom = var_dem if var_dem > epsilon else epsilon
    if denom == 0.0:
        raise ValueError("Demand variance is zero; bullwhip ratio undefined.")
    
    return var_ship / denom


def measure_bullwhip_effect(df: pd.DataFrame, date_col: str, demand_col: str, shipments_col: str, freq: str = "M", filters: Optional[Dict] = None) -> Dict:
    """Measure bullwhip effect by aggregating to periods and computing variance ratio."""
    if date_col not in df.columns or demand_col not in df.columns or shipments_col not in df.columns:
        raise KeyError("Required columns not found in DataFrame")
    
    d = df.copy()
    
    if filters:
        for k, v in filters.items():
            if k not in d.columns:
                raise KeyError(f"filter column '{k}' not in df.columns")
            d = d.loc[d[k] == v]
    
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d = d.dropna(subset=[date_col])
    
    d[demand_col] = pd.to_numeric(d[demand_col], errors="coerce")
    d[shipments_col] = pd.to_numeric(d[shipments_col], errors="coerce")
    d = d.dropna(subset=[demand_col, shipments_col])
    
    agg = (
        d.set_index(date_col)[[demand_col, shipments_col]]
        .resample(freq)
        .sum(min_count=1)
        .dropna()
    )
    
    if agg.empty:
        raise ValueError("No data after filtering/cleaning/aggregation.")
    
    var_demand = agg[demand_col].var()
    var_ship = agg[shipments_col].var()
    
    if var_demand == 0.0:
        raise ValueError("Demand variance is zero; bullwhip ratio undefined.")
    
    ratio = var_ship / var_demand
    
    return {
        'bullwhip_ratio': float(ratio),
        'var_shipments': float(var_ship),
        'var_demand': float(var_demand),
        'n_periods': int(len(agg)),
    }
