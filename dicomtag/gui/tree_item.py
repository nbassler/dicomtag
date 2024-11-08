import logging

from PyQt6.QtCore import QModelIndex

from pydicom.datadict import keyword_for_tag

logger = logging.getLogger(__name__)


class DICOMTreeItem:
    def __init__(self, tag, element, parent: 'DICOMTreeItem' = None):
        self.tag = tag
        self.element = element  # Should be pydicom DataElement
        self.child_items = []
        self.parent_item = parent

    def append_child(self, item: 'DICOMTreeItem'):
        """Add a child item to the current item."""
        self.child_items.append(item)

    def child(self, row: int) -> 'DICOMTreeItem':
        """Get the child item at the specified row."""
        if row < 0 or row >= self.child_count():
            return None
        return self.child_items[row]

    def child_count(self) -> int:
        """Get the number of child items."""
        return len(self.child_items)

    def column_count(self) -> int:
        """Get the number of columns for the item."""
        return 3  # Always "Tag, VR, Value"

    def is_sequence(self):
        """Check if the element is a sequence."""
        return hasattr(self.element, "VR") and self.element.VR == "SQ"

    def get_data(self, column):
        """Get the data for the specified column."""
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

    def __repr__(self) -> str:
        return f"DICOMTreeItem(tag={self.tag}, element={self.element})"
