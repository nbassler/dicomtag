# dicom_model.py

import pydicom
import logging

from pydicom.dataset import Dataset

from typing import Optional

logger = logging.getLogger(__name__)


class DICOMDataModel:
    def __init__(self):
        self.dicom_data: Optional[Dataset] = None

    def load_dicom_file(self, file_path: str) -> None:
        """Loads a DICOM file and stores it as a pydicom Dataset."""
        try:
            self.dicom_data = pydicom.dcmread(file_path)
            logger.info(f"Successfully loaded DICOM file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to load DICOM file: {file_path} - {e}")
            self.dicom_data = None

    def save_dicom_file(self, file_path: str) -> bool:
        """Saves the current DICOM data to a file."""
        if self.dicom_data:
            try:
                self.dicom_data.save_as(file_path)
                logger.info(f"Successfully saved DICOM file: {file_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to save DICOM file: {file_path} - {e}")
                return False
        else:
            logger.warning("No DICOM data to save.")
            return False

    def get_tag_value(self, tag: str):
        """Retrieves the value of a specific DICOM tag, if it exists."""
        if self.dicom_data and tag in self.dicom_data:
            return self.dicom_data[tag].value
        else:
            logger.warning(f"Tag {tag} not found in DICOM data.")
            return None

    def set_tag_value(self, tag: str, value) -> bool:
        """Sets the value of a specific DICOM tag, if it exists."""
        if self.dicom_data:
            if tag in self.dicom_data:
                self.dicom_data[tag].value = value
                logger.info(f"Set tag {tag} to {value}")
                return True
            else:
                logger.warning(f"Tag {tag} not found in DICOM data.")
        return False
