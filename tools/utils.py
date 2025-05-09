#!/usr/bin/env python3
"""
DICOM Utilities Module

This module provides utility functions for working with DICOM files.
"""

import json
import logging
import pydicom

# Configure logging
logger = logging.getLogger(__name__)

def dicom_to_json(file_path, output_file=None):
    """
    Read a DICOM file, convert it to JSON, and print to console.
    
    Args:
        file_path (str): Path to the DICOM file
        output_file (str, optional): Path to save the JSON output to a file
        
    Returns:
        dict: JSON-serializable dictionary of the DICOM dataset
    """
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
