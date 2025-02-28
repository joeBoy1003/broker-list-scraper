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
    url = f"https://www.linkedin.com/voyager/api/graphql?variables=(start:{start},origin:FACETED_SEARCH,query:(flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:companyHqGeo,value:List(103720977,106204383)),(key:industryCompanyVertical,value:List(43,41,45)),(key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.92cc53470cef3c578ab1d34676d5320c"

    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code == 200:
        data = response.json()
        total = data['data']['data']['searchDashClustersByAll']['paging']['total']
        included = [item for item in data['included'] if item['$type'] == 'com.linkedin.voyager.dash.organization.Company']
        return total, included
    else:
        print(f"Failed to fetch companies list: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.content}")
        return 0, []

def fetch_company_details(company_urn):
    try:
        print(f"Starting fetch for {company_urn}")
        encoded_urn = urllib.parse.quote(company_urn, safe='')
        url = f"https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(organizationalPageUrn:{encoded_urn},context:ORGANIZATIONAL_PAGE_MEMBER_HOME)&queryId=voyagerOrganizationDashViewWrapper.37e905692bf95ef899e1723453cd0085"
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            data = response.json()
            details = {}
            # Extract total employees
            try:
                total_employees = data['included'][0]['premiumCompanyInsightCardHiresWrapper']['elements'][0]['companyInsights']['highlightsInsights']['headcountGrowth'][-1]['employeeCount']
            except (KeyError, IndexError):
                total_employees = None

            # Extract company title
            try:
                company_name = data['data']['data']['organizationDashViewWrapperByOrganizationalPageAndContext']['elements'][0]['nestedComponents'][0]['component']['header']['heading']['text'].replace("Insights on ", "")
            except (KeyError, IndexError):
                company_name = None

            details['company_name'] = company_name.encode('utf-8').decode('unicode_escape')
            details['total_employees'] = total_employees

            # Save details to file immediately
            with open('company_details.json', 'a') as outfile:
                json.dump(details, outfile)
                outfile.write('\n')

            print(json.dumps(details, indent=4))  # Print details as they are fetched
        else:
            print(f"Failed to fetch company details: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Content: {response.content}")
    except Exception as e:
        print(f"Exception occurred while fetching details for {company_urn}: {e}")
    finally:
        print(f"Finished fetch for {company_urn}")

def main():
    start = 0

    while True:
        total, included = fetch_companies_list(start)
        if not included:
            break

        print(f"Fetched {len(included)} companies, fetching details sequentially...")

        for company in included:
            company_urn = company['entityUrn'].replace("fsd_company:", "fsd_organizationalPage:")
            fetch_company_details(company_urn)

        start += len(included)
        print(f"Fetched {start} of {total} companies")

        if start >= total:
            break

if __name__ == "__main__":
    main()
