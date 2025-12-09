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
    

@api_app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = {"id": item_id, "name": f"Item {item_id}"}
    return jsonify(item)

@api_app.route('/items', methods=['POST'])
def create_item():
    data = request.json
    return jsonify({"message": "Item created", "item": data}), 201
