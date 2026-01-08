# Dynamic Valve Pressurization Simulator

A Python Dash web application that simulates the dynamic pressurization of a downstream vessel as a valve opens linearly over time.

![Simulator Screenshot](screenshot.png)

## Features

- **Real Gas Law Calculations**: Uses PV = ZnRT for accurate pressure calculations
- **Dual Flow Regimes**: Automatically handles both choked (sonic) and subsonic flow conditions
- **Multiple Valve Opening Modes**: Linear, exponential, fixed, and quick-opening profiles
- **Composition-Based Properties**: Define gas mixtures with 20+ components and automatically calculate Z, k, and M
- **Interactive Dashboard**: Modern UI with real-time parameter adjustment
- **Dual-Axis Visualization**: Simultaneous pressure and flow rate plots
- **KPI Cards**: Quick view of peak flow, final pressure, equilibrium time, and total mass
- **Preset Gas Compositions**: Quick selection of common gas mixtures (natural gas, pure methane, rich gas, etc.)

## Physics Background

### Real Gas Law

$$PV = ZnRT$$

Where:

- Z = Compressibility factor
- n = Number of moles
- R = Universal gas constant (8.31446 J/mol·K)
- T = Absolute temperature (K)

### Flow Equations

**Critical Pressure Ratio:**
$$r_c = \left(\frac{2}{k+1}\right)^{\frac{k}{k-1}}$$

**Choked Flow (r ≤ r_c):**
$$\dot{m} = C_d \cdot A \cdot P_{up} \sqrt{\frac{k \cdot M}{Z \cdot R \cdot T} \left(\frac{2}{k+1}\right)^{\frac{k+1}{k-1}}}$$

**Subsonic Flow (r > r_c):**
$$\dot{m} = C_d \cdot A \cdot P_{up} \sqrt{\frac{2M}{ZRT} \cdot \frac{k}{k-1} \left[r^{\frac{2}{k}} - r^{\frac{k+1}{k}}\right]}$$

## Installation

1. Clone or download this repository

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:

   ```bash
   python app.py
   ```

2. Open your browser and navigate to:

   ```
   http://localhost:8050
   ```

3. Adjust the simulation parameters in the sidebar:

   - **Upstream Pressure (psig)**: Source pressure
   - **Initial Downstream Pressure (psig)**: Starting vessel pressure
   - **Vessel Volume (ft³)**: Volume of the downstream vessel
   - **Valve ID (inches)**: Inner diameter of the valve
   - **Valve Opening Mode**: Linear, exponential, fixed, or quick-opening
   - **Valve Opening Time (s)**: Time for valve to fully open
   - **Property Mode**: Choose between manual entry or composition-based calculation
   - **Gas Composition**: For composition mode, select components and define mole fractions
   - **Temperature (°F)**: Gas temperature
   - **Molar Mass (kg/mol)**: Molecular weight (manual mode) or calculated from composition
   - **Z-Factor**: Compressibility factor (manual mode) or calculated from composition
   - **k (Gamma)**: Heat capacity ratio (manual mode) or calculated from composition
   - **Discharge Coefficient (Cd)**: Valve flow coefficient

4. Click "Run Simulation" to execute

## Gas Composition Feature

The simulator supports two property input modes:

### Manual Mode
Directly enter Z-factor, k-ratio, and molar mass values.

### Composition Mode (Enhanced)
Define your gas mixture using 20 supported components:

**Hydrocarbons (C1-C8):**
- Methane, Ethane, Propane
- n-Butane, i-Butane
- n-Pentane, i-Pentane
- n-Hexane, n-Heptane, n-Octane

**Common Gases:**
- Nitrogen, Oxygen, Hydrogen, Carbon monoxide, Argon, Helium

**Acid Gases & Others:**
- Carbon dioxide, Hydrogen sulfide, Water, Ammonia

**Preset Compositions:**
- **Natural Gas (Pipeline)**: Typical pipeline natural gas composition
- **Pure Methane**: 100% methane for baseline comparisons
- **Rich Gas**: High C2-C5 content for NGL-rich streams
- **Sour Gas**: Contains H2S for acid gas applications
- **Lean Gas**: Minimal C2+ content

**Using the Composition Editor:**
1. Select "Composition (Derived)" as the property mode
2. Click the "✏️ Edit" button to open the composition editor
3. Choose a preset or build a custom mixture:
   - Click components in the "Available" column to add them
   - Enter mole fractions for selected components
   - Remove unwanted components with the × button
4. The total will show with color-coded validation
5. Click "Apply" to use the composition

Properties (Z, k, M) are automatically calculated using the Peng-Robinson equation of state.

## Default Parameters

| Parameter           | Default Value | Description               |
| ------------------- | ------------- | ------------------------- |
| Upstream Pressure   | 500 psig      | Source pressure           |
| Downstream Pressure | 0 psig        | Initial vessel pressure   |
| Volume              | 100 ft³       | Vessel volume             |
| Valve ID            | 2 inches      | Valve diameter            |
| Opening Time        | 5 seconds     | Time to fully open        |
| Temperature         | 70°F          | Gas temperature           |
| Molar Mass          | 0.029 kg/mol  | Air molecular weight      |
| Z-Factor            | 1.0           | Ideal gas assumption      |
| k (Gamma)           | 1.4           | Air heat capacity ratio   |
| Cd                  | 0.65          | Typical valve coefficient |

## Output

### KPI Cards

- **Peak Flow Rate**: Maximum flow rate achieved (lb/hr)
- **Final Pressure**: Equilibrium pressure reached (psig)
- **Equilibrium Time**: Time to reach steady state (seconds)
- **Total Mass Flow**: Cumulative mass transferred (lb)

### Graph

- **Blue line (left axis)**: Downstream pressure vs time
- **Red dotted line (right axis)**: Flow rate vs time
- **Green vertical line**: Valve fully open marker

### Data Table

Click "Show/Hide Data Table" to view the raw simulation data.

## Technical Details

- **Time Step**: 0.2 seconds
- **Simulation Duration**: Runs until flow rate drops to < 0.1% of peak or 10× opening time
- **Unit Conversions**: All calculations performed in SI units, then converted back to Imperial

## License

MIT License - Feel free to use and modify for your applications.

## Author

Created for engineering simulation purposes.
