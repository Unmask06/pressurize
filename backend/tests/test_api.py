from pressurize.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Pressurize API is running"}

def test_get_components():
    response = client.get("/pressurize/components")
    assert response.status_code == 200
    components = response.json()
    assert isinstance(components, list)
    assert "Methane" in components

def test_get_presets():
    response = client.get("/pressurize/presets")
    assert response.status_code == 200
    presets = response.json()
    assert isinstance(presets, list)
    # Check structure
    assert "id" in presets[0]
    assert "name" in presets[0]

def test_simulation_workflow():
    payload = {
        "p_up_psig": 500,
        "volume_ft3": 100,
        "valve_id_inch": 2,
        "opening_time_s": 5,
        "temp_f": 70,
        "molar_mass": 28.97,
        "z_factor": 1.0,
        "k_ratio": 1.4,
        "discharge_coeff": 0.65,
        "opening_mode": "linear",
        "dt": 0.5 # Larger dt for faster test
    }
    
    response = client.post("/pressurize/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "results" in data
    assert "peak_flow" in data
    assert len(data["results"]) > 0
    assert data["results"][0]["pressure_psig"] >= 0

def test_property_calculation():
    payload = {
        "composition": "Methane=0.9, Ethane=0.1",
        "pressure_psig": 500,
        "temp_f": 70
    }
    
    response = client.post("/pressurize/properties", json=payload)
    assert response.status_code == 200
    props = response.json()
    
    assert "Z" in props
    assert "k" in props
    assert "M" in props
    assert props["Z"] > 0
