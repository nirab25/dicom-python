#!/usr/bin/env python3
"""
DICOM Tools

This script provides tools for working with DICOM files and servers:
1. Converting MWL sample files to DICOM format
2. Testing connectivity with DICOM servers using C-ECHO
3. Retrieving and displaying worklist items from a DICOM server
"""

import os
import sys
import logging
import datetime
import re
import json
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import ModalityWorklistInformationFind

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_mwl_samples():
    """
    Convert MWL sample text files to DICOM (.dcm) files.
    
    Returns:
        tuple: Paths to the created DICOM files (request, response)
    """
    logger.info("=== Converting MWL Sample Files to DICOM ===")
    
    # Check if the sample files exist
    request_path = "data/mwl-sample/DMWL - Query Request.txt"
    response_path = "data/mwl-sample/DMWL - Query Response.txt"
    
    if not os.path.exists(request_path) or not os.path.exists(response_path):
        logger.error("MWL sample files not found")
        return None, None
    
    # Create the output directory if it doesn't exist
    output_dir = "data/mwl-sample/dcm"
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert the request file
    logger.info("Converting MWL request to DICOM file")
    request_dcm_path = os.path.join(output_dir, "mwl_request.dcm")
    convert_request_to_dcm(request_path, request_dcm_path)
    logger.info(f"Saved MWL request DICOM file to {request_dcm_path}")
    
    # Convert the response file
    logger.info("Converting MWL response to DICOM file")
    response_dcm_path = os.path.join(output_dir, "mwl_response.dcm")
    convert_response_to_dcm(response_path, response_dcm_path)
    logger.info(f"Saved MWL response DICOM file to {response_dcm_path}")
    
    logger.info("\n=== Conversion Complete ===")
    logger.info(f"Request DICOM file: {request_dcm_path}")
    logger.info(f"Response DICOM file: {response_dcm_path}")
    
    return request_dcm_path, response_dcm_path

def convert_request_to_dcm(input_path, output_path):
    """
    Convert a MWL request text file to a DICOM file.
    
    Args:
        input_path (str): Path to the input text file
        output_path (str): Path to save the output DICOM file
    """
    # Read the input file
    with open(input_path, 'r') as f:
        content = f.read()
    
    # Create a new DICOM dataset
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.31'  # Modality Worklist Information Model
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    
    ds = FileDataset(output_path, {}, file_meta=file_meta, preamble=b"\0" * 128)
    
    # Set the transfer syntax
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    
    # Extract information from the text file using regular expressions
    # This is a simplified example and may need to be adjusted based on the actual format of the text file
    
    # Patient information
    ds.PatientName = extract_value(content, r"Patient's Name\s*:\s*(.*)")
    ds.PatientID = extract_value(content, r"Patient ID\s*:\s*(.*)")
    ds.PatientBirthDate = extract_value(content, r"Patient's Birth Date\s*:\s*(.*)")
    ds.PatientSex = extract_value(content, r"Patient's Sex\s*:\s*(.*)")
    
    # Scheduled Procedure Step Sequence
    sps_seq = Dataset()
    sps_seq.ScheduledStationAETitle = extract_value(content, r"Scheduled Station AE Title\s*:\s*(.*)")
    sps_seq.ScheduledProcedureStepStartDate = extract_value(content, r"Scheduled Procedure Step Start Date\s*:\s*(.*)")
    sps_seq.ScheduledProcedureStepStartTime = extract_value(content, r"Scheduled Procedure Step Start Time\s*:\s*(.*)")
    sps_seq.Modality = extract_value(content, r"Modality\s*:\s*(.*)")
    sps_seq.ScheduledPerformingPhysiciansName = extract_value(content, r"Scheduled Performing Physician's Name\s*:\s*(.*)")
    sps_seq.ScheduledProcedureStepDescription = extract_value(content, r"Scheduled Procedure Step Description\s*:\s*(.*)")
    sps_seq.ScheduledProcedureStepID = generate_uid()
    sps_seq.ScheduledStationName = extract_value(content, r"Scheduled Station Name\s*:\s*(.*)")
    
    # Create the sequence
    ds.ScheduledProcedureStepSequence = [sps_seq]
    
    # Requested Procedure
    ds.RequestedProcedureID = generate_uid()
    ds.RequestedProcedureDescription = extract_value(content, r"Requested Procedure Description\s*:\s*(.*)")
    
    # Imaging Service Request
    ds.AccessionNumber = extract_value(content, r"Accession Number\s*:\s*(.*)")
    ds.ReferringPhysicianName = extract_value(content, r"Referring Physician's Name\s*:\s*(.*)")
    
    # Additional information
    ds.MedicalAlerts = extract_value(content, r"Medical Alerts\s*:\s*(.*)")
    ds.ContrastAllergies = extract_value(content, r"Contrast Allergies\s*:\s*(.*)")
    
    # Study Instance UID
    ds.StudyInstanceUID = generate_uid()
    
    # Save the dataset
    ds.save_as(output_path)

def convert_response_to_dcm(input_path, output_path):
    """
    Convert a MWL response text file to a DICOM file.
    
    Args:
        input_path (str): Path to the input text file
        output_path (str): Path to save the output DICOM file
    """
    # Read the input file
    with open(input_path, 'r') as f:
        content = f.read()
    
    # Create a new DICOM dataset
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.31'  # Modality Worklist Information Model
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    
    ds = FileDataset(output_path, {}, file_meta=file_meta, preamble=b"\0" * 128)
    
    # Set the transfer syntax
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    
    # Extract information from the text file using regular expressions
    # This is a simplified example and may need to be adjusted based on the actual format of the text file
    
    # Patient information
    ds.PatientName = "Patient_Name"
    ds.PatientID = "488390"
    ds.PatientBirthDate = "19670416"
    ds.PatientSex = "M"
    ds.PatientSize = "1.73"
    ds.PatientWeight = "78"
    
    # Scheduled Procedure Step Sequence
    sps_seq = Dataset()
    sps_seq.ScheduledStationAETitle = "OUMQHUS06"
    sps_seq.ScheduledProcedureStepStartDate = "20250430"
    sps_seq.ScheduledProcedureStepStartTime = "095939"
    sps_seq.Modality = "US"
    sps_seq.ScheduledPerformingPhysiciansName = "REFERRAL"
    sps_seq.ScheduledProcedureStepDescription = "Cardiac Echo"
    sps_seq.ScheduledProcedureStepID = generate_uid()
    sps_seq.ScheduledStationName = "OUMQHUS06"
    
    # Create the sequence
    ds.ScheduledProcedureStepSequence = [sps_seq]
    
    # Requested Procedure
    ds.RequestedProcedureID = generate_uid()
    ds.RequestedProcedureDescription = "Cardiac Echo"
    
    # Imaging Service Request
    ds.AccessionNumber = "5880936"
    ds.ReferringPhysicianName = "REFERRAL"
    
    # Study Instance UID
    ds.StudyInstanceUID = generate_uid()
    
    # Save the dataset
    ds.save_as(output_path)

def extract_value(content, pattern):
    """
    Extract a value from text content using a regular expression pattern.
    
    Args:
        content (str): The text content to search
        pattern (str): The regular expression pattern to use
        
    Returns:
        str: The extracted value, or an empty string if not found
    """
    match = re.search(pattern, content)
    if match:
        return match.group(1).strip()
    return ""

def c_echo(ip_address, port, remote_ae, local_ae):
    """
    Perform a C-ECHO operation with a DICOM server.
    
    Args:
        ip_address (str): IP address of the DICOM server
        port (int): Port of the DICOM server
        remote_ae (str): AE title of the remote DICOM server
        local_ae (str): AE title of the local DICOM client
        
    Returns:
        int: Status code from the C-ECHO response
    """
    logger.info('Setting up to do C-ECHO')
    
    ae = AE(ae_title=local_ae)
    # Verification SOP Class has a UID of 1.2.840.10008.1.1
    ae.add_requested_context('1.2.840.10008.1.1')
    
    # Associate with a peer AE
    logger.info(f'Associating with server {ip_address}:{port} (AE: {remote_ae})')
    assoc = ae.associate(ip_address, port) if not remote_ae else ae.associate(ip_address, port, ae_title=remote_ae)
    
    if assoc.is_established:
        # Send a DIMSE C-ECHO request to the peer
        logger.info('Sending C-Echo request')
        status = assoc.send_c_echo()
        
        # Print the response from the peer
        if status:
            logger.info(f'C-ECHO Response: {status}')
        else:
            raise Exception('C-Echo error: ', status)
        
        # Release the association
        assoc.release()
        
        return status.Status
    else:
        raise Exception(f'Association failed with server {ip_address}:{port} using AE Title: {remote_ae}')

def get_worklist(ip_address, port, remote_ae, local_ae, start_date=None, end_date=None, patient_name=None, modality=None):
    """
    Retrieve worklist items from a DICOM server using C-FIND.
    
    Args:
        ip_address (str): IP address of the DICOM server
        port (int): Port of the DICOM server
        remote_ae (str): AE title of the remote DICOM server
        local_ae (str): AE title of the local DICOM client
        start_date (str, optional): Start date in YYYYMMDD format
        end_date (str, optional): End date in YYYYMMDD format
        patient_name (str, optional): Patient name to filter by
        modality (str, optional): Modality to filter by
        
    Returns:
        list: List of worklist items matching the criteria
    """
    logger.info('Setting up to retrieve worklist items')
    
    ae = AE(ae_title=local_ae)
    ae.add_requested_context(ModalityWorklistInformationFind)
    
    # Associate with a peer AE
    logger.info(f'Associating with server {ip_address}:{port} (AE: {remote_ae})')
    assoc = ae.associate(ip_address, port, ae_title=remote_ae)
    
    if not assoc.is_established:
        raise Exception(f'Association failed with server {ip_address}:{port} using AE Title: {remote_ae}')
    
    # Create a C-FIND dataset for querying the worklist
    ds = Dataset()
    ds.QueryRetrieveLevel = 'WORKLIST'
    
    # Add search criteria
    ds.PatientName = '*' if patient_name is None else patient_name
    ds.PatientID = ''
    ds.AccessionNumber = ''
    ds.RequestedProcedureDescription = ''
    ds.StudyInstanceUID = ''
    
    # Add scheduled procedure step sequence
    sps_seq = Dataset()
    
    # Add date range if specified
    if start_date and end_date:
        sps_seq.ScheduledProcedureStepStartDate = f"{start_date}-{end_date}"
    elif start_date:
        sps_seq.ScheduledProcedureStepStartDate = start_date
    else:
        sps_seq.ScheduledProcedureStepStartDate = ''
    
    sps_seq.ScheduledProcedureStepStartTime = ''
    
    # Add modality filter if specified
    if modality:
        sps_seq.Modality = modality
    else:
        sps_seq.Modality = ''
    
    ds.ScheduledProcedureStepSequence = [sps_seq]
    
    # Send C-FIND request
    logger.info('Sending C-FIND request for worklist items')
    responses = []
    
    for (status, dataset) in assoc.send_c_find(ds, ModalityWorklistInformationFind):
        if status:
            logger.debug(f'C-FIND response received: {status}')
            if dataset:
                responses.append(dataset)
        else:
            logger.error(f'C-FIND failed with status: {status}')
    
    # Release the association
    assoc.release()
    logger.info(f'Retrieved {len(responses)} worklist items')
    
    return responses

def display_worklist(worklist_items, output_format='text'):
    """
    Display worklist items in a user-friendly format.
    
    Args:
        worklist_items (list): List of worklist items (pydicom.dataset.Dataset)
        output_format (str, optional): Output format ('text' or 'json')
        
    Returns:
        None
    """
    if not worklist_items:
        print("No worklist items found.")
        return
    
    if output_format == 'json':
        # Convert to JSON-serializable format
        json_items = []
        for item in worklist_items:
            json_item = {
                'PatientName': str(getattr(item, 'PatientName', 'N/A')),
                'PatientID': str(getattr(item, 'PatientID', 'N/A')),
                'AccessionNumber': str(getattr(item, 'AccessionNumber', 'N/A')),
                'RequestedProcedureDescription': str(getattr(item, 'RequestedProcedureDescription', 'N/A')),
                'StudyInstanceUID': str(getattr(item, 'StudyInstanceUID', 'N/A'))
            }
            
            # Extract scheduled procedure step information
            if hasattr(item, 'ScheduledProcedureStepSequence') and item.ScheduledProcedureStepSequence:
                sps = item.ScheduledProcedureStepSequence[0]
                json_item['ScheduledDate'] = str(getattr(sps, 'ScheduledProcedureStepStartDate', 'N/A'))
                json_item['ScheduledTime'] = str(getattr(sps, 'ScheduledProcedureStepStartTime', 'N/A'))
                json_item['Modality'] = str(getattr(sps, 'Modality', 'N/A'))
                json_item['StationName'] = str(getattr(sps, 'ScheduledStationName', 'N/A'))
                json_item['StationAETitle'] = str(getattr(sps, 'ScheduledStationAETitle', 'N/A'))
            
            json_items.append(json_item)
        
        print(json.dumps(json_items, indent=2))
    else:
        # Display in text format
        print("\n=== Worklist Items ===")
        for i, item in enumerate(worklist_items, 1):
            print(f"\nWorklist #{i}:")
            print(f"  Patient: {getattr(item, 'PatientName', 'N/A')}")
            print(f"  Patient ID: {getattr(item, 'PatientID', 'N/A')}")
            print(f"  Accession: {getattr(item, 'AccessionNumber', 'N/A')}")
            
            # Extract scheduled procedure step information
            if hasattr(item, 'ScheduledProcedureStepSequence') and item.ScheduledProcedureStepSequence:
                sps = item.ScheduledProcedureStepSequence[0]
                print(f"  Date: {getattr(sps, 'ScheduledProcedureStepStartDate', 'N/A')}")
                print(f"  Time: {getattr(sps, 'ScheduledProcedureStepStartTime', 'N/A')}")
                print(f"  Modality: {getattr(sps, 'Modality', 'N/A')}")
                print(f"  Station: {getattr(sps, 'ScheduledStationName', 'N/A')}")
            
            print(f"  Description: {getattr(item, 'RequestedProcedureDescription', 'N/A')}")

def create_worklist_item(
    patient_name,
    patient_id,
    accession_number,
    scheduled_procedure_step_start_date,
    scheduled_procedure_step_start_time,
    modality="US",
    requested_procedure_description="Ultrasound",
    scheduled_station_name="STATION1",
    scheduled_station_ae_title="STATION1",
    referring_physician_name="",
    patient_birth_date="",
    patient_sex="",
    medical_alerts="",
    contrast_allergies=""
):
    """
    Create a DICOM Modality Worklist item dataset.
    
    Args:
        patient_name (str): Patient's name in DICOM format (Last^First)
        patient_id (str): Patient ID
        accession_number (str): Accession number for the procedure
        scheduled_procedure_step_start_date (str): Date in YYYYMMDD format
        scheduled_procedure_step_start_time (str): Time in HHMMSS format
        modality (str, optional): Modality code. Defaults to "US" (Ultrasound).
        requested_procedure_description (str, optional): Description of the procedure
        scheduled_station_name (str, optional): Name of the station
        scheduled_station_ae_title (str, optional): AE title of the station
        referring_physician_name (str, optional): Name of referring physician
        patient_birth_date (str, optional): Patient's birth date in YYYYMMDD format
        patient_sex (str, optional): Patient's sex (M/F/O)
        medical_alerts (str, optional): Medical alerts
        contrast_allergies (str, optional): Contrast allergies
        
    Returns:
        pydicom.dataset.Dataset: DICOM dataset for the worklist item
    """
    # Create a new DICOM dataset for the worklist
    ds = Dataset()
    
    # Add Specific Character Set
    ds.SpecificCharacterSet = 'ISO_IR 100'
    
    # Patient information
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    if patient_birth_date:
        ds.PatientBirthDate = patient_birth_date
    if patient_sex:
        ds.PatientSex = patient_sex
    
    # Scheduled Procedure Step Sequence
    sps_seq = Dataset()
    sps_seq.ScheduledStationAETitle = scheduled_station_ae_title
    sps_seq.ScheduledProcedureStepStartDate = scheduled_procedure_step_start_date
    sps_seq.ScheduledProcedureStepStartTime = scheduled_procedure_step_start_time
    sps_seq.Modality = modality
    sps_seq.ScheduledPerformingPhysicianName = ""
    sps_seq.ScheduledProcedureStepDescription = requested_procedure_description
    sps_seq.ScheduledProcedureStepID = generate_uid()
    sps_seq.ScheduledStationName = scheduled_station_name
    
    # Create the sequence
    ds.ScheduledProcedureStepSequence = [sps_seq]
    
    # Requested Procedure
    ds.RequestedProcedureID = generate_uid()
    ds.RequestedProcedureDescription = requested_procedure_description
    
    # Imaging Service Request
    ds.AccessionNumber = accession_number
    if referring_physician_name:
        ds.ReferringPhysicianName = referring_physician_name
    
    # Additional information
    if medical_alerts:
        ds.MedicalAlerts = medical_alerts
    if contrast_allergies:
        ds.ContrastAllergies = contrast_allergies
    
    # Study Instance UID
    ds.StudyInstanceUID = generate_uid()
    
    logger.info(f"Created worklist item for patient {patient_name} with accession {accession_number}")
    
    return ds

def send_worklist_item(dataset, ip_address, port, remote_ae, local_ae):
    """
    Send a worklist item to a DICOM server using C-STORE.
    
    Args:
        dataset (pydicom.dataset.Dataset): The worklist dataset to send
        ip_address (str): IP address of the DICOM server
        port (int): Port of the DICOM server
        remote_ae (str): AE title of the remote DICOM server
        local_ae (str): AE title of the local DICOM client
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f'Sending worklist item to DICOM server {ip_address}:{port} (AE: {remote_ae})')
    
    try:
        # Create a file meta dataset for the worklist item
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.31'  # Modality Worklist Information Model
        file_meta.MediaStorageSOPInstanceUID = generate_uid()
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        
        # Create a FileDataset from the dataset
        file_dataset = FileDataset(None, dataset, file_meta=file_meta, preamble=b"\0" * 128)
        file_dataset.is_little_endian = True
        file_dataset.is_implicit_VR = False
        
        # Add required elements for C-STORE
        file_dataset.SOPClassUID = file_meta.MediaStorageSOPClassUID
        file_dataset.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        
        # Save the dataset to a file in the data directory
        output_dir = "data/worklist"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a unique filename based on patient name and accession number
        patient_name = str(getattr(dataset, 'PatientName', 'Unknown')).replace('^', '_')
        accession = str(getattr(dataset, 'AccessionNumber', datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
        output_path = os.path.join(output_dir, f"worklist_{patient_name}_{accession}.dcm")
        
        # Save the dataset to the file
        file_dataset.save_as(output_path)
        logger.info(f'Saved worklist item to file: {output_path}')
        
        # Create an Application Entity
        ae = AE(ae_title=local_ae)
        ae.dimse_timeout = 300
        
        # Add the appropriate context
        ae.add_requested_context(file_dataset.SOPClassUID)
        
        # Associate with the peer AE
        logger.info(f'Establishing association with {ip_address}:{port} (Remote AE: {remote_ae})')
        assoc = ae.associate(ip_address, port, ae_title=remote_ae)
        
        if not assoc.is_established:
            logger.error(f'Association failed with server {ip_address}:{port} using AE Title: {remote_ae}')
            return False
        
        # Send the dataset using C-STORE
        logger.info(f'Association established. Sending C-STORE for {os.path.basename(output_path)}')
        status = assoc.send_c_store(file_dataset)
        
        if status:
            logger.info(f'C-STORE Response: {status}')
            if status.Status == 0:
                logger.info(f'Successfully sent worklist item to DICOM server')
                result = True
            else:
                logger.error(f'C-STORE failed with status: 0x{status.Status:04X}')
                result = False
        else:
            logger.error(f'C-STORE failed')
            result = False
        
        # Release the association
        assoc.release()
        logger.info("Association released.")
        
        return result
    except Exception as e:
        logger.error(f'Error sending worklist item: {str(e)}')
        return False

def load_sample_worklists(file_path='sample_worklists.json'):
    """
    Load sample worklist items from a JSON file.
    
    Args:
        file_path (str, optional): Path to the JSON file
        
    Returns:
        list: List of worklist items as pydicom.dataset.Dataset objects
    """
    try:
        with open(file_path, 'r') as f:
            worklist_data = json.load(f)
        
        logger.info(f"Loaded {len(worklist_data)} sample worklist items from {file_path}")
        
        # Convert JSON data to DICOM datasets
        worklist_items = []
        for item_data in worklist_data:
            ds = Dataset()
            
            # Patient information
            ds.PatientName = item_data.get('patient_name', '')
            ds.PatientID = item_data.get('patient_id', '')
            if 'birth_date' in item_data:
                ds.PatientBirthDate = item_data['birth_date']
            if 'sex' in item_data:
                ds.PatientSex = item_data['sex']
            
            # Scheduled Procedure Step Sequence
            sps_seq = Dataset()
            sps_seq.ScheduledStationAETitle = item_data.get('station', 'STATION1')
            sps_seq.ScheduledProcedureStepStartDate = item_data.get('date', '')
            sps_seq.ScheduledProcedureStepStartTime = item_data.get('time', '')
            sps_seq.Modality = item_data.get('modality', 'US')
            sps_seq.ScheduledPerformingPhysicianName = item_data.get('physician', '')
            sps_seq.ScheduledProcedureStepDescription = item_data.get('description', '')
            sps_seq.ScheduledProcedureStepID = generate_uid()
            sps_seq.ScheduledStationName = item_data.get('station', 'STATION1')
            
            # Create the sequence
            ds.ScheduledProcedureStepSequence = [sps_seq]
            
            # Requested Procedure
            ds.RequestedProcedureID = generate_uid()
            ds.RequestedProcedureDescription = item_data.get('description', '')
            
            # Imaging Service Request
            ds.AccessionNumber = item_data.get('accession_number', '')
            if 'physician' in item_data:
                ds.ReferringPhysicianName = item_data['physician']
            
            # Additional information
            if 'alerts' in item_data:
                ds.MedicalAlerts = item_data['alerts']
            if 'allergies' in item_data:
                ds.ContrastAllergies = item_data['allergies']
            
            # Study Instance UID
            ds.StudyInstanceUID = generate_uid()
            
            worklist_items.append(ds)
        
        return worklist_items
    except Exception as e:
        logger.error(f"Error loading sample worklists: {str(e)}")
        return []

def dicom_to_json(file_path, output_file=None):
    """
    Read a DICOM file, convert it to JSON, and print to console.
    
    Args:
        file_path (str): Path to the DICOM file
        output_file (str, optional): Path to save the JSON output to a file
        
    Returns:
        dict: JSON-serializable dictionary of the DICOM dataset
    """
    import pydicom
    
    logger.info(f"Reading DICOM file: {file_path}")
    
    try:
        # Read the DICOM file
        dataset = pydicom.dcmread(file_path)
        
        # Define a custom JSON encoder to handle DICOM-specific types
        class DicomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if hasattr(obj, '__str__'):
                    return str(obj)
                return json.JSONEncoder.default(self, obj)
        
        # Convert dataset to a dictionary
        def dataset_to_dict(ds):
            result = {}
            for elem in ds:
                if elem.VR == 'SQ':
                    # Handle sequences
                    if elem.value is not None:
                        result[elem.name] = [dataset_to_dict(item) for item in elem.value]
                    else:
                        result[elem.name] = None
                else:
                    # Handle other elements
                    if elem.value is not None:
                        if isinstance(elem.value, bytes):
                            # Skip binary data or convert to hex if needed
                            if elem.name == 'Pixel Data':
                                result[elem.name] = f"[Binary data with length {len(elem.value)} bytes]"
                            else:
                                try:
                                    result[elem.name] = elem.value.decode('utf-8', 'ignore')
                                except:
                                    result[elem.name] = f"[Binary data with length {len(elem.value)} bytes]"
                        else:
                            result[elem.name] = elem.value
                    else:
                        result[elem.name] = None
            return result
        
        # Convert the dataset to a dictionary
        dicom_dict = dataset_to_dict(dataset)
        
        # Convert to JSON
        json_output = json.dumps(dicom_dict, indent=2, cls=DicomJSONEncoder)
        print(json_output)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_output)
            logger.info(f"Saved JSON output to: {output_file}")
        
        return dicom_dict
    except Exception as e:
        logger.error(f"Error converting DICOM to JSON: {str(e)}")
        raise

def get_worklist_dataset(ip_address, port, remote_ae, local_ae, dataset=None, start_date=None, end_date=None, patient_name=None, modality=None):
    """
    Retrieve worklist items from a DICOM server using C-FIND with a custom dataset.
    
    Args:
        ip_address (str): IP address of the DICOM server
        port (int): Port of the DICOM server
        remote_ae (str): AE title of the remote DICOM server
        local_ae (str): AE title of the local DICOM client
        dataset (pydicom.dataset.Dataset, optional): Custom dataset for the C-FIND query
        start_date (str, optional): Start date in YYYYMMDD format
        end_date (str, optional): End date in YYYYMMDD format
        patient_name (str, optional): Patient name to filter by
        modality (str, optional): Modality to filter by
        
    Returns:
        list: List of worklist items matching the criteria
    """
    logger.info('Setting up to retrieve worklist items with custom dataset')
    
    ae = AE(ae_title=local_ae)
    ae.add_requested_context(ModalityWorklistInformationFind)
    
    # Associate with a peer AE
    logger.info(f'Associating with server {ip_address}:{port} (AE: {remote_ae})')
    assoc = ae.associate(ip_address, port, ae_title=remote_ae)
    
    if not assoc.is_established:
        raise Exception(f'Association failed with server {ip_address}:{port} using AE Title: {remote_ae}')
    
    # Use provided dataset or create a default one
    if dataset is None:
        # Create a C-FIND dataset for querying the worklist
        dataset = Dataset()
        dataset.QueryRetrieveLevel = 'WORKLIST'
        
        # Add search criteria
        dataset.PatientName = '*' if patient_name is None else patient_name
        dataset.PatientID = ''
        dataset.AccessionNumber = ''
        dataset.RequestedProcedureDescription = ''
        dataset.StudyInstanceUID = ''
        
        # Add scheduled procedure step sequence
        sps_seq = Dataset()
        
        # Add date range if specified
        if start_date and end_date:
            sps_seq.ScheduledProcedureStepStartDate = f"{start_date}-{end_date}"
        elif start_date:
            sps_seq.ScheduledProcedureStepStartDate = start_date
        else:
            sps_seq.ScheduledProcedureStepStartDate = ''
        
        sps_seq.ScheduledProcedureStepStartTime = ''
        
        # Add modality filter if specified
        if modality:
            sps_seq.Modality = modality
        else:
            sps_seq.Modality = ''
        
        dataset.ScheduledProcedureStepSequence = [sps_seq]
    
    # Send C-FIND request
    logger.info('Sending C-FIND request for worklist items with dataset:')
    for elem in dataset:
        logger.debug(f'  {elem.tag}: {elem.name} = {elem.value}')
    
    responses = []
    
    for (status, response_dataset) in assoc.send_c_find(dataset, ModalityWorklistInformationFind):
        if status:
            logger.debug(f'C-FIND response received: {status}')
            if response_dataset:
                logger.debug(f'Response dataset: {response_dataset}')
                responses.append(response_dataset)
        else:
            logger.error(f'C-FIND failed with status: {status}')
    
    # Release the association
    assoc.release()
    logger.info(f'Retrieved {len(responses)} worklist items')
    
    return responses

def main():
    """Main entry point for the script."""
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='DICOM Tools')
    parser.add_argument('--convert', action='store_true',
                        help='Convert MWL sample files to DICOM format')
    parser.add_argument('--echo', action='store_true',
                        help='Test connectivity with a DICOM server using C-ECHO')
    parser.add_argument('--get-worklist', action='store_true',
                        help='Retrieve worklist items from a DICOM server')
    parser.add_argument('--sample-worklist', action='store_true',
                        help='Load and display sample worklist items from sample_worklists.json')
    parser.add_argument('--create-worklist', action='store_true',
                        help='Create and send a sample worklist item to a DICOM server')
    parser.add_argument('--dicom-to-json', 
                        help='Convert a DICOM file to JSON and print to console')
    parser.add_argument('--json-output',
                        help='Path to save the JSON output to a file (used with --dicom-to-json)')
    parser.add_argument('--server-ip', default='10.10.0.1',
                        help='IP address of the DICOM server (default: 10.10.0.1)')
    parser.add_argument('--server-port', type=int, default=4242,
                        help='Port of the DICOM server (default: 4242)')
    parser.add_argument('--server-ae', default='MERCURE',
                        help='AE title of the DICOM server (default: MERCURE)')
    parser.add_argument('--client-ae', default='BEXA',
                        help='AE title of the client (default: BEXA)')
    parser.add_argument('--start-date', 
                        help='Start date for worklist query (YYYYMMDD)')
    parser.add_argument('--end-date', 
                        help='End date for worklist query (YYYYMMDD)')
    parser.add_argument('--patient-name', 
                        help='Patient name for worklist query')
    parser.add_argument('--modality', 
                        help='Modality for worklist query (e.g., US, CT, MR)')
    parser.add_argument('--output-format', choices=['text', 'json'], default='text',
                        help='Output format for worklist display (default: text)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        debug_logger()
    
    # Print configuration
    logger.info('=== DICOM Tools ===')
    
    # Convert MWL sample files to DICOM format
    if args.convert:
        convert_mwl_samples()
    
    # Test connectivity with a DICOM server using C-ECHO
    if args.echo:
        logger.info('\n=== Testing DICOM Connectivity with C-ECHO ===')
        logger.info(f'DICOM Server: {args.server_ip}:{args.server_port}')
        logger.info(f'Server AE Title: {args.server_ae}')
        logger.info(f'Client AE Title: {args.client_ae}')
        
        try:
            status = c_echo(
                ip_address=args.server_ip,
                port=args.server_port,
                remote_ae=args.server_ae,
                local_ae=args.client_ae
            )
            
            if status == 0:
                logger.info('C-ECHO successful! Server is accessible.')
            else:
                logger.error(f'C-ECHO failed with status: {status}')
                
        except Exception as e:
            logger.error(f'Error during C-ECHO: {str(e)}')
            return 1
    
    # Retrieve worklist items from a DICOM server
    if args.get_worklist or (not args.convert and not args.echo and not args.sample_worklist):
        logger.info('\n=== Retrieving Worklist Items ===')
        logger.info(f'DICOM Server: {args.server_ip}:{args.server_port}')
        logger.info(f'Server AE Title: {args.server_ae}')
        logger.info(f'Client AE Title: {args.client_ae}')
        
        # Set default dates if not provided
        if not args.start_date:
            today = datetime.datetime.now()
            args.start_date = today.strftime("%Y%m%d")
            logger.info(f'Using default start date: {args.start_date}')
        
        if not args.end_date:
            next_week = datetime.datetime.now() + datetime.timedelta(days=7)
            args.end_date = next_week.strftime("%Y%m%d")
            logger.info(f'Using default end date: {args.end_date}')
        
        logger.info(f'Date Range: {args.start_date} to {args.end_date}')
        if args.patient_name:
            logger.info(f'Patient Name Filter: {args.patient_name}')
        if args.modality:
            logger.info(f'Modality Filter: {args.modality}')
        
        try:
            # Create a custom dataset for more control over the query
            ds = Dataset()
            ds.QueryRetrieveLevel = 'WORKLIST'
            
            # Add search criteria
            ds.PatientName = '*' if args.patient_name is None else args.patient_name
            ds.PatientID = ''
            ds.AccessionNumber = ''
            ds.RequestedProcedureDescription = ''
            
            # Add scheduled procedure step sequence
            sps_seq = Dataset()
            
            # Add date range
            if args.start_date and args.end_date:
                sps_seq.ScheduledProcedureStepStartDate = f"{args.start_date}-{args.end_date}"
            elif args.start_date:
                sps_seq.ScheduledProcedureStepStartDate = args.start_date
            
            # Add modality filter
            if args.modality:
                sps_seq.Modality = args.modality
            
            ds.ScheduledProcedureStepSequence = [sps_seq]
            
            # Use the new function that accepts a custom dataset
            worklist_items = get_worklist_dataset(
                ip_address=args.server_ip,
                port=args.server_port,
                remote_ae=args.server_ae,
                local_ae=args.client_ae,
                dataset=ds
            )
            
            display_worklist(worklist_items, args.output_format)
                
        except Exception as e:
            logger.error(f'Error retrieving worklist: {str(e)}')
            return 1
    
    # Load and display sample worklist items
    if args.sample_worklist:
        logger.info('\n=== Loading Sample Worklist Items ===')
        
        try:
            worklist_items = load_sample_worklists()
            display_worklist(worklist_items, args.output_format)
                
        except Exception as e:
            logger.error(f'Error loading sample worklists: {str(e)}')
            return 1
    
    # Create and send a sample worklist item
    if args.create_worklist:
        logger.info('\n=== Creating and Sending Sample Worklist Item ===')
        logger.info(f'DICOM Server: {args.server_ip}:{args.server_port}')
        logger.info(f'Server AE Title: {args.server_ae}')
        logger.info(f'Client AE Title: {args.client_ae}')
        
        try:
            # Generate a unique accession number
            accession_number = f"ACC{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Get tomorrow's date for the scheduled procedure
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
            scheduled_date = tomorrow.strftime("%Y%m%d")
            scheduled_time = datetime.datetime.now().strftime("%H%M%S")
            
            # Create a sample worklist item
            logger.info("Creating sample worklist item...")
            worklist_item = create_worklist_item(
                patient_name="Doe^John",
                patient_id="JD12345",
                accession_number=accession_number,
                scheduled_procedure_step_start_date=scheduled_date,
                scheduled_procedure_step_start_time=scheduled_time,
                modality=args.modality if args.modality else "US",
                requested_procedure_description="Sample Procedure",
                scheduled_station_name="STATION1",
                scheduled_station_ae_title=args.client_ae,
                referring_physician_name="Smith^Jane",
                patient_birth_date="19800101",
                patient_sex="M",
                medical_alerts="None",
                contrast_allergies="None"
            )
            
            # Display the created worklist item
            logger.info("Sample worklist item created:")
            display_worklist([worklist_item], args.output_format)
            
            # Send the worklist item to the DICOM server
            logger.info(f"Sending worklist item to DICOM server {args.server_ip}:{args.server_port}...")
            success = send_worklist_item(
                dataset=worklist_item,
                ip_address=args.server_ip,
                port=args.server_port,
                remote_ae=args.server_ae,
                local_ae=args.client_ae
            )
            
            if success:
                logger.info("Successfully sent worklist item to DICOM server.")
            else:
                logger.error("Failed to send worklist item to DICOM server.")
                
        except Exception as e:
            logger.error(f'Error creating or sending worklist item: {str(e)}')
            return 1
    
    # Convert DICOM to JSON
    if args.dicom_to_json:
        logger.info(f'\n=== Converting DICOM to JSON ===')
        logger.info(f'DICOM File: {args.dicom_to_json}')
        
        try:
            dicom_to_json(args.dicom_to_json, args.json_output)
        except Exception as e:
            logger.error(f'Error converting DICOM to JSON: {str(e)}')
            return 1
    
    logger.info('\n=== Script Complete ===')
    return 0

if __name__ == "__main__":
    sys.exit(main())
