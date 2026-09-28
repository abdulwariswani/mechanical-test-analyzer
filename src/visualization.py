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
    
