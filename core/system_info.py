import psutil

class SystemInfo:
    def __init__(self):
        self.temperature = ""
        self.cpu_usage = ""
        self.memory = ""



    def get_cpu_temperature():
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return "No temperature sensors found."
            for name, entries in temps.items():
                if "coretemp" in name.lower() or "cpu" in name.lower():
                    return entries[0].current
            return "No CPU temperature sensor found."
        except Exception as e:
            return f"Error: {e}"
        
    def get_memory_usage():
        try:
            memory = psutil.virtual_memory()
            # total = memory.total / (1024 ** 3)  # Convert bytes to GB
            # used = memory.used / (1024 ** 3)   # Convert bytes to GB
            # free = memory.available / (1024 ** 3)  # Convert bytes to GB
            return memory.percent  # Memory usage as a percentage
        except Exception :
            return "Not detected"
        
    def get_cpu_usage():
        # Measure CPU usage with a 1-second interval
        try:    
            cpu_usage = psutil.cpu_percent(interval=1)
            return cpu_usage
        except Exception:
            return "Can't read .."

    def get_disk_usage(path="/"):
        # Measure CPU usage with a 1-second interval
        try:
            disk_usage = psutil.disk_usage(path)
            return  disk_usage.percent
        except Exception as e:
            return "Can't read ..."



    

