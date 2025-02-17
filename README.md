# DICOM Learning

This repository is a learning project designed to demonstrate how to create and upload DICOM objects using Python. The project includes functionality to:

- **Upload PDF documents:** Convert PDF pages into images and create encapsulated PDF DICOM objects.
- **Upload image files:** Convert exam report images into DICOM objects.
- **Manage patient records:** Embed patient demographics and exam metadata into the DICOM datasets.
- **Communicate with a DICOM server:** Use the C-STORE service to send DICOM objects to an Orthanc server.

## Features

- **PDF to DICOM Conversion:**  
  Split multi-page PDF reports into individual images and upload them as DICOM objects.

- **Image to DICOM Conversion:**  
  Convert image files (e.g., exam reports) into DICOM datasets with integrated patient and exam data.

- **DICOM Communication:**  
  Establish DICOM associations using the pynetdicom library and upload objects to a DICOM server (e.g., Orthanc).

- **Patient Records Integration:**  
  Customize DICOM datasets with patient records, exam dates, operator information, and other metadata.

## Project Structure

## Requirements

- Python 3.7 or later
- The following Python packages (see `requirements.txt`):
  - pydicom
  - pynetdicom
  - Pillow
  - numpy

Install dependencies using:

```bash
pip install -r requirements.txt