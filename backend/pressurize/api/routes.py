"""API routes for gas pressurization simulation."""

import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pint_glass import TARGET_DIMENSIONS, UNIT_SYSTEMS

from pressurize.api.schemas import (
    PropertiesRequest,
    PropertiesResponse,
    SimulationRequest,
    SimulationResultPoint,
    StreamingChunk,
    StreamingComplete,
)
from pressurize.core.properties import GasState, get_gas_properties_at_conditions
from pressurize.core.simulation import run_simulation_streaming

router = APIRouter(tags=["pressurize"])

CHUNK_SIZE = 5  # Number of rows per streaming chunk


@router.get("/units/config")
async def get_units_config() -> dict:
    """Get the unit configuration including supported systems and dimension mappings."""
    # Normalize dimension keys to lowercase for consistent frontend access
    dimensions_normalized = {
        dim.lower(): systems for dim, systems in TARGET_DIMENSIONS.items()
    }
    return {
        "systems": sorted(list(UNIT_SYSTEMS)),
        "dimensions": dimensions_normalized,
    }


async def generate_simulation_stream(
    req: SimulationRequest,
    request: Request,
) -> AsyncGenerator[str, None]:
    """Generator that yields simulation results in SSE format."""
    import logging

    from pint_glass import unit_context

    logger = logging.getLogger("pressurize.simulation")

    # Get current unit system from context
    current_system = unit_context.get()

    # Log simulation start with unit system
    logger.info("=" * 80)
    logger.info("🚀 SIMULATION STARTED")
    logger.info(f"📊 Unit System: {current_system}")
    logger.info("=" * 80)

    # Log converted SI values (AFTER PintGlass Input conversion)
    logger.info("🔄 BASE INPUT (converted to SI units):")
    logger.info(json.dumps(req.model_dump(), indent=2))

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
            P_up=req.p_up,
            P_down_init=req.p_down_init,
            valve_id=req.valve_id / 1000,  # Convert mm to m for physics engine
            opening_time=req.opening_time,
            upstream_volume=req.upstream_volume,
            upstream_temp=req.upstream_temp,
            downstream_volume=req.downstream_volume,
            downstream_temp=req.downstream_temp,
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

                # Check if client disconnected after yielding
                if await request.is_disconnected():
                    client_disconnected = True
                    break

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
            # Extract flowrates and pressures (SI units)
            flowrates = [r["flowrate"] for r in all_results]
            downstream_pressures = [r["downstream_pressure"] for r in all_results]
            upstream_pressures = [r["upstream_pressure"] for r in all_results]
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

            # Calculate total mass (trapezoidal integration approx)
            dt_val = req.dt
            total_mass = sum(flowrates) * dt_val

            # Determine if simulation completed naturally or was aborted
            completed = not should_stop()
        else:
            peak_flow = 0.0
            final_pressure = req.p_down_init
            equil_time = 0.0
            total_mass = 0.0
            completed = False

        # Log base output (SI units before conversion)
        base_output = {
            "peak_flow_kg_s": peak_flow,
            "final_pressure_pa": final_pressure,
            "equilibrium_time_s": equil_time,
            "total_mass_kg": total_mass,
            "total_rows": total_rows,
            "completed": completed,
        }
        logger.info("🔧 BASE OUTPUT (SI units - before PintGlass conversion):")
        logger.info(json.dumps(base_output, indent=2))

        # Send completion message with KPIs
        complete = StreamingComplete(
            peak_flow=peak_flow,
            final_pressure=final_pressure,
            equilibrium_time=equil_time,
            total_mass=total_mass,
            completed=completed,
        )

        # Log preferred output (after PintGlass Output conversion)
        logger.info(f"✅ PREFERRED OUTPUT (converted to {current_system} unit system):")
        logger.info(json.dumps(complete.model_dump(), indent=2))
        logger.info("=" * 80)
        logger.info("🏁 SIMULATION COMPLETED")
        logger.info("=" * 80)

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

    Yields results in chunks of 5 rows via Server-Sent Events (SSE).
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
        # Inputs are already SI (Pa, K) due to PintGlass Input fields
        pressure_pa = req.pressure
        temp_k = req.temp
        z_factor, k, mol_wt = get_gas_properties_at_conditions(
            req.composition, pressure_pa, temp_k
        )

        return PropertiesResponse(Z=z_factor, k=k, M=mol_wt)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
