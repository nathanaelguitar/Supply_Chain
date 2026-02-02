import pandas as pd
import numpy as np
from typing import Dict, List
from ingestion import ingest_excel, list_sheet_names, print_schema
from forecasting import mape, measure_bullwhip_effect, exponential_smoothing_series, deseasonalize, reseasonalize, sample_variance


# PART ONE: MEASURING DEMAND FORECAST PERFORMANCE
def part_one_q1(df_sales: pd.DataFrame) -> pd.DataFrame:
    """Calculate weekly MAPE for each product and wholesaler combination."""
    
    results = []
    
    # Get unique combinations of product and wholesaler
    for product in df_sales['PDCN'].unique():
        for wholesaler in df_sales['Wslr'].unique():
            # Filter data for this combination
            mask = (df_sales['PDCN'] == product) & (df_sales['Wslr'] == wholesaler)
            combo_data = df_sales[mask].copy()
            
            # Skip if no data for this combination
            if len(combo_data) == 0:
                continue
            
            # Calculate MAPE for this combination
            actuals = combo_data["Week's Sales (Barrels)"].tolist()
            forecasts = combo_data['1 Week Forecast Demand'].tolist()
            
            try:
                combo_mape = mape(actuals, forecasts)
                num_weeks = len(combo_data)
                
                results.append({
                    'Product': product,
                    'Wholesaler': wholesaler,
                    'MAPE (%)': combo_mape,
                    'Weeks': num_weeks
                })
            except ValueError:
                # Skip if MAPE calculation fails (e.g., all actuals are zero)
                pass
    
    results_df = pd.DataFrame(results).sort_values('MAPE (%)', ascending=False)
    return results_df


# PART TWO: GENERATING DEMAND FORECASTS WITHOUT SEASONALITY
def part_two_q1(df_sales: pd.DataFrame) -> Dict:
    """Forecast Core 2/Wholesaler 2 without seasonality."""
    
    # Filter for Core 2 / Wholesaler 2
    mask = (df_sales['PDCN'] == 'Core 2') & (df_sales['Wslr'] == 'Wholesaler 2')
    combo_data = df_sales[mask].copy()
    
    # Split 2/3 train, 1/3 test
    split_idx = int(len(combo_data) * 2/3)
    train = combo_data.iloc[:split_idx]
    test = combo_data.iloc[split_idx:]
    
    # Get actuals
    train_actuals = train["Week's Sales (Barrels)"].tolist()
    test_actuals = test["Week's Sales (Barrels)"].tolist()
    
    # Generate forecasts for test period using exponential smoothing
    forecasts = exponential_smoothing_series(train_actuals, alpha=0.3)
    
    # Calculate MAPE on test period
    test_mape = mape(test_actuals, forecasts[-len(test_actuals):])
    
    return {
        'product': 'Core 2',
        'wholesaler': 'Wholesaler 2',
        'train_weeks': len(train),
        'test_weeks': len(test),
        'mape': test_mape
    }


# PART THREE: GENERATING DEMAND FORECASTS WITH SEASONALITY
def part_three_q1(df_sales: pd.DataFrame) -> Dict:
    """Calculate weekly seasonal index for each product (excluding Craft 2 and Import)."""
    
    # Products to analyze (excluding Craft 2 and Import per assignment)
    products = ['Core 1', 'Core 2', 'Core 3', 'Craft 1', 'Innovation']
    
    results = {}
    
    for product in products:
        # Filter for this product across all wholesalers
        product_data = df_sales[df_sales['PDCN'] == product].copy()
        
        # Aggregate sales across all 5 wholesalers by week
        weekly_sales = product_data.groupby('Week Beginning')["Week's Sales (Barrels)"].sum().reset_index()
        weekly_sales = weekly_sales.sort_values('Week Beginning')
        
        # Calculate overall average
        overall_avg = weekly_sales["Week's Sales (Barrels)"].mean()
        
        # Calculate seasonal index for each week (week's sales / overall average)
        seasonal_indices = (weekly_sales["Week's Sales (Barrels)"] / overall_avg).tolist()
        
        # Calculate variance of seasonal indices
        si_variance = sample_variance(seasonal_indices)
        
        results[product] = {
            'seasonal_indices': seasonal_indices,
            'variance': si_variance,
            'num_weeks': len(seasonal_indices),
            'weekly_sales': weekly_sales
        }
    
    return results


def part_three_q2(df_sales: pd.DataFrame, seasonal_results: Dict) -> Dict:
    """Forecast Core 2/Wholesaler 2 with seasonality adjustment."""
    
    # Filter for Core 2 / Wholesaler 2
    mask = (df_sales['PDCN'] == 'Core 2') & (df_sales['Wslr'] == 'Wholesaler 2')
    combo_data = df_sales[mask].copy().sort_values('Week Beginning').reset_index(drop=True)
    
    # Get the Core 2 seasonal indices (aggregated across wholesalers)
    core2_seasonal = seasonal_results['Core 2']
    
    # We need to match seasonal indices to each week in combo_data
    # Get the week order from the aggregated data
    core2_weekly = core2_seasonal['weekly_sales'].sort_values('Week Beginning').reset_index(drop=True)
    
    # Create a mapping of week -> seasonal index
    week_to_si = dict(zip(core2_weekly['Week Beginning'], core2_seasonal['seasonal_indices']))
    
    # Get seasonal indices for each week in combo_data
    combo_data['seasonal_index'] = combo_data['Week Beginning'].map(week_to_si)
    
    # Drop rows where seasonal index is missing
    combo_data = combo_data.dropna(subset=['seasonal_index']).reset_index(drop=True)
    
    # Split 2/3 train, 1/3 test
    split_idx = int(len(combo_data) * 2/3)
    train = combo_data.iloc[:split_idx]
    test = combo_data.iloc[split_idx:]
    
    # Get actuals and seasonal indices
    train_actuals = train["Week's Sales (Barrels)"].tolist()
    train_si = train['seasonal_index'].tolist()
    test_actuals = test["Week's Sales (Barrels)"].tolist()
    test_si = test['seasonal_index'].tolist()
    
    # Deseasonalize training data
    train_deseasonalized = deseasonalize(train_actuals, train_si)
    
    # Generate forecasts on deseasonalized data using exponential smoothing
    deseasonalized_forecasts = exponential_smoothing_series(train_deseasonalized, alpha=0.3)
    
    # Extend forecasts into test period (use last forecast value as base)
    last_forecast = deseasonalized_forecasts[-1]
    test_deseasonalized_forecasts = [last_forecast] * len(test_actuals)
    
    # Reseasonalize the test forecasts
    test_forecasts = reseasonalize(test_deseasonalized_forecasts, test_si)
    
    # Calculate MAPE on test period
    test_mape = mape(test_actuals, test_forecasts)
    
    return {
        'product': 'Core 2',
        'wholesaler': 'Wholesaler 2',
        'train_weeks': len(train),
        'test_weeks': len(test),
        'mape': test_mape,
        'seasonal_variance': core2_seasonal['variance']
    }


def main():
    file_name = "bana6420_u1_assigment-ab-inbev-data.xlsx"
    
    try:
        # Load the Sales & Demand Forecasts sheet
        df_sales = ingest_excel(file_name, sheet_name='Sales & Demand Forecasts')
        
        if df_sales is not None:
            # PART ONE, Q1
            results_df = part_one_q1(df_sales)
            
            # print(results_df.to_string(index=False))
            # print()
            
            # Summary statistics
            # print("-" * 80)
            # print("SUMMARY STATISTICS:")
            # print("-" * 80)
            # print(f"Largest forecast error: {results_df.iloc[0]['Product']} / {results_df.iloc[0]['Wholesaler']}")
            # print(f"  MAPE = {results_df.iloc[0]['MAPE (%)']:.2f}%\n")
            # 
            # min_mape = results_df['MAPE (%)'].min()
            # max_mape = results_df['MAPE (%)'].max()
            # print(f"Range of forecast errors: {min_mape:.2f}% to {max_mape:.2f}%")
            # print(f"Range span: {max_mape - min_mape:.2f}%\n")
            
            # PART TWO, Q2a
            part_two_results = part_two_q1(df_sales)
            
            # print("-" * 80)
            # print("PART TWO: DEMAND FORECASTS WITHOUT SEASONALITY")
            # print("-" * 80)
            # print(f"Product: {part_two_results['product']}")
            # print(f"Wholesaler: {part_two_results['wholesaler']}")
            # print(f"Training weeks: {part_two_results['train_weeks']}")
            # print(f"Test weeks: {part_two_results['test_weeks']}")
            # print(f"Test MAPE (Exponential Smoothing, α=0.3): {part_two_results['mape']:.2f}%")
            # print("-" * 80)
            
            # PART THREE
            seasonal_results = part_three_q1(df_sales)
            part_three_results = part_three_q2(df_sales, seasonal_results)
            
            # print("-" * 80)
            # print("PART THREE: DEMAND FORECASTS WITH SEASONALITY")
            # print("-" * 80)
            # 
            # # Q1: Seasonal variation by product
            # print("Q1: Weekly Seasonal Index Variance by Product")
            # print("-" * 40)
            # sorted_products = sorted(seasonal_results.items(), key=lambda x: x[1]['variance'], reverse=True)
            # for product, data in sorted_products:
            #     print(f"  {product}: variance = {data['variance']:.6f}")
            # largest_var_product = sorted_products[0][0]
            # print(f"\nLargest seasonal variation: {largest_var_product}")
            # print(f"  Variance = {sorted_products[0][1]['variance']:.6f}")
            # 
            # # Q2: Forecast with seasonality
            # print("\n" + "-" * 40)
            # print("Q2: Forecast Core 2/Wholesaler 2 with Seasonality")
            # print("-" * 40)
            # print(f"Training weeks: {part_three_results['train_weeks']}")
            # print(f"Test weeks: {part_three_results['test_weeks']}")
            # print(f"Test MAPE (with seasonality): {part_three_results['mape']:.2f}%")
            # print(f"Part Two MAPE (without seasonality): {part_two_results['mape']:.2f}%")
            # improvement = part_two_results['mape'] - part_three_results['mape']
            # print(f"Improvement: {improvement:.2f} percentage points")
            # print("-" * 80)
            
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()