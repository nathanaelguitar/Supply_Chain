from ingestion import ingest_excel, list_sheet_names, print_schema
from forecasting import mape, measure_bullwhip_effect, exponential_smoothing_series


def main():
    # Load Sales & Demand Forecasts sheet
    file_name = "bana6420_u1_assigment-ab-inbev-data.xlsx"
    
    try:
        # List all sheets in the file
        sheet_names = list_sheet_names(f"data/{file_name}")
        print(f"Available sheets: {sheet_names}\n")
        
        # Load the Sales & Demand Forecasts sheet
        df_sales = ingest_excel(file_name, sheet_name='Sales & Demand Forecasts')
        
        if df_sales is not None:
            # Print schema information
            print_schema(df_sales)
            
            # Print first few rows
            print("First few rows:")
            print(df_sales.head(10))
            print("\n")
            
            # Calculate MAPE for demand forecast vs actual sales
            actuals = df_sales["Week's Sales (Barrels)"].tolist()
            forecasts = df_sales['1 Week Forecast Demand'].tolist()
            
            mape_score = mape(actuals, forecasts)
            print(f"Overall MAPE: {mape_score:.2f}%\n")
            
            # Group by Wholesaler and calculate MAPE
            print("MAPE by Wholesaler:")
            for wslr in df_sales['Wslr'].unique():
                mask = df_sales['Wslr'] == wslr
                wslr_actuals = df_sales.loc[mask, "Week's Sales (Barrels)"].tolist()
                wslr_forecasts = df_sales.loc[mask, '1 Week Forecast Demand'].tolist()
                try:
                    wslr_mape = mape(wslr_actuals, wslr_forecasts)
                    print(f"  {wslr}: {wslr_mape:.2f}%")
                except ValueError as e:
                    print(f"  {wslr}: Error - {e}")
            
            print("\n" + "="*60 + "\n")
            
            # Now load Shipment Data for bullwhip analysis
            df_shipment = ingest_excel(file_name, sheet_name='Shipment Data')
            
            if df_shipment is not None:
                print_schema(df_shipment)
                
                print("Measuring Bullwhip Effect...")
                print("="*60 + "\n")
                
                # Overall bullwhip ratio (monthly aggregation)
                result = measure_bullwhip_effect(
                    df_shipment,
                    date_col='Week Beginning',
                    demand_col='Barrels',
                    shipments_col='Barrels',  # In this case, shipments ARE barrels
                    freq='M'
                )
                
                print(f"Overall Bullwhip Ratio: {result.bullwhip_ratio:.4f}")
                print(f"Var(Shipments): {result.var_shipments:.2f}")
                print(f"Var(Demand): {result.var_demand:.2f}")
                print(f"Periods analyzed: {result.n_periods_used}\n")
                
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()

