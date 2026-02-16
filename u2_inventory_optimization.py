# u2_inventory_optimization.py - UNIT 2 ASSIGNMENT
# This script calculates optimal inventory levels and costs for Cosmo's supply chain.

import pandas as pd
import numpy as np
from scipy.stats import norm
import os
from pathlib import Path

# --- U2: Helper function to load Cosmos data (using ingestion.py principles) ---
def load_cosmos_data(file_name: str = 'bana6420_u2_assignment-cosmos-data.xlsx', sheet_name: str = 'Data') -> pd.DataFrame:
    """Loads the Cosmos Excel data from the data directory."""
    data_dir = Path(__file__).parent / "data"
    file_path = data_dir / file_name
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        return df
    except FileNotFoundError:
        print(f"Error: Data file not found at {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading Cosmos data: {e}")
        return pd.DataFrame()

# --- U2: Parameters from Assignment Requirements ---
# Daily demand: (mean, std_dev)
DEMAND_ALBANY = {'mean': 120, 'std': 60}
DEMAND_BROOKLYN_DC = {'mean': 180, 'std': 80}
DEMAND_SYRACUSE = {'mean': 80, 'std': 60}

# Lead time (RDC to DCs): (mean_days, std_dev_days)
LT_ALBANY_DC = {'mean': 10, 'std': 2}
LT_BROOKLYN_DC = {'mean': 2, 'std': 0}
LT_SYRACUSE_DC = {'mean': 10, 'std': 3}

# RDC parameters (from Plant to RDC)
LT_RDC_FROM_PLANT = {'mean': 10, 'std': 2}
RDC_UNIT_COST = 800
DC_UNIT_COST = 850
ANNUAL_HOLDING_RATE = 0.25 # 25%

# Transportation costs
TP_PLANT_TO_RDC = 3.00
TP_RDC_TO_ALBANY = 2.00
TP_RDC_TO_BROOKLYN = 0.25
TP_RDC_TO_SYRACUSE = 2.25

# Service level target for all locations
SERVICE_LEVEL_TARGET = 0.98
Z_SCORE_98 = norm.ppf(SERVICE_LEVEL_TARGET) # Z-score for 98% service level

# Reorder period (weekly) for all locations
REORDER_PERIOD = 7 # days

# --- U2: Core Inventory Calculation Functions ---
def calculate_sigma_R_plus_L(daily_demand_std: float, lead_time_mean: float, lead_time_std: float, reorder_period: float, daily_demand_mean: float) -> float:
    """
    Calculates the demand standard deviation over the risk exposure period (R+L).
    Formula: sqrt(s^2 * lambda^2 + (R + L) * sigma^2)
    """
    # Term 1: Lead time variability component
    term1 = (lead_time_std ** 2) * (daily_demand_mean ** 2)
    # Term 2: Demand variability component
    term2 = (reorder_period + lead_time_mean) * (daily_demand_std ** 2)
    
    return np.sqrt(term1 + term2)

def calculate_safety_stock(z_score: float, sigma_R_plus_L: float) -> float:
    """Calculates safety stock."""
    return z_score * sigma_R_plus_L

def calculate_base_stock_level(daily_demand_mean: float, reorder_period: float, lead_time_mean: float, safety_stock: float) -> float:
    """
    Calculates the optimal base stock level.
    Formula: lambda * (R + L) + Safety Stock
    """
    return daily_demand_mean * (reorder_period + lead_time_mean) + safety_stock

def calculate_cycle_stock(daily_demand_mean: float, reorder_period: float) -> float:
    """Calculates cycle stock (average inventory during reorder period)."""
    return 0.5 * daily_demand_mean * reorder_period

def calculate_pipeline_stock(daily_demand_mean: float, lead_time_mean: float) -> float:
    """Calculates pipeline stock (inventory in transit)."""
    return daily_demand_mean * lead_time_mean

# --- U2: Part One Calculations (DCs and RDC) ---
def part_one_calculations():
    print("--- U2: Part One - Optimal Inventory Levels ---")
    print(f"Service Level Target: {SERVICE_LEVEL_TARGET*100:.0f}% (Z-score: {Z_SCORE_98:.3f})\n")

    results = {}

    # --- DCs ---
    for dc_name, demand_data, lt_data, tp_cost in zip(
        ['Albany DC', 'Brooklyn DC', 'Syracuse DC'],
        [DEMAND_ALBANY, DEMAND_BROOKLYN_DC, DEMAND_SYRACUSE],
        [LT_ALBANY_DC, LT_BROOKLYN_DC, LT_SYRACUSE_DC],
        [TP_RDC_TO_ALBANY, TP_RDC_TO_BROOKLYN, TP_RDC_TO_SYRACUSE]
    ):
        print(f"** {dc_name} **")
        daily_demand_mean = demand_data['mean']
        daily_demand_std = demand_data['std']
        lead_time_mean = lt_data['mean']
        lead_time_std = lt_data['std']

        sigma_R_plus_L = calculate_sigma_R_plus_L(daily_demand_std, lead_time_mean, lead_time_std, REORDER_PERIOD, daily_demand_mean)
        safety_stock = calculate_safety_stock(Z_SCORE_98, sigma_R_plus_L)
        base_stock = calculate_base_stock_level(daily_demand_mean, REORDER_PERIOD, lead_time_mean, safety_stock)

        results[dc_name] = {
            'daily_demand_mean': daily_demand_mean,
            'daily_demand_std': daily_demand_std,
            'lead_time_mean': lead_time_mean,
            'lead_time_std': lead_time_std,
            'reorder_period': REORDER_PERIOD,
            'sigma_R_plus_L': sigma_R_plus_L,
            'safety_stock': safety_stock,
            'base_stock_level': base_stock,
            'unit_cost': DC_UNIT_COST,
            'holding_cost_rate': ANNUAL_HOLDING_RATE,
            'transport_cost_per_unit': tp_cost
        }
        print(f"  Lambda (Daily Mean): {daily_demand_mean}")
        print(f"  Sigma (Daily Std): {daily_demand_std}")
        print(f"  L (Lead Time Mean): {lead_time_mean} days")
        print(f"  s (Lead Time Std): {lead_time_std} days")
        print(f"  R (Reorder Period): {REORDER_PERIOD} days")
        print(f"  Sigma(R+L): {sigma_R_plus_L:.2f}")
        print(f"  Safety Stock: {safety_stock:.2f} units")
        print(f"  Base Stock Level: {base_stock:.2f} units\n")

    # --- RDC (Brooklyn) ---
    print("** Brooklyn RDC **")
    # Aggregate demand from the three DCs for the RDC
    # Assume demands at DCs are independent for aggregation (from assignment Part Three context)
    total_demand_mean_at_rdc = DEMAND_ALBANY['mean'] + DEMAND_BROOKLYN_DC['mean'] + DEMAND_SYRACUSE['mean']
    # Aggregated standard deviation for independent demands: sqrt(sum of variances)
    total_demand_std_at_rdc = np.sqrt(
        DEMAND_ALBANY['std']**2 + DEMAND_BROOKLYN_DC['std']**2 + DEMAND_SYRACUSE['std']**2
    )

    daily_demand_mean_rdc = total_demand_mean_at_rdc
    daily_demand_std_rdc = total_demand_std_at_rdc
    lead_time_mean_rdc = LT_RDC_FROM_PLANT['mean']
    lead_time_std_rdc = LT_RDC_FROM_PLANT['std']
    
    sigma_R_plus_L_rdc = calculate_sigma_R_plus_L(daily_demand_std_rdc, lead_time_mean_rdc, lead_time_std_rdc, REORDER_PERIOD, daily_demand_mean_rdc)
    safety_stock_rdc = calculate_safety_stock(Z_SCORE_98, sigma_R_plus_L_rdc)
    base_stock_rdc = calculate_base_stock_level(daily_demand_mean_rdc, REORDER_PERIOD, lead_time_mean_rdc, safety_stock_rdc)

    results['Brooklyn RDC'] = {
        'daily_demand_mean': daily_demand_mean_rdc,
        'daily_demand_std': daily_demand_std_rdc,
        'lead_time_mean': lead_time_mean_rdc,
        'lead_time_std': lead_time_std_rdc,
        'reorder_period': REORDER_PERIOD,
        'sigma_R_plus_L': sigma_R_plus_L_rdc,
        'safety_stock': safety_stock_rdc,
        'base_stock_level': base_stock_rdc,
        'unit_cost': RDC_UNIT_COST,
        'holding_cost_rate': ANNUAL_HOLDING_RATE,
        'transport_cost_per_unit': TP_PLANT_TO_RDC
    }
    print(f"  Aggregated Lambda (Daily Mean): {daily_demand_mean_rdc}")
    print(f"  Aggregated Sigma (Daily Std): {daily_demand_std_rdc:.2f}")
    print(f"  L (Lead Time Mean): {lead_time_mean_rdc} days")
    print(f"  s (Lead Time Std): {lead_time_std_rdc} days")
    print(f"  R (Reorder Period): {REORDER_PERIOD} days")
    print(f"  Sigma(R+L): {sigma_R_plus_L_rdc:.2f}")
    print(f"  Safety Stock: {safety_stock_rdc:.2f} units")
    print(f"  Base Stock Level: {base_stock_rdc:.2f} units\n")
    
    return results

if __name__ == "__main__":
    # Load the Cosmos data (though not directly used for these calculations yet, good to have)
    cosmos_df = load_cosmos_data()
    if not cosmos_df.empty:
        print("Cosmos data loaded successfully.")
    else:
        print("Failed to load Cosmos data.")

    # Run Part One calculations
    part_one_results = part_one_calculations()

    # --- U2: Part Two - Inventory Cost Performance for DCs ---
    print("\n--- U2: Part Two - Inventory Components & Cost Performance (DCs) ---")
    annual_days = 365 # Assuming 365 operating days for annual costs

    for dc_name, data in part_one_results.items():
        if 'DC' in dc_name: # Only for DCs initially as per assignment structure
            print(f"\n** {dc_name} **")
            daily_demand_mean = data['daily_demand_mean']
            reorder_period = data['reorder_period']
            lead_time_mean = data['lead_time_mean']
            safety_stock = data['safety_stock']
            unit_cost = data['unit_cost']
            holding_cost_rate = data['holding_cost_rate']
            transport_cost_per_unit = data['transport_cost_per_unit']

            cycle_stock = calculate_cycle_stock(daily_demand_mean, reorder_period)
            pipeline_stock = calculate_pipeline_stock(daily_demand_mean, lead_time_mean)
            
            total_inventory_units = cycle_stock + pipeline_stock + safety_stock

            # Annual Holding Cost
            # Unit holding cost per year = unit_cost * annual_holding_cost_rate
            # Total annual holding cost = (unit_cost * annual_holding_cost_rate) * total_inventory_units
            annual_holding_cost = unit_cost * holding_cost_rate * total_inventory_units

            # Annual Transportation Cost
            # Annual demand = daily_demand_mean * annual_days
            # Total annual transportation cost = transport_cost_per_unit * annual_demand
            annual_transport_cost = transport_cost_per_unit * daily_demand_mean * annual_days

            total_annual_cost = annual_holding_cost + annual_transport_cost

            print(f"  Cycle Stock: {cycle_stock:.2f} units")
            print(f"  Pipeline Stock: {pipeline_stock:.2f} units")
            print(f"  Safety Stock: {safety_stock:.2f} units")
            print(f"  Total Inventory (units): {total_inventory_units:.2f}")
            print(f"  Annual Holding Cost: ${annual_holding_cost:.2f}")
            print(f"  Annual Transportation Cost: ${annual_transport_cost:.2f}")
            print(f"  Total Annual Cost: ${total_annual_cost:.2f}")
            
            # Store in results for later use
            part_one_results[dc_name].update({
                'cycle_stock': cycle_stock,
                'pipeline_stock': pipeline_stock,
                'total_inventory_units': total_inventory_units,
                'annual_holding_cost': annual_holding_cost,
                'annual_transport_cost': annual_transport_cost,
                'total_annual_cost': total_annual_cost
            })

    # Total cost of the three DCs (including all pipeline stock)
    total_cost_three_dcs = sum(part_one_results[dc]['total_annual_cost'] for dc in ['Albany DC', 'Brooklyn DC', 'Syracuse DC'])
    print(f"\nTotal Annual Cost for the Three DCs: ${total_cost_three_dcs:.2f}")


    # --- U2: Part Three - Inventory & Cost Performance for RDC and Total Supply Chain ---
    print("\n--- U2: Part Three - RDC Inventory Components & Total Supply Chain Cost ---")
    rdc_data = part_one_results['Brooklyn RDC']

    # Cycle Stock, Pipeline Stock, Safety Stock for RDC
    rdc_daily_demand_mean = rdc_data['daily_demand_mean']
    rdc_reorder_period = rdc_data['reorder_period']
    rdc_lead_time_mean = rdc_data['lead_time_mean']
    rdc_safety_stock = rdc_data['safety_stock']
    rdc_unit_cost = rdc_data['unit_cost']
    rdc_holding_cost_rate = rdc_data['holding_cost_rate']
    rdc_transport_cost_per_unit = rdc_data['transport_cost_per_unit']

    rdc_cycle_stock = calculate_cycle_stock(rdc_daily_demand_mean, rdc_reorder_period)
    rdc_pipeline_stock = calculate_pipeline_stock(rdc_daily_demand_mean, rdc_lead_time_mean)
    
    rdc_total_inventory_units = rdc_cycle_stock + rdc_pipeline_stock + rdc_safety_stock

    rdc_annual_holding_cost = rdc_unit_cost * rdc_holding_cost_rate * rdc_total_inventory_units
    rdc_annual_transport_cost = rdc_transport_cost_per_unit * rdc_daily_demand_mean * annual_days
    rdc_total_annual_cost = rdc_annual_holding_cost + rdc_annual_transport_cost

    print("\n** Brooklyn RDC **")
    print(f"  Cycle Stock: {rdc_cycle_stock:.2f} units")
    print(f"  Pipeline Stock: {rdc_pipeline_stock:.2f} units")
    print(f"  Safety Stock: {rdc_safety_stock:.2f} units")
    print(f"  Total Inventory (units): {rdc_total_inventory_units:.2f}")
    print(f"  Annual Holding Cost: ${rdc_annual_holding_cost:.2f}")
    print(f"  Annual Transportation Cost: ${rdc_annual_transport_cost:.2f}")
    print(f"  Total Annual Cost: ${rdc_total_annual_cost:.2f}")

    part_one_results['Brooklyn RDC'].update({
        'cycle_stock': rdc_cycle_stock,
        'pipeline_stock': rdc_pipeline_stock,
        'total_inventory_units': rdc_total_inventory_units,
        'annual_holding_cost': rdc_annual_holding_cost,
        'annual_transport_cost': rdc_annual_transport_cost,
        'total_annual_cost': rdc_total_annual_cost
    })

    total_supply_chain_cost = total_cost_three_dcs + rdc_total_annual_cost
    print(f"\nTotal Annual Supply Chain Cost (RDC + Three DCs): ${total_supply_chain_cost:.2f}")


    # --- U2: Part Four - Improving Supply Chain Performance ---
    print("\n--- U2: Part Four - Improving Supply Chain Performance by Reconfiguration ---")

    # Scenario 1: 10% reduction in demand uncertainty (daily demand std)
    print("\n** Scenario 1: 10% Reduction in Demand Uncertainty **")
    total_safety_stock_cost_scenario1 = 0
    print("  DCs:")
    for dc_name, data in part_one_results.items():
        if 'DC' in dc_name:
            new_daily_demand_std = data['daily_demand_std'] * 0.9 # 10% reduction
            new_sigma_R_plus_L = calculate_sigma_R_plus_L(
                new_daily_demand_std, data['lead_time_mean'], data['lead_time_std'], 
                data['reorder_period'], data['daily_demand_mean']
            )
            new_safety_stock = calculate_safety_stock(Z_SCORE_98, new_sigma_R_plus_L)
            safety_stock_holding_cost = data['unit_cost'] * data['holding_cost_rate'] * new_safety_stock
            total_safety_stock_cost_scenario1 += safety_stock_holding_cost
            print(f"    {dc_name} new Safety Stock: {new_safety_stock:.2f}, Cost: ${safety_stock_holding_cost:.2f}")

    # RDC for Scenario 1
    rdc_data_orig = part_one_results['Brooklyn RDC']
    new_daily_demand_std_rdc = rdc_data_orig['daily_demand_std'] * 0.9 # 10% reduction
    new_sigma_R_plus_L_rdc = calculate_sigma_R_plus_L(
        new_daily_demand_std_rdc, rdc_data_orig['lead_time_mean'], rdc_data_orig['lead_time_std'], 
        rdc_data_orig['reorder_period'], rdc_data_orig['daily_demand_mean']
    )
    new_safety_stock_rdc = calculate_safety_stock(Z_SCORE_98, new_sigma_R_plus_L_rdc)
    safety_stock_holding_cost_rdc = rdc_data_orig['unit_cost'] * rdc_data_orig['holding_cost_rate'] * new_safety_stock_rdc
    total_safety_stock_cost_scenario1 += safety_stock_holding_cost_rdc
    print(f"  Brooklyn RDC new Safety Stock: {new_safety_stock_rdc:.2f}, Cost: ${safety_stock_holding_cost_rdc:.2f}")
    print(f"  Total Annual Safety Stock Holding Cost (Demand Uncertainty Reduction): ${total_safety_stock_cost_scenario1:.2f}")


    # Scenario 2: 10% reduction in lead time uncertainty (lead time std)
    print("\n** Scenario 2: 10% Reduction in Lead Time Uncertainty **")
    total_safety_stock_cost_scenario2 = 0
    print("  DCs:")
    for dc_name, data in part_one_results.items():
        if 'DC' in dc_name:
            new_lead_time_std = data['lead_time_std'] * 0.9 # 10% reduction
            new_sigma_R_plus_L = calculate_sigma_R_plus_L(
                data['daily_demand_std'], data['lead_time_mean'], new_lead_time_std, 
                data['reorder_period'], data['daily_demand_mean']
            )
            new_safety_stock = calculate_safety_stock(Z_SCORE_98, new_sigma_R_plus_L)
            safety_stock_holding_cost = data['unit_cost'] * data['holding_cost_rate'] * new_safety_stock
            total_safety_stock_cost_scenario2 += safety_stock_holding_cost
            print(f"    {dc_name} new Safety Stock: {new_safety_stock:.2f}, Cost: ${safety_stock_holding_cost:.2f}")
    
    # RDC for Scenario 2
    rdc_data_orig = part_one_results['Brooklyn RDC']
    new_lead_time_std_rdc = rdc_data_orig['lead_time_std'] * 0.9 # 10% reduction
    new_sigma_R_plus_L_rdc = calculate_sigma_R_plus_L(
        rdc_data_orig['daily_demand_std'], rdc_data_orig['lead_time_mean'], new_lead_time_std_rdc, 
        rdc_data_orig['reorder_period'], rdc_data_orig['daily_demand_mean']
    )
    new_safety_stock_rdc = calculate_safety_stock(Z_SCORE_98, new_sigma_R_plus_L_rdc)
    safety_stock_holding_cost_rdc = rdc_data_orig['unit_cost'] * rdc_data_orig['holding_cost_rate'] * new_safety_stock_rdc
    total_safety_stock_cost_scenario2 += safety_stock_holding_cost_rdc
    print(f"  Brooklyn RDC new Safety Stock: {new_safety_stock_rdc:.2f}, Cost: ${safety_stock_holding_cost_rdc:.2f}")
    print(f"  Total Annual Safety Stock Holding Cost (Lead Time Uncertainty Reduction): ${total_safety_stock_cost_scenario2:.2f}")

    if total_safety_stock_cost_scenario1 < total_safety_stock_cost_scenario2:
        print("\nConclusion: 10% Demand Uncertainty Reduction is better.")
    else:
        print("\nConclusion: 10% Lead Time Uncertainty Reduction is better.")


    # --- U2: Part Four - Premium Transportation Provider ---
    print("\n** Scenario 3: Premium Transportation Provider **")
    # New rates and lead times from assignment text
    NEW_TP_PLANT_TO_RDC = 3.50
    NEW_TP_RDC_TO_ALBANY = 2.25
    NEW_TP_RDC_TO_BROOKLYN = 0.28
    NEW_TP_RDC_TO_SYRACUSE = 2.55

    NEW_LT_PLANT_TO_RDC = {'mean': 7, 'std': 1}
    NEW_LT_ALBANY_DC = {'mean': 7, 'std': 1}
    NEW_LT_BROOKLYN_DC = {'mean': 1, 'std': 0}
    NEW_LT_SYRACUSE_DC = {'mean': 7, 'std': 1}

    premium_results = {}
    total_premium_supply_chain_cost = 0

    # DCs with premium transport
    for dc_name, demand_data, new_lt_data, new_tp_cost in zip(
        ['Albany DC', 'Brooklyn DC', 'Syracuse DC'],
        [DEMAND_ALBANY, DEMAND_BROOKLYN_DC, DEMAND_SYRACUSE],
        [NEW_LT_ALBANY_DC, NEW_LT_BROOKLYN_DC, NEW_LT_SYRACUSE_DC],
        [NEW_TP_RDC_TO_ALBANY, NEW_TP_RDC_TO_BROOKLYN, NEW_TP_RDC_TO_SYRACUSE]
    ):
        print(f"\n  ** {dc_name} (Premium Transport) **")
        daily_demand_mean = demand_data['mean']
        daily_demand_std = demand_data['std']
        lead_time_mean = new_lt_data['mean']
        lead_time_std = new_lt_data['std']

        sigma_R_plus_L = calculate_sigma_R_plus_L(daily_demand_std, lead_time_mean, lead_time_std, REORDER_PERIOD, daily_demand_mean)
        safety_stock = calculate_safety_stock(Z_SCORE_98, sigma_R_plus_L)
        base_stock = calculate_base_stock_level(daily_demand_mean, REORDER_PERIOD, lead_time_mean, safety_stock)
        
        cycle_stock = calculate_cycle_stock(daily_demand_mean, REORDER_PERIOD)
        pipeline_stock = calculate_pipeline_stock(daily_demand_mean, lead_time_mean)
        total_inventory_units = cycle_stock + pipeline_stock + safety_stock

        annual_holding_cost = DC_UNIT_COST * ANNUAL_HOLDING_RATE * total_inventory_units
        annual_transport_cost = new_tp_cost * daily_demand_mean * annual_days
        total_annual_cost = annual_holding_cost + annual_transport_cost

        premium_results[dc_name] = {
            'annual_holding_cost': annual_holding_cost,
            'annual_transport_cost': annual_transport_cost,
            'total_annual_cost': total_annual_cost
        }
        total_premium_supply_chain_cost += total_annual_cost
        
        print(f"    Safety Stock: {safety_stock:.2f} units")
        print(f"    Annual Holding Cost: ${annual_holding_cost:.2f}")
        print(f"    Annual Transportation Cost: ${annual_transport_cost:.2f}")
        print(f"    Total Annual Cost: ${total_annual_cost:.2f}")

    # RDC with premium transport
    print(f"\n  ** Brooklyn RDC (Premium Transport) **")
    rdc_data_orig = part_one_results['Brooklyn RDC']
    rdc_daily_demand_mean = rdc_data_orig['daily_demand_mean']
    rdc_daily_demand_std = rdc_data_orig['daily_demand_std']
    
    rdc_lead_time_mean = NEW_LT_PLANT_TO_RDC['mean']
    rdc_lead_time_std = NEW_LT_PLANT_TO_RDC['std']

    sigma_R_plus_L_rdc = calculate_sigma_R_plus_L(rdc_daily_demand_std, rdc_lead_time_mean, rdc_lead_time_std, REORDER_PERIOD, rdc_daily_demand_mean)
    safety_stock_rdc = calculate_safety_stock(Z_SCORE_98, sigma_R_plus_L_rdc)
    base_stock_rdc = calculate_base_stock_level(rdc_daily_demand_mean, REORDER_PERIOD, rdc_lead_time_mean, safety_stock_rdc)

    rdc_cycle_stock = calculate_cycle_stock(rdc_daily_demand_mean, REORDER_PERIOD)
    rdc_pipeline_stock = calculate_pipeline_stock(rdc_daily_demand_mean, rdc_lead_time_mean)
    rdc_total_inventory_units = rdc_cycle_stock + rdc_pipeline_stock + rdc_safety_stock

    rdc_annual_holding_cost = RDC_UNIT_COST * ANNUAL_HOLDING_RATE * rdc_total_inventory_units
    rdc_annual_transport_cost = NEW_TP_PLANT_TO_RDC * rdc_daily_demand_mean * annual_days
    rdc_total_annual_cost = rdc_annual_holding_cost + rdc_annual_transport_cost

    premium_results['Brooklyn RDC'] = {
        'annual_holding_cost': rdc_annual_holding_cost,
        'annual_transport_cost': rdc_annual_transport_cost,
        'total_annual_cost': rdc_total_annual_cost
    }
    total_premium_supply_chain_cost += rdc_total_annual_cost

    print(f"    Safety Stock: {safety_stock_rdc:.2f} units")
    print(f"    Annual Holding Cost: ${rdc_annual_holding_cost:.2f}")
    print(f"    Annual Transportation Cost: ${rdc_annual_transport_cost:.2f}")
    print(f"    Total Annual Cost: ${rdc_total_annual_cost:.2f}")
    print(f"\n  Total Annual Supply Chain Cost (Premium Transport): ${total_premium_supply_chain_cost:.2f}")

    print(f"\n  Base Case Total Annual Supply Chain Cost: ${total_supply_chain_cost:.2f}")
    print("\nRecommendation for switching to Premium Transportation:")
    for loc, premium_data in premium_results.items():
        base_cost = part_one_results[loc]['total_annual_cost']
        if premium_data['total_annual_cost'] < base_cost:
            print(f"  - Recommend switching {loc}: Cost reduces from ${base_cost:.2f} to ${premium_data['total_annual_cost']:.2f}")
        else:
            print(f"  - Do NOT recommend switching {loc}: Cost increases from ${base_cost:.2f} to ${premium_data['total_annual_cost']:.2f}")
    
    # --- U2: Part Four - Order Daily from RDC to DCs ---
    print("\n** Scenario 4: DCs Order Daily from RDC **")
    # Recalculate for DCs with R = 1 day, all other parameters as original base case
    daily_order_results = {}
    total_daily_order_supply_chain_cost = 0

    print("  DCs with daily ordering:")
    for dc_name, demand_data, lt_data, tp_cost in zip(
        ['Albany DC', 'Brooklyn DC', 'Syracuse DC'],
        [DEMAND_ALBANY, DEMAND_BROOKLYN_DC, DEMAND_SYRACUSE],
        [LT_ALBANY_DC, LT_BROOKLYN_DC, LT_SYRACUSE_DC],
        [TP_RDC_TO_ALBANY, TP_RDC_TO_BROOKLYN, TP_RDC_TO_SYRACUSE]
    ):
        print(f"\n    ** {dc_name} (Daily Ordering) **")
        daily_demand_mean = demand_data['mean']
        daily_demand_std = demand_data['std']
        lead_time_mean = lt_data['mean']
        lead_time_std = lt_data['std']
        new_reorder_period = 1 # daily ordering

        sigma_R_plus_L = calculate_sigma_R_plus_L(daily_demand_std, lead_time_mean, lead_time_std, new_reorder_period, daily_demand_mean)
        safety_stock = calculate_safety_stock(Z_SCORE_98, sigma_R_plus_L)
        base_stock = calculate_base_stock_level(daily_demand_mean, new_reorder_period, lead_time_mean, safety_stock)
        
        cycle_stock = calculate_cycle_stock(daily_demand_mean, new_reorder_period)
        pipeline_stock = calculate_pipeline_stock(daily_demand_mean, lead_time_mean)
        total_inventory_units = cycle_stock + pipeline_stock + safety_stock

        annual_holding_cost = DC_UNIT_COST * ANNUAL_HOLDING_RATE * total_inventory_units
        annual_transport_cost = tp_cost * daily_demand_mean * annual_days
        total_annual_cost = annual_holding_cost + annual_transport_cost

        daily_order_results[dc_name] = {
            'annual_holding_cost': annual_holding_cost,
            'annual_transport_cost': annual_transport_cost,
            'total_annual_cost': total_annual_cost
        }
        total_daily_order_supply_chain_cost += total_annual_cost
        
        print(f"      Safety Stock: {safety_stock:.2f} units")
        print(f"      Cycle Stock: {cycle_stock:.2f} units")
        print(f"      Pipeline Stock: {pipeline_stock:.2f} units")
        print(f"      Total Inventory (units): {total_inventory_units:.2f}")
        print(f"      Annual Holding Cost: ${annual_holding_cost:.2f}")
        print(f"      Annual Transportation Cost: ${annual_transport_cost:.2f}")
        print(f"      Total Annual Cost: ${total_annual_cost:.2f}")

    # Add RDC cost (which remains unchanged from base case as it still orders weekly from plant)
    total_daily_order_supply_chain_cost += part_one_results['Brooklyn RDC']['total_annual_cost']
    print(f"\n  Total Annual Supply Chain Cost (DCs Order Daily): ${total_daily_order_supply_chain_cost:.2f}")

    benefit = total_supply_chain_cost - total_daily_order_supply_chain_cost
    print(f"  Additional Benefit (vs. Base Case): ${benefit:.2f}")
