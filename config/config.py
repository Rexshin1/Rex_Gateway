import os
from dotenv import load_dotenv

load_dotenv()

device_id = os.getenv('GATEWAY_ID')
port_app = int(os.getenv('PORT_WEB', 5001))
hostmqtt = os.getenv('MQTT_HOST')
port_mqtt = int(os.getenv('MQTT_PORT', 1883))
user_mqtt = os.getenv('MQTT_USERNAME')
pass_mqtt = os.getenv('MQTT_PASSWORD')
secret_key = os.getenv('SECRET_KEY')
database = os.getenv('DATABASE', 'app.db')
token_api = os.getenv('TOKEN_API')
host_api = os.getenv('HOST_API')

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, database)
SQLALCHEMY_TRACK_MODIFICATIONS = True