# Technical Background — Theory & Assumptions

Pressurize is built on rigorous engineering principles. This section explains the science behind the simulator.

## Real-Gas Behavior (Peng-Robinson EOS)

Simple calculators use the Ideal Gas Law ($PV = nRT$). At high pressures, gases deviate significantly from ideal behavior.

**Pressurize uses the Real Gas Law:**

$$PV = ZnRT$$

Where **Z** is the compressibility factor calculated via the **Peng-Robinson equation of state**. This is the same EOS used in commercial process simulators like HYSYS and Aspen Plus.

- If $Z = 1$, the gas behaves ideally.
- If $Z \neq 1$, real-gas corrections are applied.

When using Composition mode, Z is recalculated dynamically at each time step as pressure and temperature change, ensuring accuracy at very high pressures (>200 bar).

## Multi-Component Gas Mixtures

The simulator supports 20+ chemical species including:

Methane, Ethane, Propane, n-Butane, i-Butane, n-Pentane, i-Pentane, n-Hexane, n-Heptane, n-Octane, Nitrogen, CO₂, H₂S, Water, Oxygen, Hydrogen, Carbon Monoxide, Argon, Helium, and Ammonia.

Mixing rules follow the standard Peng-Robinson formulation, and the heat capacity ratio ($k = C_p/C_v$) is derived from the EOS — not assumed constant.

## Gauge vs Absolute Pressure

All user-facing pressures are in **gauge**. Internally, the simulation adds atmospheric pressure (101,325 Pa) to convert to absolute pressure for thermodynamic calculations:

$$P_{\text{abs}} = P_{\text{gauge}} + P_{\text{atm}}$$

Results are converted back to gauge before display.

## Flow Regimes — Sonic (Choked) vs Subsonic

Gas flow through a valve can be in one of two states:

1. **Sonic (Choked) Flow** — the gas moves at the speed of sound. This occurs when the pressure ratio across the valve exceeds a critical threshold. Increasing downstream pressure does _not_ reduce the flow rate until it rises above this threshold.

2. **Subsonic Flow** — the gas moves below the speed of sound. As the downstream vessel fills, the pressure ratio decreases and flow rate drops naturally.

Pressurize automatically detects which regime applies at every time step. In the charts, you'll often see a flat maximum flow rate at the start (sonic), which then curves downward as the vessel fills (subsonic).

## Valve Opening Profiles

The valve opening fraction $f(t)$ varies by mode:

| Mode              | Profile                                                      |
| ----------------- | ------------------------------------------------------------ |
| Linear            | $f = t / t_{\text{open}}$                                    |
| Exponential       | $f = (e^{k \cdot t/t_{\text{open}}} - 1) / (e^k - 1)$        |
| Quick Acting      | $f = \dfrac{1 - e^{-k \cdot t/t_{\text{open}}}}{1 - e^{-k}}$ |
| Orifice (Instant) | $f = 1$ at all times                                         |

The curve factor $k$ controls steepness for Exponential and Quick Acting profiles.

## Time-Stepping

The simulation uses a fixed time step ($\Delta t$, default 0.5 s). At each step, the mass flow rate is calculated based on the current valve opening, upstream/downstream pressures, and flow regime. Pressures are then updated based on the mass balance in each vessel.

For opening scenarios, the simulation stop condition is checked each step and terminates when **both** conditions are true:

- $t \ge t_{\max}$
- flow is at equilibrium (within tolerance)

For closing scenarios, it stops when valve opening reaches 0%.

## Core Formulae Used in the Simulator

The following are the key equations used directly by the simulation engine.

### 1) Real-gas density

$$\rho = \frac{P M}{Z R T}$$

### 2) Critical pressure ratio (choked-flow threshold)

$$r_c = \left(\frac{2}{k+1}\right)^{\frac{k}{k-1}}$$

Where $r = P_{\text{down}}/P_{\text{up}}$.

- If $r \le r_c$: choked flow
- If $r > r_c$: subsonic flow

### 3) Effective valve area

$$A(t) = A_{\max} \cdot f(t), \quad A_{\max} = \pi\left(\frac{d}{2}\right)^2$$

### 4) Orifice mass-flow form

$$\dot{m} = C_d\,\epsilon\,A\,\sqrt{2\,\Delta P\,\rho_{\text{up}}}$$

With regime-dependent pressure drop:

- Choked: $\Delta P = P_{\text{up}} - P_{\text{critical}}$
- Subsonic: $\Delta P = P_{\text{up}} - P_{\text{down}}$

### 5) Pressure-rate equation from real-gas mass balance

$$\frac{dP}{dt} = \frac{ZRT}{VM}\,\dot{m}$$

Applied to each vessel according to mode (pressurize, depressurize, equalize).

### 6) Time integration

$$P_{n+1} = P_n + \left(\frac{dP}{dt}\right)\Delta t$$

---

## Cv-Based Flow Model (ISA/IEC 60534)

As an alternative to the orifice-ID model, Pressurize supports a **Cv-based flow model** following the ISA/IEC 60534 valve sizing standard. This is the industry-standard method for sizing and rating control valves.

### Sizing Constant

The equations use the **N₆** numerical constant for mass-flow units:

$$N_6 = 63.338 \quad \text{(lb/hr, psia, lb/ft³)}$$

Internally all calculations are performed in FPS units and converted back to SI.

### Gas Flow Through a Cv-Rated Valve

$$W = N_6 \cdot F_P \cdot C_v \cdot Y \sqrt{x \cdot P_1 \cdot \rho_1}$$

Where:

| Symbol   | Meaning                                                                           |
| -------- | --------------------------------------------------------------------------------- |
| $W$      | Mass flow rate (lb/hr)                                                            |
| $C_v$    | Valve flow coefficient                                                            |
| $F_P$    | Piping geometry factor (assumed 1.0)                                              |
| $P_1$    | Upstream pressure (psia)                                                          |
| $\rho_1$ | Upstream density (lb/ft³)                                                         |
| $x$      | Pressure-drop ratio: $x = \Delta P / P_1$                                         |
| $Y$      | Expansion factor                                                                  |
| $x_T$    | Pressure-drop ratio factor (valve characteristic, user-configurable, default 0.7) |

**Expansion factor:**

$$Y = 1 - \frac{x}{3\,F_k\,x_T}$$

$$F_k = \frac{k}{1.4}$$

**Choked-flow limit:** $x$ is capped at $F_k \cdot x_T$. When $x \ge F_k \cdot x_T$, the flow is **choked** and $Y$ is clamped to $2/3$.

### Liquid Flow Through a Cv-Rated Valve

$$W = N_6 \cdot F_P \cdot C_v \sqrt{\rho_L \cdot \Delta P_{\text{eff}}}$$

Where $\Delta P_{\text{eff}} = \min(\Delta P,\;\Delta P_{\max})$:

$$\Delta P_{\max} = F_L^2 \left(P_1 - F_F \cdot P_v\right)$$

$$F_F = 0.96 - 0.28\sqrt{\frac{P_v}{P_c}}$$

| Symbol   | Meaning                                       |
| -------- | --------------------------------------------- |
| $\rho_L$ | Liquid density (lb/ft³)                       |
| $F_L$    | Liquid pressure-recovery factor (default 0.9) |
| $P_v$    | Vapor pressure (psia)                         |
| $P_c$    | Critical pressure (psia)                      |
| $F_F$    | Liquid critical-pressure ratio factor         |

### Two-Phase Flow (Weighted Blend)

For two-phase (gas + liquid) conditions, the model calculates gas-phase and liquid-phase flow rates independently, then combines them using the vapor mass fraction $\alpha$:

$$W_{\text{two-phase}} = (1 - \alpha)\,W_{\text{liquid}} + \alpha\,W_{\text{gas}}$$

### Cv and Valve Opening

When using the Cv model, the effective Cv at each time step is:

$$C_{v,\text{eff}} = C_v \cdot f(t)$$

where $f(t)$ is the valve opening fraction from the selected opening profile (linear, exponential, quick-acting, or orifice). This simulates linear trim behavior.
