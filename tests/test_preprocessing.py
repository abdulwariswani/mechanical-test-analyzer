import pandas as pd
import pytest
from src.preprocessing import clean_data


# Test 1: Rows with NaN in any required column must be dropped.
def test_drops_nan_rows():
    """Two of four rows contain NaN → two survivors expected."""
    nan_data = {
        'Time(s)': [0.1, 0.2, 0.3, 0.4],
        'Force(kN)': [0.03, None, 0.05, 0.06],
        'Strain 1(%)': [0.001, 0.002, None, 0.004],
    }
    df = pd.DataFrame(nan_data)
    cleaned, summary = clean_data(df, width_mm=2.0, thickness_mm=2.0)
    assert len(cleaned) == 2
    assert cleaned.isnull().sum().sum() == 0
    assert summary['removed_count'] > 0



# Test 2: Rows with negative Force or Strain (grip-seating phase) must be dropped.
def test_drops_negative_values():
    """Row 1 has negative force and strain → must be removed."""
    negative_data = {
        'Time(s)': [0.1, 0.2, 0.3, 0.4],
        'Force(kN)': [-0.01, 0.03, -0.05, 0.07],
        'Strain 1(%)': [0.001, -0.002, 0.003, 0.004],
    }
    df = pd.DataFrame(negative_data)
    cleaned, summary = clean_data(df, width_mm=2.0, thickness_mm=2.0)
    assert cleaned['stress_MPa'].min() >= 0
    assert cleaned['Strain'].min() >= 0
    assert summary['final_row_count'] == 1
    assert summary['after_filter_count'] == 1



# Test 3: Strain labelled as percent (values > 1) must be divided by 100.
def test_strain_convert_to_decimal():
    """Input max strain = 1.5 (%) → output max strain = 0.015."""
    percent_strain_data = {
        'Time(s)': [0.1, 0.2, 0.3],
        'Force(kN)': [0.03, 0.04, 0.05],
        'Strain 1(%)': [0.5, 1.0, 1.5],
    }
    df = pd.DataFrame(percent_strain_data)
    cleaned, _ = clean_data(df, width_mm=2.0, thickness_mm=2.0)
    assert cleaned['Strain'].max() == pytest.approx(0.015)





# Test 5: Stress = Force(N) / (width * thickness) in MPa.
def test_stress_calculation():
    """4 N over a 4 mm² cross-section → 1.0 MPa."""
    stress_calc_data = {
        'Time(s)': [0.1],
        'Force(kN)': [0.004],   # 0.004 kN = 4 N
        'Strain 1(%)': [0.001],
    }
    df = pd.DataFrame(stress_calc_data)
    cleaned, _ = clean_data(df, width_mm=2.0, thickness_mm=2.0)
    assert cleaned['stress_MPa'].iloc[0] == pytest.approx(1.0)



# Test 6: Duplicate strain values must be reduced to one row each.
def test_duplicates_removed():
    """Strain 0.002 appears twice → one row removed."""
    duplicate_data = {
        'Time(s)': [0.1, 0.2, 0.3, 0.4],
        'Force(kN)': [0.03, 0.04, 0.05, 0.06],
        'Strain 1(%)': [0.001, 0.002, 0.002, 0.003],
    }
    df = pd.DataFrame(duplicate_data)
    cleaned, summary = clean_data(df, width_mm=2.0, thickness_mm=2.0)
    assert cleaned['Strain'].is_unique
    assert summary['duplicates_removed'] == 1



# Test 7: Output must be sorted by strain ascending.
def test_sorted_by_strain():
    """Unordered strain input → monotonic output."""
    unsorted_data = {
        'Time(s)': [0.1, 0.2, 0.3, 0.4],
        'Force(kN)': [0.06, 0.03, 0.05, 0.04],
        'Strain 1(%)': [0.004, 0.001, 0.003, 0.002],
    }
    df = pd.DataFrame(unsorted_data)
    cleaned, _ = clean_data(df, width_mm=2.0, thickness_mm=2.0)
    assert cleaned['Strain'].is_monotonic_increasing



# Test 8: Summary must expose all canonical keys.
def test_summary_keys():
    """Summary dict must contain the full standard schema."""
    mixed_issues_data = {
        'Time(s)': [0.1, 0.2, 0.3, 0.4, 0.5],
        'Force(kN)': [0.03, -0.01, None, 0.05, 0.06],
        'Strain 1(%)': [0.001, 0.002, 0.003, 0.003, 0.004],
    }
    df = pd.DataFrame(mixed_issues_data)
    _ ,summary = clean_data(df, width_mm=2.0, thickness_mm=2.0)
    required = {
        'nan_count_before', 'after_filter_count', 'removed_count',
        'duplicates_removed', 'final_row_count',
    }
    assert required.issubset(summary.keys())
