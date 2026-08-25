import numpy as np
import pandas as pd

class IPOLotteryModel:
    """
    Core mathematical engine for Nepal's "10-Kitta" IPO Lottery System.
    Strictly implements equations from the project proposal PDF.
    """

    @staticmethod
    def compute_p_win(L, A):
        """
        Eq (1): Single-Account Win Probability
        P_win = min(1, L / A)
        L = total winning lots (S/10)
        A = total aggregate demand (valid applications)
        """
        # Supports scalar and vectorized numpy/pandas inputs
        p_win = np.minimum(1.0, L / np.maximum(A, 1)) # avoid division by zero
        return p_win

    @staticmethod
    def compute_ev_single(p_win, K, r_listing, c_asba, c_annual, M, r, t):
        """
        Eq (2): Single-Account Expected Value
        EV_single = P_win * (K * R_listing) - C_ASBA - (C_annual / M) - (K * r * t / 365)
        """
        capital_gain = K * r_listing
        maintenance_cost = c_annual / M
        opportunity_cost = K * r * (t / 365.0)
        
        ev_single = (p_win * capital_gain) - c_asba - maintenance_cost - opportunity_cost
        return ev_single

    @staticmethod
    def compute_ev_multi(n, p_win, K, r_listing, c_asba, c_annual, M, r, t):
        """
        Eq (3): Multi-Account Portfolio Dynamics (Binomial Draw)
        Assuming n << A, EV(n) = n * EV_single
        """
        ev_single = IPOLotteryModel.compute_ev_single(p_win, K, r_listing, c_asba, c_annual, M, r, t)
        return n * ev_single

    @staticmethod
    def compute_critical_demand(L, K, r_listing, c_asba, c_annual, M, r, t):
        """
        Eq (4): Game-Theoretic Nash Equilibrium (A*)
        A* = [L * (K * R_listing)] / [C_ASBA + (C_annual / M) + (K * r * t / 365)]
        
        This is the critical market demand threshold past which 
        retail lottery participation becomes unviable (EV_single <= 0).
        """
        capital_gain = K * r_listing
        maintenance_cost = c_annual / M
        opportunity_cost = K * r * (t / 365.0)
        
        frictions = c_asba + maintenance_cost + opportunity_cost
        
        # If frictions are higher than maximum possible capital gain, A* is effectively zero (never viable)
        # Using numpy.where to handle vectorization safely
        a_star = np.where(
            capital_gain > 0, 
            (L * capital_gain) / frictions, 
            0.0
        )
        return a_star

    @staticmethod
    def compute_prestige_score(net_worth_series, eps_series):
        """
        Eq (5): Issuer Prestige Factor (Q)
        Constructs Q_i in [0, 1] using min-max scaling of fundamentals.
        Uses an equally weighted composite of normalized Net Worth and EPS.
        """
        nw_min, nw_max = np.min(net_worth_series), np.max(net_worth_series)
        eps_min, eps_max = np.min(eps_series), np.max(eps_series)
        
        # Avoid division by zero if all values are identical
        if nw_max == nw_min: nw_norm = np.ones_like(net_worth_series) * 0.5
        else: nw_norm = (net_worth_series - nw_min) / (nw_max - nw_min)
            
        if eps_max == eps_min: eps_norm = np.ones_like(eps_series) * 0.5
        else: eps_norm = (eps_series - eps_min) / (eps_max - eps_min)
        
        # Q_i in [0, 1]
        q_score = (0.5 * nw_norm) + (0.5 * eps_norm)
        return q_score
        
    @staticmethod
    def compute_sharpe_ratio(returns, risk_free_rate=0.06):
        """
        Eq (6): Sharpe Ratio = (E[R_p] - R_f) / sigma_p
        """
        expected_return = np.mean(returns)
        std_dev = np.std(returns)
        if std_dev == 0:
            return 0.0
        return (expected_return - risk_free_rate) / std_dev
        
    @staticmethod
    def compute_var(returns, alpha=0.05):
        """
        Eq (6): VaR_0.95 = inf{x in R : P(R_p <= x) >= 0.05}
        Computes 95% Value at Risk (empirical percentile).
        """
        return np.percentile(returns, alpha * 100)
