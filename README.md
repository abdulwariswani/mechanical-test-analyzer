# Mechanical Test Data Analyzer

A Python tool that turns raw tensile-test data into standard mechanical
properties, plots, and an automated report. Built for aluminium 6061,
but written to be portable to any metal whose tensile data is provided
as CSV with known columns.

**Domain:** mechanical engineering / materials science
**Stack:** Python 3.10+, NumPy, pandas, Matplotlib, pytest
**Status:** All 8 pipeline stages complete.

---

## What it does

Given a CSV containing `Time(s)`, `Force(kN)`, `Strain 1(%)` from a
universal testing machine, the tool:

1. **Loads** the CSV and validates the schema.
2. **Cleans** the data — drops grip-seating noise, converts units,
   computes engineering stress.
3. **Extracts** five standard properties:
   - Young's modulus (E)
   - Yield strength at 0.2% offset (YS)
   - Ultimate tensile strength (UTS)
   - Elongation at fracture
   - Toughness (area under the curve)
4. **Plots** the stress-strain curve (with YS and UTS marked) and a
   property bar chart.
5. **Fits** the plastic region to the Hollomon power law σ = K·εⁿ and
   reports `n`, `K`, and the fit quality R².
6. **Writes** a plain-text report summarizing everything.

---

## Quick Start

```bash
# Clone
git clone https://github.com/abdulwariswani/mechanical-test-analyzer.git
cd mechanical-test-analyzer

# (Optional) Create a fresh environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the analysis on the demo dataset
python main.py data/tensile_stress_strain_6061_aluminum_2\(S32\).csv

# Run the tests
pytest
```

After a successful run you will find:

```
results/
├── processed_6061.csv              # cleaned data
├── figures/
│   ├── stress_strain_T6.png        # annotated curve
│   └── properties_bar_T6.png       # strength + ductility
└── reports/
    └── report.txt                  # automated summary
logs/
└── run_<timestamp>.log             # full DEBUG log
```

---

## Example Output

### Stress-strain curve with yield and UTS points marked

![Stress-strain curve](docs/img/stress_strain_T6.png)

### Property summary (strength and ductility)

![Properties bar chart](docs/img/properties_bar_T6.png)

### Automated report (excerpt)

```
============================================================
MECHANICAL TEST ANALYSIS
============================================================
Date: 2026-10-01 20:09
Material: Al-6061
Condition: T6
============================================================

MECHANICAL PROPERTIES
  Young's Modulus       : 64.6 GPa
  Yield Strength (0.2%) : 285.6 MPa
  Ultimate Tensile Str. : 299.5 MPa
  Elongation at Fracture: 8.48 %
  Toughness             : 23.96 MJ/m³
```

*(Full report written to `results/reports/report.txt` on each run.)*

---

## Repository Layout

```
mechanical-test-analyzer/
├── data/                    example dataset + its README
├── docs/                    math, architecture, assumptions
├── src/                     pipeline modules (one per stage)
├── tests/                   pytest suite
├── main.py                  CLI entry point
├── requirements.txt         pinned dependencies
├── README.md                (this file)
└── LICENSE
```

---

## How it works — a one-paragraph tour

Raw data flows through six stages, one per module. `data_loader.py`
reads the CSV. `preprocessing.py` cleans it and computes engineering
stress. `mechanical_properties.py` extracts the five properties.
`visualization.py` produces the figures. `hardening_analysis.py` fits
the plastic region to the Hollomon law. `reporting.py` writes the
narrative. `main.py` orchestrates the whole flow, and `logger.py`
writes everything to both the console and a timestamped log file.

For details:
- **Formulas and units** → [`docs/math.md`](docs/math.md)
- **Module responsibilities** → [`docs/architecture.md`](docs/architecture.md)
- **Explicit assumptions** → [`docs/assumptions.md`](docs/assumptions.md)
- **Dataset description** → [`data/README.md`](data/README.md)
- **Test coverage** → [`tests/README.md`](tests/README.md)

---

## Demo Dataset

`data/tensile_stress_strain_6061_aluminum_2(S32).csv` — a real tensile
test on a single Al-6061 specimen from a public dataset. Full
provenance, geometry, and reference values are in
[`data/README.md`](data/README.md).

---

## Scope and Non-Goals

This tool **only** does CSV input, single-specimen analysis, and
standard tensile properties. It does not:
- Parse Excel, JSON, or proprietary formats
- Perform machine learning or microstructure simulation
- Run as a web app or service
- Estimate hardness, fatigue life, or fracture toughness (K_IC)

These are deliberate boundaries — see `docs/assumptions.md` for the
reasoning.

---

## License

See [`LICENSE`](LICENSE).