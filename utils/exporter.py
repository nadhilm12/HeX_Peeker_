"""
Handles the exporting of comparison reports and raw data to various formats.

This module uses `QFileDialog` to prompt the user for a save location and
serializes the difference data or raw byte data into the chosen format.
"""

import csv
import json
from typing import List, Tuple, Optional

# Import QFileDialog lazily to avoid hard dependency for non-GUI use.
try:
    from PyQt6.QtWidgets import QFileDialog
except ImportError:
    QFileDialog = None

from core.error_handler import ExportError

def export_diff_report(diffs: List[Tuple[str, int, Optional[int], Optional[int]]]):
    """
    Opens a save dialog and exports the list of differences to a CSV or JSON file.
    """
    if QFileDialog is None:
        raise RuntimeError("PyQt6 is required for the export dialog.")

    path, selected_filter = QFileDialog.getSaveFileName(
        None,  # Parent widget
        "Save Difference Report",
        "diff_report.csv",
        "CSV (*.csv);;JSON (*.json)"
    )

    if not path:
        return

    try:
        if "CSV" in selected_filter:
            _write_csv_diff(path, diffs)
        elif "JSON" in selected_filter:
            _write_json_diff(path, diffs)
        else: # Fallback for some environments
            if path.lower().endswith(".csv"):
                _write_csv_diff(path, diffs)
            elif path.lower().endswith(".json"):
                _write_json_diff(path, diffs)
            else:
                raise ExportError(f"Unsupported file format for: {path}")
    except (IOError, OSError) as e:
        raise ExportError(f"Failed to write to file: {path}\nError: {e}") from e

def export_view_data(data_to_export: bytes, progress_cb=None, cancel_cb=None):
    """
    Opens a save dialog and exports the raw byte data to a .bin or .txt file.
    Includes progress reporting and cancellation support.
    """
    if QFileDialog is None:
        raise RuntimeError("PyQt6 is required for the export dialog.")

    path, selected_filter = QFileDialog.getSaveFileName(
        None,
        "Export View Data As",
        "export.bin",
        "Binary File (*.bin);;Hex Text File (*.txt)"
    )

    if not path:
        if progress_cb:
            progress_cb(100) # Ensure UI resets if cancelled at dialog
        return

    try:
        total_size = len(data_to_export)
        
        # Determine which writer to use
        writer_func = None
        if ".bin" in selected_filter or path.lower().endswith(".bin"):
            writer_func = _write_binary
        elif ".txt" in selected_filter or path.lower().endswith(".txt"):
            writer_func = _write_hex_text
        else:
            raise ExportError(f"Unsupported file format for: {path}. Please select .bin or .txt")

        # Execute the writer
        writer_func(path, data_to_export, progress_cb=progress_cb, cancel_cb=cancel_cb, total_size=total_size)

    except (IOError, OSError) as e:
        raise ExportError(f"Failed to write to file: {path}\nError: {e}") from e
    finally:
        if progress_cb:
            progress_cb(100) # Final update to ensure completion

# --- Helper functions for diff report export ---

def _write_csv_diff(path: str, diffs: List[Tuple[str, int, Optional[int], Optional[int]]]):
    """Writes the difference report to a CSV file."""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Status", "Offset", "File1_Byte(Hex)", "File2_Byte(Hex)"])
        for status, offset, b1, b2 in diffs:
            writer.writerow([
                status,
                f"0x{offset:08X}",
                f"{b1:02X}" if b1 is not None else "N/A",
                f"{b2:02X}" if b2 is not None else "N/A"
            ])

def _write_json_diff(path: str, diffs: List[Tuple[str, int, Optional[int], Optional[int]]]):
    """Writes the difference report to a JSON file."""
    report_data = [
        {
            "status": status,
            "offset": f"0x{offset:08X}",
            "file1_byte": f"{b1:02X}" if b1 is not None else None,
            "file2_byte": f"{b2:02X}" if b2 is not None else None
        }
        for status, offset, b1, b2 in diffs
    ]
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)

# --- Helper functions for raw data export ---

def _write_binary(path: str, data: bytes, progress_cb=None, cancel_cb=None, total_size=0):
    """Writes the raw bytes directly to a file with progress and cancellation."""
    CHUNK_SIZE = 4096
    bytes_written = 0
    with open(path, 'wb') as f:
        for i in range(0, total_size, CHUNK_SIZE):
            if cancel_cb and cancel_cb():
                return
            chunk = data[i:i+CHUNK_SIZE]
            f.write(chunk)
            bytes_written += len(chunk)
            if progress_cb and total_size > 0:
                progress_cb(int(bytes_written * 100 / total_size))

def _write_hex_text(path: str, data: bytes, progress_cb=None, cancel_cb=None, total_size=0):
    """Writes the byte data as a formatted hex string with progress and cancellation."""
    BYTES_PER_LINE = 16
    LINES_PER_CHUNK = 256 # Write in chunks of lines to update progress more frequently
    CHUNK_SIZE = BYTES_PER_LINE * LINES_PER_CHUNK
    
    bytes_processed = 0
    with open(path, 'w', encoding='utf-8') as f:
        for i in range(0, total_size, CHUNK_SIZE):
            if cancel_cb and cancel_cb():
                return
            
            chunk_end = min(i + CHUNK_SIZE, total_size)
            buffer = []
            for j in range(i, chunk_end, BYTES_PER_LINE):
                line_chunk = data[j:j+BYTES_PER_LINE]
                hex_string = ' '.join(f'{byte:02X}' for byte in line_chunk)
                buffer.append(hex_string + '\n')
            
            f.write(''.join(buffer))
            bytes_processed = chunk_end
            
            if progress_cb and total_size > 0:
                progress_cb(int(bytes_processed * 100 / total_size))