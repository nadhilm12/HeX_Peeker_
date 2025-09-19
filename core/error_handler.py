"""
Custom exception classes for the Hex Peeker application.
"""

class HexPeekerError(Exception):
    """Base exception class for all application-specific errors."""
    pass

class FileParsingError(HexPeekerError):
    """Raised when an error occurs during file parsing."""
    pass

class FileCompareError(HexPeekerError):
    """Raised when an error occurs during file comparison."""
    pass

class ExportError(HexPeekerError):
    """Raised when an error occurs while exporting a report."""
    pass

class MagicByteError(HexPeekerError):
    """Raised for errors related to magic byte detection."""
    pass
