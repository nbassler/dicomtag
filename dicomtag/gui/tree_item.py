import logging
from pydicom.datadict import keyword_for_tag

logger = logging.getLogger(__name__)

_MAX_VALUE_LEN = 256


class DICOMTreeItem:
    def __init__(self, tag, element, parent: 'DICOMTreeItem' = None):
        self.tag = tag
        self.element = element  # pydicom DataElement
        self.child_items = []
        self.parent_item = parent

        if self.is_sequence():
            logger.debug(f"Initializing children for sequence: {tag}")
            self._initialize_children()

    def is_sequence(self):
        """Check if the element is a sequence."""
        return hasattr(self.element, "VR") and self.element.VR == "SQ"

    def _initialize_children(self):
        """Create an intermediate node per sequence item, then recurse into its tags."""
        for i, seq_dataset in enumerate(self.element.value):
            seq_item = DICOMTreeItem(f"Item {i}", None)
            self.append_child(seq_item)
            for sub_tag in seq_dataset.keys():
                sub_item = DICOMTreeItem(sub_tag, seq_dataset[sub_tag])
                seq_item.append_child(sub_item)

    def append_child(self, item: 'DICOMTreeItem'):
        """Add a child item to the current item."""
        item.parent_item = self
        self.child_items.append(item)

    def child(self, row: int) -> 'DICOMTreeItem':
        """Get the child item at the specified row."""
        if row < 0 or row >= self.child_count():
            return None
        return self.child_items[row]

    def child_count(self) -> int:
        return len(self.child_items)

    def child_number(self) -> int:
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def column_count(self) -> int:
        return 3  # Tag, VR, Value

    def data(self, column: int):
        """Get the data for the specified column."""
        if self.element is None:
            # Intermediate sequence-item node (or invisible root)
            return str(self.tag) if column == 0 else None
        if column == 0:
            logger.debug(f"Getting data for tag: '{self.tag}'")
            keyword = keyword_for_tag(self.tag) or "Unknown"
            return f"{self.tag}   {keyword}"
        elif column == 1:
            return self.element.VR
        elif column == 2:
            if self.is_sequence():
                return "(Sequence)"
            val = str(self.element.value)
            return val[:_MAX_VALUE_LEN] + "..." if len(val) > _MAX_VALUE_LEN else val
        return None

    def set_data(self, column: int, value):
        """Set the value if the column is editable."""
        if column == 2 and self.element is not None and not self.is_sequence():
            logger.debug(f"Setting value: {value} at tag: {self.tag}")
            self.element.value = value
            return True
        return False

    def parent(self):
        return self.parent_item

    def __repr__(self) -> str:
        return f"DICOMTreeItem(tag={self.tag}, element={self.element})"
