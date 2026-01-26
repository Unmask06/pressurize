"""Physics calculations for gas flow through orifices (ISO 5167-2)."""

import numpy as np
from pressurize.config.settings import R_UNIVERSAL


def calculate_density(
    pressure: float,
    temperature: float,
    z_factor: float,
    molar_mass_g_mol: float,
) -> float:
    """Calculate gas density from pressure, temperature, Z-factor, and molar mass.

    Uses the real gas equation: ρ = (P · M) / (Z · R · T)

    Args:
        pressure: Absolute pressure in Pa.
        temperature: Temperature in Kelvin.
        z_factor: Compressibility factor (dimensionless).
        molar_mass_g_mol: Molar mass in g/mol.

    Returns:
        Density in kg/m³.
    """
    molar_mass_kg_mol = molar_mass_g_mol / 1000.0
    return (pressure * molar_mass_kg_mol) / (z_factor * R_UNIVERSAL * temperature)


def calculate_critical_pressure_ratio(k: float) -> float:
    """Calculate the critical pressure ratio for sonic/choked flow.

    Formula: r_c = (2/(k+1))^(k/(k-1))
    """
    return (2 / (k + 1)) ** (k / (k - 1))


def calculate_critical_pressure(P_up: float, k: float) -> float:
    """Calculate the critical (choked) downstream pressure.

    Args:
        P_up: Upstream absolute pressure in Pa.
        k: Heat capacity ratio (Cp/Cv).

    Returns:
        Critical downstream pressure in Pa.
    """
    r_c = calculate_critical_pressure_ratio(k)
    return P_up * r_c


def calculate_choked_flow(
    Cd: float,
    A: float,
    P_up: float,
    k: float,
    molar_mass_g_mol: float,
    Z: float,
    T: float,
) -> float:
    """Calculate mass flow rate for choked (sonic) flow conditions.

    Uses the standard choked flow equation with real gas corrections.

    Args:
        Cd: Discharge coefficient (dimensionless).
        A: Effective flow area in m².
        P_up: Upstream absolute pressure in Pa.
        k: Heat capacity ratio (Cp/Cv).
        molar_mass_g_mol: Molar mass in g/mol.
        Z: Compressibility factor (dimensionless).
        T: Gas temperature in Kelvin.

    Returns:
        Mass flow rate in kg/s.
    """
    molar_mass_kg_mol = molar_mass_g_mol / 1000.0

    # Choked flow formula
    term1 = Cd * A * P_up
    term2 = np.sqrt(
        (k * molar_mass_kg_mol) / (Z * R_UNIVERSAL * T) * (2 / (k + 1)) ** ((k + 1) / (k - 1))
    )
    return term1 * term2


def calculate_subsonic_flow(
    Cd: float,
    A: float,
    P_up: float,
    P_down: float,
    k: float,
    molar_mass_g_mol: float,
    Z: float,
    T: float,
) -> float:
    """Calculate mass flow rate for subsonic flow conditions.

    Uses the isentropic flow equation with real gas corrections.

    Args:
        Cd: Discharge coefficient (dimensionless).
        A: Effective flow area in m².
        P_up: Upstream absolute pressure in Pa.
        P_down: Downstream absolute pressure in Pa.
        k: Heat capacity ratio (Cp/Cv).
        molar_mass_g_mol: Molar mass in g/mol.
        Z: Compressibility factor (dimensionless).
        T: Gas temperature in Kelvin.

    Returns:
        Mass flow rate in kg/s.
    """
    molar_mass_kg_mol = molar_mass_g_mol / 1000.0
    r = P_down / P_up

    # Subsonic flow formula
    term1 = Cd * A * P_up
    term2 = np.sqrt(
        (2 * k * molar_mass_kg_mol)
        / ((k - 1) * Z * R_UNIVERSAL * T)
        * (r ** (2 / k) - r ** ((k + 1) / k))
    )
    return term1 * term2


def calculate_orifice_mass_flow(
    Cd: float,
    d: float,
    delta_P: float,
    rho_upstream: float,
    epsilon: float = 1.0,
    beta: float = 1.0,
) -> float:
    """Calculate mass flow rate through an orifice using ISO 5167-2 Equation 1.

    Formula: q_m = (C / sqrt(1 - β⁴)) · ε · (π/4) · d² · sqrt(2 · ΔP · ρ₁)

    Args:
        Cd: Discharge coefficient (dimensionless), typically 0.6-0.9.
        d: Orifice diameter in meters.
        delta_P: Pressure differential (P_up - P_down) in Pa.
        rho_upstream: Upstream gas density in kg/m³.
        epsilon: Expansibility factor (dimensionless). Default 1.0.
        beta: Diameter ratio d/D (dimensionless). Default 1.0.

    Returns:
        Mass flow rate in kg/s.
    """
    if delta_P <= 0:
        return 0.0

    # Velocity of approach factor: 1 / sqrt(1 - β⁴)
    velocity_approach_factor = 1.0 / np.sqrt(1 - beta**4) if beta < 1.0 else 1.0

    # Orifice area: (π/4) · d²
    area = (np.pi / 4) * d**2

    # ISO 5167-2 Equation 1
    q_m = (
        velocity_approach_factor
        * Cd
        * epsilon
        * area
        * np.sqrt(2 * delta_P * rho_upstream)
    )

    return q_m


def calculate_mass_flow_rate(
    Cd: float,
    A: float,
    P_up: float,
    P_down: float,
    k: float,
    molar_mass_g_mol: float,
    Z: float,
    T: float,
    epsilon: float = 1.0,
    beta: float = 1.0,
) -> float:
    """Calculate mass flow rate through orifice with automatic flow regime detection.

    Uses ISO 5167-2 for orifice flow. Automatically determines whether flow is
    choked (sonic) or subsonic based on the pressure ratio, and calculates the
    appropriate pressure differential.

    Args:
        Cd: Discharge coefficient (dimensionless), typically 0.6-0.9.
        A: Effective flow area in m² (used to derive orifice diameter).
        P_up: Upstream absolute pressure in Pa.
        P_down: Downstream absolute pressure in Pa.
        k: Heat capacity ratio (Cp/Cv).
        molar_mass_g_mol: Molar mass in g/mol.
        Z: Compressibility factor (dimensionless).
        T: Gas temperature in Kelvin.
        epsilon: Expansibility factor (dimensionless). Default 1.0.
        beta: Diameter ratio d/D (dimensionless). Default 1.0.

    Returns:
        Mass flow rate in kg/s. Returns 0 if pressures are equalized.
    """
    if P_down >= P_up:
        return 0.0

    # Calculate upstream density
    rho_upstream = calculate_density(P_up, T, Z, molar_mass_g_mol)

    # Derive orifice diameter from area: A = (π/4) · d² => d = sqrt(4A/π)
    d = np.sqrt(4 * A / np.pi)

    # Determine flow regime and calculate ΔP
    r = P_down / P_up
    r_c = calculate_critical_pressure_ratio(k)

    if r <= r_c:
        # Choked (sonic) flow: use critical pressure as effective downstream
        P_critical = calculate_critical_pressure(P_up, k)
        delta_P = P_up - P_critical
    else:
        # Subsonic flow: use actual downstream pressure
        delta_P = P_up - P_down

    return calculate_orifice_mass_flow(Cd, d, delta_P, rho_upstream, epsilon, beta)


def calculate_dp_dt(
    z_factor: float,
    temperature: float,
    volume: float,
    molar_mass_g_mol: float,
    mass_flow: float,
) -> float:
    """Calculate rate of pressure change using the Real Gas Law.

    Derives the pressure change rate from mass conservation and the real gas
    equation of state (PV = ZnRT).

    Formula: dP/dt = (Z·R·T)/(V·M)·ṁ
    """
    molar_mass_kg_mol = molar_mass_g_mol / 1000.0
    return (
        (z_factor * R_UNIVERSAL * temperature)
        / (volume * molar_mass_kg_mol)
        * mass_flow
    )


def calculate_dual_dp_dt(
    mode: str,
    mass_flow_upstream: float,
    mass_flow_downstream: float,
    z_factor: float,
    temperature: float,
    upstream_volume: float,
    downstream_volume: float,
    molar_mass_g_mol: float,
) -> tuple[float, float]:
    """Calculate dp/dt for upstream and downstream volumes based on mode.

    Args:
        mode: "pressurize" (skip upstream), "depressurize" (skip downstream), "equalize" (both)
        mass_flow_upstream: Mass flow rate entering/leaving upstream volume (kg/s)
        mass_flow_downstream: Mass flow rate entering/leaving downstream volume (kg/s)
        z_factor: Compressibility factor
        temperature: Gas temperature (K)
        upstream_volume: Upstream volume (m³)
        downstream_volume: Downstream volume (m³)
        molar_mass_g_mol: Molar mass (g/mol)

    Returns:
        Tuple of (dp_dt_upstream, dp_dt_downstream) in Pa/s.
        Returns 0 for sides that are not calculated based on mode.
    """
    molar_mass_kg_mol = molar_mass_g_mol / 1000.0

    dp_dt_upstream = 0.0
    dp_dt_downstream = 0.0

    if mode == "pressurize":
        # Pressurize: skip upstream dp/dt (upstream is constant)
        # Only downstream changes
        dp_dt_downstream = (
            (z_factor * R_UNIVERSAL * temperature)
            / (downstream_volume * molar_mass_kg_mol)
            * mass_flow_downstream
        )
    elif mode == "depressurize":
        # Depressurize: skip downstream dp/dt (downstream is constant)
        # Only upstream changes
        dp_dt_upstream = (
            (z_factor * R_UNIVERSAL * temperature)
            / (upstream_volume * molar_mass_kg_mol)
            * mass_flow_upstream
        )
    elif mode == "equalize":
        # Equalize: both sides change
        dp_dt_upstream = (
            (z_factor * R_UNIVERSAL * temperature)
            / (upstream_volume * molar_mass_kg_mol)
            * mass_flow_upstream
        )
        dp_dt_downstream = (
            (z_factor * R_UNIVERSAL * temperature)
            / (downstream_volume * molar_mass_kg_mol)
            * mass_flow_downstream
        )

    return dp_dt_upstream, dp_dt_downstream
