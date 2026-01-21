from flask import jsonify, render_template, request, redirect, url_for, flash
from flask_server.app import db
from flask_server.app.model.model import Device, DeviceRecord
from flask_server.app.model.user_model import User
from flask_login import current_user

class DeviceController:
    # --- BAGIAN MANAJEMEN DEVICE (CRUD) ---
    
    @staticmethod
    def list_devices():
        if current_user.is_authenticated:
            data = Device.query.filter_by(user_id=current_user.id).all()
        else:
            data = []
        page = {"title":"Dashboard"}
        user = User.query.filter(User.id==current_user.id).first()
        return render_template('device_list.html',page=page,user=user,data=data)

    @staticmethod
    def add_device():
        if request.method == 'POST':
            device_id = request.form.get('device_id')
            device_name = request.form.get('device_name') 
            type_device = request.form.get('type_device')
            status = request.form.get('status')
            
            if not device_id or not device_name : 
                flash('Nama device dan device ID harus diisi', 'danger')
                return redirect(url_for('app.add_device'))

            # Check for existing device with SAME ID AND SAME TYPE
            existing = Device.query.filter_by(device_id=device_id, type_device=type_device).first()
            if existing:
                flash(f'Device ID {device_id} untuk tipe {type_device} sudah ada!', 'danger')
                return redirect(url_for('app.add_device'))

            try:
                new_device = Device(device_name=device_name, device_id=device_id, type_device=type_device, status=status, user_id=current_user.id)
                db.session.add(new_device)

                # Create initial data record with default values based on type
                # Set irrelevant fields to None so they appear as "-" in the UI
                initial_power = 220.0 if type_device == 'power' else None
                initial_voltage = 220.0 if type_device == 'power' else None
                initial_current = 1.0 if type_device == 'power' else None
                initial_frequency = 50.0 if type_device == 'power' else None
                initial_energy = 0.5 if type_device == 'power' else None

                # Consolidated humidity-temp type
                initial_humidity = 60.0 if type_device == 'humidity-temp' else None
                initial_temperature = 25.0 if type_device == 'humidity-temp' else None
                
                initial_weather = "Cerah" if type_device == 'weather' else None
                initial_lux = 300.0 if type_device == 'lux' else None
                initial_water = 0.0 if type_device == 'water' else None
                initial_water_level = 0.0 if type_device == 'water' else None
                initial_total_volume = 0.0 if type_device == 'water' else None
                initial_distance = 10.0 if type_device == 'ultrasonic' else None

                initial_gas_ppm = 150.0 if type_device == 'gas' else None
                initial_gas_voltage = 1.5 if type_device == 'gas' else None

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
                    fire=0 if type_device == 'fire' else None,
                    gas=0.0 if type_device == 'gas' else None,
                    gas_ppm=initial_gas_ppm,
                    gas_voltage=initial_gas_voltage,
                    smoke=0.0 if type_device == 'smoke' else None,

                    lux=initial_lux,
                    water=initial_water,
                    water_level=initial_water_level,
                    total_volume=initial_total_volume,
                    distance=initial_distance
                )
                db.session.add(new_record)
                db.session.commit()
                flash('Device berhasil ditambahkan', 'success')
                return redirect(url_for('app.list_device'))
            except Exception as e:
                db.session.rollback()  
                flash(f'Gagal menyimpan: {str(e)}', 'danger')
                return redirect(url_for('app.add_device'))

        # Handle GET request:
        page = {"title":"Add Device"}
        user = User.query.filter(User.id==current_user.id).first() 
        return render_template('add_device.html', page=page, user=user)

    @staticmethod
    def view_device(device_id):
        device = Device.query.filter_by(device_id=device_id, user_id=current_user.id).first()
        if not device:
            flash('Device tidak ditemukan', 'danger')
            return redirect(url_for('app.list_device'))
        
        page = {"title": "View Device"}
        user = User.query.filter(User.id==current_user.id).first()
        return render_template('view_device.html', page=page, user=user, device=device)

    @staticmethod
    def edit_device(device_id):
        device = Device.query.filter_by(device_id=device_id, user_id=current_user.id).first()
        if not device:
            flash('Device tidak ditemukan', 'danger')
            return redirect(url_for('app.list_device'))
        
        if request.method == 'POST':
            device.device_name = request.form.get('device_name')
            device.type_device = request.form.get('type_device')
            device.status = request.form.get('status')
            
            try:
                db.session.commit()
                flash('Device berhasil diupdate', 'success')
                return redirect(url_for('app.list_device'))
            except Exception as e:
                db.session.rollback()
                flash(f'Gagal memperbarui: {str(e)}', 'danger')
        
        page = {"title": "Edit Device"}
        user = User.query.filter(User.id==current_user.id).first()
        return render_template('edit_device.html', page=page, user=user, device=device)

    @staticmethod
    def update_device():
        if request.method == 'POST':
            device_id = request.form.get('device_id')
            device_name = request.form.get('device_name')
            type_device = request.form.get('type_device')
            status = request.form.get('status')
            
            if not device_id or not device_name:
                data ={
                    "code":400,
                    "message":"Nama device dan device ID harus diisi"
                }
                return jsonify(data),400
            try:
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
    def delete_device(device_id):
        try:
            device_to_delete = Device.query.filter_by(device_id=device_id, user_id=current_user.id).first()
            if device_to_delete:
                # Juga hapus semua data record milik device ini biar database bersih
                DeviceRecord.query.filter_by(device_id=device_id).delete()
                
                db.session.delete(device_to_delete)
                db.session.commit()
                flash('Device dan semua data recordnya berhasil dihapus', 'success')
            else:
                flash('Device tidak ditemukan', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal menghapus: {str(e)}', 'danger')
        
        return redirect(url_for('app.list_device'))

    # --- BAGIAN DATA RECORDS (BARU) ---
    
    @staticmethod
    def data_record():
        # Ambil semua data record milik user
        page = {"title": "Data Record"}
        user = User.query.filter(User.id == current_user.id).first()
        records = []
        if current_user.is_authenticated:
            # Join with Device table to ensure ownership
            records = DeviceRecord.query.join(Device, DeviceRecord.device_id == Device.device_id)\
                                      .filter(Device.user_id == current_user.id)\
                                      .order_by(DeviceRecord.created_at.desc()).all()
        return render_template('data_record.html', page=page, user=user, records=records)

    @staticmethod
    def add_data_record():
        # Fungsi ini dipanggil saat tombol 'Simpan' di modal Data Record ditekan
        if request.method == 'POST':
            device_id = request.form.get('device_id')
            record_value = request.form.get('record_value')
            type_device = request.form.get('type_device')
            
            try:
                # Simpan data baru ke tabel DeviceRecord (bukan Device)
                new_record = DeviceRecord(
                    device_id=device_id,
                    record_value=float(record_value),
                    type_device=type_device
                )
                db.session.add(new_record)
                db.session.commit()
                flash('Data Record berhasil ditambahkan!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Gagal menyimpan: {str(e)}', 'danger')
            
            return redirect(url_for('app.data_record'))