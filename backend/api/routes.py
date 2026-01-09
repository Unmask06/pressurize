"""
API routes for gas pressurization simulation.
"""

from fastapi import APIRouter, HTTPException
from backend.api.schemas import (
    SimulationRequest,
    SimulationResponse,
    PropertiesRequest,
    PropertiesResponse,
)
from backend.core.simulation import run_simulation
from backend.core.properties import GasState, get_gas_properties_at_conditions
from backend.utils.converters import fahrenheit_to_kelvin, psig_to_pa

router = APIRouter()


@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation_endpoint(req: SimulationRequest) -> SimulationResponse:
    """Execute a gas pressurization simulation and return results with KPIs."""
    try:
        df = run_simulation(
            P_up_psig=req.p_up_psig,
            P_down_init_psig=req.p_down_init_psig,
            volume_ft3=req.volume_ft3,
            valve_id_inch=req.valve_id_inch,
            opening_time_s=req.opening_time_s,
            temp_f=req.temp_f,
            molar_mass=req.molar_mass,
            z_factor=req.z_factor,
            k_ratio=req.k_ratio,
            discharge_coeff=req.discharge_coeff,
            opening_mode=req.opening_mode,
            k_curve=req.k_curve,
            dt=req.dt,
            property_mode=req.property_mode,
            composition=req.composition,
        )

        # Calculate KPIs
        peak_flow = float(df["flowrate_lb_hr"].max())
        final_pressure = float(df["pressure_psig"].iloc[-1])

        # Find equilibrium time
        # Use simple logic: first time pressure >= upstream OR last time
        # The simulation logic already handles this somewhat, but let's be safe
        equilibrium_mask = df["pressure_psig"] >= df["upstream_pressure_psig"]
        if equilibrium_mask.any():
            equil_time = float(df.loc[equilibrium_mask, "time"].iloc[0])
        else:
            equil_time = float(df["time"].iloc[-1])

        # Calc total mass
        dt = req.dt  # Approximate integration using fixed time step provided in request
        # Better: use the actual time steps from dataframe if needed, but dt is constant
        total_mass = (df["flowrate_lb_hr"].sum() * dt) / 3600

        # Convert DataFrame to list of dicts
        results = df.to_dict(orient="records")

        return SimulationResponse(
            results=results,
            peak_flow=peak_flow,
            final_pressure=final_pressure,
            equilibrium_time=equil_time,
            total_mass_lb=total_mass,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/components")
async def get_components() -> list[str]:
    """Get list of available gas components for composition modeling."""
    return GasState.get_default_components()


@router.get("/presets")
async def get_presets() -> list[dict[str, str]]:
    """Get list of predefined gas composition presets."""
    return [
        {"id": "natural_gas", "name": "Natural Gas (Pipeline)"},
        {"id": "pure_methane", "name": "Pure Methane"},
        {"id": "rich_gas", "name": "Rich Gas"},
        {"id": "sour_gas", "name": "Sour Gas"},
        {"id": "lean_gas", "name": "Lean Gas"},
    ]


@router.get("/presets/{preset_id}")
async def get_preset_details(preset_id: str) -> dict[str, float]:
    """Get detailed composition data for a specific preset."""
    comp = GasState.get_preset_composition(preset_id)
    return comp


@router.post("/properties", response_model=PropertiesResponse)
async def calculate_properties(req: PropertiesRequest) -> PropertiesResponse:
    """Calculate gas properties (Z, k, M) from composition and conditions."""
    try:
        # Convert units for the internal function (expects Pa and Kelvin)
        pressure_pa = psig_to_pa(req.pressure_psig)
        temp_k = fahrenheit_to_kelvin(req.temp_f)
        z_factor, k, mol_wt = get_gas_properties_at_conditions(
            req.composition, pressure_pa, temp_k
        )

        return PropertiesResponse(Z=z_factor, k=k, M=mol_wt)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
