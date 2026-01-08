"""Unit conversion utilities for temperature and pressure.

This module provides conversion functions between different units commonly used
in engineering calculations, particularly for gas flow simulations.
"""

from config.settings import ATM_PSI, PA_TO_PSI, PSI_TO_PA


def fahrenheit_to_kelvin(temp_f):
    """Convert temperature from Fahrenheit to Kelvin.
    
    Args:
        temp_f (float): Temperature in degrees Fahrenheit (°F).
    
    Returns:
        float: Temperature in Kelvin (K).
    
    Notes:
        Formula: K = (°F - 32) × 5/9 + 273.15
        
        Absolute zero: -459.67°F = 0 K
        Freezing point of water: 32°F = 273.15 K
        Boiling point of water: 212°F = 373.15 K
    
    Examples:
        >>> fahrenheit_to_kelvin(32)
        273.15
        >>> fahrenheit_to_kelvin(70)
        294.26
        >>> fahrenheit_to_kelvin(-459.67)
        0.0
    """
    return (temp_f - 32) * 5/9 + 273.15

def psig_to_pa(pressure_psig):
    """Convert gauge pressure (psig) to absolute pressure (Pa).
    
    Args:
        pressure_psig (float): Gauge pressure in pounds per square inch gauge (psig).
            Gauge pressure is measured relative to atmospheric pressure.
    
    Returns:
        float: Absolute pressure in Pascals (Pa).
    
    Notes:
        Conversion process:
        1. Add atmospheric pressure to convert gauge to absolute (psia)
        2. Convert from psia to Pascals
        
        Formula: Pa = (psig + 14.696) × 6894.76
        
        Standard atmospheric pressure = 14.696 psia = 101,325 Pa
    
    Examples:
        >>> psig_to_pa(0)
        101325.0  # Atmospheric pressure
        >>> psig_to_pa(14.696)
        202650.0  # Twice atmospheric pressure
        >>> psig_to_pa(100)
        791,000  # Typical industrial pressure
    """
    pressure_psia = pressure_psig + ATM_PSI
    return pressure_psia * PSI_TO_PA

def pa_to_psig(pressure_pa):
    """Convert absolute pressure (Pa) to gauge pressure (psig).
    
    Args:
        pressure_pa (float): Absolute pressure in Pascals (Pa).
    
    Returns:
        float: Gauge pressure in pounds per square inch gauge (psig).
    
    Notes:
        Conversion process:
        1. Convert from Pascals to absolute psi (psia)
        2. Subtract atmospheric pressure to get gauge pressure
        
        Formula: psig = (Pa / 6894.76) - 14.696
        
        Gauge pressure can be negative (vacuum conditions).
    
    Examples:
        >>> pa_to_psig(101325)
        0.0  # Atmospheric pressure = 0 psig
        >>> pa_to_psig(202650)
        14.696  # Twice atmospheric
        >>> pa_to_psig(50000)
        -7.3  # Below atmospheric (vacuum)
    """
    pressure_psia = pressure_pa * PA_TO_PSI
    return pressure_psia - ATM_PSI
