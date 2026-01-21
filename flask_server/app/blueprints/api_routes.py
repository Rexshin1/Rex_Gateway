from flask import Blueprint, jsonify, request
from flask_server.app import csrf
from flask_server.app.controller.network_controller import DeviceNetwork
from flask_jwt_extended import jwt_required
from flask_server.app.controller.auth_controller import AuthController
from flask_server.app.controller.api.device_controller import DeviceController
from flask_server.app.controller.api.network_controller import DeviceNetwork



api_app = Blueprint('api', __name__, url_prefix='/api')



@api_app.route('/login', methods=['POST'])
@csrf.exempt
def login():
    return AuthController.api_login()

@api_app.route('/register', methods=['POST'])
@csrf.exempt
def register():
    return AuthController.api_register()

@api_app.route('/scan_ip', methods=['POST'])
@csrf.exempt
@jwt_required()
def scan_ip():
    return DeviceNetwork.scan_network()

@api_app.route('/list_devices', methods=['POST'])
@csrf.exempt
@jwt_required()
def list_devices():
    return DeviceController.list_devices()

from functools import wraps
from config import config

def require_api_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-API-TOKEN')
        if not token or token != config.token_api:
            return jsonify({"code": 401, "message": "Unauthorized: Invalid or Missing API Token"}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_app.route('/add_device', methods=['POST'])
@csrf.exempt
def add_device():
    return DeviceController.add_device()

@api_app.route('/add_data_record', methods=['POST'])
@csrf.exempt
def add_data_record():
    return DeviceController.add_data_record()

@api_app.route('/add_power', methods=['POST'])
@csrf.exempt
def add_power():
    return DeviceController.add_power()

@api_app.route('/add_lux', methods=['POST'])
@csrf.exempt
def add_lux():
    return DeviceController.add_lux()

@api_app.route('/add_gas', methods=['POST'])
@csrf.exempt
def add_gas():
    return DeviceController.add_gas()

@api_app.route('/add_smoke', methods=['POST'])
@csrf.exempt
def add_smoke():
    return DeviceController.add_smoke()

@api_app.route('/add_water', methods=['POST'])
@csrf.exempt
def add_water():
    return DeviceController.add_water()

@api_app.route('/add_fire', methods=['POST'])
@csrf.exempt
def add_fire():
    return DeviceController.add_fire()

@api_app.route('/add_weather', methods=['POST'])
@csrf.exempt
def add_weather():
    return DeviceController.add_weather()

@api_app.route('/add_humidity_temp', methods=['POST'])
@csrf.exempt
def add_humidity_temp():
    return DeviceController.add_humidity_temp()

@api_app.route('/update_device', methods=['POST'])
@csrf.exempt
def update_device():
    return DeviceController.update_device()

@api_app.route('/delete_device', methods=['POST'])
@csrf.exempt
def delete_device():
    return DeviceController.delete_device()

@api_app.route('/devices', methods=['GET'])
@csrf.exempt
def get_devices():
    return DeviceController.list_devices()

@api_app.route('/records', methods=['GET'])
@csrf.exempt
def get_records():
    return DeviceController.get_data_records()

# Type-Specific Routes
@api_app.route('/get_power/<device_id>', methods=['GET'])
@csrf.exempt
def get_power_json_api(device_id):
    return DeviceController.get_power_json(device_id)

@api_app.route('/get_lux/<device_id>', methods=['GET'])
@csrf.exempt
def get_lux_json_api(device_id):
    return DeviceController.get_lux_json(device_id)

@api_app.route('/get_gas/<device_id>', methods=['GET'])
@csrf.exempt
def get_gas_json_api(device_id):
    return DeviceController.get_gas_json(device_id)

@api_app.route('/get_smoke/<device_id>', methods=['GET'])
@csrf.exempt
def get_smoke_json_api(device_id):
    return DeviceController.get_smoke_json(device_id)

@api_app.route('/get_water/<device_id>', methods=['GET'])
@csrf.exempt
def get_water_json_api(device_id):
    return DeviceController.get_water_json(device_id)

@api_app.route('/get_fire/<device_id>', methods=['GET'])
@csrf.exempt
def get_fire_json_api(device_id):
    return DeviceController.get_fire_json(device_id)

@api_app.route('/get_weather/<device_id>', methods=['GET'])
@csrf.exempt
def get_weather_json_api(device_id):
    return DeviceController.get_weather_json(device_id)

@api_app.route('/get_humidity_temp/<device_id>', methods=['GET'])
@csrf.exempt
def get_humidity_temp_json_api(device_id):
    return DeviceController.get_humidity_temp_json(device_id)
    

@api_app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = {"id": item_id, "name": f"Item {item_id}"}
    return jsonify(item)

@api_app.route('/items', methods=['POST'])
def create_item():
    data = request.json
    return jsonify({"message": "Item created", "item": data}), 201

# Bulk Sync Endpoint
@api_app.route('/sync/all', methods=['POST'])
@csrf.exempt
def sync_all_data():
    return DeviceController.sync_data_records()

@api_app.route('/sync/power', methods=['POST'])
@csrf.exempt
def sync_power():
    return DeviceController.sync_data_records('power')

@api_app.route('/sync/water', methods=['POST'])
@csrf.exempt
def sync_water():
    return DeviceController.sync_data_records('water')

@api_app.route('/sync/gas', methods=['POST'])
@csrf.exempt
def sync_gas():
    return DeviceController.sync_data_records('gas')

@api_app.route('/sync/smoke', methods=['POST'])
@csrf.exempt
def sync_smoke():
    return DeviceController.sync_data_records('smoke')

@api_app.route('/sync/fire', methods=['POST'])
@csrf.exempt
def sync_fire():
    return DeviceController.sync_data_records('fire')

@api_app.route('/sync/weather', methods=['POST'])
@csrf.exempt
def sync_weather():
    return DeviceController.sync_data_records('weather')

@api_app.route('/sync/lux', methods=['POST'])
@csrf.exempt
def sync_lux():
    return DeviceController.sync_data_records('lux')

@api_app.route('/sync/humidity_temp', methods=['POST'])
@csrf.exempt
def sync_humidity_temp():
    return DeviceController.sync_data_records('humidity_temp')

# PULL API (Cloud asks Gateway)
@api_app.route('/pull/all', methods=['POST'])
@csrf.exempt
def pull_all_data():
    return DeviceController.pull_data_records()

@api_app.route('/pull/power', methods=['POST'])
@csrf.exempt
def pull_power():
    return DeviceController.pull_data_records('power')

@api_app.route('/pull/water', methods=['POST'])
@csrf.exempt
def pull_water():
    return DeviceController.pull_data_records('water')

@api_app.route('/pull/gas', methods=['POST'])
@csrf.exempt
def pull_gas():
    return DeviceController.pull_data_records('gas')

@api_app.route('/pull/smoke', methods=['POST'])
@csrf.exempt
def pull_smoke():
    return DeviceController.pull_data_records('smoke')

@api_app.route('/pull/fire', methods=['POST'])
@csrf.exempt
def pull_fire():
    return DeviceController.pull_data_records('fire')

@api_app.route('/pull/weather', methods=['POST'])
@csrf.exempt
def pull_weather():
    return DeviceController.pull_data_records('weather')

@api_app.route('/pull/lux', methods=['POST'])
@csrf.exempt
def pull_lux():
    return DeviceController.pull_data_records('lux')

@api_app.route('/pull/humidity_temp', methods=['POST'])
@csrf.exempt
def pull_humidity_temp():
    return DeviceController.pull_data_records('humidity_temp')

# --- DASHBOARD LIVE UPDATE ---
from flask_server.app.controller.home_Controller import HomeController

@api_app.route('/dashboard_updates', methods=['GET'])
def dashboard_updates():
    return HomeController.get_dashboard_updates()

