"""
Provides utility functions for calculating file hashes.

These functions are designed to be memory-efficient by reading files in chunks,
making them suitable for large files.
"""

import hashlib
from typing import Callable

def _hash_file(path: str, hash_algo: Callable, chunk_size: int = 1 << 20) -> str:
    """
    A generic function to compute a hash for a file.

    Args:
        path: The absolute path to the file.
        hash_algo: The hash algorithm constructor from `hashlib` (e.g., hashlib.sha256).
        chunk_size: The size of each chunk to read from the file (in bytes).

    Returns:
        The hexadecimal digest of the hash.

    Raises:
        IOError: If the file cannot be read.
    """
    hasher = hash_algo()
    with open(path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def sha256_file(path: str, chunk_size: int = 1 << 20) -> str:
    """
    Computes the SHA256 hash of a file.

    Args:
        path: The absolute path to the file.
        chunk_size: The size of each chunk to read from the file (in bytes).

    Returns:
        The hexadecimal SHA256 digest.
    """
    return _hash_file(path, hashlib.sha256, chunk_size)

def sha1_file(path: str, chunk_size: int = 1 << 20) -> str:
    """
    Computes the SHA1 hash of a file.

    Args:
        path: The absolute path to the file.
        chunk_size: The size of each chunk to read from the file (in bytes).

    Returns:
        The hexadecimal SHA1 digest.
    """
    return _hash_file(path, hashlib.sha1, chunk_size)
