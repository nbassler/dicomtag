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

        if self.is_sequence():
            logger.debug(f"Initializing children for sequence: {tag}")
            self._initialize_children()  # Initialize sequence items as children

    def append_child(self, item: 'DICOMTreeItem'):
        """Add a child item to the current item."""
        self.child_items.append(item)

    def child(self, row: int) -> 'DICOMTreeItem':
        """Get the child item at the specified row."""
        if row < 0 or row >= self.child_count():
            return None
        return self.child_items[row]

    def last_child(self):
        return self.child_items[-1] if self.child_items else None

    def child_count(self) -> int:
        """Get the number of child items."""
        return len(self.child_items)

    def child_number(self) -> int:
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def column_count(self) -> int:
        """Get the number of columns for the item."""
        return 3  # Always "Tag, VR, Value"

    def parent(self):
        return self.parent_item

    def is_sequence(self):
        """Check if the element is a sequence."""
        return hasattr(self.element, "VR") and self.element.VR == "SQ"

    def _initialize_children(self):
        """Create children if this item is a sequence."""
        for i, dataset in enumerate(self.element.value):
            seq_label = f"Item {i + 1}"
            seq_item = DICOMTreeItem(seq_label, dataset, self)
            self.append_child(seq_item)
            # Recursively add child items to each sequence item
            for sub_tag in dataset.keys():
                sub_element = dataset[sub_tag]
                child = DICOMTreeItem(sub_tag, sub_element, self)
                logger.debug(f"Adding child: {sub_tag}")
                seq_item.append_child(child)

    def get_data(self, column: int):
        """Get the data for the specified column."""
        if column == 0:
            # Display tag ID and keyword
            keyword = keyword_for_tag(self.tag) or "Unknown"
            # logger.debug(f"Tag: {self.tag}, Keyword: {keyword}")
            return f"{self.tag} ({keyword})"
        elif column == 1:
            # Display VR type if available
            # logger.debug(f"VR: {self.element.VR}")
            return self.element.VR  # if hasattr(self.element, 'VR') else ""
        elif column == 2:
            # Display the value directly, label as "Sequence" if it's an SQ element
            # logger.debug(f"Value: {self.element.value}")
            return str(self.element.value) if not self.is_sequence() else "Sequence"
        return None

    def set_data(self, column: int, value):
        if column != 2:
            return False

        logger.debug(f"Setting value: {value} at tag: {self.tag}")
        self.element.value = value
        return True

    def __repr__(self) -> str:
        return f"DICOMTreeItem(tag={self.tag}, element={self.element})"
