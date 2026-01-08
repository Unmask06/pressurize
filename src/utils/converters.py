"""Unit conversion utilities for temperature and pressure."""

from config.settings import ATM_PSI, PA_TO_PSI, PSI_TO_PA


def fahrenheit_to_kelvin(temp_f):
    """Convert temperature from Fahrenheit to Kelvin."""
    return (temp_f - 32) * 5/9 + 273.15

def psig_to_pa(pressure_psig):
    """Convert gauge pressure (psig) to absolute pressure (Pa)."""
    pressure_psia = pressure_psig + ATM_PSI
    return pressure_psia * PSI_TO_PA

def pa_to_psig(pressure_pa):
    """Convert absolute pressure (Pa) to gauge pressure (psig)."""
    pressure_psia = pressure_pa * PA_TO_PSI
    return pressure_psia - ATM_PSI
