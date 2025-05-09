#!/usr/bin/env python3
"""
DICOM Communication Module

This module provides functions for communicating with DICOM servers:
- C-ECHO for testing connectivity
- C-FIND for retrieving worklist items
"""

import logging
from pydicom.dataset import Dataset
from pynetdicom import AE
from pynetdicom.sop_class import ModalityWorklistInformationFind

# Configure logging
logger = logging.getLogger(__name__)

def c_echo(ip_address, port, remote_ae, local_ae="MERCURE"):
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

def get_worklist(ip_address, port, remote_ae, local_ae="MERCURE", start_date=None, end_date=None, patient_name=None, modality=None):
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

def get_worklist_dataset(ip_address, port, remote_ae, local_ae="MERCURE", dataset=None, start_date=None, end_date=None, patient_name=None, modality=None):
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
