# How to Use — Quickstart

This guide walks you through setting up and running a simulation in Pressurize.

## Basic Workflow

### 1. Choose a Simulation Mode

Select one of the three modes at the top of the form:

- **🔼 Pressurize** — upstream is a constant supply; downstream vessel fills up.
- **🔽 Depressurize** — downstream is constant; upstream vessel bleeds down.
- **⇌ Equalize** — both vessels exchange gas until pressures balance.

### 2. Define the Upstream Vessel

- **Pressure** — upstream gauge pressure (e.g., `500 psi (g)`).
- **Temperature** — upstream temperature (e.g., `70 °F`).
- **Volume** — shown only in Depressurize and Equalize modes (e.g., `100 ft³`).

### 3. Define the Downstream Vessel

- **Pressure** — initial downstream gauge pressure (e.g., `0 psi (g)` for atmospheric).
- **Temperature** — downstream temperature (e.g., `70 °F`).
- **Volume** — shown only in Pressurize and Equalize modes (e.g., `100 ft³`).

### 4. Configure the Valve

- **Valve ID** — internal diameter (e.g., `2 in` or `50 mm` depending on unit system).
- **Discharge Coeff (Cd)** — typically `0.65` to `0.9`.
- **Valve Action** — `Open` (0→100%) or `Close` (100→0%).
- **Opening Time** — how long the valve takes to fully open or close (e.g., `5 s`).
- **Opening Mode** — choose from:
  - `Linear` — constant rate of opening
  - `Exponential` — slow start, fast finish
  - `Quick Acting` — fast start, slow finish
  - `Fixed (Instant)` — full open/close immediately
- **Curve Factor (k)** — controls steepness for Exponential and Quick Acting modes.

### 5. Set Gas Properties

Choose between two property modes:

- **Manual** — enter Molar Mass (g/mol), Z-Factor, and k (Cp/Cv) directly.
- **Composition** — paste a composition string (e.g., `Methane=0.9387, Nitrogen=0.0433, CO2=0.0054`). The app fetches Z, k, and MW automatically from the Peng-Robinson EOS at the current upstream conditions.

Preset compositions are available: Natural Gas, Pure Methane, Rich Gas, Sour Gas, and Lean Gas.

### 6. Run the Simulation

Click **Run Simulation**. Results stream live:

- **Charts** update in real time showing Pressure vs Time and Flow Rate vs Time.
- **KPI Cards** appear when complete: Peak Flow, Final Pressure, Equilibrium Time, and Total Mass.
- **Results Table** shows every time step with pressure, flow rate, valve opening, and flow regime.

### 7. Change Unit System

Open the **Settings** panel (gear icon) and select a unit system. All inputs, outputs, charts, and KPIs re-render in the new units immediately. Available systems:

- Imperial (psi, °F, ft³, lb)
- Engineering Field (psi, °F, ft³, lb/h)
- Engineering SI (bar, °C, m³, kg/h)
- SI (Pa, K, m³, kg/s)
- CGS (Ba, °C, cm³, g/s)

## Example: Filling a Tank

1. Mode: **Pressurize**
2. Upstream: `500 psi (g)`, `70 °F`
3. Downstream: `0 psi (g)`, `70 °F`, `100 ft³`
4. Valve: `2 in` ID, Cd = `0.9`, Action = Open, Linear, `5 s`
5. Property Mode: Composition → `Nitrogen=1.0`
6. Click **Run Simulation**

Early in the simulation you'll see flat maximum flow (choked/sonic regime). As the vessel fills, flow decreases naturally (subsonic). The KPIs show peak flow, how long to equalize, and total mass transferred.

## Example: Rapid Failure-Open Safety Check

Same setup as above, but change:

- Opening Mode → `Fixed (Instant)`

Compare the pressure rise rate and peak flow against the slower Linear case. This worst-case scenario helps size relief devices and verify system safety margins.

## Exporting Results

Click the **Download Report** button to export a PDF capturing all inputs, KPI values, and charts.
