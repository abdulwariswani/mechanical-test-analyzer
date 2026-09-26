"""
Data loader for mechanical tensile test files.

Stage 2 of the pipeline. Responsible only for I/O and schema validation:
reads a CSV, verifies the expected columns are present, and returns the
raw DataFrame without any transformation.

Downstream cleaning and unit conversion live in `src.preprocessing`.
"""
from pathlib import Path
import pandas as pd


# Columns the raw CSV must contain. If a file is missing any of these,
# loading fails immediately with a clear error.
REQUIRED_COLUMNS = {'Time(s)', 'Force(kN)', 'Strain 1(%)'}


def load_tensile_data(file_path):
    """
    Read a tensile test CSV and validate its schema.

    Parameters
    ----------
    file_path : str or Path
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Raw data with original column names (no cleaning applied).

    Raises
    ------
    FileNotFoundError
        If the path does not have a .csv extension.
    ValueError
        If any of the required columns are missing.
    """
    path_object = Path(file_path)
    if path_object.suffix.lower() != '.csv':
        raise FileNotFoundError("This is not a CSV file.")

    df = pd.read_csv(file_path)

    # Schema check: fail fast if the expected columns are absent.
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    return df