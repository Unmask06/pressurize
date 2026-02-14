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

| Mode            | Profile                                               |
| --------------- | ----------------------------------------------------- |
| Linear          | $f = t / t_{\text{open}}$                             |
| Exponential     | $f = (e^{k \cdot t/t_{\text{open}}} - 1) / (e^k - 1)$ |
| Quick Acting    | $f = 1 - e^{-k \cdot t/t_{\text{open}}}$ (normalized) |
| Fixed (Instant) | $f = 1$ at all times                                  |

The curve factor $k$ controls steepness for Exponential and Quick Acting profiles.

## Time-Stepping

The simulation uses a fixed time step ($\Delta t$, default 0.5 s). At each step, the mass flow rate is calculated based on the current valve opening, upstream/downstream pressures, and flow regime. Pressures are then updated based on the mass balance in each vessel.

The simulation terminates when pressures equalize (within tolerance) or the maximum simulation time is reached.
