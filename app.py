from flask import Flask, request, jsonify , render_template
from datetime import datetime
import json

app = Flask(__name__)

# ✅ ADD IT HERE
@app.route("/")
def home():
    return render_template('index.html')

FILE = "incidents.json"

def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

# ✅ CREATE INCIDENT
@app.route("/incidents", methods=["POST"])
def create_incident():
    data = load_data()
    body = request.json

    if data:
        last_id = max(int(inc["id"].split("-")[1]) for inc in data)
        incident_id = f"INC-{last_id + 1:03}"
    else:
        incident_id = "INC-001"

    incident = {
        "id": incident_id,
        "service": body["service"],
        "severity": body["severity"],
        "description": body["description"],
        "status": "Open",
        "created_at": str(datetime.now())
    }

    data.append(incident)
    save_data(data)

    return jsonify(incident), 201


# ✅ GET ALL INCIDENTS
@app.route("/incidents", methods=["GET"])
def get_incidents():
    return jsonify(load_data())


# ✅ UPDATE INCIDENT
@app.route("/incidents/<incident_id>", methods=["PUT"])
def update_incident(incident_id):
    data = load_data()

    for inc in data:
        if inc["id"] == incident_id:
            body = request.json

            if "status" in body:
                inc["status"] = body["status"]

            if "severity" in body:
                inc["severity"] = body["severity"]

            if "description" in body:
                inc["description"] = body["description"]

            inc["updated_at"] = str(datetime.now())
            save_data(data)

            return jsonify(inc)

    return jsonify({"error": "Not found"}), 404


# ✅ DELETE INCIDENT
@app.route("/incidents/<incident_id>", methods=["DELETE"])
def delete_incident(incident_id):
    data = load_data()

    for inc in data:
        if inc["id"] == incident_id:
            data.remove(inc)
            save_data(data)
            return jsonify({"message": "Deleted"})

    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)