import requests
import re
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from build_signatures import download_all_signatures

def clean_pattern(pattern):
    return pattern.split("\\;")[0]

def detect_technologies(domain, signatures):
    url = "https://" + domain
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }
    try:
        response = requests.get(url, timeout=8, headers=headers)
        html_text = response.text
    except Exception as e:
        return {"_error": str(e)}
    found = {}

    for tech_name, tech_data in signatures.items():
        matches = []
        script_src_patterns = tech_data.get("scriptSrc", [])
        for raw_pattern in script_src_patterns:
            pattern = clean_pattern(raw_pattern)
            try:
                if re.search(pattern, html_text):
                    matches.append(f"scriptSrc: {raw_pattern}")
            except re.error:
                continue

        meta_patterns = tech_data.get("meta", {})
        for meta_name, meta_content_pattern in meta_patterns.items():
            meta_tag_regex = rf'<meta[^>]+name=["\']?{re.escape(meta_name)}["\']?[^>]*>'
            if re.search(meta_tag_regex, html_text, re.IGNORECASE):
                matches.append(f"meta: {meta_name}")

        if matches:
            found[tech_name] = matches
    return found

print("Loading signatures...")
signatures = download_all_signatures()
print(f"Loaded {len(signatures)} technologies")

df = pd.read_parquet("part-00000-66e0628d-2c7f-425a-8f5b-738bcd6bf198-c000.snappy.parquet")
domains = df["root_domain"].tolist()

results = {}

#cate 20 de domenii in paralel
with ThreadPoolExecutor(max_workers=20) as executor:
    future_to_domain = {executor.submit(detect_technologies, domain, signatures): domain for domain in domains}

    for i, future in enumerate(as_completed(future_to_domain)):
        domain = future_to_domain[future]
        result = future.result()
        results[domain] = result
        print(f"[{i+1}/{len(domains)}] Done: {domain} — {len(result)} technologies found")

#salvez rezultatele intr-un fisier
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved to results.json")

# statistici
all_found_techs = set()
for domain, techs in results.items():
    if "_error" not in techs:
        all_found_techs.update(techs.keys())

print(f"Total unique technologies found: {len(all_found_techs)}")