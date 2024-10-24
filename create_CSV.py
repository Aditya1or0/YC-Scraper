import json
import csv

# Load your JSON data
with open('yc_companies_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Set maximum number of founders to handle
MAX_FOUNDERS = 5  # You can change this as needed

# Open a single CSV file for writing
with open('yc_companies_data.csv', 'w', newline='', encoding='utf-8') as csv_file:

    # Define CSV writer
    csv_writer = csv.writer(csv_file)

    # Write headers for the CSV
    headers = [
        'name', 'one_liner', 'website', 'long_description', 'mission',
        'batch_name', 'year_founded', 'team_size', 'location', 'city', 'country',
        'linkedin', 'twitter', 'facebook', 'crunchbase'
    ]

    # Dynamically add headers for founders
    for i in range(1, MAX_FOUNDERS + 1):
        headers.extend([
            f'founder_{i}_name', f'founder_{i}_title', f'founder_{i}_bio',
            f'founder_{i}_twitter', f'founder_{i}_linkedin'
        ])

    # Write the header row to the CSV
    csv_writer.writerow(headers)

    # Loop through the companies in the JSON data
    for company in data:
        # Extract company data
        row = [
            company.get('name'),
            company.get('one_liner'),
            company.get('website'),
            company.get('long_description'),
            company.get('mission'),
            company.get('key_details', {}).get('batch_name'),
            company.get('key_details', {}).get('year_founded'),
            company.get('key_details', {}).get('team_size'),
            company.get('key_details', {}).get('location'),
            company.get('key_details', {}).get('city'),
            company.get('key_details', {}).get('country'),
            company.get('social_media', {}).get('linkedin'),
            company.get('social_media', {}).get('twitter'),
            company.get('social_media', {}).get('facebook'),
            company.get('social_media', {}).get('crunchbase')
        ]

        # Add founders data
        founders = company.get('founders', [])
        for i in range(MAX_FOUNDERS):
            if i < len(founders):
                row.extend([
                    founders[i].get('full_name', ''),
                    founders[i].get('title', ''),
                    founders[i].get('bio', ''),
                    founders[i].get('social_links', {}).get('twitter', ''),
                    founders[i].get('social_links', {}).get('linkedin', '')
                ])
            else:
                # If fewer founders than MAX_FOUNDERS, fill with empty strings
                row.extend(['', '', '', '', ''])

        # Write the row to the CSV
        csv_writer.writerow(row)
