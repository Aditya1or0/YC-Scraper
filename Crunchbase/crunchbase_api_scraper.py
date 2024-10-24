import os
import requests
import pandas as pd
from tqdm import tqdm
import time
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Logging
logging.basicConfig(
    filename='crunchbase_api_scraper.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Load API Key from Environment Variable
API_KEY = os.getenv('CRUNCHBASE_API_KEY')
if not API_KEY:
    logging.error("API key not found. Please set the CRUNCHBASE_API_KEY environment variable.")
    exit(1)
else:
    logging.info("API key loaded successfully.")

# API Configuration
BASE_URL = 'https://api.crunchbase.com/v4/data/entities/organizations'
HEADERS = {
    'X-cb-user-key': API_KEY,
    'Content-Type': 'application/json',
    'User-Agent': 'YourAppName/1.0 (your.email@example.com)'  # Replace with your details
}

# Pagination Settings
PER_PAGE = 100  # Maximum allowed by API
TOTAL_PAGES = 10000  # Set a high number; loop will stop when no more data
RATE_LIMIT_DELAY = 0.3  # 200 calls per minute => 0.3 seconds per call

# Initialize Data Storage
companies_data = []

def fetch_companies(page):
    """
    Fetch companies data from a specific page.
    """
    params = {
        'page': page,
        'limit': PER_PAGE
        # Add other filters or parameters as needed
    }
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            # Rate limit exceeded
            logging.warning(f"Rate limit exceeded on page {page}. Waiting for 60 seconds.")
            time.sleep(60)  # Wait before retrying
            return fetch_companies(page)
        elif response.status_code == 401:
            logging.error("Unauthorized access. Check your API key.")
            exit(1)
        else:
            logging.error(f"Failed to fetch page {page}. Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request exception on page {page}: {e}")
        return None

def extract_company_data(item):
    """
    Extract desired fields from a single company item.
    """
    organization = item.get('organization', {})
    
    # Handle nested fields and missing data
    def get_nested(data, keys, default=None):
        for key in keys:
            data = data.get(key, {})
        return data if data else default
    
    # Extract Top 5 Investors (assuming the API provides such data)
    top_investors = []
    investors = organization.get('investors', {}).get('items', [])
    for investor in investors[:5]:
        investor_name = investor.get('investor', {}).get('name')
        if investor_name:
            top_investors.append(investor_name)
    
    # Extract Founders
    founders = []
    founders_data = organization.get('founders', {}).get('items', [])
    for founder in founders_data:
        founder_name = founder.get('founder', {}).get('name')
        if founder_name:
            founders.append(founder_name)
    
    company = {
        'Organization Name': organization.get('name'),
        'Stage': organization.get('stage'),
        'Industries': ', '.join(organization.get('categories', [])),
        'Headquarters Location': organization.get('headquarters', {}).get('region'),
        'Description': organization.get('short_description'),
        'CB Rank (Company)': organization.get('cb_rank'),
        'Investment Stage': organization.get('investment_stage'),
        'Number of Portfolio Organizations': organization.get('portfolio_count'),
        'Number of Investments': organization.get('investments_count'),
        'Number of Lead Investments': organization.get('lead_investments_count'),
        'Accelerator Program Type': organization.get('accelerator_program_type'),
        'Accelerator Application Deadline': organization.get('accelerator_application_deadline'),
        'Investor Type': organization.get('investor_type'),
        'Number of Founders (Alumni)': len(founders),
        'Number of Alumni': organization.get('alumni_count'),
        'Founders': ', '.join(founders),
        'Number of Employees': organization.get('number_of_employees'),
        'Last Funding Date': organization.get('last_funding_date'),
        'Last Funding Amount': organization.get('last_funding_amount'),
        'Last Funding Type': organization.get('last_funding_type'),
        'Last Equity Funding Type': organization.get('last_equity_funding_type'),
        'Last Equity Funding Amount': organization.get('last_equity_funding_amount'),
        'Total Funding Amount': organization.get('total_funding_amount'),
        'Top 5 Investors': ', '.join(top_investors),
        'Estimated Revenue Range': organization.get('estimated_revenue_range'),
        'Operating Status': organization.get('operating_status'),
        'Founded Date': organization.get('founded_date'),
        'Company Type': organization.get('company_type'),
        'Website': organization.get('homepage_url'),
        'LinkedIn': organization.get('linkedin_url'),
        'Contact Email': organization.get('contact_email'),
        'Phone Number': organization.get('phone_number'),
        'Full Description': organization.get('full_description')
    }
    
    return company

def main():
    """
    Main function to fetch and store company data.
    """
    global companies_data
    for page in tqdm(range(1, TOTAL_PAGES + 1), desc="Fetching Companies"):
        data = fetch_companies(page)
        if data and 'data' in data and 'items' in data['data']:
            items = data['data']['items']
            if not items:
                logging.info(f"No more data found at page {page}. Stopping.")
                break
            for item in items:
                company = extract_company_data(item)
                companies_data.append(company)
        else:
            logging.warning(f"Unexpected data format or failed to retrieve data on page {page}. Stopping.")
            break
        
        # Respect Rate Limits
        time.sleep(RATE_LIMIT_DELAY)  # 0.3 seconds delay to stay within 200 calls/minute
    
    # Convert to DataFrame
    df = pd.DataFrame(companies_data)
    
    # Data Cleaning
    df.drop_duplicates(subset=['Organization Name'], inplace=True)
    df['Founded Date'] = pd.to_datetime(df['Founded Date'], errors='coerce')
    df['Last Funding Date'] = pd.to_datetime(df['Last Funding Date'], errors='coerce')
    
    # Save to CSV
    output_file = 'crunchbase_companies_selected_columns.csv'
    df.to_csv(output_file, index=False)
    logging.info(f"Data retrieval complete. Saved to {output_file}.")
    print(f"Data retrieval complete. Saved to {output_file}.")

if __name__ == "__main__":
    main()
