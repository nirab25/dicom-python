import os
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

def create_and_upload_sample_worklist(
    orthanc_url="http://localhost:8042",
    username=None,
    password=None,
    modality_name="orthanc"
):
    """
    Create and upload a sample worklist item to Orthanc.
    
    Args:
        orthanc_url (str): URL of the Orthanc server
        username (str, optional): Username for Orthanc authentication
        password (str, optional): Password for Orthanc authentication
        modality_name (str, optional): Name of the modality in Orthanc configuration
        
    Returns:
        dict: Response from the Orthanc server
    """
    # Get current date and time
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    
    # Format dates and times
    today_date = today.strftime("%Y%m%d")
    today_time = today.strftime("%H%M%S")
    tomorrow_date = tomorrow.strftime("%Y%m%d")
    
    # Create a sample worklist item
    logging.info("Creating sample worklist item...")
    worklist = create_worklist_item(
        patient_name="Doe^John",
        patient_id="JD12345",
        accession_number="ACC" + today.strftime("%Y%m%d%H%M%S"),
        scheduled_procedure_step_start_date=tomorrow_date,
        scheduled_procedure_step_start_time=today_time,
        modality="US",
        requested_procedure_description="Abdominal Ultrasound",
        scheduled_station_name="STATION1",
        referring_physician_name="Smith^Jane",
        patient_birth_date="19800101",
        patient_sex="M",
        medical_alerts="None",
        contrast_allergies="None"
    )
    
    # Upload the worklist item to Orthanc
    logging.info(f"Uploading worklist item to Orthanc at {orthanc_url}...")
    result = upload_worklist_to_orthanc(
        worklist,
        orthanc_url=orthanc_url,
        username=username,
        password=password,
        modality_name=modality_name
    )
    
    if "error" in result:
        logging.error(f"Failed to upload worklist: {result.get('error')}")
    else:
        logging.info(f"Successfully uploaded worklist. ID: {result.get('ID', 'Unknown')}")
    
    return result

def retrieve_worklists_by_date_range(
    start_date,
    end_date,
    orthanc_url="http://localhost:8042",
    username=None,
    password=None,
    modality_name="orthanc"
):
    """
    Retrieve and display worklist items from Orthanc by date range.
    
    Args:
        start_date (str): Start date in YYYYMMDD format
        end_date (str): End date in YYYYMMDD format
        orthanc_url (str): URL of the Orthanc server
        username (str, optional): Username for Orthanc authentication
        password (str, optional): Password for Orthanc authentication
        modality_name (str, optional): Name of the modality in Orthanc configuration
        
    Returns:
        list: List of worklist items matching the date range
    """
    logging.info(f"Retrieving worklists from {start_date} to {end_date}...")
    
    worklists = get_worklists_by_date_range(
        start_date=start_date,
        end_date=end_date,
        orthanc_url=orthanc_url,
        username=username,
        password=password,
        modality_name=modality_name
    )
    
    if isinstance(worklists, dict) and "error" in worklists:
        logging.error(f"Failed to retrieve worklists: {worklists.get('error')}")
        return []
    
    logging.info(f"Found {len(worklists)} worklist items")
    
    # Display the worklists
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
    
    return worklists

if __name__ == "__main__":
    # Orthanc server configuration
    orthanc_url = "http://localhost:8042"  # Change to your Orthanc server URL
    username = None  # Change if authentication is required
    password = None  # Change if authentication is required
    modality_name = "orthanc"  # Change to match your Orthanc configuration
    
    # Example 1: Create and upload a sample worklist item
    print("\n=== Creating and Uploading Sample Worklist ===")
    result = create_and_upload_sample_worklist(
        orthanc_url=orthanc_url,
        username=username,
        password=password,
        modality_name=modality_name
    )
    print(f"Upload result: {json.dumps(result, indent=2)}")
    
    # Example 2: Retrieve worklists by date range
    print("\n=== Retrieving Worklists by Date Range ===")
    # Get today and tomorrow's dates
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    next_week = today + datetime.timedelta(days=7)
    
    # Format dates
    today_date = today.strftime("%Y%m%d")
    tomorrow_date = tomorrow.strftime("%Y%m%d")
    next_week_date = next_week.strftime("%Y%m%d")
    
    # Retrieve worklists for the next week
    worklists = retrieve_worklists_by_date_range(
        start_date=today_date,
        end_date=next_week_date,
        orthanc_url=orthanc_url,
        username=username,
        password=password,
        modality_name=modality_name
    )
    
    print("\n=== Example Complete ===")
    print("You can modify the script parameters to match your Orthanc server configuration.")
