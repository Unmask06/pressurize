"""Dynamic valve pressurization simulation engine."""

import logging
from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from pressurize.config.settings import (
    KG_S_TO_LB_HR,
    MAX_SIMULATION_TIME_FIXED,
    TIME_STEP,
)
from pressurize.core.physics import (
    calculate_critical_pressure_ratio,
    calculate_dual_dp_dt,
    calculate_mass_flow_rate,
)
from pressurize.core.properties import GasState

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Equilibrium tolerance values
EQUILIBRIUM_TOLERANCE_PA = 1e-3
EQUILIBRIUM_TOLERANCE_KGS = 1e-6

# Batch size for yielding results (yield every N steps for performance)
YIELD_BATCH_SIZE = 10


@dataclass
class SimulationState:
    """Container for simulation state variables."""

    P_up: float
    P_down: float
    V_up: float
    V_down: float
    T_up: float
    T_down: float
    A_max: float
    Cd: float
    M: float
    Z: float
    k: float
    gas_state_up: GasState | None
    gas_state_down: GasState | None


def _initialize_simulation_state(
    P_up: float,
    P_down_init: float,
    valve_id: float,
    molar_mass: float,
    z_factor: float,
    k_ratio: float,
    discharge_coeff: float,
    property_mode: Literal["manual", "composition"],
    composition: str | None,
    mode: Literal["pressurize", "depressurize", "equalize"],
    upstream_volume: float,
    upstream_temp: float,
    downstream_volume: float,
    downstream_temp: float,
) -> SimulationState:
    """Initialize all simulation state variables.

    Args:
        P_up: Upstream pressure (SI: Pa).
        P_down_init: Initial downstream pressure (SI: Pa).
        valve_id: Valve inner diameter (SI: m).
        molar_mass: Gas molar mass in g/mol (manual mode).
        z_factor: Compressibility factor (manual mode).
        k_ratio: Heat capacity ratio Cp/Cv (manual mode).
        discharge_coeff: Valve discharge coefficient.
        property_mode: 'manual' or 'composition'.
        composition: Gas composition string for composition mode.
        mode: "pressurize", "depressurize", or "equalize".
        upstream_volume: Upstream vessel volume (SI: m³).
        upstream_temp: Upstream vessel temperature (SI: K).
        downstream_volume: Downstream vessel volume (SI: m³).
        downstream_temp: Downstream vessel temperature (SI: K).

    Returns:
        SimulationState object with initialized values.
    """
    logger.debug(
        f"Initializing simulation state: property_mode={property_mode}, mode={mode}"
    )

    # Pressures are already in SI (Pa) thanks to PintGlass
    P_down = P_down_init
    logger.debug(f"Pressures: P_up={P_up:.0f} Pa, P_down={P_down:.0f} Pa")

    # Volumes and temperatures are already in SI (m³, K)
    V_down = downstream_volume
    V_up = upstream_volume
    logger.debug(f"Volumes: V_up={V_up:.2f} m³, V_down={V_down:.2f} m³")

    T_up = upstream_temp
    T_down = downstream_temp
    logger.debug(f"Temperatures: T_up={T_up:.1f} K, T_down={T_down:.1f} K")

    # Valve parameters (valve_id is in meters)
    valve_radius = valve_id / 2
    A_max = np.pi * valve_radius**2
    Cd = discharge_coeff
    logger.debug(
        f"Valve parameters: radius={valve_radius:.4f} m, A_max={A_max:.6f} m², Cd={Cd}"
    )

    # Initialize gas properties based on mode
    if property_mode == "composition" and composition:
        logger.debug(f"Using composition mode with composition: {composition}")
        if mode == "equalize":
            gas_state_up = GasState(composition)
            gas_state_down = GasState(composition)
            props_up = gas_state_up.get_properties(P_up, T_up)
            props_down = gas_state_down.get_properties(P_down, T_down)
            M, Z, k = props_down.M, props_down.Z, props_down.k
        elif mode == "pressurize":
            gas_state_up = None
            gas_state_down = GasState(composition)
            props_down = gas_state_down.get_properties(P_down, T_down)
            M, Z, k = props_down.M, props_down.Z, props_down.k
        else:  # depressurize
            gas_state_up = GasState(composition)
            gas_state_down = None
            props_up = gas_state_up.get_properties(P_up, T_up)
            M, Z, k = props_up.M, props_up.Z, props_up.k
    else:
        # Manual mode
        logger.debug(
            f"Using manual mode: M={molar_mass} g/mol, Z={z_factor}, k={k_ratio}"
        )
        gas_state_up = None
        gas_state_down = None
        M = molar_mass
        Z = z_factor
        k = k_ratio

    logger.debug(f"Gas properties: M={M:.2f} g/mol, Z={Z:.4f}, k={k:.4f}")
    return SimulationState(
        P_up=P_up,
        P_down=P_down,
        V_up=V_up,
        V_down=V_down,
        T_up=T_up,
        T_down=T_down,
        A_max=A_max,
        Cd=Cd,
        M=M,
        Z=Z,
        k=k,
        gas_state_up=gas_state_up,
        gas_state_down=gas_state_down,
    )


def _initialize_results(
    P_up: float,
    P_down_init: float,
    valve_action: Literal["open", "close"],
    opening_mode: Literal["linear", "exponential", "quick_acting", "fixed"],
    Z: float,
    k: float,
    M: float,
) -> dict:
    """Initialize results dictionary with initial state.

    Args:
        P_up: Initial upstream pressure (Pa).
        P_down_init: Initial downstream pressure (Pa).
        valve_action: "open" or "close".
        opening_mode: Type of valve opening curve.
        Z: Compressibility factor.
        k: Heat capacity ratio.
        M: Molar mass.

    Returns:
        Dictionary with initialized result lists.
    """
    # Determine initial valve opening percentage
    if valve_action == "close":
        initial_opening = 100.0
    elif opening_mode == "fixed":
        initial_opening = 100.0
    else:
        initial_opening = 0.0

    return {
        "time": [0],
        "pressure": [P_down_init],
        "upstream_pressure": [P_up],
        "downstream_pressure": [P_down_init],
        "flowrate": [0],  # Stored as kg/s or converted to display unit? Using kg/s internally?
                          # Wait, SimulationResultPoint.flowrate is float.
                          # Previously flowrate_lb_hr. Let's store kg/s here and let frontend/API decide?
                          # But SimulationResultPoint just says 'flowrate'.
                          # I'll stick to kg/s if I want SI.
        "valve_opening_pct": [initial_opening],
        "flow_regime": ["None"],
        "dp_dt_upstream": [0.0],
        "dp_dt_downstream": [0.0],
        "z_factor": [round(Z, 4)],
        "k_ratio": [round(k, 4)],
        "molar_mass": [round(M, 2)],
    }


def _calculate_valve_opening_fraction(
    t: float,
    opening_time: float,
    valve_action: Literal["open", "close"],
    opening_mode: Literal["linear", "exponential", "quick_acting", "fixed"],
    k_curve: float,
) -> float:
    """Calculate valve opening fraction (0.0 to 1.0) based on time and opening mode.

    Args:
        t: Current simulation time in seconds.
        opening_time: Time for valve to fully open in seconds.
        valve_action: "open" or "close".
        opening_mode: Type of valve opening curve.
        k_curve: Curve steepness parameter for exponential/quick_acting modes.

    Returns:
        Opening fraction from 0.0 (fully closed) to 1.0 (fully open).
    """
    if opening_mode == "fixed":
        return 1.0 if valve_action == "open" else 0.0

    if opening_time <= 0:
        return 0.0 if valve_action == "close" else 1.0

    ratio = min(t / opening_time, 1.0)

    if opening_mode == "exponential":
        # Exponential growth: slow start, steep end
        curve_fraction = (np.exp(k_curve * ratio) - 1) / (np.exp(k_curve) - 1)
    elif opening_mode == "quick_acting":
        # Quick rise: fast initial jump, then levels off
        numerator = 1 - np.exp(-k_curve * ratio)
        denominator = 1 - np.exp(-k_curve)
        curve_fraction = numerator / denominator
    else:  # linear (default)
        curve_fraction = ratio

    # Invert for closing mode
    return (1.0 - curve_fraction) if valve_action == "close" else curve_fraction


def _update_gas_properties(
    state: SimulationState,
    P_up: float,
    P_down: float,
    mode: Literal["pressurize", "depressurize", "equalize"],
) -> tuple[float, float, float]:
    """Update gas properties dynamically in composition mode.

    Args:
        state: Current simulation state.
        P_up: Current upstream pressure in Pa.
        P_down: Current downstream pressure in Pa.
        mode: Simulation mode.

    Returns:
        Tuple of (M, Z, k) - updated properties.
    """
    if mode == "equalize" and state.gas_state_up and state.gas_state_down:
        props_up = state.gas_state_up.get_properties(P_up, state.T_up)
        props_down = state.gas_state_down.get_properties(P_down, state.T_down)
        return props_down.M, props_down.Z, props_down.k
    elif mode == "pressurize" and state.gas_state_down:
        props_down = state.gas_state_down.get_properties(P_down, state.T_down)
        return props_down.M, props_down.Z, props_down.k
    elif mode == "depressurize" and state.gas_state_up:
        props_up = state.gas_state_up.get_properties(P_up, state.T_up)
        return props_up.M, props_up.Z, props_up.k
    else:
        return state.M, state.Z, state.k


def _calculate_flow_regime_and_mass_flow(
    P_up: float,
    P_down: float,
    A: float,
    k: float,
    M: float,
    Z: float,
    T: float,
    Cd: float,
) -> tuple[str, float]:
    """Calculate flow regime and mass flow rate.

    Args:
        P_up: Upstream pressure in Pa.
        P_down: Downstream pressure in Pa.
        A: Valve opening area in m².
        k: Heat capacity ratio.
        M: Molar mass in g/mol.
        Z: Compressibility factor.
        T: Temperature in K.
        Cd: Discharge coefficient.

    Returns:
        Tuple of (regime, massflow_kgs).
    """
    pressure_diff = P_up - P_down

    if abs(pressure_diff) < EQUILIBRIUM_TOLERANCE_PA:  # Effectively equilibrium
        return "Equilibrium", 0.0

    r = P_down / P_up if P_up > 0 else 1.0
    r_c = calculate_critical_pressure_ratio(k)
    regime = "Choked" if r <= r_c else "Subsonic"

    massflow_kgs = calculate_mass_flow_rate(Cd, A, P_up, P_down, k, M, Z, T)
    if abs(massflow_kgs) < EQUILIBRIUM_TOLERANCE_KGS:
        massflow_kgs = 0.0
        regime = "Equilibrium"
    return regime, massflow_kgs


def _calculate_pressure_rates(
    mode: Literal["pressurize", "depressurize", "equalize"],
    pressure_diff: float,
    massflow_kgs: float,
    Z: float,
    T: float,
    V_up: float,
    V_down: float,
    M: float,
) -> tuple[float, float]:
    """Calculate pressure rate of change for both vessels.

    Args:
        mode: Simulation mode.
        pressure_diff: P_up - P_down in Pa.
        massflow_kgs: Mass flow rate in kg/s.
        Z: Compressibility factor.
        T: Temperature in K.
        V_up: Upstream volume in m³.
        V_down: Downstream volume in m³.
        M: Molar mass in g/mol.

    Returns:
        Tuple of (dp_dt_up, dp_dt_down) in Pa/s.
    """
    if abs(pressure_diff) < EQUILIBRIUM_TOLERANCE_PA:
        return 0.0, 0.0

    mass_flow_up = -massflow_kgs
    mass_flow_down = massflow_kgs

    dp_dt_up, dp_dt_down = calculate_dual_dp_dt(
        mode=mode,
        mass_flow_upstream=mass_flow_up,
        mass_flow_downstream=mass_flow_down,
        z_factor=Z,
        temperature=T,
        upstream_volume=V_up,
        downstream_volume=V_down,
        molar_mass_g_mol=M,
    )
    return dp_dt_up, dp_dt_down


def _update_pressures(
    P_up: float,
    P_down: float,
    dp_dt_up: float,
    dp_dt_down: float,
    dt: float,
) -> tuple[float, float]:
    """Update pressures based on rates of change.

    Args:
        P_up: Current upstream pressure in Pa.
        P_down: Current downstream pressure in Pa.
        dp_dt_up: Rate of pressure change upstream in Pa/s.
        dp_dt_down: Rate of pressure change downstream in Pa/s.
        dt: Time step in seconds.

    Returns:
        Tuple of (new P_up, new P_down) in Pa.
    """
    if dp_dt_up != 0.0:
        P_up += dp_dt_up * dt
    if dp_dt_down != 0.0:
        P_down += dp_dt_down * dt
    return P_up, P_down


def _check_stopping_condition(
    valve_action: Literal["open", "close"],
    opening_fraction: float,
    regime: str,
) -> bool:
    """Check if simulation should stop.

    Args:
        valve_action: "open" or "close".
        opening_fraction: Current valve opening (0.0 to 1.0).
        regime: Current flow regime.
        P_up: Current upstream pressure in Pa.

    Returns:
        True if simulation should stop, False otherwise.
    """
    if valve_action == "close":
        # For closing: stop when valve reaches 0% (fully closed)
        should_stop = opening_fraction <= 0.0
        if should_stop:
            logger.debug(
                f"Stopping condition met for closing valve: opening_fraction={opening_fraction:.6f} <= 0.0"
            )
    else:
        # For opening: stop when valve reaches 100% AND pressure equilibrium
        should_stop = regime == "Equilibrium" and opening_fraction >= 1.0
        if should_stop:
            logger.debug(
                f"Stopping condition met for opening valve: opening_fraction={opening_fraction:.6f} >= 1.0 "
            )

    return should_stop


def _append_step_results(
    results: dict,
    t: float,
    P_up: float,
    P_down: float,
    opening_fraction: float,
    massflow_kgs: float,
    regime: str,
    dp_dt_up: float,
    dp_dt_down: float,
    Z: float,
    k: float,
    M: float,
) -> None:
    """Append current simulation step results to results dictionary.

    Args:
        results: Results dictionary to append to.
        t: Current time in seconds.
        P_up: Upstream pressure in Pa.
        P_down: Downstream pressure in Pa.
        opening_fraction: Valve opening (0.0 to 1.0).
        massflow_kgs: Mass flow rate in kg/s.
        regime: Flow regime string.
        dp_dt_up: Upstream pressure rate in Pa/s.
        dp_dt_down: Downstream pressure rate in Pa/s.
        Z: Compressibility factor.
        k: Heat capacity ratio.
        M: Molar mass in g/mol.
    """
    # PintGlass Output fields expect SI base units, so we store Pa directly.
    # Flowrate is float in schema, so we can decide unit. Previously lb/hr.
    # Let's keep flowrate as kg/s if we want to be fully SI internal?
    # But wait, the schema said flowrate: float. If I give it kg/s, the user will see kg/s.
    # The previous version converted to lb/hr.
    # Ideally, flowrate should also be a PintGlass field if we want auto-conversion.
    # But for now I'll store kg/s and let the user handle it or update schema later.
    # Actually, let's stick to kg/s for cleaner physics.
    # NOTE: If frontend expects lb/hr, this is a breaking change.
    # I will assume frontend will be updated to handle unit selection or generic units.

    results["time"].append(round(t, 2))
    results["pressure"].append(P_down)
    results["upstream_pressure"].append(P_up)
    results["downstream_pressure"].append(P_down)
    results["flowrate"].append(massflow_kgs) # Storing kg/s
    results["valve_opening_pct"].append(round(opening_fraction * 100, 1))
    results["flow_regime"].append(regime)
    results["dp_dt_upstream"].append(dp_dt_up)
    results["dp_dt_downstream"].append(dp_dt_down)
    results["z_factor"].append(round(Z, 4))
    results["k_ratio"].append(round(k, 4))
    results["molar_mass"].append(round(M, 2))


def _calculate_max_simulation_time(
    opening_mode: Literal["linear", "exponential", "quick_acting", "fixed"],
    opening_time: float,
    valve_action: Literal["open", "close"],
) -> float:
    """Calculate maximum simulation time to prevent infinite loops.

    Args:
        opening_mode: Type of valve opening curve.
        opening_time: Time for valve to fully open in seconds.
        valve_action: "open" or "close".

    Returns:
        Maximum simulation time in seconds.
    """
    if opening_mode == "fixed" or opening_time <= 0:
        return MAX_SIMULATION_TIME_FIXED
    elif valve_action == "close":
        return opening_time * 1.2  # Closing: 1.2x closing time
    else:
        return opening_time * 10  # Opening: 10x opening time for equilibrium


def run_simulation(
    P_up: float,
    P_down_init: float,
    valve_id: float,
    opening_time: float,
    upstream_volume: float,
    upstream_temp: float,
    downstream_volume: float,
    downstream_temp: float,
    molar_mass: float,
    z_factor: float,
    k_ratio: float,
    discharge_coeff: float = 0.65,
    valve_action: Literal["open", "close"] = "open",
    opening_mode: Literal["linear", "exponential", "quick_acting", "fixed"] = "linear",
    k_curve: float = 4.0,
    dt: float = TIME_STEP,
    property_mode: Literal["manual", "composition"] = "manual",
    composition: str | None = None,
    mode: Literal["pressurize", "depressurize", "equalize"] = "equalize",
) -> pd.DataFrame:
    """Run the valve pressurization simulation.

    Args:
        P_up: Upstream pressure (Pa).
        P_down_init: Initial downstream pressure (Pa).
        valve_id: Valve inner diameter (m).
        opening_time: Time for valve to fully open in seconds.
        upstream_volume: Upstream vessel volume (m³).
        upstream_temp: Upstream vessel temperature (K).
        downstream_volume: Downstream vessel volume (m³).
        downstream_temp: Downstream vessel temperature (K).
        molar_mass: Gas molar mass in g/mol (manual mode).
        z_factor: Compressibility factor (manual mode).
        k_ratio: Heat capacity ratio Cp/Cv (manual mode).
        discharge_coeff: Valve discharge coefficient. Default 0.65.
        valve_action: "open" or "close" valve action. Default "open".
        opening_mode: 'linear', 'exponential', 'quick_acting', or 'fixed'.
        k_curve: Curve steepness for exponential/quick_acting. Default 4.0.
        dt: Simulation timestep in seconds.
        property_mode: 'manual' or 'composition'. Default 'manual'.
        composition: Gas composition string for composition mode.
        mode: Controls which sides compute dp/dt. Default "equalize".

    Returns:
        DataFrame with columns: time, pressure, upstream_pressure,
        downstream_pressure, flowrate, valve_opening_pct, flow_regime,
        dp_dt_upstream, dp_dt_downstream.
    """
    logger.info(
        f"Starting simulation: valve_action={valve_action}, opening_mode={opening_mode}, "
        f"opening_time={opening_time}s, mode={mode}"
    )
    logger.debug(
        f"Initial conditions: P_up={P_up:.0f} Pa, P_down={P_down_init:.0f} Pa"
    )

    # Initialize simulation state
    state = _initialize_simulation_state(
        P_up=P_up,
        P_down_init=P_down_init,
        valve_id=valve_id,
        molar_mass=molar_mass,
        z_factor=z_factor,
        k_ratio=k_ratio,
        discharge_coeff=discharge_coeff,
        property_mode=property_mode,
        composition=composition,
        mode=mode,
        upstream_volume=upstream_volume,
        upstream_temp=upstream_temp,
        downstream_volume=downstream_volume,
        downstream_temp=downstream_temp,
    )

    # Initialize results storage
    results = _initialize_results(
        P_up=P_up,
        P_down_init=P_down_init,
        valve_action=valve_action,
        opening_mode=opening_mode,
        Z=state.Z,
        k=state.k,
        M=state.M,
    )

    # Calculate maximum simulation time
    max_time = _calculate_max_simulation_time(
        opening_mode=opening_mode,
        opening_time=opening_time,
        valve_action=valve_action,
    )
    logger.debug(f"Calculated max simulation time: {max_time}s")

    # Main simulation loop
    t: float = 0
    P_up = state.P_up
    P_down = state.P_down
    M = state.M
    Z = state.Z
    k = state.k
    P_up_current = P_up
    P_down_current = P_down_init

    while t < max_time:
        t += dt

        # Calculate valve opening fraction
        opening_fraction = _calculate_valve_opening_fraction(
            t=t,
            opening_time=opening_time,
            valve_action=valve_action,
            opening_mode=opening_mode,
            k_curve=k_curve,
        )

        # Log progress every 10 seconds or at key milestones
        if int(t) % 10 == 0 and int(t - dt) % 10 != 0:
            logger.debug(
                f"t={t:.1f}s: valve_opening={opening_fraction:.3f}, "
                f"P_up={P_up:.0f} Pa, P_down={P_down:.0f} Pa"
            )

        A = state.A_max * opening_fraction

        # Update gas properties dynamically in composition mode
        M, Z, k = _update_gas_properties(
            state=state,
            P_up=P_up,
            P_down=P_down,
            mode=mode,
        )

        # Calculate flow regime and mass flow rate
        regime, massflow_kgs = _calculate_flow_regime_and_mass_flow(
            P_up=P_up,
            P_down=P_down,
            A=A,
            k=k,
            M=M,
            Z=Z,
            T=state.T_up,
            Cd=state.Cd,
        )

        # Calculate pressure rates of change
        pressure_diff = P_up - P_down
        dp_dt_up, dp_dt_down = _calculate_pressure_rates(
            mode=mode,
            pressure_diff=pressure_diff,
            massflow_kgs=massflow_kgs,
            Z=Z,
            T=state.T_up,
            V_up=state.V_up,
            V_down=state.V_down,
            M=M,
        )

        # Update pressures
        P_up, P_down = _update_pressures(
            P_up=P_up,
            P_down=P_down,
            dp_dt_up=dp_dt_up,
            dp_dt_down=dp_dt_down,
            dt=dt,
        )

        P_up_current = P_up
        P_down_current = P_down

        # Append results
        _append_step_results(
            results=results,
            t=t,
            P_up=P_up_current,
            P_down=P_down_current,
            opening_fraction=opening_fraction,
            massflow_kgs=massflow_kgs,
            regime=regime,
            dp_dt_up=dp_dt_up,
            dp_dt_down=dp_dt_down,
            Z=Z,
            k=k,
            M=M,
        )

        # Check stopping condition
        if _check_stopping_condition(
            valve_action=valve_action,
            opening_fraction=opening_fraction,
            regime=regime,
        ):
            logger.info(
                f"Simulation stopped at t={t:.2f}s: valve_opening={opening_fraction:.3f}, "
                f"P_up={P_up_current:.0f} Pa, P_down={P_down_current:.0f} Pa"
            )
            break

    logger.info(
        f"Simulation completed: {len(results['time'])} steps, final_time={t:.2f}s"
    )
    return pd.DataFrame(results)


def run_simulation_streaming(
    P_up: float,
    P_down_init: float,
    valve_id: float,
    opening_time: float,
    upstream_volume: float,
    upstream_temp: float,
    downstream_volume: float,
    downstream_temp: float,
    molar_mass: float,
    z_factor: float,
    k_ratio: float,
    discharge_coeff: float = 0.65,
    valve_action: Literal["open", "close"] = "open",
    opening_mode: Literal["linear", "exponential", "quick_acting", "fixed"] = "linear",
    k_curve: float = 4.0,
    dt: float = TIME_STEP,
    property_mode: Literal["manual", "composition"] = "manual",
    composition: str | None = None,
    mode: Literal["pressurize", "depressurize", "equalize"] = "equalize",
    should_stop_callback: Callable[[], bool] | None = None,
) -> Generator[dict, None, None]:
    """Run the valve pressurization simulation as a generator that yields batches of results.

    Yields:
        Dictionary representing a single simulation row with all computed values.
    """
    logger.info(
        f"Starting streaming simulation: valve_action={valve_action}, opening_mode={opening_mode}, "
        f"opening_time={opening_time}s, mode={mode}"
    )
    logger.debug(
        f"Initial conditions: P_up={P_up:.0f} Pa, P_down={P_down_init:.0f} Pa"
    )

    # Initialize simulation state
    state = _initialize_simulation_state(
        P_up=P_up,
        P_down_init=P_down_init,
        valve_id=valve_id,
        molar_mass=molar_mass,
        z_factor=z_factor,
        k_ratio=k_ratio,
        discharge_coeff=discharge_coeff,
        property_mode=property_mode,
        composition=composition,
        mode=mode,
        upstream_volume=upstream_volume,
        upstream_temp=upstream_temp,
        downstream_volume=downstream_volume,
        downstream_temp=downstream_temp,
    )

    # Initialize results storage
    results = _initialize_results(
        P_up=P_up,
        P_down_init=P_down_init,
        valve_action=valve_action,
        opening_mode=opening_mode,
        Z=state.Z,
        k=state.k,
        M=state.M,
    )

    # Yield initial row
    yield {
        "time": 0,
        "pressure": P_down_init,
        "upstream_pressure": P_up,
        "downstream_pressure": P_down_init,
        "flowrate": 0,
        "valve_opening_pct": 100.0
        if (valve_action == "close" or opening_mode == "fixed")
        else 0.0,
        "flow_regime": "None",
        "dp_dt_upstream": 0.0,
        "dp_dt_downstream": 0.0,
        "z_factor": round(state.Z, 4),
        "k_ratio": round(state.k, 4),
        "molar_mass": round(state.M, 2),
    }

    # Calculate maximum simulation time
    max_time = _calculate_max_simulation_time(
        opening_mode=opening_mode,
        opening_time=opening_time,
        valve_action=valve_action,
    )
    logger.debug(f"Calculated max simulation time: {max_time}s")

    # Main simulation loop
    t: float = 0
    P_up = state.P_up
    P_down = state.P_down
    M = state.M
    Z = state.Z
    k = state.k
    step_count = 0
    P_up_current = P_up
    P_down_current = P_down_init

    while t < max_time:
        # Check for abort signal
        if should_stop_callback and should_stop_callback():
            logger.info(f"Simulation aborted by user at t={t:.2f}s")
            break

        t += dt
        step_count += 1

        # Calculate valve opening fraction
        opening_fraction = _calculate_valve_opening_fraction(
            t=t,
            opening_time=opening_time,
            valve_action=valve_action,
            opening_mode=opening_mode,
            k_curve=k_curve,
        )

        A = state.A_max * opening_fraction

        # Update gas properties dynamically in composition mode
        M, Z, k = _update_gas_properties(
            state=state,
            P_up=P_up,
            P_down=P_down,
            mode=mode,
        )

        # Calculate flow regime and mass flow rate
        regime, massflow_kgs = _calculate_flow_regime_and_mass_flow(
            P_up=P_up,
            P_down=P_down,
            A=A,
            k=k,
            M=M,
            Z=Z,
            T=state.T_up,
            Cd=state.Cd,
        )

        # Calculate pressure rates of change
        pressure_diff = P_up - P_down
        dp_dt_up, dp_dt_down = _calculate_pressure_rates(
            mode=mode,
            pressure_diff=pressure_diff,
            massflow_kgs=massflow_kgs,
            Z=Z,
            T=state.T_up,
            V_up=state.V_up,
            V_down=state.V_down,
            M=M,
        )

        # Update pressures
        P_up, P_down = _update_pressures(
            P_up=P_up,
            P_down=P_down,
            dp_dt_up=dp_dt_up,
            dp_dt_down=dp_dt_down,
            dt=dt,
        )

        P_up_current = P_up
        P_down_current = P_down

        # Append to results buffer
        _append_step_results(
            results=results,
            t=t,
            P_up=P_up_current,
            P_down=P_down_current,
            opening_fraction=opening_fraction,
            massflow_kgs=massflow_kgs,
            regime=regime,
            dp_dt_up=dp_dt_up,
            dp_dt_down=dp_dt_down,
            Z=Z,
            k=k,
            M=M,
        )

        # Yield batch of results every YIELD_BATCH_SIZE steps for performance
        if step_count % YIELD_BATCH_SIZE == 0:
            # Get the last YIELD_BATCH_SIZE rows
            for i in range(-YIELD_BATCH_SIZE, 0):
                yield {
                    "time": results["time"][i],
                    "pressure": results["pressure"][i],
                    "upstream_pressure": results["upstream_pressure"][i],
                    "downstream_pressure": results["downstream_pressure"][i],
                    "flowrate": results["flowrate"][i],
                    "valve_opening_pct": results["valve_opening_pct"][i],
                    "flow_regime": results["flow_regime"][i],
                    "dp_dt_upstream": results["dp_dt_upstream"][i],
                    "dp_dt_downstream": results["dp_dt_downstream"][i],
                    "z_factor": results["z_factor"][i],
                    "k_ratio": results["k_ratio"][i],
                    "molar_mass": results["molar_mass"][i],
                }

        # Check stopping condition
        if _check_stopping_condition(
            valve_action=valve_action,
            opening_fraction=opening_fraction,
            regime=regime,
        ):
            logger.info(
                f"Simulation stopped at t={t:.2f}s: valve_opening={opening_fraction:.3f}, "
                f"P_up={P_up_current:.0f} Pa, P_down={P_down_current:.0f} Pa"
            )
            break

    # Yield any remaining rows not yet yielded
    remaining = step_count % YIELD_BATCH_SIZE
    if remaining > 0:
        for i in range(-remaining, 0):
            yield {
                "time": results["time"][i],
                "pressure": results["pressure"][i],
                "upstream_pressure": results["upstream_pressure"][i],
                "downstream_pressure": results["downstream_pressure"][i],
                "flowrate": results["flowrate"][i],
                "valve_opening_pct": results["valve_opening_pct"][i],
                "flow_regime": results["flow_regime"][i],
                "dp_dt_upstream": results["dp_dt_upstream"][i],
                "dp_dt_downstream": results["dp_dt_downstream"][i],
                "z_factor": results["z_factor"][i],
                "k_ratio": results["k_ratio"][i],
                "molar_mass": results["molar_mass"][i],
            }

    logger.info(
        f"Streaming simulation completed: {len(results['time'])} steps, final_time={t:.2f}s"
    )

