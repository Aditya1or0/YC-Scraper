import json
import pandas as pd
from openpyxl import load_workbook
import os

# Load the JSON data
with open('yc_companies_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract required fields
rows = []
for company in data:
    company_name = company.get("name")
    website = company.get("website")
    linkedin_company = company.get("social_media", {}).get("linkedin")

    for founder in company.get("founders", []):
        founder_name = founder.get("full_name")
        founder_linkedin = founder.get("social_links", {}).get("linkedin")
        founder_twitter = founder.get("social_links", {}).get("twitter")

        rows.append({
            "Company Name": company_name,
            "Website": website,
            "LinkedIn (Company)": linkedin_company,
            "Founder Name": founder_name,
            "Founder LinkedIn": founder_linkedin,
            "Founder Twitter": founder_twitter
        })

# Convert to DataFrame
df = pd.DataFrame(rows)

# Define filename
excel_filename = 'yc_companies_filtered.xlsx'

# Handle overwrite if file is in use
if os.path.exists(excel_filename):
    try:
        os.remove(excel_filename)
    except PermissionError:
        print(f"⚠️ Please close '{excel_filename}' and run the script again.")
        exit()

# Save to Excel
df.to_excel(excel_filename, index=False)

# Adjust column widths
wb = load_workbook(excel_filename)
ws = wb.active

# Set reasonable column widths for readability
column_widths = {
    'A': 30,  # Company Name
    'B': 45,  # Website
    'C': 50,  # LinkedIn (Company)
    'D': 25,  # Founder Name
    'E': 50,  # Founder LinkedIn
    'F': 40   # Founder Twitter
}

for col, width in column_widths.items():
    ws.column_dimensions[col].width = width

wb.save(excel_filename)

print(f" Excel file '{excel_filename}' created successfully with founder social links.")
