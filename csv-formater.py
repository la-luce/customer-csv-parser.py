import csv
import io
import json
import sys

# This is the core transformation function.
def transform_csv_with_ids(input_csv_content, tag_name_to_id_mapping):
    """
    Transforms CSV data into a four-column format for readability:
    tagkey_id_number, tagkey_name, tagvalue_short_name, project_number.

    Args:
        input_csv_content (str): A string containing the content of the input CSV.
        tag_name_to_id_mapping (dict): A dictionary mapping tag display names 
                                       (from CSV headers) to their unique IDs.

    Returns:
        str: A string containing the transformed data in CSV format, or None if an error occurs.
    """
    # Use io.StringIO to treat the string input_csv_content as a file
    input_file = io.StringIO(input_csv_content)
    reader = csv.reader(input_file)

    try:
        tag_name_headers = next(reader)[1:] # Get all tag name headers, skipping the first column
    except StopIteration:
        print("Error: CSV file is empty or has no headers.", file=sys.stderr)
        return None

    # Validate that all headers from the CSV have a corresponding ID in the mapping
    missing_keys = [header for header in tag_name_headers if header.strip() and header not in tag_name_to_id_mapping]
    if missing_keys:
        print(f"Error: Missing ID mapping for the following Tag Names: {', '.join(missing_keys)}", file=sys.stderr)
        return None

    output_rows = []
    # Set the new header row as requested
    output_rows.append(['tagkey_id_number', 'tagkey_name', 'tagvalue_short_name', 'project_number'])

    # Rewind the file-like object to read from the beginning again
    input_file.seek(0) 
    next(reader) # Skip header row
    
    for row in reader:
        if not row or not any(field.strip() for field in row):
            continue
        if len(row) < 1:
            continue
            
        metadata_value = row[0]
        if not metadata_value.strip():
            continue
            
        tag_values = row[1:]

        for i, tag_name in enumerate(tag_name_headers):
            if i < len(tag_values):
                tag_value = tag_values[i]
                if tag_value.strip() and tag_name in tag_name_to_id_mapping:
                    tag_id = tag_name_to_id_mapping[tag_name]
                    # Append the data in the new order
                    output_rows.append([tag_id, tag_name, tag_value, metadata_value])

    output_file = io.StringIO()
    writer = csv.writer(output_file)
    writer.writerows(output_rows)
    
    return output_file.getvalue()


# --- How to run in Google Colab / Jupyter Notebook ---
#
# Instead of using the command line, you will run the code below in a notebook cell.
# This code handles uploading your files, processing them, and making the result available
# for download.
#
# Steps:
# 1. Copy the code from the 'main_notebook_runner' function into a new Colab cell.
# 2. Run the cell.
# 3. You will be prompted to upload two files:
#    - First, your input CSV (e.g., 'Mage Tagging Sheet - Sheet1.csv').
#    - Second, your mapping JSON file (e.g., 'tag_mappings.json').
# 4. The script will process the files and save the output as 'transformed_output.csv'.
# 5. This output file will appear in the Colab file browser (the folder icon on the left),
#    from where you can download it.

def main_notebook_runner():
    """
    This function replaces the command-line interface for use in a notebook.
    """
    try:
        from google.colab import files
        print("Please upload your input CSV file:")
        uploaded_csv = files.upload()
        
        if not uploaded_csv:
            print("No CSV file was uploaded. Aborting.")
            return

        # Get the content of the first uploaded CSV file
        input_csv_filename = list(uploaded_csv.keys())[0]
        input_csv_content = uploaded_csv[input_csv_filename].decode('utf-8')
        print(f"Successfully uploaded '{input_csv_filename}'.")

        print("\nPlease upload your tag mapping JSON file:")
        uploaded_json = files.upload()

        if not uploaded_json:
            print("No JSON file was uploaded. Aborting.")
            return
            
        # Get the content of the first uploaded JSON file
        mapping_json_filename = list(uploaded_json.keys())[0]
        tag_name_to_id_mapping = json.loads(uploaded_json[mapping_json_filename].decode('utf-8'))
        print(f"Successfully uploaded and parsed '{mapping_json_filename}'.")

    except ImportError:
        # Fallback for environments other than Colab (like a local Jupyter notebook)
        print("Not in a Google Colab environment. Please define file contents manually.")
        # In a local Jupyter notebook, you would load files like this:
        # with open('path/to/your/file.csv', 'r') as f:
        #     input_csv_content = f.read()
        # with open('path/to/your/mapping.json', 'r') as f:
        #     tag_name_to_id_mapping = json.load(f)
        return # Stop execution if not in Colab for this example

    # --- Transform Data ---
    print("\nStarting CSV transformation...")
    transformed_data = transform_csv_with_ids(input_csv_content, tag_name_to_id_mapping)

    # --- Display and Save Output ---
    if transformed_data:
        # Print a preview of the first few lines
        print("\n--- Transformation Successful ---")
        preview = '\n'.join(transformed_data.splitlines()[:10])
        print("Preview of the first 10 lines of output:\n")
        print(preview)

        # Save the result to a file
        output_filename = 'transformed_output.csv'
        with open(output_filename, 'w', encoding='utf-8', newline='') as f:
            f.write(transformed_data)
        
        print(f"\nOutput successfully saved as '{output_filename}'.")
        print("You can find and download this file from the file browser on the left.")
    else:
        print("\nTransformation failed. Please check the error messages above.", file=sys.stderr)

# To run this in your notebook, copy the following line into a new cell and execute it:
# main_notebook_runner()
