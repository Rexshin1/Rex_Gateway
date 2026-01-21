from flask import jsonify, render_template, request, redirect, url_for
from core.send_server import CloudSender
from flask_server.app import db
from flask_server.app.model.model import Device, DeviceRecord
from flask_server.app.model.user_model import User
from flask_login import current_user
import json


from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError


class DeviceController:
    @staticmethod
    def get_authenticated_user():
        if current_user.is_authenticated:
            return current_user
        
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            if identity:
                # Assuming identity is the email, logic from AuthController
                user = User.query.filter_by(email=identity).first()
                return user
        except (NoAuthorizationError, Exception):
            pass
            
        return None
    @staticmethod
    def list_devices():
        user = DeviceController.get_authenticated_user()
        
        if user:
            devices = Device.query.filter_by(user_id=user.id).all()
        else:
            return jsonify({"message": "Unauthorized"}), 401

        # Serialize the User objects using the to_dict method
        device_list = [device.to_dict() for device in devices]  # Convert each user to a dict
        return jsonify(device_list)  # Return the list as a JSON response

    @staticmethod
    def get_data_records():
        from flask_server.app.model.model import DeviceRecord, Device
        
        user = DeviceController.get_authenticated_user()
        if not user:
            return jsonify([]), 401
        
        # Ambil parameter dari URL (contoh: ?device_id=ID_001&limit=5)
        device_id = request.args.get('device_id')
        limit = request.args.get('limit', default=100, type=int)

        # Join with Device table to ensure ownership
        query = DeviceRecord.query.join(Device, DeviceRecord.device_id == Device.device_id)\
                                  .filter(Device.user_id == user.id)

        # Jika ada parameter device_id, filter datanya (Ownership is already checked by join)
        if device_id:
            query = query.filter(DeviceRecord.device_id == device_id)

        # Ambil data terbaru sesuai limit
        records = query.order_by(DeviceRecord.created_at.desc()).limit(limit).all()

        record_list = []
        for record in records:
            d = record.to_dict()
            if d.get('created_at'):
                d['created_at'] = d['created_at'].isoformat()
            record_list.append(d)
        
        return jsonify(record_list)

    

    @staticmethod
    def add_device():
        if request.method == 'POST':
            user = DeviceController.get_authenticated_user()
            if not user:
                return jsonify({"code": 401, "message": "Unauthorized"}), 401
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
                    
                    # Ensure generated ID is unique for this type (though auto-gen usually implies new unique ID globaly, 
                    # but let's stick to simple auto-increment for now. 
                    # If user manually provides ID, the check below handles it.)
                except Exception as e:
                    return jsonify({"code": 500, "message": f"Gagal generate ID: {str(e)}"}), 500

            if not device_name:
                data = {
                    "code": 400,
                    "message": "Nama device harus diisi"
                }
                return jsonify(data), 400
            
            # Check for existing device with SAME ID AND SAME TYPE
            existing_device = Device.query.filter_by(device_id=device_id, type_device=type_device).first()
            if existing_device:
                 data = {
                    "code": 400,
                    "message": f"Device ID {device_id} untuk tipe {type_device} sudah ada!"
                }
                 return jsonify(data), 400

            try:
                new_device = Device(device_name=device_name, device_id=device_id, type_device=type_device, status=status, user_id=user.id)
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
                # Ensure we only update devices owned by this user
                device = Device.query.filter_by(device_id=device_id, user_id=current_user.id).first()
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
        user = DeviceController.get_authenticated_user()
        if not user:
            return jsonify({"code": 401, "message": "Unauthorized"}), 401
            
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
            # Find the device first, ensuring ownership
            device = Device.query.filter_by(device_id=device_id, user_id=user.id).first()
            
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
    def _process_add_record(data, valid_fields):
        """
        Helper function to process and save a new data record.
        valid_fields: list of fields to extract from data (others are ignored/None)
        """
        try:
            device_id = data.get('device_id')
            if not device_id:
                return jsonify({"code": 400, "message": "device_id is required"}), 400

            # Construct arguments for DeviceRecord based on valid_fields
            record_args = {'device_id': device_id}
            
            # Explicitly mapping fields to ensure safety
            allowed_keys = [
                'power', 'voltage', 'current', 'frequency', 'energy',
                'humidity', 'temperature', 'weather',
                'fire', 'gas', 'smoke',
                'lux', 'water', 'water_level', 'total_volume',
                'gas_ppm', 'gas_voltage', 'distance'
            ]
            
            # Only extract fields that are both in allowed_keys AND valid_fields (if specific)
            # Or if valid_fields is None, take all known keys
            target_keys = valid_fields if valid_fields else allowed_keys

            for key in allowed_keys:
                if key in target_keys:
                    val = data.get(key)
                    # Convert to appropriate type if needed, or let SQLAlchemy handle it (usually safer to cast if possible, but keeping it simple)
                    record_args[key] = val
                else:
                     record_args[key] = None

            new_record = DeviceRecord(**record_args)
            
            db.session.add(new_record)
            db.session.commit()

            # Send to Cloud (Moved to Scheduler every 5 mins)
            # try:
            #     CloudSender.send_data(new_record.to_dict())
            # except Exception as e:
            #     print(f"Cloud sync error: {e}")
            
            return jsonify({
                "code": 200, 
                "message": "Data Record successfully added",
                "data": new_record.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"code": 500, "message": f"Failed to save record: {str(e)}"}), 500

    @staticmethod
    def add_data_record():
        """
        Generic endpoint - Retained for backward compatibility
        """
        return DeviceController._process_add_record(request.json, None)

    @staticmethod
    def add_power():
        return DeviceController._process_add_record(
            request.json, 
            ['power', 'voltage', 'current', 'frequency', 'energy']
        )

    @staticmethod
    def add_lux():
        return DeviceController._process_add_record(
            request.json, 
            ['lux']
        )

    @staticmethod
    def add_gas():
        return DeviceController._process_add_record(
            request.json, 
            ['gas', 'gas_ppm', 'gas_voltage']
        )

    @staticmethod
    def add_smoke():
        return DeviceController._process_add_record(
            request.json, 
            ['smoke']
        )

    @staticmethod
    def add_water():
        return DeviceController._process_add_record(
            request.json, 
            ['water', 'water_level', 'total_volume']
        )
    
    @staticmethod
    def add_fire():
        return DeviceController._process_add_record(
            request.json, 
            ['fire', 'temperature', 'smoke']
        )

    @staticmethod
    def add_weather():
        return DeviceController._process_add_record(
            request.json, 
            ['weather', 'temperature']
        )

    @staticmethod
    def add_humidity_temp():
        return DeviceController._process_add_record(
            request.json, 
            ['humidity', 'temperature']
        )


    @staticmethod
    def _get_sensor_data(device_id, target_type):
        from config import config
        device_id = device_id.strip()
        
        if not current_user.is_authenticated:
             return jsonify([]), 401

        # Check if device exists with specific type AND belongs to user
        device = Device.query.filter_by(device_id=device_id, type_device=target_type, user_id=current_user.id).first()
        if not device:
             return jsonify({
                "code": 404,
                "message": f"Device {device_id} of type {target_type} not found in your account"
             }), 404

        record = DeviceRecord.query.filter_by(device_id=device_id).order_by(DeviceRecord.created_at.desc()).first()
        if not record:
            return jsonify({
                "code": 404,
                "message": f"No data for {device_id}"
            }), 404
        
        payload = {}
        # Common fields
        payload["gw"] = config.device_id
        payload["id"] = record.device_id
        payload["amp"] = record.created_at.strftime('%Y-%m-%d %H:%M:%S')

        if target_type == 'power':
            payload["vt"] = str(record.voltage if record.voltage is not None else 0)
            payload["pw"] = str(record.power if record.power is not None else 0)
            
        elif target_type == 'lux':
            payload["lux"] = str(record.lux if record.lux is not None else 0)
            
        elif target_type == 'gas':
            payload["ppm"] = str(record.gas_ppm if record.gas_ppm is not None else 0)
            payload["vol"] = str(record.gas_voltage if record.gas_voltage is not None else 0)

        elif target_type == 'smoke':
             payload["ppm"] = str(record.smoke if record.smoke is not None else 0)
            
        elif target_type == 'water':
            payload["level"] = str(record.water_level if record.water_level is not None else 0)
            payload["vol"] = str(record.total_volume if record.total_volume is not None else 0)

        elif target_type == 'fire':
            payload["status"] = str(record.fire if record.fire is not None else 0)
            
        elif target_type == 'weather':
             payload["weather"] = str(record.weather if record.weather else "-")
             payload["temp"] = str(record.temperature if record.temperature is not None else 0)

        elif target_type == 'humidity-temp': 
             payload["hum"] = str(record.humidity if record.humidity is not None else 0)
             payload["temp"] = str(record.temperature if record.temperature is not None else 0)
        
        return jsonify(payload), 200

    @staticmethod
    def get_power_json(device_id):
        return DeviceController._get_sensor_data(device_id, 'power')

    @staticmethod
    def get_lux_json(device_id):
        return DeviceController._get_sensor_data(device_id, 'lux')

    @staticmethod
    def get_gas_json(device_id):
        return DeviceController._get_sensor_data(device_id, 'gas')

    @staticmethod
    def get_smoke_json(device_id):
        return DeviceController._get_sensor_data(device_id, 'smoke')

    @staticmethod
    def get_water_json(device_id):
        return DeviceController._get_sensor_data(device_id, 'water')

    @staticmethod
    def get_fire_json(device_id):
        return DeviceController._get_sensor_data(device_id, 'fire')

    @staticmethod
    def get_weather_json(device_id):
        return DeviceController._get_sensor_data(device_id, 'weather')

    @staticmethod
    def get_humidity_temp_json(device_id):
        return DeviceController._get_sensor_data(device_id, 'humidity-temp')

    @staticmethod
    def sync_data_records(type_arg=None):
        """
        Manually trigger bulk sync of all local data to cloud.
        Supports filtering by type via query param ?type=power OR function argument
        """
        target_type = type_arg if type_arg else request.args.get('type') # e.g. power, water
        
        try:
            query = DeviceRecord.query
            
            # Simple filtering logic based on columns being not null
            if target_type == 'power':
                query = query.filter(DeviceRecord.power.isnot(None))
            elif target_type == 'water':
                query = query.filter(DeviceRecord.water.isnot(None))
            elif target_type == 'gas':
                query = query.filter((DeviceRecord.gas.isnot(None)) | (DeviceRecord.gas_ppm.isnot(None)))
            elif target_type == 'smoke':
                query = query.filter(DeviceRecord.smoke.isnot(None))
            elif target_type == 'fire':
                query = query.filter(DeviceRecord.fire.isnot(None))
            elif target_type == 'weather':
                query = query.filter(DeviceRecord.weather.isnot(None))
            elif target_type == 'lux':
                query = query.filter(DeviceRecord.lux.isnot(None))
            elif target_type == 'humidity_temp':
                query = query.filter((DeviceRecord.humidity.isnot(None)) | (DeviceRecord.temperature.isnot(None)))
            
            # Get all matching records
            records = query.all()
            total = len(records)
            success_count = 0

            print(f"[BULK SYNC] Starting sync for {total} records (Type: {target_type})...")

            # Define fields to keep for each type
            field_map = {
                'power': ['power', 'voltage', 'current', 'frequency', 'energy'],
                'lux': ['lux'],
                'gas': ['gas', 'gas_ppm', 'gas_voltage'],
                'smoke': ['smoke'],
                'water': ['water', 'water_level', 'total_volume'],
                'fire': ['fire', 'temperature', 'smoke'],
                'weather': ['weather', 'temperature'],
                'humidity_temp': ['humidity', 'temperature']
            }
            
            allowed_fields = field_map.get(target_type, [])
            # Always include identification fields
            base_fields = ['device_id', 'created_at']

            data_list = []

            for record in records:
                # Get full dict
                full_data = record.to_dict()
                
                # If we have specific fields defined, filter the dict
                if allowed_fields:
                    filtered_data = {k: full_data[k] for k in base_fields if k in full_data}
                    for field in allowed_fields:
                        if field in full_data:
                            filtered_data[field] = full_data[field]
                    data_list.append(filtered_data)
                else:
                    # If type not found or generic, send everything (fallback)
                    data_list.append(full_data)

                success_count += 1
            
            # Send bulk data using CloudSender
            if data_list:
                # If triggered manually via sync endpoint, we send it to cloud
                success, msg, status_code = CloudSender.send_bulk_data(data_list, target_type)
                
                if not success:
                    return jsonify({
                        "code": status_code if status_code != 0 else 500,
                        "message": f"Cloud Sync Failed: {msg}",
                        "synced_count": 0,
                        "total_records": len(records),
                        "type_filter": target_type
                    }), status_code if status_code != 0 and status_code < 600 else 500
                
            return jsonify({
                "code": 200, 
                "message": "Bulk sync completed successfully", 
                "synced_count": len(data_list),
                "total_records": len(records),
                "type_filter": target_type
            })

        except Exception as e:
            return jsonify({
                "code": 500,
                "message": f"Bulk sync failed: {str(e)}"
            }), 500

    @staticmethod
    def pull_data_records(target_type='all'):
        try:
            query = DeviceRecord.query
            
            # Simple Map for filters
            field_map = {
                'power': ['power', 'voltage', 'current', 'frequency', 'energy'],
                'water': ['water_level', 'total_volume'],
                'gas': ['gas', 'gas_ppm', 'gas_voltage'],
                'smoke': ['smoke', 'fire', 'temperature'],
                'fire': ['fire', 'smoke', 'temperature'],
                'weather': ['weather', 'temperature'],
                'lux': ['lux'],
                'humidity_temp': ['humidity', 'temperature']
            }

            base_fields = ['device_id', 'created_at']
            allowed_fields = field_map.get(target_type, [])

            if not current_user.is_authenticated:
                return jsonify([])

            # Filter by ownership
            query = query.join(Device, DeviceRecord.device_id == Device.device_id)\
                         .filter(Device.user_id == current_user.id)

            if target_type in field_map:
                 # Check if the MAIN field is not None
                 main_field = getattr(DeviceRecord, target_type if target_type != 'humidity_temp' else 'humidity', None)
                 if main_field:
                     query = query.filter(main_field.isnot(None))

            records = query.all()
            
            data_list = []
            for record in records:
                full_data = record.to_dict()
                if allowed_fields:
                    filtered_data = {k: full_data[k] for k in base_fields if k in full_data}
                    for field in allowed_fields:
                        if field in full_data:
                            filtered_data[field] = full_data[field]
                    data_list.append(filtered_data)
                else:
                    data_list.append(full_data)

            return jsonify(data_list)
            
        except Exception as e:
            return jsonify({"code": 500, "message": str(e)}), 500




        