#!/usr/bin/env python3
"""
DICOM Modality Worklist CLI for Orthanc

This script provides a command-line interface for managing DICOM Modality Worklist items
in an Orthanc server using REST API.

Usage:
    python worklist_cli.py create --patient-name "Doe^John" --patient-id "JD12345" ...
    python worklist_cli.py list --start-date 20250501 --end-date 20250531
    python worklist_cli.py get --id "worklist-id"
"""

import os
import sys
import argparse
import datetime
import json
import logging
from worklist import (
    create_worklist_item,
    upload_worklist_to_orthanc,
    get_worklists_by_date_range,
    get_worklist_details
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_argparse():
    """Set up command-line argument parsing."""
    parser = argparse.ArgumentParser(description='DICOM Modality Worklist CLI for Orthanc')
    
    # Common arguments for all commands
    parser.add_argument('--orthanc-url', default='http://localhost:8042',
                        help='URL of the Orthanc server (default: http://localhost:8042)')
    parser.add_argument('--username', help='Username for Orthanc authentication')
    parser.add_argument('--password', help='Password for Orthanc authentication')
    parser.add_argument('--modality', default='orthanc',
                        help='Name of the modality in Orthanc configuration (default: orthanc)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create worklist command
    create_parser = subparsers.add_parser('create', help='Create and upload a worklist item')
    create_parser.add_argument('--patient-name', required=True, help='Patient name (Last^First)')
    create_parser.add_argument('--patient-id', required=True, help='Patient ID')
    create_parser.add_argument('--accession', required=True, help='Accession number')
    create_parser.add_argument('--date', help='Scheduled procedure date (YYYYMMDD), defaults to tomorrow')
    create_parser.add_argument('--time', help='Scheduled procedure time (HHMMSS), defaults to current time')
    create_parser.add_argument('--modality-type', default='US', help='Modality type (default: US)')
    create_parser.add_argument('--description', default='Ultrasound', help='Procedure description')
    create_parser.add_argument('--station', default='STATION1', help='Station name')
    create_parser.add_argument('--physician', help='Referring physician name (Last^First)')
    create_parser.add_argument('--birth-date', help='Patient birth date (YYYYMMDD)')
    create_parser.add_argument('--sex', choices=['M', 'F', 'O'], help='Patient sex (M/F/O)')
    create_parser.add_argument('--alerts', help='Medical alerts')
    create_parser.add_argument('--allergies', help='Contrast allergies')
    
    # List worklists command
    list_parser = subparsers.add_parser('list', help='List worklist items by date range')
    list_parser.add_argument('--start-date', required=True, help='Start date (YYYYMMDD)')
    list_parser.add_argument('--end-date', required=True, help='End date (YYYYMMDD)')
    list_parser.add_argument('--output', choices=['text', 'json'], default='text',
                            help='Output format (default: text)')
    
    # Get worklist details command
    get_parser = subparsers.add_parser('get', help='Get details of a specific worklist item')
    get_parser.add_argument('--id', required=True, help='Worklist item ID')
    get_parser.add_argument('--output', choices=['text', 'json'], default='text',
                           help='Output format (default: text)')
    
    # Batch create command
    batch_parser = subparsers.add_parser('batch', help='Create multiple worklist items from a JSON file')
    batch_parser.add_argument('--file', required=True, help='JSON file containing worklist items')
    
    return parser

def create_worklist_command(args):
    """Handle the create worklist command."""
    # Set default date and time if not provided
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    
    if not args.date:
        args.date = tomorrow.strftime("%Y%m%d")
    
    if not args.time:
        args.time = today.strftime("%H%M%S")
    
    logger.info(f"Creating worklist item for patient {args.patient_name}")
    
    # Create the worklist item
    worklist = create_worklist_item(
        patient_name=args.patient_name,
        patient_id=args.patient_id,
        accession_number=args.accession,
        scheduled_procedure_step_start_date=args.date,
        scheduled_procedure_step_start_time=args.time,
        modality=args.modality_type,
        requested_procedure_description=args.description,
        scheduled_station_name=args.station,
        referring_physician_name=args.physician if args.physician else "",
        patient_birth_date=args.birth_date if args.birth_date else "",
        patient_sex=args.sex if args.sex else "",
        medical_alerts=args.alerts if args.alerts else "",
        contrast_allergies=args.allergies if args.allergies else ""
    )
    
    # Upload the worklist item to Orthanc
    logger.info(f"Uploading worklist item to Orthanc at {args.orthanc_url}")
    result = upload_worklist_to_orthanc(
        worklist_dataset=worklist,
        orthanc_url=args.orthanc_url,
        username=args.username,
        password=args.password,
        modality_name=args.modality
    )
    
    if "error" in result:
        logger.error(f"Failed to upload worklist: {result.get('error')}")
        return False
    
    logger.info(f"Successfully uploaded worklist. ID: {result.get('ID', 'Unknown')}")
    print(json.dumps(result, indent=2))
    return True

def list_worklists_command(args):
    """Handle the list worklists command."""
    logger.info(f"Retrieving worklists from {args.start_date} to {args.end_date}")
    
    worklists = get_worklists_by_date_range(
        start_date=args.start_date,
        end_date=args.end_date,
        orthanc_url=args.orthanc_url,
        username=args.username,
        password=args.password,
        modality_name=args.modality
    )
    
    if isinstance(worklists, dict) and "error" in worklists:
        logger.error(f"Failed to retrieve worklists: {worklists.get('error')}")
        return False
    
    logger.info(f"Found {len(worklists)} worklist items")
    
    # Display the worklists
    if args.output == 'json':
        print(json.dumps(worklists, indent=2))
    else:
        if worklists:
            print("\n=== Worklist Items ===")
            for i, item in enumerate(worklists, 1):
                print(f"\nWorklist #{i}:")
                print(f"  Patient: {item.get('PatientName', 'N/A')}")
                print(f"  Patient ID: {item.get('PatientID', 'N/A')}")
                print(f"  Accession: {item.get('AccessionNumber', 'N/A')}")
                print(f"  Date: {item.get('ScheduledDate', 'N/A')}")
                print(f"  Time: {item.get('ScheduledTime', 'N/A')}")
                print(f"  Modality: {item.get('Modality', 'N/A')}")
                print(f"  Description: {item.get('Description', 'N/A')}")
                print(f"  ID: {item.get('ID', 'N/A')}")
        else:
            print("\nNo worklist items found for the specified date range.")
    
    return True

def get_worklist_command(args):
    """Handle the get worklist details command."""
    logger.info(f"Retrieving details for worklist item {args.id}")
    
    details = get_worklist_details(
        worklist_id=args.id,
        orthanc_url=args.orthanc_url,
        username=args.username,
        password=args.password
    )
    
    if isinstance(details, dict) and "error" in details:
        logger.error(f"Failed to retrieve worklist details: {details.get('error')}")
        return False
    
    # Display the worklist details
    if args.output == 'json':
        print(json.dumps(details, indent=2))
    else:
        print("\n=== Worklist Details ===")
        for key, value in details.items():
            print(f"{key}: {value}")
    
    return True

def batch_create_command(args):
    """Handle the batch create command."""
    try:
        with open(args.file, 'r') as f:
            worklist_items = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON file: {str(e)}")
        return False
    
    if not isinstance(worklist_items, list):
        logger.error("JSON file must contain a list of worklist items")
        return False
    
    logger.info(f"Creating {len(worklist_items)} worklist items")
    
    success_count = 0
    for i, item in enumerate(worklist_items, 1):
        logger.info(f"Processing item {i}/{len(worklist_items)}")
        
        # Create the worklist item
        try:
            worklist = create_worklist_item(
                patient_name=item.get('patient_name', ''),
                patient_id=item.get('patient_id', ''),
                accession_number=item.get('accession_number', ''),
                scheduled_procedure_step_start_date=item.get('date', ''),
                scheduled_procedure_step_start_time=item.get('time', ''),
                modality=item.get('modality', 'US'),
                requested_procedure_description=item.get('description', 'Ultrasound'),
                scheduled_station_name=item.get('station', 'STATION1'),
                referring_physician_name=item.get('physician', ''),
                patient_birth_date=item.get('birth_date', ''),
                patient_sex=item.get('sex', ''),
                medical_alerts=item.get('alerts', ''),
                contrast_allergies=item.get('allergies', '')
            )
            
            # Upload the worklist item to Orthanc
            result = upload_worklist_to_orthanc(
                worklist_dataset=worklist,
                orthanc_url=args.orthanc_url,
                username=args.username,
                password=args.password,
                modality_name=args.modality
            )
            
            if "error" in result:
                logger.error(f"Failed to upload item {i}: {result.get('error')}")
            else:
                logger.info(f"Successfully uploaded item {i}. ID: {result.get('ID', 'Unknown')}")
                success_count += 1
                
        except Exception as e:
            logger.error(f"Error processing item {i}: {str(e)}")
    
    logger.info(f"Batch processing complete. {success_count}/{len(worklist_items)} items uploaded successfully.")
    return True

def main():
    """Main entry point for the CLI."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle commands
    if args.command == 'create':
        success = create_worklist_command(args)
    elif args.command == 'list':
        success = list_worklists_command(args)
    elif args.command == 'get':
        success = get_worklist_command(args)
    elif args.command == 'batch':
        success = batch_create_command(args)
    else:
        parser.print_help()
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
