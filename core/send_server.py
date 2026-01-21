import requests
import json
from config import config
from flask import current_app
from flask_server.app.model.model import EndpointConfig

class CloudSender:
    
    @staticmethod
    def send_data(data):
        # 1. Fetch Advanced Endpoints safely
        advanced_endpoints = []
        total_endpoints_count = -1 # Initialize to -1 to differentiate "Zero Endpoints" vs "Query Failed"
        try:
             # We assume app context is already pushed by caller (main.py or controller)
             if current_app:
                advanced_endpoints = EndpointConfig.query.filter_by(is_active=True).all()
                total_endpoints_count = EndpointConfig.query.count()
        except RuntimeError as e:
            print(f"[CLOUD] Context Error: {e}")
        except Exception as e:
            print(f"[CLOUD] unexpected Error in send_data: {e}")

        # 2. SMART DECISION:
        # If DB Error (count is still -1), ABORT. Do not fallback to Legacy as it might leak data.
        if total_endpoints_count == -1:
            # print("[CLOUD] DB Query Failed. Aborting sync to prevent leak.")
            return

        # If user has Created Endpoints (total > 0) but NONE are active, STOP completely.
        if total_endpoints_count > 0 and not advanced_endpoints:
             # print("[CLOUD] All custom endpoints disabled. Transmission stopped.")
             return

        # Only use Legacy (.env) if Factory State (No endpoints defined)
        if total_endpoints_count == 0:
            CloudSender._send_legacy(data)
            return

        # 3. Iterate and Send to each Custom Endpoint
        for ep in advanced_endpoints:
            CloudSender._send_to_custom_endpoint(data, ep)

    @staticmethod
    def _send_to_custom_endpoint(raw_data, ep_config):
        try:
            # STOP LOOP: If target is localhost:5001 (Self), abort or switch to 5002
            if ":5001" in ep_config.url:
                print(f"[CLOUD-MULTI] ⚠️ SKIPPING {ep_config.name}: Cannot send to self (Port 5001).")
                return

            # Apply Mapping
            payload = raw_data.copy()
            if ep_config.mapping:
                try:
                    mapping = json.loads(ep_config.mapping)
                    new_payload = {}
                    if mapping:
                        for target_key, source_key in mapping.items():
                            if source_key in raw_data:
                                new_payload[target_key] = raw_data[source_key]
                            elif source_key == "FULL_PAYLOAD":
                                new_payload[target_key] = raw_data
                        if new_payload:
                            payload = new_payload
                except:
                    pass

            # --- SMART ROUTING FOR UNIVERSAL ENDPOINTS ---
            # If URL is generic (e.g. .../api/v1) and we detect specific data, append suffix
            target_url = ep_config.url
            
            # Suffix Map
            suffix_map = {
                'power': '/add_power', 'water': '/add_water', 'gas': '/add_gas',
                'smoke': '/add_smoke', 'fire': '/add_fire', 'weather': '/add_weather',
                'lux': '/add_lux', 'humidity': '/add_humidity_temp', 'temperature': '/add_humidity_temp',
                'humidity_temp': '/add_humidity_temp', 'ultrasonic': '/add_ultrasonic'
            }

            suffix = ""
            
            # 1. IF ENDPOINT HAS FIXED TYPE (e.g. "lux"), USE IT FORCEFULLY
            if ep_config.target_device_type:
                target_type = ep_config.target_device_type
                
                # VALIDATION: Check if this payload actually contains the data we want
                # (Simple check: is key present?)
                # Special cases: humidity/temp share same packet often
                
                data_present = False
                data_present = False
                if target_type == 'power' and raw_data.get('power') is not None: data_present = True
                elif target_type == 'lux' and raw_data.get('lux') is not None: data_present = True
                elif target_type == 'gas' and (raw_data.get('gas') is not None or raw_data.get('gas_ppm') is not None): data_present = True
                elif target_type == 'smoke' and raw_data.get('smoke') is not None: data_present = True
                elif target_type == 'fire' and raw_data.get('fire') is not None: data_present = True
                elif target_type == 'water' and (raw_data.get('water') is not None or raw_data.get('water_level') is not None): data_present = True
                elif target_type == 'weather' and raw_data.get('weather') is not None: data_present = True
                elif target_type == 'ultrasonic' and raw_data.get('distance') is not None: data_present = True
                elif target_type in ['humidity', 'temperature', 'humidity_temp']:
                     if raw_data.get('humidity') is not None or raw_data.get('temperature') is not None: data_present = True
                
                # If Strict Type is set but data not present, SKIP
                if not data_present:
                    # Debug log only if verbose
                    # print(f"[CLOUD-MULTI] Skipping {ep_config.name} (Type: {target_type}) - Data not matched.")
                    return

                suffix = suffix_map.get(target_type, "")

            # 2. AUTO-DETECT (Fallback if no type set)
            else:
                if 'power' in raw_data: suffix = "/add_power"
                elif 'water_level' in raw_data or 'water' in raw_data: suffix = "/add_water"
                elif 'gas' in raw_data: suffix = "/add_gas"
                elif 'smoke' in raw_data: suffix = "/add_smoke"
                elif 'fire' in raw_data: suffix = "/add_fire"
                elif 'weather' in raw_data: suffix = "/add_weather"
                elif 'lux' in raw_data: suffix = "/add_lux"
                elif 'distance' in raw_data: suffix = "/add_ultrasonic"
                elif 'humidity' in raw_data: suffix = "/add_humidity_temp"
            
            # Append if valid suffix and NOT already in URL
            if suffix and suffix not in target_url:
                 if target_url.endswith('/'):
                     target_url += suffix[1:]
                 else:
                     target_url += suffix
            
            headers = {'Content-Type': 'application/json'}
            headers = {'Content-Type': 'application/json'}
            # Add Custom Headers if any
            if ep_config.headers:
                try:
                    custom_headers = json.loads(ep_config.headers)
                    if isinstance(custom_headers, dict):
                        headers.update(custom_headers)
                except:
                    pass # Ignore if invalid JSON or empty

            def json_serial(obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                return str(obj)

            json_payload = json.dumps(payload, default=json_serial)
            
            # Send to calculated target_url
            response = requests.post(target_url, data=json_payload, headers=headers, timeout=5)
            if response.status_code in [200, 201]:
                 print(f"[CLOUD-MULTI] Sent to {ep_config.name} ✅")
            else:
                 print(f"[CLOUD-MULTI] Failed {ep_config.name}: {response.status_code}")

        except Exception as e:
            print(f"[CLOUD-MULTI] Error {ep_config.name}: {e}")

    @staticmethod
    def _send_legacy(data):
        base_url = config.host_api
        if not base_url:
            return

        # AUTO-FIX: If user accidentally points to Gateway (5001) instead of Cloud (5002)
        if ":5001" in base_url:
            base_url = base_url.replace(":5001", ":5002")

        # Determine target endpoint based on data content
        endpoint = "/add_data_record" # Default fallback
        
        if data.get('lux') is not None: endpoint = "/add_lux"
        elif data.get('humidity') is not None or data.get('hum') is not None: endpoint = "/add_humidity_temp"
        elif data.get('temperature') is not None or data.get('temp') is not None: endpoint = "/add_humidity_temp"
        elif data.get('power') is not None: endpoint = "/add_power"
        elif data.get('gas') is not None: endpoint = "/add_gas"
        elif data.get('smoke') is not None: endpoint = "/add_smoke"
        elif data.get('water') is not None: endpoint = "/add_water"
        elif data.get('fire') is not None: endpoint = "/add_fire"
        elif data.get('weather') is not None: endpoint = "/add_weather"

        if base_url.endswith('/'): base_url = base_url[:-1]
        url = f"{base_url}{endpoint}"

        headers = { 'Content-Type': 'application/json', 'X-API-TOKEN': config.token_api }

        def json_serial(obj):
            if hasattr(obj, 'isoformat'): return obj.isoformat()
            return str(obj)

        try:
            payload = json.dumps(data, default=json_serial)
            response = requests.post(url, data=payload, headers=headers, timeout=5)
            if response.status_code in [200, 201]:
                print(f"[CLOUD] Data sent to {endpoint} successfully.")
            else:
                print(f"[CLOUD] Failed to {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"[CLOUD] Error sending to {endpoint}: {str(e)}")

    @staticmethod
    def _apply_mapping(data, mapping_str):
        if not mapping_str or mapping_str == '{}':
            return data
            
        try:
            mapping = json.loads(mapping_str)
            new_payload = {}
            for target_key, source_key in mapping.items():
                if source_key in data:
                    new_payload[target_key] = data[source_key]
                elif source_key == "FULL_PAYLOAD":
                    new_payload[target_key] = data
            return new_payload if new_payload else data
        except:
            return data

    @staticmethod
    def send_bulk_to_endpoint(data_list, ep_config):
        """
        Send a list of data to a specific Advanced Endpoint, applying its mapping.
        """
        try:
            # 1. Apply Mapping for each item
            mapped_list = []
            for item in data_list:
                mapped_item = CloudSender._apply_mapping(item, ep_config.mapping)
                mapped_list.append(mapped_item)
            
            # 2. Serialize
            def json_serial(obj):
                if hasattr(obj, 'isoformat'): return obj.isoformat()
                return str(obj)
            
            json_payload = json.dumps(mapped_list, default=json_serial)
            
            # 3. Send
            headers = {'Content-Type': 'application/json'}
            # (Optional: Parse ep_config.headers here if needed)
            
            response = requests.post(ep_config.url, data=json_payload, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                return True, "Success", 200
            return False, f"HTTP {response.status_code}: {response.text[:100]}", response.status_code
            
        except Exception as e:
            return False, str(e), 500

    @staticmethod
    def send_bulk_data(data_list, target_type):
        """
        Smart Bulk Sync:
        1. If Custom Endpoints exist: Send to ALL Active Endpoints (Multi-Cloud).
        2. If No Custom Endpoints: Fallback to Legacy (.env).
        """
        try:
             advanced_endpoints = []
             total_endpoints_count = -1
             if current_app:
                advanced_endpoints = EndpointConfig.query.filter_by(is_active=True).all()
                total_endpoints_count = EndpointConfig.query.count()
             
             # 1. Advanced Mode
             if total_endpoints_count > 0:
                 if not advanced_endpoints:
                     return True, "All endpoints disabled (No-Op)", 200
                 
                 success_count = 0
                 errors = []
                 
                 for ep in advanced_endpoints:
                     # Filter Logic: Check if this endpoint cares about this data type?
                     # Currently send_bulk_to_endpoint applies mapping. 
                     # Smart Routing (Suffix) is needed?
                     
                     # We need to construct a "Target EP" with the correct Suffix if needed.
                     # Similar to send_data logic or toggle logic.
                     # For Bulk, we blindly send to the configured URL unless we apply smart routing.
                     # Let's apply Smart Routing here too to be consistent.
                     
                     suffix_map = {
                        'power': '/add_power', 'water': '/add_water', 'gas': '/add_gas',
                        'smoke': '/add_smoke', 'fire': '/add_fire', 'weather': '/add_weather',
                        'lux': '/add_lux', 'humidity': '/add_humidity_temp', 'temperature': '/add_humidity_temp',
                        'humidity_temp': '/add_humidity_temp', 'ultrasonic': '/add_ultrasonic'
                     }
                     
                     target_ep = ep # Default
                     
                     # Apply Smart Routing Suffix if implicit type match or generic URL
                     suffix = suffix_map.get(target_type, "")
                     # Logic: If Type is set in Endpoint, strict match? 
                     # For Bulk Sync, the triggerer (Scheduler) passes 'target_type'.
                     
                     # If Endpoint has Specific Type (e.g. 'power'), ONLY send if target_type matches.
                     if ep.target_device_type and ep.target_device_type != 'all':
                         if ep.target_device_type != target_type:
                             # Skip this endpoint for this data batch
                             continue
                     
                     # Construct Temp EP with Suffix
                     temp_url = ep.url
                     if suffix and suffix not in temp_url:
                         if temp_url.endswith('/'): temp_url += suffix[1:]
                         else: temp_url += suffix
                     
                     # We can't modify the SQLA object directly without persisting or detaching.
                     # Use a lightweight shim/wrapper or just pass modified URL to a helper.
                     # CloudSender.send_bulk_to_endpoint uses ep_config.url. 
                     # Let's make a shim class again or modify the method signature. 
                     # Shim is safer.
                     class TempEP:
                        def __init__(self, obj, url):
                            self.url = url
                            self.mapping = obj.mapping
                            self.headers = obj.headers
                            self.name = obj.name
                     
                     shim_ep = TempEP(ep, temp_url)
                     
                     ok, msg, code = CloudSender.send_bulk_to_endpoint(data_list, shim_ep)
                     if ok: success_count += 1
                     else: errors.append(f"{ep.name}: {msg}")

                 if success_count > 0:
                     return True, f"Synced to {success_count} endpoints", 200
                 elif len(errors) > 0:
                    return False, " | ".join(errors), 500
                 else:
                    return True, "No matching endpoints for this type", 200

             # 2. Factory/Legacy Mode
             if total_endpoints_count == 0:
                 # DISABLING LEGACY FALLBACK as requested.
                 # User must explicitly configure an endpoint in Settings.
                 # return CloudSender._send_legacy_bulk(data_list, target_type)
                 return True, "No endpoints configured (Legacy disabled)", 200
                 
             # Fallback
             return True, "No endpoints", 200

        except Exception as e:
             return False, str(e), 500

    @staticmethod
    def _send_legacy_bulk(data_list, target_type):
        # ... (Previous bulk code) ...
        # For brevity, I'm keeping the previous logic or re-implementing it quickly
        base_url = config.host_api
        if not base_url: return False, "HOST_API not set", 0
        
        endpoint_map = { 'power': '/add_power', 'lux': '/add_lux', 'gas': '/add_gas', 'smoke': '/add_smoke',
            'water': '/add_water', 'fire': '/add_fire', 'weather': '/add_weather', 'humidity_temp': '/add_humidity_temp',
            'ultrasonic': '/add_ultrasonic' }
        endpoint = endpoint_map.get(target_type, '/sync')
        
        if base_url.endswith('/'): base_url = base_url[:-1]
        url = f"{base_url}{endpoint}"
        headers = { 'Content-Type': 'application/json', 'X-API-TOKEN': config.token_api }
        
        def json_serial(obj):
            if hasattr(obj, 'isoformat'): return obj.isoformat()
            return str(obj)
            
        try:
            payload = json.dumps(data_list, default=json_serial)
            response = requests.post(url, data=payload, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                return True, "Success", 200
            return False, response.text, response.status_code
        except Exception as e:
            return False, str(e), 500
