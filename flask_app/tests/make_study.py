import requests
import yaml

with open("flask_app/tests/test_config.yml", "r") as f:
    config = yaml.safe_load(f)
    
def get_token():
    print("Getting access token")
    url = f"{config['flask_app_url']}/api/login"
    data = {
        "email": config["email"],
        "password": config["password"]
    }
    header = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=header)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    if response.status_code == 200:
        return response.json()["access_token"]
    
def create_study(token):
    print("Creating study")
    url = f"{config['flask_app_url']}/api/studies"
    data = {
        "public_name": "Test Study",
        "internal_name": "test_study"
    }
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, json=data, headers=header)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    return response.json()

def make_ping_templates(token, study_id):
    print("Creating ping templates")
    url = f"{config['flask_app_url']}/api/studies/{study_id}/ping_templates"
    data = {
        "name": "Test Ping Template",
        "message": "Test message",
        "url": "https://www.google.com",
        "schedule": [
            {"start_day_num": 1, "start_time": "09:00", "end_day_num": 1, "end_time": "10:00"},
            {"start_day_num": 2, "start_time": "09:00", "end_day_num": 2, "end_time": "10:00"},
            {"start_day_num": 3, "start_time": "09:00", "end_day_num": 3, "end_time": "10:00"},
        ],
        "reminder_latency": "1 hour",
        "expire_latency": "12 hours"
    }
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, json=data, headers=header)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    return response.json()

    
    
def get_study(token, study_id):
    print("Getting study")
    
    url = f"{config['flask_app_url']}/api/studies/{study_id}"
    header = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=header)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


    
if __name__ == "__main__":
    token = get_token()
    resp = create_study(token)
    study_id = resp["study"]["id"]
    make_ping_templates(token, study_id)
    