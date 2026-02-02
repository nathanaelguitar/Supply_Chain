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
    combo_data = df_sales[mask].copy().sort_values('Week Beginning').reset_index(drop=True)

    # Split 2/3 train, 1/3 test
    split_idx = int(len(combo_data) * 2/3)
    train = combo_data.iloc[:split_idx]
    test = combo_data.iloc[split_idx:]

    # Get actuals
    train_actuals = train["Week's Sales (Barrels)"].tolist()
    test_actuals = test["Week's Sales (Barrels)"].tolist()

    # Generate one-step-ahead forecasts using exponential smoothing
    # Run ES on full series, then extract test period forecasts
    all_actuals = train_actuals + test_actuals
    all_forecasts = exponential_smoothing_series(all_actuals, alpha=0.3)
    test_forecasts = all_forecasts[split_idx:]

    # Calculate MAPE on test period
    test_mape = mape(test_actuals, test_forecasts)
    
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

    # Deseasonalize all data
    all_actuals = train_actuals + test_actuals
    all_si = train_si + test_si
    all_deseasonalized = deseasonalize(all_actuals, all_si)

    # Generate one-step-ahead forecasts on deseasonalized data using exponential smoothing
    all_deseasonalized_forecasts = exponential_smoothing_series(all_deseasonalized, alpha=0.3)
    test_deseasonalized_forecasts = all_deseasonalized_forecasts[split_idx:]

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


# PART FOUR: ASSESSING SUPPLY CHAIN DEMAND VARIABILITY
def part_four_q1(df_sales: pd.DataFrame, df_shipments: pd.DataFrame) -> pd.DataFrame:
    """Calculate bullwhip ratio for each product/wholesaler combination using 2017 monthly data."""
    
    # Filter for 2017 only
    df_sales_2017 = df_sales[df_sales['Week Beginning'].dt.year == 2017].copy()
    df_shipments_2017 = df_shipments[df_shipments['Year'] == 2017].copy()
    
    results = []
    
    # Get unique products and wholesalers
    products = df_sales_2017['PDCN'].unique()
    wholesalers = df_sales_2017['Wslr'].unique()
    
    for product in products:
        for wholesaler in wholesalers:
            # Filter sales (demand) data
            sales_mask = (df_sales_2017['PDCN'] == product) & (df_sales_2017['Wslr'] == wholesaler)
            sales_data = df_sales_2017[sales_mask].copy()
            
            # Filter shipment data
            ship_mask = (df_shipments_2017['Product'] == product) & (df_shipments_2017['Wholesaler'] == wholesaler)
            ship_data = df_shipments_2017[ship_mask].copy()
            
            if len(sales_data) == 0 or len(ship_data) == 0:
                continue
            
            # Aggregate to monthly for sales
            sales_data['Month'] = sales_data['Week Beginning'].dt.to_period('M')
            monthly_demand = sales_data.groupby('Month')["Week's Sales (Barrels)"].sum()
            
            # Aggregate to monthly for shipments
            monthly_shipments = ship_data.groupby('Month')['Barrels'].sum()
            
            # Need at least 2 months for variance calculation
            if len(monthly_demand) < 2 or len(monthly_shipments) < 2:
                continue
            
            try:
                var_demand = sample_variance(monthly_demand.values)
                var_shipments = sample_variance(monthly_shipments.values)
                
                if var_demand > 0:
                    bullwhip = var_shipments / var_demand
                else:
                    bullwhip = float('inf')
                
                results.append({
                    'Product': product,
                    'Wholesaler': wholesaler,
                    'Var(Demand)': var_demand,
                    'Var(Shipments)': var_shipments,
                    'Bullwhip Ratio': bullwhip,
                    'Months': len(monthly_demand)
                })
            except ValueError:
                continue
    
    results_df = pd.DataFrame(results).sort_values('Bullwhip Ratio', ascending=False)
    return results_df


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
            
            # PART FOUR
            df_shipments = ingest_excel(file_name, sheet_name='Shipment Data')
            if df_shipments is not None:
                bullwhip_results = part_four_q1(df_sales, df_shipments)
                
                print("-" * 80)
                print("PART FOUR: BULLWHIP EFFECT ANALYSIS (2017 Monthly Data)")
                print("-" * 80)
                print(bullwhip_results.to_string(index=False))
                print()
                
                # Summary
                print("-" * 40)
                print("Summary:")
                print(f"Largest bullwhip ratio: {bullwhip_results.iloc[0]['Product']} / {bullwhip_results.iloc[0]['Wholesaler']}")
                print(f"  Ratio = {bullwhip_results.iloc[0]['Bullwhip Ratio']:.4f}")
                
                min_bw = bullwhip_results['Bullwhip Ratio'].min()
                max_bw = bullwhip_results['Bullwhip Ratio'].max()
                print(f"\nRange of bullwhip ratios: {min_bw:.4f} to {max_bw:.4f}")
                print("-" * 80)
            
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()