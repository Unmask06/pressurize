"""Configuration constants for simulation and unit conversions."""

from typing import Final

# Universal Constants
R_UNIVERSAL: Final[float] = 8.31446  # Universal gas constant (J/mol·K)
ATM_PSI: Final[float] = 14.696  # Atmospheric pressure in psi

# Simulation Settings
TIME_STEP: Final[float] = 0.5  # Time step for simulation (seconds)
MAX_SIMULATION_TIME_FIXED: Final[float] = (
    10000  # Max simulation time for fixed opening mode (seconds)
)

