import urllib.parse
import webbrowser
import pandas as pd
import os

def generate_verification_links(symbol, company_name):
    print(f"\n========================================================")
    print(f" Verification Links for: {company_name} ({symbol})")
    print(f"========================================================")
    
    # 1. Fundamentals and Company Profile (MeroLagani)
    merolagani_url = f"https://merolagani.com/CompanyDetail.aspx?symbol={symbol}"
    print(f"\n[1] Fundamentals & Profile (MeroLagani):")
    print(f"    URL: {merolagani_url}")
    print(f"    Check: Net Worth Per Share, EPS")
    
    # 2. Application Counts & Allotment Data (Google Search restricted to ShareSansar)
    query = urllib.parse.quote_plus(f"{company_name} IPO allotment sharesansar")
    google_url = f"https://www.google.com/search?q={query}"
    print(f"\n[2] Application Counts (ShareSansar via Google):")
    print(f"    URL: {google_url}")
    print(f"    Check: Valid Applications, Total Applied Shares")
    
    # 3. First Day Trading Prices (NepseAlpha Chart)
    nepse_alpha_url = f"https://nepsealpha.com/trading/chart?symbol={symbol}"
    print(f"\n[3] First Day Trading Price (NepseAlpha Chart):")
    print(f"    URL: {nepse_alpha_url}")
    print(f"    Check: First Trading Day Close Price")

    return merolagani_url, google_url, nepse_alpha_url

def main():
    csv_file = "nepse_ipo_raw.csv"
    df = None
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        
    print("Welcome to the NEPSE IPO Verification Helper!")
    while True:
        user_input = input("\nEnter a Symbol (e.g., SARBTM) or type 'exit' to quit: ").strip().upper()
        if user_input == 'EXIT':
            break
            
        company_name = user_input
        # If we have the CSV, try to look up the full company name
        if df is not None:
            match = df[df['symbol'] == user_input]
            if not match.empty:
                company_name = match.iloc[0]['company_name']
                
        merolagani, google, nepsealpha = generate_verification_links(user_input, company_name)
        
        # Ask if the user wants to open them in the browser automatically
        open_browser = input("\nDo you want to open these links in your browser? (y/n): ").strip().lower()
        if open_browser == 'y':
            webbrowser.open(merolagani)
            webbrowser.open(google)
            webbrowser.open(nepsealpha)

if __name__ == "__main__":
    main()
