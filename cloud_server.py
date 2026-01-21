from flask import Flask, request, jsonify, render_template_string
import logging
import datetime
import json
import os

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [CLOUD] %(message)s')

app = Flask(__name__)

# Simpan data di Memory (List) sementara
DB_FILE = 'cloud_db.json'

def load_db():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_db():
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(CLOUD_DB, f, indent=2)
    except Exception as e:
        print(f"Error saving DB: {e}")

CLOUD_DB = load_db()

# HTML Dashboard Sederhana (Updated untuk menampilkan Raw JSON)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloud Server Center</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <meta http-equiv="refresh" content="3"> 
    <style>
        body{background:#111; color:#ddd; font-family: 'Segoe UI', monospace;} 
        .table{color:#eee; font-size: 13px;}
        pre { margin: 0; white-space: pre-wrap; font-size: 11px; color: #8fd3fe; }
    </style>
</head>
<body class="p-4">
    <div class="container-fluid">
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom border-secondary pb-3">
            <div>
                <h2 class="mb-0">☁️ Cloud Server</h2>
                <small class="text-muted">Universal Endpoint for IoT Gateway (Port 5002)</small>
            </div>
            <div class="text-end">
                <span class="badge bg-primary fs-5 rounded-0">{{ count }} Records</span>
                <a href="/api/v1/debug/clear" class="btn btn-sm btn-outline-danger ms-2 rounded-0">Clear Data</a>
            </div>
        </div>
        
        <div class="card bg-dark border-secondary rounded-0">
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-dark table-hover mb-0 align-middle">
                        <thead>
                            <tr class="table-secondary text-dark text-uppercase small">
                                <th style="width: 100px;">Recv Time</th>
                                <th style="width: 150px;">DEVICE ID</th>
                                <th style="width: 150px;">ENDPOINT / TYPE</th>
                                <th>RAW JSON PAYLOAD (AS RECEIVED)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in data %}
                            <tr>
                                <td class="text-info font-monospace">{{ row.recv }}</td>
                                <td class="fw-bold">{{ row.device_id }}</td>
                                <td class="text-warning">{{ row.type }}</td>
                                <td>
                                    <!-- Menampilkan Raw JSON -->
                                    <pre>{{ row.raw_str }}</pre>
                                </td>
                            </tr>
                            {% endfor %}
                            
                            {% if not data %}
                            <tr>
                                <td colspan="4" class="text-center py-5 text-muted fst-italic">
                                    Waiting for incoming data stream...
                                </td>
                            </tr>
                            {% endif %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    """Halaman Dashboard Web (HTML)"""
    # Tampilkan 50 data terakhir (terbalik agar yang baru di atas)
    return render_template_string(DASHBOARD_HTML, data=CLOUD_DB[-50:][::-1], count=len(CLOUD_DB))

@app.route('/api/v1/debug/clear', methods=['GET'])
def clear_storage():
    """Reset Memori"""
    CLOUD_DB.clear()
    save_db()
    return render_template_string("<script>window.location.href='/'</script>")

def process_payload(endpoint_name):
    """
    Unified Processor that handles guessing fields for the UI.
    Explicitly looking for 'device_id' and determining 'type' from endpoint.
    """
    try:
        payload = request.json
        if payload is None:
            return jsonify({"status": "error", "message": "No JSON payload"}), 400

        incoming_items = payload if isinstance(payload, list) else [payload]
        count = 0
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        
        print(f"\\n [CLOUD] Received on {endpoint_name}: {json.dumps(payload)}")

        for item in incoming_items:
            # --- LOGIC VISUAL DASHBOARD ---
            # 1. Determine Type from Endpoint Name
            # e.g. 'add_power' -> 'power'
            type_label = endpoint_name.replace('add_', '')
            if type_label == 'sync': type_label = 'generic'

            # 2. Determine Device ID from Payload
            device_id_label = "-"
            
            if isinstance(item, dict):
                 # Priority search for Device ID
                 # Checks: device_id, gw_id, id, serial, etc.
                for k, v in item.items():
                    k_lower = k.lower()
                    if k_lower in ['device_id', 'dev_id', 'device', 'gw_id', 'gateway_id', 'id', 'serial', 'id_alat', 'nomor_seri']:
                        device_id_label = str(v)
                        break
            
            CLOUD_DB.append({
                "recv": now_str,
                "device_id": device_id_label,  # Explicit Key
                "type": type_label,            # Explicit Key
                "raw_str": json.dumps(item, indent=2),
                "payload": item
            })
            count += 1
            
        save_db()
            
        return jsonify({"status": "success", "stored": count}), 200
    except Exception as e:
        print(f" Error: {e}")
        return jsonify({"error": str(e)}), 500

# Explicit Routes matching Rex Gateway Logic
@app.route('/api/v1/add_data_record', methods=['POST'])
def add_data_record(): return process_payload("add_data_record")

@app.route('/api/v1/add_power', methods=['POST'])
def add_power(): return process_payload("power")

@app.route('/api/v1/add_water', methods=['POST'])
def add_water(): return process_payload("water")

@app.route('/api/v1/add_gas', methods=['POST'])
def add_gas(): return process_payload("gas")

@app.route('/api/v1/add_smoke', methods=['POST'])
def add_smoke(): return process_payload("smoke")

@app.route('/api/v1/add_fire', methods=['POST'])
def add_fire(): return process_payload("fire")

@app.route('/api/v1/add_weather', methods=['POST'])
def add_weather(): return process_payload("weather")

@app.route('/api/v1/add_lux', methods=['POST'])
def add_lux(): return process_payload("lux")

@app.route('/api/v1/add_humidity_temp', methods=['POST'])
def add_humidity_temp(): return process_payload("humidity_temp")

@app.route('/api/v1/add_ultrasonic', methods=['POST'])
def add_ultrasonic(): return process_payload("ultrasonic")


# Universal Fallback (Just in case)
@app.route('/api/v1/sync', methods=['POST'])
def receive_sync(): return process_payload("sync")

@app.route('/<path:subpath>', methods=['POST'])
def catch_all_post(subpath):
    return process_payload(subpath)


if __name__ == "__main__":
    # RUN ON PORT 5002 TO AVOID CONFLICT WITH GATEWAY (5001)
    print("MOCK CLOUD RUNNING ON PORT 5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
