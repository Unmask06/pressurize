# How to Use — Quickstart

This guide will walk you through setting up and running a simulation in Pressurize.

## Basic Workflow (Quickstart Steps)

In Pressurize, you begin by choosing a simulation mode—Pressurize, Depressurize, or Equalize—so the app knows which side evolves in time. 

You then describe the upstream and downstream vessels in familiar units: pressures in psig, temperatures in °F, and volumes in ft³. With the vessels framed, you turn to the valve: a simple set of controls lets you set the internal diameter in inches, the discharge coefficient, whether the valve is opening or closing, and how it moves (linear, exponential, quick acting, or instant). 

Finally, you decide how to handle gas properties: paste a composition to have MW, Z, and k filled in automatically, or enter those values manually. With everything in place, you run the simulation and explore the results as the system evolves.

## Example 1: Filling a Tank (UI-aligned)

This example follows the form fields in the app.

### Step 1 — Source Conditions

- **Upstream Pressure (psig)**: enter the supply gauge pressure (e.g., `500`).
- **Upstream Temperature (°F)**: default `70 °F`.
- **Property Mode / Composition**: set `Property Mode` to `Composition` and paste a composition string (e.g., `Nitrogen=1.0`). The app calls the properties API and fills `MW (g/mol)`, `Z-Factor`, and `k (Cp/Cv)` automatically.

### Step 2 — Valve Configuration

- **Valve ID (in)**: internal diameter in inches (e.g., `2.0`).
- **Discharge Coeff (Cd)**: e.g., `0.9`.
- **Valve Action**: `Open` (default) or `Close`.
- **Opening Time (s)**: e.g., `5` seconds.
- **Opening Mode**: choose `Linear`, `Exponential`, `Quick Acting`, or `Fixed (Instant)`.
- **Curve Factor (k)**: used with `Exponential` or `Quick Acting` modes.

### Step 3 — Vessel Definition

- **Downstream Volume (ft³)**: e.g., `100`.
- **Initial Pressure (psig)**: downstream initial gauge pressure (e.g., `0` for atmospheric gauge).
- **Downstream Temperature (°F)**: default `70 °F`.

### Step 4 — Run Simulation

- Click the **Run Simulation** button. While the backend is working the button shows `Running...`.
- If results exist, click **📊 View Results Table** to inspect time-stepped rows, or open the charts to view `Pressure vs Time` and `Flow Rate`.
  This example follows the form fields in the app.

Imagine you’re filling a downstream vessel from an upstream supply. On the upstream side, you type 500 into Pressure (psig) and leave Temperature at 70 °F. In Gas Properties, you switch Property Mode to Composition and paste `Nitrogen=1.0`; almost instantly the app fills in MW, Z-Factor, and k based on the current conditions.

Moving to the valve, you enter 2.0 for Valve ID (in), set Cd to 0.9, keep Valve Action as Open, and choose a Linear opening with 5 seconds. If you want a snappier start, you can pick Exponential and nudge the curve factor k.

On the downstream side, you set a vessel volume of 100 ft³, an initial pressure of 0 psig, and a temperature of 70 °F. When you click Run Simulation, the button changes to “Running…” and the backend steps through the physics. As soon as results arrive, you open the 📊 View Results Table or watch the Pressure vs Time and Flow Rate charts evolve. Early on you’ll often see choked flow and a flat maximum; as the vessel fills, the flow naturally tails off.

## Example 2 — Quick-Acting / Instant Opening Safety Check

For a rapid failure-open scenario, you flip the valve profile to Fixed (Instant) or Quick Acting. With the same source and vessel settings as before, an instant-opening valve drives a much faster pressure rise and higher peak flows. Comparing these curves against a slower Linear ramp helps you size relief devices and understand worst‑case transients.

## Exporting Results (PDF)

When it’s time to share the outcome, you export a PDF that captures inputs and key charts so colleagues can review the scenario without opening the app.
