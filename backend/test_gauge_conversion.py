import json

from fastapi.testclient import TestClient
from pressurize.main import app

client = TestClient(app)


def test_gauge_pressure_conversion():
    # 500 psi gauge input
    payload = {
        "p_up": 500,
        "p_down_init": 0,
        "upstream_volume": 100,
        "upstream_temp": 70,
        "downstream_volume": 100,
        "downstream_temp": 70,
        "valve_id": 2.0,
        "opening_time": 5,
        "molar_mass": 28.97,
        "z_factor": 1.0,
        "k_ratio": 1.4,
        "discharge_coeff": 0.65,
        "opening_mode": "linear",
        "dt": 0.5,
    }

    with client.stream(
        "POST", "/simulate/stream", json=payload, headers={"x-unit-system": "imperial"}
    ) as response:
        assert response.status_code == 200
        for line in response.iter_lines():
            if line.startswith("data: "):
                msg = json.loads(line[6:])
                if msg["type"] == "chunk":
                    row = msg["rows"][0]
                    # Upstream pressure should be close to 500 psi gauge
                    # The value in JSON is already converted back to user units (psi) by PintGlass
                    p_up_user = row["upstream_pressure"]
                    print(f"DEBUG: Row P_up (user units) = {p_up_user}")
                    assert abs(p_up_user - 500) < 1.0
                elif msg["type"] == "complete":
                    # For a 0->500 equalization, final pressure should be around 250 psi gauge
                    final_p = msg["final_pressure"]
                    print(f"DEBUG: Final Pressure (user units) = {final_p}")
                    # 250 psi gauge is ~1723689 Pa
                    # If it was absolute, it would be ~1825014 Pa
                    assert 200 < final_p < 300
                    # )  # Just a loose check it's not absolute Pa scale


if __name__ == "__main__":
    test_gauge_pressure_conversion()
