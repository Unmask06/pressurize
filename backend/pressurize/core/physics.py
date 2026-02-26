"""Physics calculations for gas flow through orifices (ISO 5167-2) and Cv valves (ISA/IEC 60534)."""

import numpy as np

from pressurize.config.settings import (
    KGM3_TO_LBFT3,
    LBHR_TO_KGS,
    N6_FPS,
    PA_TO_PSIA,
    R_UNIVERSAL,
)


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
        (k * molar_mass_kg_mol)
        / (Z * R_UNIVERSAL * T)
        * (2 / (k + 1)) ** ((k + 1) / (k - 1))
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


# ---------------------------------------------------------------------------
# ISA/IEC 60534 Cv-based flow calculations
# All functions accept SI inputs, convert to FPS internally, compute with
# N6 = 63.338, and convert the output (lb/hr) back to kg/s.
# ---------------------------------------------------------------------------


def calculate_cv_gas_flow(
    Cv: float,
    P_up_pa: float,
    P_down_pa: float,
    k: float,
    rho_upstream_kgm3: float,
    x_T: float = 0.7,
) -> tuple[str, float]:
    """Calculate mass flow rate through a control valve using ISA/IEC 60534 gas sizing.

    Converts SI inputs to FPS, applies the standard Cv gas equation with
    expansion factor Y and specific-heat-ratio factor Fk, then converts
    the result back to kg/s.

    Formula (FPS):
        W = N6 · Fp · Cv · Y · √(x · P1 · ρ1)
        Fp = 1.0 (no piping reducers)

    Args:
        Cv: Valve flow coefficient (US gpm / √psi).
        P_up_pa: Upstream absolute pressure in Pa.
        P_down_pa: Downstream absolute pressure in Pa.
        k: Heat capacity ratio (Cp/Cv).
        rho_upstream_kgm3: Upstream gas density in kg/m³.
        x_T: Terminal pressure drop ratio (dimensionless, typically 0.7).

    Returns:
        Tuple of (regime, mass_flow_kgs):
            regime: "Choked" if x ≥ Fk·xT, "Subsonic" otherwise.
            mass_flow_kgs: Mass flow rate in kg/s. Returns 0 if P_down ≥ P_up.
    """
    if P_down_pa >= P_up_pa:
        return "Equilibrium", 0.0

    # Convert SI → FPS
    Pu_psia = P_up_pa * PA_TO_PSIA
    Pd_psia = P_down_pa * PA_TO_PSIA
    rho_lbft3 = rho_upstream_kgm3 * KGM3_TO_LBFT3

    # Specific heat ratio factor
    Fk = k / 1.4

    # Pressure drop ratio
    x = (Pu_psia - Pd_psia) / Pu_psia

    # Terminal (choked) limit
    x_limit = Fk * x_T

    # Determine regime and cap x
    if x >= x_limit:
        regime = "Choked"
        x_sizing = x_limit
    else:
        regime = "Subsonic"
        x_sizing = x

    # Expansion factor Y (clamped to 2/3 minimum)
    Y = 1.0 - (x_sizing / (3.0 * x_limit))
    if Y < 2.0 / 3.0:
        Y = 2.0 / 3.0

    # ISA/IEC 60534 gas mass flow (lb/hr)
    Fp = 1.0  # Piping geometry factor (no reducers)
    W_lbhr = N6_FPS * Fp * Cv * Y * np.sqrt(x_sizing * Pu_psia * rho_lbft3)

    # Convert FPS → SI
    mass_flow_kgs = W_lbhr * LBHR_TO_KGS

    return regime, mass_flow_kgs


def calculate_cv_liquid_flow(
    Cv: float,
    P_up_pa: float,
    P_down_pa: float,
    rho_liquid_kgm3: float,
    P_vapor_pa: float,
    P_critical_pa: float,
    F_L: float = 0.9,
) -> tuple[str, float]:
    """Calculate liquid mass flow rate through a control valve using ISA/IEC 60534.

    Handles both sub-critical and choked (flashing) liquid flow conditions.

    Formula (FPS):
        W = N6 · Fp · Cv · √(ρ_L · ΔP_eff)

    Args:
        Cv: Valve flow coefficient (US gpm / √psi).
        P_up_pa: Upstream absolute pressure in Pa.
        P_down_pa: Downstream absolute pressure in Pa.
        rho_liquid_kgm3: Upstream liquid density in kg/m³.
        P_vapor_pa: Fluid vapor pressure in Pa.
        P_critical_pa: Fluid critical pressure in Pa.
        F_L: Liquid pressure recovery factor (dimensionless, typically 0.9).

    Returns:
        Tuple of (regime, mass_flow_kgs):
            regime: "Choked" if actual ΔP exceeds maximum, "Subsonic" otherwise.
            mass_flow_kgs: Mass flow rate in kg/s. Returns 0 if P_down ≥ P_up.
    """
    if P_down_pa >= P_up_pa:
        return "Equilibrium", 0.0

    # Convert SI → FPS
    Pu_psia = P_up_pa * PA_TO_PSIA
    Pd_psia = P_down_pa * PA_TO_PSIA
    Pv_psia = P_vapor_pa * PA_TO_PSIA
    Pc_psia = P_critical_pa * PA_TO_PSIA
    rho_lbft3 = rho_liquid_kgm3 * KGM3_TO_LBFT3

    # Liquid critical pressure ratio factor
    FF = 0.96 - 0.28 * np.sqrt(Pv_psia / Pc_psia) if Pc_psia > 0 else 0.96

    # Maximum allowable pressure drop for choking
    dP_max = (F_L**2) * (Pu_psia - FF * Pv_psia)

    # Actual pressure drop
    dP = Pu_psia - Pd_psia

    # Effective pressure drop and regime
    if dP > dP_max:
        regime = "Choked"
        dP_eff = dP_max
    else:
        regime = "Subsonic"
        dP_eff = dP

    if dP_eff <= 0:
        return "Equilibrium", 0.0

    # ISA/IEC 60534 liquid mass flow (lb/hr)
    Fp = 1.0
    W_lbhr = N6_FPS * Fp * Cv * np.sqrt(rho_lbft3 * dP_eff)

    # Convert FPS → SI
    mass_flow_kgs = W_lbhr * LBHR_TO_KGS

    return regime, mass_flow_kgs


def calculate_cv_two_phase_flow(
    vapor_fraction: float,
    Cv: float,
    rho_liquid_kgm3: float,
    rho_vapor_kgm3: float,
    P_up_pa: float,
    P_down_pa: float,
    P_vapor_pa: float,
    P_critical_pa: float,
    k: float = 1.4,
    x_T: float = 0.7,
    F_L: float = 0.9,
) -> tuple[str, float]:
    """Calculate two-phase mass flow through a control valve (ISA/IEC 60534).

    Blends liquid and gas Cv flow results weighted by the vapor mass fraction.

    Args:
        vapor_fraction: Vapor mass fraction (0 = pure liquid, 1 = pure gas).
        Cv: Valve flow coefficient (US gpm / √psi).
        rho_liquid_kgm3: Liquid phase density in kg/m³.
        rho_vapor_kgm3: Vapor phase density in kg/m³.
        P_up_pa: Upstream absolute pressure in Pa.
        P_down_pa: Downstream absolute pressure in Pa.
        P_vapor_pa: Fluid vapor pressure in Pa.
        P_critical_pa: Fluid critical pressure in Pa.
        k: Heat capacity ratio (Cp/Cv) for vapor.
        x_T: Terminal pressure drop ratio (dimensionless).
        F_L: Liquid pressure recovery factor (dimensionless).

    Returns:
        Tuple of (regime, mass_flow_kgs).

    Raises:
        ValueError: If vapor_fraction is not between 0 and 1.
    """
    if not (0.0 <= vapor_fraction <= 1.0):
        raise ValueError(f"vapor_fraction must be 0–1, got {vapor_fraction}")

    if P_down_pa >= P_up_pa:
        return "Equilibrium", 0.0

    # Pure liquid
    if vapor_fraction == 0.0:
        return calculate_cv_liquid_flow(
            Cv, P_up_pa, P_down_pa, rho_liquid_kgm3, P_vapor_pa, P_critical_pa, F_L
        )

    # Pure gas
    if vapor_fraction == 1.0:
        return calculate_cv_gas_flow(Cv, P_up_pa, P_down_pa, k, rho_vapor_kgm3, x_T)

    # Mixed phase: weighted blend
    regime_liq, flow_liq = calculate_cv_liquid_flow(
        Cv, P_up_pa, P_down_pa, rho_liquid_kgm3, P_vapor_pa, P_critical_pa, F_L
    )
    regime_gas, flow_gas = calculate_cv_gas_flow(
        Cv, P_up_pa, P_down_pa, k, rho_vapor_kgm3, x_T
    )

    mass_flow = (1.0 - vapor_fraction) * flow_liq + vapor_fraction * flow_gas

    # Report regime of the dominant phase
    regime = (
        regime_gas if vapor_fraction >= 0.5 else regime_liq
    )  # TODO: Check if this is the best way to report regime for two-phase flow

    return regime, mass_flow
