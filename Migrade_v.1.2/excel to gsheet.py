import pandas as pd
import gspread
from google.auth import exceptions
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Set up Google Sheets API credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# Use an absolute path to the JSON key file
credentials = service_account.Credentials.from_service_account_file('keys.json', scopes=scope)
gc = gspread.authorize(credentials)

# Load your Excel file into a pandas DataFrame
excel_file_path = 'SF1_2023_Grade-1-JACINTO (1).xlsx'
df = pd.read_excel(excel_file_path)

# Create a new Google Sheets file
gsheet = gc.create('New Google Sheet')  # You can specify the name

# Select the default worksheet
worksheet = gsheet.get_worksheet(0)

# Update the Google Sheets file with data from the pandas DataFrame
for i, row in enumerate(df.values):
    worksheet.insert_row(list(row), i + 2)

# Get the email address of the service account
service_account_email = credentials.service_account_email

# Share the Google Sheets file with the service account
gsheet.share(service_account_email, perm_type='user', role='writer')

print(f"Excel file '{excel_file_path}' has been successfully converted to Google Sheets.")
print(f"Google Sheets file created: {gsheet.url}")
print(f"Google Sheets file shared with service account: {service_account_email}")
