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
from pynetdicom import debug_logger

# Import modules from tools package
from tools.mwl_converter import convert_mwl_samples
from tools.dicom_communication import c_echo, get_worklist, get_worklist_dataset
from tools.worklist_manager import create_worklist_item, send_worklist_item, load_sample_worklists, display_worklist
from tools.utils import dicom_to_json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    parser.add_argument('--client-ae', default='MERCURE',
                        help='AE title of the client (default: MERCURE)')
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
            # Use the get_worklist function with the provided parameters
            worklist_items = get_worklist(
                ip_address=args.server_ip,
                port=args.server_port,
                remote_ae=args.server_ae,
                local_ae=args.client_ae,
                start_date=args.start_date,
                end_date=args.end_date,
                patient_name=args.patient_name,
                modality=args.modality
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
