from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID of your Google Sheet.
SAMPLE_SPREADSHEET_ID = '1ROX5689XMB2qkXP3ou144w1kJGOflz0f1SSrfFc92SY'

service = build('sheets', 'v4', credentials=creds)

# Define the existing sheet's name
existing_sheet_name = "FRONT"  # Replace with the name of your existing sheet

# The value you want to write to cell F13
value_to_write = "maam gina"

# Define the range in A1 notation (F13 in this case)
range_name = existing_sheet_name + "!E9:M9"

# Create the request body to update the value
request_body = {
    'values': [[value_to_write]]
}

# Execute the request to update the value in cell F13
result = service.spreadsheets().values().update(
    spreadsheetId=SAMPLE_SPREADSHEET_ID,
    range=range_name,
    valueInputOption="RAW",
    body=request_body
).execute()

print(f"Updated {result['updatedCells']} cells with the value: {value_to_write}")
