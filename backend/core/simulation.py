"""Dynamic valve pressurization simulation engine."""

from typing import Literal, Optional

import numpy as np
import pandas as pd

from backend.config.settings import FT3_TO_M3, INCH_TO_M, KG_S_TO_LB_HR, TIME_STEP
from backend.core.physics import (
    calculate_critical_pressure_ratio,
    calculate_dp_dt,
    calculate_mass_flow_rate,
)
from backend.core.properties import GasState
from backend.utils.converters import fahrenheit_to_kelvin, pa_to_psig, psig_to_pa


def run_simulation(
    P_up_psig: float,
    P_down_init_psig: float,
    volume_ft3: float,
    valve_id_inch: float,
    opening_time_s: float,
    temp_f: float,
    molar_mass: float,
    z_factor: float,
    k_ratio: float,
    discharge_coeff: float = 0.65,
    valve_action: Literal["open", "close"] = "open",
    opening_mode: Literal["linear", "exponential", "quick_acting", "fixed"] = "linear",
    k_curve: float = 4.0,
    dt: float = TIME_STEP,
    property_mode: Literal["manual", "composition"] = "manual",
    composition: Optional[str] = None,
) -> pd.DataFrame:
    """Run the valve pressurization simulation.

    Simulates gas flow through a valve into a downstream vessel with dynamic
    pressure and flow rate calculations over time.

    Args:
        P_up_psig: Upstream pressure in psig.
        P_down_init_psig: Initial downstream pressure in psig.
        volume_ft3: Vessel volume in ft³.
        valve_id_inch: Valve inner diameter in inches.
        opening_time_s: Time for valve to fully open in seconds.
        temp_f: Gas temperature in °F.
        molar_mass: Gas molar mass in g/mol (manual mode).
        z_factor: Compressibility factor (manual mode).
        k_ratio: Heat capacity ratio Cp/Cv (manual mode).
        discharge_coeff: Valve discharge coefficient. Default 0.65.
        opening_mode: 'linear', 'exponential', 'quick_acting', or 'fixed'. Default 'linear'.
        k_curve: Curve steepness for exponential/quick_acting. Default 4.0.
        dt: Simulation timestep in seconds.
        property_mode: 'manual' or 'composition'. Default 'manual'.
        composition: Gas composition string for composition mode.

    Returns:
        DataFrame with columns: time, pressure_psig, upstream_pressure_psig,
        flowrate_lb_hr, valve_opening_pct, flow_regime.
    """
    # Convert to SI units
    P_up = psig_to_pa(P_up_psig)
    P_down = psig_to_pa(P_down_init_psig)
    V = volume_ft3 * FT3_TO_M3
    valve_radius = (valve_id_inch * INCH_TO_M) / 2
    A_max = np.pi * valve_radius**2
    T = fahrenheit_to_kelvin(temp_f)
    Cd = discharge_coeff

    # Initialize gas properties based on mode
    if property_mode == "composition" and composition:
        gas_state = GasState(composition)
        # Get initial properties at downstream pressure
        props = gas_state.get_properties(P_down, T)
        M = props.M
        Z = props.Z
        k = props.k
    else:
        # Manual mode - use provided values
        gas_state = None
        M = molar_mass
        Z = z_factor
        k = k_ratio

    # Initialize results storage
    # For closing: starts at 100%; For opening with fixed: 100%; Otherwise: 0%
    if valve_action == "close":
        initial_opening = 100.0
    elif opening_mode == "fixed":
        initial_opening = 100.0
    else:
        initial_opening = 0.0
    results = {
        "time": [0],
        "pressure_psig": [P_down_init_psig],
        "upstream_pressure_psig": [P_up_psig],
        "flowrate_lb_hr": [0],
        "valve_opening_pct": [initial_opening],
        "flow_regime": ["None"],
        "z_factor": [round(Z, 4)],
        "k_ratio": [round(k, 4)],
        "molar_mass": [round(M, 2)],
    }

    t = 0

    # Simulation loop - continue until equilibrium or max time
    # If fixed mode or opening time is 0, use a reasonable safety limit
    if opening_mode == "fixed" or opening_time_s <= 0:
        max_time = 3600  # Safety timeout for fixed/instantaneous opening
    elif valve_action == "close":
        max_time = opening_time_s * 1.2  # Limit closing simulation to 1.2x closing time
    else:
        max_time = opening_time_s * 10  # Opening simulation can run longer for equilibrium

    while t < max_time:
        t += dt

        # Calculate current valve opening fraction based on mode
        if opening_mode == "fixed":
            # Fixed only applies to opening (instant 100%); for closing treat as instant 0%
            opening_fraction = 1.0 if valve_action == "open" else 0.0
        elif opening_mode == "exponential":
            if opening_time_s > 0:
                # Exponential growth: Slow start, steep end
                # Formula: (e^(k*x) - 1) / (e^k - 1) where x = t/T
                ratio = min(t / opening_time_s, 1.0)
                curve_fraction = (np.exp(k_curve * ratio) - 1) / (np.exp(k_curve) - 1)
                # Invert for closing: 100% → 0%
                opening_fraction = (1.0 - curve_fraction) if valve_action == "close" else curve_fraction
            else:
                opening_fraction = 0.0 if valve_action == "close" else 1.0
        elif opening_mode == "quick_acting":
            if opening_time_s > 0:
                ratio = min(t / opening_time_s, 1.0)

                # k_curve controls the "steepness" of the initial jump.
                # Suggested value for your drawing: k_curve = 5.0
                numerator = 1 - np.exp(-k_curve * ratio)
                denominator = 1 - np.exp(-k_curve)
                curve_fraction = numerator / denominator
                # Invert for closing
                opening_fraction = (1.0 - curve_fraction) if valve_action == "close" else curve_fraction
            else:
                opening_fraction = 0.0 if valve_action == "close" else 1.0
        else:  # linear (default)
            if opening_time_s > 0:
                curve_fraction = min(t / opening_time_s, 1.0)
                opening_fraction = (1.0 - curve_fraction) if valve_action == "close" else curve_fraction
            else:
                opening_fraction = 0.0 if valve_action == "close" else 1.0

        A = A_max * opening_fraction

        # Update gas properties dynamically in composition mode
        if gas_state is not None:
            props = gas_state.get_properties(P_down, T)
            M = props.M
            Z = props.Z
            k = props.k

        # Determine flow regime
        if P_down >= P_up:
            massflow_kgs = 0
            regime = "Equilibrium"
        else:
            r = P_down / P_up
            r_c = calculate_critical_pressure_ratio(k)

            if r <= r_c:
                regime = "Choked"
            else:
                regime = "Subsonic"

            # Calculate mass flow rate
            massflow_kgs = calculate_mass_flow_rate(Cd, A, P_up, P_down, k, M, Z, T)

        # Calculate pressure increment
        dP = calculate_dp_dt(Z, T, V, M, massflow_kgs) * dt
        P_down += dP

        # Cap downstream pressure at upstream pressure
        P_down = min(P_down, P_up)

        # Convert and store results
        P_down_psig = pa_to_psig(P_down)
        flowrate_lb_hr = massflow_kgs * KG_S_TO_LB_HR

        results["time"].append(round(t, 2))
        results["pressure_psig"].append(round(P_down_psig, 2))
        results["upstream_pressure_psig"].append(P_up_psig)
        results["flowrate_lb_hr"].append(round(flowrate_lb_hr, 2))
        results["valve_opening_pct"].append(round(opening_fraction * 100, 1))
        results["flow_regime"].append(regime)

        # Store computed properties if in composition mode
        results["z_factor"].append(round(Z, 4))
        results["k_ratio"].append(round(k, 4))
        results["molar_mass"].append(round(M, 2))

        # Stop conditions based on valve action
        if valve_action == "close":
            # For closing: stop when closing time is complete (valve fully closed)
            if t >= opening_time_s:
                break
        else:
            # For opening: stop if pressures are equalized AND time has passed the opening duration
            # This ensures the valve curve is fully plotted even if equilibrium is reached early
            if P_down >= P_up and t >= opening_time_s:
                break

        # Check for equilibrium (flow rate < 0.1% of peak) - redundant but kept for safety logic for now,
        # though the pressure check above likely catches it first.
        # if len(results['flowrate_lb_hr']) > 10:
        #    peak_flow = max(results['flowrate_lb_hr'])
        #    if peak_flow > 0 and flowrate_lb_hr < 0.001 * peak_flow:
        #        break

    return pd.DataFrame(results)
