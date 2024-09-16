import requests
import os


token = os.getenv("SERVER_TOKEN")

url = "http://0.0.0.0:8000/api-stats"
headers = {
    "Authorization": "Bearer " + token
}

response = requests.get(url, headers=headers)
print(response.json())