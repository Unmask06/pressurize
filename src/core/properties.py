"""
Gas property calculations using the thermo library.

This module provides dynamic gas property calculations based on composition
and thermodynamic conditions (pressure, temperature).
"""

from dataclasses import dataclass

from thermo import PRMIX, CEOSGas, ChemicalConstantsPackage

# Default components: C1 through C5 + CO2, H2S, H2O, N2
DEFAULT_COMPONENTS = [
    "Methane",      # C1
    "Ethane",       # C2
    "Propane",      # C3
    "n-Butane",     # C4
    "n-Pentane",    # C5
    "CO2",          # Carbon Dioxide
    "H2S",          # Hydrogen Sulfide
    "Water",        # H2O
    "Nitrogen",     # N2
]


@dataclass
class GasProperties:
    """Container for calculated gas properties."""
    Z: float           # Compressibility factor
    k: float           # Heat capacity ratio (Cp/Cv)
    M: float           # Molar mass (g/mol)
    rho: float         # Density (kg/m³)
    Cp: float          # Heat capacity at constant pressure (J/mol/K)
    Cv: float          # Heat capacity at constant volume (J/mol/K)


class GasState:
    """
    Handles gas composition and calculates thermodynamic properties
    using the Peng-Robinson equation of state.
    
    Usage:
        gas = GasState("Methane=0.9, Ethane=0.1")
        props = gas.get_properties(P=1e6, T=300)  # P in Pa, T in K
        print(props.Z, props.k, props.M)
    """
    
    def __init__(self, composition: str):
        """
        Initialize GasState with a composition string.
        
        Args:
            composition: Comma-separated component=fraction pairs.
                         Example: "Methane=0.9, Ethane=0.1"
                         Fractions should be mole fractions (0-1) or will be normalized.
        """
        self.components, self.zs = self._parse_composition(composition)
        self._setup_thermo()
    
    def _parse_composition(self, composition: str) -> tuple[list[str], list[float]]:
        """
        Parse composition string into component names and mole fractions.
        
        Args:
            composition: String like "Methane=0.9, Ethane=0.1"
        
        Returns:
            Tuple of (component_names, mole_fractions)
        """
        components = []
        fractions = []
        
        if not composition or not composition.strip():
            # Default to pure methane if no composition provided
            return ["Methane"], [1.0]
        
        pairs = composition.split(",")
        for pair in pairs:
            pair = pair.strip()
            if "=" in pair:
                name, value = pair.split("=", 1)
                name = name.strip()
                try:
                    fraction = float(value.strip())
                    if fraction > 0:
                        components.append(name)
                        fractions.append(fraction)
                except ValueError:
                    continue
        
        if not components:
            # Default to pure methane if parsing fails
            return ["Methane"], [1.0]
        
        # Normalize fractions to sum to 1.0
        total = sum(fractions)
        if total > 0:
            fractions = [f / total for f in fractions]
        
        return components, fractions
    
    def _setup_thermo(self):
        """Initialize the thermodynamic property package."""
        self.constants, self.correlations = ChemicalConstantsPackage.from_IDs(
            self.components
        )
        
        # Calculate mixture molar mass
        self.molar_mass = sum(
            z * mw for z, mw in zip(self.zs, self.constants.MWs)
        )
    
    def get_properties(self, P: float, T: float) -> GasProperties:
        """
        Calculate gas properties at given pressure and temperature.
        
        Args:
            P: Pressure in Pascals
            T: Temperature in Kelvin
        
        Returns:
            GasProperties dataclass with Z, k, M, rho, Cp, Cv
        """
        # Create Peng-Robinson gas phase
        eos_kwargs = dict(
            Tcs=self.constants.Tcs,
            Pcs=self.constants.Pcs,
            omegas=self.constants.omegas
        )
        
        gas = CEOSGas(
            PRMIX,
            eos_kwargs,
            HeatCapacityGases=self.correlations.HeatCapacityGases,
            T=T,
            P=P,
            zs=self.zs
        )
        
        # Extract properties
        Z = gas.Z()
        Cp = gas.Cp()  # J/mol/K
        Cv = gas.Cv()  # J/mol/K
        
        # Heat capacity ratio (avoid division by zero)
        k = Cp / Cv if Cv > 0 else 1.4
        
        # Density from ideal gas law with compressibility
        R = 8.314  # J/mol/K
        rho = (P * self.molar_mass / 1000) / (Z * R * T)  # kg/m³
        
        return GasProperties(
            Z=Z,
            k=k,
            M=self.molar_mass,  # g/mol
            rho=rho,
            Cp=Cp,
            Cv=Cv
        )
    
    @staticmethod
    def get_default_components() -> list[str]:
        """Return the list of default supported components."""
        return DEFAULT_COMPONENTS.copy()
    
    @staticmethod
    def create_default_composition() -> str:
        """
        Create a default composition string for typical natural gas.
        
        Returns:
            Composition string with C1-C5, CO2, H2S, H2O, N2
        """
        return "Methane=0.9387, Ethane=0.0121, Propane=0.0004, n-Butane=0.00, n-Pentane=0.00, CO2=0.0054, H2S=0.00, Water=0.00, Nitrogen=0.0433"


def get_gas_properties_at_conditions(
    composition: str,
    P: float,
    T: float
) -> tuple[float, float, float]:
    """
    Convenience function to get Z, k, M for a given composition and conditions.
    
    Args:
        composition: Composition string (e.g., "Methane=0.9, Ethane=0.1")
        P: Pressure in Pascals
        T: Temperature in Kelvin
    
    Returns:
        Tuple of (Z_factor, k_ratio, molar_mass_g_mol)
    """
    gas = GasState(composition)
    props = gas.get_properties(P, T)
    return props.Z, props.k, props.M
