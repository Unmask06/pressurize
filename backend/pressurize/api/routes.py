"""API routes for gas pressurization simulation."""

import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from pressurize.api.schemas import (
    PropertiesRequest,
    PropertiesResponse,
    SimulationRequest,
    SimulationResponse,
    SimulationResultPoint,
    StreamingChunk,
    StreamingComplete,
)
from pressurize.core.properties import GasState, get_gas_properties_at_conditions
from pressurize.core.simulation import run_simulation, run_simulation_streaming
from pressurize.utils.converters import fahrenheit_to_kelvin, psig_to_pa

router = APIRouter(tags=["pressurize"])

CHUNK_SIZE = 5  # Number of rows per streaming chunk


@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation_endpoint(req: SimulationRequest) -> SimulationResponse:
    """Execute a gas pressurization simulation and return results with KPIs."""
    try:
        df = run_simulation(
            P_up_psig=req.p_up_psig,
            P_down_init_psig=req.p_down_init_psig,
            valve_id_inch=req.valve_id_inch,
            opening_time_s=req.opening_time_s,
            upstream_volume_ft3=req.upstream_volume_ft3,
            upstream_temp_f=req.upstream_temp_f,
            downstream_volume_ft3=req.downstream_volume_ft3,
            downstream_temp_f=req.downstream_temp_f,
            molar_mass=req.molar_mass,
            z_factor=req.z_factor,
            k_ratio=req.k_ratio,
            discharge_coeff=req.discharge_coeff,
            valve_action=req.valve_action,
            opening_mode=req.opening_mode,
            k_curve=req.k_curve,
            dt=req.dt,
            property_mode=req.property_mode,
            composition=req.composition,
            mode=req.mode,
        )

        # Calculate KPIs
        peak_flow = float(df["flowrate_lb_hr"].max())
        final_pressure = float(df["downstream_pressure_psig"].iloc[-1])

        # Find equilibrium time
        # Use simple logic: first time pressure >= upstream OR last time
        # The simulation logic already handles this somewhat, but let's be safe
        equilibrium_mask = (
            df["downstream_pressure_psig"] >= df["upstream_pressure_psig"]
        )
        if equilibrium_mask.any():
            equil_time = float(df.loc[equilibrium_mask, "time"].iloc[0])
        else:
            equil_time = float(df["time"].iloc[-1])

        # Calc total mass
        dt = req.dt  # Approximate integration using fixed time step provided in request
        total_mass = (df["flowrate_lb_hr"].sum() * dt) / 3600

        results = [
            SimulationResultPoint.model_validate(row)
            for row in df.to_dict(orient="records")
        ]

        return SimulationResponse(
            results=results,
            peak_flow=peak_flow,
            final_pressure=final_pressure,
            equilibrium_time=equil_time,
            total_mass_lb=total_mass,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


async def generate_simulation_stream(
    req: SimulationRequest,
    request: Request,
) -> AsyncGenerator[str, None]:
    """Generator that yields simulation results in SSE format."""
    try:
        # Track if client disconnected
        client_disconnected = False

        def should_stop():
            """Check if client has disconnected."""
            nonlocal client_disconnected
            return client_disconnected

        # Use the streaming generator
        all_results = []
        total_rows = 0

        for row_dict in run_simulation_streaming(
            P_up_psig=req.p_up_psig,
            P_down_init_psig=req.p_down_init_psig,
            valve_id_inch=req.valve_id_inch,
            opening_time_s=req.opening_time_s,
            upstream_volume_ft3=req.upstream_volume_ft3,
            upstream_temp_f=req.upstream_temp_f,
            downstream_volume_ft3=req.downstream_volume_ft3,
            downstream_temp_f=req.downstream_temp_f,
            molar_mass=req.molar_mass,
            z_factor=req.z_factor,
            k_ratio=req.k_ratio,
            discharge_coeff=req.discharge_coeff,
            valve_action=req.valve_action,
            opening_mode=req.opening_mode,
            k_curve=req.k_curve,
            dt=req.dt,
            property_mode=req.property_mode,
            composition=req.composition,
            mode=req.mode,
            should_stop_callback=should_stop,
        ):
            # Store all results for KPI calculation
            all_results.append(row_dict)
            total_rows += 1

            # Stream in chunks of CHUNK_SIZE
            if len(all_results) % CHUNK_SIZE == 0:
                # Get last CHUNK_SIZE rows
                chunk_rows = [
                    SimulationResultPoint(**r) for r in all_results[-CHUNK_SIZE:]
                ]
                chunk = StreamingChunk(
                    rows=chunk_rows,
                    total_rows=total_rows,
                )
                yield f"data: {chunk.model_dump_json()}\n\n"

        # Send any remaining rows
        remaining = len(all_results) % CHUNK_SIZE
        if remaining > 0:
            chunk_rows = [SimulationResultPoint(**r) for r in all_results[-remaining:]]
            chunk = StreamingChunk(
                rows=chunk_rows,
                total_rows=total_rows,
            )
            yield f"data: {chunk.model_dump_json()}\n\n"

        # Calculate KPIs from collected results
        if all_results:
            # Extract flowrates and pressures
            flowrates = [r["flowrate_lb_hr"] for r in all_results]
            downstream_pressures = [r["downstream_pressure_psig"] for r in all_results]
            upstream_pressures = [r["upstream_pressure_psig"] for r in all_results]
            times = [r["time"] for r in all_results]

            peak_flow = max(flowrates)
            final_pressure = downstream_pressures[-1]

            # Find equilibrium time
            equil_time = times[-1]
            for _, (down_p, up_p, t) in enumerate(
                zip(downstream_pressures, upstream_pressures, times, strict=True)
            ):
                if down_p >= up_p:
                    equil_time = t
                    break

            # Calculate total mass (trapezoidal integration)
            dt_val = req.dt
            total_mass = (sum(flowrates) * dt_val) / 3600

            # Determine if simulation completed naturally or was aborted
            completed = not should_stop()
        else:
            peak_flow = 0.0
            final_pressure = req.p_down_init_psig
            equil_time = 0.0
            total_mass = 0.0
            completed = False

        # Send completion message with KPIs
        complete = StreamingComplete(
            peak_flow=peak_flow,
            final_pressure=final_pressure,
            equilibrium_time=equil_time,
            total_mass_lb=total_mass,
            completed=completed,
        )
        yield f"data: {complete.model_dump_json()}\n\n"

    except GeneratorExit:
        # Client disconnected
        client_disconnected = True
        raise
    except Exception as e:
        error_msg = json.dumps({"type": "error", "message": str(e)})
        yield f"data: {error_msg}\n\n"


@router.post("/simulate/stream")
async def stream_simulation_endpoint(
    req: SimulationRequest,
    request: Request,
) -> StreamingResponse:
    """Stream simulation results progressively for large datasets.

    Yields results in chunks of 100 rows via Server-Sent Events (SSE).
    Final message contains computed KPIs.
    """
    return StreamingResponse(
        generate_simulation_stream(req, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


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
