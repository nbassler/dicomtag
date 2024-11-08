# dicomtag/gui/tree_model.py

import logging

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtWidgets import QTreeView, QLineEdit

from dicomtag.gui.tree_item import DICOMTreeItem

logger = logging.getLogger(__name__)


class DICOMTreeModel(QAbstractItemModel):
    def __init__(self, dicom_data_model, parent=None):
        super().__init__(parent)
        self.dicom_data_model = dicom_data_model
        self.dicom_dataset = dicom_data_model.dicom_data if dicom_data_model.dicom_data is not None else {}
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
        # Enable editing only for column 2 (Value) if it's not a sequence
        item = self.items[index.row()]
        if index.column() == 2 and not item.is_sequence():
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        # Non-editable for sequences
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            item = self.items[index.row()]
            logger.debug(f"Attempting to set value for {item.tag}: {value}")

            # Check if the tag exists in the dataset
            if item.tag in self.dicom_dataset:
                try:
                    item.element.value = value  # Attempt to set the new value
                    # Notify view of change
                    self.dataChanged.emit(index, index)
                    return True
                except Exception as e:
                    logger.error(f"Error setting value for {item.tag}: {e}")
            else:
                logger.warning(f"Tag {item.tag} not found in DICOM dataset.")
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
