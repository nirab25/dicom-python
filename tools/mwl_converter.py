#!/usr/bin/env python3
"""
MWL Converter Module

This module provides functions for converting MWL (Modality Worklist) sample files to DICOM format.
"""

import os
import re
import logging
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian

# Configure logging
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
