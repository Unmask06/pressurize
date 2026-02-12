# Real-World Use Cases

## Typical Applications

### 1. Gas Distribution Systems

Engineers designing networks for natural gas or hydrogen need to know how fast they can pressurize a section of pipe or a storage tank without exceeding material temperature limits or triggering safety systems.

**Pressurize helps by**: simulating the fill profile with real-gas accuracy, showing exactly when choked flow transitions to subsonic, and calculating the total mass transferred.

### 2. Pressure Equalization Between Vessels

In process plants, gas is often transferred between vessels at different pressures. The Equalize mode models both sides simultaneously, predicting the equilibrium pressure and the time to reach it.

### 3. Industrial Process Safety

Safety valves and relief systems must be sized correctly. If a control valve fails open, how fast does pressure build up? Pressurize simulates these worst-case scenarios — switch to Fixed (Instant) opening mode and compare peak flow rates against relief device capacity.

### 4. Blowdown Analysis

Depressurizing a vessel for maintenance or emergency shutdown requires knowing the blowdown time and minimum temperature (Joule-Thomson cooling). The Depressurize mode models this scenario.

### 5. Valve Sizing & Selection

By varying valve ID and Cd values across multiple runs, engineers can identify the minimum valve size that meets fill-time requirements without exceeding allowable flow velocities.

## Comparison: Pressurize vs Alternatives

### Excel / Simple Spreadsheets

| Limitation                      | Pressurize                                    |
| ------------------------------- | --------------------------------------------- |
| Assumes ideal gas ($Z=1$)       | Peng-Robinson EOS, dynamic Z                  |
| Manual sonic/subsonic switching | Automatic regime detection at every time step |
| No multi-component gas support  | 20+ species, preset compositions              |
| Static calculations only        | Time-stepped dynamic simulation               |
| Single unit system              | 5 unit systems, switchable on the fly         |

### Commercial Simulators (HYSYS, Aspen)

| Consideration                        | Pressurize                                 |
| ------------------------------------ | ------------------------------------------ |
| Expensive licenses                   | Free and browser-based                     |
| Steep learning curve                 | Purpose-built UI for valve/vessel problems |
| Overkill for single-vessel scenarios | Focused and fast                           |
| Requires installation                | Runs in any browser                        |
