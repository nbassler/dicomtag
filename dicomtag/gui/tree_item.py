import logging
from PyQt6.QtCore import QModelIndex

from pydicom.datadict import keyword_for_tag

logger = logging.getLogger(__name__)


class DICOMTreeItem:
    def __init__(self, tag, element):
        self.tag = tag
        self.element = element  # Should be pydicom DataElement
        logger.debug(
            f"Initializing DICOMTreeItem with tag: {self.tag}, element type: {type(self.element)} element VR: {self.element.VR}")

    def get_data(self, column):
        if column == 0:
            # Display tag ID and keyword
            keyword = keyword_for_tag(self.tag) or "Unknown"
            logger.debug(f"Tag: {self.tag}, Keyword: {keyword}")
            return f"{self.tag} ({keyword})"
        elif column == 1:
            # Display VR type if available
            logger.debug(f"VR: {self.element.VR}")
            return self.element.VR  # if hasattr(self.element, 'VR') else ""
        elif column == 2:
            # Display the value directly, label as "Sequence" if it's an SQ element
            logger.debug(f"Value: {self.element.value}")
            return str(self.element.value) if not self.is_sequence() else "Sequence"

        return None

    def is_sequence(self):
        # Determines if the element is a Sequence
        return hasattr(self.element, "VR") and self.element.VR == "SQ"
