"""Configuration constants for simulation and unit conversions."""

from typing import Final

# Universal Constants
R_UNIVERSAL: Final[float] = 8.31446  # Universal gas constant (J/mol·K)
ATM_PSI: Final[float] = 14.696  # Atmospheric pressure in psi

# ISA/IEC 60534 Cv Sizing Constants
N6_FPS: Final[float] = 63.338  # ISA sizing constant for lb/hr, psia, lb/ft³

# Unit Conversion: SI ↔ FPS (for Cv calculations)
PA_TO_PSIA: Final[float] = 1.0 / 6894.757  # Pascal → psi absolute
KGM3_TO_LBFT3: Final[float] = 0.062428  # kg/m³ → lb/ft³
LBHR_TO_KGS: Final[float] = 0.000125998  # lb/hr → kg/s (1/3600 * 0.453592)

# Simulation Settings
TIME_STEP: Final[float] = 0.5  # Time step for simulation (seconds)
MAX_SIMULATION_TIME_FIXED: Final[float] = (
    10000  # Max simulation time for orifice opening mode (seconds)
)
