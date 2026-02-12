# Overview — What Pressurize Does

**Pressurize** is a browser-based simulation tool for engineers who need to model gas flow through valves into or out of pressure vessels. It answers questions like:

- How long will it take to reach a target gauge pressure?
- What is the peak flow rate through the valve?
- Is the valve sized correctly for this scenario?
- What happens in a worst-case rapid-opening event?

## Simulation Modes

Pressurize supports three distinct simulation modes:

| Mode             | What changes              | What stays constant               |
| ---------------- | ------------------------- | --------------------------------- |
| **Pressurize**   | Downstream pressure rises | Upstream pressure held constant   |
| **Depressurize** | Upstream pressure drops   | Downstream pressure held constant |
| **Equalize**     | Both pressures evolve     | Both vessels interact dynamically |

## Key Capabilities

### Real-Gas Thermodynamics

The simulator uses the **Peng-Robinson equation of state** to calculate compressibility (Z), heat capacity ratio (k), and molar mass (MW) from a user-defined gas composition. 20+ species are supported, including methane, ethane, propane, CO₂, H₂S, nitrogen, hydrogen, and more.

You can also enter Z, k, and MW manually if you prefer.

### Gauge Pressure Throughout

All pressure inputs and outputs are in **gauge pressure**. The labels show units like `psi (g)` or `bar (g)`. Internally, the simulator converts to absolute pressure for thermodynamic calculations and converts back to gauge for display.

### Flexible Unit Systems

Switch between unit systems at any time via the settings panel:

| Dimension   | Imperial | Engg Field | Engg SI | SI     | CGS    |
| ----------- | -------- | ---------- | ------- | ------ | ------ |
| Pressure    | psi (g)  | psi (g)    | bar (g) | Pa (g) | Ba (g) |
| Temperature | °F       | °F         | °C      | K      | °C     |
| Volume      | ft³      | ft³        | m³      | m³     | cm³    |
| Valve ID    | in       | in         | mm      | mm     | mm     |
| Mass Flow   | lb/s     | lb/h       | kg/h    | kg/s   | g/s    |

### Live Streaming Results

Simulation results stream in real time via Server-Sent Events (SSE). Charts and the results table update progressively as the backend computes each time step.

### Four KPIs at a Glance

After each simulation, four key performance indicators are displayed:

1. **Peak Flow Rate** — maximum mass flow through the valve
2. **Final Pressure** — equilibrium or end-state gauge pressure
3. **Equilibrium Time** — time to reach pressure balance
4. **Total Mass Flow** — cumulative mass transferred

### PDF Report Export

Export a complete report capturing inputs, KPIs, and charts for sharing with colleagues.

## Intended Users

- **Process Engineers** designing gas systems
- **Mechanical Engineers** selecting valves and vessels
- **Safety Analysts** verifying system safety under transient conditions
