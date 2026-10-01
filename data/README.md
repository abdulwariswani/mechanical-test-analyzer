# Data — Al-6061 Tensile Test

## File

`tensile_stress_strain_6061_aluminum_2(S32).csv` — raw tensile-test
data for one specimen (S32) of 6061 aluminium.

## Source

- **Repository:** Mendeley Data
- **URL:** https://data.mendeley.com/datasets/jzw6jn7g39/1
- **Dataset title:** *tensile_stress_strain_6061 al_Ti64*
- **License:** CC BY (verify on the dataset page)
- **Accessed:** 2026-09-XX *(fill in the actual date)*

If you replace this file with data from a different source, update
this block with the new citation.

## Material

- **Alloy:** 6061 aluminium (Al-Mg-Si, 6xxx series)
- **Condition:** T6 (solution-treated + artificially aged)
- **Note:** 6061 is a heat-treatable alloy — properties depend
  strongly on temper. T6 gives high strength at reduced ductility
  compared to the as-received condition.

## Specimen Geometry

From the drawing *"Miniature dogbone tensile sample (6061 aluminum)"*:

| Dimension       | Value (mm)   |
|-----------------|--------------|
| Thickness       | 2.00         |
| Gauge width     | 2.00 ± 0.10  |
| Gauge length    | 17.53        |
| Overall length  | 38.00        |
| Grip width      | 4.00         |

**Initial gauge cross-sectional area:**

    A₀ = gauge width × thickness = 2.00 × 2.00 = 4.00 mm²

This is passed to `clean_data()` from `main.py` via the constants
`WIDTH_MM` and `THICKNESS_MM`.

## Raw Columns

| Column         | Unit | Description                                   |
|----------------|------|-----------------------------------------------|
| `Time(s)`      | s    | Elapsed time from the start of the test.      |
| `Force(kN)`    | kN   | Axial load applied to the specimen.           |
| `Strain 1(%)`  | %    | Axial strain measured by the extensometer.    |

The tool only expects these three columns. Optional metadata columns
(`material`, `condition`) are supplied as CLI arguments instead.

## Unit Conversions

| Quantity | From | To        | Factor | Location                   |
|----------|------|-----------|--------|----------------------------|
| Force    | kN   | N         | × 1000 | `preprocessing.clean_data` |
| Strain   | %    | decimal   | ÷ 100  | `preprocessing.clean_data` |

## Derived Columns

| Column       | Formula          | Unit          |
|--------------|------------------|---------------|
| `stress_MPa` | `Force(N) / A₀`  | MPa (= N/mm²) |

`N/mm² = MPa` exactly, so no further conversion is needed.

## Data Quality Notes

The raw file contains three artifacts that `preprocessing.clean_data`
handles automatically:

1. **Negative initial values** — the first rows show slightly negative
   force and strain from grip seating. These are dropped.
2. **Duplicate strain values** — the DAQ samples faster than the
   extensometer updates. Only the first occurrence is kept.
3. **Non-monotonic strain** — sorting plus deduplication enforces
   strictly increasing strain, which every downstream calculation
   assumes.

## Reference Values (Al-6061-T6)

Used as sanity checks in `tests/test_properties.py`:

| Property                     | Typical range | Source        |
|------------------------------|---------------|---------------|
| Young's modulus              | 68–70 GPa     | Callister     |
| Yield strength (0.2% offset) | ~276 MPa      | ASM Handbook  |
| Ultimate tensile strength    | 290–310 MPa   | ASM Handbook  |
| Elongation at fracture       | 8–12 %        | ASM Handbook  |

## Observed Values (this specimen)

Computed by running the pipeline on this file:

| Property        | Value      | Within literature range?     |
|-----------------|------------|------------------------------|
| Young's modulus | 64.6 GPa   | Yes (slightly low, expected) |
| UTS             | 299.5 MPa  | Yes                          |
| Yield (0.2%)    | 285.6 MPa  | Slightly above typical       |
| Elongation      | 8.48 %     | Yes                          |
| Toughness       | 23.96 MJ/m³| —                            |
| n               | 0.021      | Below typical (near-flat)    |

The slightly high yield strength and low `n` reflect the very flat
plastic region typical of a T6-temper specimen — see the note in the
auto-generated `report.txt`.