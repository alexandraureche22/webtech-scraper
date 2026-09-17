import requests

url = "https://raw.githubusercontent.com/enthec/webappanalyzer/refs/heads/main/src/technologies/s.json"
response = requests.get(url)
data = response.json()

print(data.get("Shopify"))