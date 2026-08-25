import pandas as pd
import numpy as np

def process_data():
    # 1. Load Raw Data
    df_raw = pd.read_csv("nepse_ipo_raw.csv")
    
    # 2. Generate Clean Dataset
    # Normalize dates and ensure data types
    df_clean = df_raw.copy()
    date_cols = ["issue_open_date", "issue_close_date", "allotment_date", "listing_date", "first_trading_date"]
    for col in date_cols:
        df_clean[col] = pd.to_datetime(df_clean[col]).dt.strftime('%Y-%m-%d')
    
    # Clean dataset output
    df_clean.to_csv("nepse_ipo_clean.csv", index=False)
    print("Created nepse_ipo_clean.csv")

    # 3. Generate Model Dataset (Derived variables)
    df_model = df_clean.copy()
    
    # Constants from context.md & PDF
    K = 1000  # Application capital for 10-kitta
    M = 20    # Number of IPOs in the modeled annual horizon
    
    # Derived parameters
    df_model['winning_lots'] = df_model['general_public_shares'] / 10
    
    # Probability of winning
    df_model['p_win'] = df_model.apply(
        lambda row: min(1.0, row['winning_lots'] / row['valid_applications']) if row['valid_applications'] > 0 else 1.0, 
        axis=1
    )
    
    # Oversubscription ratio
    df_model['oversubscription'] = df_model['applied_shares'] / df_model['general_public_shares']
    
    # Listing return
    df_model['listing_return'] = (df_model['first_day_close'] - df_model['issue_price']) / df_model['issue_price']
    
    # Expected gross return
    df_model['expected_gross_return'] = df_model['p_win'] * (K * df_model['listing_return'])
    
    # Opportunity cost
    df_model['opportunity_cost'] = K * df_model['risk_free_rate'] * (df_model['capital_lock_days'] / 365)
    
    # Expected Value (EV_single)
    # EV_single = p_win * (K * listing_return) - C_ASBA - (C_annual / M) - opportunity_cost
    df_model['EV_single'] = (
        (df_model['p_win'] * (K * df_model['listing_return'])) 
        - df_model['casba_fee'] 
        - (df_model['annual_account_cost'] / M) 
        - df_model['opportunity_cost']
    )
    
    # A_star (Critical market demand threshold for equilibrium)
    # A* = [L * (K * R_listing)] / [C_ASBA + (C_annual / M) + (K * r * t / 365)]
    df_model['A_star'] = (df_model['winning_lots'] * (K * df_model['listing_return'])) / (
        df_model['casba_fee'] + (df_model['annual_account_cost'] / M) + df_model['opportunity_cost']
    )
    
    # Generate missing data report
    missing_report = []
    missing_count = df_raw.isnull().sum()
    if missing_count.sum() > 0:
        missing_report.append("Missing fields detected in raw data:")
        missing_report.append(str(missing_count[missing_count > 0]))
    else:
        missing_report.append("No missing fields detected in the prototype dataset.")
        
    with open("missing_data_report.txt", "w") as f:
        f.write("\n".join(missing_report))
    
    # Select specific columns for model.csv to keep it concise and useful for the Monte Carlo step
    model_cols = [
        'ipo_id', 'company_name', 'symbol', 'winning_lots', 'p_win', 'oversubscription',
        'listing_return', 'capital_lock_days', 'opportunity_cost', 'expected_gross_return', 
        'EV_single', 'A_star'
    ]
    df_model[model_cols].to_csv("nepse_ipo_model.csv", index=False)
    print("Created nepse_ipo_model.csv")
    print("Created missing_data_report.txt")

if __name__ == "__main__":
    process_data()
