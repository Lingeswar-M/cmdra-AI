"""
cmdra AI - Offline Desktop AI Assistant
Main entry point for the application.
"""
import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Initialize logging first
from utils.logger import setup_logger
setup_logger()

from ui.main_window import MainWindow
import config

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info("Starting cmdra AI - Offline Desktop AI Assistant")
    logger.info("=" * 60)
    
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("cmdra AI")
    app.setOrganizationName("cmdra AI")
    if config.ICON_PATH and QIcon(config.ICON_PATH).isNull() is False:
        app_icon = QIcon(config.ICON_PATH)
        app.setWindowIcon(app_icon)
    else:
        app_icon = QIcon()
    
    # Create and show main window
    logger.info("Initializing main window...")
    window = MainWindow()
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)
    window.show()
    
    logger.info("cmdra AI is ready!")
    logger.info("Type a command and press Send")
    
    # Run application
    exit_code = app.exec_()
    
    logger.info("cmdra AI shutting down...")
    logger.info("=" * 60)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()


