# dicomtag/gui/tree_model.py

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtWidgets import QTreeView, QLineEdit
from pydicom import Dataset
from pydicom.datadict import keyword_for_tag
from pydicom import Dataset, Sequence, DataElement
from pydicom.dataelem import RawDataElement
import logging

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


class DICOMTreeModel(QAbstractItemModel):
    def __init__(self, dicom_data_model, parent=None):
        super().__init__(parent)
        self.dicom_data_model = dicom_data_model
        self.dicom_dataset = dicom_data_model.dicom_data
        self.items = [DICOMTreeItem(tag, self.dicom_dataset[tag])
                      for tag in self.dicom_dataset.keys()]

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.items)

    def columnCount(self, parent=QModelIndex()):
        return 3  # Tag, Value, VR

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        item = self.items[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return item.get_data(index.column())

        elif role == Qt.ItemDataRole.BackgroundRole and item.is_sequence() and index.column() == 1:
            # Highlight sequences for readability
            from PyQt6.QtGui import QColor
            return QColor(Qt.GlobalColor.lightGray)

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            headers = ["Tag", "VR", "Value"]
            return headers[section] if section < len(headers) else None
        return None

    def index(self, row, column, parent=QModelIndex()):
        if self.hasIndex(row, column, parent):
            return self.createIndex(row, column, self.items[row])
        return QModelIndex()

    def parent(self, index):
        return QModelIndex()  # Flat structure, no parent-child relationships

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        # Enable editing only for column 2 (Value)
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | (
            Qt.ItemFlag.ItemIsEditable if index.column() == 2 else Qt.ItemFlag.NoItemFlags
        )

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            item = self.items[index.row()]
            if index.column() == 2:  # Value column
                item.element.value = value
                # Notify the view that data has changed
                self.dataChanged.emit(index, index)
                return True
        return False

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        item = self.items[index.row()]
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return item.get_data(index.column())
        return None


class CustomTreeView(QTreeView):
    """Custom QTreeView subclass to enable single-click editing of the Value column only."""

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid() and index.column() == 2:  # Check if it's column 2
            self.edit(index)  # Start editing the cell directly
            event.accept()  # Accept the event to prevent further processing
        else:
            super().mousePressEvent(event)  # Handle other clicks normally

    def edit(self, index, trigger=QTreeView.EditTrigger.DoubleClicked, event=None):
        if not index.isValid():
            return False  # Return False if the index is not valid

        # Call the base edit method to open the editor
        edit_success = super().edit(index, trigger, event)

        # Ensure the editor has focus and select all text if editing was successful
        editor = self.indexWidget(index)
        if editor and isinstance(editor, QLineEdit):
            editor.selectAll()  # Highlight all text in the editor

        return edit_success  # Return whether the edit was successful
