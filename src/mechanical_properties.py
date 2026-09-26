"""
Mechanical property extraction from cleaned stress-strain data.

Stage 4 of the pipeline. Takes the cleaned DataFrame from
`preprocessing.clean_data` and computes standard tensile properties:

    E          - Young's modulus (slope of the elastic region)
    YS         - Yield strength via the 0.2% offset method
    UTS        - Ultimate tensile strength (max stress)
    Elongation - Strain at fracture (max strain)
    Toughness  - Area under the stress-strain curve

Unit conventions:
    strain    : unitless (decimal)
    stress    : MPa
    E         : MPa internally, reported in GPa
    Toughness : MPa * strain, which equals MJ/m^3 (since 1 MPa = 1 MJ/m^3)
"""
import logging
import numpy as np


# Fraction of the total strain range assumed elastic when fitting
# Young's modulus. 5% is a heuristic for metals; refine if E deviates
# substantially from literature values.
ELASTIC_FRACTION = 0.05

# Strain offset used by the standard 0.2% yield strength method.
YIELD_OFFSET = 0.002


def compute_young_modulus(strain, stress):
    """
    Young's modulus E = d(sigma)/d(epsilon) in the initial linear region.

    Approach:
        - Take the first `ELASTIC_FRACTION` of the strain range.
        - Fit a first-degree polynomial (linear regression) to sigma vs eps.
        - The slope is E.

    Parameters
    ----------
    strain : np.ndarray
        Strain values (unitless, decimal).
    stress : np.ndarray
        Stress values (MPa).

    Returns
    -------
    float
        Young's modulus in MPa.

    Raises
    ------
    ValueError
        If fewer than 5 points fall inside the elastic window.
    """
    max_strain = strain.max()
    cut_off = max_strain * ELASTIC_FRACTION

    mask = strain <= cut_off
    strain_elastic = strain[mask]
    stress_elastic = stress[mask]

    if len(strain_elastic) < 5:
        raise ValueError(
            f"Insufficient data points ({len(strain_elastic)}) in the elastic region."
        )

    # Linear regression: sigma = E * epsilon + intercept (intercept ~ 0)
    slope, _intercept = np.polyfit(strain_elastic, stress_elastic, 1)
    return slope  # MPa


def compute_yield_strength(strain, stress, E_MPa, off_set=YIELD_OFFSET):
    """
    Yield strength via the 0.2% offset method.

    The offset line is parallel to the elastic slope, shifted to the
    right by `off_set` (0.002). Yield is where this line intersects the
    stress-strain curve:

        sigma_offset(eps) = E * (eps - 0.002)

    We look for the point where (sigma - sigma_offset) changes sign from
    positive to non-positive, then linearly interpolate for precision.

    Parameters
    ----------
    strain : np.ndarray
    stress : np.ndarray
    E_MPa : float
        Young's modulus in MPa (from compute_young_modulus).
    off_set : float
        Strain offset (default 0.002 = 0.2%).

    Returns
    -------
    float
        Yield stress in MPa. Falls back to max stress if no crossing is
        detected (should be rare; logged as a warning).
    """
    offset_line = E_MPa * (strain - off_set)
    diff = stress - offset_line

    # Where does diff flip from positive (curve above line) to non-positive?
    crossings = np.where((diff[:-1] > 0) & (diff[1:] <= 0))[0]

    if len(crossings) == 0:
        logging.warning("No yield crossing found: returning UTS as fallback")
        return stress.max()

    # Linear interpolation between the two bracketing points.
    idx = crossings[0]
    d1 = diff[idx]
    d2 = diff[idx + 1]
    stress_yield = stress[idx] + (-d1 / (d2 - d1)) * (stress[idx + 1] - stress[idx])
    return stress_yield


def compute_uts(stress):
    """Ultimate tensile strength = maximum stress value (MPa)."""
    return stress.max()


def compute_elongation(strain):
    """Elongation at fracture = maximum strain (unitless decimal)."""
    return strain.max()


def compute_toughness(strain, stress):
    """
    Total area under the stress-strain curve up to fracture.

        U_T = integral( sigma d(epsilon) )

    Numerically integrated with the trapezoidal rule. Units work out to
    MPa * strain, which equals MJ/m^3.

    Parameters
    ----------
    strain : np.ndarray
    stress : np.ndarray

    Returns
    -------
    float
        Toughness in MJ/m^3.
    """
    return np.trapezoid(stress, strain)


def compute_properties(processed_df):
    """
    Compute all mechanical properties from a cleaned DataFrame.

    Parameters
    ----------
    processed_df : pd.DataFrame
        Must contain columns 'Strain' and 'stress_MPa'.

    Returns
    -------
    dict
        Keys: E_GPa, Yield_MPa, UTS_MPa, Elongation_pct, Toughness_MJ_m3.
    """
    strain = processed_df['Strain'].to_numpy()
    stress = processed_df['stress_MPa'].to_numpy()

    E_MPa = compute_young_modulus(strain, stress)
    YS = compute_yield_strength(strain, stress, E_MPa)
    UTS = compute_uts(stress)
    elong = compute_elongation(strain)
    tough = compute_toughness(strain, stress)

    return {
        'E_GPa': E_MPa / 1000.0,
        'Yield_MPa': YS,
        'UTS_MPa': UTS,
        'Elongation_pct': elong * 100.0,
        'Toughness_MJ_m3': tough,
    }