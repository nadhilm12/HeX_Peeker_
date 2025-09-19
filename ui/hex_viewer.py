"""
Defines the HexViewer custom widget for displaying binary data.

This module contains the `HexViewer` class, a `QTableWidget` subclass optimized
for displaying data in a traditional hex editor layout (address, hex, ASCII).
It uses UI virtualization to handle large files efficiently.
"""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtCore import pyqtSignal, Qt
from typing import List, Tuple, Optional, Dict

class HexViewer(QTableWidget):
    """
    A custom table widget optimized for displaying file content in hexadecimal format.
    It uses on-demand rendering (virtualization) to handle large files.
    """
    cell_selected = pyqtSignal(int)

    def __init__(self):
        """Initializes the HexViewer widget."""
        super().__init__()

        self._data: bytes = b''
        self._diff_map: Dict[int, Tuple[str, Optional[int], Optional[int]]] = {}
        self._is_left_viewer: bool = False

        # --- Theme-aware Colors ---
        self.light_theme_colors = {
            'replace': QColor(255, 215, 0, 150),
            'delete': QColor(255, 99, 71, 150),
            'insert': QColor(60, 179, 113, 150),
            'default_bg': self.palette().color(QPalette.ColorRole.Base)
        }
        self.dark_theme_colors = {
            'replace': QColor(255, 165, 0),
            'delete': QColor(220, 20, 60),
            'insert': QColor(0, 200, 0),
            'default_bg': QColor("#3C3F41")
        }
        self.active_colors = self.light_theme_colors

        self.setColumnCount(18)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)

        font = QFont("Courier New", 10)
        self.setFont(font)
        self.verticalHeader().setVisible(False)

        headers = [f"{i:X}" for i in range(16)]
        self.setHorizontalHeaderLabels(["Address"] + headers + ["ASCII"])

        header_view = self.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, 80)
        for i in range(1, 17):
            self.setColumnWidth(i, 30)
        self.setColumnWidth(17, 130)

        self.cellClicked.connect(self._handle_cell_clicked)
        self.verticalScrollBar().valueChanged.connect(self.update_visible_rows)

    def update_theme_colors(self, is_dark: bool):
        """Switches the active color palette for highlights."""
        self.active_colors = self.dark_theme_colors if is_dark else self.light_theme_colors
        self.update_visible_rows() # Redraw with new colors

    def load_bytes(self, data: bytes):
        self.setUpdatesEnabled(False)
        self.clearContents()
        self.clear_highlights()
        
        self._data = data
        num_rows = (len(self._data) + 15) // 16
        self.setRowCount(num_rows)
        
        self.setUpdatesEnabled(True)
        self.update_visible_rows()

    def update_visible_rows(self, value: int = 0):
        if not self._data and not self._diff_map:
            return

        first_visible_row = self.rowAt(0)
        if first_visible_row == -1:
            first_visible_row = self.verticalScrollBar().value()

        last_visible_row = self.rowAt(self.viewport().height() - 1)
        if last_visible_row == -1:
            last_visible_row = first_visible_row + self.verticalScrollBar().pageStep()

        first_row = max(0, first_visible_row - 20)
        last_row = min(self.rowCount(), last_visible_row + 20)

        self.setUpdatesEnabled(False)
        for row in range(first_row, last_row):
            addr = row * 16
            # Populate address column
            if not self.item(row, 0):
                addr_item = QTableWidgetItem(f"{addr:08X}")
                addr_item.setForeground(QColor('gray'))
                self.setItem(row, 0, addr_item)

            ascii_chars = []
            for col in range(16):
                offset = addr + col
                item_exists = self.item(row, col + 1) is not None

                # Only update if item doesn't exist or if there are diffs to handle
                if not item_exists or self._diff_map:
                    byte_val = self._data[offset] if offset < len(self._data) else None
                    
                    if byte_val is not None:
                        if not item_exists:
                            hex_item = QTableWidgetItem(f"{byte_val:02X}")
                            self.setItem(row, col + 1, hex_item)
                        else:
                            hex_item = self.item(row, col + 1)
                        
                        # Apply highlighting
                        self._apply_cell_highlight(hex_item, offset)
                        ascii_chars.append(chr(byte_val) if 32 <= byte_val <= 126 else '.')
                    elif not item_exists:
                        self.setItem(row, col + 1, QTableWidgetItem(""))

            # Populate ASCII column
            if not self.item(row, 17) and ascii_chars:
                ascii_item = QTableWidgetItem("".join(ascii_chars))
                self.setItem(row, 17, ascii_item)

        self.setUpdatesEnabled(True)

    def _apply_cell_highlight(self, item: QTableWidgetItem, offset: int):
        """Applies background color to a cell based on the diff map."""
        diff_info = self._diff_map.get(offset)
        if diff_info:
            status, _, _ = diff_info
            if status == 'replace':
                item.setBackground(self.active_colors['replace'])
            elif status == 'delete' and self._is_left_viewer:
                item.setBackground(self.active_colors['delete'])
            elif status == 'insert' and not self._is_left_viewer:
                item.setBackground(self.active_colors['insert'])
            else:
                item.setBackground(self.active_colors['default_bg'])
        else:
            item.setBackground(self.active_colors['default_bg'])

    def _handle_cell_clicked(self, row, column):
        if column > 0 and column < 17:
            offset = (row * 16) + (column - 1)
            if offset < len(self._data):
                self.cell_selected.emit(offset)

    def jump_to_offset(self, offset: int, length: int):
        if not self._data or offset >= len(self._data):
            return

        target_row = offset // 16
        self.clearSelection()
        self.scrollToItem(self.item(target_row, 0) or self.takeItem(target_row, 0), QAbstractItemView.ScrollHint.PositionAtTop)
        
        for i in range(length):
            current_offset = offset + i
            row = current_offset // 16
            col = (current_offset % 16) + 1
            if row < self.rowCount() and col < self.columnCount():
                item = self.item(row, col)
                if item:
                    item.setSelected(True)

    def set_differences(self, diffs: List[tuple], is_left: bool):
        """Builds a lookup map for differences and triggers a UI refresh."""
        self._is_left_viewer = is_left
        self._diff_map = {offset: (status, b1, b2) for status, offset, b1, b2 in diffs}
        self.update_visible_rows()

    def clear_highlights(self):
        """Clears the difference map and resets the background of visible cells."""
        if not self._diff_map:
            return
        self._diff_map.clear()
        self.update_visible_rows() # Redraw visible rows with default background
