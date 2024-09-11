import requests

response = requests.get("https://api.example.com/data")
if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}")
