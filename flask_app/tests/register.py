import requests
import yaml

with open("flask_app/tests/test_config.yml", "r") as f:
    config = yaml.safe_load(f)

def register():
    url = f"{config['flask_app_url']}/api/register"
    data = {
        "email": config["email"],
        "password": config["password"],
        "firstname": config["first_name"],
        "lastname": config["last_name"],
        "institution": config["institution"]
    }
    header = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=header)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
if __name__ == "__main__":
    register()
    