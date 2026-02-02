import pandas as pd
from ingestion import ingest_excel, list_sheet_names, print_schema
from forecasting import mape, measure_bullwhip_effect, exponential_smoothing_series


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


def main():
    file_name = "bana6420_u1_assigment-ab-inbev-data.xlsx"
    
    try:
        # List all sheets in the file
        sheet_names = list_sheet_names(f"data/{file_name}")
        print(f"Available sheets: {sheet_names}\n")
        
        # Load the Sales & Demand Forecasts sheet
        df_sales = ingest_excel(file_name, sheet_name='Sales & Demand Forecasts')
        
        if df_sales is not None:
            print("="*80)
            print("PART ONE: MEASURING DEMAND FORECAST PERFORMANCE")
            print("="*80)
            print("\nQ1: Weekly MAPE for each Product and Wholesaler combination\n")
            
            # Calculate MAPE for all combinations
            results_df = part_one_q1(df_sales)
            
            print(results_df.to_string(index=False))
            print()
            
            # Summary statistics
            print("\n" + "="*80)
            print("SUMMARY STATISTICS:")
            print("="*80)
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



