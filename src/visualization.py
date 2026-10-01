"""
Visualization module for the Mechanical Test Data Analyzer (Stage 5).

Produces figures from a cleaned stress-strain DataFrame and computed
mechanical properties. All figures are saved as PNGs; no GUI window
pops up because matplotlib is forced to use its headless Agg backend.

Public functions:
    plot_curve             - single stress-strain curve with YS/UTS marked
    plot_comparison        - multiple curves overlaid for comparison
    plot_properties_bar    - bar chart of key properties
    generate_all_figures   - convenience wrapper that produces the standard set
"""
import os
import logging

import numpy as np
import matplotlib
matplotlib.use('Agg')          # must be called BEFORE importing pyplot
import matplotlib.pyplot as plt


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Style constants — change once, affects every figure
# ---------------------------------------------------------------------------
FIG_DPI = 150                    # output resolution (dots per inch)
FIG_SIZE_WIDE = (10, 6)          # figure size (width, height) in inches
FIG_SIZE_BAR = (8, 5)
COLOR_CURVE = '#1f77b4'          # matplotlib tab:blue
COLOR_YIELD = 'red'
COLOR_UTS = 'orange'
COLOR_BARS = ['#1f77b4', '#ff7f0e', '#2ca02c']
GRID_ON = False                  # per blueprint: gridlines off
FONT_TITLE = 13
FONT_LABEL = 11
FONT_ANNOT = 9


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def apply_base_style(ax, title, xlabel, ylabel):
    """
    Apply consistent title, axis labels, and grid styling to an Axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    title, xlabel, ylabel : str
    """
    ax.set_title(title, fontsize=FONT_TITLE)
    ax.set_xlabel(xlabel, fontsize=FONT_LABEL)
    ax.set_ylabel(ylabel, fontsize=FONT_LABEL)
    ax.grid(GRID_ON, alpha=0.3)
    return ax


def save_figure(fig, filepath):
    """
    Save a figure to disk and free its memory.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
    filepath : str
        Full path ending in .png. Parent directories are created if missing.
    """
    parent_dir = os.path.dirname(filepath)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    fig.tight_layout()
    fig.savefig(filepath, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)
    logger.info(f"Saved figure: {filepath}")


# ---------------------------------------------------------------------------
# Plot 1: single stress-strain curve
# ---------------------------------------------------------------------------
def plot_curve(processed_df, properties, filepath,
               material='Al-6061', condition='unknown'):
    """
    Plot a single stress-strain curve with the yield and UTS points marked.

    Parameters
    ----------
    processed_df : pd.DataFrame
        Must contain 'Strain' (decimal) and 'stress_MPa'.
    properties : dict
        Output of compute_properties(). Needs 'E_GPa', 'Yield_MPa', 'UTS_MPa'.
    filepath : str
        Output PNG path.
    material, condition : str
        Used in the plot title.
    """
    strain = processed_df['Strain'].to_numpy()
    stress = processed_df['stress_MPa'].to_numpy()

    # Guard: a meaningful curve needs several points.
    if len(strain) < 5:
        logger.warning(
            f"Only {len(strain)} points available; skipping curve plot."
        )
        return None

    fig, ax = plt.subplots(figsize=FIG_SIZE_WIDE)

    # --- main curve --------------------------------------------------------
    ax.plot(strain * 100.0, stress,
            color=COLOR_CURVE, linewidth=1.5, label='Stress-Strain')

    # --- yield point -------------------------------------------------------
    # The 0.2% offset yield point lies on the curve at
    #     eps_yield = sigma_yield / E + 0.002
    # because the offset line is   sigma = E * (eps - 0.002).
    yield_stress = properties.get('Yield_MPa')
    if yield_stress:
        E_MPa = properties['E_GPa'] * 1000.0
        yield_strain = yield_stress / E_MPa + 0.002
        ax.plot(yield_strain * 100.0, yield_stress,
                marker='o', markersize=7, color=COLOR_YIELD,
                linestyle='None', zorder=5)
        ax.annotate(
            f'YS = {yield_stress:.1f} MPa',
            xy=(yield_strain * 100.0, yield_stress),
            xytext=(yield_strain * 100.0 + 1.5, yield_stress * 0.7),
            arrowprops=dict(arrowstyle='->', color=COLOR_YIELD),
            color=COLOR_YIELD,
            fontsize=FONT_ANNOT,
        )
    else:
        logger.warning("Yield_MPa missing; yield marker will not be drawn.")

    # --- UTS point ---------------------------------------------------------
    uts = properties.get('UTS_MPa')
    if uts:
        uts_idx = int(np.argmax(stress))
        uts_strain = strain[uts_idx] * 100.0
        ax.plot(uts_strain, uts,
                marker='s', markersize=7, color=COLOR_UTS,
                linestyle='None', zorder=5)
        ax.annotate(
            f'UTS = {uts:.1f} MPa',
            xy=(uts_strain, uts),
            xytext=(uts_strain - 3.5, uts * 0.9),
            arrowprops=dict(arrowstyle='->', color=COLOR_UTS),
            color=COLOR_UTS,
            fontsize=FONT_ANNOT,
        )
    else:
        logger.warning("UTS_MPa missing; UTS marker will not be drawn.")

    apply_base_style(ax,
                     title=f"Stress-Strain Curve: {material} ({condition})",
                     xlabel='Strain (%)',
                     ylabel='Stress (MPa)')
    ax.legend(loc='best')

    save_figure(fig, filepath)
    return filepath


# ---------------------------------------------------------------------------
# Plot 2: comparison of multiple conditions
# ---------------------------------------------------------------------------
def plot_comparison(curves, filepath, title='Stress-Strain Comparison'):
    """
    Overlay multiple stress-strain curves for visual comparison.

    Parameters
    ----------
    curves : list of dict
        Each entry:
            'df'    : cleaned DataFrame with 'Strain' and 'stress_MPa'
            'label' : str shown in the legend
            'color' : optional matplotlib color
    filepath : str
        Output PNG path.
    title : str
    """
    if not curves:
        logger.warning("No curves supplied; skipping comparison plot.")
        return None

    fig, ax = plt.subplots(figsize=FIG_SIZE_WIDE)
    for i, curve in enumerate(curves):
        df = curve['df']
        strain = df['Strain'].to_numpy() * 100.0
        stress = df['stress_MPa'].to_numpy()
        ax.plot(strain, stress,
                linewidth=1.5,
                label=curve.get('label', f'Condition {i+1}'),
                color=curve.get('color'))

    apply_base_style(ax, title, xlabel='Strain (%)', ylabel='Stress (MPa)')
    ax.legend(loc='best')
    save_figure(fig, filepath)
    return filepath


# ---------------------------------------------------------------------------
# Plot 3: property bar chart
# ---------------------------------------------------------------------------
def plot_properties_bar(props, filepath, material="Al-6061", condition="T6"):
    """
    Two-subplot bar chart: strength (YS, UTS) on the left,
    ductility (elongation) on the right.

    Strength and ductility have different units (MPa vs %), so they are
    kept on separate axes. Otherwise the elongation bar would be
    invisible next to the ~300 MPa strength bars.
    """
    ys = props['Yield_MPa']
    uts = props['UTS_MPa']
    elong = props['Elongation_pct']     # FIX: was 'Elong_%'

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # --- Left subplot: strength (MPa) ------------------------------------
    x_strength = np.arange(2)
    strength_values = [ys, uts]
    strength_labels = ['Yield', 'UTS']
    colors_strength = ['#1f77b4', '#ff7f0e']

    bars1 = ax1.bar(x_strength, strength_values, width=0.5, color=colors_strength)
    ax1.bar_label(bars1, fmt='%.1f', padding=3)
    ax1.set_xticks(x_strength)
    ax1.set_xticklabels(strength_labels)
    ax1.set_title('Strength', fontsize=12)
    ax1.set_ylabel('Stress (MPa)', fontsize=11)
    ax1.set_ylim(0, max(strength_values) * 1.2)   # 20% headroom for labels
    ax1.grid(False)

    # --- Right subplot: ductility (%) ------------------------------------
    x_elong = np.array([0])
    elong_values = [elong]

    bars2 = ax2.bar(x_elong, elong_values, width=0.5, color='#2ca02c')
    ax2.bar_label(bars2, fmt='%.1f', padding=3)
    ax2.set_xticks(x_elong)
    ax2.set_xticklabels(['Elongation'])
    ax2.set_title('Ductility', fontsize=12)
    ax2.set_ylabel('Elongation (%)', fontsize=11)
    ax2.set_ylim(0, max(elong_values) * 1.5)      # 50% headroom; bar is small
    ax2.grid(False)

    # Overall title and layout
    fig.suptitle(f'Mechanical Properties: {material} ({condition})', fontsize=14)

    save_figure(fig, filepath)                     # FIX: was '_save_figure'


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------
def generate_all_figures(processed_df, properties, output_dir,
                         material='Al-6061', condition='unknown'):
    """
    Produce every Stage 5 figure for a single specimen.

    Parameters
    ----------
    processed_df : pd.DataFrame
    properties : dict
    output_dir : str
        Directory where PNGs are written (created if missing).
    material, condition : str

    Returns
    -------
    dict
        Mapping {'curve': path, 'bar': path}.
    """
    os.makedirs(output_dir, exist_ok=True)

    curve_path = os.path.join(output_dir, f"stress_strain_{condition}.png")
    plot_curve(processed_df, properties, curve_path,
               material=material, condition=condition)

    bar_path = os.path.join(output_dir, f"properties_bar_{condition}.png")
    plot_properties_bar(properties, bar_path,
                        material=material, condition=condition)

    return {'curve': curve_path, 'bar': bar_path}