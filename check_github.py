import requests
import json

def check_github():
    url = "https://api.github.com/repos/Aabishkar2/nepse-data/contents/data"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for item in data:
            print(f"{item['name']} - {item['type']}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    check_github()
