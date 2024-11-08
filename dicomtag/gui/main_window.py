# dicomtag/gui/main_window.py

import os
import logging
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QTreeView, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction
from dicomtag.gui.tree_model import DICOMTreeItem, DICOMTreeModel, CustomTreeView
from dicomtag.model.dicom_model import DICOMDataModel

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
        self._setup_menu()

    def _setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout for central widget
        layout = QVBoxLayout(central_widget)

        # QTreeView for displaying DICOM tags
        self.tree_view = CustomTreeView()
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setAlternatingRowColors(True)

        # Set up the custom tree model for the QTreeView
        self.tree_model = DICOMTreeModel(self.dicom_data_model)
        self.tree_view.setModel(self.tree_model)

        # Add the tree view to the layout
        layout.addWidget(self.tree_view)

        # Resize columns to fit their contents
        self.tree_view.resizeColumnToContents(0)  # Resize Tag column
        self.tree_view.resizeColumnToContents(1)  # Resize VR column

        # Prevent the last section from stretching
        header = self.tree_view.header()
        header.setStretchLastSection(True)

        # Set the horizontal header to allow for scrollable content
        header.setSectionsMovable(True)

        # Enable editing on double-click or single click in column 2
        self.tree_view.setEditTriggers(
            QTreeView.EditTrigger.DoubleClicked | QTreeView.EditTrigger.EditKeyPressed)

        # Set default window size
        self.resize(800, 600)

    def _setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        # Create "Open" action
        open_action = QAction("&Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Create "Save As" action
        save_as_action = QAction("&Save As", self)
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)

        # Add an exit action
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open DICOM File", "", "DICOM Files (*.dcm);;All Files (*)")
        if filename:
            logger.info(f"Loading DICOM file: {filename}")
            self.dicom_data_model.load_dicom_file(filename)

            # Ensure that the model updates to reflect the new data
            self.update_tree_model()  # Update the tree model to show new data

    def update_tree_model(self):
        # Update the tree model with new data
        self.tree_model.items = [DICOMTreeItem(
            tag, self.dicom_data_model.dicom_data[tag]) for tag in self.dicom_data_model.dicom_data.keys()]
        self.tree_view.reset()  # Refresh the view to reflect the new model data

        # Resize columns based on their content
        self.tree_view.resizeColumnToContents(0)  # Resize Tag column
        self.tree_view.resizeColumnToContents(1)  # Resize VR column

    def save_as_file(self):
        original_filename = self.dicom_data_model.filename or "untitled.dcm"
        new_filename, _ = QFileDialog.getSaveFileName(
            self, "Save DICOM File", f"{os.path.splitext(original_filename)[0]}_EDITED.dcm", "DICOM Files (*.dcm);;All Files (*)")
        if new_filename:
            self.dicom_data_model.save_dicom_file(new_filename)
