"""Test suite for simulation module.

This module tests the main simulation engine that integrates
all physics calculations over time.
"""

import pandas as pd
import pytest
from app.core.simulation import run_simulation


def _find_time_index(df, target_time):
    """Helper function to find the index of a row at or after target_time.
    
    Args:
        df: DataFrame with 'time' column.
        target_time: Target time value to search for.
    
    Returns:
        Index of first row where time >= target_time, or -1 if not found.
    """
    matching_rows = df[df['time'] >= target_time]
    return matching_rows.index[0] if len(matching_rows) > 0 else -1


class TestSimulationBasics:
    """Basic tests for simulation execution."""
    
    def test_simulation_returns_dataframe(self):
        """Test that simulation returns a pandas DataFrame."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    
    def test_simulation_has_required_columns(self):
        """Test that simulation output has all required columns."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        required_columns = [
            'time',
            'pressure_psig',
            'upstream_pressure_psig',
            'flowrate_lb_hr',
            'valve_opening_pct',
            'flow_regime'
        ]
        
        for col in required_columns:
            assert col in df.columns
    
    def test_time_starts_at_zero(self):
        """Test that simulation time starts at 0."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        assert df['time'].iloc[0] == 0
    
    def test_pressure_starts_at_initial_value(self):
        """Test that pressure starts at specified initial value."""
        initial_pressure = 50
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=initial_pressure,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        assert df['pressure_psig'].iloc[0] == initial_pressure


class TestValveOpeningModes:
    """Tests for different valve opening modes."""
    
    def test_linear_opening_mode(self):
        """Test linear valve opening mode."""
        opening_time = 10
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=opening_time,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4,
            opening_mode='linear'
        )
        
        # Check valve starts at 0%
        assert df['valve_opening_pct'].iloc[0] == 0
        
        # Find the row at or near opening_time
        idx = _find_time_index(df, opening_time)
        if idx >= 0:
            # Valve should be at or near 100%
            assert df['valve_opening_pct'].iloc[idx] >= 95
    
    def test_fixed_opening_mode(self):
        """Test fixed (instant) valve opening mode."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=10,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4,
            opening_mode='fixed'
        )
        
        # Valve should be 100% open from the start
        assert df['valve_opening_pct'].iloc[0] == 100.0
        # And remain at 100%
        assert all(df['valve_opening_pct'] == 100.0)
    
    def test_exponential_opening_mode(self):
        """Test exponential valve opening mode."""
        opening_time = 10
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=opening_time,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4,
            opening_mode='exponential',
            k_curve=4.0
        )
        
        # Should start at 0%
        assert df['valve_opening_pct'].iloc[0] == 0
        
        # Exponential opening should result in slower opening at start
        # Check that opening at 50% of time is less than 50% open
        halfway_time = opening_time / 2
        idx = _find_time_index(df, halfway_time)
        if idx >= 0 and idx < len(df):
            # For exponential with k=4, should be less than 50% at halfway
            assert df['valve_opening_pct'].iloc[idx] < 50


class TestPressureBehavior:
    """Tests for pressure behavior during simulation."""
    
    def test_pressure_increases(self):
        """Test that downstream pressure increases during simulation."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Pressure should generally increase
        assert df['pressure_psig'].iloc[-1] > df['pressure_psig'].iloc[0]
    
    def test_pressure_does_not_exceed_upstream(self):
        """Test that downstream pressure never exceeds upstream."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Downstream should never exceed upstream
        assert all(df['pressure_psig'] <= df['upstream_pressure_psig'] + 0.1)  # Small tolerance
    
    def test_pressure_approaches_upstream(self):
        """Test that pressure approaches upstream pressure."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Final pressure should be close to upstream
        final_pressure = df['pressure_psig'].iloc[-1]
        upstream_pressure = df['upstream_pressure_psig'].iloc[-1]
        
        # Should reach equilibrium or be very close
        assert pytest.approx(final_pressure, abs=10) == upstream_pressure
    
    def test_pressure_monotonic_increase(self):
        """Test that pressure increases monotonically (never decreases)."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Check that pressure never decreases
        pressures = df['pressure_psig'].values
        for i in range(1, len(pressures)):
            assert pressures[i] >= pressures[i-1] - 0.01  # Small tolerance for rounding


class TestFlowRateBehavior:
    """Tests for flow rate behavior during simulation."""
    
    def test_flow_rate_positive_when_pressure_difference_exists(self):
        """Test that flow rate is positive when there's a pressure difference."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Flow rate should be positive while pressures differ (except initial)
        middle_rows = df[1:-1]  # Skip first and last
        if len(middle_rows) > 0:
            assert all(middle_rows['flowrate_lb_hr'] >= 0)
    
    def test_flow_rate_zero_at_equilibrium(self):
        """Test that flow rate approaches zero at equilibrium."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Final flow rate should be much smaller than peak
        peak_flow = df['flowrate_lb_hr'].max()
        final_flow = df['flowrate_lb_hr'].iloc[-1]
        # At equilibrium, flow should be < 5% of peak (reasonable threshold)
        assert final_flow < peak_flow * 0.05
    
    def test_peak_flow_occurs(self):
        """Test that flow rate has a peak value."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Peak flow should be greater than initial and final
        peak_flow = df['flowrate_lb_hr'].max()
        assert peak_flow > df['flowrate_lb_hr'].iloc[0]
        assert peak_flow > df['flowrate_lb_hr'].iloc[-1]


class TestFlowRegimeDetection:
    """Tests for flow regime detection."""
    
    def test_regime_starts_as_choked_or_none(self):
        """Test that flow regime starts appropriately."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # First regime should be None (no flow yet) or Choked (if valve opens immediately)
        first_regime = df['flow_regime'].iloc[0]
        assert first_regime in ['None', 'Choked']
    
    def test_regime_ends_as_equilibrium_or_subsonic(self):
        """Test that final regime is Equilibrium or Subsonic (near equilibrium)."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Final regime should be Equilibrium or Subsonic (very close to equilibrium)
        final_regime = df['flow_regime'].iloc[-1]
        assert final_regime in ['Equilibrium', 'Subsonic']
    
    def test_regime_transitions(self):
        """Test that regime transitions occur (Choked -> Subsonic -> Equilibrium)."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Should have at least Choked and Equilibrium
        unique_regimes = df['flow_regime'].unique()
        assert len(unique_regimes) >= 2


class TestParameterSensitivity:
    """Tests for sensitivity to input parameters."""
    
    def test_larger_valve_gives_faster_pressurization(self):
        """Test that larger valve results in faster pressurization."""
        df_small = run_simulation(
            P_up_psig=500, P_down_init_psig=0, volume_ft3=100,
            valve_id_inch=1, opening_time_s=5, temp_f=70,
            molar_mass=29, z_factor=1.0, k_ratio=1.4
        )
        
        df_large = run_simulation(
            P_up_psig=500, P_down_init_psig=0, volume_ft3=100,
            valve_id_inch=3, opening_time_s=5, temp_f=70,
            molar_mass=29, z_factor=1.0, k_ratio=1.4
        )
        
        # Larger valve should have higher peak flow
        assert df_large['flowrate_lb_hr'].max() > df_small['flowrate_lb_hr'].max()
    
    def test_larger_volume_gives_slower_pressurization(self):
        """Test that larger volume results in slower pressurization."""
        df_small = run_simulation(
            P_up_psig=500, P_down_init_psig=0, volume_ft3=50,
            valve_id_inch=2, opening_time_s=5, temp_f=70,
            molar_mass=29, z_factor=1.0, k_ratio=1.4
        )
        
        df_large = run_simulation(
            P_up_psig=500, P_down_init_psig=0, volume_ft3=200,
            valve_id_inch=2, opening_time_s=5, temp_f=70,
            molar_mass=29, z_factor=1.0, k_ratio=1.4
        )
        
        # At same time, smaller volume should have higher pressure
        # Compare at 50% of opening time
        time_check = 2.5
        
        idx_small = _find_time_index(df_small, time_check)
        idx_large = _find_time_index(df_large, time_check)
        
        assert df_small['pressure_psig'].iloc[idx_small] > df_large['pressure_psig'].iloc[idx_large]


class TestCompositionMode:
    """Tests for composition-based property calculations."""
    
    def test_composition_mode_runs(self):
        """Test that composition mode executes successfully."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,  # Will be overridden
            z_factor=1.0,   # Will be overridden
            k_ratio=1.4,    # Will be overridden
            property_mode='composition',
            composition="Methane=0.9, Ethane=0.1"
        )
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    
    def test_composition_mode_has_extra_columns(self):
        """Test that composition mode adds property columns."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4,
            property_mode='composition',
            composition="Methane=1.0"
        )
        
        # Should have additional columns
        assert 'z_factor' in df.columns
        assert 'k_ratio' in df.columns
        assert 'molar_mass' in df.columns


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_equal_initial_pressures(self):
        """Test simulation when initial pressures are equal."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=500,  # Same as upstream
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Should complete quickly with no flow
        assert len(df) > 0
        assert df['flowrate_lb_hr'].max() < 100  # Very little flow
    
    def test_very_small_valve(self):
        """Test simulation with very small valve."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=0.1,  # Very small
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Should still complete
        assert len(df) > 0
        # Flow should be small
        assert df['flowrate_lb_hr'].max() < 1000
    
    def test_zero_opening_time(self):
        """Test simulation with zero opening time (instant opening)."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=0,  # Instant
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Should complete
        assert len(df) > 0
        # Valve should be fully open from start - check first row after t=0
        first_nonzero_idx = _find_time_index(df, 0.01)  # First timestep after t=0
        if first_nonzero_idx >= 0:
            assert df['valve_opening_pct'].iloc[first_nonzero_idx] == 100.0


class TestUnitConsistency:
    """Tests for unit consistency and reasonable output values."""
    
    def test_reasonable_flow_rates(self):
        """Test that flow rates are in reasonable range."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Flow rates should be positive and reasonable (not astronomical)
        assert all(df['flowrate_lb_hr'] >= 0)
        assert df['flowrate_lb_hr'].max() < 1e6  # Less than a million lb/hr
    
    def test_reasonable_pressures(self):
        """Test that pressures stay in reasonable ranges."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Pressures should be reasonable
        assert all(df['pressure_psig'] >= -15)  # Not below perfect vacuum
        assert all(df['pressure_psig'] <= 600)  # Not above upstream + margin
    
    def test_time_increments(self):
        """Test that time increments are consistent."""
        df = run_simulation(
            P_up_psig=500,
            P_down_init_psig=0,
            volume_ft3=100,
            valve_id_inch=2,
            opening_time_s=5,
            temp_f=70,
            molar_mass=29,
            z_factor=1.0,
            k_ratio=1.4
        )
        
        # Time should increase monotonically
        times = df['time'].values
        for i in range(1, len(times)):
            assert times[i] > times[i-1]
