"""
Manages the creation and cleanup of temporary files and directories.

This module ensures that all temporary data generated during the application's
lifecycle is stored in a dedicated cache directory and is automatically
deleted upon application exit.
"""

import atexit
import os
import shutil
import tempfile

# Create a single, global temporary directory for the application's session.
# The directory is prefixed for easy identification.
try:
    TEMP_DIR = tempfile.mkdtemp(prefix="hexpeeker_cache_")
except (IOError, OSError) as e:
    print(f"Fatal Error: Could not create temporary directory. {e}")
    # In a real GUI app, you'd show a critical error dialog and exit.
    # For this script, we'll raise an exception to halt execution.
    raise RuntimeError("Failed to create a necessary temporary directory.") from e

def get_temp_path(filename: str) -> str:
    """
    Constructs the full, absolute path for a file within the global temp directory.

    Args:
        filename: The base name of the file (e.g., "temp1.bin").

    Returns:
        The absolute path to the temporary file.
    """
    return os.path.join(TEMP_DIR, filename)

def cleanup_temp():
    """
    Removes the entire temporary directory tree.

    This function is registered with `atexit` to be called automatically
    when the Python interpreter exits, ensuring no temporary files are left behind.
    `ignore_errors=True` prevents exceptions if the directory is already gone.
    """
    try:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    except Exception:
        # Silently ignore any exceptions during cleanup, as the OS will handle it.
        pass

# Register the cleanup function to be executed upon program termination.
# This is a robust way to handle cleanup without manual intervention.
atexit.register(cleanup_temp)
