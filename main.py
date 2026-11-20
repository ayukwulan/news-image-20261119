#!/usr/bin/env python3
"""Entry program for news-image-20261119 (make.fun).

Copies the repo's entry.png to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output) and verifies it is a whole PNG of at most 1 MiB.
Standard library only, no network. The image itself is drawn by
draw.py (PIL, run locally while building the entry); this program
only delivers the finished bytes, so both runs write identical
output.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(SRC, "rb") as f:
        magic = f.read(8)
    if magic != PNG_MAGIC:
        raise SystemExit("entry.png is not a PNG file")
    src_size = os.path.getsize(SRC)
    if src_size > MAX_BYTES:
        raise SystemExit(
            "entry.png too large: %d bytes (limit %d)" % (src_size, MAX_BYTES)
        )
    shutil.copyfile(SRC, dst)
    dst_size = os.path.getsize(dst)
    if src_size != dst_size:
        raise SystemExit(
            "copy-size mismatch: source %d bytes, destination %d bytes"
            % (src_size, dst_size)
        )
    print("wrote %s (%d bytes)" % (dst, dst_size))


if __name__ == "__main__":
    main()
