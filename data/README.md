# Data: Al-6061 Tensile Test

## File

- `tensile_stress_strain_6061_aluminum_2(S32).csv` — raw tensile test data
  for a single specimen (S32) of 6061 aluminium.

## Source

> - Repository: Mendeley Data
> - URL: https://data.mendeley.com/datasets/jzw6jn7g39/1
> - Dataset title: *tensile_stress_strain_6061 al_Ti64*
> - License: CC BY (verify on the dataset page)
> - Accessed: [YYYY-MM-DD]
>
> If the source is different, replace the block above with the correct
> citation: repository name, URL, license, and access date.

## Material

- **Alloy:** 6061 aluminium (Al-Mg-Si, 6xxx series).
- **Condition:** Confirm from source (likely T6 or as-received).
- 6061 is a heat-treatable alloy: T6 = solution-treated + artificially aged.

## Specimen Geometry

From the drawing *"Miniature dogbone tensile sample (6061 aluminum)"*:

| Dimension      | Value (mm)  |
|----------------|-------------|
| Thickness      | 2.00        |
| Gauge width    | 2.00 ± 0.10 |
| Gauge length   | 17.53       |
| Overall length | 38.00       |
| Grip width     | 4.00        |

**Gauge cross-sectional area:**

    A0 = gauge width * thickness = 2.00 * 2.00 = 4.00 mm^2

This value is encoded as `WIDTH_MM` and `THICKNESS_MM` in `main.py`.

## Raw Columns

| Column        | Unit | Description                                 |
|---------------|------|---------------------------------------------|
| `Time(s)`     | s    | Elapsed time from test start.               |
| `Force(kN)`   | kN   | Axial load applied to the specimen.         |
| `Strain 1(%)` | %    | Axial strain measured by the extensometer.  |

## Unit Conversions Used in the Pipeline

| Quantity | From | To       | Factor | Location                      |
|----------|------|----------|--------|-------------------------------|
| Force    | kN   | N        | x 1000 | `preprocessing.clean_data`    |
| Strain   | %    | decimal  | / 100  | `preprocessing.clean_data`    |

## Derived Columns

| Column       | Formula              | Unit           |
|--------------|----------------------|----------------|
| `stress_MPa` | `Force(N) / A0`      | MPa (= N/mm^2) |

N/mm^2 is numerically identical to MPa, so no further conversion is
needed after this step.

## Data Quality Notes

The raw file contains artifacts that `preprocessing.clean_data` handles:

1. **Negative initial values** — the first rows have slightly negative
   force and strain from grip seating. Removed.
2. **Duplicate strain values** — the DAQ samples faster than the
   extensometer updates, producing repeated readings. First occurrence kept.
3. **Non-monotonic strain** — small fluctuations may cause strain to
   momentarily decrease. Sorting plus deduplication enforces monotonicity.

## Reference Values (Literature)

Typical properties for Al-6061-T6, used as sanity checks:

| Property                     | Typical range | Source                       |
|------------------------------|---------------|------------------------------|
| Young's modulus              | 68–70 GPa     | Callister                   |
| Yield strength (0.2% offset) | ~276 MPa      | ASM Handbook                |
| Ultimate tensile strength    | 290–310 MPa   | ASM Handbook                |
| Elongation at fracture       | 8–12%         | ASM Handbook                |

## Observed Values (from this file)

| Property          | Computed  | Within literature range?       |
|-------------------|-----------|--------------------------------|
| Young's modulus   | 64.6 GPa  | Yes (slightly low, acceptable) |
| UTS               | 299.5 MPa | Yes                            |