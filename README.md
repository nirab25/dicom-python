# DICOM Learning

This repository is a learning project designed to demonstrate how to create and upload DICOM objects using Python. The project includes functionality to:

- **Upload PDF documents:** Convert PDF pages into images and create encapsulated PDF DICOM objects.
- **Upload image files:** Convert exam report images into DICOM objects.
- **Manage patient records:** Embed patient demographics and exam metadata into the DICOM datasets.
- **Communicate with a DICOM server:** Use the C-STORE service to send DICOM objects to an Orthanc server.
- **DICOM Modality Worklist Management:** Create, upload, and retrieve DICOM Modality Worklist items using Orthanc's REST API.

## Features

- **PDF to DICOM Conversion:**  
  Split multi-page PDF reports into individual images and upload them as DICOM objects.

- **Image to DICOM Conversion:**  
  Convert image files (e.g., exam reports) into DICOM datasets with integrated patient and exam data.

- **DICOM Communication:**  
  Establish DICOM associations using the pynetdicom library and upload objects to a DICOM server (e.g., Orthanc).

- **Patient Records Integration:**  
  Customize DICOM datasets with patient records, exam dates, operator information, and other metadata.

- **DICOM Modality Worklist Management:**  
  Create, upload, and retrieve DICOM Modality Worklist (MWL) items using Orthanc's REST API. This includes:
  - Creating worklist items with patient and procedure information
  - Uploading worklist items to Orthanc
  - Retrieving worklist items by date range
  - Command-line interface for worklist management
  - Batch processing of multiple worklist items

## Project Structure

- **main.py**: Main script for creating and uploading DICOM images
- **worklist.py**: Module for DICOM Modality Worklist management
- **worklist_example.py**: Example script demonstrating worklist functionality
- **worklist_cli.py**: Command-line interface for worklist management
- **sample_worklists.json**: Sample data for batch worklist creation
- **data/**: Directory containing sample images

## Requirements

- Python 3.7 or later
- The following Python packages (see `requirements.txt`):
  - pydicom
  - pynetdicom
  - Pillow
  - numpy
  - requests

Install dependencies using:

```bash
pip install -r requirements.txt
```

## Worklist Management

### Creating and Uploading Worklist Items

```python
from worklist import create_worklist_item, upload_worklist_to_orthanc

# Create a worklist item
worklist = create_worklist_item(
    patient_name="Doe^John",
    patient_id="JD12345",
    accession_number="ACC12345",
    scheduled_procedure_step_start_date="20250507",
    scheduled_procedure_step_start_time="090000",
    modality="US",
    requested_procedure_description="Abdominal Ultrasound"
)

# Upload to Orthanc
result = upload_worklist_to_orthanc(
    worklist,
    orthanc_url="http://localhost:8042",
    username="orthanc",  # if authentication is required
    password="orthanc"   # if authentication is required
)
```

### Retrieving Worklist Items by Date Range

```python
from worklist import get_worklists_by_date_range

# Get worklists for a specific date range
worklists = get_worklists_by_date_range(
    start_date="20250501",
    end_date="20250531",
    orthanc_url="http://localhost:8042",
    username="orthanc",  # if authentication is required
    password="orthanc"   # if authentication is required
)

# Process the results
for item in worklists:
    print(f"Patient: {item.get('PatientName')}")
    print(f"Procedure: {item.get('Description')}")
    print(f"Date: {item.get('ScheduledDate')}")
```

### Using the Command-Line Interface

The `worklist_cli.py` script provides a command-line interface for worklist management:

```bash
# Create a worklist item
python worklist_cli.py create --patient-name "Doe^John" --patient-id "JD12345" --accession "ACC12345"

# List worklists by date range
python worklist_cli.py list --start-date 20250501 --end-date 20250531

# Get details of a specific worklist item
python worklist_cli.py get --id "worklist-id"

# Create multiple worklist items from a JSON file
python worklist_cli.py batch --file sample_worklists.json
```

For more options, run:

```bash
python worklist_cli.py --help
```

## Example Usage

Run the example script to see the worklist functionality in action:

```bash
python worklist_example.py
```

This will create a sample worklist item and retrieve worklists for the next week.
