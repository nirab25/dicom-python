import os
import datetime
import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid
import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_worklist_item(
    patient_name,
    patient_id,
    accession_number,
    scheduled_procedure_step_start_date,
    scheduled_procedure_step_start_time,
    modality="US",
    requested_procedure_description="Ultrasound",
    scheduled_station_name="STATION1",
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
    sps_seq.ScheduledStationAETitle = scheduled_station_name
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
    
    logging.info(f"Created worklist item for patient {patient_name} with accession {accession_number}")
    
    return ds

def upload_worklist_to_orthanc(
    worklist_dataset,
    orthanc_url="http://localhost:8042",
    username=None,
    password=None,
    modality_name="orthanc"
):
    """
    Upload a DICOM worklist item to Orthanc via REST API.
    
    Args:
        worklist_dataset (pydicom.dataset.Dataset): The worklist dataset to upload
        orthanc_url (str, optional): URL of the Orthanc server. Defaults to "http://localhost:8042".
        username (str, optional): Username for Orthanc authentication. Defaults to None.
        password (str, optional): Password for Orthanc authentication. Defaults to None.
        modality_name (str, optional): Name of the modality in Orthanc configuration. Defaults to "orthanc".
        
    Returns:
        dict: Response from the Orthanc server
    """
    # Save the dataset to a temporary file and read the binary data
    import tempfile
    import os
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.dcm') as temp_file:
        temp_path = temp_file.name
    
    # Save the dataset to the temporary file
    worklist_dataset.is_little_endian = True
    worklist_dataset.is_implicit_VR = False
    worklist_dataset.save_as(temp_path)
    
    # Read the binary data from the temporary file
    with open(temp_path, 'rb') as f:
        binary_data = f.read()
    
    # Delete the temporary file
    os.unlink(temp_path)
    
    # Authentication
    auth = None
    if username and password:
        auth = (username, password)
    
    # Upload the worklist to Orthanc
    headers = {'Content-Type': 'application/dicom'}
    
    # Endpoint for uploading DICOM data
    upload_url = f"{orthanc_url}/instances"
    
    try:
        response = requests.post(
            upload_url,
            data=binary_data,
            headers=headers,
            auth=auth
        )
        
        if response.status_code == 200:
            result = response.json()
            logging.info(f"Successfully uploaded worklist item. ID: {result.get('ID', 'Unknown')}")
            return result
        else:
            logging.error(f"Failed to upload worklist. Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return {"error": response.text, "status_code": response.status_code}
            
    except Exception as e:
        logging.error(f"Error uploading worklist: {str(e)}")
        return {"error": str(e)}

def get_worklists_by_date_range(
    start_date,
    end_date,
    orthanc_url="http://localhost:8042",
    username=None,
    password=None,
    modality_name="orthanc"
):
    """
    Retrieve worklist items from Orthanc by date range.
    
    Args:
        start_date (str): Start date in YYYYMMDD format
        end_date (str): End date in YYYYMMDD format
        orthanc_url (str, optional): URL of the Orthanc server. Defaults to "http://localhost:8042".
        username (str, optional): Username for Orthanc authentication. Defaults to None.
        password (str, optional): Password for Orthanc authentication. Defaults to None.
        modality_name (str, optional): Name of the modality in Orthanc configuration. Defaults to "orthanc".
        
    Returns:
        list: List of worklist items matching the date range
    """
    # Authentication
    auth = None
    if username and password:
        auth = (username, password)
    
    # Create a DICOM C-FIND query for worklists
    query = {
        "Level": "WorkList",
        "Query": {
            "ScheduledProcedureStepSequence": {
                "Sequence": [
                    {
                        "ScheduledProcedureStepStartDate": f"{start_date}-{end_date}"
                    }
                ]
            },
            "PatientName": "",
            "PatientID": "",
            "AccessionNumber": "",
            "RequestedProcedureDescription": "",
            "StudyInstanceUID": ""
        }
    }
    
    # Endpoint for querying worklists
    find_url = f"{orthanc_url}/modalities/{modality_name}/find-worklist"
    
    try:
        response = requests.post(
            find_url,
            json=query,
            auth=auth
        )
        
        if response.status_code == 200:
            results = response.json()
            logging.info(f"Found {len(results)} worklist items in date range {start_date} to {end_date}")
            
            # Process the results to extract relevant information
            worklists = []
            for result in results:
                # Get the full details of each worklist item
                instance_url = f"{orthanc_url}/instances/{result}"
                instance_response = requests.get(instance_url, auth=auth)
                
                if instance_response.status_code == 200:
                    instance_data = instance_response.json()
                    
                    # Extract simplified information
                    simplified = {
                        "ID": result,
                        "PatientName": instance_data.get("PatientName", ""),
                        "PatientID": instance_data.get("PatientID", ""),
                        "AccessionNumber": instance_data.get("AccessionNumber", ""),
                        "ScheduledDate": instance_data.get("ScheduledProcedureStepStartDate", ""),
                        "ScheduledTime": instance_data.get("ScheduledProcedureStepStartTime", ""),
                        "Modality": instance_data.get("Modality", ""),
                        "Description": instance_data.get("RequestedProcedureDescription", "")
                    }
                    
                    worklists.append(simplified)
            
            return worklists
        else:
            logging.error(f"Failed to query worklists. Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return {"error": response.text, "status_code": response.status_code}
            
    except Exception as e:
        logging.error(f"Error querying worklists: {str(e)}")
        return {"error": str(e)}

def get_worklist_details(
    worklist_id,
    orthanc_url="http://localhost:8042",
    username=None,
    password=None
):
    """
    Get detailed information about a specific worklist item.
    
    Args:
        worklist_id (str): The Orthanc ID of the worklist item
        orthanc_url (str, optional): URL of the Orthanc server. Defaults to "http://localhost:8042".
        username (str, optional): Username for Orthanc authentication. Defaults to None.
        password (str, optional): Password for Orthanc authentication. Defaults to None.
        
    Returns:
        dict: Detailed information about the worklist item
    """
    # Authentication
    auth = None
    if username and password:
        auth = (username, password)
    
    # Endpoint for getting instance details
    instance_url = f"{orthanc_url}/instances/{worklist_id}"
    
    try:
        response = requests.get(
            instance_url,
            auth=auth
        )
        
        if response.status_code == 200:
            instance_data = response.json()
            logging.info(f"Retrieved details for worklist item {worklist_id}")
            return instance_data
        else:
            logging.error(f"Failed to get worklist details. Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return {"error": response.text, "status_code": response.status_code}
            
    except Exception as e:
        logging.error(f"Error getting worklist details: {str(e)}")
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    # Example: Create and upload a worklist item
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    
    # Format dates and times
    today_date = today.strftime("%Y%m%d")
    today_time = today.strftime("%H%M%S")
    tomorrow_date = tomorrow.strftime("%Y%m%d")
    
    # Create a worklist item
    worklist = create_worklist_item(
        patient_name="Test^Patient",
        patient_id="TP12345",
        accession_number="ACC12345",
        scheduled_procedure_step_start_date=tomorrow_date,
        scheduled_procedure_step_start_time=today_time,
        modality="US",
        requested_procedure_description="Abdominal Ultrasound",
        scheduled_station_name="STATION1",
        referring_physician_name="Referring^Doctor",
        patient_birth_date="19800101",
        patient_sex="M"
    )
    
    # Upload the worklist item to Orthanc
    # Uncomment and modify with your Orthanc server details
    # result = upload_worklist_to_orthanc(
    #     worklist,
    #     orthanc_url="http://localhost:8042",
    #     username="orthanc",
    #     password="orthanc"
    # )
    # print(result)
    
    # Example: Get worklists by date range
    # Uncomment and modify with your Orthanc server details
    # worklists = get_worklists_by_date_range(
    #     start_date=today_date,
    #     end_date=tomorrow_date,
    #     orthanc_url="http://localhost:8042",
    #     username="orthanc",
    #     password="orthanc"
    # )
    # print(json.dumps(worklists, indent=2))
