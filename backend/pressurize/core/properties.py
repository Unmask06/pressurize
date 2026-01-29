"""Gas property calculations using the thermo library."""

from dataclasses import dataclass

from thermo import (  # type: ignore[import-untyped]
    PRMIX,
    CEOSGas,
    ChemicalConstantsPackage,
)

# Top 20 components for natural gas and industrial applications
DEFAULT_COMPONENTS = [
    "Methane",  # C1
    "Ethane",  # C2
    "Propane",  # C3
    "n-Butane",  # n-C4
    "i-Butane",  # i-C4
    "n-Pentane",  # n-C5
    "i-Pentane",  # i-C5
    "n-Hexane",  # n-C6
    "n-Heptane",  # n-C7
    "n-Octane",  # n-C8
    "Nitrogen",  # N2
    "Carbon dioxide",  # CO2
    "Hydrogen sulfide",  # H2S
    "Water",  # H2O
    "Oxygen",  # O2
    "Hydrogen",  # H2
    "Carbon monoxide",  # CO
    "Argon",  # Ar
    "Helium",  # He
    "Ammonia",  # NH3
]


@dataclass
class GasProperties:
    """Container for calculated gas properties."""

    Z: float  # Compressibility factor
    k: float  # Heat capacity ratio (Cp/Cv)
    M: float  # Molar mass (g/mol)
    rho: float  # Density (kg/m³)
    Cp: float  # Heat capacity at constant pressure (J/mol/K)
    Cv: float  # Heat capacity at constant volume (J/mol/K)


class GasState:
    """Handles gas composition and thermodynamic property calculations.

    Uses the Peng-Robinson equation of state for real gas behavior.
    """

    def __init__(self, composition: str):
        """Initialize GasState with a composition string.

        Args:
            composition: Comma-separated "Component=fraction" pairs.
                Example: "Methane=0.9, Ethane=0.1"
        """
        self.components, self.molar_fraction = self._parse_composition(composition)
        self._setup_thermo()

    def _parse_composition(self, composition: str) -> tuple[list[str], list[float]]:
        """Parse composition string into component names and mole fractions."""
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

    def _setup_thermo(self) -> None:
        """Initialize the thermodynamic property package."""
        self.constants, self.correlations = ChemicalConstantsPackage.from_IDs(
            self.components
        )

        # Calculate mixture molar mass
        self.molar_mass = sum(
            z * mw
            for z, mw in zip(self.molar_fraction, self.constants.MWs, strict=True)
        )

    def get_properties(self, pressure: float, temperature: float) -> GasProperties:
        """Calculate gas properties at given pressure and temperature.

        Args:
            pressure: Pressure in Pascals.
            temperature: Temperature in Kelvin.

        Returns:
            GasProperties with Z, k, M, rho, Cp, Cv.
        """
        # Create Peng-Robinson gas phase
        eos_kwargs = dict(
            Tcs=self.constants.Tcs, Pcs=self.constants.Pcs, omegas=self.constants.omegas
        )

        gas = CEOSGas(
            PRMIX,
            eos_kwargs,
            HeatCapacityGases=self.correlations.HeatCapacityGases,
            T=temperature,
            P=pressure,
            zs=self.molar_fraction,
        )

        # Extract properties
        Z = gas.Z()
        Cp = gas.Cp()  # J/mol/K
        Cv = gas.Cv()  # J/mol/K

        # Heat capacity ratio (avoid division by zero)
        k = Cp / Cv if Cv > 0 else 1.4

        # Density from ideal gas law with compressibility
        R = 8.314  # J/mol/K
        rho = (pressure * self.molar_mass / 1000) / (Z * R * temperature)  # kg/m³

        return GasProperties(
            Z=Z,
            k=k,
            M=self.molar_mass,
            rho=rho,
            Cp=Cp,
            Cv=Cv,  # g/mol
        )

    @staticmethod
    def get_default_components() -> list[str]:
        """Return the list of default supported components."""
        return DEFAULT_COMPONENTS.copy()

    @staticmethod
    def create_default_composition() -> str:
        """Create a default composition string for typical natural gas."""
        return (
            "Methane=0.9387, Ethane=0.0121, Propane=0.0004, "
            "n-Butane=0.00, n-Pentane=0.00, Carbon dioxide=0.0054, "
            "Hydrogen sulfide=0.00, Water=0.00, Nitrogen=0.0433"
        )

    @staticmethod
    def get_preset_composition(preset_name: str) -> dict[str, float]:
        """Get a preset composition as a dictionary of component:fraction pairs.

        Args:
            preset_name: Name of the preset ('natural_gas', 'pure_methane', 'rich_gas', 'sour_gas', 'lean_gas').

        Returns:
            Dictionary mapping component names to mole fractions.
        """
        presets = {
            "natural_gas": {
                "Methane": 0.9387,
                "Ethane": 0.0121,
                "Propane": 0.0004,
                "n-Butane": 0.0,
                "n-Pentane": 0.0,
                "Carbon dioxide": 0.0054,
                "Hydrogen sulfide": 0.0,
                "Water": 0.0,
                "Nitrogen": 0.0433,
            },
            "pure_methane": {
                "Methane": 1.0,
            },
            "rich_gas": {
                "Methane": 0.75,
                "Ethane": 0.12,
                "Propane": 0.08,
                "n-Butane": 0.03,
                "n-Pentane": 0.01,
                "Carbon dioxide": 0.005,
                "Nitrogen": 0.005,
            },
            "sour_gas": {
                "Methane": 0.85,
                "Ethane": 0.05,
                "Propane": 0.02,
                "n-Butane": 0.01,
                "Carbon dioxide": 0.08,
                "Hydrogen sulfide": 0.04,
            },
            "lean_gas": {
                "Methane": 0.96,
                "Ethane": 0.02,
                "Propane": 0.005,
                "Carbon dioxide": 0.005,
                "Nitrogen": 0.01,
            },
        }

        return presets.get(preset_name, presets["natural_gas"])


def get_gas_properties_at_conditions(
    composition: str, pressure: float, temperature: float
) -> tuple[float, float, float]:
    """Get Z, k, M for a given composition and conditions.

    Args:
        composition: Composition string (e.g., "Methane=0.9, Ethane=0.1").
        pressure: Pressure in Pascals.
        temperature: Temperature in Kelvin.

    Returns:
        Tuple of (Z_factor, k_ratio, molar_mass_g_mol).
    """
    gas = GasState(composition)
    props = gas.get_properties(pressure, temperature)
    return props.Z, props.k, props.M
