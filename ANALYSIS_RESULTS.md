# AB InBev Supply Chain Analysis - Unit 1 Assignment Results

## Project Overview

This analysis assesses and improves the forecast performance of AB InBev's three-tiered supply chain using the dataset provided in `bana6420_u1_assigment-ab-inbev-data.xlsx`.

**Dataset:** Weekly sales and shipment data from 2016-01-04 to 2017-12-25  
**Products:** Core 1, Core 2, Core 3, Craft 1, Craft 2, Import, Innovation  
**Wholesalers:** Wholesaler 1, Wholesaler 2, Wholesaler 3, Wholesaler 4, Wholesaler 5  

---

## Part One: Measuring Demand Forecast Performance

### Q1: Weekly MAPE for Each Product and Wholesaler Combination

I calculated the Mean Absolute Percentage Error (MAPE) for the 1-week ahead forecast compared to actual weekly sales for all 35 product/wholesaler combinations across 2016-2017.

#### Key Findings

| Metric | Value |
|--------|-------|
| Total Combinations Analyzed | 35 |
| Date Range | 2016-01-04 to 2017-12-25 |
| **Largest Forecast Error** | **Craft 2 / Wholesaler 1: 17,670.27%** |
| **Smallest Forecast Error** | **Import / Wholesaler 1: 7.60%** |
| Range of Errors | 7.60% to 17,670.27% |
| Range Span | 17,662.67% |
| Mean MAPE | 540.42% |
| Median MAPE | 25.07% |
| Standard Deviation | 2,980.79% |

#### Top 10 Worst Forecasts

| Rank | Product | Wholesaler | MAPE (%) | Weeks |
|------|---------|-----------|----------|-------|
| 1 | Craft 2 | Wholesaler 1 | 17,670.27 | 70 |
| 2 | Core 1 | Wholesaler 5 | 138.48 | 99 |
| 3 | Core 1 | Wholesaler 1 | 114.66 | 63 |
| 4 | Core 3 | Wholesaler 2 | 96.39 | 103 |
| 5 | Craft 1 | Wholesaler 3 | 82.04 | 103 |
| 6 | Craft 1 | Wholesaler 2 | 69.85 | 103 |
| 7 | Craft 1 | Wholesaler 5 | 61.49 | 103 |
| 8 | Core 2 | Wholesaler 2 | 53.98 | 103 |
| 9 | Innovation | Wholesaler 4 | 48.26 | 101 |
| 10 | Innovation | Wholesaler 1 | 43.43 | 101 |

#### Top 10 Best Forecasts

| Rank | Product | Wholesaler | MAPE (%) | Weeks |
|------|---------|-----------|----------|-------|
| 1 | Core 2 | Wholesaler 5 | 18.40 | 103 |
| 2 | Core 3 | Wholesaler 5 | 16.52 | 103 |
| 3 | Import | Wholesaler 2 | 15.26 | 91 |
| 4 | Core 2 | Wholesaler 1 | 12.61 | 102 |
| 5 | Import | Wholesaler 5 | 12.37 | 90 |
| 6 | Import | Wholesaler 3 | 11.74 | 91 |
| 7 | Core 2 | Wholesaler 4 | 11.67 | 101 |
| 8 | Import | Wholesaler 4 | 10.71 | 89 |
| 9 | Core 3 | Wholesaler 1 | 9.90 | 102 |
| 10 | Import | Wholesaler 1 | 7.60 | 90 |

#### Analysis and Observations

1. **Extreme Error Outlier**: The Craft 2 / Wholesaler 1 combination exhibits an exceptionally high MAPE of 17,670.27%, which is likely due to:
   - Very low and sporadic sales volumes
   - Weeks with zero or near-zero actual sales (where percentage error becomes unbounded)
   - This is a common challenge with MAPE on low-volume products

2. **Best Performance**: Import products consistently show the best forecast accuracy:
   - All Import/Wholesaler combinations rank in the top 15 best forecasts
   - Import products appear to have more stable, predictable demand patterns

3. **Product Performance Hierarchy**:
   - **Best**: Import products (7.60% - 15.26%)
   - **Good**: Core 2, Core 3 products (9.90% - 18.40%)
   - **Moderate**: Core 1, Innovation (40%+ MAPE)
   - **Poor**: Craft 1, Craft 2 (61%+ MAPE)

4. **Median MAPE of 25.07%**: Excluding the Craft 2/Wholesaler 1 outlier, most forecasts achieve reasonable accuracy around 25%, suggesting the baseline 1-week forecast method is moderately effective.

---

## Part Two: Generating Demand Forecasts Without Seasonality

### Q2a: Exponential Smoothing Forecast Results for Core 2 / Wholesaler 2

I developed a forecast using exponential smoothing (α = 0.3) for the Core 2 / Wholesaler 2 combination, trained on historical data and evaluated on held-out test data.

#### Methodology

1. **Data Filtering**: Extracted all 103 weeks of Core 2 / Wholesaler 2 sales data
2. **Train-Test Split**: 
   - Training set: First 68 weeks (66% of data)
   - Test set: Last 35 weeks (34% of data)
3. **Exponential Smoothing**: Applied with smoothing parameter α = 0.3
   - Formula: $F(t) = \alpha \cdot D(t-1) + (1-\alpha) \cdot F(t-1)$
4. **Evaluation**: Calculated MAPE on test period to measure out-of-sample accuracy

#### Key Results

| Metric | Value |
|--------|-------|
| Total Weeks | 103 |
| Training Weeks | 68 |
| Test Weeks | 35 |
| **Test MAPE (Exponential Smoothing)** | **37.13%** |
| Baseline MAPE (1-week forecast) | 53.98% |
| Improvement over Baseline | 16.85 percentage points |

#### Observations

- The exponential smoothing model achieves **37.13% MAPE** on the test set
- This represents a **31% improvement** over the baseline 1-week forecast (53.98% MAPE)
- The model effectively captures short-term demand patterns without seasonality adjustment
- The improvement suggests that exponential smoothing provides better accuracy than the baseline method for this product/wholesaler combination

---

## Part Three: Generating Demand Forecasts With Seasonality

### Q1: Weekly Seasonal Index by Product

I calculated the weekly seasonal index for each product by aggregating sales across all 5 wholesalers and dividing each week's sales by the overall average. Products Craft 2 and Import were excluded due to limited data.

#### Methodology

1. **Aggregate Sales**: Sum weekly sales across all 5 wholesalers for each product
2. **Calculate Overall Average**: Compute mean of aggregated weekly sales
3. **Compute Seasonal Index**: Divide each week's sales by the overall average
4. **Calculate Variance**: Measure variance of seasonal indices to quantify seasonal variation

#### Seasonal Index Variance by Product

| Product | Variance | Rank |
|---------|----------|------|
| Core 3 | 0.239068 | 1 (Highest) |
| Core 1 | 0.158116 | 2 |
| Innovation | 0.122756 | 3 |
| Craft 1 | 0.057541 | 4 |
| Core 2 | 0.025702 | 5 (Lowest) |

**Largest Seasonal Variation: Core 3** (variance = 0.239068)

#### Why Core 3 Has the Largest Seasonal Variation

Core 3 exhibits the highest seasonal variance because its demand pattern shows more pronounced peaks and troughs throughout the year compared to other products. This could be due to:
- Stronger correlation with seasonal events or holidays
- More variable promotional activity timing
- Greater sensitivity to weather or seasonal consumption patterns

### Q2: Forecast Core 2/Wholesaler 2 with Seasonality

I applied seasonal adjustment to the Core 2/Wholesaler 2 forecast by deseasonalizing the training data, applying exponential smoothing, and reseasonalizing the test forecasts.

#### Methodology

1. **Deseasonalize Training Data**: Divide actual sales by seasonal index
2. **Apply Exponential Smoothing**: Forecast on deseasonalized data (α = 0.3)
3. **Reseasonalize Forecasts**: Multiply forecasts by seasonal index for test period
4. **Evaluate**: Calculate MAPE on seasonalized test data

#### Key Results

| Metric | Value |
|--------|-------|
| Training Weeks | 68 |
| Test Weeks | 35 |
| **Test MAPE (with seasonality)** | **23.11%** |
| Part Two MAPE (without seasonality) | 37.13% |
| **Improvement** | **14.02 percentage points (38% better)** |

#### Comparison Across Methods

| Method | Test MAPE | Improvement vs Baseline |
|--------|-----------|------------------------|
| Baseline (1-week forecast) | 53.98% | — |
| Exponential Smoothing (no seasonality) | 37.13% | 31% |
| Exponential Smoothing (with seasonality) | 23.11% | 57% |

#### Observations

- Adding seasonality reduced MAPE from 37.13% to 23.11%, a **38% improvement**
- The seasonal model achieves **57% better accuracy** than the original baseline forecast
- Core 2 has relatively low seasonal variance (0.026), yet accounting for it still significantly improves forecasts
- This demonstrates that even products with mild seasonality benefit from seasonal adjustment

---

## Code Organization

The analysis is implemented using a modular Python structure:

### Files

- **`ingestion.py`**: Data loading and schema inspection utilities
  - `load_excel_file()`: Load Excel files with specified sheet
  - `ingest_excel()`: Convenience wrapper pointing to data directory
  - `list_sheet_names()`: List all available sheets
  - `get_schema()` / `print_schema()`: Inspect DataFrame structure

- **`forecasting.py`**: Supply chain forecasting and analysis functions
  - `moving_average()`: Calculate moving average forecast
  - `exponential_smoothing()`: Single-period exponential smoothing
  - `exponential_smoothing_series()`: Generate full forecast series
  - `mape()`: Calculate Mean Absolute Percentage Error
  - `deseasonalize()` / `reseasonalize()`: Seasonal adjustment
  - `sample_variance()`: Excel VAR.S compatible variance
  - `bullwhip_ratio()`: Measure bullwhip effect
  - `measure_bullwhip_effect()`: Full DataFrame-based analysis

- **`Assignment1.py`**: Main analysis script
  - `part_one_q1()`: Calculate MAPE by product/wholesaler
  - Generates all Part One Question 1 results

- **`data/`**: Excel data file
  - `bana6420_u1_assigment-ab-inbev-data.xlsx`

### Key Features

- Type hints throughout for code clarity
- Pure functions with no side effects
- Consistent error handling
- Modular design allows reuse across assignment parts

---

## Data Summary

### Sheet Descriptions

1. **Sales & Demand Forecasts** (3,309 rows)
   - Columns: Week Beginning, Wslr, PDCN, Week's Sales (Barrels), 1 Week Forecast Demand
   - Contains all product/wholesaler combinations across 2016-2017
   - 1-week ahead forecasts for demand

2. **Shipment Data**
   - Columns: Year, Month, Week Beginning, Shpd_Dt, Wholesaler, Product, Barrels
   - Used for bullwhip effect analysis

3. **Inventory Levels**
   - Available for inventory analysis

4. **Instructions**
   - Assignment instructions and context

---

## Methodology

### MAPE Calculation

Mean Absolute Percentage Error is calculated as:

$$MAPE = \frac{1}{n} \sum_{t=1}^{n} \left| \frac{A_t - F_t}{A_t} \right| \times 100\%$$

Where:
- $A_t$ = Actual value (weekly sales)
- $F_t$ = Forecast value (1-week ahead forecast)
- $n$ = Number of observations
- Zero actuals are excluded from calculation to avoid undefined values

### Interpretation

- **MAPE < 10%**: Excellent forecast accuracy
- **MAPE 10-20%**: Good forecast accuracy
- **MAPE 20-50%**: Acceptable forecast accuracy
- **MAPE > 50%**: Poor forecast accuracy

---

## Running the Analysis

```bash
# Install dependencies
pip install pandas openpyxl numpy pdfplumber

# Run analysis
python Assignment1.py
```

---

## Next Steps

The remaining assignment parts will focus on:

1. **Part Two**: Develop improved forecasts for Core 2/Wholesaler 2
   - Test moving average and exponential smoothing methods
   - Split data into training (2/3) and test (1/3) sets
   - Compare performance against baseline

2. **Part Three**: Add seasonality to forecasts
   - Calculate seasonal indices by product
   - Deseasonalize, forecast, and reseasonalize
   - Evaluate improvement from seasonal adjustment

3. **Part Four**: Assess bullwhip effect
   - Calculate monthly variance for shipments and demand
   - Compute bullwhip ratio for all combinations
   - Identify products/wholesalers with high amplification

---

**Last Updated:** 2026-02-01  
**Python Version:** 3.14.2  
**Key Libraries:** pandas, numpy, openpyxl
