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

    def is_sequence(self):
        """Check if the element is a sequence."""
        return hasattr(self.element, "VR") and self.element.VR == "SQ"

    def _initialize_children(self):
        """Create children if this item is a sequence."""
        for i, dataset in enumerate(self.element.value):
            seq_label = f"Item {i + 1}"
            # Sequence item as parent
            seq_item = DICOMTreeItem(seq_label, dataset, self)
            self.append_child(seq_item)
            # Recursively add child items for each sequence
            for sub_tag in dataset.keys():
                sub_element = dataset[sub_tag]
                child = DICOMTreeItem(sub_tag, sub_element, seq_item)
                logger.debug(f"Adding child: {sub_tag} to sequence {self.tag}")
                seq_item.append_child(child)

    def get_data(self, column: int):
        """Get the data for the specified column."""
        if column == 0:
            # Display tag ID and keyword
            keyword = keyword_for_tag(self.tag) or "Unknown"
            return f"{self.tag} ({keyword})"
        elif column == 1:
            # Display VR type if available
            return self.element.VR
        elif column == 2:
            # Display the value directly, label as "Sequence" if it's an SQ element
            return str(self.element.value) if not self.is_sequence() else "Sequence"
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
