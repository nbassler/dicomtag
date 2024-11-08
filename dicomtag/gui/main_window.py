# dicomtag/gui/main_window.py

from PyQt6.QtWidgets import QMainWindow, QTreeView, QVBoxLayout, QWidget, QHeaderView
import logging
from dicomtag.gui.tree_model import DICOMTreeModel

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, dicom_data_model):
        super().__init__()
        logger.debug("Initializing main window")
        self.setWindowTitle("DICOM Tag Viewer")

        # Use the DICOM data model passed from main
        self.dicom_data_model = dicom_data_model

        # Set up the main layout and tree view
        self._setup_ui()

    def _setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout for central widget
        layout = QVBoxLayout(central_widget)

        # QTreeView for displaying DICOM tags
        self.tree_view = QTreeView()
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setAlternatingRowColors(True)

        # Set up the custom tree model for the QTreeView
        self.tree_model = DICOMTreeModel(self.dicom_data_model)
        self.tree_view.setModel(self.tree_model)

        # Add the tree view to the layout
        layout.addWidget(self.tree_view)

        # Resize columns to fit the content initially
        self.tree_view.header().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree_view.header().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents)

        # Set default window size
        self.resize(800, 600)
