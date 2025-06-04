import csv
import io

def transform_csv_with_ids(input_csv_content, tag_name_to_id_mapping):
    """
    Transforms CSV data into a four-column format for readability:
    tagkey_id, tagkey_name, tagvalue, metadata.

    Args:
        input_csv_content (str): A string containing the content of the input CSV.
        tag_name_to_id_mapping (dict): A dictionary mapping tag display names 
                                       (from CSV headers) to their unique IDs.

    Returns:
        str: A string containing the transformed data in CSV format, or an
             error message if a mapping is missing.
    """
    # Use io.StringIO to treat the string input_csv_content as a file
    input_file = io.StringIO(input_csv_content)
    reader = csv.reader(input_file)

    # Read the header row to get the tag names
    try:
        # The first column header is our metadata column (e.g., 'project_number')
        metadata_header = next(reader)[0] 
        # Rewind the file to process headers again with the data
        input_file.seek(0)
        # Get all tag name headers, skipping the first column
        tag_name_headers = next(reader)[1:]
    except StopIteration:
        return "Error: CSV file is empty or has no headers."

    # Validate that all headers from the CSV have a corresponding ID in the mapping
    missing_keys = [header for header in tag_name_headers if header.strip() and header not in tag_name_to_id_mapping]
    if missing_keys:
        return f"Error: Missing ID mapping for the following Tag Names: {', '.join(missing_keys)}"

    output_rows = []
    # Add the header for the new output format, with 'metadata' as the last column
    output_rows.append(['tagkey_id', 'tagkey_name', 'tagvalue', 'metadata'])

    # Process each data row from the input CSV
    # We already skipped the header, so the reader is at the first data row
    input_file.seek(0) # Rewind to read from the beginning
    next(reader) # Skip header row again
    
    for row in reader:
        if not row or not any(field.strip() for field in row):  # Skip empty or all-whitespace rows
            continue

        if len(row) < 1:
            continue
            
        metadata_value = row[0]
        if not metadata_value.strip(): # Skip if metadata value (project_number) is missing
            continue
            
        tag_values = row[1:] # Get all values corresponding to the tag headers

        # Iterate through the headers and their corresponding values
        for i, tag_name in enumerate(tag_name_headers):
            if i < len(tag_values):
                tag_value = tag_values[i]
                if tag_value.strip(): # Only process if there is a value
                    # Look up the tag ID from the mapping dictionary
                    tag_id = tag_name_to_id_mapping[tag_name]
                    # Append the new four-column row with metadata (project_number) at the end
                    output_rows.append([tag_id, tag_name, tag_value, metadata_value])

    # Convert the list of output rows back to a CSV formatted string
    output_file = io.StringIO()
    writer = csv.writer(output_file)
    writer.writerows(output_rows)
    
    return output_file.getvalue()

# --- Example Usage ---

# 1. First, you would run 'gcloud resource-manager tags keys list ...' in your
#    terminal to get the mapping between display names and their IDs.

# 2. Populate this dictionary with your actual data.
#    The key is the column header from your CSV (the display name).
#    The value is the numeric ID from the 'name' field (e.g., the '123456789012' from 'tagKeys/123456789012').
TAG_NAME_TO_ID_MAPPING = {
    "Directorate in BQ": "111222333444",
    "Project  in BQ": "222333444555",
    "Shared in BQ": "333444555666",
    "directorate": "444555666777",
    "shared": "555666777888",
    "firebase": "666777888999",
    "environment": "777888999000",
    "shielded": "888999000111",
    "application-name": "999000111222",
    "billing-account": "123123123123",
    "UII | Investment code": "456456456456",
    "Application Name": "789789789789",
    "Sub-Application | Project Name": "987987987987",
    "FISMA ID": "654654654654",
    "OIT Executing Office": "321321321321",
    "Customer Office": "112233445566",
    "Funding Office": "778899001122",
    "Gov Lead": "334455667788",
    "Funding Status": "998877665544",
    "Funding Source": "113355779900"
    # ... add all of your other mappings here
}


# 3. Get the content of your CSV file into a string variable.
#    (This part would be replaced by actually reading your file)
# input_csv_string = """project_number,Directorate in BQ,environment
# 346380439549,TASPD,dev
# 1098178225458,CTO,prd
# """

# 4. Call the function with the CSV content and the mapping.
# transformed_data_with_ids = transform_csv_with_ids(input_csv_string, TAG_NAME_TO_ID_MAPPING)

# 5. Print the result. The output now has the 'metadata' column at the end.
# print("--- Transformed CSV with Metadata Column Last ---")
# print(transformed_data_with_ids)
# Expected output:
# tagkey_id,tagkey_name,tagvalue,metadata
# 111222333444,Directorate in BQ,TASPD,346380439549
# 777888999000,environment,dev,346380439549
# 111222333444,Directorate in BQ,CTO,1098178225458
# 777888999000,environment,prd,1098178225458
