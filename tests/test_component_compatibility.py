"""Test suite for expanded component list compatibility with thermo package.

This module tests that all 20 default components can be successfully
loaded and used with the thermo library for property calculations.
"""

import pytest
from src.core.properties import GasState, DEFAULT_COMPONENTS


class TestComponentCompatibility:
    """Tests to verify all components work with thermo package."""
    
    def test_all_components_listed(self):
        """Test that we have exactly 20 components."""
        components = GasState.get_default_components()
        assert len(components) == 20, f"Expected 20 components, got {len(components)}"
    
    def test_component_list_matches_constant(self):
        """Test that get_default_components returns DEFAULT_COMPONENTS."""
        assert GasState.get_default_components() == DEFAULT_COMPONENTS
    
    @pytest.mark.parametrize("component", DEFAULT_COMPONENTS)
    def test_individual_component_loads(self, component):
        """Test that each component can be loaded individually."""
        # Create pure component composition
        composition = f"{component}=1.0"
        
        # Should not raise an exception
        gas = GasState(composition)
        
        assert len(gas.components) == 1
        assert gas.components[0] == component
        assert pytest.approx(gas.zs[0], abs=0.001) == 1.0
    
    @pytest.mark.parametrize("component", DEFAULT_COMPONENTS)
    def test_component_property_calculation(self, component):
        """Test that properties can be calculated for each pure component."""
        composition = f"{component}=1.0"
        gas = GasState(composition)
        
        # Standard conditions: 1 atm (101325 Pa), 25°C (298.15 K)
        P = 101325  # Pa
        T = 298.15  # K
        
        # Calculate properties - should not raise an exception
        props = gas.get_properties(P, T)
        
        # Verify properties are reasonable
        assert props.Z > 0, f"Z-factor should be positive for {component}"
        assert props.k > 1.0, f"k-ratio should be > 1 for {component}"
        assert props.M > 0, f"Molar mass should be positive for {component}"
        assert props.rho > 0, f"Density should be positive for {component}"
        assert props.Cp > 0, f"Cp should be positive for {component}"
        assert props.Cv > 0, f"Cv should be positive for {component}"
    
    def test_hydrocarbon_series(self):
        """Test that hydrocarbon series (C1-C8) loads correctly."""
        hydrocarbons = [
            "Methane",
            "Ethane",
            "Propane",
            "n-Butane",
            "i-Butane",
            "n-Pentane",
            "i-Pentane",
            "n-Hexane",
            "n-Heptane",
            "n-Octane"
        ]
        
        for hc in hydrocarbons:
            assert hc in DEFAULT_COMPONENTS, f"{hc} should be in DEFAULT_COMPONENTS"
    
    def test_common_gases(self):
        """Test that common industrial gases are included."""
        common_gases = [
            "Nitrogen",
            "Carbon dioxide",
            "Oxygen",
            "Hydrogen",
            "Water"
        ]
        
        for gas in common_gases:
            assert gas in DEFAULT_COMPONENTS, f"{gas} should be in DEFAULT_COMPONENTS"
    
    def test_acid_gases(self):
        """Test that acid gases are included."""
        acid_gases = ["Hydrogen sulfide", "Carbon dioxide"]
        
        for gas in acid_gases:
            assert gas in DEFAULT_COMPONENTS, f"{gas} should be in DEFAULT_COMPONENTS"
    
    def test_binary_mixture_with_new_components(self):
        """Test binary mixtures using new components."""
        test_pairs = [
            ("Methane", "i-Butane"),
            ("Nitrogen", "Oxygen"),
            ("Hydrogen", "Helium"),
            ("Ethane", "n-Hexane"),
        ]
        
        for comp1, comp2 in test_pairs:
            composition = f"{comp1}=0.7, {comp2}=0.3"
            gas = GasState(composition)
            
            assert len(gas.components) == 2
            assert comp1 in gas.components
            assert comp2 in gas.components
            assert pytest.approx(sum(gas.zs), abs=0.001) == 1.0
    
    def test_complex_mixture_with_10_components(self):
        """Test a complex mixture with 10 different components."""
        composition = (
            "Methane=0.85, Ethane=0.05, Propane=0.03, "
            "n-Butane=0.02, i-Pentane=0.01, "
            "Nitrogen=0.015, Carbon dioxide=0.01, "
            "Hydrogen sulfide=0.005, Water=0.005, Helium=0.005"
        )
        
        gas = GasState(composition)
        
        assert len(gas.components) == 10
        assert pytest.approx(sum(gas.zs), abs=0.001) == 1.0
        
        # Should be able to calculate properties
        P = 5e6  # 5 MPa
        T = 300  # K
        props = gas.get_properties(P, T)
        
        assert props.Z > 0
        assert props.k > 1.0
        assert props.M > 0
    
    def test_all_components_in_one_mixture(self):
        """Test that all 20 components can be used together."""
        # Create equal mole fraction mixture
        fraction = 1.0 / 20
        comp_parts = [f"{comp}={fraction:.6f}" for comp in DEFAULT_COMPONENTS]
        composition = ", ".join(comp_parts)
        
        gas = GasState(composition)
        
        assert len(gas.components) == 20
        assert pytest.approx(sum(gas.zs), abs=0.001) == 1.0
        
        # Calculate properties at standard conditions
        P = 101325  # Pa
        T = 298.15  # K
        props = gas.get_properties(P, T)
        
        assert props.Z > 0
        assert props.k > 1.0
        assert props.M > 0


class TestPresetCompositionsWithNewComponents:
    """Test that preset compositions work with updated component names."""
    
    def test_natural_gas_preset(self):
        """Test natural gas preset composition."""
        preset = GasState.get_preset_composition('natural_gas')
        
        # Build composition string
        comp_parts = [f"{comp}={val:.4f}" for comp, val in preset.items() if val > 0]
        composition = ", ".join(comp_parts)
        
        gas = GasState(composition)
        props = gas.get_properties(101325, 298.15)
        
        assert props.Z > 0
        assert props.k > 1.0
    
    def test_pure_methane_preset(self):
        """Test pure methane preset."""
        preset = GasState.get_preset_composition('pure_methane')
        
        assert preset['Methane'] == 1.0
        
        composition = "Methane=1.0"
        gas = GasState(composition)
        props = gas.get_properties(101325, 298.15)
        
        assert props.Z > 0
        assert props.k > 1.0
    
    def test_rich_gas_preset(self):
        """Test rich gas preset composition."""
        preset = GasState.get_preset_composition('rich_gas')
        
        comp_parts = [f"{comp}={val:.4f}" for comp, val in preset.items() if val > 0]
        composition = ", ".join(comp_parts)
        
        gas = GasState(composition)
        props = gas.get_properties(101325, 298.15)
        
        assert props.Z > 0
        assert props.k > 1.0
    
    def test_sour_gas_preset(self):
        """Test sour gas preset with H2S."""
        preset = GasState.get_preset_composition('sour_gas')
        
        assert preset['Hydrogen sulfide'] > 0
        
        comp_parts = [f"{comp}={val:.4f}" for comp, val in preset.items() if val > 0]
        composition = ", ".join(comp_parts)
        
        gas = GasState(composition)
        props = gas.get_properties(101325, 298.15)
        
        assert props.Z > 0
        assert props.k > 1.0
    
    def test_lean_gas_preset(self):
        """Test lean gas preset composition."""
        preset = GasState.get_preset_composition('lean_gas')
        
        comp_parts = [f"{comp}={val:.4f}" for comp, val in preset.items() if val > 0]
        composition = ", ".join(comp_parts)
        
        gas = GasState(composition)
        props = gas.get_properties(101325, 298.15)
        
        assert props.Z > 0
        assert props.k > 1.0


class TestComponentPropertyRanges:
    """Test that calculated properties are within reasonable ranges."""
    
    @pytest.mark.parametrize("component", DEFAULT_COMPONENTS)
    def test_z_factor_range(self, component):
        """Test that Z-factor is within reasonable range."""
        composition = f"{component}=1.0"
        gas = GasState(composition)
        
        # Test at various pressures
        pressures = [101325, 1e6, 5e6]  # 1 atm, 10 bar, 50 bar
        T = 298.15  # K
        
        for P in pressures:
            props = gas.get_properties(P, T)
            # Z should be positive. For heavier hydrocarbons and polar compounds
            # at high pressure, Z can be very low (approaching liquid phase)
            assert 0.01 < props.Z < 2.0, f"Z={props.Z} out of range for {component} at P={P}"
    
    @pytest.mark.parametrize("component", DEFAULT_COMPONENTS)
    def test_k_ratio_range(self, component):
        """Test that k-ratio (Cp/Cv) is within reasonable range."""
        composition = f"{component}=1.0"
        gas = GasState(composition)
        
        P = 101325  # Pa
        T = 298.15  # K
        props = gas.get_properties(P, T)
        
        # k should typically be between 1.0 and 1.7 for gases
        assert 1.0 < props.k < 2.0, f"k={props.k} out of range for {component}"
    
    @pytest.mark.parametrize("component", DEFAULT_COMPONENTS)
    def test_molar_mass_positive(self, component):
        """Test that molar mass is positive and reasonable."""
        composition = f"{component}=1.0"
        gas = GasState(composition)
        
        # Molar mass should be positive and less than 200 g/mol for these components
        assert 0 < gas.molar_mass < 200, f"Molar mass={gas.molar_mass} out of range for {component}"
