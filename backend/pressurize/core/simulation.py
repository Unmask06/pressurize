"""Dynamic valve pressurization simulation engine."""

from typing import Literal

import numpy as np
import pandas as pd

from pressurize.config.settings import FT3_TO_M3, INCH_TO_M, KG_S_TO_LB_HR, TIME_STEP
from pressurize.core.physics import (
    calculate_critical_pressure_ratio,
    calculate_dual_dp_dt,
    calculate_mass_flow_rate,
)
from pressurize.core.properties import GasState
from pressurize.utils.converters import fahrenheit_to_kelvin, pa_to_psig, psig_to_pa


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
    composition: float | None = None,
    mode: Literal["pressurize", "depressurize", "equalize"] = "equalize",
    upstream_volume_ft3: float | None = None,
    upstream_temp_f: float | None = None,
    downstream_volume_ft3: float | None = None,
    downstream_temp_f: float | None = None,
) -> pd.DataFrame:
    """Run the valve pressurization simulation.

    Simulates gas flow through a valve with dual upstream/downstream vessels and dynamic
    pressure and flow rate calculations over time.

    Args:
        P_up_psig: Upstream pressure in psig.
        P_down_init_psig: Initial downstream pressure in psig.
        volume_ft3: Legacy vessel volume in ft³ (used if downstream_volume_ft3 not provided).
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
        mode: "pressurize", "depressurize", or "equalize". Controls which sides compute dp/dt.
        upstream_volume_ft3: Upstream vessel volume in ft³. Required for equalize mode.
        upstream_temp_f: Upstream vessel temperature in °F. TODO: Currently constant.
        downstream_volume_ft3: Downstream vessel volume in ft³. Uses volume_ft3 if not provided.
        downstream_temp_f: Downstream vessel temperature in °F. TODO: Currently constant.

    Returns:
        DataFrame with columns: time, pressure_psig, upstream_pressure_psig,
        downstream_pressure_psig, flowrate_lb_hr, valve_opening_pct, flow_regime,
        dp_dt_upstream_psig_s, dp_dt_downstream_psig_s.
    """
    # Convert to SI units
    P_up = psig_to_pa(P_up_psig)
    P_down = psig_to_pa(P_down_init_psig)

    # Handle volume and temperature setup
    # If separate volumes not provided, use legacy volume_ft3 for downstream
    V_down = (downstream_volume_ft3 or volume_ft3) * FT3_TO_M3
    V_up = (upstream_volume_ft3 or volume_ft3) * FT3_TO_M3

    # Temperature: use provided values or default to temp_f
    # TODO: Add dynamic temperature model (energy balance) in future
    T = fahrenheit_to_kelvin(temp_f)
    T_up = fahrenheit_to_kelvin(upstream_temp_f or temp_f)
    T_down = fahrenheit_to_kelvin(downstream_temp_f or temp_f)

    valve_radius = (valve_id_inch * INCH_TO_M) / 2
    A_max = np.pi * valve_radius**2
    Cd = discharge_coeff

    # Initialize gas properties based on mode
    # In equalize mode: use dual gas states (upstream and downstream) for accuracy
    # In other modes: use single gas state for the changing side (faster)
    if property_mode == "composition" and composition:
        if mode == "equalize":
            # Dual gas state for equalize mode
            gas_state_up = GasState(composition)
            gas_state_down = GasState(composition)
            # Get initial properties
            props_up = gas_state_up.get_properties(P_up, T_up)
            props_down = gas_state_down.get_properties(P_down, T_down)
            M = props_down.M  # Use downstream for primary (can use either)
            Z = props_down.Z
            k = props_down.k
        elif mode == "pressurize":
            # Only downstream changes - use downstream gas state
            gas_state_up = None
            gas_state_down = GasState(composition)
            props_down = gas_state_down.get_properties(P_down, T_down)
            M = props_down.M
            Z = props_down.Z
            k = props_down.k
        else:  # depressurize
            # Only upstream changes - use upstream gas state
            gas_state_up = GasState(composition)
            gas_state_down = None
            props_up = gas_state_up.get_properties(P_up, T_up)
            M = props_up.M
            Z = props_up.Z
            k = props_up.k
    else:
        # Manual mode - use provided values
        gas_state_up = None
        gas_state_down = None
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
        "pressure_psig": [P_down_init_psig],  # For backward compatibility
        "upstream_pressure_psig": [P_up_psig],
        "downstream_pressure_psig": [P_down_init_psig],
        "flowrate_lb_hr": [0],
        "valve_opening_pct": [initial_opening],
        "flow_regime": ["None"],
        "dp_dt_upstream_psig_s": [0.0],
        "dp_dt_downstream_psig_s": [0.0],
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
        max_time = (
            opening_time_s * 10
        )  # Opening simulation can run longer for equilibrium

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
                opening_fraction = (
                    (1.0 - curve_fraction)
                    if valve_action == "close"
                    else curve_fraction
                )
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
                opening_fraction = (
                    (1.0 - curve_fraction)
                    if valve_action == "close"
                    else curve_fraction
                )
            else:
                opening_fraction = 0.0 if valve_action == "close" else 1.0
        else:  # linear (default)
            if opening_time_s > 0:
                curve_fraction = min(t / opening_time_s, 1.0)
                opening_fraction = (
                    (1.0 - curve_fraction)
                    if valve_action == "close"
                    else curve_fraction
                )
            else:
                opening_fraction = 0.0 if valve_action == "close" else 1.0

        A = A_max * opening_fraction

        # Update gas properties dynamically in composition mode
        if (
            mode == "equalize"
            and gas_state_up is not None
            and gas_state_down is not None
        ):
            # Equalize mode: update both upstream and downstream properties
            props_up = gas_state_up.get_properties(P_up, T_up)
            props_down = gas_state_down.get_properties(P_down, T_down)
            # Use downstream for primary properties (both sides should have similar M, but Z and k can differ)
            M = props_down.M
            Z = props_down.Z
            k = props_down.k
        elif mode == "pressurize" and gas_state_down is not None:
            # Pressurize mode: only downstream changes
            props_down = gas_state_down.get_properties(P_down, T_down)
            M = props_down.M
            Z = props_down.Z
            k = props_down.k
        elif mode == "depressurize" and gas_state_up is not None:
            # Depressurize mode: only upstream changes
            props_up = gas_state_up.get_properties(P_up, T_up)
            M = props_up.M
            Z = props_up.Z
            k = props_up.k

        # Determine flow regime based on pressure differential
        # Flow is always from high to low pressure
        pressure_diff = P_up - P_down

        if abs(pressure_diff) < 1:  # Effectively equilibrium
            massflow_kgs = 0
            regime = "Equilibrium"
            dp_dt_up = 0.0
            dp_dt_down = 0.0
        else:
            r = P_down / P_up if P_up > 0 else 1.0
            r_c = calculate_critical_pressure_ratio(k)

            if r <= r_c:
                regime = "Choked"
            else:
                regime = "Subsonic"

            # Calculate mass flow rate (positive means flow from upstream to downstream)
            massflow_kgs = calculate_mass_flow_rate(Cd, A, P_up, P_down, k, M, Z, T)

            # For dual-vessel mode, flow goes from high-pressure to low-pressure
            # Upstream loses mass (negative), downstream gains mass (positive)
            mass_flow_up = -massflow_kgs  # Upstream loses mass
            mass_flow_down = massflow_kgs  # Downstream gains mass

            # Calculate dp/dt for both sides based on mode
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

        # Update pressures based on dp/dt
        if dp_dt_up != 0.0:
            dP_up = dp_dt_up * dt
            P_up += dP_up

        if dp_dt_down != 0.0:
            dP_down = dp_dt_down * dt
            P_down += dP_down

        # Convert to psig for storage and comparisons
        P_up_psig_current = pa_to_psig(P_up)
        P_down_psig_current = pa_to_psig(P_down)

        # Convert dp/dt to psig/s for output
        dp_dt_up_psig_s = (
            dp_dt_up / 6894.76 if dp_dt_up != 0.0 else 0.0
        )  # Pa/s to psig/s
        dp_dt_down_psig_s = dp_dt_down / 6894.76 if dp_dt_down != 0.0 else 0.0

        flowrate_lb_hr = massflow_kgs * KG_S_TO_LB_HR

        results["time"].append(round(t, 2))
        results["pressure_psig"].append(
            round(P_down_psig_current, 2)
        )  # Backward compatibility
        results["upstream_pressure_psig"].append(round(P_up_psig_current, 2))
        results["downstream_pressure_psig"].append(round(P_down_psig_current, 2))
        results["flowrate_lb_hr"].append(round(flowrate_lb_hr, 2))
        results["valve_opening_pct"].append(round(opening_fraction * 100, 1))
        results["flow_regime"].append(regime)
        results["dp_dt_upstream_psig_s"].append(round(dp_dt_up_psig_s, 6))
        results["dp_dt_downstream_psig_s"].append(round(dp_dt_down_psig_s, 6))

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
