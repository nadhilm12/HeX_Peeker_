"""
hex_core.py — Safe hex/text parsing & general binary routing
Rules:
- .hex/.txt  -> parsed as hex (strict)
- any other extension -> copied as raw binary (no parsing)
- Preserve 1:1 integrity. Never pad/cut odd-length hex silently.
"""

from __future__ import annotations
import os
import re
import shutil
from typing import Iterator

# Regex for token bytes like 0xAB, \xAB, or plain AB inside text
BYTE_TOKEN = re.compile(
    r"""
    (?: 
        0x([0-9A-Fa-f]{2})      # 0xAB
        |
        \\x([0-9A-Fa-f]{2})     # \xAB
        |
        \b([0-9A-Fa-f]{2})\b    # AB (word boundary guarded)
    )
    """,
    re.VERBOSE,
)

def iter_hex_bytes_from_stream(stream: Iterator[str]) -> Iterator[int]:
    """
    Generator that reads text stream and yields bytes (int 0..255).
    - Fast path: pure hex line (only [0-9A-Fa-f]), must have even length.
      If odd → fail-fast with line number.
    - Mixed path: extract valid hex pairs via regex.
    """
    for lineno, raw_line in enumerate(stream, 1):
        line = raw_line.strip()
        if not line:
            continue

        if all(c in '0123456789abcdefABCDEF' for c in line):
            # Fast path: pure hex line
            if len(line) % 2 != 0:
                raise ValueError(
                    f"Pure-hex line has odd length at line {lineno}: '{line}'"
                )
            for i in range(0, len(line), 2):
                yield int(line[i:i+2], 16)
        else:
            # Mixed content: pull pairs via regex
            for m in BYTE_TOKEN.finditer(raw_line):
                hx = m.group(1) or m.group(2) or m.group(3)
                if hx:
                    yield int(hx, 16)

def smart_parse_to_temp(input_path: str, temp_filename: str) -> str:
    """
    Decide parsing route:
      - .hex/.txt -> parse as hex text (strict)
      - any other file -> copy as raw binary
    Returns: absolute path to temporary output file.
    """
    from core.temp_manager import get_temp_path

    ext = os.path.splitext(input_path)[1].lower()
    temp_output_path = get_temp_path(temp_filename)

    if ext in ('.hex', '.txt'):
        # Text mode + strict hex parsing
        with open(input_path, 'r', encoding='utf-8', errors='replace') as fin, \
             open(temp_output_path, 'wb') as fout:
            for byte_int in iter_hex_bytes_from_stream(fin):
                fout.write(bytes([byte_int]))
        return temp_output_path

    # Default: treat all other files as raw binary
    shutil.copyfile(input_path, temp_output_path)
    return temp_output_path
