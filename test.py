import requests
import json

# Replace with the API URL found in DevTools
api_url = "https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22103720977%22%2C%22106204383%22%5D&industryCompanyVertical=%5B%2245%22%2C%2241%22%2C%2243%22%5D&origin=FACETED_SEARCH&sid=QzK"


with open('linkedin_cookies.json', 'r') as f:
    linkedin_cookies = json.load(f)
cookies = {cookie['name']: cookie['value'] for cookie in linkedin_cookies}


# Set headers (copy from DevTools -> Headers)
headers = {
    "User-Agent": "Mozilla/5.0",
    "csrf-token": "ajax:4048042056122993237",  # Replace with the actual CSRF token
}

response = requests.get(api_url, headers=headers, cookies=cookies)

if response.status_code == 200:
    data = response.json()
    print(data)  # Print and analyze available fields
else:
    print("Failed to fetch data:", response.status_code)
