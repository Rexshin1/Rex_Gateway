from flask import render_template,jsonify, request, redirect, url_for,g
from flask_server.app import db
from config import config
from flask_server.app.model.model import NetworkDevice
from flask_server.app.model.user_model import User
from flask_login import current_user
from core.networking import Networking
import json

class DeviceNetwork:
    @staticmethod
    def list_network():
        data = NetworkDevice.query.all()
        page = {"title": "List Network Device"}
        user = User.query.filter(User.id==current_user.id).first()

        return render_template('network_device.html',page=page,user=user,data=data)
    
    @staticmethod
    def add_network():
        if request.method == 'POST':
            device_id = request.form.get('device_id')
            parent_id = request.form.get('parent_id')
            device_name = request.form.get('device_name')
            type = request.form.get('type')

            if not device_id or not parent_id : #Add validation
                data = {
                    "code": 400,
                    "message": "Nama device dan device ID harus diisi"
                }
                return jsonify(data), 400 #Return a suitable error code like 400 Bad Request

            try:
                new_device = NetworkDevice(device_name=device_name, device_id=device_id, parent_id=parent_id, type=type)
                db.session.add(new_device)
                db.session.commit()
                data = {
                    "code": 200,
                    "message": "Device berhasil ditambahkan" # Clearer success message
                }

                return jsonify(data), 201 # 201 Created is a more appropriate status code
            except Exception as e:
                db.session.rollback()  # Rollback the transaction in case of error
                data = {
                    "code": 500, # 500 for server error
                    "message": f"Gagal menyimpan: {str(e)}"  # Include the actual error for debugging
                }
                return jsonify(data), 500
            

    @staticmethod     
    def update_network():
        if request.method == 'POST':
            device_id = request.form.get('device_id')
            device_name = request.form.get('device_name')
            parent_id = request.form.get('parent_id')
            device_name = request.form.get('device_name')
            type = request.form.get('type')

    @staticmethod
    def delete_network():
        if request.method == 'POST':
            device_id = request.form.get('device_id')
            

    @staticmethod
    def scan_network():
         if request.method == 'POST':
            start_ip = request.json['start_ip']
            end_ip = request.json['end_ip']

            network = Networking()
            list_network = network.scan_network(start_ip, end_ip, threads=10)
            return jsonify(list_network)