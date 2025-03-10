import requests
import json
import urllib.parse

# Define your headers, replace with your actual headers from your environment.
headers = {
    "accept": "application/vnd.linkedin.normalized+json+2.1",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "csrf-token": "ajax:4048042056122993237",  # Replace with the actual CSRF token
    "referer": "https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22103720977%22%2C%22106204383%22%5D&industryCompanyVertical=%5B%2243%22%2C%2245%22%2C%2241%22%5D&keywords=dubai&origin=FACETED_SEARCH&sid=ePb",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "x-li-lang": "en_US",
    "x-restli-protocol-version": "2.0.0",
}

# Load cookies from linkedin_cookies.json
with open('linkedin_cookies.json', 'r') as f:
    linkedin_cookies = json.load(f)
cookies = {cookie['name']: cookie['value'] for cookie in linkedin_cookies}

def fetch_companies_list(start=0):
    url = f"https://www.linkedin.com/voyager/api/graphql?variables=(start:{start},origin:FACETED_SEARCH,query:(flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:companyHqGeo,value:List(103720977,106204383)),(key:industryCompanyVertical,value:List(1737,1770,1696,43,41,45)),(key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.92cc53470cef3c578ab1d34676d5320c"

    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code == 200:
        data = response.json()
        total = data['data']['data']['searchDashClustersByAll']['paging']['total']
        company_objects = [item for item in data['included'] if item.get('template') == 'UNIVERSAL']
        included = []
        for company in company_objects:
            company_data = {}
            company_data['id'] = company['trackingUrn'].split(":")[-1]
            company_data['name'] = company['title']['text']
            company_data['universalName'] = company['navigationUrl'].split("/")[-2]
            included.append(company_data)
        print("included: ", included)

        return total, included
    else:
        print(f"Failed to fetch companies list: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.content}")
        return 0, []

def fetch_company_details(universal_name, company_name):
    url = f"https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(universalName:{universal_name})&queryId=voyagerOrganizationDashCompanies.00f354be1dd02e328635b27fbeb6cbea"
    response = requests.get(url, headers=headers, cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        included = data.get('included', [])  # Fix: Look inside 'included' list

        company_info = None
        for entry in included:
            if 'specialities' in entry:  # Find the correct object
                company_info = entry
                break

        if company_info:
            specialities = company_info.get('specialities', [])  # Extract specialities correctly
            headquarters = company_info.get('headquarter', {}).get('address', {})
            employee_count = company_info.get('employeeCount', {})
            website_url = company_info.get('websiteUrl', '')

            location = {
                'city': headquarters.get('city', ''),
                'geographicArea': headquarters.get('geographicArea', ''),
                'country': headquarters.get('country', '')
            }

            result = {
                'name': company_name,
                'specialities': specialities,
                'headquarters': location,
                'employee_count': employee_count,
                'website_url': website_url
            }

            print("Fetched company info: ", result)

            # Write result to file
            with open('company_details_output.json', 'a') as outfile:
                json.dump(result, outfile)
                outfile.write('\n')

            return result

    print(f"Failed to fetch details for {company_name}")
    return None

def main():
    start = 0

    while True:
        total, included = fetch_companies_list(start)
        print(total)
        if not included:
            break

        print(f"Fetched {len(included)} companies, fetching details sequentially...")

        for company in included:
            company_universal_name = company['universalName']
            company_name = company['name']
            fetch_company_details(company_universal_name, company_name)
            print(f"Company: {company['name']}")

        start += len(included)
        print(f"Fetched {start} of {total} companies")

        if start >= 10:
            break

if __name__ == "__main__":
    main()
