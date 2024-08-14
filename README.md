# Sheets-Generator POC

## Table of Contents
1. [Introduction](#introduction)
2. [Purpose of the Tool](#purpose-of-the-tool)
3. [Environment](#environment)
4. [Environment Requirements](#environment-requirements)
5. [Technologies Used](#technologies-used)
6. [Dependencies](#dependencies)
7. [Usage](#usage)
	  - [Using Arguments](#using-arguments)
	    - [dump.py](#dump.py)
	    - [report.py](#report.py)
	  - [Without Arguments](#without-arguments)
8. [Workflow](#workflow)
9. [Execution Flow](#execution-flow)
	  - [dump.py Script](#dump.py-script)
	  - [report.py Script](#report.py-script)
10. [Additional Notes](#additional-notes)
	  - [Example `env.json` File](#example-envjson-file)

## Introduction

The `sheets-generator` tool is designed to automate the process of generating detailed reports by extracting data from Google Drive folders and converting it into structured Google Sheets or CSV files. The tool operates in two phases using two scripts: `dump.py` and `report.py`. These scripts are manually executed in sequence to gather data, process it, and generate the final reports.

## Purpose of the Tool

The primary purpose of the `sheets-generator` tool is to simplify and automate the extraction, organization, and reporting of test data stored in Google Drive. The tool is particularly useful for generating test reports that include links to relevant media files (e.g., screenshots, videos, and packet captures) stored in Drive.

## Environment

The tool is intended to run in a Python environment with access to Google Drive APIs. It requires authentication through either OAuth 2.0 (Client Secret) or Service Account credentials.

## Environment Requirements

- Python 3.x
- Internet access for API calls to Google Drive
- Google Drive API enabled
- Authentication credentials (Client Secret or Service Account JSON file)

## Technologies Used

- **Python 3.x**: Primary programming language used for the scripts.
- **Google Drive API**: For accessing and manipulating files in Google Drive.
- **Pandas**: For data manipulation and analysis.
- **Gspread**: For interacting with Google Sheets.
- **Numpy**: For numerical operations.

## Dependencies

The tool relies on several Python libraries that need to be installed prior to running the scripts. These can be installed via pip:

```sh
pip install pandas numpy gspread google-api-python-client oauth2client
```
OR
```sh
pip install -r dependencies/requirements.txt
```

## Usage

### Using Arguments

Both `dump.py` and `report.py` scripts require specific arguments to run.

#### `dump.py`

```sh
python dump.py <ENTRY_POINT> <FILTER>
```

- `<ENTRY_POINT>`: The name of the VM or environment from which data is to be extracted.
- `<FILTER>`: A string to filter the directories of interest in Google Drive.

#### `report.py`

```sh
python report.py <ENTRY_POINT>
```

- `<ENTRY_POINT>`: The name of the VM or environment for which the report needs to be generated.

### Without Arguments

Running the scripts without the necessary arguments will result in an error. Ensure you provide all required arguments to avoid execution failure.

## Workflow

The tool operates in a sequential workflow involving two primary phases:

1. **Data Extraction (dump.py)**: The `dump.py` script connects to Google Drive, navigates through specified directories, and extracts data. It generates JSON dumps of the data, which are stored locally.

2. **Report Generation (report.py)**: The `report.py` script reads the JSON dumps created in the first phase and generates a detailed report in Google Sheets format. It can also export the data as CSV files if required.

## Execution Flow

### `dump.py Script`

The `dump.py` script performs the following tasks:

1. **Google Drive Authentication**: Authenticates using the provided credentials (Service Account or OAuth 2.0 Client Secret).
2. **Directory Navigation**: Navigates through the specified Google Drive directories based on the provided `ENTRY_POINT` and `FILTER`.
3. **Data Extraction**: Extracts relevant data, such as links to media files, and organizes it into a structured format.
4. **JSON Dump Creation**: Saves the extracted data as JSON files in a designated local directory.

### `report.py Script`

The `report.py` script performs the following tasks:

1. **Google Sheets Authentication**: Authenticates using the provided credentials.
2. **Data Aggregation**: Aggregates data from the JSON dumps created by `dump.py`.
3. **Google Sheets Creation**: Creates a new Google Sheet and populates it with the aggregated data.
4. **CSV Export (Optional)**: Optionally exports the data into CSV format for offline analysis.

## Additional Notes

### Example `env.json` File

The `env.json` file contains additional configuration parameters, such as the Drive ID, VM information, and worksheet details. An example `env.json` file might look like this:

```json
{
  "driveID": "your-drive-id",
  "VMInfo": [
    {
      "name": "VM1",
      "parent_directory_id": "parent-dir-id-1"
    },
    {
      "name": "VM2",
      "parent_directory_id": "parent-dir-id-2"
    }
  ],
  "worksheet": [
    {
      "id": "worksheet-id-1",
      "name": "Sheet1"
    }
  ],
  "spreadsheet": [
    {
      "acronym": "VM1",
      "spreadsheetFolderID": "spreadsheet-folder-id-1"
    }
  ]
}
```

## Author
[Aayush Rajthala](https://github.com/AayushRajthala99)
