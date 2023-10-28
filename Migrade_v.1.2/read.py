from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID of your Google Sheet.
SAMPLE_SPREADSHEET_ID = '1UKj2k_prPb8rC0sa_shnuSVZClI_0_iCd1p6zmbWxx8'

service = build('sheets', 'v4', credentials=creds)

# Define the existing sheet's name
existing_sheet_name = "SF1"  # Replace with the name of your existing sheet

# Function to retrieve values from the sheet
def get_sheet_values(sheet_id, start_range, end_range):
    result = service.spreadsheets().values().get(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=f"{sheet_id}!{start_range}:{end_range}",
    ).execute()
    values = result.get('values', [])
    return values

# Function to find LRN and store row data with LRN as a dictionary
def find_lrn_and_store_as_dict(sheet_values):
    lrn_row_index = None
    lrn_col_index = None
    lrn_data = {}  # Initialize an empty dictionary to store LRN data
    
    for i, row in enumerate(sheet_values):
        if "LRN" in row:
            lrn_row_index = i
            lrn_col_index = row.index("LRN")
            break
    
    if lrn_row_index is not None:
        current_lrn = None
        
        for i in range(lrn_row_index + 1, len(sheet_values)):
            row = sheet_values[i]
            if lrn_col_index < len(row):
                lrn_value = row[lrn_col_index]
                if len(lrn_value) == 12 and lrn_value.isdigit():
                    current_lrn = lrn_value
                    lrn_data[current_lrn] = []  # Initialize an empty list for the LRN
                else:
                    current_lrn = None  # Reset current LRN if it's not 12 digits
                    
                if current_lrn:
                    non_empty_fields = [field for field in row if field.strip() != '']
                    lrn_data[current_lrn].append(non_empty_fields)  # Append non-empty fields to the LRN
                    
        return lrn_data
    else:
        print("Cell containing 'LRN' not found in the sheet.")
        return lrn_data  # Return an empty dictionary if no LRN cell is found


# Get the values from the existing sheet
existing_sheet_values = get_sheet_values(existing_sheet_name, "A1", "ZZ1000")

if existing_sheet_values:
    lrn_data = find_lrn_and_store_as_dict(existing_sheet_values)
    
    # Filter for LRNs with 12 numbers
    valid_lrns = [lrn for lrn in lrn_data if len(lrn) == 12 and lrn.isdigit()]
    
    # Define the keys you want for each LRN
    keys = ["LRN", "Name", "Sex", "Birthday"]
    
    
    for lrn in valid_lrns:
        if lrn in lrn_data:
            associated_rows = lrn_data[lrn]
            for row in associated_rows:
               for key, value in zip(keys, row):
                print(f"{key}: {value}")
        else:
            print(f"Could not find the existing sheet named '{existing_sheet_name}'.")
