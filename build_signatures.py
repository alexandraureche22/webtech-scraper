import requests
import string

BASE_URL = "https://raw.githubusercontent.com/enthec/webappanalyzer/refs/heads/main/src/technologies/"

def download_all_signatures():
    all_technologies = {}
    # litere de la a la z plus "_" pt nume care incep cu cifra sau simbol
    letters = list(string.ascii_lowercase) + ["_"]
    for letter in letters:
        url = BASE_URL + letter + ".json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            all_technologies.update(data)
        else:
            print(f"Could not fetch {letter}.json (status {response.status_code})")

    return all_technologies
# test it
signatures = download_all_signatures()
print(f"Total technologies loaded: {len(signatures)}")
print("Shopify entry:", signatures.get("Shopify"))