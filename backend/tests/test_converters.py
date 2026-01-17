"""Test suite for unit conversion utilities.

This module tests temperature and pressure conversion functions.
"""

import pytest
from app.utils.converters import (
    fahrenheit_to_kelvin,
    pa_to_psig,
    psig_to_pa,
)


class TestTemperatureConversion:
    """Tests for temperature conversion."""
    
    def test_freezing_point(self):
        """Test conversion at water freezing point."""
        temp_f = 32.0
        temp_k = fahrenheit_to_kelvin(temp_f)
        assert pytest.approx(temp_k, abs=0.01) == 273.15
    
    def test_boiling_point(self):
        """Test conversion at water boiling point."""
        temp_f = 212.0
        temp_k = fahrenheit_to_kelvin(temp_f)
        assert pytest.approx(temp_k, abs=0.01) == 373.15
    
    def test_absolute_zero(self):
        """Test conversion at absolute zero."""
        temp_f = -459.67
        temp_k = fahrenheit_to_kelvin(temp_f)
        assert pytest.approx(temp_k, abs=0.01) == 0.0
    
    def test_room_temperature(self):
        """Test conversion at typical room temperature."""
        temp_f = 70.0
        temp_k = fahrenheit_to_kelvin(temp_f)
        # 70°F = 294.26 K
        assert pytest.approx(temp_k, abs=0.01) == 294.26
    
    def test_negative_fahrenheit(self):
        """Test conversion with negative Fahrenheit values."""
        temp_f = -40.0
        temp_k = fahrenheit_to_kelvin(temp_f)
        # -40°F = -40°C = 233.15 K
        assert pytest.approx(temp_k, abs=0.01) == 233.15


class TestPressureConversionPsigToPa:
    """Tests for psig to Pa conversion."""
    
    def test_atmospheric_pressure(self):
        """Test that 0 psig equals atmospheric pressure in Pa."""
        pressure_psig = 0.0
        pressure_pa = psig_to_pa(pressure_psig)
        # Atmospheric pressure ≈ 101,325 Pa
        assert pytest.approx(pressure_pa, rel=0.001) == 101325
    
    def test_positive_gauge_pressure(self):
        """Test conversion of positive gauge pressure."""
        pressure_psig = 14.696  # One atmosphere above atmospheric
        pressure_pa = psig_to_pa(pressure_psig)
        # Should be approximately 2 atmospheres = 202,650 Pa
        assert pytest.approx(pressure_pa, rel=0.001) == 202650
    
    def test_typical_industrial_pressure(self):
        """Test conversion of typical industrial pressure."""
        pressure_psig = 100.0
        pressure_pa = psig_to_pa(pressure_psig)
        # 100 psig ≈ 791,000 Pa
        assert pytest.approx(pressure_pa, rel=0.01) == 791000
    
    def test_negative_gauge_pressure(self):
        """Test conversion of negative gauge pressure (vacuum)."""
        pressure_psig = -5.0
        pressure_pa = psig_to_pa(pressure_psig)
        # Should be less than atmospheric
        assert pressure_pa < 101325
        assert pressure_pa > 0  # But still positive absolute pressure
    
    def test_high_pressure(self):
        """Test conversion of high pressure."""
        pressure_psig = 1000.0
        pressure_pa = psig_to_pa(pressure_psig)
        # Should be approximately 7 MPa (slightly under due to conversion)
        assert pressure_pa > 6.9e6
        assert pressure_pa < 7.1e6


class TestPressureConversionPaToPsig:
    """Tests for Pa to psig conversion."""
    
    def test_atmospheric_pressure(self):
        """Test that atmospheric pressure equals 0 psig."""
        pressure_pa = 101325.0
        pressure_psig = pa_to_psig(pressure_pa)
        assert pytest.approx(pressure_psig, abs=0.01) == 0.0
    
    def test_positive_absolute_pressure(self):
        """Test conversion of pressure above atmospheric."""
        pressure_pa = 202650.0  # Approximately 2 atmospheres
        pressure_psig = pa_to_psig(pressure_pa)
        # Should be approximately 14.696 psig
        assert pytest.approx(pressure_psig, rel=0.001) == 14.696
    
    def test_vacuum_pressure(self):
        """Test conversion of vacuum (below atmospheric)."""
        pressure_pa = 50000.0  # Below atmospheric
        pressure_psig = pa_to_psig(pressure_pa)
        # Should be negative
        assert pressure_psig < 0
    
    def test_high_pressure(self):
        """Test conversion of high absolute pressure."""
        pressure_pa = 7e6  # 7 MPa
        pressure_psig = pa_to_psig(pressure_pa)
        # Should be around 1000 psig
        assert 900 < pressure_psig < 1100


class TestRoundTripConversions:
    """Tests for round-trip conversion consistency."""
    
    def test_psig_to_pa_to_psig(self):
        """Test that converting psig->Pa->psig gives original value."""
        original_psig = 250.0
        pa = psig_to_pa(original_psig)
        final_psig = pa_to_psig(pa)
        assert pytest.approx(final_psig, rel=0.0001) == original_psig
    
    def test_pa_to_psig_to_pa(self):
        """Test that converting Pa->psig->Pa gives original value."""
        original_pa = 500000.0
        psig = pa_to_psig(original_pa)
        final_pa = psig_to_pa(psig)
        assert pytest.approx(final_pa, rel=0.0001) == original_pa
    
    def test_multiple_pressure_values(self):
        """Test round-trip conversions for multiple values."""
        test_values = [0, 10, 50, 100, 500, 1000, 2000]
        for psig in test_values:
            pa = psig_to_pa(psig)
            result = pa_to_psig(pa)
            assert pytest.approx(result, rel=0.0001) == psig


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_zero_temperature(self):
        """Test absolute zero temperature conversion."""
        temp_f = -459.67
        temp_k = fahrenheit_to_kelvin(temp_f)
        assert pytest.approx(temp_k, abs=0.1) == 0.0
    
    def test_very_high_temperature(self):
        """Test conversion of very high temperature."""
        temp_f = 1000.0
        temp_k = fahrenheit_to_kelvin(temp_f)
        assert temp_k > 500  # Should be reasonable
        # Verify calculation: (1000-32)*5/9 + 273.15 = 810.93 K
        assert pytest.approx(temp_k, abs=0.1) == 810.93
    
    def test_very_low_vacuum(self):
        """Test conversion of very low pressure (deep vacuum)."""
        pressure_pa = 1000.0  # 1000 Pa absolute
        pressure_psig = pa_to_psig(pressure_pa)
        # Should be strongly negative
        assert pressure_psig < -10
    
    def test_perfect_vacuum(self):
        """Test conversion at perfect vacuum (0 Pa)."""
        pressure_pa = 0.0
        pressure_psig = pa_to_psig(pressure_pa)
        # Should be -14.696 psig (negative of atmospheric)
        assert pytest.approx(pressure_psig, abs=0.01) == -14.696


class TestConsistency:
    """Tests for internal consistency and mathematical properties."""
    
    def test_pressure_conversion_linearity(self):
        """Test that pressure conversion is linear."""
        # If we double psig, Pa should not quite double (due to offset)
        psig1 = 100.0
        psig2 = 200.0
        
        pa1 = psig_to_pa(psig1)
        pa2 = psig_to_pa(psig2)
        
        # Difference should be linear
        diff = pa2 - pa1
        expected_diff = 100.0 * 6894.76  # 100 psi difference
        assert pytest.approx(diff, rel=0.001) == expected_diff
    
    def test_temperature_conversion_linearity(self):
        """Test that temperature conversion maintains proper offset."""
        # Test that a 180°F difference equals 100 K difference
        temp_f1 = 32.0   # Freezing point
        temp_f2 = 212.0  # Boiling point
        
        temp_k1 = fahrenheit_to_kelvin(temp_f1)
        temp_k2 = fahrenheit_to_kelvin(temp_f2)
        
        diff_k = temp_k2 - temp_k1
        # 180°F = 100 K
        assert pytest.approx(diff_k, abs=0.01) == 100.0
    
    def test_pressure_monotonicity(self):
        """Test that pressure conversions are monotonic."""
        # Higher psig should always give higher Pa
        pressures_psig = [0, 50, 100, 200, 500, 1000]
        pressures_pa = [psig_to_pa(p) for p in pressures_psig]
        
        # Check that each pressure is higher than the previous
        for i in range(1, len(pressures_pa)):
            assert pressures_pa[i] > pressures_pa[i-1]
    
    def test_temperature_monotonicity(self):
        """Test that temperature conversion is monotonic."""
        # Higher °F should always give higher K
        temps_f = [-100, 0, 32, 70, 100, 212, 500]
        temps_k = [fahrenheit_to_kelvin(t) for t in temps_f]
        
        # Check that each temperature is higher than the previous
        for i in range(1, len(temps_k)):
            assert temps_k[i] > temps_k[i-1]
