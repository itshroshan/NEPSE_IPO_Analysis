import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sim import MonteCarloEngine

def generate_plots():
    print("Generating Simulation Visualizations...")
    
    # Run the engine
    engine = MonteCarloEngine()
    metrics = engine.run_simulation(num_accounts=1)
    
    returns_naive = metrics['raw_returns_naive']
    returns_filtered = metrics['raw_returns_filtered']
    
    # Plot 1: Histogram of Annual Returns (N=10,000)
    plt.figure(figsize=(10, 6))
    sns.histplot(returns_naive, color='red', alpha=0.5, label='Unfiltered Naive', bins=50, kde=True)
    sns.histplot(returns_filtered, color='green', alpha=0.5, label='Quality-Filtered (Q > 0.5)', bins=50, kde=True)
    
    # Mark VaR lines
    plt.axvline(metrics['naive_var_95'], color='red', linestyle='--', label=f"Naive 95% VaR: NPR {metrics['naive_var_95']:,.0f}")
    plt.axvline(metrics['filtered_var_95'], color='green', linestyle='--', label=f"Filtered 95% VaR: NPR {metrics['filtered_var_95']:,.0f}")
    
    plt.title("Monte Carlo Bootstrap: Distribution of Annual Portfolio Returns (n=1)\n10,000 Iterations")
    plt.xlabel("Annual Net Return (NPR)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig("return_distribution.png", dpi=300)
    print("Saved return_distribution.png")
    
    # Plot 2: Expected Value vs Family Accounts (n)
    accounts = np.arange(1, 11)
    naive_evs = []
    filtered_evs = []
    
    for n in accounts:
        # We can reuse the raw logic for multi-account scaling to save computation time
        # Or just call engine.run_simulation(n)
        metrics_n = engine.run_simulation(num_accounts=n)
        naive_evs.append(metrics_n['naive_expected_return'])
        filtered_evs.append(metrics_n['filtered_expected_return'])
        
    plt.figure(figsize=(8, 6))
    plt.plot(accounts, naive_evs, marker='o', color='red', label='Unfiltered Naive Strategy')
    plt.plot(accounts, filtered_evs, marker='s', color='green', label='Quality-Filtered Strategy')
    
    plt.title("Expected Annual Return vs. Number of Family Accounts (n)")
    plt.xlabel("Number of Accounts (n)")
    plt.ylabel("Expected Net Return (NPR)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("expected_return_scaling.png", dpi=300)
    print("Saved expected_return_scaling.png")

if __name__ == "__main__":
    generate_plots()
