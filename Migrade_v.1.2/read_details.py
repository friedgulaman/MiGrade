from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID of your Google Sheet.
SAMPLE_SPREADSHEET_ID = '1UKj2k_prPb8rC0sa_shnuSVZClI_0_iCd1p6zmbWxx8'

service = build('sheets', 'v4', credentials=creds)

# Define the existing sheet's name
existing_sheet_name = "SF1"  # Replace with the name of your existing sheet

# Function to retrieve values from the sheet and store rows 1 to 5 without empty fields in a list
def get_rows(sheet_values):
    rows_list = []

    for i in range(5):
        if i < len(sheet_values):
            row = sheet_values[i]
            non_empty_values = [value.strip() for value in row if value.strip() != '']
            rows_list.append(non_empty_values)
        else:
            rows_list.append([])

    return rows_list

# Get the values from the existing sheet
existing_sheet_values = service.spreadsheets().values().get(
    spreadsheetId=SAMPLE_SPREADSHEET_ID,
    range=f"{existing_sheet_name}!A1:ZZ5",
).execute().get('values', [])

if existing_sheet_values:
    rows_list = get_rows(existing_sheet_values)
    
    # Define the terms to look for
    terms_to_find = ["School ID", "School Name", "Division", "District", "School Year", "Grade Level", "Section"]

    # Create a dictionary to store key-value pairs
    data_dict = {}
    
    # Iterate through rows and check for specified terms
    for i, row in enumerate(rows_list, start=1):
        for term in terms_to_find:
            if term in row:
                index = row.index(term)
                if index + 1 < len(row):  # Ensure there is a value next to the term
                    data_dict[term] = row[index + 1]
                else:
                    data_dict[term] = None
    
    # Print the resulting dictionary
    print("Key-Value Pairs:")
    for key, value in data_dict.items():
        print(f"{key}: {value}")
else:
    print(f"Could not find the existing sheet named '{existing_sheet_name}'.")
