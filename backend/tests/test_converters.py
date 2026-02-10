"""Test suite for SimulationRequest unit conversions.

Verifies that the API schema correctly converts inputs (assumed Imperial)
to internal SI units (Pascal, Kelvin, meters, m³).
"""

import pytest
from pint_glass import unit_context
from pressurize.api.schemas import SimulationRequest


@pytest.fixture(autouse=True)
def set_imperial_context():
    """Ensure tests run in imperial context as default for external API."""
    token = unit_context.set("imperial")
    yield
    unit_context.reset(token)


class TestSimulationRequestConversion:
    """Tests for automatic unit conversion in SimulationRequest."""

    def test_temperature_conversion_to_kelvin(self):
        """Test that temperature inputs (F) are converted to Kelvin."""
        # 212°F = 373.15 K
        # 32°F = 273.15 K

        req = SimulationRequest(
            mode="equalize",
            p_up=0.0,
            upstream_volume=10.0,
            upstream_temp=212.0,  # 212 F
            p_down_init=0.0,
            downstream_volume=10.0,
            downstream_temp=32.0,  # 32 F
            valve_id=1.0,
            opening_time=10.0,
            molar_mass=28.0,
            z_factor=1.0,
            k_ratio=1.4,
        )

        # Check upstream temp (212 F -> 373.15 K)
        assert pytest.approx(req.upstream_temp, abs=0.1) == 373.15

        # Check downstream temp (32 F -> 273.15 K)
        assert pytest.approx(req.downstream_temp, abs=0.1) == 273.15

    def test_pressure_conversion_psi_to_pa(self):
        """Test that pressure inputs (psi) are converted to Absolute Pa."""
        # 14.696 psi = 101325 Pa
        # 0 psi = 0 Pa

        req = SimulationRequest(
            mode="equalize",
            p_up=0.0,  # 0 psi
            upstream_volume=10.0,
            upstream_temp=70.0,
            p_down_init=14.696,  # 14.696 psi
            downstream_volume=10.0,
            downstream_temp=70.0,
            valve_id=1.0,
            opening_time=10.0,
            molar_mass=28.0,
            z_factor=1.0,
            k_ratio=1.4,
        )

        # 0 psi -> 0 Pa
        assert pytest.approx(req.p_up, abs=0.1) == 0.0

        # 14.696 psi -> 101325 Pa
        assert pytest.approx(req.p_down_init, rel=0.01) == 101325.0

    def test_length_conversion_to_meters(self):
        """Test that length inputs (feet) are converted to meters."""
        # 1 ft = 0.3048 m

        req = SimulationRequest(
            mode="equalize",
            p_up=100.0,
            upstream_volume=10.0,
            upstream_temp=70.0,
            p_down_init=0.0,
            downstream_volume=10.0,
            downstream_temp=70.0,
            valve_id=1.0,  # 1 ft
            opening_time=10.0,
            molar_mass=28.0,
            z_factor=1.0,
            k_ratio=1.4,
        )

        assert pytest.approx(req.valve_id, abs=0.0001) == 0.3048

    def test_volume_conversion_to_cubic_meters(self):
        """Test that volume inputs (ft³) are converted to m³."""
        # 1 ft³ = 0.0283168 m³

        req = SimulationRequest(
            mode="equalize",
            p_up=100.0,
            upstream_volume=1.0,  # 1 ft³
            upstream_temp=70.0,
            p_down_init=0.0,
            downstream_volume=100.0,  # 100 ft³
            downstream_temp=70.0,
            valve_id=1.0,
            opening_time=10.0,
            molar_mass=28.0,
            z_factor=1.0,
            k_ratio=1.4,
        )

        assert pytest.approx(req.upstream_volume, abs=0.0001) == 0.0283168
        assert pytest.approx(req.downstream_volume, abs=0.001) == 2.83168
