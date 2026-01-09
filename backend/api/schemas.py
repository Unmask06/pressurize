"""
Pydantic schemas for API requests and responses.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    """Request schema for gas pressurization simulation.

    Contains all parameters needed to run a valve pressurization simulation,
    including vessel properties, valve characteristics, and gas properties.
    """

    p_up_psig: float = Field(..., description="Upstream pressure (psig)", ge=0)
    p_down_init_psig: float = Field(
        0.0, description="Initial downstream pressure (psig)", ge=0
    )
    volume_ft3: float = Field(..., description="Vessel volume (ft3)", gt=0)
    valve_id_inch: float = Field(..., description="Valve ID (inches)", gt=0)
    opening_time_s: float = Field(..., description="Valve opening time (s)", ge=0)
    temp_f: float = Field(..., description="Temperature (F)")

    # Gas Properties (Manual)
    molar_mass: float = Field(28.97, description="Molar mass (g/mol)")
    z_factor: float = Field(1.0, description="Compressibility factor")
    k_ratio: float = Field(1.4, description="Heat capacity ratio (Cp/Cv)")

    # Valve Characteristics
    discharge_coeff: float = Field(0.65, description="Discharge coefficient (Cd)")
    opening_mode: str = Field(
        "linear",
        description="Valve opening mode: linear, exponential, quick_opening, fixed",
    )
    k_curve: float = Field(
        4.0, description="Curve steepness for exponential/quick_opening"
    )
    dt: float = Field(0.05, description="Time step (s)")

    # Composition Mode
    property_mode: str = Field(
        "manual", description="Property mode: manual or composition"
    )
    composition: Optional[str] = Field(
        None, description="Composition string, e.g., 'Methane=0.9, Ethane=0.1'"
    )


class SimulationResultPoint(BaseModel):
    """Single timestep result from a pressurization simulation.

    Contains pressure, flow, valve opening, and gas properties at a specific time.
    """

    time: float
    pressure_psig: float
    upstream_pressure_psig: float
    flowrate_lb_hr: float
    valve_opening_pct: float
    flow_regime: str

    # Composition properties
    z_factor: Optional[float] = None
    k_ratio: Optional[float] = None
    molar_mass: Optional[float] = None


class SimulationResponse(BaseModel):
    """Complete response from a pressurization simulation.

    Includes time-series results and calculated KPIs like peak flow and equilibrium time.
    """

    results: List[SimulationResultPoint]
    peak_flow: float
    final_pressure: float
    equilibrium_time: float
    total_mass_lb: float


class PropertiesRequest(BaseModel):
    """Request schema for calculating gas properties from composition.

    Used to compute Z-factor, k-ratio, and molar mass from a gas mixture.
    """

    composition: str
    pressure_psig: float
    temp_f: float


class PropertiesResponse(BaseModel):
    """Response schema for gas property calculations.

    Returns compressibility (Z), heat capacity ratio (k), and molar mass (M).
    """

    Z: float
    k: float
    M: float
