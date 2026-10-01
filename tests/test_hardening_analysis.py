import numpy as np
import pandas as pd
from src.hardening_analysis import compute_work_hardening

def test_work_hardening_synthetic():
    # Generate synthetic data: σ = 500 * ε^0.2
    strain = np.linspace(0.01, 0.10, 50)
    stress = 500 * (strain ** 0.2)
    
    df = pd.DataFrame({'Strain': strain, 'stress_MPa': stress})
    
    # Mock props (yield at 0.01, UTS at 0.10)
    props = {'yield_strain': 0.01, 'uts_strain': 0.10}
    
    result = compute_work_hardening(df, props)
    
    # Check n and K within tolerance
    assert abs(result['n'] - 0.2) < 0.01
    assert abs(result['K_MPa'] - 500) < 1.0
    assert result['R2'] > 0.99