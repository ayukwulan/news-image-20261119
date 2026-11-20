#!/usr/bin/env python3
"""Entry point for news-image-20261119.

Validates the front-page PNG produced by draw.py (PNG magic, IHDR
dimensions, file size) and copies it to the output directory as
entry.png. Standard library only; no network access.
"""

import os
import shutil
import struct
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576  # 1 MiB
EXPECTED_SIZE = (1024, 1024)


def read_png_header(path):
    """Return (width, height) from the IHDR chunk of a PNG file."""
    with open(path, "rb") as handle:
        magic = handle.read(len(PNG_MAGIC))
        if magic != PNG_MAGIC:
            raise ValueError(f"{path}: not a PNG file (bad magic)")
        length_bytes = handle.read(4)
        chunk_type = handle.read(4)
        if len(length_bytes) != 4 or chunk_type != b"IHDR":
            raise ValueError(f"{path}: missing IHDR chunk")
        width, height = struct.unpack(">II", handle.read(8))
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        print(f"error: {source} not found; run draw.py first",
              file=sys.stderr)
        return 1

    size = os.path.getsize(source)
    if size > MAX_BYTES:
        print(f"error: {source} is {size} bytes, over the 1 MiB limit",
              file=sys.stderr)
        return 1

    width, height = read_png_header(source)
    if (width, height) != EXPECTED_SIZE:
        print(f"error: {source} is {width}x{height}, expected "
              f"{EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]}", file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, dest)
    print(f"wrote {dest} ({size} bytes, {width}x{height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
