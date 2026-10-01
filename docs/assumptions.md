# Assumptions and Heuristics

Every non-trivial decision in the pipeline, listed explicitly. If any
of these turns out to be wrong for a given dataset, the numbers
downstream will be wrong too — so they are documented here rather than
buried in code comments.

---

## Data Interpretation

| # | Assumption | Where | Why | Risk if wrong |
|---|---|---|---|---|
| 1 | Strain is in percent | preprocessing | Header says `(%)` | E and elongation off by 100× |
| 2 | Force is in kN | preprocessing | Header says `(kN)` | Stress and E off by 1000× |
| 3 | Specimen cross-section is constant during the test | preprocessing | Engineering stress definition | True stress differs after necking |
| 4 | The specimen is a flat dogbone with A₀ = w × t | main | From the specimen drawing | Wrong geometry → wrong stress |

---

## Cleaning Rules

| # | Assumption | Where | Why | Risk if wrong |
|---|---|---|---|---|
| 5 | Negative force/strain at start is grip-seating noise | preprocessing | Universal tensile-test behavior | Would drop legitimate data in a compression test |
| 6 | Duplicate strain values are DAQ oversampling | preprocessing | Common extensometer issue | Would drop legitimate data if two points genuinely share strain |
| 7 | Non-numeric entries are corrupt cells, not data | preprocessing | `errors='coerce'` to NaN | Would silently misreport if the value was meaningful |

---

## Property Extraction

| # | Assumption | Where | Why | Risk if wrong |
|---|---|---|---|---|
| 8 | First 5% of strain range is elastic | mechanical_properties | Heuristic for metals | E underestimated if plastic region contaminates the fit |
| 9 | Yield offset = 0.002 | mechanical_properties | ASTM E8 standard | — |
| 10 | Max stress = UTS | mechanical_properties | Definition | — |
| 11 | Max strain = fracture strain | mechanical_properties | Data ends at fracture | Overestimates elongation if test stopped early |
| 12 | Trapezoidal integration of engineering curve = toughness | mechanical_properties | Standard engineering practice | True toughness differs slightly |

---

## Work-Hardening

| # | Assumption | Where | Why | Risk if wrong |
|---|---|---|---|---|
| 13 | Plastic region lies between yield and UTS | hardening_analysis | Necking breaks bulk Hollomon | Fit includes non-Hollomon data |
| 14 | Total strain ≈ plastic strain in the plastic region | hardening_analysis | Elastic strain is small relative to plastic strain above yield | n underestimated at very low strains |
| 15 | R² ≥ 0.95 means fit is trustworthy | hardening_analysis | Conventional cutoff | — |

---

## Out of Scope

The following effects are **real** in tensile testing but are **not
modeled** by this tool. If a dataset requires them, they must be
applied before feeding data in.

- Temperature correction
- Strain-rate correction
- Machine-compliance correction
- True stress / true strain conversion (only engineering values reported)
- Vickers / Rockwell hardness (not derived from tensile data)
- Any microstructural interpretation (grain size, precipitates, phases)

---

## When to Revisit These

If a run produces:
- E outside 50–100 GPa for aluminum → revisit #8
- Elongation > 30% for a T6 temper → revisit #11
- n outside 0.05–0.5 → revisit #13 and #14

Each of these is already logged as a warning by the pipeline, so watch
the log file for the trigger.