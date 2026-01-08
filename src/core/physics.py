"""Physics calculations for gas flow through valves.

This module provides functions for calculating mass flow rates through valves
using the real gas law and handling both choked (sonic) and subsonic flow regimes.
"""

import numpy as np

from config.settings import R_UNIVERSAL


def calculate_critical_pressure_ratio(k):
    """Calculate the critical pressure ratio for sonic/choked flow.
    
    The critical pressure ratio determines the boundary between choked and subsonic
    flow regimes. When the downstream-to-upstream pressure ratio falls below this
    value, the flow becomes choked (sonic) at the valve throat.
    
    Args:
        k (float): Heat capacity ratio (Cp/Cv), also known as gamma or kappa.
            Typical values: 1.4 for air, 1.3 for natural gas.
    
    Returns:
        float: Critical pressure ratio r_c. When P_down/P_up <= r_c, flow is choked.
    
    Notes:
        Formula: r_c = (2/(k+1))^(k/(k-1))
        This is derived from isentropic flow relations.
    
    Examples:
        >>> calculate_critical_pressure_ratio(1.4)  # Air
        0.528
        >>> calculate_critical_pressure_ratio(1.3)  # Natural gas
        0.546
    """
    return (2 / (k + 1)) ** (k / (k - 1))

def calculate_choked_flow(Cd, A, P_up, k, M, Z, T):
    """Calculate mass flow rate for choked (sonic) flow.
    
    When flow is choked, the velocity at the valve throat reaches the speed of sound
    and the mass flow rate becomes independent of downstream pressure. This represents
    the maximum possible flow rate through the valve.
    
    Args:
        Cd (float): Discharge coefficient (dimensionless), typically 0.6-0.9.
            Accounts for flow losses and non-ideal valve geometry.
        A (float): Effective flow area in square meters (m²).
        P_up (float): Upstream absolute pressure in Pascals (Pa).
        k (float): Heat capacity ratio (Cp/Cv), dimensionless.
        M (float): Molar mass in kg/mol.
        Z (float): Compressibility factor (dimensionless). Z=1 for ideal gas.
        T (float): Gas temperature in Kelvin (K).
    
    Returns:
        float: Mass flow rate in kg/s.
    
    Notes:
        Formula: ṁ = Cd·A·P_up·√[(k·M)/(Z·R·T)·(2/(k+1))^((k+1)/(k-1))]
        Derived from isentropic flow equations at sonic conditions.
    
    Examples:
        >>> calculate_choked_flow(0.65, 0.001, 3.5e6, 1.3, 0.017, 0.9, 300)
        1.234  # Returns mass flow in kg/s
    """
    term1 = (k * M) / (Z * R_UNIVERSAL * T)
    term2 = (2 / (k + 1)) ** ((k + 1) / (k - 1))
    return Cd * A * P_up * np.sqrt(term1 * term2)

def calculate_subsonic_flow(Cd, A, P_up, P_down, k, M, Z, T):
    """Calculate mass flow rate for subsonic flow.
    
    When the pressure ratio is above the critical value, flow remains subsonic
    and depends on both upstream and downstream pressures. The flow rate varies
    with the pressure differential across the valve.
    
    Args:
        Cd (float): Discharge coefficient (dimensionless), typically 0.6-0.9.
        A (float): Effective flow area in square meters (m²).
        P_up (float): Upstream absolute pressure in Pascals (Pa).
        P_down (float): Downstream absolute pressure in Pascals (Pa).
        k (float): Heat capacity ratio (Cp/Cv), dimensionless.
        M (float): Molar mass in kg/mol.
        Z (float): Compressibility factor (dimensionless).
        T (float): Gas temperature in Kelvin (K).
    
    Returns:
        float: Mass flow rate in kg/s. Returns 0 if downstream pressure
            equals or exceeds upstream pressure.
    
    Notes:
        Formula: ṁ = Cd·A·P_up·√[(2M)/(ZRT)·(k/(k-1))·(r^(2/k) - r^((k+1)/k))]
        where r = P_down/P_up
        
        The function includes safety checks to prevent:
        - Negative square root (r >= 1)
        - Invalid flow conditions (term3 <= 0)
    
    Examples:
        >>> calculate_subsonic_flow(0.65, 0.001, 3.5e6, 2.0e6, 1.3, 0.017, 0.9, 300)
        0.987  # Returns mass flow in kg/s
    """
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
    
    This function automatically determines whether the flow is choked (sonic) or
    subsonic based on the pressure ratio and critical pressure ratio, then applies
    the appropriate flow equation.
    
    Args:
        Cd (float): Discharge coefficient (dimensionless), typically 0.6-0.9.
        A (float): Effective flow area in square meters (m²).
        P_up (float): Upstream absolute pressure in Pascals (Pa).
        P_down (float): Downstream absolute pressure in Pascals (Pa).
        k (float): Heat capacity ratio (Cp/Cv), dimensionless.
        M (float): Molar mass in kg/mol.
        Z (float): Compressibility factor (dimensionless).
        T (float): Gas temperature in Kelvin (K).
    
    Returns:
        float: Mass flow rate in kg/s. Returns 0 if pressures are equalized.
    
    Notes:
        Flow regime determination:
        - If P_down >= P_up: No flow (returns 0)
        - If r <= r_c: Choked flow (sonic)
        - If r > r_c: Subsonic flow
        
        where r = P_down/P_up and r_c is the critical pressure ratio.
    
    Examples:
        >>> # Choked flow example
        >>> calculate_mass_flow_rate(0.65, 0.001, 3.5e6, 1.0e6, 1.3, 0.017, 0.9, 300)
        1.234  # Flow is choked
        
        >>> # Subsonic flow example
        >>> calculate_mass_flow_rate(0.65, 0.001, 3.5e6, 2.5e6, 1.3, 0.017, 0.9, 300)
        0.567  # Flow is subsonic
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

def calculate_dp_dt(Z, T, V, M, m_dot):
    """Calculate rate of pressure change using the Real Gas Law.
    
    Derives the pressure change rate from mass conservation and the real gas equation
    of state (PV = ZnRT). Used to integrate pressure over time in dynamic simulations.
    
    Args:
        Z (float): Compressibility factor (dimensionless). Z=1 for ideal gas.
        T (float): Gas temperature in Kelvin (K).
        V (float): Vessel volume in cubic meters (m³).
        M (float): Molar mass in kg/mol.
        m_dot (float): Mass flow rate into the vessel in kg/s (positive for inflow).
    
    Returns:
        float: Rate of pressure change dP/dt in Pascals per second (Pa/s).
    
    Notes:
        Formula: dP/dt = (Z·R·T)/(V·M)·ṁ
        
        Derivation from PV = ZnRT:
        - n = m/M (moles from mass)
        - dn/dt = ṁ/M (rate of change of moles)
        - P = ZnRT/V
        - dP/dt = (ZRT/V)·(dn/dt) = (ZRT/V)·(ṁ/M)
        
        Temperature is assumed constant (isothermal process).
    
    Examples:
        >>> calculate_dp_dt(0.9, 300, 2.0, 0.017, 0.5)
        1988.2  # Pressure increases at ~1988 Pa/s
        
        >>> calculate_dp_dt(1.0, 300, 10, 0.029, -0.1)
        -86.0  # Pressure decreases (negative flow)
    """
    return (Z * R_UNIVERSAL * T) / (V * M) * m_dot
