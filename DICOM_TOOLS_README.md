# DICOM Tools

A Python utility for working with DICOM files and servers, specifically focused on Modality Worklist (MWL) functionality.

## Overview

This tool provides five main functions:

1. **Converting MWL sample files to DICOM format**: Converts text-based MWL sample files to DICOM (.dcm) files that can be used for testing and development.
2. **Testing connectivity with DICOM servers using C-ECHO**: Verifies connectivity with DICOM servers by performing a C-ECHO operation.
3. **Retrieving worklist items from a DICOM server**: Queries a DICOM server for worklist items using C-FIND and displays them in a user-friendly format.
4. **Loading and displaying sample worklist items**: Loads sample worklist items from a JSON file and displays them in a user-friendly format.
5. **Creating and sending worklist items to a DICOM server**: Creates a sample worklist item and sends it to a DICOM server.

## Prerequisites

- Python 3.7 or later
- Required Python packages (install using `pip install -r requirements.txt`):
  - pydicom
  - pynetdicom
  - requests

## Installation

1. Clone this repository or download the script.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

The script can be run with various command-line options:

```bash
python dicom_tools.py [options]
```

### Available Options

- `--convert`: Convert MWL sample files to DICOM format
- `--echo`: Test connectivity with a DICOM server using C-ECHO
- `--get-worklist`: Retrieve worklist items from a DICOM server
- `--sample-worklist`: Load and display sample worklist items from sample_worklists.json
- `--create-worklist`: Create and send a sample worklist item to a DICOM server
- `--server-ip`: IP address of the DICOM server (default: 10.10.0.1)
- `--server-port`: Port of the DICOM server (default: 4242)
- `--server-ae`: AE title of the DICOM server (default: MERCURE)
- `--client-ae`: AE title of the client (default: BEXA)
- `--start-date`: Start date for worklist query (YYYYMMDD)
- `--end-date`: End date for worklist query (YYYYMMDD)
- `--patient-name`: Patient name for worklist query
- `--modality`: Modality for worklist query (e.g., US, CT, MR)
- `--output-format`: Output format for worklist display (choices: text, json, default: text)
- `--verbose`, `-v`: Enable verbose output
- `--help`, `-h`: Show help message and exit

### Examples

#### Converting MWL Sample Files to DICOM Format

```bash
python dicom_tools.py --convert
```

This will:
1. Read the MWL sample text files from the `data/mwl-sample/` directory
2. Convert them to DICOM (.dcm) files
3. Save the DICOM files to the `data/mwl-sample/dcm/` directory

#### Testing Connectivity with a DICOM Server

```bash
python dicom_tools.py --echo
```

This will:
1. Establish a DICOM association with the server
2. Send a C-ECHO request
3. Print the response from the server

#### Retrieving Worklist Items from a DICOM Server

```bash
python dicom_tools.py
```

By default, the script will retrieve worklist items from the DICOM server. You can also explicitly specify the `--get-worklist` option:

```bash
python dicom_tools.py --get-worklist
```

This will:
1. Establish a DICOM association with the server
2. Send a C-FIND request for worklist items
3. Display the retrieved worklist items

You can specify date ranges, patient names, and modalities to filter the results:

```bash
python dicom_tools.py --start-date 20250501 --end-date 20250531 --modality US
```

#### Loading and Displaying Sample Worklist Items

```bash
python dicom_tools.py --sample-worklist
```

This will:
1. Load sample worklist items from the `sample_worklists.json` file
2. Display the worklist items in a user-friendly format

You can also output the worklist items in JSON format:

```bash
python dicom_tools.py --sample-worklist --output-format json
```

#### Creating and Sending a Sample Worklist Item

```bash
python dicom_tools.py --create-worklist
```

This will:
1. Create a sample worklist item with default values
2. Display the created worklist item
3. Send the worklist item to the DICOM server

You can specify the server details and modality:

```bash
python dicom_tools.py --create-worklist --server-ip 192.168.1.100 --server-port 104 --server-ae ORTHANC --modality CT
```

#### Custom Server Configuration

```bash
python dicom_tools.py --server-ip 192.168.1.100 --server-port 104 --server-ae ORTHANC --client-ae CLIENT
```

#### Enabling Verbose Output

```bash
python dicom_tools.py --verbose
```

## File Structure

- `dicom_tools.py`: The main script containing all functionality
- `data/mwl-sample/`: Directory containing sample MWL files
  - `DMWL - Query Request.txt`: Sample MWL request file
  - `DMWL - Query Response.txt`: Sample MWL response file
  - `dcm/`: Directory containing converted DICOM files
    - `mwl_request.dcm`: Converted MWL request file
    - `mwl_response.dcm`: Converted MWL response file

## Functions

### `convert_mwl_samples()`

Converts MWL sample text files to DICOM (.dcm) files.

### `c_echo(ip_address, port, remote_ae, local_ae)`

Performs a C-ECHO operation with a DICOM server.

Parameters:
- `ip_address`: IP address of the DICOM server
- `port`: Port of the DICOM server
- `remote_ae`: AE title of the remote DICOM server
- `local_ae`: AE title of the local DICOM client

Returns:
- Status code from the C-ECHO response (0 indicates success)

### `get_worklist(ip_address, port, remote_ae, local_ae, start_date=None, end_date=None, patient_name=None, modality=None)`

Retrieves worklist items from a DICOM server using C-FIND.

Parameters:
- `ip_address`: IP address of the DICOM server
- `port`: Port of the DICOM server
- `remote_ae`: AE title of the remote DICOM server
- `local_ae`: AE title of the local DICOM client
- `start_date`: Start date in YYYYMMDD format (optional)
- `end_date`: End date in YYYYMMDD format (optional)
- `patient_name`: Patient name to filter by (optional)
- `modality`: Modality to filter by (optional)

Returns:
- List of worklist items matching the criteria

### `get_worklist_dataset(ip_address, port, remote_ae, local_ae, dataset=None, start_date=None, end_date=None, patient_name=None, modality=None)`

Retrieves worklist items from a DICOM server using C-FIND with a custom dataset.

Parameters:
- `ip_address`: IP address of the DICOM server
- `port`: Port of the DICOM server
- `remote_ae`: AE title of the remote DICOM server
- `local_ae`: AE title of the local DICOM client
- `dataset`: Custom dataset for the C-FIND query (optional)
- `start_date`: Start date in YYYYMMDD format (optional)
- `end_date`: End date in YYYYMMDD format (optional)
- `patient_name`: Patient name to filter by (optional)
- `modality`: Modality to filter by (optional)

Returns:
- List of worklist items matching the criteria

### `display_worklist(worklist_items, output_format='text')`

Displays worklist items in a user-friendly format.

Parameters:
- `worklist_items`: List of worklist items (pydicom.dataset.Dataset)
- `output_format`: Output format ('text' or 'json', default: 'text')

### `load_sample_worklists(file_path='sample_worklists.json')`

Loads sample worklist items from a JSON file.

Parameters:
- `file_path`: Path to the JSON file (default: 'sample_worklists.json')

Returns:
- List of worklist items as pydicom.dataset.Dataset objects

### `create_worklist_item(patient_name, patient_id, accession_number, scheduled_procedure_step_start_date, scheduled_procedure_step_start_time, ...)`

Creates a DICOM Modality Worklist item dataset.

Parameters:
- `patient_name`: Patient's name in DICOM format (Last^First)
- `patient_id`: Patient ID
- `accession_number`: Accession number for the procedure
- `scheduled_procedure_step_start_date`: Date in YYYYMMDD format
- `scheduled_procedure_step_start_time`: Time in HHMMSS format
- `modality`: Modality code (default: "US")
- `requested_procedure_description`: Description of the procedure (default: "Ultrasound")
- `scheduled_station_name`: Name of the station (default: "STATION1")
- `scheduled_station_ae_title`: AE title of the station (default: "STATION1")
- `referring_physician_name`: Name of referring physician (optional)
- `patient_birth_date`: Patient's birth date in YYYYMMDD format (optional)
- `patient_sex`: Patient's sex (M/F/O) (optional)
- `medical_alerts`: Medical alerts (optional)
- `contrast_allergies`: Contrast allergies (optional)

Returns:
- DICOM dataset for the worklist item

### `send_worklist_item(dataset, ip_address, port, remote_ae, local_ae)`

Sends a worklist item to a DICOM server.

Parameters:
- `dataset`: The worklist dataset to send
- `ip_address`: IP address of the DICOM server
- `port`: Port of the DICOM server
- `remote_ae`: AE title of the remote DICOM server
- `local_ae`: AE title of the local DICOM client

Returns:
- True if successful, False otherwise
