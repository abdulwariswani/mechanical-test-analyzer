import os 
import logging 
import numpy as np
import matplotlib
matplotlib.use('Agg') # headless backend , No GUI needed 

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

# CONStANTS 
FIG_DPI = 150 # Dots per inch 
FIG_SIZE_WIDE = (10,6)
FIG_SIZE_BAR  = (10,6)
COLOR_CURVE = '#1f77b4'
COLOR_YIELD = 'red' # yield strength
COLOR_UTS = 'orange' # UTS
GRID_ON = False
FONT_TITLE = 13 # text size of the main title 
FONT_LABEL = 11 # text size of X & Y labels


# style the matplot axes.
def apply_base_style(ax, title, xlabel, ylabel):
    ax.set_title(title, frontsize=FONT_LABEL)
    ax.set_xlabel(xlabel, fontsize=FONT_LABEL)
    ax.set_ylabel(ylabel, fontsize=FONT_LABEL)
    if GRID_ON: ax.grid(True, alpha=0.3)
    else: ax.grid(False)
    ax.legend(loc='best')
    return ax


# save plot graphs. 
def save_figure(fig,filepath):
    # filepath is a full path ending in .png 
    parent_dir = os.path.dirname(filepath)
    if  parent_dir:
        os.makedirs(parent_dir,exist_ok=True)
    # everything fits the frame without overlapping or getting cut off
    fig.tight_layout()
    # crops away useless whitespaces. 
    fig.savefig(filepath, dpi=FIG_DPI, bbox_inches='tight')
    # clears graphs from RAM
    plt.close(fig)
    logger.info(f"saved figure: {filepath}")

def plot_curve(processed_df, properties, filepath, material, condition):
    strain = processed_df['Strain'].to_numpy()
    stress = processed_df['stress_MPa']

    # guard: need atleast 2 points to plot. 
    if len(strain) <2:
        logger.warning('Not ')


    #__create figure and axes__
    fig, ax = plt.subplots(figsize=FIG_SIZE_WIDE)

    # Plot the raw curve 
    ax.plot(strain*100,stress,color=COLOR_CURVE, linewidth = 1.5, label='Stress-Strain')

    # Mark yield point 
    yield_stress = properties['Yield_MPa']
    if yield_stress:
        yield_strain = yield_stress/(properties['E_GPa'] *1000)
        if yield_strain:
            ax.plot(yield_strain*100, yield_stress, marker='o', markersize=7,color=COLOR_YIELD, zorder=5, label=f'Yield (0.2% offset) = {yield_stress:.1f} MPa')


        # Annotate with arrow 
        ax.annotate(f'YS={yield_stress:.1f}MPa',
                    xy=(yield_strain *100,yield_stress),
                    xytest=(yield_strain*100+1.5,yield_stress * 0.75)
                    arrowprops=dict(arrowstyle='->', color=COLOR_YIELD),color=COLOR_YIELD, fontsize=9)
    else:
        logger.warning("Yield_Strain not present; cannot place YS dot.")

    # mark UTS point. 
    uts = properties['UTS_MPa']
    if uts:
        uts_idx = np.argmax(stress)
        uts_strain = strain[uts_idx] *100
        ax.plot(uts_strain,uts,marker='s', markersize=7,color=COLOR_UTS, zorder=5, label=f'UTS={uts:.1f} MPa',xy=(uts_strain, uts),xytext=(uts_strain - 3.0, uts * 0.92),arrowprops=dict(arrowstyle='->',color=COLOR_UTS),color=COLOR_UTS, fontsize=9)

    # Label , title, style
    title = f"Stress - Strain Curve: {material} ({condition})"
    apply_base_style(ax, title, xlabel='Strain (%)', ylabel='Stress (MPa)')

    # save 
    save_figure(fig, filepath)




def plot_properties_bar(properties,filepath,material='Al-6061',condition ='T6'):

    if len(properties)==0:
        logger.warning("No properties to plot: skipping bar chart")
        return None 


    # Extract metric arrays
    ys_value = properties['Yield_MPa']
    uts_value = properties['UTS_MPa']
    elong_value = properties['Elongation_percentage']

     # --- 2. Pair labels with values and colors ---
    names  = ['Yield (MPa)', 'UTS (MPa)', 'Elongation (%)']
    values = [ys_value, uts_value, elong_value]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    # X positions 
    x = np.arrange(len(names))

    # Create Figure
    fig, ax = plt.subplots(figsize=(8, 5))

    # Draw bars 
    bars  = ax.bar(x, values, width=0.5, color=colors)

    # Value labels on top of each bar
    ax.bar_label(bars,fmt='%.1f', padding=3)



    # style

    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_title(f"Mechanical Properties: {material}({condition})")
    ax.set_ylabel('Value')
    ax.grid(False)

    # Save 
    save_figure(fig, filepath)



    def generate_all_figures(processed_df,properties,output_dir, material, condition):
        os.makedirs(output_dir, exist_ok=True)
        fig_path = os.path.join(output_dir,
                            f"stress_strain_{condition}.png")
    plot_curve(processed_df, props, fig_path,
               material=material, condition=condition)


        return fig_path