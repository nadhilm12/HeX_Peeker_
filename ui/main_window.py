"""
Defines the main window of the Hex Peeker application.

This module brings all components together: the core logic, utility functions,
and the HexViewer widget, orchestrating them to provide the application's functionality.
"""

import os
import re
import sys
from typing import List, Optional

# --- PyQt6 Imports ---
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSplitter, QFileDialog, QMessageBox, QProgressBar, QStatusBar,
    QLineEdit, QComboBox, QLabel, QTextEdit, QFormLayout
)
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QFont

# --- Project Imports ---
from ui.hex_viewer import HexViewer
from core.worker import Worker
from core.hex_core import smart_parse_to_temp
from core.comparator import compare_two_files
from core.temp_manager import get_temp_path
from utils.exporter import export_diff_report, export_view_data # <-- IMPORT NEW FUNCTION
from helpers.search_worker import SearchWorker


def load_bin_as_bytes(bin_path: str) -> bytes:
    try:
        with open(bin_path, 'rb') as f:
            return f.read()
    except Exception as e:
        raise IOError(f"Failed to read binary file: {bin_path}") from e

class MainWindow(QMainWindow):
    """
    The main application window, responsible for UI layout and event handling.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hex Peeker v3.4 - Sync Scroll")
        self.setGeometry(100, 100, 1600, 900)

        # --- Application State ---
        self.file_paths: List[Optional[str]] = [None, None]
        self.bytes_data: List[Optional[bytes]] = [None, None]
        self.differences: List[tuple] = []
        self.current_worker: Optional[Worker] = None
        self.search_thread: Optional[QThread] = None
        self.search_worker: Optional[SearchWorker] = None
        self.found_offsets: List[int] = []
        self.current_search_index: int = -1
        self._is_syncing_scroll = False # Flag to prevent scroll loops

        # --- Theme Management ---
        self.is_dark_mode = False
        self.dark_stylesheet = self._load_stylesheet()

        self._build_ui()
        self._connect_signals()
        self.enable_ui()
        self.log("Ready. Please load a file.")

    def _load_stylesheet(self) -> str:
        """Loads the QSS file for the dark theme."""
        try:
            style_path = os.path.join(os.path.dirname(__file__), 'dark_theme.qss')
            with open(style_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            self.log("WARN: dark_theme.qss not found. Theme toggle will not work.")
            return ""

    def log(self, message: str):
        """Append a message to the log console and the status bar."""
        self.log_console.append(message)
        self.status_bar.showMessage(message)

    def _build_ui(self):
        """Constructs the user interface widgets and layouts based on the new design."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 1. Search Bar ---
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter text (ASCII) or hex string...")
        self.search_mode = QComboBox(self)
        self.search_mode.addItems(["Teks (ASCII)", "Hexadecimal"])
        self.btn_search = QPushButton("Cari")
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.search_status = QLabel("")

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_mode)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_prev)
        search_layout.addWidget(self.btn_next)
        search_layout.addStretch()
        search_layout.addWidget(self.search_status)
        main_layout.addLayout(search_layout)

        # --- 2. File Loading Area ---
        file_controls_layout = QHBoxLayout()
        
        form1_layout = QFormLayout()
        self.btn_load1 = QPushButton("Load File 1...")
        self.path_label1 = QLineEdit(self)
        self.path_label1.setReadOnly(True)
        self.path_label1.setPlaceholderText("Lokasi file direktori yang terload")
        form1_layout.addRow(self.btn_load1, self.path_label1)
        
        form2_layout = QFormLayout()
        self.btn_load2 = QPushButton("Load File 2...")
        self.path_label2 = QLineEdit(self)
        self.path_label2.setReadOnly(True)
        self.path_label2.setPlaceholderText("Lokasi file direktori yang terload")
        form2_layout.addRow(self.btn_load2, self.path_label2)

        file_controls_layout.addLayout(form1_layout)
        file_controls_layout.addLayout(form2_layout)
        main_layout.addLayout(file_controls_layout)

        # --- 3. Action Buttons ---
        action_layout = QHBoxLayout()
        self.btn_compare = QPushButton("Compare")
        self.btn_export_diff = QPushButton("Export Diff...")
        self.btn_export_view1 = QPushButton("Export File 1")
        self.btn_export_view2 = QPushButton("Export File 2")
        self.btn_toggle_theme = QPushButton("Toggle Theme")
        self.btn_cancel = QPushButton("Cancel Process")
        action_layout.addWidget(self.btn_compare)
        action_layout.addWidget(self.btn_export_diff)
        action_layout.addWidget(self.btn_export_view1)
        action_layout.addWidget(self.btn_export_view2)
        action_layout.addWidget(self.btn_toggle_theme)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_cancel)
        main_layout.addLayout(action_layout)

        # --- 4. Main Content Area (Resizable) ---
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.viewer1 = HexViewer()
        self.viewer2 = HexViewer()
        self.splitter.addWidget(self.viewer1)
        self.splitter.addWidget(self.viewer2)
        main_splitter.addWidget(self.splitter)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Courier", 9))
        main_splitter.addWidget(self.log_console)

        main_splitter.setSizes([700, 150])
        main_layout.addWidget(main_splitter, 1)

        # --- 5. Progress and Status Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _connect_signals(self):
        """Connects widget signals to their corresponding handler slots."""
        self.btn_load1.clicked.connect(lambda: self.browse_file(0))
        self.btn_load2.clicked.connect(lambda: self.browse_file(1))
        self.btn_compare.clicked.connect(self.compare_files)
        self.btn_export_diff.clicked.connect(self.export_diff_report_handler)
        self.btn_export_view1.clicked.connect(lambda: self.export_view_data_handler(0))
        self.btn_export_view2.clicked.connect(lambda: self.export_view_data_handler(1))
        self.btn_cancel.clicked.connect(self.cancel_current_process)
        self.btn_toggle_theme.clicked.connect(self.toggle_theme)

        self.btn_search.clicked.connect(self.start_search)
        self.btn_next.clicked.connect(self.find_next)
        self.btn_prev.clicked.connect(self.find_prev)
        self.search_input.returnPressed.connect(self.start_search)

        self.viewer1.cell_selected.connect(lambda offset: self.on_hex_cell_selected(0, offset))
        self.viewer2.cell_selected.connect(lambda offset: self.on_hex_cell_selected(1, offset))

        # --- Sync Scrolling ---
        self.viewer1.verticalScrollBar().valueChanged.connect(self._sync_scroll_2)
        self.viewer2.verticalScrollBar().valueChanged.connect(self._sync_scroll_1)

    def _sync_scroll_1(self, value):
        """Syncs viewer1 to match viewer2's scroll position."""
        if self._is_syncing_scroll:
            return
        self._is_syncing_scroll = True
        self.viewer1.verticalScrollBar().setValue(value)
        self._is_syncing_scroll = False

    def _sync_scroll_2(self, value):
        """Syncs viewer2 to match viewer1's scroll position."""
        if self._is_syncing_scroll:
            return
        self._is_syncing_scroll = True
        self.viewer2.verticalScrollBar().setValue(value)
        self._is_syncing_scroll = False

    def toggle_theme(self):
        app = QApplication.instance()
        if not app: return

        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            app.setStyleSheet(self.dark_stylesheet)
            self.log("Switched to Dark Mode.")
        else:
            app.setStyleSheet("")
            self.log("Switched to Light Mode.")

        self.viewer1.update_theme_colors(self.is_dark_mode)
        self.viewer2.update_theme_colors(self.is_dark_mode)

        if self.differences:
            # Re-apply differences with the new theme
            self.viewer1.set_differences(self.differences, is_left=True)
            self.viewer2.set_differences(self.differences, is_left=False)

    def browse_file(self, index: int):
        file_filter = "All Files (*);;Hex/Text Files (*.hex *.txt);;Binary Files (*.exe *.xlsx *.PNG)"
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", file_filter)
        if path:
            self.file_paths[index] = path
            if index == 0:
                self.path_label1.setText(path)
            else:
                self.path_label2.setText(path)
            self.load_file(index, path)

    # --- Worker-driven Handlers ---

    def load_file(self, index: int, path: str):
        self.disable_ui()
        self.log(f"Processing file: {os.path.basename(path)}...")
        self.progress_bar.setRange(0, 0)

        worker = Worker(self._load_file_task, path, f"view_{index}.bin")
        worker.finished.connect(lambda data: self.on_load_finished(index, data))
        worker.error.connect(self.on_worker_error)
        self.current_worker = worker
        worker.start()

    def compare_files(self):
        if self.bytes_data[0] is None or self.bytes_data[1] is None:
            self.on_worker_error("Both files must be loaded before comparing.")
            return

        self.disable_ui()
        self.log("Comparing files...")
        self.viewer1.clear_highlights()
        self.viewer2.clear_highlights()
        self.viewer1.clearSelection()
        self.viewer2.clearSelection()
        
        max_len = max(len(self.bytes_data[0]), len(self.bytes_data[1]))
        self.progress_bar.setRange(0, max_len)

        worker = Worker(compare_two_files, self.bytes_data[0], self.bytes_data[1])
        worker.finished.connect(self.on_compare_finished)
        worker.error.connect(self.on_worker_error)
        worker.progress.connect(self.update_progress)
        self.current_worker = worker
        worker.start()

    def export_diff_report_handler(self):
        self.disable_ui()
        self.log("Opening export dialog for diff report...")
        worker = Worker(export_diff_report, self.differences)
        worker.finished.connect(lambda: self.log("Diff report export process finished."))
        worker.finished.connect(self.enable_ui)
        worker.error.connect(self.on_worker_error)
        self.current_worker = worker
        worker.start()

    def export_view_data_handler(self, index: int):
        if self.bytes_data[index] is None:
            QMessageBox.warning(self, "No Data", f"Please load a file into View {index + 1} first.")
            return

        self.disable_ui()
        self.log(f"Opening export dialog for view {index + 1}...")
        
        # Set progress bar for export
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        worker = Worker(export_view_data, self.bytes_data[index])
        worker.finished.connect(lambda: self.log(f"View {index + 1} data export process finished."))
        worker.finished.connect(self.enable_ui)
        worker.error.connect(self.on_worker_error)
        worker.progress.connect(self.update_progress)  # Connect progress signal
        self.current_worker = worker
        worker.start()

    def cancel_current_process(self):
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.quit()
            self.search_thread.wait()
        self.log("Process cancelled by user.")
        self.enable_ui()

    def start_search(self):
        if self.bytes_data[0] is None:
            QMessageBox.warning(self, "Peringatan", "Muat File 1 terlebih dahulu.")
            return
        query = self.search_input.text()
        if not query: return

        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.quit()
            self.search_thread.wait()

        self.search_thread = QThread()
        self.search_worker = SearchWorker()
        self.search_worker.moveToThread(self.search_thread)
        self.search_worker.found_offsets.connect(self.on_search_finished)
        self.search_worker.error.connect(self.on_worker_error)
        self.search_thread.started.connect(lambda: self.search_worker.run(self.bytes_data[0], query, self.search_mode.currentText()))
        self.search_worker.finished.connect(self.search_thread.quit)
        self.search_worker.finished.connect(self.search_worker.deleteLater)
        self.search_thread.finished.connect(self.search_thread.deleteLater)

        self.disable_ui()
        self.log(f"Searching for '{query}'...")
        self.search_thread.start()

    # --- Worker Callback Slots ---

    def on_search_finished(self, offsets: List[int]):
        self.found_offsets = offsets
        self.current_search_index = -1
        self.search_status.setText(f"Found: {len(offsets)}")
        self.log("Search complete.")
        self.enable_ui()
        if offsets:
            self.find_next()
        else:
            self.viewer1.clearSelection()

    def find_next(self):
        if not self.found_offsets: return
        self.current_search_index = (self.current_search_index + 1) % len(self.found_offsets)
        self._jump_to_search_result()

    def find_prev(self):
        if not self.found_offsets: return
        self.current_search_index = (self.current_search_index - 1 + len(self.found_offsets)) % len(self.found_offsets)
        self._jump_to_search_result()

    def _jump_to_search_result(self):
        offset = self.found_offsets[self.current_search_index]
        query_text = self.search_input.text()
        if self.search_mode.currentText() == 'Hexadecimal':
            query_len = len(bytes.fromhex(re.sub(r'[^0-9a-fA-F]', '', query_text)))
        else:
            query_len = len(query_text.encode('ascii', errors='ignore'))
        self.viewer1.jump_to_offset(offset, query_len)
        self.search_status.setText(f"Result {self.current_search_index + 1}/{len(self.found_offsets)}")

    def on_hex_cell_selected(self, viewer_index: int, offset: int):
        pass

    def on_load_finished(self, index: int, data: bytes):
        try:
            if not data and self.current_worker and self.current_worker.is_cancelled():
                self.log("File loading cancelled.")
            else:
                self.bytes_data[index] = data
                viewer = self.viewer1 if index == 0 else self.viewer2
                viewer.load_bytes(self.bytes_data[index])
                self.log(f"File loaded successfully. {len(data):,} bytes.")
        except Exception as e:
            self.on_worker_error(f"Failed to display processed file: {e}")
        finally:
            self.enable_ui()

    def on_compare_finished(self, diffs: List[tuple]):
        self.differences = diffs
        self.viewer1.set_differences(diffs, is_left=True)
        self.viewer2.set_differences(diffs, is_left=False)
        self.log(f"Comparison complete. Found {len(diffs):,} differences.")
        self.enable_ui()

    def on_worker_error(self, error_message: str):
        self.log(f"Error: {error_message}")
        QMessageBox.critical(self, "Operation Failed", error_message)
        self.enable_ui()

    def update_progress(self, value: int):
        if self.progress_bar.maximum() == 0:
            self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(value)

    # --- UI State Management ---

    def disable_ui(self):
        self.btn_load1.setEnabled(False)
        self.btn_load2.setEnabled(False)
        self.btn_compare.setEnabled(False)
        self.btn_export_diff.setEnabled(False)
        self.btn_export_view1.setEnabled(False)
        self.btn_export_view2.setEnabled(False)
        self.btn_search.setEnabled(False)
        self.btn_toggle_theme.setEnabled(False)
        self.btn_cancel.setEnabled(True)

    def enable_ui(self):
        self.btn_load1.setEnabled(True)
        self.btn_load2.setEnabled(True)
        self.btn_compare.setEnabled(all(self.bytes_data))
        self.btn_export_diff.setEnabled(bool(self.differences))
        self.btn_export_view1.setEnabled(self.bytes_data[0] is not None)
        self.btn_export_view2.setEnabled(self.bytes_data[1] is not None)
        self.btn_search.setEnabled(self.bytes_data[0] is not None)
        self.btn_toggle_theme.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.current_worker = None

    # --- Static Task Methods for Worker ---

    @staticmethod
    def _load_file_task(in_path: str, temp_filename: str, progress_cb=None, cancel_cb=None) -> bytes:
        temp_path = smart_parse_to_temp(in_path, temp_filename)
        if cancel_cb and cancel_cb():
            return b''
        data = load_bin_as_bytes(temp_path)
        return data