"""
Data cleaning and transformation for raw tensile test data.

Stage 3 of the pipeline. Takes the raw DataFrame from `data_loader`
and returns a cleaned, unit-consistent DataFrame ready for property
extraction in `src.mechanical_properties`.

Cleaning steps (in order):
    1. Coerce all required columns to numeric (non-numeric → NaN).
    2. Drop rows with NaN.
    3. Drop rows with negative Force or Strain (grip-seating noise).
    4. Convert Force kN → N        (× 1000).
    5. Convert Strain % → decimal  (÷ 100).
    6. Sort by Strain ascending.
    7. Drop duplicate Strain values (keep first).
    8. Compute engineering stress:
           stress_MPa = Force(N) / A0
       where A0 = width_mm * thickness_mm  [mm^2].
       Note: N / mm^2 = MPa exactly.
"""
import pandas as pd


# Raw CSV columns this module expects.
REQUIRED_COLUMNS = ['Time(s)', 'Force(kN)', 'Strain 1(%)']


def clean_data(df, width_mm, thickness_mm):
    """
    Clean and transform a raw tensile test DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw data from `load_tensile_data`. Must contain the columns in
        REQUIRED_COLUMNS.
    width_mm : float
        Specimen gauge-section width in mm (used for stress calculation).
    thickness_mm : float
        Specimen thickness in mm.

    Returns
    -------
    processed_df : pd.DataFrame
        Columns: ['Time(s)', 'Strain', 'stress_MPa'].
    summary : dict
        Row-count bookkeeping for audit and reporting.
    """
    df = df.copy()
    start_count = len(df)
    summary = {}

    # --- 1. Count missing values before any transformation --------------
    summary['nan_count_before'] = int(df.isnull().sum().sum())

    # --- 2. Coerce to numeric; non-numeric entries become NaN -----------
    for col in REQUIRED_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- 3. Drop NaN and negative rows ----------------------------------
    # Negative force/strain at the start of a test comes from grip seating;
    # it is not physical material response and must be removed.
    df = df.dropna(subset=REQUIRED_COLUMNS)
    df = df[(df['Force(kN)'] >= 0) & (df['Strain 1(%)'] >= 0)]
    summary['after_filter_count'] = len(df)

    # --- 4. Unit conversions --------------------------------------------
    # Force: kN -> N
    df['Force(kN)'] = df['Force(kN)'] * 1000
    df = df.rename(columns={'Force(kN)': 'Force(N)'})

    # Strain: % -> decimal fraction
    df['Strain 1(%)'] = df['Strain 1(%)'] / 100
    df = df.rename(columns={'Strain 1(%)': 'Strain'})

    # --- 5. Sort and deduplicate ----------------------------------------
    # The DAQ may sample faster than the extensometer updates, producing
    # duplicate strain readings. Keep only the first.
    df_sorted = (
        df.drop_duplicates(subset=['Strain'])
          .sort_values(by='Strain')
          .reset_index(drop=True)
          .copy()
    )
    summary['duplicates_removed'] = summary['after_filter_count'] - len(df_sorted)
    summary['final_row_count'] = len(df_sorted)
    summary['removed_count'] = start_count - summary['final_row_count']

    # --- 6. Engineering stress ------------------------------------------
    # sigma = F / A0  ;  A0 = width * thickness  [mm^2]
    # Units: N / mm^2 = MPa (identical by definition).
    original_area_mm2 = width_mm * thickness_mm
    df_sorted['stress_MPa'] = df_sorted['Force(N)'] / original_area_mm2

    processed_df = df_sorted[['Time(s)', 'Strain', 'stress_MPa']]
    return processed_df, summary