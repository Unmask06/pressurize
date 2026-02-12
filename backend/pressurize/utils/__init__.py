"""Utility functions for the pressurize package."""

ATM_PA = 101325.0  # 1 atmosphere in Pascals


def absolute_pressure(gauge_pressure_pa: float) -> float:
    """Convert gauge pressure (Pa) to absolute pressure (Pa)."""
    return gauge_pressure_pa + ATM_PA
