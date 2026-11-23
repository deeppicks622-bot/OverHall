"""Command line entry point: python -m overhall inspect <file>"""

import argparse
from pathlib import Path
import sys

from .pe import PEFormatError, parse_pe


def main() -> int:
    parser = argparse.ArgumentParser(prog="overhall", description="Offline PE32+ metadata inspector (no execution).")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect = subparsers.add_parser("inspect", help="show PE32+ header and section metadata")
    inspect.add_argument("path", type=Path, help="path to a PE32+ file")
    args = parser.parse_args()
    try:
        image = parse_pe(args.path.read_bytes())
    except (OSError, PEFormatError) as exc:
        print(f"overhall: {exc}", file=sys.stderr)
        return 2
    print(f"Machine: AMD64 (0x{image.machine:04x})")
    print(f"Timestamp: 0x{image.timestamp:08x}")
    print(f"Image base: 0x{image.image_base:x}")
    print(f"Image size: 0x{image.size_of_image:x}; headers: 0x{image.size_of_headers:x}")
    print(f"Sections ({image.section_count}):")
    for section in image.sections:
        print(f"  {section.name or '<unnamed>':8} RVA=0x{section.virtual_address:08x} "
              f"virtual=0x{section.virtual_size:x} raw=0x{section.raw_size:x} "
              f"file=0x{section.raw_offset:x} flags=0x{section.characteristics:08x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
