# YC Companies Data Scraper

This project is a web scraping utility designed to extract detailed information about companies from the Y Combinator website, storing the data in JSON format and providing options to export it into a CSV file for further analysis.

## Features
- Scrapes company names, one-liners, websites, descriptions, and key details such as team size, location, and more.
- Dynamically extracts details for up to a specified number of founders, including names, titles, bios, and social media links.
- Exports scraped data into a structured CSV file, ensuring all relevant information (company data, founder details) is available in a flat table format.
- Allows easy conversion of JSON data into CSV format.

## Requirements
- Python 3.x
- Node.js
- Puppeteer
- Python dependencies: BeautifulSoup, requests, tqdm, json, csv

## Installation

### Clone the Repository

```bash
git clone https://github.com/akhan2000/YC-Scraper
cd yc-companies-scraper
npm install puppeteer
pip install requests beautifulsoup4 tqdm
```

## Usage
Step 1: Scrape Company URLs
The first step is to use the Puppeteer script to scrape all the company URLs from the YC directory.

Run the Puppeteer Script
This script scrapes the company URLs from the Y Combinator companies directory and saves them to a file (company_urls.json):

```bash
node scrape_yc_companies.js
```
This script will create a file called company_urls.json that contains the URLs of all companies listed on the YC directory.

Step 2: Scrape Company Data
Once the company URLs are obtained, the Python script will scrape detailed data for each company and save it in JSON format.

Run the Python Script
After obtaining the company URLs, use the Python script to scrape detailed data about each company:

```bash
python scrape_yc_data.py
```
This script will generate a file called yc_companies_data.json that contains all the detailed information for each company.

Step 3: Convert JSON to CSV
To export the scraped data into a CSV format for analysis:

Run the JSON to CSV Conversion
The Python script can also convert the JSON data into a CSV file:

```bash
python json_to_csv.py
```
The resulting CSV file (yc_companies_data.csv) will contain all the company data, including founder information in separate columns (e.g., founder_1_name, founder_1_twitter).

## CSV Structure
- The CSV file will have the following column structure:

- name: Company name
- one_liner: Short company description
- website: Company website URL
- long_description: Full description of the company
- mission: Company mission statement
- key_details.batch_name: Y Combinator batch name
- key_details.year_founded: Year the company was founded
- key_details.team_size: Team size
- key_details.location: Location of the company
- key_details.city: City where the company is located
- key_details.country: Country of the company
- social_media.linkedin: LinkedIn URL
- social_media.twitter: Twitter URL
- social_media.facebook: Facebook URL
- social_media.crunchbase: Crunchbase URL
- founder_1_name, founder_1_title, founder_1_bio, founder_1_twitter, founder_1_linkedin: Details of the first founder
- founder_2_name, founder_2_title, founder_2_bio, founder_2_twitter, founder_2_linkedin: Details of the second founder
- (and so on for more founders up to a specified number)

## Customization
- Max Founders: You can customize the maximum number of founders stored by modifying the MAX_FOUNDERS variable in the Python script.
- Sleep Time: The delay between requests in the Python scraper is set to 1 second to avoid overwhelming the server. You can adjust the time.sleep(1) call in the script as needed.

## Future Improvements
- Add error handling for potential edge cases.
- Implement database storage (e.g., PostgreSQL) for scalable querying and better integration.
- Automate the entire scraping and conversion process into a streamlined pipeline.
