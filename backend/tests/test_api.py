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

    response = client.post("/simulate", json=payload, headers={"x-unit-system": "imperial"})
    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    assert "peak_flow" in data
    assert len(data["results"]) > 0
    assert data["results"][0]["pressure"] >= 0


def test_streaming_simulation():
    payload = {
        "p_up": 500,
        "p_down_init": 0,
        "upstream_volume": 100, 
        "upstream_temp": 70,
        "downstream_volume": 100, 
        "downstream_temp": 70,
        "valve_id": 0.5, # larger valve
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

    with client.stream("POST", "/simulate/stream", json=payload, headers={"x-unit-system": "imperial"}) as response:
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


def test_property_calculation():
    payload = {
        "composition": "Methane=0.9, Ethane=0.1",
        "pressure": 500,
        "temp": 70,
    }

    response = client.post("/properties", json=payload, headers={"x-unit-system": "imperial"})
    assert response.status_code == 200
    props = response.json()

    assert "Z" in props
    assert "k" in props
    assert "M" in props
    assert props["Z"] > 0
