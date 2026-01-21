import requests
import speedtest
import threading
from queue import Queue
import subprocess
import socket


class Networking:
    def __init__(self):
        pass
   
    def SpeedTest(self):
        st = speedtest.Speedtest()

        # Pilih server terbaik berdasarkan ping
        print("Mencari server terbaik...")
        st.get_best_server()

        # Uji kecepatan download
        print("Mengukur kecepatan download...")
        download_speed = st.download()

        # Uji kecepatan upload
        print("Mengukur kecepatan upload...")
        upload_speed = st.upload()

        # Uji ping
        ping = st.results.ping

        # Tampilkan hasil
        print(f"Ping: {ping:.2f} ms")
        print(f"Kecepatan Download: {download_speed / 1_000_000:.2f} Mbps")
        print(f"Kecepatan Upload: {upload_speed / 1_000_000:.2f} Mbps")


    def ping_ip(self,ip):
        try:
            # Send a single ping packet (adjust for OS: "-c" for Linux/Mac, "-n" for Windows)
            output = subprocess.run(
                ["ping", "-c", "1", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return output.returncode == 0
        except Exception as e:
            print(f"Error pinging {ip}: {e}")
            return False

    # Get hostname for an IP address
    def get_hostname(self,ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except socket.herror:
            return None
        
    def scan_ports(self,ip, ports):
        open_ports = []
        for port in ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    if s.connect_ex((ip, port)) == 0:
                        open_ports.append(port)
            except Exception as e:
                pass
        return open_ports

    # Worker function for threads
    def worker(self,queue, results, ports):
        while not queue.empty():
            ip = queue.get()
            if self.ping_ip(ip):
                hostname = self.get_hostname(ip)
                open_ports = self.scan_ports(ip, ports)
                results.append((ip, hostname or "Unknown", open_ports))

    def scan_ips(self,start_ip, end_ip, ports, threads=10):
        def ip_to_int(ip):
            return sum(int(octet) << (8 * i) for i, octet in enumerate(reversed(ip.split("."))))
        
        def int_to_ip(ip_int):
            return ".".join(str((ip_int >> (8 * i)) & 0xFF) for i in reversed(range(4)))

        start = ip_to_int(start_ip)
        end = ip_to_int(end_ip)

        # Prepare queue and results list
        ip_queue = Queue()
        results = []
        for ip_int in range(start, end + 1):
            ip_queue.put(int_to_ip(ip_int))

        # Start threads
        threads_list = []
        for _ in range(threads):
            thread = threading.Thread(target=self.worker, args=(ip_queue, results, ports))
            thread.start()
            threads_list.append(thread)

        # Wait for all threads to finish
        for thread in threads_list:
            thread.join()

        return results
    
    def scan_network(self,start_ip, end_ip, threads=10):
        list_network = []
        ports_to_scan = [22, 80, 443, 8080]  # Common ports to scan
        
        active_hosts = self.scan_ips(start_ip, end_ip, ports_to_scan, threads=10)
        for ip, hostname, open_ports in active_hosts:
            data = {
                "ip_address": ip,
                "hostname": hostname,
                "port": open_ports
            }
            list_network.append(data)
        
        return list_network