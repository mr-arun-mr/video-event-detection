from functools import wraps

from flask import Flask, jsonify, request

from auth import generate_token, validate_token

app = Flask(__name__)

DETECTABLE_OBJECTS = {"person", "car", "truck", "bus", "motorbike", "fire", "smoke"}

EVENT_TYPE_MAP = {
    "person": "HUMAN_DETECTED",
    "car": "VEHICLE_DETECTED",
    "truck": "VEHICLE_DETECTED",
    "bus": "VEHICLE_DETECTED",
    "motorbike": "VEHICLE_DETECTED",
    "fire": "FIRE_DETECTED",
    "smoke": "SMOKE_DETECTED",
}


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Invalid or expired token"}), 401
        token = auth_header[7:]
        try:
            payload = validate_token(token)
            request.user = payload
        except ValueError:
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(*args, **kwargs)

    return decorated


@app.route("/auth/token", methods=["POST"])
def get_token():
    data = request.get_json() or {}
    user_id = data.get("user_id", "anonymous")
    token = generate_token(user_id)
    return jsonify({"token": token})


@app.route("/pipeline/run", methods=["POST"])
@require_auth
def run_pipeline():
    data = request.get_json() or {}
    scenario = data.get("scenario", {})
    events = _process_scenario(scenario)
    return jsonify({"status": "ok", "events": events})


@app.route("/events", methods=["GET"])
@require_auth
def list_events():
    import json, os

    event_file = os.path.join(os.path.dirname(__file__), "events", "events.json")
    events = []
    if os.path.exists(event_file):
        with open(event_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    return jsonify({"status": "ok", "events": events})


def _process_scenario(scenario: dict) -> list:
    detections = scenario.get("detections", [])
    events = []
    for detection in detections:
        obj = detection.get("object", "")
        if obj not in DETECTABLE_OBJECTS:
            continue
        events.append(
            {
                "event_type": EVENT_TYPE_MAP.get(obj, "UNKNOWN"),
                "object": obj,
                "confidence": float(detection.get("confidence", 0.9)),
            }
        )
    return events


if __name__ == "__main__":
    app.run(debug=True)
