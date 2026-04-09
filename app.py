from flask import Flask, request, jsonify, render_template
from prometheus_client import Counter, generate_latest
from flask import Response
import mysql.connector
import time

app = Flask(__name__)
REQUEST_COUNT = Counter('app_requests_total', 'Total HTTP Requests')

# -------------------------------
# WAIT FOR DB (VERY IMPORTANT FOR DOCKER)
# -------------------------------
def wait_for_db():
    while True:
        try:
            conn = mysql.connector.connect(
                host="mariadb-service",
                user="root",
                password="root"
            )
            conn.close()
            print("✅ MySQL Ready!")
            break
        except:
            print("⏳ Waiting for MySQL...")
            time.sleep(2)

wait_for_db()


# -------------------------------
# DATABASE CONNECTION
# -------------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="mariadb-service",
        user="root",
        password="root",
        database="incidents_db"
    )


# -------------------------------
# INITIALIZE DATABASE
# -------------------------------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id INT AUTO_INCREMENT PRIMARY KEY,
        incident_id VARCHAR(20) UNIQUE,
        service VARCHAR(255),
        severity VARCHAR(50),
        description TEXT,
        status VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NULL
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()

init_db()


# -------------------------------
# HOME ROUTE
# -------------------------------
@app.route("/")
def home():
    REQUEST_COUNT.inc()
    return render_template("index.html")



# -------------------------------
# CREATE INCIDENT (FIXED)
# -------------------------------
@app.route("/incidents", methods=["POST"])
def create_incident():
    REQUEST_COUNT.inc()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    body = request.json

    # safer ID generation
    cursor.execute("SELECT MAX(id) as max_id FROM incidents")
    result = cursor.fetchone()
    next_id = (result["max_id"] or 0) + 1

    incident_id = f"INC-{next_id:03}"

    query = """
    INSERT INTO incidents (incident_id, service, severity, description, status)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        incident_id,
        body.get("service"),
        body.get("severity"),
        body.get("description"),
        "Open"
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Incident created",
        "incident_id": incident_id
    }), 201


# -------------------------------
# GET ALL INCIDENTS
# -------------------------------
@app.route("/incidents", methods=["GET"])
def get_incidents():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM incidents ORDER BY created_at DESC")
    incidents = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(incidents)


# -------------------------------
# UPDATE INCIDENT
# -------------------------------
@app.route("/incidents/<incident_id>", methods=["PUT"])
def update_incident(incident_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    body = request.json

    cursor.execute("SELECT * FROM incidents WHERE incident_id=%s", (incident_id,))
    incident = cursor.fetchone()

    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    status = body.get("status", incident["status"])
    severity = body.get("severity", incident["severity"])
    description = body.get("description", incident["description"])

    query = """
    UPDATE incidents 
    SET status=%s, severity=%s, description=%s, updated_at=NOW()
    WHERE incident_id=%s
    """

    cursor.execute(query, (status, severity, description, incident_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Incident updated"})


# -------------------------------
# DELETE INCIDENT
# -------------------------------
@app.route("/incidents/<incident_id>", methods=["DELETE"])
def delete_incident(incident_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM incidents WHERE incident_id=%s",
        (incident_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Incident deleted"})


#--------------------------------------------------
@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype='text/plain')
#-------------------------------------------

# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)