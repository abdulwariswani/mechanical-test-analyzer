"""
Command-line entry point for the Mechanical Test Data Analyzer.

Usage:
    python main.py <path/to/raw_tensile.csv>

Pipeline:
    1. Load raw CSV           (src.data_loader)
    2. Clean & convert units  (src.preprocessing)
    3. Compute properties     (src.mechanical_properties)
    4. Save processed CSV to results/processed_6061.csv
"""
import sys
import os
import logging
from src.logger import setup_logging 

from src.data_loader import load_tensile_data
from src.preprocessing import clean_data
from src.mechanical_properties import compute_properties


# Specimen geometry for the Al-6061 miniature dogbone (see data/README.md).
# Update if using a different specimen.
WIDTH_MM = 2.00
THICKNESS_MM = 2.00

# Output location for the processed CSV.
OUTPUT_CSV = 'results/processed_6061.csv'


def get_path_from_the_arg():
    """Return the CSV path from argv, or exit with a usage message."""
    if len(sys.argv) >= 2:
        return sys.argv[1]
    logging.error("Usage: python main.py <file_path>")
    sys.exit(1)


def main():
    setup_logging()
    file_path = get_path_from_the_arg()

    # Stage 2: load raw data (I/O + schema validation).
    try:
        raw_df = load_tensile_data(file_path)
        logging.info('Loaded raw data successfully.')
    except (ValueError, FileNotFoundError) as e:
        logging.error(f"Error: {e}")
        sys.exit(1)

    # Ensure output directory exists.
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    # Stage 3: clean, convert units, compute engineering stress.
    processed_df, summary = clean_data(
        raw_df,
        width_mm=WIDTH_MM,
        thickness_mm=THICKNESS_MM,
    )
    processed_df.to_csv(OUTPUT_CSV, index=False)
    logging.info(summary)

    # Stage 4: mechanical properties.
    properties = compute_properties(processed_df)
    logging.info(f'Properties: {properties}')


if __name__ == "__main__":
    main()