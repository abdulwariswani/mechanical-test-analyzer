# Mechanical Test Data Analyzer

A Python tool that ingests raw tensile-test data (stress-strain curves),
cleans and validates it, extracts standard mechanical properties, and
produces a reproducible analysis of aluminium 6061.

## What it does

Given a raw CSV of tensile test data (`Time`, `Force`, `Strain`):

1. **Load** — reads the CSV and validates the schema.
2. **Clean** — converts units, removes invalid rows, sorts by strain.
3. **Compute** — calculates Young's modulus, yield strength (0.2%
   offset), UTS, elongation, and toughness.
4. **Plot** *(Stage 5, in progress)* — stress-strain curves.
5. **Report** *(Stage 7, pending)* — automated text summary.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt