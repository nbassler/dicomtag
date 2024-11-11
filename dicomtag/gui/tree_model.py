# dicomtag/gui/tree_model.py
# https://doc.qt.io/qtforpython-6/examples/example_widgets_itemviews_editabletreemodel.html
import logging

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtWidgets import QTreeView, QLineEdit

from dicomtag.gui.tree_item import DICOMTreeItem

logger = logging.getLogger(__name__)


class DICOMTreeModel(QAbstractItemModel):
    def __init__(self, dicom_data_model, parent=None):
        super().__init__(parent)
        self.dicom_data_model = dicom_data_model
        self.root_item = DICOMTreeItem("Root", None)

        self._setup_model_data(dicom_data_model.dicom_data, self.root_item)

    def update_model_data(self):
        """Clears and rebuilds the model data."""
        self.beginResetModel()  # Notify view that a reset is starting
        self.root_item.child_items = []  # Clear existing children
        self._setup_model_data(
            self.dicom_data_model.dicom_data, self.root_item)
        self.endResetModel()  # Notify view that reset has completed

    def _setup_model_data(self, dataset, parent):
        """Recursively create DICOMTreeItem instances for each DICOM element."""
        for tag in dataset.keys():
            element = dataset[tag]
            item = DICOMTreeItem(tag, element, parent)
            parent.append_child(item)

    def get_item(self, index: QModelIndex = QModelIndex()) -> DICOMTreeItem:
        if index.isValid():
            item: DICOMTreeItem = index.internalPointer()
            if item:
                return item

        return self.root_item

    # What follows are Mandatory methods for QAbstractItemModel:
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # Mandatory
        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item: DICOMTreeItem = self.get_item(parent)
        if not parent_item:
            return 0
        return parent_item.child_count()

    def columnCount(self, parent=QModelIndex()):  # Mandatory
        return 3  # Tag, Value, VR

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Return the data for the specified index and role."""
        if not index.isValid():
            return None

        item = self.get_item(index)
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return item.data(index.column())
        elif role == Qt.ItemDataRole.BackgroundRole and item.is_sequence() and index.column() == 1:
            # Highlight sequences for readability
            from PyQt6.QtGui import QColor
            return QColor(Qt.GlobalColor.lightGray)
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # Mandatory
        """Return the header data for the specified section, orientation, and role."""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            headers = ["Tag", "VR", "Value"]
            return headers[section] if section < len(headers) else None
        return None

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:  # Mandatory
        """Return the index for the specified row, column, and parent index."""
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item: DICOMTreeItem = self.get_item(parent)
        if not parent_item:
            return QModelIndex()

        child_item: DICOMTreeItem = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index):  # Mandatory
        if not index.isValid():
            return QModelIndex()

        child_item: DICOMTreeItem = self.get_item(index)
        if child_item:
            parent_item: DICOMTreeItem = child_item.parent()
        else:
            parent_item = None
        if parent_item == self.root_item or not parent_item:
            return QModelIndex()
        return self.createIndex(parent_item.child_number(), 0, parent_item)

    def flags(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        # Enable editing only for column 2 (Value) if it's not a sequence
        item = self.get_item(index)
        if index.column() == 2 and not item.is_sequence():
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        # Non-editable for sequences
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    # mandatory for editing
    def setData(self, index: QModelIndex, value, role: int) -> bool:
        if role != Qt.ItemDataRole.EditRole:
            return False

        item: DICOMTreeItem = self.get_item(index)
        result: bool = item.set_data(index.column(), value)

        if result:
            self.dataChanged.emit(index, index,
                                  [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])

        return result

    # stictly also setHeaderData()


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
