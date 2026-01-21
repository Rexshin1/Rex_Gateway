from flask_server.app import db
from datetime import datetime

class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    type_device = db.Column(db.String(20), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    mac_address = db.Column(db.String(50), nullable=True, unique=True) # New: For auto-provisioning
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Linked to User
    user = db.relationship('User', backref=db.backref('devices', cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Device {self.device_id} ({self.mac_address}) - {self.type_device}>"
    def to_dict(self):
        """Convert the Device object to a dictionary for JSON response."""
        return {
            'id': self.id,
            'device_name': self.device_name,
            'device_id': self.device_id,
            'type_device': self.type_device,
            'status': self.status
        }
    

class DeviceRecord(db.Model):
    __tablename__ = 'device_records'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), nullable=False)
    
    # Sensor Data Columns
    power = db.Column(db.Float, nullable=True)
    voltage = db.Column(db.Float, nullable=True)
    current = db.Column(db.Float, nullable=True)
    frequency = db.Column(db.Float, nullable=True)
    energy = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    weather = db.Column(db.String(50), nullable=True)
    fire = db.Column(db.Integer, nullable=True) # 0 or 1
    gas = db.Column(db.Float, nullable=True)
    gas_ppm = db.Column(db.Float, nullable=True)
    gas_voltage = db.Column(db.Float, nullable=True)
    smoke = db.Column(db.Float, nullable=True)
    lux = db.Column(db.Float, nullable=True)
    water = db.Column(db.Float, nullable=True)
    water_level = db.Column(db.Float, nullable=True)
    total_volume = db.Column(db.Float, nullable=True)
    distance = db.Column(db.Float, nullable=True) # For Ultrasonic
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<DeviceRecord {self.device_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'power': self.power,
            'voltage': self.voltage,
            'current': self.current,
            'frequency': self.frequency,
            'energy': self.energy,
            'humidity': self.humidity,
            'temperature': self.temperature,
            'weather': self.weather,
            'fire': self.fire,
            'gas': self.gas,
            'gas_ppm': self.gas_ppm,
            'gas_voltage': self.gas_voltage,
            'smoke': self.smoke,
            'lux': self.lux,
            'water': self.water,
            'water_level': self.water_level,
            'total_volume': self.total_volume,
            'distance': self.distance,
            'created_at': self.created_at
        }
    
class EndpointConfig(db.Model):
    __tablename__ = 'endpoint_configs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), default='POST')
    headers = db.Column(db.Text, nullable=True) # JSON string
    mapping = db.Column(db.Text, nullable=True) # JSON string, e.g. {"gw_id": "Gateway ID"}
    is_active = db.Column(db.Boolean, default=True)
    target_device_type = db.Column(db.String(50), nullable=True) # Filter by device type, e.g. 'power'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'method': self.method,
            'headers': self.headers,
            'mapping': self.mapping,
            'is_active': self.is_active,
            'target_device_type': self.target_device_type
        }

class NetworkDevice(db.Model):
    __tablename__ = 'network_devices'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.String(100), nullable=True)
    device_id = db.Column(db.String(100), nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(50), nullable=True)
    status = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Device {self.device_id} - ${self.device_name}>"
    
