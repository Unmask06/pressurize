import numpy as np
import pandas as pd

from config.settings import FT3_TO_M3, INCH_TO_M, KG_S_TO_LB_HR
from src.core.physics import (
    calculate_critical_pressure_ratio,
    calculate_dp_dt,
    calculate_mass_flow_rate,
)
from src.utils.converters import fahrenheit_to_kelvin, pa_to_psig, psig_to_pa


def run_simulation(P_up_psig, P_down_init_psig, volume_ft3, valve_id_inch, 
                   opening_time_s, temp_f, molar_mass, z_factor, k_ratio,
                   discharge_coeff=0.65, opening_mode='linear', k_curve=4.0, dt=0.2):
    """
    Run the valve pressurization simulation.
    
    Opening modes:
    - 'linear': Valve opens linearly over opening_time_s
    - 'exponential': Valve opens exponentially (convex) over opening_time_s
    - 'fixed': Valve is fully open instantly (ignores opening_time_s)
    """
    # Convert to SI units
    P_up = psig_to_pa(P_up_psig)
    P_down = psig_to_pa(P_down_init_psig)
    V = volume_ft3 * FT3_TO_M3
    valve_radius = (valve_id_inch * INCH_TO_M) / 2
    A_max = np.pi * valve_radius ** 2
    T = fahrenheit_to_kelvin(temp_f)
    M = molar_mass / 1000.0  # Convert g/mol to kg/mol
    Z = z_factor
    k = k_ratio
    Cd = discharge_coeff
    
    # Initialize results storage
    # For fixed mode, valve starts at 100%; otherwise starts at 0
    initial_opening = 100.0 if opening_mode == 'fixed' else 0
    results = {
        'time': [0],
        'pressure_psig': [P_down_init_psig],
        'upstream_pressure_psig': [P_up_psig],
        'flowrate_lb_hr': [0],
        'valve_opening_pct': [initial_opening],
        'flow_regime': ['None']
    }
    
    t = 0
    
    # Simulation loop - continue until equilibrium or max time
    # If fixed mode or opening time is 0, use a reasonable safety limit
    if opening_mode == 'fixed' or opening_time_s <= 0:
        max_time = 3600  # Safety timeout for fixed/instantaneous opening
    else:
        max_time = opening_time_s * 10
    
    while t < max_time:
        t += dt
        
        # Calculate current valve opening fraction based on mode
        if opening_mode == 'fixed':
            opening_fraction = 1.0  # Fully open instantly
        elif opening_mode == 'exponential':
            if opening_time_s > 0:
                # Exponential growth: Slow start, steep end
                # Formula: (e^(k*x) - 1) / (e^k - 1) where x = t/T
                ratio = min(t / opening_time_s, 1.0)
                opening_fraction = (np.exp(k_curve * ratio) - 1) / (np.exp(k_curve) - 1)
            else:
                opening_fraction = 1.0
        elif opening_mode == "quick_opening":
            if opening_time_s > 0:
                ratio = min(t / opening_time_s, 1.0)
                
                # k_curve controls the "steepness" of the initial jump.
                # Suggested value for your drawing: k_curve = 5.0
                numerator = 1 - np.exp(-k_curve * ratio)
                denominator = 1 - np.exp(-k_curve)
                
                opening_fraction = numerator / denominator
            else:
                opening_fraction = 1.0
        else:  # linear (default)
            if opening_time_s > 0:
                opening_fraction = min(t / opening_time_s, 1.0)
            else:
                opening_fraction = 1.0
            
        A = A_max * opening_fraction
        
        # Determine flow regime
        if P_down >= P_up:
            massflow_kgs = 0
            regime = 'Equilibrium'
        else:
            r = P_down / P_up
            r_c = calculate_critical_pressure_ratio(k)
            
            if r <= r_c:
                regime = 'Choked'
            else:
                regime = 'Subsonic'
            
            # Calculate mass flow rate
            massflow_kgs = calculate_mass_flow_rate(Cd, A, P_up, P_down, k, M, Z, T)
        
        # Calculate pressure increment
        dP = calculate_dp_dt(Z, T, V, M, massflow_kgs) * dt
        P_down += dP
        
        # Cap downstream pressure at upstream pressure
        if P_down >= P_up:
            P_down = P_up
        
        # Convert and store results
        P_down_psig = pa_to_psig(P_down)
        flowrate_lb_hr = massflow_kgs * KG_S_TO_LB_HR
        
        results['time'].append(round(t, 2))
        results['pressure_psig'].append(round(P_down_psig, 2))
        results['upstream_pressure_psig'].append(P_up_psig)
        results['flowrate_lb_hr'].append(round(flowrate_lb_hr, 2))
        results['valve_opening_pct'].append(round(opening_fraction * 100, 1))
        results['flow_regime'].append(regime)
        
        # Stop if pressures are equalized AND time has passed the opening duration
        # This ensures the valve curve is fully plotted even if equilibrium is reached early
        if P_down >= P_up and t >= opening_time_s:
            break
            
        # Check for equilibrium (flow rate < 0.1% of peak) - redundant but kept for safety logic for now, 
        # though the pressure check above likely catches it first.
        # if len(results['flowrate_lb_hr']) > 10:
        #    peak_flow = max(results['flowrate_lb_hr'])
        #    if peak_flow > 0 and flowrate_lb_hr < 0.001 * peak_flow:
        #        break
    
    return pd.DataFrame(results)
