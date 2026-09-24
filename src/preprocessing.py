import pandas as pd


def clean_data(df, width_mm, thickness_mm):
        start_count  = len(df)
        summary = {}
    # 4. Check for missing values (optional log)
        summary['nan_count_before']= int(df.isnull().sum(),sum())

    
        # 5. Force data to be numeric
        required_cols = {'Time(s)', 'Force(kN)', 'Strain 1(%)'}
        for col in required_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    
        # 6. Drop rows with NaN values
        df = df.dropna(subset=['Time(s)', 'Force(kN)', 'Strain 1(%)'])

    
        # 7. Filter out negative values (grip seating phase)
        df = df[(df['Force(kN)'] >= 0) & (df['Strain 1(%)'] >= 0)]

        summary['final_row_count'] = len(df)
        summary['removed_count'] = start_count - summary['final_row_count']
        
    
        # 8. Unit conversions
        df['Force(kN)'] = df['Force(kN)'] * 1000
        df = df.rename(columns={'Force(kN)': 'Force(N)'})

        
        # Convert strain % to decimal
        df['Strain 1(%)'] = df['Strain 1(%)'] / 100
        df = df.rename(columns={'Strain 1(%)': 'Strain'})

        
        original_area_mm2 = width_mm * thickness_mm  
        
        df['stress_MPa'] = df['Force(N)'] / original_area_mm2

        processed_df = df[['Time(s)', 'Strain', 'stress_MPa']]

        return processed_df , summary