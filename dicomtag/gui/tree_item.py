import logging
from pydicom.datadict import keyword_for_tag

logger = logging.getLogger(__name__)


class DICOMTreeItem:
    def __init__(self, tag, element, parent: 'DICOMTreeItem' = None):
        self.tag = tag
        self.element = element  # pydicom DataElement
        self.child_items = []
        self.parent_item = parent

        if self.is_sequence():
            logger.debug(f"Initializing children for sequence: {tag}")
            self._initialize_children()  # Recursively create children for sequences

    def is_sequence(self):
        """Check if the element is a sequence."""
        return hasattr(self.element, "VR") and self.element.VR == "SQ"

    def _initialize_children(self):
        """Create children for each dataset item in the sequence."""
        for i, seq_dataset in enumerate(self.element.value):
            # Recursively add sub-items within the sequence item
            # Create a parent item for each sequence
            for sub_tag in seq_dataset.keys():
                sub_element = seq_dataset[sub_tag]
                sub_item_data = DICOMTreeItem(
                    sub_tag, sub_element, self.parent)
                self.append_child(sub_item_data)

    def append_child(self, item: 'DICOMTreeItem'):
        """Add a child item to the current item."""
        item.parent_item = self  # Ensure child has correct parent
        self.child_items.append(item)

    def child(self, row: int) -> 'DICOMTreeItem':
        """Get the child item at the specified row."""
        if row < 0 or row >= self.child_count():
            return None
        return self.child_items[row]

    def child_count(self) -> int:
        """Get the number of child items."""
        return len(self.child_items)

    def child_number(self) -> int:
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def column_count(self) -> int:
        return 3  # Tag, VR, Value

    def data(self, column: int):
        """Get the data for the specified column."""
        if column == 0:
            # Display tag ID and keyword
            logger.debug(f"Getting data for tag: '{self.tag}'")
            keyword = keyword_for_tag(self.tag) or "Unknown"
            return f"{self.tag}   {keyword}"
        elif column == 1:
            # Display VR type if available
            return self.element.VR
        elif column == 2:
            # Display the value directly, label as "Sequence" if it's an SQ element
            return str(self.element.value) if not self.is_sequence() else "(Sequence)"
        return None

    def set_data(self, column: int, value):
        """Set the value if the column is editable."""
        if column == 2 and not self.is_sequence():
            logger.debug(f"Setting value: {value} at tag: {self.tag}")
            self.element.value = value
            return True
        return False

    def parent(self):
        return self.parent_item  # Access parent node

    def __repr__(self) -> str:
        return f"DICOMTreeItem(tag={self.tag}, element={self.element})"
