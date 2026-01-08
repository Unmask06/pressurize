"""Physics calculations for gas flow through valves."""

import numpy as np

from config.settings import R_UNIVERSAL


def calculate_critical_pressure_ratio(k):
    """Calculate the critical pressure ratio for sonic/choked flow.
    
    Formula: r_c = (2/(k+1))^(k/(k-1))
    """
    return (2 / (k + 1)) ** (k / (k - 1))

def calculate_choked_flow(Cd, A, P_up, k, M, Z, T):
    """Calculate mass flow rate for choked (sonic) flow."""
    term1 = (k * M) / (Z * R_UNIVERSAL * T)
    term2 = (2 / (k + 1)) ** ((k + 1) / (k - 1))
    return Cd * A * P_up * np.sqrt(term1 * term2)

def calculate_subsonic_flow(Cd, A, P_up, P_down, k, M, Z, T):
    """Calculate mass flow rate for subsonic flow."""
    r = P_down / P_up
    
    # Prevent negative values under square root
    if r >= 1:
        return 0.0
    
    term1 = (2 * M) / (Z * R_UNIVERSAL * T)
    term2 = k / (k - 1)
    term3 = r ** (2/k) - r ** ((k+1)/k)
    
    if term3 <= 0:
        return 0.0
    
    return Cd * A * P_up * np.sqrt(term1 * term2 * term3)

def calculate_mass_flow_rate(Cd, A, P_up, P_down, k, M, Z, T):
    """Calculate mass flow rate through valve with automatic flow regime detection.
    
    Automatically determines whether flow is choked (sonic) or subsonic based on
    the pressure ratio, then applies the appropriate flow equation.
    
    Args:
        Cd: Discharge coefficient (dimensionless), typically 0.6-0.9.
        A: Effective flow area in m².
        P_up: Upstream absolute pressure in Pa.
        P_down: Downstream absolute pressure in Pa.
        k: Heat capacity ratio (Cp/Cv).
        M: Molar mass in kg/mol.
        Z: Compressibility factor (dimensionless).
        T: Gas temperature in Kelvin.
    
    Returns:
        Mass flow rate in kg/s. Returns 0 if pressures are equalized.
    """
    if P_down >= P_up:
        return 0.0
    
    r = P_down / P_up
    r_c = calculate_critical_pressure_ratio(k)
    
    if r <= r_c:
        # Choked flow
        return calculate_choked_flow(Cd, A, P_up, k, M, Z, T)
    else:
        # Subsonic flow
        return calculate_subsonic_flow(Cd, A, P_up, P_down, k, M, Z, T)

def calculate_dp_dt(Z, T, V, M, mass_flow):
    """Calculate rate of pressure change using the Real Gas Law.
    
    Derives the pressure change rate from mass conservation and the real gas
    equation of state (PV = ZnRT).
    
    Formula: dP/dt = (Z·R·T)/(V·M)·ṁ
    """
    return (Z * R_UNIVERSAL * T) / (V * M) * mass_flow
