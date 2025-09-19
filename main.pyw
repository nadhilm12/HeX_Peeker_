"""
Main entry point for the Hex Peeker application.

This script initializes the PyQt6 application, creates the main window, and starts
the event loop.
"""

import sys
from PyQt6.QtWidgets import QApplication

# It's crucial to add the project root to the Python path if running this script directly.
# This ensures that modules in `core`, `ui`, and `utils` can be found.
# In a packaged application, this might be handled differently.
# try:
#     from ui.main_window import MainWindow
# except ImportError:
#     # This block helps in running the script directly from the project root
#     # for development purposes without needing to install it as a package.
#     project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#     if project_root not in sys.path:
#         sys.path.insert(0, project_root)
#     from ui.main_window import MainWindow

from ui.main_window import MainWindow

def main():
    """
    Initializes and runs the PyQt6 application.
    """
    # Create the application instance.
    app = QApplication(sys.argv)

    # Create and show the main window.
    window = MainWindow()
    window.show()

    # Start the application's event loop.
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
