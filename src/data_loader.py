import pandas as pd
import logging

def load_tensile_data(csv_file):
    # 1. Define required columns
    required_cols = {'Time(s)', 'Force(kN)', 'Strain 1(%)'}
    
    # 2. Load the CSV
    df = pd.read_csv(csv_file)
    
    # 3. Check for missing columns IMMEDIATELY
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
        
    # 4. Check for missing values (optional log)
    logging.info(f"Null values before cleaning:\n{df.isnull().sum()}")

    # 5. Force data to be numeric
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 6. Drop rows with NaN values
    df = df.dropna(subset=['Time(s)', 'Force(kN)', 'Strain 1(%)'])

    # 7. Filter out negative values (grip seating phase)
    df = df[(df['Force(kN)'] >= 0) & (df['Strain 1(%)'] >= 0)]

    # 8. Unit conversions
    df['Force(kN)'] = df['Force(kN)'] * 1000
    df = df.rename(columns={'Force(kN)': 'Force(N)'})
    
    # Convert strain % to decimal
    df['Strain 1(%)'] = df['Strain 1(%)'] / 100
    df = df.rename(columns={'Strain 1(%)': 'Strain'})

    # 9. Calculate Engineering Stress
    width_mm = 2.00       # From PDF drawing
    thickness_mm = 2.00   # From PDF drawing
    original_area_mm2 = width_mm * thickness_mm  # Fixed typo: original
    
    df['stress_MPa'] = df['Force(N)'] / original_area_mm2

    # 10. Export processed data
    processed_df = df[['Time(s)', 'Strain', 'stress_MPa']]
    processed_df.to_csv('data/processed_6061.csv', index=False)
    return processed_df