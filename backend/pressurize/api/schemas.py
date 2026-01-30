"""Pydantic schemas for API requests and responses."""

from typing import Literal

from pint_glass import PintGlass
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    """Request schema for gas pressurization simulation.

    Contains all parameters needed to run a valve pressurization simulation,
    including vessel properties, valve characteristics, and gas properties.
    """

    # Mode: pressurize (upstream only dp/dt), depressurize (downstream only dp/dt), equalize (both dp/dt)
    mode: Literal["pressurize", "depressurize", "equalize"] = Field(
        "equalize", description="Simulation mode: pressurize, depressurize, or equalize"
    )

    # Upstream vessel properties
    p_up: PintGlass("pressure", "Input") = Field(
        ..., description="Upstream pressure", ge=0
    )
    upstream_volume: PintGlass("volume", "Input") = Field(
        ..., description="Upstream vessel volume", gt=0
    )
    upstream_temp: PintGlass("temperature", "Input") = Field(
        ...,
        description="Upstream vessel temperature. TODO: Currently constant; may add dynamic model later.",
    )

    # Downstream vessel properties
    p_down_init: PintGlass("pressure", "Input") = Field(
        0.0, description="Initial downstream pressure", ge=0
    )
    downstream_volume: PintGlass("volume", "Input") = Field(
        ..., description="Downstream vessel volume", gt=0
    )
    downstream_temp: PintGlass("temperature", "Input") = Field(
        ...,
        description="Downstream vessel temperature. TODO: Currently constant; may add dynamic model later.",
    )

    valve_id: PintGlass("length", "Input") = Field(..., description="Valve ID", gt=0)
    opening_time: PintGlass("time", "Input") = Field(
        ..., description="Valve opening time", ge=0
    )

    # Gas Properties (Manual)
    molar_mass: float = Field(28.97, description="Molar mass (g/mol)")
    z_factor: float = Field(1.0, description="Compressibility factor")
    k_ratio: float = Field(1.4, description="Heat capacity ratio (Cp/Cv)")

    # Valve Characteristics
    discharge_coeff: float = Field(0.65, description="Discharge coefficient (Cd)")
    valve_action: Literal["open", "close"] = Field(
        "open",
        description="Valve action: open (0→100%) or close (100→0%)",
    )
    opening_mode: Literal["linear", "exponential", "quick_acting", "fixed"] = Field(
        "linear",
        description="Valve opening mode: linear, exponential, quick_acting, fixed",
    )
    k_curve: float = Field(
        4.0, description="Curve steepness for exponential/quick_acting"
    )
    dt: float = Field(0.05, description="Time step (s)")

    # Composition Mode
    property_mode: Literal["manual", "composition"] = Field(
        "manual", description="Property mode: manual or composition"
    )
    composition: str | None = Field(
        None, description="Composition string, e.g., 'Methane=0.9, Ethane=0.1'"
    )


class SimulationResultPoint(BaseModel):
    """Single timestep result from a pressurization simulation.

    Contains pressure, flow, valve opening, and gas properties at a specific time.
    """

    time: PintGlass("time", "Output")
    pressure: PintGlass("pressure", "Output")
    upstream_pressure: PintGlass("pressure", "Output")
    downstream_pressure: PintGlass("pressure", "Output")
    flowrate: float
    valve_opening_pct: float
    flow_regime: str

    # Optional dp/dt rates (depending on mode)
    dp_dt_upstream: float | None = None
    dp_dt_downstream: float | None = None

    # Composition properties
    z_factor: float | None = None
    k_ratio: float | None = None
    molar_mass: float | None = None


class SimulationResponse(BaseModel):
    """Complete response from a pressurization simulation.

    Includes time-series results and calculated KPIs like peak flow and equilibrium time.
    """

    results: list[SimulationResultPoint]
    peak_flow: float
    final_pressure: PintGlass("pressure", "Output")
    equilibrium_time: PintGlass("time", "Output")
    total_mass: PintGlass("mass", "Output")


class PropertiesRequest(BaseModel):
    """Request schema for calculating gas properties from composition.

    Used to compute Z-factor, k-ratio, and molar mass from a gas mixture.
    """

    composition: str
    pressure: PintGlass("pressure", "Input")
    temp: PintGlass("temperature", "Input")


class PropertiesResponse(BaseModel):
    """Response schema for gas property calculations.

    Returns compressibility (Z), heat capacity ratio (k), and molar mass (M).
    """

    Z: float
    k: float
    M: float


class StreamingChunk(BaseModel):
    """A chunk of simulation results sent via SSE.

    Contains a batch of result rows for progressive chart updates.
    """

    type: Literal["chunk"] = "chunk"
    rows: list[SimulationResultPoint]
    total_rows: int  # Running total of rows sent so far


class StreamingComplete(BaseModel):
    """Final message sent when simulation streaming completes.

    Contains the final KPIs calculated from all results.
    """

    type: Literal["complete"] = "complete"
    peak_flow: float
    final_pressure: PintGlass("pressure", "Output")
    equilibrium_time: PintGlass("time", "Output")
    total_mass: PintGlass("mass", "Output")
    completed: bool = True  # False if aborted early
