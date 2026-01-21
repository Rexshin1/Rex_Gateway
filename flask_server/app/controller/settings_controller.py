from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from config import config
from flask_server.app.model.user_model import User
from flask_server.app.model.model import EndpointConfig
from flask_server.app import db
import os
import re
import json

class SettingsController:
    
    @staticmethod
    def settings():
        # Handle "Default" Config Saving (Lite Version)
        if request.method == 'POST' and 'host_api' in request.form:
            host_api = request.form.get('host_api')
            token_api = request.form.get('token_api')
            
            if not host_api:
                flash("Host API cannot be empty", "danger")
                return redirect(url_for('app.settings'))

            # Update Runtime Config
            config.host_api = host_api
            config.token_api = token_api
            
            # Update .env file
            SettingsController._update_env_file('HOST_API', host_api)
            SettingsController._update_env_file('TOKEN_API', token_api)
            
            flash("General Configuration saved successfully!", "success")
            return redirect(url_for('app.settings'))
            
        page = {"title": "Settings"}
        user = User.query.filter(User.id == current_user.id).first()
        endpoints = EndpointConfig.query.all()
        return render_template('settings.html', page=page, config=config, user=user, endpoints=endpoints)

    # --- ADVANCED ENDPOINTS CRUD ---
    @staticmethod
    def add_endpoint():
        if request.method == 'POST':
            endpoint_id = request.form.get('endpoint_id')
            name = request.form.get('name')
            url = request.form.get('url')
            # Mapping is passed as JSON string from hidden input or constructed
            mapping_str = request.form.get('mapping') 
            headers_str = request.form.get('headers')
            is_active = request.form.get('is_active') == 'on'
            
            # Sync Params
            sync_history = request.form.get('sync_history') == 'on'
            preset_type = request.form.get('preset_type') # e.g. 'power', 'water'

            # Simple Defaults
            if not mapping_str:
                mapping_str = '{}'
            
            if endpoint_id:
                # EDIT MODE
                endpoint = EndpointConfig.query.get(endpoint_id)
                if endpoint:
                    endpoint.name = name
                    endpoint.url = url
                    endpoint.mapping = mapping_str
                    endpoint.headers = headers_str
                    endpoint.is_active = is_active
                    # Update Target Type jika ada input (biasanya hidden input dari modal)
                    if preset_type:
                        endpoint.target_device_type = preset_type
                    
                    msg = "Endpoint Updated!"
                    new_ep = endpoint # For sync logic below
                else:
                    flash("Endpoint not found.", "danger")
                    return redirect(url_for('app.settings'))
            else:
                # CREATE MODE
                new_ep = EndpointConfig(name=name, url=url, mapping=mapping_str, headers=headers_str, is_active=is_active, target_device_type=preset_type)
                db.session.add(new_ep)
                msg = "Endpoint Added!"

            db.session.commit()
            
            # --- SYNC HISTORY LOGIC ---
            if sync_history and preset_type:
                synced_count, sync_msg = SettingsController._sync_endpoint_history(new_ep, preset_type)
                if synced_count > 0:
                    msg += f" {sync_msg}"
                else:
                    msg += " (No historical data found)."
            
            flash(msg, "success")
            return redirect(url_for('app.settings'))
        return redirect(url_for('app.settings'))

    @staticmethod
    def delete_endpoint(id):
        ep = EndpointConfig.query.get(id)
        if ep:
            db.session.delete(ep)
            db.session.commit()
            flash("Endpoint Deleted!", "success")
        return redirect(url_for('app.settings'))
        
    @staticmethod
    def toggle_endpoint(id):
        ep = EndpointConfig.query.get(id)
        if ep:
            new_state = not ep.is_active
            ep.is_active = new_state
            db.session.commit()

            if new_state: # Turned ON
                preset_type = ep.target_device_type if ep.target_device_type else 'all'
                synced_count, sync_msg = SettingsController._sync_endpoint_history(ep, preset_type)
                flash(f"Endpoint {ep.name} ACTIVATED. {sync_msg}", "success")
            else:
                flash(f"Endpoint {ep.name} DEACTIVATED.", "warning")

        return redirect(url_for('app.settings'))

    @staticmethod
    def _sync_endpoint_history(endpoint, preset_type):
        from flask_server.app.model.model import DeviceRecord
        from core.send_server import CloudSender
        
        # Define types to sync
        types_to_sync = []
        if preset_type == 'all':
            types_to_sync = ['power', 'water', 'gas', 'smoke', 'fire', 'weather', 'lux', 'humidity', 'temperature']
        else:
            types_to_sync = [preset_type]
        
        total_synced = 0
        
        # Suffix Map for Smart Routing
        suffix_map = {
            'power': '/add_power', 'water': '/add_water', 'gas': '/add_gas',
            'smoke': '/add_smoke', 'fire': '/add_fire', 'weather': '/add_weather',
            'lux': '/add_lux', 
            'humidity': '/add_humidity_temp', 
            'temperature': '/add_humidity_temp'
        }

        for p_type in types_to_sync:
            # Re-use logic from DeviceController to fetch data
            query = DeviceRecord.query
            if p_type == 'power': query = query.filter(DeviceRecord.power.isnot(None))
            elif p_type == 'water': query = query.filter(DeviceRecord.water.isnot(None))
            elif p_type == 'gas': query = query.filter((DeviceRecord.gas.isnot(None)) | (DeviceRecord.gas_ppm.isnot(None)))
            elif p_type == 'smoke': query = query.filter(DeviceRecord.smoke.isnot(None))
            elif p_type == 'fire': query = query.filter(DeviceRecord.fire.isnot(None))
            elif p_type == 'weather': query = query.filter(DeviceRecord.weather.isnot(None))
            elif p_type == 'lux': query = query.filter(DeviceRecord.lux.isnot(None))
            elif p_type == 'humidity': query = query.filter(DeviceRecord.humidity.isnot(None))
            elif p_type == 'temperature': query = query.filter(DeviceRecord.temperature.isnot(None))
            
            records = query.all()
            if records:
                data_list = [r.to_dict() for r in records]
                
                # SMART ROUTING: Create Temp Endpoint with Specific Suffix
                temp_url = endpoint.url
                suffix = suffix_map.get(p_type, "")
                
                if suffix and suffix not in temp_url:
                        if temp_url.endswith('/'):
                            temp_url += suffix[1:] 
                        else:
                            temp_url += suffix
                
                class TempEP:
                    def __init__(self, url, mapping, name):
                        self.url = url
                        self.mapping = mapping
                        self.name = name
                
                target_ep = TempEP(temp_url, endpoint.mapping, endpoint.name)

                # Send to specific endpoint
                success, s_msg, code = CloudSender.send_bulk_to_endpoint(data_list, target_ep)
                if success:
                    total_synced += len(data_list)
        
        if total_synced > 0:
            return total_synced, f"Backfilled {total_synced} historical records."
        else:
            return 0, "No historical data to sync."

    @staticmethod
    def _update_env_file(key, value):
        env_path = os.path.join(os.getcwd(), '.env')
        if not os.path.exists(env_path):
            return
            
        try:
            with open(env_path, 'r') as f:
                lines = f.readlines()
                
            new_lines = []
            key_found = False
            
            for line in lines:
                if line.strip().startswith(f"{key}=") or line.strip().startswith(f"{key} ="):
                    new_lines.append(f"{key}={value}\n")
                    key_found = True
                else:
                    new_lines.append(line)
            
            if not key_found:
                new_lines.append(f"\n{key}={value}\n")
                
            with open(env_path, 'w') as f:
                f.writelines(new_lines)
                
        except Exception as e:
            print(f"Error updating .env: {e}")
    @staticmethod
    def test_connection():
        # 1. Get Params
        url = request.form.get('url')
        headers_str = request.form.get('headers')
        mapping_str = request.form.get('mapping')
        
        if not url:
            return jsonify({"status": 400, "message": "URL is required"})

        # 2. Simulate Payload
        simulated_data = {
            "device_id": "TEST_GATEWAY_001",
            "power": 100.5,
            "voltage": 220,
            "current": 0.45,
            "energy": 12.3,
            "frequency": 50,
            "temperature": 25.5,
            "humidity": 60,
            "lux": 1500,
            "gas": 12,
            "smoke": 0,
            "created_at": "2025-01-01T12:00:00"
        }
        
        # 3. Reuse CloudSender Logic (Simulated)
        # We need to manually invoke the mapping logic here to show the user what WOULD be sent.
        final_payload = simulated_data.copy()
        
        # ... Apply Mapping Logic (Simplified Duplication for Safety/Speed) ...
        try:
            if mapping_str and mapping_str != '{}':
                mapping = json.loads(mapping_str)
                new_payload = {}
                for target_key, source_key in mapping.items():
                    if source_key in simulated_data:
                        new_payload[target_key] = simulated_data[source_key]
                    elif source_key == "FULL_PAYLOAD":
                        new_payload[target_key] = simulated_data
                if new_payload:
                    final_payload = new_payload
        except Exception as e:
            return jsonify({"status": 500, "message": f"Mapping Error: {str(e)}"})
            
        # 4. Prepare Request
        try:
            req_headers = {'Content-Type': 'application/json'}
            if headers_str:
                try:
                    custom_headers = json.loads(headers_str)
                    req_headers.update(custom_headers)
                except:
                   pass # Ignore bad headers for valid test
                   
            # Serialization helper
            def json_serial(obj):
                if hasattr(obj, 'isoformat'): return obj.isoformat()
                return str(obj)
                
            json_payload = json.dumps(final_payload, default=json_serial)
            
            # 5. SEND (Short Timeout)
            import requests
            response = requests.post(url, data=json_payload, headers=req_headers, timeout=5)
            
            return jsonify({
                "status": response.status_code,
                "message": response.text[:200], # Trucate for UI
                "sent_payload": final_payload
            })
            
        except Exception as e:
            return jsonify({"status": 0, "message": f"Connection Failed: {str(e)}"})
