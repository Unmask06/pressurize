# How to Use

This guide will walk you through setting up and running a simulation in Pressurize.

## Basic Workflow

1.  **Define Source Conditions**: Set the pressure and temperature of the gas supply.
2.  **Configure the Valve**: Choose the valve characteristics and opening profile.
3.  **Define the Vessel**: Set the volume and initial conditions of the tank you are filling.
4.  **Run Simulation**: Start the calculation and view the results.

## Example 1: Filling a Nitrogen Tank

Let's simulate filling a 5 m³ tank with Nitrogen from a 100 bar source.

### Step 1: Source Setup
- **Supply Pressure**: 100 bar
- **Supply Temperature**: 25°C
- **Gas Composition**: Select "Nitrogen" (N2) from the presets or define a mixture (100% N2).

### Step 2: Valve Configuration
We want to open the valve linearly over 10 seconds.
- **Valve Cv**: 50 (a measure of valve flow capacity)
- **Opening Mode**: Linear
- **Opening Time**: 10 seconds

### Step 3: Vessel Setup
- **Vessel Volume**: 5 m³
- **Initial Pressure**: 1 bar (atmospheric)
- **Initial Temperature**: 25°C

### Step 4: Run
Click the **"Run Simulation"** button.

**What to look for:**
- Watch the **Pressure vs Time** graph. You should see the vessel pressure rise and eventually approach the source pressure.
- Check the **Flow Rate** graph to see the peak flow.

## Example 2: Quick Opening Safety Check

Simulate a scenario where a valve fails open instantly (Quick Opening).

1. Keep the same Source and Vessel settings as Example 1.
2. Change **Valve Configuration**:
   - **Opening Mode**: Quick / Instant
3. Run the simulation.

**Result**: Compare the pressure rise rate with Example 1. The pressure will rise much faster, representing a potential safety case (e.g., relief valve sizing scenario).

## Exporting Results

Once a simulation is complete, you can download a report:
- Click the **"Export PDF"** button to generate a summary report containing all input parameters and the resulting graphs.
