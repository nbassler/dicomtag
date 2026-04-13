# dicomtag/gui/tree_model.py
# https://doc.qt.io/qtforpython-6/examples/example_widgets_itemviews_editabletreemodel.html
import logging

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QTimer
from PyQt6.QtWidgets import QApplication, QTreeView, QLineEdit

from dicomtag.gui.tree_item import DICOMTreeItem

logger = logging.getLogger(__name__)


class DICOMTreeModel(QAbstractItemModel):
    def __init__(self, dicom_data_model, parent=None):
        super().__init__(parent)
        self.dicom_data_model = dicom_data_model
        self.root_item = DICOMTreeItem("Root", None)
        if dicom_data_model.dicom_data:
            self._setup_model_data(dicom_data_model.dicom_data, self.root_item)

    def update_model_data(self):
        """Clears and rebuilds the model data."""
        self.beginResetModel()
        self.root_item.child_items = []
        if self.dicom_data_model.dicom_data is not None:
            self._setup_model_data(self.dicom_data_model.dicom_data, self.root_item)
        self.endResetModel()

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
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # Mandatory # noqa: N802
        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item: DICOMTreeItem = self.get_item(parent)
        if not parent_item:
            return 0
        return parent_item.child_count()

    def columnCount(self, parent=QModelIndex()):  # Mandatory # noqa: N802
        return 3  # Tag, VR, Value

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

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # Mandatory # noqa: N802
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            headers = ["Tag", "VR", "Value"]
            return headers[section] if section < len(headers) else None
        return None

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:  # Mandatory # noqa: N802
        """Return the index for the specified row, column, and parent index."""
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item: DICOMTreeItem = self.get_item(parent)
        if not parent_item:
            return QModelIndex()

        child_item: DICOMTreeItem | None = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:  # type: ignore[override]
        if not child.isValid():
            return QModelIndex()

        child_item: DICOMTreeItem | None = self.get_item(child)
        if child_item:
            parent_item: DICOMTreeItem | None = child_item.parent()
        else:
            parent_item = None
        if parent_item == self.root_item or not parent_item:
            return QModelIndex()
        return self.createIndex(parent_item.child_number(), 0, parent_item)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        item = self.get_item(index)
        if index.column() == 2 and item.element is not None and not item.is_sequence():
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    # mandatory for editing
    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:  # noqa: N802
        if role != Qt.ItemDataRole.EditRole:
            return False

        item: DICOMTreeItem = self.get_item(index)
        result: bool = item.set_data(index.column(), value)

        if result:
            self.dataChanged.emit(index, index,
                                  [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])

        return result


class CustomTreeView(QTreeView):
    """Custom QTreeView subclass to enable single-click editing of the Value column only."""

    def mousePressEvent(self, e):  # noqa: N802
        # Call super first so the row gets selected/highlighted normally.
        super().mousePressEvent(e)
        assert e is not None
        index = self.indexAt(e.pos())
        if index.isValid() and index.column() == 2:
            self.edit(index)
            # Delegate editors are not accessible via indexWidget(); use a
            # zero-delay timer to select all text once the editor has focus.
            QTimer.singleShot(0, _select_all_in_focused_editor)


def _select_all_in_focused_editor():
    widget = QApplication.focusWidget()
    if isinstance(widget, QLineEdit):
        widget.selectAll()
