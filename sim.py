import numpy as np
import pandas as pd
from models import IPOLotteryModel

class MonteCarloEngine:
    def __init__(self, data_path="nepse_ipo_model.csv", raw_data_path="nepse_ipo_raw.csv"):
        self.df_model = pd.read_csv(data_path)
        self.df_raw = pd.read_csv(raw_data_path)
        
        # Calculate Q scores based on raw fundamentals
        self.q_scores = IPOLotteryModel.compute_prestige_score(
            self.df_raw['net_worth_per_share'].values, 
            self.df_raw['eps'].values
        )
        self.df_model['q_score'] = self.q_scores
        
        # Simulation Parameters
        self.N_sim = 10000        # Number of Monte Carlo iterations
        self.M = 20               # IPOs per year
        self.K = 1000             # Capital per application
        self.c_asba = 15          # ASBA fee
        self.c_annual = 150       # Annual demat fee
        self.r = 0.06             # Risk-free rate
        self.tau = 0.5            # Prestige Score Threshold (Quality filter)
        
        # Empirical Noise constraints (Eq 5)
        self.sigma_R = 0.2        # 20% volatility noise on listing returns
        self.sigma_A = 200000     # 200k applicant volatility

    def run_simulation(self, num_accounts=1):
        print(f"Running Monte Carlo Simulation (N={self.N_sim}) for n={num_accounts} accounts...")
        
        # Store portfolio returns for each simulation run
        returns_naive = np.zeros(self.N_sim)
        returns_filtered = np.zeros(self.N_sim)
        
        # Empirical Bootstrap: randomly draw M IPO indices (with replacement) N_sim times
        # Shape: (10000, 20)
        np.random.seed(42) # For reproducibility
        pool_size = len(self.df_model)
        draws = np.random.choice(pool_size, size=(self.N_sim, self.M), replace=True)
        
        # Extract base parameters according to the random draws
        base_L = self.df_model['winning_lots'].values[draws]
        base_A = self.df_raw['valid_applications'].values[draws]
        base_R = self.df_model['listing_return'].values[draws]
        base_Q = self.df_model['q_score'].values[draws]
        base_t = self.df_model['capital_lock_days'].values[draws]
        
        # Apply stochastic noise to empirical data (Eq 5)
        noise_A = np.random.normal(0, self.sigma_A, size=(self.N_sim, self.M))
        noise_R = np.random.normal(0, self.sigma_R, size=(self.N_sim, self.M))
        
        sim_A = np.maximum(1, base_A + noise_A) # Demand cannot be negative
        sim_R = np.maximum(-1.0, base_R + noise_R) # Returns bounded at -100% for worst case
        
        # 1. NAIVE STRATEGY (Participate in all M IPOs)
        # Compute dynamic probability given simulated demand
        p_win_naive = IPOLotteryModel.compute_p_win(base_L, sim_A)
        ev_matrix_naive = IPOLotteryModel.compute_ev_multi(
            num_accounts, p_win_naive, self.K, sim_R, self.c_asba, self.c_annual, self.M, self.r, base_t
        )
        # Sum over the M IPOs to get annual return per simulation
        returns_naive = np.sum(ev_matrix_naive, axis=1)
        
        # 2. QUALITY-FILTERED STRATEGY (Participate only if Q_i > tau)
        filter_mask = (base_Q > self.tau)
        
        # Set EV to 0 where the filter mask is False (we don't participate)
        # However, we still pay the annual maintenance fee divided across the year, 
        # so non-participation still costs (c_annual/M) per account.
        annual_maintenance_deduction = -1 * (self.c_annual / self.M) * num_accounts
        
        ev_matrix_filtered = np.where(filter_mask, ev_matrix_naive, annual_maintenance_deduction)
        returns_filtered = np.sum(ev_matrix_filtered, axis=1)
        
        # Compute Metrics
        metrics = {
            'accounts': num_accounts,
            'naive_expected_return': np.mean(returns_naive),
            'naive_sharpe': IPOLotteryModel.compute_sharpe_ratio(returns_naive, self.r * num_accounts * self.K * self.M),
            'naive_var_95': IPOLotteryModel.compute_var(returns_naive, 0.05),
            
            'filtered_expected_return': np.mean(returns_filtered),
            'filtered_sharpe': IPOLotteryModel.compute_sharpe_ratio(returns_filtered, self.r * num_accounts * self.K * self.M),
            'filtered_var_95': IPOLotteryModel.compute_var(returns_filtered, 0.05),
            
            'raw_returns_naive': returns_naive,
            'raw_returns_filtered': returns_filtered
        }
        
        return metrics

if __name__ == "__main__":
    engine = MonteCarloEngine()
    metrics = engine.run_simulation(num_accounts=1)
    
    print("\n--- MONTE CARLO RESULTS (N=10,000, Accounts=1) ---")
    print(f"Naive Strategy:")
    print(f"  Expected Return: NPR {metrics['naive_expected_return']:,.2f}")
    print(f"  Sharpe Ratio:    {metrics['naive_sharpe']:.4f}")
    print(f"  VaR (95%):       NPR {metrics['naive_var_95']:,.2f}")
    
    print(f"\nQuality-Filtered Strategy (tau=0.5):")
    print(f"  Expected Return: NPR {metrics['filtered_expected_return']:,.2f}")
    print(f"  Sharpe Ratio:    {metrics['filtered_sharpe']:.4f}")
    print(f"  VaR (95%):       NPR {metrics['filtered_var_95']:,.2f}")
