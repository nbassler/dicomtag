# dicomtag/gui/tree_model.py
import logging

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtGui import QColor
from dicomtag.model.dicom_model import DICOMDataModel

logger = logging.getLogger(__name__)


class DICOMTreeModel(QAbstractItemModel):
    def __init__(self, dicom_data_model: DICOMDataModel, parent=None):
        super().__init__(parent)
        self.dicom_data_model = dicom_data_model
        self.dicom_dataset = self.dicom_data_model.dicom_data

    def rowCount(self, parent=QModelIndex()):
        if not self.dicom_dataset or parent.isValid():
            return 0
        return len(self.dicom_dataset)

    def columnCount(self, parent=QModelIndex()):
        return 3  # Tag Name, Value, and VR Type

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not self.dicom_dataset:
            return None

        dicom_tags = list(self.dicom_dataset.keys())
        dicom_tag = dicom_tags[index.row()]
        dicom_element = self.dicom_dataset[dicom_tag]

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return f"{dicom_tag} ({dicom_element.keyword})"  # Tag Name
            elif index.column() == 1:
                return dicom_element.value  # Value
            elif index.column() == 2:
                return dicom_element.VR  # VR Type (Value Representation)
        elif role == Qt.ItemDataRole.BackgroundRole:
            if index.column() == 1 and dicom_element.VR == 'SQ':
                # Highlight sequences differently for better readability
                return QColor(Qt.GlobalColor.lightGray)

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            headers = ["Tag", "Value", "VR"]
            return headers[section] if section < len(headers) else None
        return None

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        return self.createIndex(row, column)

    def parent(self, index):
        return QModelIndex()  # Flat structure without parent-child relationships for now

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
