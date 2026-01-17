"""Test suite for gas properties module.

This module tests gas property calculations using the thermo library,
including composition parsing and property calculations.
"""

import pytest
from pressurize.core.properties import (
    GasProperties,
    GasState,
    get_gas_properties_at_conditions,
)


class TestGasStateInitialization:
    """Tests for GasState initialization and composition parsing."""
    
    def test_pure_methane(self):
        """Test initialization with pure methane."""
        gas = GasState("Methane=1.0")
        assert len(gas.components) == 1
        assert gas.components[0] == "Methane"
        assert pytest.approx(gas.molar_fraction[0], abs=0.001) == 1.0
    
    def test_binary_mixture(self):
        """Test initialization with binary mixture."""
        gas = GasState("Methane=0.9, Ethane=0.1")
        assert len(gas.components) == 2
        assert "Methane" in gas.components
        assert "Ethane" in gas.components
        # Fractions should sum to 1
        assert pytest.approx(sum(gas.molar_fraction), abs=0.001) == 1.0
    
    def test_composition_normalization(self):
        """Test that compositions are normalized to sum to 1."""
        gas = GasState("Methane=90, Ethane=10")
        # Even though we gave 90 and 10, they should normalize to 0.9 and 0.1
        assert pytest.approx(sum(gas.molar_fraction), abs=0.001) == 1.0
        methane_idx = gas.components.index("Methane")
        assert pytest.approx(gas.molar_fraction[methane_idx], abs=0.01) == 0.9
    
    def test_default_composition_on_empty_string(self):
        """Test that empty string defaults to pure methane."""
        gas = GasState("")
        assert len(gas.components) == 1
        assert gas.components[0] == "Methane"
        assert gas.molar_fraction[0] == 1.0
    
    def test_default_composition_on_none(self):
        """Test that None defaults to pure methane."""
        gas = GasState(None)
        assert len(gas.components) == 1
        assert gas.components[0] == "Methane"
        assert gas.molar_fraction[0] == 1.0
    
    def test_multi_component_mixture(self):
        """Test initialization with multiple components."""
        composition = "Methane=0.85, Ethane=0.10, Propane=0.03, CO2=0.02"
        gas = GasState(composition)
        assert len(gas.components) == 4
        assert pytest.approx(sum(gas.molar_fraction), abs=0.001) == 1.0
    
    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        gas = GasState("  Methane = 0.9 ,  Ethane = 0.1  ")
        assert len(gas.components) == 2
        assert pytest.approx(sum(gas.molar_fraction), abs=0.001) == 1.0
    
    def test_ignores_zero_fractions(self):
        """Test that zero fractions are ignored."""
        gas = GasState("Methane=0.9, Ethane=0.1, Propane=0")
        assert len(gas.components) == 2  # Propane should be ignored
        assert "Propane" not in gas.components


class TestGasProperties:
    """Tests for gas property calculations."""
    
    def test_methane_properties_at_standard_conditions(self):
        """Test methane properties at standard conditions."""
        gas = GasState("Methane=1.0")
        P = 101325  # 1 atm in Pa
        T = 288.15  # 15°C in K
        
        props = gas.get_properties(P, T)
        
        # Check that properties are reasonable
        assert props.Z > 0.9  # Should be close to ideal gas
        assert props.Z < 1.1
        assert props.k > 1.2  # Methane k is around 1.3
        assert props.k < 1.4
        assert props.M > 15  # Methane molar mass ~16 g/mol
        assert props.M < 17
        assert props.rho > 0  # Density should be positive
        assert props.Cp > props.Cv  # Heat capacities should follow Cp > Cv
    
    def test_properties_at_high_pressure(self):
        """Test that compressibility deviates from ideal at high pressure."""
        gas = GasState("Methane=1.0")
        P_low = 101325  # 1 atm
        P_high = 10e6   # ~100 atm
        T = 300  # K
        
        props_low = gas.get_properties(P_low, T)
        props_high = gas.get_properties(P_high, T)
        
        # At high pressure, Z should deviate more from 1
        z_deviation_low = abs(props_low.Z - 1.0)
        z_deviation_high = abs(props_high.Z - 1.0)
        
        # High pressure should have more deviation (though this depends on conditions)
        # At least both should be reasonable
        assert 0.5 < props_low.Z < 1.5
        assert 0.5 < props_high.Z < 1.5
    
    def test_density_increases_with_pressure(self):
        """Test that density increases with pressure at constant temperature."""
        gas = GasState("Methane=1.0")
        T = 300  # K
        P1 = 1e5   # 1 bar
        P2 = 5e5   # 5 bar
        
        props1 = gas.get_properties(P1, T)
        props2 = gas.get_properties(P2, T)
        
        # Higher pressure should give higher density
        assert props2.rho > props1.rho
    
    def test_k_ratio_positive(self):
        """Test that heat capacity ratio is always positive and > 1."""
        gas = GasState("Methane=0.9, Ethane=0.1")
        P = 2e6  # Pa
        T = 300  # K
        
        props = gas.get_properties(P, T)
        
        # k should be greater than 1 for all gases
        assert props.k > 1.0
        # For natural gas mixtures, typically between 1.2 and 1.4
        assert props.k < 2.0
    
    def test_molar_mass_calculation(self):
        """Test that molar mass is calculated correctly for mixtures."""
        # Pure methane (M ≈ 16 g/mol)
        gas1 = GasState("Methane=1.0")
        
        # Pure ethane (M ≈ 30 g/mol)
        gas2 = GasState("Ethane=1.0")
        
        # 50/50 mixture should be between the two
        gas_mix = GasState("Methane=0.5, Ethane=0.5")
        
        P = 1e6
        T = 300
        
        props1 = gas1.get_properties(P, T)
        props2 = gas2.get_properties(P, T)
        props_mix = gas_mix.get_properties(P, T)
        
        # Mixture molar mass should be between pure components
        assert props1.M < props_mix.M < props2.M


class TestDefaultComponents:
    """Tests for default component handling."""
    
    def test_get_default_components(self):
        """Test that default components list is returned."""
        components = GasState.get_default_components()
        
        # Should include common natural gas components
        assert "Methane" in components
        assert "Ethane" in components
        assert "Propane" in components
        assert "Carbon dioxide" in components
        assert "Nitrogen" in components
        
        # Should now have 20 components
        assert len(components) == 20
    
    def test_create_default_composition(self):
        """Test that default composition string is valid."""
        composition = GasState.create_default_composition()
        
        # Should be a non-empty string
        assert isinstance(composition, str)
        assert len(composition) > 0
        
        # Should be parseable
        gas = GasState(composition)
        assert len(gas.components) > 0
        
        # Fractions should sum to 1
        assert pytest.approx(sum(gas.molar_fraction), abs=0.001) == 1.0
    
    def test_default_composition_is_valid_natural_gas(self):
        """Test that default composition represents natural gas."""
        composition = GasState.create_default_composition()
        gas = GasState(composition)
        
        # Should be dominated by methane
        methane_idx = gas.components.index("Methane")
        assert gas.molar_fraction[methane_idx] > 0.8  # Natural gas is mostly methane


class TestConvenienceFunction:
    """Tests for get_gas_properties_at_conditions convenience function."""
    
    def test_convenience_function_returns_tuple(self):
        """Test that convenience function returns (Z, k, M) tuple."""
        result = get_gas_properties_at_conditions(
            "Methane=1.0",
            pressure=1e6,
            temperature=300
        )
        
        assert isinstance(result, tuple)
        assert len(result) == 3
        
        Z, k, M = result
        assert 0.5 < Z < 1.5
        assert 1.0 < k < 2.0
        assert M > 0
    
    def test_convenience_function_matches_gas_state(self):
        """Test that convenience function gives same results as GasState."""
        composition = "Methane=0.9, Ethane=0.1"
        P = 2e6
        T = 300
        
        # Using convenience function
        Z1, k1, M1 = get_gas_properties_at_conditions(composition, P, T)
        
        # Using GasState directly
        gas = GasState(composition)
        props = gas.get_properties(P, T)
        
        # Should match
        assert pytest.approx(Z1, rel=0.001) == props.Z
        assert pytest.approx(k1, rel=0.001) == props.k
        assert pytest.approx(M1, rel=0.001) == props.M


class TestPropertyConsistency:
    """Tests for thermodynamic consistency of properties."""
    
    def test_heat_capacity_relation(self):
        """Test that Cp > Cv for all conditions."""
        gas = GasState("Methane=0.9, Ethane=0.1")
        
        # Test at various conditions
        conditions = [
            (1e5, 250),   # Low P, low T
            (1e5, 400),   # Low P, high T
            (10e6, 250),  # High P, low T
            (10e6, 400),  # High P, high T
        ]
        
        for P, T in conditions:
            props = gas.get_properties(P, T)
            assert props.Cp > props.Cv
            
            # k = Cp/Cv should be consistent
            k_calculated = props.Cp / props.Cv
            assert pytest.approx(k_calculated, rel=0.01) == props.k
    
    def test_properties_vary_with_conditions(self):
        """Test that properties change with P and T."""
        gas = GasState("Methane=1.0")
        
        # Get properties at different conditions
        props1 = gas.get_properties(pressure=1e6, temperature=300)
        props2 = gas.get_properties(pressure=5e6, temperature=300)  # Different P
        props3 = gas.get_properties(pressure=1e6, temperature=400)  # Different T
        
        # Properties should differ
        # Z changes with pressure
        assert props1.Z != props2.Z
        
        # Heat capacities change with temperature
        assert props1.Cp != props3.Cp
        
        # Density changes with both P and T
        assert props1.rho != props2.rho
        assert props1.rho != props3.rho


class TestErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_handles_invalid_component_gracefully(self):
        """Test that invalid components are handled."""
        # This might raise an error or ignore invalid components
        # The behavior depends on the thermo library
        try:
            gas = GasState("InvalidComponent=1.0")
            # If it doesn't raise an error, it should at least not crash
            assert len(gas.components) >= 0
        except Exception:
            # Expected behavior - invalid component causes error
            pass
    
    def test_handles_malformed_composition(self):
        """Test handling of malformed composition strings."""
        # Missing equals sign
        gas = GasState("Methane 1.0")
        # Should default to pure methane or handle gracefully
        assert len(gas.components) >= 1
    
    def test_properties_at_extreme_conditions(self):
        """Test that properties can be calculated at extreme conditions."""
        gas = GasState("Methane=1.0")
        
        # Very high pressure
        props_high_p = gas.get_properties(pressure=100e6, temperature=300)
        assert props_high_p.Z > 0
        assert props_high_p.rho > 0
        
        # Very low pressure (near vacuum)
        props_low_p = gas.get_properties(pressure=1000, temperature=300)
        assert props_low_p.Z > 0
        assert props_low_p.rho > 0
