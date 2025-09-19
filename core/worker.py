"""
Provides a generic worker thread for running long-running tasks in the background.

This module defines a `Worker` class that inherits from `QThread` to prevent
the main GUI thread from freezing during heavy operations like file parsing,
comparison, or exporting.
"""

from PyQt6.QtCore import QThread, pyqtSignal
from typing import Callable, Any

class Worker(QThread):
    """
    A generic, reusable QThread for offloading any function to a background thread.

    Signals:
        finished: Emits the return value of the target function when completed.
        error: Emits an error message (string) if an exception occurs.
        progress: Emits an integer value to report progress (e.g., percentage, byte count).
    """
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        """
        Args:
            func: The target function to execute in the background.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False

        # Automatically connect the worker's progress signal to the function's
        # `progress_cb` argument if it exists.
        if "progress_cb" not in self.kwargs:
            self.kwargs["progress_cb"] = self.progress.emit

        # Automatically connect the worker's cancellation check to the function's
        # `cancel_cb` argument if it exists.
        if "cancel_cb" not in self.kwargs:
            self.kwargs["cancel_cb"] = self.is_cancelled

    def run(self):
        """
        The main execution method of the thread. Calls the target function.
        """
        try:
            result = self.func(*self.args, **self.kwargs)
            # Only emit the finished signal if the task was not cancelled.
            if not self._is_cancelled:
                self.finished.emit(result)
        except Exception as e:
            # Only emit the error signal if the task was not cancelled.
            if not self._is_cancelled:
                self.error.emit(str(e))

    def cancel(self):
        """
        Sets the cancellation flag to True.
        The running function is responsible for checking this flag.
        """
        self._is_cancelled = True

    def is_cancelled(self) -> bool:
        """
        Allows the running function to check if a cancellation has been requested.

        Returns:
            True if `cancel()` has been called, False otherwise.
        """
        return self._is_cancelled
