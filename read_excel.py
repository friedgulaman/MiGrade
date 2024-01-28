import openpyxl

def find_learner_names_and_store_as_dict(sheet_values, search_value):
    learner_name_row_index = None
    learner_name_col_index = None
    learner_name_data = {}  # Initialize an empty dictionary to store LEARNER'S NAME data

    # Find the row and column indices for the search value
    for i, row in enumerate(sheet_values):
        if search_value in row:
            learner_name_row_index = i
            learner_name_col_index = row.index(search_value)
            break

    if learner_name_row_index is not None:
        current_lrn = None

        # Iterate over rows below the row containing the search value
        for i in range(learner_name_row_index + 1, len(sheet_values)):
            row = sheet_values[i]

            # Ensure that the column index exists for each row
            if learner_name_col_index < len(row):
                learner_name_value = row[learner_name_col_index]

                # Check if the cell is not empty or whitespace
                if learner_name_value is not None and str(learner_name_value).strip() != '':
                    current_lrn = learner_name_value
                    learner_name_data[current_lrn] = []  # Initialize an empty list for the LEARNER'S NAME
                else:
                    current_lrn = None  # Reset current LEARNER'S NAME if it's empty

                if current_lrn:
                    # Append non-empty fields to the LEARNER'S NAME
                    non_empty_fields = [field for field in row if field is not None and str(field).strip() != '']
                    learner_name_data[current_lrn].append(non_empty_fields)

        return learner_name_data
    else:
        print(f"Cell containing '{search_value}' not found in the sheet.")
        return learner_name_data  # Return an empty dictionary if no LEARNER'S NAME cell is found

# Example usage with search value "LEARNER'S NAME"
file_path = 'SAMPLE_CLASS_RECORD.xlsx'  # Replace with the actual path to your Excel file
search_value = "LEARNER'S NAME"
workbook = openpyxl.load_workbook(file_path)
sheet = workbook.active
sheet_values = [list(row) for row in sheet.iter_rows(values_only=True)]

# Debugging: Print the entire sheet_values
print("Sheet Values:")
for row in sheet_values:
    print(row)

# Use the function to find and store LEARNER'S NAME data
learner_name_data = find_learner_names_and_store_as_dict(sheet_values, search_value)                                 

# Debugging: Print the result
print("\nResult:")
for learner_name, fields in learner_name_data.items():
    print(f"LEARNER'S NAME: {learner_name}")
    print(f"Fields: {fields}")
    print("------------------------")
