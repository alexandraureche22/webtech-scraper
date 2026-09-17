import requests
import re
from build_signatures import download_all_signatures

def clean_pattern(pattern):
    #pattern-urile din Wappalyzer pot avea metadate dupa punct si virgula, de ex.
    #"sdks\.shopifycdn\.com;confidence:50"- doar partea de regex
    return pattern.split("\\;")[0]

def detect_technologies(domain, signatures):
    url = "https://" + domain
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }

    try:
        response = requests.get(url, timeout=10, headers=headers)
        html_text = response.text
    except Exception as e:
        print(f"Could not fetch {domain}: {e}")
        return {}

    found = {}  # nume_tehnologie - lista de dovezi (ce pattern s a potrivit)

    for tech_name, tech_data in signatures.items():
        matches = []
        # verificam semnaturile de tip scriptSrc
        script_src_patterns = tech_data.get("scriptSrc", [])
        for raw_pattern in script_src_patterns:
            pattern = clean_pattern(raw_pattern)
            try:
                if re.search(pattern, html_text):
                    matches.append(f"scriptSrc: {raw_pattern}")
            except re.error:
                continue  #sar pattern-urile care raman invalide si dupa curatare

        #verific semnaturile de tip meta
        meta_patterns = tech_data.get("meta", {})
        for meta_name, meta_pattern in meta_patterns.items():
            if meta_name.lower() in html_text.lower():
                matches.append(f"meta: {meta_name}")
        if matches:
            found[tech_name] = matches
    return found

# toate semnaturile o singura data
print("Loading signatures...")
signatures = download_all_signatures()
print(f"Loaded {len(signatures)} technologies")

# test pe disneystore.com
result = detect_technologies("disneystore.com", signatures)
for tech, proof in result.items():
    print(f"{tech}: {proof}")