import pandas as pd
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager  # For automatic driver management
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------------------------
# Configure Logging
# ------------------------------
logging.basicConfig(
    filename='scraping.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# ------------------------------
# Configuration and Setup
# ------------------------------

# List of randomized user agents
AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/120.0.0.0 Safari/537.36",
    # Add more user agents as needed
]

# List of Crunchbase company identifiers
page_id = [
    'goally-llc', 'cloudtrack', 'planable-io', 'dynepic', 'learnt',
    'players-lounge', 'maaxmarket', 'kinsu', 'bamboo', 
    'many', 'thync', 'trekker', 'databook', 'fleetwit',
    'jamieai', 'medbelle', 'amio-io', 'agnes-intelligence',
    'hypefactors', 'botstar', '4tuna', 'zohunt', 'volumeet',
    'greendeck', 'juntrax-solutions', 'urbanhire', 'triporate',
    'synchronous-health', 'livescale', 'botsify', 'iostash',
    'visualino-ug-haftungsbeschrankt', 'contentstudio', 'campsite-bio',
    'retainly', 'pushbots', 'hoy', 'intelistyle', 'shopic',
    'gatsby-d792', 'pythias-labs', 'app-renda-fixa', 'inrecovery',
    'snapcare', 'standuply', 'naiz-chat', 'klickly', 'fireflies-3#section-overview',
    'yobs-technologies-inc', 'togethar', 'savelist', 'keyrock',
    'coursedog', 'shipthis', 'interseller', 'nettrons', 'lexio',
    'buzi#section-overview', 'gamingmonk-entertainment', 'sprinkl-io',
    'scorebird', 'yastaa', 'headstart-app', 'droneentry-corporation',
    'zamphyr', 'wellochat', 'brainio', 'deciphex', 
    'jenyai', 'ujra', 'codeberry-programming-school',
    'planetwatchers', 'multibashi', 'auxxit', 'bellwethr',
    'twic-inc', 'discrash', 'activechat', 'tars', 'bbox-sports',
    'pitched', 'upcado', 'gangwaze', 'bulvrd', 'teamgrid',
    'donaid-8e7e', 'torrent-detective', 'bankfeeds-io',
    'zubale', 'retruster', 'crowdaa', 'standuply', 
    'droneios', 'authmetrik', 'stackraft', 'cover-technologies-inc',
    'snackpass', 'ticombo', 'pigpeg', 'stackml', 'squadcast-d690',
    'mongrov', 'cyber-skyline', 'trakbar', 'chief-io',
    'eddy-travels', 'nestrom'
]

# Base URL for Crunchbase organization pages
baseurl = 'https://www.crunchbase.com/organization/'

# ------------------------------
# Initialize Selenium WebDriver
# ------------------------------

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Randomize User-Agent
    user_agent = random.choice(AGENTS)
    chrome_options.add_argument(f'user-agent={user_agent}')
    
    # Setup ChromeDriver using Service and WebDriver Manager
    service = ChromeService(ChromeDriverManager().install())  # Automatically manages ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

# ------------------------------
# Safe Extraction Function
# ------------------------------

def safe_find(soup, tag, **kwargs):
    element = soup.find(tag, **kwargs)
    return element.get_text(strip=True) if element else ''

# ------------------------------
# Scraping Function
# ------------------------------

def scrape_crunchbase(driver, url):
    data = {
        'Name': '',
        'Description': '',
        'Funding': '',
        'Location': '',
        'Industry': '',
        'Stage': '',
        'Founding Date': '',
        'Website': '',
        'Number of Employees': '',
        'Headquarters Address': '',
        'Founders': '',
        'Key Executives': '',
        'Investors': '',
        'Acquisitions': '',
        'Products': '',
        'Competitors': '',
        'Revenue': '',
        'Last Funding Date': '',
        'Total Funding Amount': '',
        'Social Media Profiles': '',
        'Company Type': '',
        'Stock Exchange Listing': ''
    }
    
    try:
        driver.get(url)
        
        # Wait for the company name to be present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'profile-name'))
        )
        
        # Optional: Scroll to the bottom to load all dynamic content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))  # Short sleep to allow content to load
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # ------------------------------
        # Extract Company Name
        # ------------------------------
        data['Name'] = safe_find(soup, 'h1', class_='profile-name')
        
        # ------------------------------
        # Extract Description
        # ------------------------------
        data['Description'] = safe_find(soup, 'span', class_='component--field-formatter field-type-text_long ng-star-inserted')
        
        # ------------------------------
        # Extract Location
        # ------------------------------
        data['Location'] = safe_find(soup, 'span', class_='component--field-formatter field-type-identifier-multi')
        
        # ------------------------------
        # Extract Funding
        # ------------------------------
        funding_tag = soup.find('a', class_='cb-link component--field-formatter field-type-money ng-star-inserted')
        if funding_tag:
            data['Funding'] = funding_tag.get_text(strip=True)
        
        # ------------------------------
        # Extract Industry, Stage, Founding Date
        # ------------------------------
        section2 = soup.find('div', class_='layout-wrap layout-row')
        if section2:
            # Industry
            indus_tag = section2.find('identifier-multi-formatter', class_='ng-star-inserted')
            if indus_tag:
                data['Industry'] = indus_tag.get_text(strip=True)
            
            # Founding Date
            date_tag = section2.find('span', class_='component--field-formatter field-type-date_precision ng-star-inserted')
            if date_tag:
                data['Founding Date'] = date_tag.get_text(strip=True)
            
            # Funding Stage
            stage_tags = section2.find_all('span', class_='component--field-formatter field-type-enum ng-star-inserted')
            if len(stage_tags) > 1:
                data['Stage'] = stage_tags[1].get('title', '').strip()
        
        # ------------------------------
        # Extract Website URL
        # ------------------------------
        website_tag = soup.find('a', class_='component--field-formatter field-type-url ng-star-inserted')
        if website_tag:
            data['Website'] = website_tag.get('href', '').strip()
        
        # ------------------------------
        # Extract Number of Employees
        # ------------------------------
        emp_label = soup.find('span', string='Number of Employees')
        if emp_label:
            emp_value = emp_label.find_next('span', class_='component--field-formatter field-type-enum ng-star-inserted')
            if emp_value:
                data['Number of Employees'] = emp_value.get_text(strip=True)
        
        # ------------------------------
        # Extract Headquarters Address
        # ------------------------------
        hq_label = soup.find('span', string='Headquarters Address')
        if hq_label:
            hq_value = hq_label.find_next('span', class_='component--field-formatter field-type-address ng-star-inserted')
            if hq_value:
                data['Headquarters Address'] = hq_value.get_text(strip=True)
        
        # ------------------------------
        # Extract Founders
        # ------------------------------
        founders_section = soup.find('section', id='founders')
        if founders_section:
            founders = founders_section.find_all('a', class_='cb-link')
            founders_list = [founder.get_text(strip=True) for founder in founders]
            data['Founders'] = ', '.join(founders_list)
        
        # ------------------------------
        # Extract Key Executives
        # ------------------------------
        executives_section = soup.find('section', id='executives')
        if executives_section:
            executives = executives_section.find_all('a', class_='cb-link')
            executives_list = [exec.get_text(strip=True) for exec in executives]
            data['Key Executives'] = ', '.join(executives_list)
        
        # ------------------------------
        # Extract Investors
        # ------------------------------
        investors_section = soup.find('section', id='investors')
        if investors_section:
            investors = investors_section.find_all('a', class_='cb-link')
            investors_list = [inv.get_text(strip=True) for inv in investors]
            data['Investors'] = ', '.join(investors_list)
        
        # ------------------------------
        # Extract Acquisitions
        # ------------------------------
        acquisitions_section = soup.find('section', id='acquisitions')
        if acquisitions_section:
            acquisitions = acquisitions_section.find_all('a', class_='cb-link')
            acquisitions_list = [acq.get_text(strip=True) for acq in acquisitions]
            data['Acquisitions'] = ', '.join(acquisitions_list)
        
        # ------------------------------
        # Extract Products
        # ------------------------------
        products_section = soup.find('section', id='products')
        if products_section:
            products = products_section.find_all('a', class_='cb-link')
            products_list = [prod.get_text(strip=True) for prod in products]
            data['Products'] = ', '.join(products_list)
        
        # ------------------------------
        # Extract Competitors
        # ------------------------------
        competitors_section = soup.find('section', id='competitors')
        if competitors_section:
            competitors = competitors_section.find_all('a', class_='cb-link')
            competitors_list = [comp.get_text(strip=True) for comp in competitors]
            data['Competitors'] = ', '.join(competitors_list)
        
        # ------------------------------
        # Extract Revenue
        # ------------------------------
        revenue_label = soup.find('span', string='Revenue')
        if revenue_label:
            revenue_value = revenue_label.find_next('span', class_='component--field-formatter field-type-money ng-star-inserted')
            if revenue_value:
                data['Revenue'] = revenue_value.get_text(strip=True)
        
        # ------------------------------
        # Extract Last Funding Date
        # ------------------------------
        last_funding_label = soup.find('span', string='Last Funding Date')
        if last_funding_label:
            last_funding_value = last_funding_label.find_next('span', class_='component--field-formatter field-type-date ng-star-inserted')
            if last_funding_value:
                data['Last Funding Date'] = last_funding_value.get_text(strip=True)
        
        # ------------------------------
        # Extract Total Funding Amount
        # ------------------------------
        total_funding_label = soup.find('span', string='Total Funding Amount')
        if total_funding_label:
            total_funding_value = total_funding_label.find_next('span', class_='component--field-formatter field-type-money ng-star-inserted')
            if total_funding_value:
                data['Total Funding Amount'] = total_funding_value.get_text(strip=True)
        
        # ------------------------------
        # Extract Social Media Profiles
        # ------------------------------
        social_media_section = soup.find('div', class_='social-media-links')
        if social_media_section:
            social_links = social_media_section.find_all('a', class_='social-link')
            social_profiles = [link.get('href', '').strip() for link in social_links]
            data['Social Media Profiles'] = ', '.join(social_profiles)
        
        # ------------------------------
        # Extract Company Type
        # ------------------------------
        company_type_label = soup.find('span', string='Company Type')
        if company_type_label:
            company_type_value = company_type_label.find_next('span', class_='component--field-formatter field-type-enum ng-star-inserted')
            if company_type_value:
                data['Company Type'] = company_type_value.get_text(strip=True)
        
        # ------------------------------
        # Extract Stock Exchange Listing
        # ------------------------------
        stock_exchange_label = soup.find('span', string='Stock Exchange Listing')
        if stock_exchange_label:
            stock_exchange_value = stock_exchange_label.find_next('span', class_='component--field-formatter field-type-enum ng-star-inserted')
            if stock_exchange_value:
                data['Stock Exchange Listing'] = stock_exchange_value.get_text(strip=True)
        
        logging.info(f"Successfully scraped: {url}")
    
    except TimeoutException:
        logging.error(f"Timeout while loading page: {url}")
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
    
    return data

# ------------------------------
# Main Scraping Loop
# ------------------------------

def main():
    driver = init_driver()
    scraped_data = []
    
    # Define the limit for testing
    LIMIT = 10  # Number of entries to scrape for testing
    
    # Slice the page_id list to process only the first 'LIMIT' entries
    for idx, pid in enumerate(page_id[:LIMIT], start=1):
        # Construct the full URL
        url = baseurl + pid
        logging.info(f"Scraping ({idx}/{LIMIT}) URL: {url}")
        print(f"Scraping ({idx}/{LIMIT}) URL: {url}")
        
        # Scrape data
        data = scrape_crunchbase(driver, url)
        scraped_data.append(data)
        
        # Randomized delay to mimic human behavior
        sleep_time = random.uniform(5, 10)  # 5 to 10 seconds
        logging.info(f"Sleeping for {sleep_time:.2f} seconds...\n")
        print(f"Sleeping for {sleep_time:.2f} seconds...\n")
        time.sleep(sleep_time)
    
    # Close the driver
    driver.quit()
    logging.info("Closed the Selenium driver.")
    
    # ------------------------------
    # Save Data to CSV
    # ------------------------------
    df = pd.DataFrame(scraped_data, columns=[
        'Name', 'Description', 'Funding', 'Location', 'Industry', 'Stage', 
        'Founding Date', 'Website', 'Number of Employees', 'Headquarters Address',
        'Founders', 'Key Executives', 'Investors', 'Acquisitions', 'Products',
        'Competitors', 'Revenue', 'Last Funding Date', 'Total Funding Amount',
        'Social Media Profiles', 'Company Type', 'Stock Exchange Listing'
    ])
    df.to_csv('crunchbase_data.csv', index=False)
    logging.info("Scraping completed. Data saved to 'crunchbase_data.csv'.")
    print("Scraping completed. Data saved to 'crunchbase_data.csv'.")

# ------------------------------
# Execute the Script
# ------------------------------
if __name__ == "__main__":
    main()



# import pandas as pd
# import time
# import random
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from bs4 import BeautifulSoup
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager  # For automatic driver management

# # ------------------------------
# # Configuration and Setup
# # ------------------------------

# # List of randomized user agents
# AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
#     " Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
#     " Version/15.1 Safari/605.1.15",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
#     " Chrome/120.0.0.0 Safari/537.36",
#     # Add more user agents as needed
# ]

# # List of Crunchbase company identifiers
# page_id = [
#     'goally-llc', 'cloudtrack', 'planable-io', 'dynepic', 'learnt',
#     'players-lounge', 'maaxmarket', 'kinsu', 'bamboo', 
#     'many', 'thync', 'trekker', 'databook', 'fleetwit',
#     'jamieai', 'medbelle', 'amio-io', 'agnes-intelligence',
#     'hypefactors', 'botstar', '4tuna', 'zohunt', 'volumeet',
#     'greendeck', 'juntrax-solutions', 'urbanhire', 'triporate',
#     'synchronous-health', 'livescale', 'botsify', 'iostash',
#     'visualino-ug-haftungsbeschrankt', 'contentstudio', 'campsite-bio',
#     'retainly', 'pushbots', 'hoy', 'intelistyle', 'shopic',
#     'gatsby-d792', 'pythias-labs', 'app-renda-fixa', 'inrecovery',
#     'snapcare', 'standuply', 'naiz-chat', 'klickly', 'fireflies-3#section-overview',
#     'yobs-technologies-inc', 'togethar', 'savelist', 'keyrock',
#     'coursedog', 'shipthis', 'interseller', 'nettrons', 'lexio',
#     'buzi#section-overview', 'gamingmonk-entertainment', 'sprinkl-io',
#     'scorebird', 'yastaa', 'headstart-app', 'droneentry-corporation',
#     'zamphyr', 'wellochat', 'brainio', 'deciphex', 
#     'jenyai', 'ujra', 'codeberry-programming-school',
#     'planetwatchers', 'multibashi', 'auxxit', 'bellwethr',
#     'twic-inc', 'discrash', 'activechat', 'tars', 'bbox-sports',
#     'pitched', 'upcado', 'gangwaze', 'bulvrd', 'teamgrid',
#     'donaid-8e7e', 'torrent-detective', 'bankfeeds-io',
#     'zubale', 'retruster', 'crowdaa', 'standuply', 
#     'droneios', 'authmetrik', 'stackraft', 'cover-technologies-inc',
#     'snackpass', 'ticombo', 'pigpeg', 'stackml', 'squadcast-d690',
#     'mongrov', 'cyber-skyline', 'trakbar', 'chief-io',
#     'eddy-travels', 'nestrom'
# ]

# # Base URL for Crunchbase organization pages
# baseurl = 'https://www.crunchbase.com/organization/'

# # ------------------------------
# # Initialize Selenium WebDriver
# # ------------------------------

# def init_driver():
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")  # Run Chrome in headless mode
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--window-size=1920,1080")
    
#     # Randomize User-Agent
#     user_agent = random.choice(AGENTS)
#     chrome_options.add_argument(f'user-agent={user_agent}')
    
#     # Setup ChromeDriver using Service and WebDriver Manager
#     service = ChromeService(ChromeDriverManager().install())  # Automatically manages ChromeDriver
#     driver = webdriver.Chrome(service=service, options=chrome_options)
    
#     return driver

# # ------------------------------
# # Scraping Function
# # ------------------------------

# def scrape_crunchbase(driver, url):
#     data = {
#         'Name': '',
#         'Description': '',
#         'Funding': '',
#         'Location': '',
#         'Industry': '',
#         'Stage': '',
#         'Founding Date': '',
#         'Website': '',
#         'Number of Employees': '',
#         'Headquarters Address': '',
#         'Founders': '',
#         'Key Executives': '',
#         'Investors': '',
#         'Acquisitions': '',
#         'Products': '',
#         'Competitors': '',
#         'Revenue': '',
#         'Last Funding Date': '',
#         'Total Funding Amount': '',
#         'Social Media Profiles': '',
#         'Company Type': '',
#         'Stock Exchange Listing': ''
#     }
    
#     try:
#         driver.get(url)
#         # Wait for the page to load completely
#         time.sleep(random.uniform(5, 7))  # Adjust as necessary
        
#         # Get page source and parse with BeautifulSoup
#         soup = BeautifulSoup(driver.page_source, 'html.parser')
        
#         # ------------------------------
#         # Extract Company Name
#         # ------------------------------
#         name_tag = soup.find('h1', class_='profile-name')
#         if name_tag:
#             data['Name'] = name_tag.get_text(strip=True)
        
#         # ------------------------------
#         # Extract Description
#         # ------------------------------
#         descrip_tag = soup.find('span', class_='component--field-formatter field-type-text_long ng-star-inserted')
#         if descrip_tag:
#             data['Description'] = descrip_tag.get_text(strip=True)
        
#         # ------------------------------
#         # Extract Location
#         # ------------------------------
#         loca_tag = soup.find('span', class_='component--field-formatter field-type-identifier-multi')
#         if loca_tag:
#             data['Location'] = loca_tag.get_text(strip=True)
        
#         # ------------------------------
#         # Extract Funding
#         # ------------------------------
#         fund_tag = soup.find('a', class_='cb-link component--field-formatter field-type-money ng-star-inserted')
#         if fund_tag:
#             data['Funding'] = fund_tag.get_text(strip=True)
        
#         # ------------------------------
#         # Extract Industry, Stage, Founding Date
#         # ------------------------------
#         section2 = soup.find('div', class_='layout-wrap layout-row')
#         if section2:
#             # Industry
#             indus_tag = section2.find('identifier-multi-formatter', class_='ng-star-inserted')
#             if indus_tag:
#                 data['Industry'] = indus_tag.get_text(strip=True)
            
#             # Founding Date
#             date_tag = section2.find('span', class_='component--field-formatter field-type-date_precision ng-star-inserted')
#             if date_tag:
#                 data['Founding Date'] = date_tag.get_text(strip=True)
            
#             # Funding Stage
#             stage_tags = section2.find_all('span', class_='component--field-formatter field-type-enum ng-star-inserted')
#             if len(stage_tags) > 1:
#                 data['Stage'] = stage_tags[1].get('title', '').strip()
        
#         # ------------------------------
#         # Extract Website URL
#         # ------------------------------
#         website_tag = soup.find('a', class_='component--field-formatter field-type-url ng-star-inserted')
#         if website_tag:
#             data['Website'] = website_tag.get('href', '').strip()
        
#         # ------------------------------
#         # Extract Number of Employees
#         # ------------------------------
#         emp_label = soup.find('span', text='Number of Employees')
#         if emp_label:
#             emp_value = emp_label.find_next('span', class_='component--field-formatter field-type-enum ng-star-inserted')
#             if emp_value:
#                 data['Number of Employees'] = emp_value.get_text(strip=True)
        
#         # ------------------------------
#         # Extract Headquarters Address
#         # ------------------------------
#         hq_label = soup.find('span', text='Headquarters Address')
#         if hq_label:
#             hq_value = hq_label.find_next('span', class_='component--field-formatter field-type-address ng-star-inserted')
#             if hq_value:
#                 data['Headquarters Address'] = hq_value.get_text(strip=True)
        
#         # ------------------------------
#         # Extract Founders
#         # ------------------------------
#         founders_section = soup.find('section', id='founders')
#         if founders_section:
#             founders = founders_section.find_all('a', class_='cb-link')
#             founders_list = [founder.get_text(strip=True) for founder in founders]
#             data['Founders'] = ', '.join(founders_list)
        
#         # ------------------------------
#         # Extract Key Executives
#         # ------------------------------
#         executives_section = soup.find('section', id='executives')
#         if executives_section:
#             executives = executives_section.find_all('a', class_='cb-link')
#             executives_list = [exec.get_text(strip=True) for exec in executives]
#             data['Key Executives'] = ', '.join(executives_list)
        
#         # ------------------------------
#         # Extract Investors
#         # ------------------------------
#         investors_section = soup.find('section', id='investors')
#         if investors_section:
#             investors = investors_section.find_all('a', class_='cb-link')
#             investors_list = [inv.get_text(strip=True) for inv in investors]
#             data['Investors'] = ', '.join(investors_list)
        
#         # ------------------------------
#         # Extract Acquisitions
#         # ------------------------------
#         acquisitions_section = soup.find('section', id='acquisitions')
#         if acquisitions_section:
#             acquisitions = acquisitions_section.find_all('a', class_='cb-link')
#             acquisitions_list = [acq.get_text(strip=True) for acq in acquisitions]
#             data['Acquisitions'] = ', '.join(acquisitions_list)
        
#         # ------------------------------
#         # Extract Products
#         # ------------------------------
#         products_section = soup.find('section', id='products')
#         if products_section:
#             products = products_section.find_all('a', class_='cb-link')
#             products_list = [prod.get_text(strip=True) for prod in products]
#             data['Products'] = ', '.join(products_list)
        
#         # ------------------------------
#         # Extract Competitors
#         # ------------------------------
#         competitors_section = soup.find('section', id='competitors')
#         if competitors_section:
#             competitors = competitors_section.find_all('a', class_='cb-link')
#             competitors_list = [comp.get_text(strip=True) for comp in competitors]
#             data['Competitors'] = ', '.join(competitors_list)
        
#         # ------------------------------
#         # Extract Revenue
#         # ------------------------------
#         revenue_label = soup.find('span', text='Revenue')
#         if revenue_label:
#             revenue_value = revenue_label.find_next('span', class_='component--field-formatter field-type-money ng-star-inserted')
#             if revenue_value:
#                 data['Revenue'] = revenue_value.get_text(strip=True)
        
#         # ------------------------------
#         # Extract Last Funding Date
#         # ------------------------------
#         last_funding_label = soup.find('span', text='Last Funding Date')
#         if last_funding_label:
#             last_funding_value = last_funding_label.find_next('span', class_='component--field-formatter field-type-date ng-star-inserted')
#             if last_funding_value:
#                 data['Last Funding Date'] = last_funding_value.get_text(strip=True)
        
#         # ------------------------------
#         # Extract Total Funding Amount
#         # ------------------------------
#         total_funding_label = soup.find('span', text='Total Funding Amount')
#         if total_funding_label:
#             total_funding_value = total_funding_label.find_next('span', class_='component--field-formatter field-type-money ng-star-inserted')
#             if total_funding_value:
#                 data['Total Funding Amount'] = total_funding_value.get_text(strip=True)
        
#         # ------------------------------
#         # Extract Social Media Profiles
#         # ------------------------------
#         social_media_section = soup.find('div', class_='social-media-links')
#         if social_media_section:
#             social_links = social_media_section.find_all('a', class_='social-link')
#             social_profiles = [link.get('href', '').strip() for link in social_links]
#             data['Social Media Profiles'] = ', '.join(social_profiles)
        
#         # ------------------------------
#         # Extract Company Type
#         # ------------------------------
#         company_type_label = soup.find('span', text='Company Type')
#         if company_type_label:
#             company_type_value = company_type_label.find_next('span', class_='component--field-formatter field-type-enum ng-star-inserted')
#             if company_type_value:
#                 data['Company Type'] = company_type_value.get_text(strip=True)
        
#         # ------------------------------
#         # Extract Stock Exchange Listing
#         # ------------------------------
#         stock_exchange_label = soup.find('span', text='Stock Exchange Listing')
#         if stock_exchange_label:
#             stock_exchange_value = stock_exchange_label.find_next('span', class_='component--field-formatter field-type-enum ng-star-inserted')
#             if stock_exchange_value:
#                 data['Stock Exchange Listing'] = stock_exchange_value.get_text(strip=True)
        
#     except TimeoutException:
#         print(f"Timeout while loading page: {url}")
#     except Exception as e:
#         print(f"Error scraping {url}: {e}")
    
#     return data

# # ------------------------------
# # Main Scraping Loop
# # ------------------------------

# def main():
#     driver = init_driver()
#     scraped_data = []
    
#     for pid in page_id:
#         # Construct the full URL
#         url = baseurl + pid
#         print(f"Scraping URL: {url}")
        
#         # Scrape data
#         data = scrape_crunchbase(driver, url)
#         scraped_data.append(data)
        
#         # Randomized delay to mimic human behavior
#         sleep_time = random.uniform(5, 10)  # 5 to 10 seconds
#         print(f"Sleeping for {sleep_time:.2f} seconds...\n")
#         time.sleep(sleep_time)
    
#     # Close the driver
#     driver.quit()
    
#     # ------------------------------
#     # Save Data to CSV
#     # ------------------------------
#     df = pd.DataFrame(scraped_data, columns=[
#         'Name', 'Description', 'Funding', 'Location', 'Industry', 'Stage', 
#         'Founding Date', 'Website', 'Number of Employees', 'Headquarters Address',
#         'Founders', 'Key Executives', 'Investors', 'Acquisitions', 'Products',
#         'Competitors', 'Revenue', 'Last Funding Date', 'Total Funding Amount',
#         'Social Media Profiles', 'Company Type', 'Stock Exchange Listing'
#     ])
#     df.to_csv('crunchbase_data.csv', index=False)
#     print("Scraping completed. Data saved to 'crunchbase_data.csv'.")

# # ------------------------------
# # Execute the Script
# # ------------------------------
# if __name__ == "__main__":
#     main()
