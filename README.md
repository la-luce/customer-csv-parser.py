# CSV Tag Transformation Script

## Overview

This Python script transforms a wide-format CSV file of project tags into a long-format, database-friendly CSV. It is designed to be run in an interactive environment like Google Colab or a Jupyter Notebook, where it will prompt the user to upload the necessary files.

The core purpose is to take a CSV where each row represents a project and each column represents a possible tag, and "unpivot" it into a normalized, four-column format.

## How It Works

The script reads two files:

1.  An **input CSV** containing the project data.
2.  A **JSON mapping file** that provides a unique ID for each tag name (the headers from the input CSV).

It then iterates through each cell of the input CSV. For every cell that contains a value, it creates a new row in the output file, combining the project number, the tag name (from the column header), the tag value (from the cell), and the corresponding tag ID (from the JSON map).

## File Formats

### 1. Input CSV

The input CSV must have the project identifier in the first column. All subsequent columns should have headers that represent the `tagkey_name`. For example, a row might contain 'proj-001' in the 'project_number' column, 'Production' in the 'Environment' column, and 'Auth Service' in the 'Application' column.

### 2. Tag Mapping JSON

This file should be a simple JSON object where keys are the exact header names from the input CSV (`tagkey_name`) and values are their corresponding unique IDs (`tagkey_id_number`). For instance, the mapping might pair the 'Environment' key with the ID '101' and the 'Application' key with '102'.

## Output Format

The script generates a single output file named `transformed_output.csv`. This file will always have the following four columns:

* `tagkey_id_number`
* `tagkey_name`
* `tagvalue_short_name`
* `project_number`

Based on the example inputs described above, the script would generate a new row for each tag associated with a project.

## How to Use

Follow these steps to run the script in a Google Colab or Jupyter Notebook:

1.  Copy the entire Python script provided in the notebook into a single cell.
2.  Run the cell.
3.  The script will prompt you to **upload your input CSV file**. Use the file browser to select and upload it.
4.  Next, it will prompt you to **upload your tag mapping JSON file**.
5.  Once both files are uploaded, the script will perform the transformation.
6.  A success message will be displayed, and the output file (`transformed_output.csv`) will appear in the Colab/Jupyter file browser, ready for you to download.

If any `tagkey_name` from your CSV headers is missing from the JSON file, the script will print an error and stop.
