import numpy as np
import logging

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

def compute_yield_strength(strain, stress, E_MPa, off_set = 0.002):
    # Construct offset line: σ_offset = E * (ε - 0.002)
    offset_line = E_MPa * (strain - off_set)

    # find where curve crosses offset line (stress - offset_line "sign change ")
    diff = stress - offset_line

    # find indices where signs change from postive to negative 
    crossings  = np.where((diff[:-1] >0) & (diff[1:] <= 0))[0]

    if len(crossings) == 0 :
        logging.warning("No yield crossing found: returning UTS as fallback")
        return stress.max() # Fallback scaler



 # Linear interpolation to get the exact SINGLE stress value
    idx = crossings[0]
    d1 = diff[idx]
    d2 =diff[idx+1]

    stress_yield = stress[idx] + (-d1/(d2-d1)) * (stress[idx+1] - stress[idx])

    return stress_yield


    


def compute_uts(stress):
    """ultimate tensile strength  = max stress"""
    return stress.max()
     

def compute_elongation(strain):
    """Elongation at fracture = max strain  """
    return strain.max()

def compute_toughness(strain,stress):
    """
     Total area under the stress-strain curve (up to the fracture)
     stress in MPa and strain unitless , toughness(MJ/m3)
    """
    area =np.trapezoid(stress,strain)
    return area
    

     



def compute_properties(processed_df):

    # Convert columns to NumPy arrays for speed
    strain = processed_df['Strain'].to_numpy()
    stress = processed_df['stress_MPa'].to_numpy()
    E_MPa = compute_young_modulus(strain,stress)
    YS = compute_yield_strength(strain,stress,E_MPa)
    UTS = compute_uts(stress)
    elong = compute_elongation(strain)
    tough = compute_toughness(strain, stress)

    return {
        'E_GPa':        E_MPa / 1000.0,
        'Yield_MPa':    YS,
        'UTS_MPa':      UTS,
        'Elongation_pct': elong * 100.0,
        'Toughness_MJ_m3': tough,
    }