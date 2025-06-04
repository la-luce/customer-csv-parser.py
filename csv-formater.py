import csv
import io
import argparse
import json
import sys

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
        # Using sys.stderr to report errors is a good practice for command-line tools
        sys.stderr.write(f"Error: Missing ID mapping for the following Tag Names: {', '.join(missing_keys)}\n")
        return None

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
                # Check if the tag_name actually exists in our mapping before proceeding
                if tag_value.strip() and tag_name in tag_name_to_id_mapping:
                    # Look up the tag ID from the mapping dictionary
                    tag_id = tag_name_to_id_mapping[tag_name]
                    # Append the new four-column row with metadata (project_number) at the end
                    output_rows.append([tag_id, tag_name, tag_value, metadata_value])

    # Convert the list of output rows back to a CSV formatted string
    output_file = io.StringIO()
    writer = csv.writer(output_file)
    writer.writerows(output_rows)
    
    return output_file.getvalue()

def main():
    """
    Main function to run the script from the command line.
    Parses arguments, reads files, calls the transformation function, and writes the output.
    """
    parser = argparse.ArgumentParser(
        description="Transforms a CSV of project tags into a long format suitable for ingestion.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'input_csv',
        help="Path to the input CSV file."
    )
    parser.add_argument(
        'mapping_json',
        help="Path to the JSON file containing the mapping of tag names to tag IDs."
    )
    parser.add_argument(
        'output_csv',
        help="Path for the output CSV file."
    )

    args = parser.parse_args()

    # --- Read Input Files ---
    try:
        with open(args.input_csv, 'r', encoding='utf-8') as f:
            input_csv_content = f.read()
    except FileNotFoundError:
        sys.stderr.write(f"Error: Input file not found at '{args.input_csv}'\n")
        sys.exit(1)

    try:
        with open(args.mapping_json, 'r', encoding='utf-8') as f:
            tag_name_to_id_mapping = json.load(f)
    except FileNotFoundError:
        sys.stderr.write(f"Error: Mapping file not found at '{args.mapping_json}'\n")
        sys.exit(1)
    except json.JSONDecodeError:
        sys.stderr.write(f"Error: Could not parse the JSON mapping file. Please check its format.\n")
        sys.exit(1)

    # --- Transform Data ---
    print("Starting CSV transformation...")
    transformed_data = transform_csv_with_ids(input_csv_content, tag_name_to_id_mapping)
    
    # --- Write Output File ---
    if transformed_data:
        try:
            with open(args.output_csv, 'w', encoding='utf-8', newline='') as f:
                f.write(transformed_data)
            print(f"Transformation complete. Output written to '{args.output_csv}'")
        except IOError as e:
            sys.stderr.write(f"Error writing to output file '{args.output_csv}': {e}\n")
            sys.exit(1)
    else:
        sys.stderr.write("Transformation failed. Please check the error messages above.\n")
        sys.exit(1)

# This block makes the script executable from the command line
if __name__ == "__main__":
    main()
