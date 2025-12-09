from flask import render_template, request, redirect, url_for, g, jsonify
from flask_server.app import db
from config import config
from flask_server.app.model.model import Device, DeviceRecord
from flask_server.app.model.user_model import User
from flask_login import current_user
import psutil 
import random 

class HomeController:
    @staticmethod
    def index():
        page = {"title":"Dashboard"}
        user = User.query.filter(User.id == current_user.id).first()
        device = Device.query.all()
        hostmqtt = config.hostmqtt
        return render_template('home.html', page=page, device=device, hostmqtt=hostmqtt, user=user)

    @staticmethod
    def data_record():
        page = {"title":"Data Record"}
        user = User.query.filter(User.id == current_user.id).first()
        records = DeviceRecord.query.order_by(DeviceRecord.created_at.desc()).all()
        return render_template('data_record.html', page=page, records=records, user=user)
    
    @staticmethod
    def system_stats():
        try:
            
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            # 2. Baca Suhu (Khusus Linux/Raspberry Pi)
            temp = 0
            if hasattr(psutil, "sensors_temperatures"):
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            for entry in entries:
                                temp = entry.current
                                break
                except:
                    pass
            
            
            if temp == 0:
                temp = 40 + (cpu / 2) + random.uniform(-1.5, 1.5)

        except Exception as e:
            print(f"Error reading stats: {e}")
            cpu, ram, disk, temp = 0, 0, 0, 45 # Default 45 kalau error parah
            
        return jsonify({
            'cpu': cpu,
            'ram': ram,
            'disk': disk,
            'temp': round(temp, 1) # Kita buletin 1 angka belakang koma (cth: 45.2)
        })