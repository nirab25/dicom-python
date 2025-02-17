import os
import datetime
import numpy as np
from PIL import Image
import pydicom
from pydicom.dataset import FileDataset
from pydicom.uid import generate_uid, SecondaryCaptureImageStorage, ExplicitVRLittleEndian
from pynetdicom import AE
from pynetdicom.sop_class import SecondaryCaptureImageStorage
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_dicom_from_image(image_path, patient_name="Anonymous", patient_id="123456"):
    img = Image.open(image_path)

    if img.mode != "RGB":
        img = img.convert("RGB")
    np_img = np.array(img)

    photometric = "RGB"

    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    dt = datetime.datetime.now()
    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)

    ds.is_little_endian = True
    ds.is_implicit_VR = False

    ds.PatientName = patient_name
    ds.PatientID = patient_id

    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()

    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.Modality = "OT"
    ds.SeriesNumber = 1
    ds.InstanceNumber = 1
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
    ds.SamplesPerPixel = 3
    ds.PlanarConfiguration = 0
    ds.PhotometricInterpretation = photometric
    ds.Rows, ds.Columns = np_img.shape[0], np_img.shape[1]
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0

    pixel_data = np_img.tobytes()

    logging.info("Original pixel data length: %d", len(pixel_data))

    if len(pixel_data) % 2 != 0:
        pixel_data += b'\x00'
        logging.info("Pixel data padded, new length: %d", len(pixel_data))

    ds.PixelData = pixel_data
    ds.StudyDate = dt.strftime('%Y%m%d')
    ds.StudyTime = dt.strftime('%H%M%S')
    ds.ContentDate = dt.strftime('%Y%m%d')
    ds.ContentTime = dt.strftime('%H%M%S')
    logging.info("Created DICOM dataset from image: %s", image_path)

    return ds

def upload_image_to_dicom_server(image_path, server_ip, server_port, remote_ae, local_ae, 
                                 patient_name="Anonymous", patient_id="123456",
                                 patient_dob="19700101", exam_date=None, exam_time=None,
                                 examiner="Unknown", accession="N/A", studyUdi=None):
    ds = create_dicom_from_image(image_path, patient_name, patient_id)
    ds.Modality = 'DOC'
    ds.PatientBirthDate = patient_dob
    ds.StudyDescription = 'Ultrasound'
    ds.Manufacturer = "Nirab"

    if exam_date is None:
        exam_date = datetime.datetime.now().strftime('%Y%m%d')
    if exam_time is None:
        exam_time = datetime.datetime.now().strftime('%H%M%S')

    ds.StudyDate = exam_date
    ds.SeriesDate = exam_date
    ds.StudyTime = exam_time
    ds.SeriesTime = exam_time
    ds.OperatorsName = examiner
    ds.AccessionNumber = accession

    # Do not update UIDs here to keep them consistent with file meta
    logging.info("Prepared DICOM dataset for image: %s", image_path)

    ae = AE(ae_title=local_ae)
    ae.dimse_timeout = 300

    ae.add_requested_context(SecondaryCaptureImageStorage)

    logging.info("Establishing association with %s:%s (Remote AE: %s)", server_ip, server_port, remote_ae)
    assoc = ae.associate(server_ip, server_port, ae_title=remote_ae)

    if assoc.is_established:
        logging.info("Association established. Sending C-STORE for %s", os.path.basename(image_path))
        status = assoc.send_c_store(ds)
        if status:
            logging.info("Sent %s with status: 0x%04x", os.path.basename(image_path), status.Status)
        else:
            logging.error("Failed to send %s", os.path.basename(image_path))
        assoc.release()
        logging.info("Association released.")
    else:
        logging.error("Failed to establish association with DICOM server")

if __name__ == '__main__':
    image_path = os.path.join("data", "image_1.png")
    server_ip = "192.168.8.100"
    server_port = 4242
    remote_ae = "ORTHANC"
    local_ae = "Nirab App Client"
    patient_name = "Nirab^Haque"
    patient_id = "123456"
    patient_dob = "19800101"
    exam_date = "20250223"
    exam_time = "101010"
    examiner = "Amdadul^Haque"
    accession = "ACC001"
    studyUdi = generate_uid()

    logging.info("Uploading image: %s", image_path)
    upload_image_to_dicom_server(image_path, server_ip, server_port, remote_ae, local_ae,
                                 patient_name, patient_id, patient_dob, exam_date, exam_time,
                                 examiner, accession, studyUdi)