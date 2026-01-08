"""Test suite for physics calculations module.

This module tests the gas flow physics calculations including:
- Critical pressure ratio calculations
- Choked flow calculations
- Subsonic flow calculations
- Mass flow rate calculations with regime detection
- Pressure change rate calculations
"""

import numpy as np
import pytest

from src.core.physics import (
    calculate_choked_flow,
    calculate_critical_pressure_ratio,
    calculate_dp_dt,
    calculate_mass_flow_rate,
    calculate_subsonic_flow,
)


class TestCriticalPressureRatio:
    """Tests for critical pressure ratio calculation."""
    
    def test_air_critical_ratio(self):
        """Test critical ratio for air (k=1.4)."""
        k = 1.4
        r_c = calculate_critical_pressure_ratio(k)
        # For air, critical ratio should be approximately 0.528
        assert pytest.approx(r_c, abs=0.001) == 0.528
    
    def test_natural_gas_critical_ratio(self):
        """Test critical ratio for natural gas (k=1.3)."""
        k = 1.3
        r_c = calculate_critical_pressure_ratio(k)
        # For natural gas, critical ratio should be approximately 0.546
        assert pytest.approx(r_c, abs=0.001) == 0.546
    
    def test_monatomic_gas_critical_ratio(self):
        """Test critical ratio for monatomic gas (k=1.67)."""
        k = 1.67
        r_c = calculate_critical_pressure_ratio(k)
        # For monatomic gas, critical ratio should be approximately 0.487
        assert pytest.approx(r_c, abs=0.001) == 0.487
    
    def test_critical_ratio_range(self):
        """Test that critical ratio is always between 0 and 1."""
        for k in [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7]:
            r_c = calculate_critical_pressure_ratio(k)
            assert 0 < r_c < 1


class TestChokedFlow:
    """Tests for choked flow calculations."""
    
    def test_choked_flow_positive(self):
        """Test that choked flow produces positive mass flow rate."""
        Cd = 0.65
        A = 0.001  # 1000 mm² in m²
        P_up = 3.5e6  # 3.5 MPa
        k = 1.3
        M = 0.017  # 17 g/mol in kg/mol
        Z = 0.9
        T = 300  # K
        
        mass_flow = calculate_choked_flow(Cd, A, P_up, k, M, Z, T)
        assert mass_flow > 0
    
    def test_choked_flow_scales_with_area(self):
        """Test that flow rate doubles when area doubles."""
        Cd = 0.65
        A1 = 0.001
        A2 = 0.002
        P_up = 3.5e6
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        mass_flow1 = calculate_choked_flow(Cd, A1, P_up, k, M, Z, T)
        mass_flow2 = calculate_choked_flow(Cd, A2, P_up, k, M, Z, T)
        
        assert pytest.approx(mass_flow2, rel=0.01) == 2 * mass_flow1
    
    def test_choked_flow_scales_with_pressure(self):
        """Test that flow rate doubles when upstream pressure doubles."""
        Cd = 0.65
        A = 0.001
        P_up1 = 3.5e6
        P_up2 = 7.0e6
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        mass_flow1 = calculate_choked_flow(Cd, A, P_up1, k, M, Z, T)
        mass_flow2 = calculate_choked_flow(Cd, A, P_up2, k, M, Z, T)
        
        assert pytest.approx(mass_flow2, rel=0.01) == 2 * mass_flow1
    
    def test_choked_flow_decreases_with_temperature(self):
        """Test that flow rate decreases with higher temperature."""
        Cd = 0.65
        A = 0.001
        P_up = 3.5e6
        k = 1.3
        M = 0.017
        Z = 0.9
        T1 = 300
        T2 = 400
        
        mass_flow1 = calculate_choked_flow(Cd, A, P_up, k, M, Z, T1)
        mass_flow2 = calculate_choked_flow(Cd, A, P_up, k, M, Z, T2)
        
        # Higher temperature should reduce flow rate (density effect)
        assert mass_flow2 < mass_flow1


class TestSubsonicFlow:
    """Tests for subsonic flow calculations."""
    
    def test_subsonic_flow_positive(self):
        """Test that subsonic flow produces positive mass flow rate."""
        Cd = 0.65
        A = 0.001
        P_up = 3.5e6
        P_down = 2.5e6  # Above critical ratio for k=1.3
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        mass_flow = calculate_subsonic_flow(Cd, A, P_up, P_down, k, M, Z, T)
        assert mass_flow > 0
    
    def test_subsonic_flow_zero_at_equilibrium(self):
        """Test that flow is zero when pressures are equal."""
        Cd = 0.65
        A = 0.001
        P = 3.5e6
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        mass_flow = calculate_subsonic_flow(Cd, A, P, P, k, M, Z, T)
        assert mass_flow == 0.0
    
    def test_subsonic_flow_zero_when_inverted(self):
        """Test that flow is zero when downstream pressure exceeds upstream."""
        Cd = 0.65
        A = 0.001
        P_up = 2.5e6
        P_down = 3.5e6
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        mass_flow = calculate_subsonic_flow(Cd, A, P_up, P_down, k, M, Z, T)
        assert mass_flow == 0.0
    
    def test_subsonic_flow_increases_with_pressure_difference(self):
        """Test that flow increases with larger pressure differential."""
        Cd = 0.65
        A = 0.001
        P_up = 3.5e6
        P_down1 = 3.0e6  # Smaller differential
        P_down2 = 2.5e6  # Larger differential
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        mass_flow1 = calculate_subsonic_flow(Cd, A, P_up, P_down1, k, M, Z, T)
        mass_flow2 = calculate_subsonic_flow(Cd, A, P_up, P_down2, k, M, Z, T)
        
        # Larger pressure difference should give higher flow
        assert mass_flow2 > mass_flow1


class TestMassFlowRate:
    """Tests for mass flow rate calculation with automatic regime detection."""
    
    def test_detects_choked_flow(self):
        """Test that function correctly identifies choked flow conditions."""
        Cd = 0.65
        A = 0.001
        P_up = 3.5e6
        P_down = 1.0e6  # Low enough for choked flow
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        # Calculate what choked flow should give
        mass_flow_choked = calculate_choked_flow(Cd, A, P_up, k, M, Z, T)
        mass_flow_actual = calculate_mass_flow_rate(Cd, A, P_up, P_down, k, M, Z, T)
        
        # Should match choked flow
        assert pytest.approx(mass_flow_actual, rel=0.01) == mass_flow_choked
    
    def test_detects_subsonic_flow(self):
        """Test that function correctly identifies subsonic flow conditions."""
        Cd = 0.65
        A = 0.001
        P_up = 3.5e6
        P_down = 2.5e6  # High enough for subsonic flow
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        # Calculate what subsonic flow should give
        mass_flow_subsonic = calculate_subsonic_flow(Cd, A, P_up, P_down, k, M, Z, T)
        mass_flow_actual = calculate_mass_flow_rate(Cd, A, P_up, P_down, k, M, Z, T)
        
        # Should match subsonic flow
        assert pytest.approx(mass_flow_actual, rel=0.01) == mass_flow_subsonic
    
    def test_zero_at_equilibrium(self):
        """Test that flow is zero when pressures are equalized."""
        Cd = 0.65
        A = 0.001
        P = 3.5e6
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        mass_flow = calculate_mass_flow_rate(Cd, A, P, P, k, M, Z, T)
        assert mass_flow == 0.0
    
    def test_transition_at_critical_ratio(self):
        """Test behavior near critical pressure ratio transition."""
        Cd = 0.65
        A = 0.001
        P_up = 3.5e6
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        # Calculate critical pressure ratio
        r_c = calculate_critical_pressure_ratio(k)
        P_critical = P_up * r_c
        
        # Just below critical (choked)
        P_choked = P_critical * 0.99
        mass_flow_choked = calculate_mass_flow_rate(Cd, A, P_up, P_choked, k, M, Z, T)
        
        # Just above critical (subsonic)
        P_subsonic = P_critical * 1.01
        mass_flow_subsonic = calculate_mass_flow_rate(Cd, A, P_up, P_subsonic, k, M, Z, T)
        
        # Both should be positive
        assert mass_flow_choked > 0
        assert mass_flow_subsonic > 0
        
        # Choked flow should be higher (less downstream resistance)
        assert mass_flow_choked > mass_flow_subsonic


class TestPressureChangeRate:
    """Tests for pressure change rate calculations."""
    
    def test_pressure_increases_with_positive_flow(self):
        """Test that pressure increases when gas flows in."""
        Z = 0.9
        T = 300
        V = 2.0  # 2 m³
        M = 0.017
        mass_flow = 0.5  # 0.5 kg/s inflow
        
        dp_dt = calculate_dp_dt(Z, T, V, M, mass_flow)
        assert dp_dt > 0
    
    def test_pressure_decreases_with_negative_flow(self):
        """Test that pressure decreases when gas flows out."""
        Z = 0.9
        T = 300
        V = 2.0
        M = 0.017
        mass_flow = -0.5  # 0.5 kg/s outflow
        
        dp_dt = calculate_dp_dt(Z, T, V, M, mass_flow)
        assert dp_dt < 0
    
    def test_no_pressure_change_with_zero_flow(self):
        """Test that pressure is constant with no flow."""
        Z = 0.9
        T = 300
        V = 2.0
        M = 0.017
        mass_flow = 0.0
        
        dp_dt = calculate_dp_dt(Z, T, V, M, mass_flow)
        assert dp_dt == 0.0
    
    def test_pressure_change_scales_with_flow(self):
        """Test that pressure change rate doubles when flow doubles."""
        Z = 0.9
        T = 300
        V = 2.0
        M = 0.017
        mass_flow1 = 0.5
        mass_flow2 = 1.0
        
        dp_dt1 = calculate_dp_dt(Z, T, V, M, mass_flow1)
        dp_dt2 = calculate_dp_dt(Z, T, V, M, mass_flow2)
        
        assert pytest.approx(dp_dt2, rel=0.01) == 2 * dp_dt1
    
    def test_pressure_change_inverse_to_volume(self):
        """Test that pressure change is inversely proportional to volume."""
        Z = 0.9
        T = 300
        V1 = 2.0
        V2 = 4.0
        M = 0.017
        mass_flow = 0.5
        
        dp_dt1 = calculate_dp_dt(Z, T, V1, M, mass_flow)
        dp_dt2 = calculate_dp_dt(Z, T, V2, M, mass_flow)
        
        # Doubling volume should halve the pressure change rate
        assert pytest.approx(dp_dt2, rel=0.01) == dp_dt1 / 2
    
    def test_pressure_change_scales_with_temperature(self):
        """Test that pressure change rate scales with temperature."""
        Z = 0.9
        T1 = 300
        T2 = 400
        V = 2.0
        M = 0.017
        mass_flow = 0.5
        
        dp_dt1 = calculate_dp_dt(Z, T1, V, M, mass_flow)
        dp_dt2 = calculate_dp_dt(Z, T2, V, M, mass_flow)
        
        # Should scale proportionally with temperature
        assert pytest.approx(dp_dt2 / dp_dt1, rel=0.01) == T2 / T1


class TestIntegration:
    """Integration tests verifying multiple functions work together."""
    
    def test_flow_regime_transition(self):
        """Test that flow transitions smoothly from choked to subsonic to zero."""
        Cd = 0.65
        A = 0.001
        P_up = 3.5e6
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        # Test various downstream pressures
        pressures = np.linspace(0, P_up, 20)
        flow_rates = []
        
        for P_down in pressures:
            mass_flow = calculate_mass_flow_rate(Cd, A, P_up, P_down, k, M, Z, T)
            flow_rates.append(mass_flow)
        
        # Flow rates should all be non-negative
        assert all(m >= 0 for m in flow_rates)
        
        # Flow rate should be zero at equilibrium
        assert flow_rates[-1] == 0.0
        
        # Flow rate should generally decrease as downstream pressure increases
        # (with possible plateau in choked regime)
        assert flow_rates[0] >= flow_rates[-2]
    
    def test_realistic_valve_scenario(self):
        """Test a realistic valve opening scenario."""
        # 2-inch valve opening into a vessel
        Cd = 0.65
        valve_radius = 0.0254  # 1 inch in meters
        A = np.pi * valve_radius ** 2
        P_up = 3.5e6  # 500 psig approximately
        P_down = 0.5e6  # 50 psig approximately
        k = 1.3
        M = 0.017
        Z = 0.9
        T = 300
        
        # Calculate flow
        mass_flow = calculate_mass_flow_rate(Cd, A, P_up, P_down, k, M, Z, T)
        
        # Should be a reasonable flow rate (positive and not extreme)
        assert 0 < mass_flow < 100  # kg/s
        
        # Calculate pressure change in a 2 m³ vessel
        V = 2.0
        dp_dt = calculate_dp_dt(Z, T, V, M, mass_flow)
        
        # Pressure should increase
        assert dp_dt > 0
        
        # Rate should be reasonable (not instantaneous)
        assert dp_dt < 1e7  # Less than 10 MPa/s
