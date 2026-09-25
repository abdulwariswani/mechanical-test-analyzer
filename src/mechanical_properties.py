import numpy as np


def compute_young_modulus(strain,stress):
        elastic_fraction = 0.05 # assumption taking 5% of the data as elastic region 

     

        max_strain = strain.max()
        cut_off  = max_strain * elastic_fraction

        # Create boolean to filter both the arrays 
        mask = strain <= cut_off 
        strain_elastic = strain[mask] # drop the False values 
        stress_elastic = stress[mask]

        if len(strain_elastic) <5 :
            raise ValueError(f"Insufficient data points ({len(strain_elastic)}) in the elastic region.")
        # linear regression slope = Δσ/Δε
        slope , intercept = np.polyfit(strain_elastic,stress_elastic,1)

        return slope  # MPa

#def compute_yield_strength(strain, stress, E_MPa, off_set = 0.02):
 #   #Construct offset line: σ_offset = E * (ε - 0.002)
  #  offset_line = E_MPa * (strain - off_set)


def compute_uts(stress):
    """ultimate tensile strength  = max stress"""
    return stress.max()
     

def compute_elongation(strain):
    """Elongation at fracture = max strain  """
    return strain.max()

def compute_toughness():



def compute_properties(processed_df):

    # Convert columns to NumPy arrays for speed
    strain = processed_df['Strain'].to_numpy()
    stress = processed_df['Stress'].to_numpy()
    E_MPa = compute_young_modulus(strain,stress)
    #YS = compute_yield_strength(strain,stress,E_MPa)
    UTS = compute_uts(stress)
    elong = compute_elongation(strain)
    #tough = compute_toughness(strain, stress)

    return {
         'E_GPa':        E_MPa / 1000.0,
        #'Yield_MPa':    YS,
        'UTS_MPa':      UTS,
        'Elongation_pct': elong * 100.0,
        #'Toughness_MJ_m3': tough,
    }