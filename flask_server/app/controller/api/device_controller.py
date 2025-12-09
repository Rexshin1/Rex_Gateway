from flask import jsonify, render_template, request, redirect, url_for
from flask_server.app import db
from flask_server.app.model.model import Device, DeviceRecord
from flask_server.app.model.user_model import User
from flask_login import current_user
import json



class DeviceController:
    @staticmethod
    def list_devices():
        devices = Device.query.all()  # Query all users from the database
        # Serialize the User objects using the to_dict method
        device_list = [device.to_dict() for device in devices]  # Convert each user to a dict
        return jsonify(device_list)  # Return the list as a JSON response

    @staticmethod
    def get_data_records():
        from flask_server.app.model.model import DeviceRecord
        records = DeviceRecord.query.order_by(DeviceRecord.created_at.desc()).limit(100).all()
        record_list = [record.to_dict() for record in records]
        return jsonify(record_list)

    

    @staticmethod
    def add_device():
        if request.method == 'POST':
            device_id = request.json.get('device_id')
            device_name = request.json.get('device_name') # Use .get to handle missing keys safely
            type_device = request.json.get('type_device')
            status = request.json.get('status')
            # Add more fields as needed
            # Auto-Generate ID if not provided
            if not device_id:
                try:
                    # Fetch all devices to find the latest ID_XXX
                    all_devices = Device.query.all()
                    max_id = 0
                    for d in all_devices:
                        if d.device_id.startswith("ID_"):
                            try:
                                num = int(d.device_id.split("_")[1])
                                if num > max_id:
                                    max_id = num
                            except (IndexError, ValueError):
                                pass
                    
                    # Generate next ID
                    device_id = f"ID_{max_id + 1:03d}"
                except Exception as e:
                    return jsonify({"code": 500, "message": f"Gagal generate ID: {str(e)}"}), 500

            if not device_name:
                data = {
                    "code": 400,
                    "message": "Nama device harus diisi"
                }
                return jsonify(data), 400

            try:
                new_device = Device(device_name=device_name, device_id=device_id, type_device=type_device, status=status)
                db.session.add(new_device)
                
                # Create initial data record with default values based on type
                # Set irrelevant fields to None so they appear as "-" in the UI
                initial_power = 220.0 if type_device == 'power' else None
                initial_voltage = 220.0 if type_device == 'power' else None
                initial_current = 1.0 if type_device == 'power' else None
                initial_frequency = 50.0 if type_device == 'power' else None
                initial_energy = 0.5 if type_device == 'power' else None
                initial_humidity = 60.0 if type_device == 'humidity' else None
                initial_temperature = 25.0 if type_device == 'temperature' else None
                initial_weather = "Cerah" if type_device == 'weather' else None
                initial_lux = 300.0 if type_device == 'lux' else None
                initial_water = 0.0 if type_device == 'water' else None
                initial_water_level = 0.0 if type_device == 'water' else None
                initial_total_volume = 0.0 if type_device == 'water' else None
                
                new_record = DeviceRecord(
                    device_id=device_id,
                    power=initial_power,
                    voltage=initial_voltage,
                    current=initial_current,
                    frequency=initial_frequency,
                    energy=initial_energy,
                    humidity=initial_humidity,
                    temperature=initial_temperature,
                    weather=initial_weather,
                    fire=0 if type_device == 'fire' else None, # 0 means Safe, None means N/A
                    gas=0.0 if type_device == 'gas' else None,
                    smoke=0.0 if type_device == 'smoke' else None,

                    lux=initial_lux,
                    water=initial_water,
                    water_level=initial_water_level,
                    total_volume=initial_total_volume
                )
                db.session.add(new_record)
                db.session.commit()
                data = {
                    "code": 200,
                    "message": "Device berhasil ditambahkan",
                    "device_id": device_id  # Return the generated ID
                }

                return jsonify(data), 200
            except Exception as e:
                db.session.rollback()
                data = {
                    "code": 500,
                    "message": f"Gagal menyimpan: {str(e)}"
                }
                return jsonify(data), 500



    @staticmethod
    def update_device():
        if request.method == 'POST':
            # Support both JSON and Form data
            data_source = request.json if request.is_json else request.form
            
            device_id = data_source.get('device_id')
            device_name = data_source.get('device_name')
            type_device = data_source.get('type_device')
            status = data_source.get('status')
            
            # Add more fields as needed
            if not device_id or not device_name:
                data ={
                    "code":400,
                    "message":"Nama device dan device ID harus diisi"
                }
                return jsonify(data),400
            try:
                device = Device.query.filter_by(device_id=device_id).first()
                if device:
                    device.device_name = device_name
                    device.type_device = type_device
                    device.status = status
                    db.session.commit()
                    data = {
                        "code":200,
                        "message":"Device berhasil diupdate"
                    }
                    return jsonify(data),200
                else:
                    data = {
                        "code":404,
                        "message":"Device tidak ditemukan"
                    }
                    return jsonify(data),404
            except Exception as e:
                db.session.rollback()
                data = {
                    "code":500,
                    "message":f"Gagal memperbarui: {str(e)}"
                }
                return jsonify(data),500
        
        page = {"title":"Update Device"}
        user = User.query.filter(User.id==current_user.id).first()
        return render_template('update_device.html',page=page,user=user)
    
    @staticmethod
    def delete_device(device_id=None):
        # If device_id is not passed as argument (e.g. from API), try to get from request
        if not device_id:
            if request.method == 'POST':
                if request.is_json:
                    device_id = request.json.get('device_id')
                else:
                    device_id = request.form.get('device_id')
        
        if not device_id:
            data = {
                "code":400,
                "message":"Device ID harus diisi"
            }
            return jsonify(data),400
            
        try:
            # Find the device first
            device = Device.query.filter_by(device_id=device_id).first()
            
            if not device:
                data = {
                    "code": 404,
                    "message": "Device tidak ditemukan"
                }
                return jsonify(data), 404

            # Delete the device object, not the ID string
            db.session.delete(device)
            db.session.commit()
            
            data = {
                "code":200,
                "message":"Device berhasil dihapus"
            }
            return jsonify(data),200
        except Exception as e:
            db.session.rollback()
            data = {
                "code":500,
                "message":f"Gagal menghapus: {str(e)}"
            }
            return jsonify(data),500
        
    
    

    @staticmethod
    def add_data_record():
        """
        Endpoint to add a detailed sensor data record (Power, Env, etc.)
        """
        try:
            data = request.json
            device_id = data.get('device_id')
            
            if not device_id:
                return jsonify({"code": 400, "message": "device_id is required"}), 400

            # Create new record with all potential fields
            new_record = DeviceRecord(
                device_id=device_id,
                power=data.get('power'),
                voltage=data.get('voltage'),
                current=data.get('current'),
                frequency=data.get('frequency'),
                energy=data.get('energy'),
                
                humidity=data.get('humidity'),
                temperature=data.get('temperature'),
                weather=data.get('weather'),
                
                fire=data.get('fire'),
                gas=data.get('gas'),
                smoke=data.get('smoke'),
                
                lux=data.get('lux'),
                water=data.get('water'),
                water_level=data.get('water_level'),
                total_volume=data.get('total_volume')
            )
            
            db.session.add(new_record)
            db.session.commit()
            
            return jsonify({
                "code": 200, 
                "message": "Data Record successfully added",
                "data": new_record.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"code": 500, "message": f"Failed to save record: {str(e)}"}), 500
        