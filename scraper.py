import requests

technology_signatures = {
    "Salesforce Commerce Cloud": "demandware.static",
    "Adobe Experience Platform Launch": "assets.adobedtm.com",
    "Google reCAPTCHA": "google.com/recaptcha",
    "Salesforce CQuotient": "cdn.cquotient.com",
    "Google Analytics": "google-analytics",
    "LaunchDarkly": "launch-darkly",
}

def detect_technologies(domain):
    #add https:// in front if it's missing, so requests knows how to reach it
    url = "https://" + domain

    try:
        #fetch the raw HTML of the page(timeout so we dontt wait forever on a dead site)
        response = requests.get(url, timeout=10)
        html_text = response.text
    except Exception as e:
        #some sites will fail to load(timeout, no SSL, doesnt exist, etc.)
        print(f"Could not fetch {domain}: {e}")
        return []
    found = []  #empty list to collect technologies we detect
    #go through every(name, signature) pair in the dictionary
    for tech_name, signature in technology_signatures.items():
        if signature in html_text:
            found.append(tech_name)
    return found

# #test it on one domain first
# result = detect_technologies("disneystore.com")
# print("disneystore.com:", result)

# test it on a few domains
test_domains = [
    "disneystore.com",
    "gogroupauto.com",
    "jcmobilecigars.com",
]

for domain in test_domains:
    result = detect_technologies(domain)
    print(f"{domain}: {result}")