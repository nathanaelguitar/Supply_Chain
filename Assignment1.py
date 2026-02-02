import pandas as pd
from typing import Dict
from ingestion import ingest_excel, list_sheet_names, print_schema
from forecasting import mape, measure_bullwhip_effect, exponential_smoothing_series


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


def run_part(part_num: int, question_num: int, title: str, func, *args):
    """
    Run a part of the assignment and display results with formatted header.
    
    Args:
        part_num (int): Part number (e.g., 1, 2, 3, 4)
        question_num (int): Question number (e.g., 1)
        title (str): Title of the analysis
        func: Function to call
        *args: Arguments to pass to func
    """
    print(f"\nPART {part_num}, Q{question_num}: {title}")
    print("-" * 80)
    result = func(*args)
    return result


def main():
    file_name = "bana6420_u1_assigment-ab-inbev-data.xlsx"
    
    try:
        # Load the Sales & Demand Forecasts sheet
        df_sales = ingest_excel(file_name, sheet_name='Sales & Demand Forecasts')
        
        if df_sales is not None:
            # PART ONE, Q1
            results_df = run_part(
                1, 1,
                "Weekly MAPE for each Product and Wholesaler combination",
                part_one_q1,
                df_sales
            )
            
            print(results_df.to_string(index=False))
            print()
            
            # Summary statistics
            print("\n" + "-" * 80)
            print("SUMMARY STATISTICS:")
            print("-" * 80)
            print(f"Largest forecast error: {results_df.iloc[0]['Product']} / {results_df.iloc[0]['Wholesaler']}")
            print(f"  MAPE = {results_df.iloc[0]['MAPE (%)']:.2f}%\n")
            
            min_mape = results_df['MAPE (%)'].min()
            max_mape = results_df['MAPE (%)'].max()
            print(f"Range of forecast errors: {min_mape:.2f}% to {max_mape:.2f}%")
            print(f"Range span: {max_mape - min_mape:.2f}%\n")
            
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()


# Part Two: Generating Demand Forecasts Without Seasonality
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