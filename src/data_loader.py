import pandas as pd
from pathlib import Path

def load_tensile_data(file_path):
    path_object= Path(file_path)
    if path_object.suffix.lower() != '.csv':
        raise FileNotFoundError("This is not a CSV file.")

    # 1. Define required columns
    required_cols = {'Time(s)', 'Force(kN)', 'Strain 1(%)'}
    
    # 2. Load the CSV
    df = pd.read_csv(file_path)
    
    # 3. Check for missing columns IMMEDIATELY
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    return df 
   


    

   