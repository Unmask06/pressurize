"""Configuration constants for simulation and unit conversions."""

from typing import Final

# Universal Constants
R_UNIVERSAL: Final[float] = 8.31446  # Universal gas constant (J/mol·K)
ATM_PSI: Final[float] = 14.696  # Atmospheric pressure in psi

# Simulation Settings
TIME_STEP: Final[float] = 0.05  # Time step for simulation (seconds)
MAX_SIMULATION_TIME_FIXED: Final[float] = (
    10000  # Max simulation time for fixed opening mode (seconds)
)

# Unit Conversion Factors
PSI_TO_PA: Final[float] = 6894.76  # psi to Pascal
PA_TO_PSI: Final[float] = 1 / PSI_TO_PA
INCH_TO_M: Final[float] = 0.0254  # inches to meters
FT3_TO_M3: Final[float] = 0.0283168  # cubic feet to cubic meters
KG_S_TO_LB_HR: Final[float] = 7936.64  # kg/s to lb/hr
