import paho.mqtt.client as mqtt
import time,json
from core import SystemInfo


class MqttSensor:
    def __init__(self,host):
        self.host = host
        self.subscriber_client = None


    def publish_message(self, topic, message):
        from config import config
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                # print("Connected to MQTT Broker for publishing!")
                pass
            else:
                print(f"Failed to connect for publishing, return code {rc}")

        client = mqtt.Client()
        
        # Tambahkan autentikasi di sini
        if config.user_mqtt and config.pass_mqtt:
            client.username_pw_set(config.user_mqtt, config.pass_mqtt)
            
        client.on_connect = on_connect

        try:
            client.connect(self.host, config.port_mqtt, 60)
            client.loop_start()
            result = client.publish(topic, message, qos=0)
            status = result[0]
        except Exception as e:
            # print(f"Publish error: {e}")
            pass
        finally:
            client.loop_stop()
            client.disconnect()

    def start_subscriber(self, topic, on_message_callback=None):
        from config import config
        self.on_message_callback = on_message_callback
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        
        # Tambahkan autentikasi di sini
        if config.user_mqtt and config.pass_mqtt:
            self.client.username_pw_set(config.user_mqtt, config.pass_mqtt)
            
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        try:
            self.client.connect(self.host, config.port_mqtt, 60)
            self.client.loop_forever()
        except Exception as e:
            print(f"Subscriber failed to start: {e}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Subscriber connected to MQTT Broker!")
            client.subscribe("sensor/data/#")
        else:
            print(f"Failed to connect subscriber, return code {rc}")
    
    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        # print(f"Received message: {payload} on topic {msg.topic}")
        
        if self.on_message_callback:
            self.on_message_callback(payload)

    @staticmethod
    def sensor_record(msg):
        return msg
    
    def system_info_msg(self,topic):
        """
        Periodically sends system information to the specified topic.
        This is a looping function.
        """
        while True:
            try :
                cpu_temp = SystemInfo.get_cpu_temperature()
                cpu_usage = SystemInfo.get_cpu_usage()
                ram_usage = SystemInfo.get_memory_usage()
                disk_usage = SystemInfo.get_disk_usage()

                msg = {
                    "temperature" : f"{cpu_temp}",
                    "cpu_usage" : f"{cpu_usage}",
                    "memory" : f"{ram_usage}",
                    "disk" : f"{disk_usage}"
                }
                self.publish_message(topic,json.dumps(msg))
            except Exception as e:
                print(e)

            time.sleep(5)

