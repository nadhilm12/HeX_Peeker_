"""
Provides the core logic for comparing two byte sequences.
"""

from typing import List, Tuple, Optional, Callable

def compare_two_files(
    file1_bytes: bytes,
    file2_bytes: bytes,
    progress_cb: Optional[Callable[[int], None]] = None,
    cancel_cb: Optional[Callable[[], bool]] = None
) -> List[Tuple[str, int, Optional[int], Optional[int]]]:
    """
    Compares two byte sequences and returns a list of differences with their status.

    The comparison runs up to the length of the longer sequence.
    This function supports progress reporting and cancellation for large comparisons.

    Args:
        file1_bytes: The first byte sequence.
        file2_bytes: The second byte sequence.
        progress_cb: A callback to report progress (current offset).
        cancel_cb: A callback to check if the operation should be cancelled.

    Returns:
        A list of tuples, where each tuple represents a difference and contains:
        (status, offset, byte_from_file1, byte_from_file2).
        'status' can be 'replace', 'delete', or 'insert'.

    Raises:
        Exception: If the operation is cancelled by the user.
    """
    differences: List[Tuple[str, int, Optional[int], Optional[int]]] = []
    max_len = max(len(file1_bytes), len(file2_bytes))

    # Define a progress reporting interval to avoid excessive signal emissions.
    progress_interval = max(1000, max_len // 100) # Report ~100 times or every 1000 bytes

    for i in range(max_len):
        # Check for cancellation at regular intervals.
        if i % progress_interval == 0:
            if cancel_cb and cancel_cb():
                raise Exception("File comparison cancelled by user.")
            if progress_cb:
                progress_cb(i)

        byte1 = file1_bytes[i] if i < len(file1_bytes) else None
        byte2 = file2_bytes[i] if i < len(file2_bytes) else None

        if byte1 != byte2:
            status = ''
            if byte1 is not None and byte2 is not None:
                status = 'replace'
            elif byte1 is not None and byte2 is None:
                # Byte exists in file 1 but not in file 2 (file 2 is shorter)
                status = 'delete'
            elif byte1 is None and byte2 is not None:
                # Byte exists in file 2 but not in file 1 (file 1 is shorter)
                status = 'insert'
            
            if status:
                differences.append((status, i, byte1, byte2))

    # Ensure final progress is reported.
    if progress_cb:
        progress_cb(max_len)

    return differences
