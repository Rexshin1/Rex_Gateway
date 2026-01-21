from flask import Blueprint, g
from flask_login import login_user, current_user, logout_user, login_required
from flask_server.app.controller.device_controller import DeviceController
from flask_server.app.controller.home_Controller import HomeController
from flask_server.app.controller.auth_controller import AuthController
from flask_server.app.controller.network_controller import DeviceNetwork
from flask_server.app.controller.settings_controller import SettingsController
from flask_server.app.controller.user_controller import UserController
from datetime import datetime, timedelta

web_app = Blueprint('app', __name__, url_prefix="/") 

@web_app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}

@web_app.app_template_filter('wib_format')
def wib_format(value):
    if value is None:
        return "-"
    # Add 7 hours to the timestamp
    wib_time = value + timedelta(hours=7)
    return wib_time.strftime('%Y-%m-%d %H:%M:%S')

@web_app.before_request
def set_global_title():
    g.title = "Dashboard Look"

@web_app.route('/login', methods=['GET','POST'])
def login():
    return AuthController.login()

@web_app.route('/logout', methods=['GET'])
@login_required
def logout():
    return AuthController.logout()

@web_app.route('/register', methods=['GET','POST'])
def register():
    return AuthController.register()

    return AuthController.register()

@web_app.route('/', methods=['GET'])
@login_required
def index():
    return HomeController.index()

@web_app.route('/list_devices', methods=['GET'])
@login_required
def list_device():
    return DeviceController.list_devices()

@web_app.route('/add_device', methods=['GET', 'POST'])
@login_required
def add_device():
    return DeviceController.add_device()

@web_app.route('/api/system_stats', methods=['GET'])
@login_required 
def system_stats():
    return HomeController.system_stats()
    
@web_app.route('/data_record', methods=['GET'])
@login_required
def data_record():
    # Kita arahkan ke Controller
    return DeviceController.data_record()

@web_app.route('/add_data_record', methods=['POST'])
@login_required
def add_data_record():
    # Ini route buat SAVE data pas tombol simpan ditekan
    return DeviceController.add_data_record()

@web_app.route('/view_device/<device_id>', methods=['GET'])
@login_required
def view_device(device_id):
    return DeviceController.view_device(device_id)

@web_app.route('/edit_device/<device_id>', methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    return DeviceController.edit_device(device_id)

@web_app.route('/delete_device/<device_id>', methods=['POST'])
@login_required
def delete_device(device_id):
    return DeviceController.delete_device(device_id)

@web_app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return SettingsController.settings()

@web_app.route('/settings/add_endpoint', methods=['POST'])
@login_required
def add_endpoint():
    return SettingsController.add_endpoint()

@web_app.route('/settings/delete_endpoint/<id>', methods=['GET'])
@login_required
def delete_endpoint(id):
    return SettingsController.delete_endpoint(id)

@web_app.route('/settings/toggle_endpoint/<id>', methods=['GET'])
@login_required
def toggle_endpoint(id):
    return SettingsController.toggle_endpoint(id)

@web_app.route('/settings/test_connection', methods=['POST'])
@login_required
def test_connection():
    return SettingsController.test_connection()

# --- USER MANAGEMENT ---
@web_app.route('/users', methods=['GET'])
@login_required
def users():
    return UserController.index()

@web_app.route('/users/add', methods=['POST'])
@login_required
def add_user():
    return UserController.add_user()

@web_app.route('/users/edit/<user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    return UserController.edit_user(user_id)

@web_app.route('/users/delete/<user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    return UserController.delete_user(user_id)

@web_app.route('/profile', methods=['GET'])
@login_required
def profile():
    return UserController.profile()

@web_app.route('/users/change_password', methods=['POST'])
@login_required
def change_password():
    return UserController.change_password()