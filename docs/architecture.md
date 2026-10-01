# Architecture

The pipeline is a **one-way flow** from raw CSV to final report. Every
stage lives in its own module, has one job, and hands its output to the
next stage. Nothing downstream modifies the input it received; nothing
upstream knows what happens next.

This is deliberate: it makes each stage independently testable, and it
means a bug in (say) the report writer cannot corrupt the property
calculations.

---

## Pipeline Diagram
raw CSV
│
▼
┌──────────────────┐
│ data_loader.py │ Read file, validate schema. No cleaning.
└──────────────────┘
│ DataFrame
▼
┌──────────────────┐
│ preprocessing.py │ Drop bad rows, convert units, compute σ.
└──────────────────┘
│ cleaned DataFrame + summary dict
▼
┌──────────────────────────┐
│ mechanical_properties.py │ E, YS, UTS, elongation, toughness.
└──────────────────────────┘
│ properties dict
├──────────────────────────────┬─────────────────────────────┐
▼ ▼ ▼
┌──────────────────┐ ┌────────────────────┐ ┌──────────────────┐
│ visualization.py │ │ hardening_analysis │ │ reporting.py │
│ PNG figures │ │ n, K, R² │ │ report.txt │
└──────────────────┘ └────────────────────┘ └──────────────────┘



`main.py` orchestrates the flow. `logger.py` is a cross-cutting utility
that all modules use.

---

## Module Responsibilities

| Module | Stage | Responsibility | Inputs | Outputs |
|---|---|---|---|---|
| `data_loader.py` | 2 | Read CSV, validate required columns exist | file path | raw DataFrame |
| `preprocessing.py` | 3 | Clean, convert units, compute engineering stress | raw DataFrame + geometry | cleaned DataFrame + summary dict |
| `mechanical_properties.py` | 4 | Compute E, YS, UTS, elongation, toughness | cleaned DataFrame | properties dict |
| `visualization.py` | 5 | Generate PNG figures | cleaned DataFrame + properties | PNG file paths |
| `hardening_analysis.py` | 6 | Fit Hollomon power law to plastic region | cleaned DataFrame + properties | n, K, R² |
| `reporting.py` | 7 | Write human-readable text report | properties + summary | report.txt |
| `logger.py` | — | Dual-handler logging (console + file) | — | configured root logger |
| `main.py` | — | Orchestrate the pipeline | CLI argument | all outputs in `results/` |

---

## Data Flow Contracts

Each stage has a strict contract. Breaking a contract is a bug.

### Stage 2 → Stage 3
- **DataFrame columns:** `Time(s)`, `Force(kN)`, `Strain 1(%)`
- **No NaN handling yet.** Raw values as read from CSV.

### Stage 3 → Stage 4
- **DataFrame columns:** `Time(s)`, `Strain`, `stress_MPa`
- **Strain** is decimal (unitless), sorted ascending, unique.
- **stress_MPa** is in MPa.
- **No negative values.**

### Stage 4 → Stage 5, 6, 7
- **Properties dict keys:**
  - `E_GPa` (float)
  - `Yield_MPa` (float)
  - `UTS_MPa` (float)
  - `uts_strain` (float, decimal)
  - `Elongation_pct` (float, percent)
  - `Toughness_MJ_m3` (float)
  - `yield_strain` (float, decimal)

### Stage 6 → Stage 7
- **Hardening results dict keys:**
  - `n` (float or None)
  - `K_MPa` (float or None)
  - `R2` (float or None)

Merged into the properties dict before Stage 7 runs.

---

## Output Contract

A successful run of `python main.py <csv>` produces:

esults/
├── processed_6061.csv cleaned data (for inspection)
├── figures/
│ ├── stress_strain_T6.png curve with YS and UTS marked
│ └── properties_bar_T6.png strength + ductility bars
└── reports/
└── report.txt narrative summary

logs/
└── run_<timestamp>.log DEBUG-level log of the run


Console output shows INFO-level logs: load confirmation, cleaning
summary, properties, figure paths, work-hardening values, report path.

---

## Error Handling

| Failure | Where caught | Behavior |
|---|---|---|
| File not found / not a CSV | `data_loader` | Raise; `main` logs and exits with code 1 |
| Missing required columns | `data_loader` | Raise `ValueError`; `main` logs and exits |
| < 5 elastic points | `mechanical_properties` | Raise `ValueError` |
| No yield crossing | `mechanical_properties` | Log warning; fall back to `stress.max()` |
| < 3 plastic points | `hardening_analysis` | Log warning; return `None`s |
| R² < 0.95 | `hardening_analysis` | Log warning; still return values |
| n outside 0.05–0.5 | `hardening_analysis` | Log warning; still return values |

Warnings never crash the pipeline; they are recorded in the log file
and (for some cases) noted in the report.

---

## Testing Strategy

Tests are organized by module:

- `test_data_loader.py` — schema validation
- `test_preprocessing.py` — cleaning rules, unit conversions
- `test_properties.py` — property formulas on synthetic data
- `test_hardening_analysis.py` — power-law fit recovery

Synthetic test data is used wherever the analytical answer is known
(e.g., E = 1000 MPa for `stress = 1000·strain`), so the assertion is
exact rather than approximate. The single integration test
(`test_al_6061_sanity`) runs the real processed CSV and checks the
result falls inside literature bounds.

See `tests/README.md` for a per-test breakdown.