"""Dynamic valve pressurization simulation engine.

This module implements the core simulation logic for modeling gas flow through
a valve into a downstream vessel. It handles various valve opening modes,
property calculation methods, and integrates the physics equations over time.
"""

import numpy as np
import pandas as pd

from config.settings import FT3_TO_M3, INCH_TO_M, KG_S_TO_LB_HR, TIME_STEP
from src.core.physics import (
    calculate_critical_pressure_ratio,
    calculate_dp_dt,
    calculate_mass_flow_rate,
)
from src.core.properties import GasState
from src.utils.converters import fahrenheit_to_kelvin, pa_to_psig, psig_to_pa


def run_simulation(P_up_psig, P_down_init_psig, volume_ft3, valve_id_inch, 
                   opening_time_s, temp_f, molar_mass, z_factor, k_ratio,
                   discharge_coeff=0.65, opening_mode='linear', k_curve=4.0, dt=TIME_STEP,
                   property_mode='manual', composition=None):
    """Run the valve pressurization simulation.
    
    Simulates the dynamic pressurization of a downstream vessel as gas flows through
    a valve that opens over time. The simulation integrates mass flow and pressure
    change using timestep-based numerical methods.
    
    Args:
        P_up_psig (float): Upstream pressure in pounds per square inch gauge (psig).
        P_down_init_psig (float): Initial downstream pressure in psig.
        volume_ft3 (float): Downstream vessel volume in cubic feet (ft³).
        valve_id_inch (float): Valve inner diameter in inches.
        opening_time_s (float): Time for valve to fully open in seconds.
        temp_f (float): Gas temperature in degrees Fahrenheit (°F).
        molar_mass (float): Gas molar mass in g/mol (used when property_mode='manual').
        z_factor (float): Compressibility factor, dimensionless (used when property_mode='manual').
        k_ratio (float): Heat capacity ratio Cp/Cv (used when property_mode='manual').
        discharge_coeff (float, optional): Valve discharge coefficient. Defaults to 0.65.
        opening_mode (str, optional): Valve opening behavior. Defaults to 'linear'.
            Options:
            - 'linear': Linear opening over opening_time_s
            - 'exponential': Exponential (convex) opening profile
            - 'quick_opening': Quick opening profile (steep initial opening)
            - 'fixed': Fully open instantly (ignores opening_time_s)
        k_curve (float, optional): Curve steepness for exponential/quick_opening modes.
            Defaults to 4.0.
        dt (float, optional): Simulation timestep in seconds. Defaults to TIME_STEP.
        property_mode (str, optional): Property calculation method. Defaults to 'manual'.
            Options:
            - 'manual': Use provided molar_mass, z_factor, and k_ratio values
            - 'composition': Derive properties dynamically from gas composition using thermo library
        composition (str, optional): Gas composition string for 'composition' mode.
            Format: "Component1=fraction1, Component2=fraction2, ..."
            Example: "Methane=0.9, Ethane=0.1"
    
    Returns:
        pandas.DataFrame: Simulation results with columns:
            - time: Time in seconds
            - pressure_psig: Downstream pressure in psig
            - upstream_pressure_psig: Upstream pressure in psig (constant)
            - flowrate_lb_hr: Mass flow rate in lb/hr
            - valve_opening_pct: Valve opening percentage (0-100%)
            - flow_regime: Flow regime ('None', 'Choked', 'Subsonic', or 'Equilibrium')
            
            Additional columns when property_mode='composition':
            - Z_factor: Compressibility factor at each timestep
            - k_ratio: Heat capacity ratio at each timestep
            - molar_mass_g_mol: Molar mass in g/mol at each timestep
    
    Notes:
        The simulation continues until:
        - Pressures equalize (P_down >= P_up) AND time >= opening_time_s
        - Maximum simulation time is reached (10× opening_time_s or 3600s for fixed mode)
        
        All internal calculations use SI units (Pa, K, m, kg, s).
        Input and output use engineering units (psig, °F, ft³, lb/hr).
    
    Examples:
        >>> # Basic simulation with manual properties
        >>> df = run_simulation(
        ...     P_up_psig=500, P_down_init_psig=0, volume_ft3=100,
        ...     valve_id_inch=2, opening_time_s=5, temp_f=70,
        ...     molar_mass=29, z_factor=1.0, k_ratio=1.4
        ... )
        
        >>> # Simulation with composition-based properties
        >>> df = run_simulation(
        ...     P_up_psig=2800, P_down_init_psig=800, volume_ft3=62,
        ...     valve_id_inch=3.7, opening_time_s=30, temp_f=55,
        ...     molar_mass=16.9, z_factor=0.771, k_ratio=1.9,
        ...     property_mode='composition',
        ...     composition="Methane=0.9, Ethane=0.1"
        ... )
    """
    # Convert to SI units
    P_up = psig_to_pa(P_up_psig)
    P_down = psig_to_pa(P_down_init_psig)
    V = volume_ft3 * FT3_TO_M3
    valve_radius = (valve_id_inch * INCH_TO_M) / 2
    A_max = np.pi * valve_radius ** 2
    T = fahrenheit_to_kelvin(temp_f)
    Cd = discharge_coeff
    
    # Initialize gas properties based on mode
    if property_mode == 'composition' and composition:
        gas_state = GasState(composition)
        # Get initial properties at downstream pressure
        props = gas_state.get_properties(P_down, T)
        M = props.M / 1000.0  # Convert g/mol to kg/mol
        Z = props.Z
        k = props.k
    else:
        # Manual mode - use provided values
        gas_state = None
        M = molar_mass / 1000.0  # Convert g/mol to kg/mol
        Z = z_factor
        k = k_ratio
    
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
    
    # Add computed property columns if in composition mode
    if property_mode == 'composition':
        results['Z_factor'] = [round(Z, 4)]
        results['k_ratio'] = [round(k, 4)]
        results['molar_mass_g_mol'] = [round(M * 1000, 2)]
    
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
        
        # Update gas properties dynamically in composition mode
        if gas_state is not None:
            props = gas_state.get_properties(P_down, T)
            M = props.M / 1000.0  # Convert g/mol to kg/mol
            Z = props.Z
            k = props.k
        
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
        
        # Store computed properties if in composition mode
        if property_mode == 'composition':
            results['Z_factor'].append(round(Z, 4))
            results['k_ratio'].append(round(k, 4))
            results['molar_mass_g_mol'].append(round(M * 1000, 2))
        
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
