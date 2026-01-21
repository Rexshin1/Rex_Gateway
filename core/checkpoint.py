
import requests

class Checkpoint:
    def __init__(self,username,password,endpoint):
        self.username = username
        self.password = password
        self.endpoint = endpoint

    def CheckPointAuth(self):
        login_payload = {
            "user": self.username,
            "password": self.password
        }
        login_response = requests.post(f"{self.endpoint}/login", json=login_payload, verify=False)
        sid = login_response.json().get("sid")
        return sid
    
    def CheckpointGateway(self,token):
        headers = {
            "Content-Type": "application/json",
            "X-chkp-sid": token
        }
        # Performa Gateway
        gateway_response = requests.post(f"{self.endpoint}/show-simple-gateway", headers=headers, verify=False)
        return gateway_response.json()

    def CheckpointHealth(self,token):
        headers = {
            "Content-Type": "application/json",
            "X-chkp-sid": token
        }
        # Performa Checkpoint
        health_response = requests.post(f"{self.endpoint}/show-health-monitor", headers=headers, verify=False)
        return health_response.json()
  