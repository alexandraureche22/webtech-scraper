import requests
import re
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
            meta_tag_regex = rf'<meta[^>]+name=["\']?{re.escape(meta_name)}["\']?[^>]+content=["\']([^"\']*)["\']'
            match = re.search(meta_tag_regex, html_text, re.IGNORECASE)

            if match:
                content_value = match.group(1)
                if meta_content_pattern == "":
                    matches.append(f"meta: {meta_name}")
                else:
                    clean_content_pattern = clean_pattern(meta_content_pattern)
                    try:
                        if re.search(clean_content_pattern, content_value, re.IGNORECASE):
                            matches.append(f"meta: {meta_name}={content_value}")
                    except re.error:
                        continue

        if matches:
            found[tech_name] = matches

    return found


# testam
print("Loading signatures...")
signatures = download_all_signatures()

result = detect_technologies("abbikadabbisbakingco.com", signatures)
print(f"Technologies found: {len(result)}")
for tech, proof in result.items():
    print(f"{tech}: {proof}")