import glob
import json
import os

import pytest

SCENARIOS_DIR = os.path.join(os.path.dirname(__file__), "scenarios")


def _load_scenarios():
    files = sorted(glob.glob(os.path.join(SCENARIOS_DIR, "scenario_*.json")))
    scenarios = []
    for path in files:
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path) as f:
            data = json.load(f)
        scenarios.append((name, data))
    return scenarios


class TestScenario:
    @pytest.mark.parametrize("scenario_name,scenario_data", _load_scenarios())
    def test_scenario(self, client, auth_headers, scenario_name, scenario_data):
        response = client.post(
            "/pipeline/run",
            json={"scenario": scenario_data["input"]},
            headers=auth_headers,
        )
        assert response.status_code == 200, (
            f"Pipeline returned HTTP {response.status_code}: "
            f"{response.data.decode()}"
        )

        result = response.get_json()
        expected = scenario_data["expected"]

        assert result["status"] == expected["status"]

        if "event_type" in expected:
            assert any(
                e["event_type"] == expected["event_type"] for e in result["events"]
            ), (
                f"Expected event_type '{expected['event_type']}' not found in "
                f"{[e['event_type'] for e in result['events']]}"
            )

        if "event_count" in expected:
            assert len(result["events"]) == expected["event_count"], (
                f"Expected {expected['event_count']} events, got {len(result['events'])}"
            )

    def test_pipeline_rejects_missing_token(self, client):
        response = client.post("/pipeline/run", json={"scenario": {}})
        assert response.status_code == 401

    def test_pipeline_rejects_invalid_token(self, client):
        response = client.post(
            "/pipeline/run",
            json={"scenario": {}},
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_auth_token_endpoint(self, client):
        response = client.post("/auth/token", json={"user_id": "test"})
        assert response.status_code == 200
        assert "token" in response.get_json()
