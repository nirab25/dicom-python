#!/usr/bin/env python3
"""
Worklist Manager Module

This module provides functions for creating, managing, and displaying DICOM worklist items.
"""

import os
import json
import logging
import datetime
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
from pynetdicom import AE

# Configure logging
logger = logging.getLogger(__name__)

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

def send_worklist_item(dataset, ip_address, port, remote_ae, local_ae="MERCURE"):
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
        output_dir = "worklist"
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
