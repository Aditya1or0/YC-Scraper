import requests
from bs4 import BeautifulSoup
import json
import html
import time
from tqdm import tqdm
import os

# Function to extract company data from a single company URL
def extract_company_data(company_url, headers):
    response = requests.get(company_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to load company page {company_url} (Status code: {response.status_code})")
        return None
    
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract the data-page div
    data_page_div = soup.find('div', attrs={'data-page': True})
    if not data_page_div:
        print(f"Couldn't find the data-page div in the company page: {company_url}")
        return None
    
    # The data-page attribute contains HTML-encoded JSON
    data_page_json_str = data_page_div['data-page']
    # Unescape HTML entities
    data_page_json_str = html.unescape(data_page_json_str)
    
    # Parse the JSON string
    try:
        data_page = json.loads(data_page_json_str)
    except json.JSONDecodeError as e:
        print(f"JSON decoding failed for {company_url}: {e}")
        return None
    
    # Structure the data
    company_info = {
        "name": data_page.get("props", {}).get("company", {}).get("name"),
        "one_liner": data_page.get("props", {}).get("company", {}).get("one_liner"),
        "website": data_page.get("props", {}).get("company", {}).get("website"),
        "long_description": data_page.get("props", {}).get("company", {}).get("long_description"),
        "mission": data_page.get("props", {}).get("company", {}).get("mission"),
        "key_details": {
            "batch_name": data_page.get("props", {}).get("company", {}).get("batch_name"),
            "year_founded": data_page.get("props", {}).get("company", {}).get("year_founded"),
            "team_size": data_page.get("props", {}).get("company", {}).get("team_size"),
            "location": data_page.get("props", {}).get("company", {}).get("location"),
            "city": data_page.get("props", {}).get("company", {}).get("city"),
            "country": data_page.get("props", {}).get("company", {}).get("country"),
        },
        "founders": [],
        "latest_news": [],
        "social_media": {
            "linkedin": data_page.get("props", {}).get("company", {}).get("linkedin_url"),
            "twitter": data_page.get("props", {}).get("company", {}).get("twitter_url"),
            "facebook": data_page.get("props", {}).get("company", {}).get("fb_url"),
            "crunchbase": data_page.get("props", {}).get("company", {}).get("cb_url"),
            # Add other social media links if available
        },
        "footer_info": {}  # Placeholder for future extraction
    }
    
    # Extract Founders Information
    founders_data = data_page.get("props", {}).get("company", {}).get("founders", [])
    for founder in founders_data:
        founder_info = {
            "full_name": founder.get("full_name"),
            "title": founder.get("title"),
            "bio": founder.get("founder_bio"),
            "social_links": {
                "twitter": founder.get("twitter_url"),
                "linkedin": founder.get("linkedin_url"),
            }
        }
        company_info["founders"].append(founder_info)
    
    # Extract Latest News from data-page JSON
    news_data = data_page.get("props", {}).get("company", {}).get("newsItems", [])
    
    for news in news_data:
        news_item = {
            "title": news.get("title"),
            "url": news.get("url"),
            "date": news.get("date")
        }
        company_info["latest_news"].append(news_item)
    
    # Fetch Latest News from newsUrl if available
    news_url = data_page.get("props", {}).get("company", {}).get("newsUrl")
    if news_url:
        # Complete the news_url if it's relative
        if news_url.startswith("/"):
            news_url = "https://www.ycombinator.com" + news_url
        news_response = requests.get(news_url, headers=headers)
        if news_response.status_code == 200:
            try:
                # Assuming the response is JSON
                additional_news_data = news_response.json()
                # Check if 'newsItems' exists
                if 'newsItems' in additional_news_data:
                    for news in additional_news_data['newsItems']:
                        # Avoid duplicates
                        if news.get("url") not in [item['url'] for item in company_info["latest_news"]]:
                            news_item = {
                                "title": news.get("title"),
                                "url": news.get("url"),
                                "date": news.get("date")
                            }
                            company_info["latest_news"].append(news_item)
                else:
                    print(f"No 'newsItems' found in newsUrl response for {company_url}")
            except json.JSONDecodeError:
                print(f"Failed to decode JSON from newsUrl response for {company_url}")
        else:
            print(f"Failed to fetch news from {news_url} (Status code: {news_response.status_code})")
    
    return company_info

# Function to extract all company URLs from the companies directory page
def get_all_company_urls(directory_url, headers, max_companies=None):
    response = requests.get(directory_url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to load directory page {directory_url} (Status code: {response.status_code})")
    
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract the data-page div
    data_page_div = soup.find('div', attrs={'data-page': True})
    if not data_page_div:
        raise Exception("Couldn't find the data-page div in the directory page.")
    
    # The data-page attribute contains HTML-encoded JSON
    data_page_json_str = data_page_div['data-page']
    # Unescape HTML entities
    data_page_json_str = html.unescape(data_page_json_str)
    
    # Parse the JSON string
    try:
        data_page = json.loads(data_page_json_str)
    except json.JSONDecodeError as e:
        raise Exception(f"JSON decoding failed for directory page: {e}")
    
    # Extract companies list
    companies = data_page.get("props", {}).get("companies", {}).get("list", [])
    
    company_urls = []
    for company in companies:
        # Assuming each company has a 'url' field
        url = company.get("url")
        if url:
            # Complete the URL if it's relative
            if url.startswith("/"):
                url = "https://www.ycombinator.com" + url
            company_urls.append(url)
            # If max_companies is set and reached, stop
            if max_companies and len(company_urls) >= max_companies:
                break
    
    return company_urls

def main():
    # Directory URL
    directory_url = "https://www.ycombinator.com/companies"
    
    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DataExtractionBot/1.0)"
    }
    
    # Read company URLs from 'company_urls.json' generated by Puppeteer
    urls_file = 'filtered_company_urls.json'
    if not os.path.exists(urls_file):
        print(f"Error: '{urls_file}' not found. Please run the Puppeteer script first to generate this file.")
        return
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        try:
            company_urls = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding '{urls_file}': {e}")
            return
    
    print(f"Found {len(company_urls)} company URLs.")

    # List to hold all company data
    all_companies_data = []
    
    # Iterate through each company URL and extract data
    for company_url in tqdm(company_urls, desc="Processing Companies"):
        company_data = extract_company_data(company_url, headers)
        if company_data:
            all_companies_data.append(company_data)
        # Be polite and avoid hammering the server
        time.sleep(1)  # Adjust delay as needed
    
    # Save all data to a single JSON file
    output_file = 'yc_companies_data.json'  # Final output file
    
    # Check if the file exists to avoid overwriting
    if os.path.exists(output_file):
        # Optionally, append to the existing file or handle duplicates based on 'website'
        with open(output_file, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
        # Combine existing data with new data, avoiding duplicates based on 'website'
        existing_urls = set(company['website'] for company in existing_data if company.get('website'))
        new_data = [company for company in all_companies_data if company.get('website') not in existing_urls]
        combined_data = existing_data + new_data
    else:
        combined_data = all_companies_data
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=4, ensure_ascii=False)
    
    print(f"Data extraction complete. JSON data saved to '{output_file}'.")

if __name__ == "__main__":
    main()
