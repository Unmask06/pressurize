"""Configuration constants for simulation and unit conversions.

This module defines all physical constants and conversion factors used
throughout the application for consistency and maintainability.
"""

# Universal Constants
R_UNIVERSAL = 8.31446  # Universal gas constant (J/mol·K)
ATM_PSI = 14.696  # Atmospheric pressure in psi

# Simulation Settings
TIME_STEP = 0.05  # Time step for simulation (seconds)

# Unit Conversion Factors
PSI_TO_PA = 6894.76  # psi to Pascal
PA_TO_PSI = 1 / PSI_TO_PA
INCH_TO_M = 0.0254  # inches to meters
FT3_TO_M3 = 0.0283168  # cubic feet to cubic meters
KG_S_TO_LB_HR = 7936.64  # kg/s to lb/hr
