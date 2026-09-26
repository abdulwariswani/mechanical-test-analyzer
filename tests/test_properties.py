import pytest ,numpy as np , pandas as pd
from src.mechanical_properties import compute_young_modulus, compute_yield_strength, compute_uts, compute_elongation, compute_toughness,compute_properties

# test1: 
def test_young_modulus():
    #  # Create synthetic: stress = 1000 * strain (E = 1000 MPa)
    strain = np.linspace(0,0.01,100)
    stress = (strain *1000)
    slope=compute_young_modulus(strain,stress)
    # 3. Convert MPa to GPa
    E_GPa = slope / 1000.0
    assert E_GPa == pytest.approx(1.0,rel =0.05)

#test2:
def test_young_modulus_insufficient_data():
    # Create only 50 points (which we know results in 3 points under the 5% threshold)
    strain = np.linspace(0, 0.01, 50)
    stress = strain * 1000
    
    # Verify that the function throws a ValueError exactly as expected
    with pytest.raises(ValueError) as exc_info:
        compute_young_modulus(strain, stress)
        
    # Check that your custom error message is correct
    assert "Insufficient data points (3) in the elastic region." in str(exc_info.value)


def test_yield_strength_synthetic():
    # ASSUMPTIONS: E = 1000 MPa, Target Yield = 5.0 MPa
    # Intersection occurs at Strain = Yield/E + Offset = (5/1000) + 0.002 = 0.007
    strain = np.linspace(0, 0.02, 100)
    
    # Generate elastic line (Slope = 1000)
    stress = strain * 1000 
    
    # Cap stress at 5.0 MPa to simulate an elastic-perfectly plastic curve
    stress = np.where(stress > 5.0, 5.0, stress)
    
    # Run the 0.2% offset algorithm
    stress_yield = compute_yield_strength(strain, stress, E_MPa=1000, off_set=0.002)
    
    # VERIFICATION: The offset line intersects the flat 5.0 MPa plateau at exactly 5.0 MPa
    assert stress_yield == pytest.approx(5.0, rel=0.05)




# test3:
def test_uts():
    stress = np.array([0, 1, 5, 10, 8, 5])
    uts = compute_uts(stress)
    assert uts == 10

# test4:
def test_elongation():
    strain = np.linspace(0,0.12,15)
    elong = compute_elongation(strain)
    assert elong == strain.max()

# test5:
def test_toughness():
    # example area = rectangle = 100 MPa * 0.01 strain  = 1MJ/m3
    strain = np.array([0,0.01])
    stress = np.array([100,100])
    tough= compute_toughness(strain,stress)
    assert tough == pytest.approx(1.0)

# test6:
def test_al_6061_sanity():
    """Run on the real processed CSV and check E is in plausible range. """
    df=pd.read_csv('results/processed_6061.csv')
    props = compute_properties(df)
    # E should be within  the range 50-100 GPa for aluminium 
    print(f"\n>>> Computed E = {props['E_GPa']:.2f} GPa, UTS = {props['UTS_MPa']:.2f} MPa")
    assert 50 < props['E_GPa'] <100
    # UTS should be 200–400 MPa for Al-6061
    assert 200 < props['UTS_MPa'] < 400
    