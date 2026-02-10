import json

from fastapi.testclient import TestClient
from pressurize.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Pressurize API is running"}


def test_get_components():
    response = client.get("/components")
    assert response.status_code == 200
    components = response.json()
    assert isinstance(components, list)
    assert "Methane" in components


def test_get_presets():
    response = client.get("/presets")
    assert response.status_code == 200
    presets = response.json()
    assert isinstance(presets, list)
    # Check structure
    assert "id" in presets[0]
    assert "name" in presets[0]


def test_get_preset_details():
    response = client.get("/presets/natural_gas")
    assert response.status_code == 200
    comp = response.json()
    assert isinstance(comp, dict)
    assert "Methane" in comp
    assert comp["Methane"] > 0


def test_simulation_workflow():
    payload = {
        "p_up": 500,
        "p_down_init": 0,
        "upstream_volume": 100,
        "upstream_temp": 70,
        "downstream_volume": 100,
        "downstream_temp": 70,
        "valve_id": 0.1667,  # 2 inches in ft
        "opening_time": 5,
        "molar_mass": 28.97,
        "z_factor": 1.0,
        "k_ratio": 1.4,
        "discharge_coeff": 0.65,
        "opening_mode": "linear",
        "dt": 0.5,  # Larger dt for faster test
    }

    complete = None
    chunk_count = 0

    with client.stream(
        "POST", "/simulate/stream", json=payload, headers={"x-unit-system": "imperial"}
    ) as response:
        assert response.status_code == 200

        for line in response.iter_lines():
            if not line:
                continue

            if line.startswith("data: "):
                data_content = line[6:].strip()
                if not data_content:
                    continue
                try:
                    msg = json.loads(data_content)
                    if msg.get("type") == "chunk":
                        chunk_count += 1
                    elif msg.get("type") == "complete":
                        complete = msg
                        break
                except json.JSONDecodeError:
                    continue

    assert chunk_count >= 1
    assert complete is not None
    assert complete["peak_flow"] >= 0
    assert "final_pressure" in complete


def test_streaming_simulation():
    payload = {
        "p_up": 500,
        "p_down_init": 0,
        "upstream_volume": 100,
        "upstream_temp": 70,
        "downstream_volume": 100,
        "downstream_temp": 70,
        "valve_id": 0.5,  # larger valve
        "opening_time": 5,
        "molar_mass": 28.97,
        "z_factor": 1.0,
        "k_ratio": 1.4,
        "discharge_coeff": 0.65,
        "opening_mode": "linear",
        "dt": 0.1,
    }
    complete = None
    chunk_count = 0

    with client.stream(
        "POST", "/simulate/stream", json=payload, headers={"x-unit-system": "imperial"}
    ) as response:
        assert response.status_code == 200

        for line in response.iter_lines():
            if not line:
                continue

            if line.startswith("data: "):
                data_content = line[6:].strip()
                if not data_content:
                    continue
                try:
                    msg = json.loads(data_content)
                    if msg.get("type") == "chunk":
                        chunk_count += 1
                    elif msg.get("type") == "complete":
                        complete = msg
                        break
                except json.JSONDecodeError:
                    continue

    assert chunk_count >= 1
    assert complete is not None
    assert complete["peak_flow"] >= 0
    assert "final_pressure" in complete


def test_simulation_engg_field_kpis():
    """Test simulation with engg_field unit system and verify all 4 KPIs.

    Inputs (engg_field units: psi, ft³, °F, in, s):
        - Mode: equalize
        - Upstream: 1350 psig, 1980 ft³, 248 °F
        - Downstream: 900 psig, 22319 ft³, 248 °F
        - Valve: 0.75 in, fixed open, Cd=0.90
        - Gas: composition mode (natural gas blend), k=1.43, MW=16.89, Z=0.95
        - Opening time: 5 s

    Expected KPIs (engg_field output: lb/hr, psig, s, lb):
        - Peak Flow Rate:    36,045 lb/hr
        - Final Pressure:       936.7 psig
        - Equilibrium Time:     422.6 s
        - Total Mass Flow:    1,892.1 lb
    """
    payload = {
        "mode": "equalize",
        "p_up": 1350.0,
        "p_down_init": 900.0,
        "upstream_volume": 1980.0,
        "upstream_temp": 248.0,
        "downstream_volume": 22319.0,
        "downstream_temp": 248.0,
        "valve_id": 0.75,
        "opening_time": 5.0,
        "molar_mass": 16.89,
        "z_factor": 0.95,
        "k_ratio": 1.43,
        "discharge_coeff": 0.90,
        "opening_mode": "fixed",
        "valve_action": "open",
        "property_mode": "composition",
        "composition": "Methane=0.9387, Ethane=0.0121, Propane=0.0004, Carbon dioxide=0.0054, Nitrogen=0.0433",
    }

    complete = None
    chunk_count = 0

    with client.stream(
        "POST",
        "/simulate/stream",
        json=payload,
        headers={"x-unit-system": "engg_field"},
    ) as response:
        assert response.status_code == 200

        for line in response.iter_lines():
            if not line:
                continue

            if line.startswith("data: "):
                data_content = line[6:].strip()
                if not data_content:
                    continue
                try:
                    msg = json.loads(data_content)
                    if msg.get("type") == "chunk":
                        chunk_count += 1
                    elif msg.get("type") == "complete":
                        complete = msg
                        break
                except json.JSONDecodeError:
                    continue

    assert chunk_count >= 1, "Should receive at least one data chunk"
    assert complete is not None, "Should receive a 'complete' message"

    # Verify all 4 KPIs within 5% tolerance
    tolerance = 0.05

    peak_flow = complete["peak_flow"]
    assert abs(peak_flow - 36045) / 36045 < tolerance, (
        f"Peak Flow Rate: expected ~36,045 lb/hr, got {peak_flow}"
    )

    final_pressure = complete["final_pressure"]
    assert abs(final_pressure - 936.7) / 936.7 < tolerance, (
        f"Final Pressure: expected ~936.7 psig, got {final_pressure}"
    )

    equilibrium_time = complete["equilibrium_time"]
    assert abs(equilibrium_time - 422.6) / 422.6 < tolerance, (
        f"Equilibrium Time: expected ~422.6 s, got {equilibrium_time}"
    )

    total_mass = complete["total_mass"]
    assert abs(total_mass - 1892.1) / 1892.1 < tolerance, (
        f"Total Mass Flow: expected ~1,892.1 lb, got {total_mass}"
    )


def test_property_calculation():
    payload = {
        "composition": "Methane=0.9, Ethane=0.1",
        "pressure": 500,
        "temp": 70,
    }

    response = client.post(
        "/properties", json=payload, headers={"x-unit-system": "imperial"}
    )
    assert response.status_code == 200
    props = response.json()

    assert "Z" in props
    assert "k" in props
    assert "M" in props
    assert props["Z"] > 0
