import pandas as pd


def clean_data(df, width_mm, thickness_mm):
    df = df.copy()
    start_count = len(df)
    summary = {}

    # Check for missing values (optional log)
    summary['nan_count_before'] = int(df.isnull().sum().sum())

    # Force data to be numeric
    required_cols = {'Time(s)', 'Force(kN)', 'Strain 1(%)'}
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with NaN values
    df = df.dropna(subset=['Time(s)', 'Force(kN)', 'Strain 1(%)'])

    # Filter out negative values (grip seating phase)
    df = df[(df['Force(kN)'] >= 0) & (df['Strain 1(%)'] >= 0)]

    summary['after_filter_count'] = len(df)

    # Unit conversions
    df['Force(kN)'] = df['Force(kN)'] * 1000
    df = df.rename(columns={'Force(kN)': 'Force(N)'})

    # Convert strain % to decimal
    df['Strain 1(%)'] = df['Strain 1(%)'] / 100
    df = df.rename(columns={'Strain 1(%)': 'Strain'})

    # Sort by strain ascending and remove duplicate strain points
    df_sorted = (df.drop_duplicates(subset=['Strain'])
                   .sort_values(by='Strain')
                   .reset_index(drop=True)
                   .copy())

    summary['duplicates_removed'] = summary['after_filter_count'] - len(df_sorted)
    summary['final_row_count'] = len(df_sorted)
    summary['removed_count'] = start_count - summary['final_row_count']

    # Calculate engineering stress
    original_area_mm2 = width_mm * thickness_mm
    df_sorted['stress_MPa'] = df_sorted['Force(N)'] / original_area_mm2

    processed_df = df_sorted[['Time(s)', 'Strain', 'stress_MPa']]

    return processed_df, summary