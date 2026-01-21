


# REX GATEWAY

Rex Gateway adalah aplikasi untuk penghubung antara sensor maupun controller dengan server

### Sensor Device Support: 
<table width="100%" valign="top">
<tr>
<td>
    <ul>
        <li><b>Sensor Power Meter</b> (Voltage, Current, Watt, kWh)</li>
        <li><b>Sensor Water</b> (Ultrasonic Level, AWLR, & Water Quality)</li>
        <li><b>Sensor Environmental</b> (Humidity & Temperature)</li>
        <li><b>Weather Station</b> (Rain, Wind Speed, Direction)</li>
    </ul>
</td>
<td>
    <ul>
        <li><b>Safety Sensors</b>:
            <ul>
                <li>Fire Detection</li>
                <li>Smoke Detection</li>
                <li>Gas Leak Detection</li>
            </ul>
        </li>
        <li><b>Lighting</b>: LUX Sensor / Light Meter</li>
    </ul>
</td>
</tr>
</table> 


### Informasi Aplikasi: 
**Core System:**
- **Language**: Python 3.10 +
- **Protocol**: MQTT using Mosquitto Broker
- **Framework**: Flask (Micro-framework)
- **Database**: SQLite (Default) / Support MySQL

**Frontend & UI:**
- **Templating**: Jinja2
- **Styling**: Bootstrap 3 + Custom CSS (Dark/Light support)
- **Interactivity**: jQuery AJAX (Realtime Updates)
- **Charts**: Flot Charts

**Python Packages:**
- `Flask`, `Flask-SQLAlchemy`, `Flask-Migrate`, `Flask-Login`
- `Flask-Bcrypt` (Security), `Flask-WTF` (Forms)
- `paho-mqtt` (IoT Communication)
- `psutil` (System Monitoring), `speedtest-cli`

    #### Struktur File:
```
.
├── README.md
├── config
│   ├── __init__.py
│   ├── api.py
│   ├── app.db
│   ├── config.py
│   └── model.py
├── core
│   ├── __init__.py
│   ├── checkpoint.py
│   ├── cisco_switch.py
│   ├── mqtt_sensor.py
│   ├── networking.py
│   ├── send_server.py
│   └── system_info.py
├── flask_server
│   └── app
│       ├── __init__.py
│       ├── blueprints
│       │   ├── api_routes.py
│       │   └── web_routes.py
│       ├── controller
│       │   ├── api
│       │   │   ├── device_controller.py
│       │   │   └── network_controller.py
│       │   ├── auth_controller.py
│       │   ├── device_controller.py
│       │   ├── home_Controller.py
│       │   ├── network_controller.py
│       │   └── setting.py
│       ├── model
│       │   ├── model.py
│       │   └── user_model.py
│       ├── request_form
│       │   ├── LoginForm.py
│       │   ├── RegisterForm.py
│       ├── static
│       │   └── assets
│       │       ├── css
│       │       ├── img
│       │       ├── js
│       │       ├── less
│       │       └── lib
│       └── views
│           ├── device_list.html
│           ├── home.html
│           ├── layouts
│           │   ├── app.html
│           │   └── auth.html
│           ├── login.html
│           ├── networking.html
│           └── register.html
├── config.ini
├── main.py
└── requirements.txt
```
### Installation
Clone repository github:<br>

````
$ git clone https://github.com/Rexshin1/Rex_Gateway.git
````
Masuk dalam directory:
````
$ cd rex_gateway/
````
Membuat environment:
````
$ python venv env
````
Mengaktifkan environment:
````
Linux or Mac:
 $ source env/bin/activate 

Windows:
 $ .\venv\Scripts\activate
````

Update package:
````
$ pip install -r requirements.txt
````
Running program:
```
Linux or Mac:
$ python main.py

Windows:
$ py main.py
```

### File main.py
````python
from core import MqttSensor,SystemInfo
from config import config
import threading

from flask_server.app import create_app,db


app = create_app()





def start_flask():
    with app.app_context():
        db.create_all()
       
    app.run(host='0.0.0.0',port=config.port_app,debug=True,threaded=False ,use_reloader=False)

def publis_system():
    mqtt = MqttSensor(config.hostmqtt)
    topic= config.device_id+"/status"
    return mqtt.system_info_msg(topic)
# 
# print(SystemInfo.get_cpu_temperature())

if __name__ == '__main__':
    
    # publis_system()
    flask_thred = threading.Thread(target=start_flask)
    mqtt_thread = threading.Thread(target=publis_system)

    # flask_thred.daemon = True
    # mqtt_thread.daemon = True

    flask_thred.start()
    # mqtt_thread.start()
    flask_thred.join()
    # mqtt_thread.join()

    # # Start threads
    # thread1.start()
    # thread2.start()

    
    # start_flask()
    

    # mqtt.system_info_msg(topic)
````
