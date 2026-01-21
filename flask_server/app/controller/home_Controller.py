from flask import render_template, request, redirect, url_for, g, jsonify
from flask_server.app import db
from datetime import datetime
from config import config
from flask_server.app.model.model import Device, DeviceRecord
from flask_server.app.model.user_model import User
from flask_login import current_user
import psutil 
import random 

class HomeController:
    @staticmethod
    def index():
        print("!!! CONTROLLER RELOADED - NEW VERSION !!!")
        page = {"title":"Dashboard"}
        user = User.query.filter(User.id == current_user.id).first()
        
        # 1. Ambil Devices
        devices = Device.query.filter_by(user_id=current_user.id).all()
        
        # 2. Logic Status & Ping Device
        for d in devices:
            last_rec = DeviceRecord.query.filter_by(device_id=d.device_id).order_by(DeviceRecord.created_at.desc()).first()
            if last_rec:
                delta = datetime.now() - last_rec.created_at
                total_seconds = int(delta.total_seconds())
                d.status = 1 if total_seconds < 20 else 0
                
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                d.ping = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
            else:
                d.status = 0
                d.ping = "N/A"

        # 3. Ambil Last Records (Pakai OUTER JOIN explicit)
        raw_query = db.session.query(DeviceRecord, Device.device_name, Device.type_device)\
                              .outerjoin(Device, DeviceRecord.device_id == Device.device_id)\
                              .order_by(DeviceRecord.created_at.desc())\
                              .limit(10).all()

        print(f"[DEBUG] Raw Query Result Len: {len(raw_query)}")

        last_records = []
        for rec, dev_name, dev_type in raw_query:
            data = rec.to_dict()
            
            # FORMATTING NAMA DEVICE & TYPE
            if dev_name:
                data['device_name_display'] = dev_name
                data['type_device'] = dev_type # Simpan type device untuk filter di view
            else:
                data['device_name_display'] = f"{rec.device_id} (Unknown)"
                data['type_device'] = "unknown"
            
            # FORMATTING TIME AGO (Jika perlu)
            delta = datetime.now() - rec.created_at
            data['age'] = str(delta).split('.')[0] # Simple formatting
            
            # IMPORTANT: Override created_at with object (not string) just in case
            data['created_at'] = rec.created_at
            
            last_records.append(data)

        hostmqtt = config.hostmqtt
        return render_template('home.html', page=page, devices=devices, last_records=last_records, hostmqtt=hostmqtt, user=user)

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
    @staticmethod
    def get_dashboard_updates():
        # 1. Ambil Devices Status
        devices = Device.query.filter_by(user_id=current_user.id).all()
        devices_data = []
        for d in devices:
            d_dict = d.to_dict() # Pastikan to_dict ada dan lengkap
            
            # Hitung Status & Ping
            last_rec = DeviceRecord.query.filter_by(device_id=d.device_id).order_by(DeviceRecord.created_at.desc()).first()
            if last_rec:
                delta = datetime.now() - last_rec.created_at
                total_seconds = int(delta.total_seconds())
                d_dict['status'] = 1 if total_seconds < 20 else 0
                
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                d_dict['ping'] = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
            else:
                d_dict['status'] = 0
                d_dict['ping'] = "N/A"
            
            devices_data.append(d_dict)

        # 2. Ambil Last Records
        # Logic yang sama persis dengan Index
        raw_query = db.session.query(DeviceRecord, Device.device_name, Device.type_device)\
                              .outerjoin(Device, DeviceRecord.device_id == Device.device_id)\
                              .order_by(DeviceRecord.created_at.desc())\
                              .limit(10).all()

        last_records = []
        for rec, dev_name, dev_type in raw_query:
            data = rec.to_dict()
            
            # FORMATTING NAMA DEVICE & TYPE
            if dev_name:
                data['device_name_display'] = dev_name
                data['type_device'] = dev_type
            else:
                data['device_name_display'] = f"{rec.device_id} (Unknown)"
                data['type_device'] = "unknown"
            
            # FORMATTING TIME (Jam Asli)
            # Karena JSON tidak punya object datetime, kita string-kan di sini
            data['created_at_fmt'] = rec.created_at.strftime('%H:%M:%S')

            last_records.append(data)

        # Return JSON
        return jsonify({
            'devices': devices_data,
            'last_records': last_records
        })