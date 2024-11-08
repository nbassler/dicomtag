# dicomtag/main.py

import sys
import argparse
import logging
from PyQt6.QtWidgets import QApplication
from dicomtag.gui.main_window import MainWindow
from dicomtag.model.dicom_model import DICOMDataModel

__version__ = "0.1.0"  # Replace with dynamic version if using setuptools_scm

# Configure logger
logger = logging.getLogger(__name__)


def configure_logging(verbosity: int):
    """Set the logging level based on verbosity."""
    if verbosity >= 3:
        logging_level = logging.DEBUG
    elif verbosity == 2:
        logging_level = logging.INFO
    elif verbosity == 1:
        logging_level = logging.WARNING
    else:
        logging_level = logging.ERROR
    logging.basicConfig(level=logging_level)
    logger.debug(f"Logging level set to {logging.getLevelName(logging_level)}")


def main(args=None):
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='View and Edit DICOM tags.')
    parser.add_argument('inputfile', nargs='?',
                        help='Input DICOM filename', type=str)
    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity (e.g., -v, -vv, -vvv)')
    parser.add_argument('-V', '--version', action='version',
                        version=f'dicomtag {__version__}')
    args = parser.parse_args(args)

    # Configure logging based on verbosity level
    configure_logging(args.verbosity)

    # Initialize the application
    app = QApplication(sys.argv)

    # Create the DICOM data model and load the specified file, if provided
    dicom_data_model = DICOMDataModel()
    if args.inputfile:
        logger.info(f"Loading DICOM file: {args.inputfile}")
        dicom_data_model.load_dicom_file(args.inputfile)
    else:
        logger.warning(
            "No input file specified. The application will start without a DICOM file loaded.")

    # Create and show the main window, passing the DICOM model
    window = MainWindow(dicom_data_model)
    window.show()

    # Start the Qt event loop
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
