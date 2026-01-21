from core import MqttSensor, SystemInfo
from core.send_server import CloudSender
from config import config
import threading

from flask_server.app import create_app,db


from flask_server.app.model.model import DeviceRecord
import json
from datetime import datetime, timedelta

app = create_app()

from flask_server.app.scheduler import init_scheduler

def start_flask():
    with app.app_context():
        db.create_all()
        # Start Auto-Sync Scheduler
        init_scheduler(app)
       
    app.run(host='0.0.0.0',port=config.port_app,debug=True,threaded=False ,use_reloader=False)

def publis_system():
    mqtt = MqttSensor(config.hostmqtt)
    topic= config.device_id+"/status"
    return mqtt.system_info_msg(topic)

def process_sensor_data(payload):
    """
    Callback function to process incoming MQTT messages and save to DB.
    Rate Limit: Saves only if > 5 minutes since last record for this device.
    """
    try:
        data = json.loads(payload)
        device_id = data.get('device_id')
        
        if not device_id:
            return

        with app.app_context():
            # 1. Rate Limiting Check
            last_record = DeviceRecord.query.filter_by(device_id=device_id).order_by(DeviceRecord.created_at.desc()).first()
            
            if last_record:
                time_diff = datetime.now() - last_record.created_at
                if time_diff < timedelta(minutes=5):
                   return

            # 2. Save Data (Flexible keys)
            record = DeviceRecord(
                device_id=device_id,
                power=float(data.get('power')) if data.get('power') is not None else None,
                humidity=float(data.get('humidity') or data.get('hum')) if (data.get('humidity') is not None or data.get('hum') is not None) else None,
                temperature=float(data.get('temperature') or data.get('temp')) if (data.get('temperature') is not None or data.get('temp') is not None) else None,
                weather=str(data.get('weather')) if data.get('weather') is not None else None,
                fire=int(data.get('fire')) if data.get('fire') is not None else None,
                gas=float(data.get('gas')) if data.get('gas') is not None else None,
                gas_ppm=float(data.get('gas_ppm')) if data.get('gas_ppm') is not None else None,
                gas_voltage=float(data.get('gas_voltage')) if data.get('gas_voltage') is not None else None,
                smoke=float(data.get('smoke')) if data.get('smoke') is not None else None,
                lux=float(data.get('lux')) if data.get('lux') is not None else None,
                distance=float(data.get('distance')) if data.get('distance') is not None else None
            )
            
            db.session.add(record)
            db.session.commit()
            print(f"Saved data for device {device_id}")

            # Send to Cloud (Moved to Scheduler every 5 mins)
            # try:
            #     # Kirim data ASLI dari ESP32 (tanpa mapping ulang oleh gateway)
            #     CloudSender.send_data(data)
            # except Exception as e:
            #     print(f"Cloud sync error: {e}")

    except json.JSONDecodeError:
        print("Error: Failed to decode JSON payload")
    except Exception as e:
        print(f"Error saving to DB: {e}")

def subscribe_to_sensors():
    mqtt = MqttSensor(config.hostmqtt)
    mqtt.start_subscriber("sensor/data/#", on_message_callback=process_sensor_data)

if __name__ == '__main__':
    
    flask_thred = threading.Thread(target=start_flask)
    mqtt_thread = threading.Thread(target=publis_system)
    subscriber_thread = threading.Thread(target=subscribe_to_sensors)

    flask_thred.start()
    mqtt_thread.start()
    subscriber_thread.start()

    flask_thred.join()
    mqtt_thread.join()
    subscriber_thread.join()
