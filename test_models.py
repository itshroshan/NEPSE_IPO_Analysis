import numpy as np
from models import IPOLotteryModel

def test_nash_equilibrium():
    """
    Test that the Nash Equilibrium A* works exactly as mathematically derived.
    If aggregate demand A == A*, then EV_single should be exactly 0.0
    """
    print("Testing Eq(4) Nash Equilibrium Theorem...")
    
    # Dummy simulation parameters
    L = 200000          # 2,000,000 shares / 10
    K = 1000            # Application capital
    r_listing = 2.50    # 250% listing return
    c_asba = 15         # NPR 15 ASBA fee
    c_annual = 150      # NPR 150 annual fee
    M = 20              # 20 IPOs per year
    r = 0.06            # 6% risk-free rate
    t = 15              # 15 days locked capital
    
    # 1. Compute A* (Critical demand threshold)
    a_star = IPOLotteryModel.compute_critical_demand(L, K, r_listing, c_asba, c_annual, M, r, t)
    print(f"Calculated A* (Critical Demand): {a_star:,.2f}")
    
    # 2. Compute P_win exactly at A*
    p_win_at_star = IPOLotteryModel.compute_p_win(L, a_star)
    print(f"Win Probability at A*: {p_win_at_star:.6f}")
    
    # 3. Compute EV_single exactly at A*
    ev_at_star = IPOLotteryModel.compute_ev_single(p_win_at_star, K, r_listing, c_asba, c_annual, M, r, t)
    print(f"EV_single at A*: {ev_at_star:,.6f}")
    
    # Assert mathematically
    assert np.isclose(ev_at_star, 0.0, atol=1e-8), "Nash Equilibrium validation failed!"
    print("\n[SUCCESS] EV_single mathematically proven to be 0 at A* threshold.")

def test_vectorization():
    print("\nTesting NumPy Vectorization capabilities...")
    L_array = np.array([200000, 300000])
    A_array = np.array([1500000, 1500000])
    
    p_win_arr = IPOLotteryModel.compute_p_win(L_array, A_array)
    print(f"Vectorized P_win output: {p_win_arr}")
    assert len(p_win_arr) == 2
    print("[SUCCESS] Vectorization functional.")
    
def test_prestige_score():
    print("\nTesting Prestige Score scaling...")
    nw = np.array([100, 150, 200])
    eps = np.array([5, 10, 15])
    
    q_scores = IPOLotteryModel.compute_prestige_score(nw, eps)
    print(f"Normalized Q_scores: {q_scores}")
    assert q_scores[0] == 0.0 # Min limits
    assert q_scores[2] == 1.0 # Max limits
    assert q_scores[1] == 0.5 # Middle
    print("[SUCCESS] Prestige Score Min-Max functional.")

if __name__ == "__main__":
    test_nash_equilibrium()
    test_vectorization()
    test_prestige_score()
