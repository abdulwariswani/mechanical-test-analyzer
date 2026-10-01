# Math Reference

Every formula used by the pipeline, with units and a plain-English
description. If a reviewer reads only one document, this should be it.

Conventions used throughout:
- Stress is in **MPa**
- Strain is **unitless (decimal)** — 0.01 means 1%
- Force is in **N** (after preprocessing)
- Area is in **mm²**
- Energy density (toughness) is in **MJ/m³**

The identity **1 N/mm² = 1 MPa** is used repeatedly and is exact
by definition of the pascal.

---

## 1. Engineering Stress

    σ = F / A₀

- `F` = axial force (N)
- `A₀` = initial gauge cross-section (mm²) = width × thickness
- `σ` = engineering stress (MPa)

For the demo specimen: A₀ = 2.00 × 2.00 = **4.00 mm²**.

**Why "engineering"?** We divide by the *original* area, not the
current (necked) area. This is the standard convention for tensile
reporting; true stress would divide by the instantaneous area.

**Implemented in:** `src/preprocessing.py :: clean_data` (step 6).

---

## 2. Engineering Strain

    ε = ΔL / L₀

The raw CSV gives strain as a **percent** (column `Strain 1(%)`).
Preprocessing divides by 100 to get a decimal fraction:

    ε_decimal = ε_percent / 100

**Implemented in:** `src/preprocessing.py :: clean_data` (step 5).

---

## 3. Unit Conversions

| Quantity | From | To | Factor | Where |
|---|---|---|---|---|
| Force | kN | N | × 1000 | preprocessing |
| Strain | % | decimal | ÷ 100 | preprocessing |
| Stress | N/mm² | MPa | identity | preprocessing |
| Young's modulus | MPa | GPa | ÷ 1000 | mechanical_properties |
| Elongation | decimal | % | × 100 | mechanical_properties |
| Toughness | MPa·strain | MJ/m³ | identity | mechanical_properties |

The last identity: 1 MPa = 1 N/mm² = 1 N·mm/mm³ = 1 mJ/mm³ = 1 MJ/m³.

---

## 4. Young's Modulus

    E = dσ / dε   (evaluated in the linear-elastic region)

**Discrete implementation:**
- Select the first `ELASTIC_FRACTION = 5%` of the total strain range.
- Fit a first-degree polynomial with `np.polyfit(strain, stress, 1)`.
- The slope is E (in MPa).

**Why 5%?** A heuristic. Too small → noisy fit. Too large → includes
plastic yielding and underestimates E. For Al-6061-T6 the elastic
region ends around 0.4% strain, so 5% of an ~8% fracture strain
(≈ 0.4%) sits comfortably inside.

**Guard:** raises `ValueError` if fewer than 5 points land in the
elastic window.

**Reported as:** `E_GPa = E_MPa / 1000`.

**Literature (Al-6061-T6):** 68–70 GPa.

**Implemented in:** `src/mechanical_properties.py :: compute_young_modulus`.

---

## 5. Yield Strength (0.2% Offset Method)

**Definition (ASTM E8):** the stress at which a line parallel to the
elastic slope, offset by 0.002 strain, intersects the stress-strain
curve.

**Offset line equation:**

    σ_offset(ε) = E · (ε − 0.002)

**Intersection condition:**

    σ_curve(ε) − σ_offset(ε) = 0

**Discrete implementation:**
1. Compute `diff = stress − E·(strain − 0.002)` for every point.
2. Find the first index `i` where `diff[i] > 0` and `diff[i+1] <= 0`.
3. Linearly interpolate between the two bracketing points:

       σ_yield = σ[i] + (−d₁ / (d₂ − d₁)) · (σ[i+1] − σ[i])
       ε_yield = ε[i] + (−d₁ / (d₂ − d₁)) · (ε[i+1] − ε[i])

   where d₁ = diff[i], d₂ = diff[i+1].

**Fallback:** if no crossing is found, log a warning and return
`stress.max()` (i.e., UTS). Rare; indicates a pathological curve.

**Literature (Al-6061-T6):** ~276 MPa.

**Implemented in:** `src/mechanical_properties.py :: compute_yield_strength`.

---

## 6. Ultimate Tensile Strength (UTS)

    UTS = max(σ)

The maximum engineering stress on the curve. Physically it corresponds
to the onset of necking (Considère's criterion).

**Literature (Al-6061-T6):** 290–310 MPa.

**Implemented in:** `src/mechanical_properties.py :: compute_uts`.

---

## 7. Elongation at Fracture

    elongation = max(ε) × 100%

Assumes the last recorded strain corresponds to fracture. A more
rigorous estimate would fit the post-necking region back to zero
stress, but the max-strain definition is standard for engineering
reports.

**Literature (Al-6061-T6):** 8–12%.

**Implemented in:** `src/mechanical_properties.py :: compute_elongation`.

---

## 8. Toughness (Modulus of Toughness)

    U_T = ∫₀^ε_f σ dε

Total energy absorbed per unit volume up to fracture.

**Numerical implementation:** trapezoidal rule via `np.trapezoid(stress, strain)`.

**Units:** MPa · strain = MJ/m³ (see §3 identity).

**Caveat:** computed on the *engineering* curve. True toughness differs
slightly because it uses true stress and true strain. For ductile
metals at moderate strain this difference is small.

**Implemented in:** `src/mechanical_properties.py :: compute_toughness`.

---

## 9. Work-Hardening (Hollomon Power Law)

**Model:**

    σ = K · εⁿ     (plastic region only)

where:
- `n` = work-hardening exponent (unitless)
- `K` = strength coefficient (MPa)
- both evaluated using the **true** plastic strain; the pipeline
  approximates this with total strain above yield — acceptable for
  moderate strains.

**Linearization:** take natural logs of both sides:

    log σ = log K + n · log ε

This is a straight line in (log ε, log σ) with slope `n` and
intercept `log K`.

**Fit:** `np.polyfit(log_strain, log_stress, 1)` returns `[slope, intercept]`.

    n = slope
    K = exp(intercept)

**Plastic-region slice:** `yield_strain ≤ ε ≤ uts_strain`. Points beyond
UTS are excluded because necking breaks the bulk-Hollomon assumption.

**Guard:** requires ≥ 3 points in the plastic region.

**Quality check — R²:**

    R² = 1 − SS_res / SS_tot

    SS_res = Σ (log σ − ŷ)²      (residuals of the fit)
    SS_tot = Σ (log σ − mean)²   (variance of the data)

If R² < 0.95 the fit is logged as unreliable.

**Sanity check:** typical `n` for Al alloys is 0.1–0.4. Values outside
0.05–0.5 trigger a warning.

**Implemented in:** `src/hardening_analysis.py :: compute_work_hardening`.

---

## 10. Summary Table — Properties and Units

| Property | Symbol | Unit reported | Typical Al-6061-T6 |
|---|---|---|---|
| Young's modulus | E | GPa | 68–70 |
| Yield strength (0.2%) | YS | MPa | ~276 |
| Ultimate tensile strength | UTS | MPa | 290–310 |
| Elongation at fracture | ε_f | % | 8–12 |
| Toughness | U_T | MJ/m³ | — |
| Work-hardening exponent | n | — | 0.1–0.4 |
| Strength coefficient | K | MPa | — |

---

## 11. References

- ASTM E8 / E8M — Standard Test Methods for Tension Testing of Metallic Materials.
- Callister, W.D. — *Materials Science and Engineering: An Introduction* (Young's modulus values).
- ASM Handbook, Vol. 2 — Properties and Selection: Nonferrous Alloys (Al-6061-T6 properties).
- Hollomon, J.H. (1945) — "Tensile deformation," *Trans. AIME* 162, 268–290.