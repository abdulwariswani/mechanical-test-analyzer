import logging 
import numpy as np
logger = logging.getLogger(__name__)
def compute_work_hardening(processed_df,properties):
    # Extract the data
    strain = processed_df['Strain'].values 
    stress = processed_df['stress_MPa'].values


    # Get the boundary for plastic region 
    yield_strain = properties['yield_strain']
    uts_strain = properties['uts_strain']


    # Gaurd we dont have the boudary condition we can slice the plastic region
    if yield_strain is None or uts_strain is None:
        logger.warning("Missing yield or UTS stain. Cannot compute work hardening. ")
        return {'n':None , 'K_MPa':None, 'R2':None }


    # SLice the plastic region 
    # Plastic region is between yield strain and UTS strain 
    # (Beyond UTS is necking, which doesn't follow bulk holloman law)
    mask = (strain >= yield_strain) &(strain <= uts_strain)
    plastic_strain = strain[mask]
    plastic_stress = stress[mask]

    # Gaurd: Need at least 3 points to a line 
    if len(plastic_strain) < 3:
        logger.warning("Not enough points in plastic region to fit. ")
        return {'n': None, 'K_MPa': None, 'R2': None}

    # Log-Log transforma 
    # σ = K * ε^n  ->  log(σ) = log(K) + n * log(ε)
    # We use natural log (np.log) but base 10 (np.log10) works too as long as we are consistent.
    log_strain = np.log(plastic_strain)
    log_stress = np.log(plastic_stress)


    # --- linear regression ---
    # np.polyfit(x,y,1) returns [slope, intercept]
    # Here, slope = n, intercept = log(K)
    slope , intercept = np.polyfit(log_strain, log_stress, 1)
    n = slope
    K = np.exp(intercept) # Convert log(K) back to k


        # --- Calculate R² (Goodness of Fit) ---
    # R² tells us how well the power law fits the data.
    
    # 1. Generate the predicted log-stress values using the linear regression model (y = mx + c)
    y_pred = slope * log_strain + intercept
    
    # 2. Residual Sum of Squares: Measures the total squared error between the actual data and our model's predictions
    ss_res = np.sum((log_stress - y_pred)**2)
    
    # 3. Total Sum of Squares: Measures the baseline variance/spread of the actual data around its own mean
    ss_tot = np.sum((log_stress - np.mean(log_stress)) ** 2)
    
    # 4. R² Score: Compares the model's error to the baseline variance (closer to 1.0 means a better fit)
    r2 = 1 - (ss_res / ss_tot)


    # Quality Check 
    if r2  < 0.95:
        logger.warning(f"Plastic region fit R^2 is low ({r2:.3f}. Results may be unreliable.)")

    # Sanity check for AL alloys. 
    # Typical n for AL alloys is 0.1 to 0.4
    if n < 0.05 or n>0.5:
        logger.warning(f"Work-hardening exponent n={n:.3f} is outside typical range for Al alloys.")

    return {'n': n, 'K_MPa': K, 'R2': r2}
