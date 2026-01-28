# Technical Background

While Pressurize is easy to use, it is built on rigorous engineering principles. This section explains the science behind the simulator.

## Real Gas Law
Most simple calculators use the Ideal Gas Law ($PV = nRT$). However, at high pressures, gases don't behave "ideally". They compress more or less than expected.

**Pressurize uses the Real Gas Law:**
$$PV = ZnRT$$

Where **Z** is the compressibility factor.
- If $Z=1$, the gas is ideal.
- If $Z \neq 1$, the gas is non-ideal.

Pressurize calculates **Z** dynamically as pressure and temperature change, ensuring accuracy even at very high pressures (e.g., >200 bar).

## Flow Regimes: Sonic vs. Subsonic
Gas flow through a valve can be in one of two states:

1.  **Sonic (Choked) Flow**: The gas is moving at the speed of sound.
    - This happens when the pressure difference is high.
    - Increasing downstream pressure *does not* reduce the flow rate until it rises above a critical point.
2.  **Subsonic Flow**: The gas moves slower than sound.
    - This happens when the vessel is nearly full.
    - As the vessel pressure rises, the flow rate decreases naturally.

**Why it matters:**
Pressurize automatically detects which regime applies at every millisecond of the simulation. You will often see a "flat" maximum flow rate at the start (Sonic), which then drops off as the vessel fills (Subsonic).

## Thermodynamics
When gas flows from a high-pressure source into a lower-pressure vessel, energy is converted.
- The gas inside the vessel often **heats up** due to compression.
- The gas expanding through the valve may **cool down** (Joule-Thomson effect).

Pressurize accounts for these thermal effects to give you a realistic temperature profile, which is critical for choosing materials that can withstand the operating temperatures.
