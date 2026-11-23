import struct
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from overhall import PEFormatError, parse_pe


def synthetic_pe(*, machine=0x8664, magic=0x20B, virtual_size=0x180, raw_size=0x200):
    """Build a tiny PE32+ fixture entirely in memory; no external binaries are used."""
    pe_offset = 0x80
    optional_size = 0xF0
    headers_size = 0x200
    raw_offset = 0x200
    data = bytearray(raw_offset + raw_size)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, pe_offset)
    data[pe_offset:pe_offset + 4] = b"PE\0\0"
    coff = pe_offset + 4
    struct.pack_into("<HHIIIHH", data, coff, machine, 1, 0x12345678, 0, 0, optional_size, 0x22)
    opt = coff + 20
    struct.pack_into("<H", data, opt, magic)
    struct.pack_into("<Q", data, opt + 24, 0x140000000)
    struct.pack_into("<II", data, opt + 32, 0x1000, 0x200)
    struct.pack_into("<II", data, opt + 56, 0x2000, headers_size)
    sec = opt + optional_size
    data[sec:sec + 8] = b".text\0\0\0"
    struct.pack_into("<IIII", data, sec + 8, virtual_size, 0x1000, raw_size, raw_offset)
    struct.pack_into("<I", data, sec + 36, 0x60000020)
    data[raw_offset:raw_offset + raw_size] = bytes(range(256)) * (raw_size // 256) + bytes(raw_size % 256)
    return data


class PEParserTests(unittest.TestCase):
    def test_parses_amd64_pe32_plus(self):
        image = parse_pe(synthetic_pe())
        self.assertEqual(image.machine, 0x8664)
        self.assertEqual(image.timestamp, 0x12345678)
        self.assertEqual(image.image_base, 0x140000000)
        self.assertEqual(image.sections[0].name, ".text")
        self.assertEqual(image.sections[0].characteristics, 0x60000020)

    def test_maps_header_and_section_rvas(self):
        image = parse_pe(synthetic_pe())
        self.assertEqual(image.rva_to_offset(0x100), 0x100)
        self.assertEqual(image.rva_to_offset(0x1010, 4), 0x210)

    def test_rejects_virtual_only_bytes(self):
        image = parse_pe(synthetic_pe(virtual_size=0x300, raw_size=0x200))
        with self.assertRaisesRegex(PEFormatError, "virtual-only"):
            image.rva_to_offset(0x1200)

    def test_rejects_truncated_and_wrong_architecture_inputs(self):
        with self.assertRaises(PEFormatError):
            parse_pe(b"MZ")
        with self.assertRaisesRegex(PEFormatError, "AMD64"):
            parse_pe(synthetic_pe(machine=0x14C))
        with self.assertRaisesRegex(PEFormatError, r"PE32\+"):
            parse_pe(synthetic_pe(magic=0x10B))

    def test_rejects_out_of_bounds_raw_section(self):
        fixture = synthetic_pe()
        section = 0x80 + 4 + 20 + 0xF0
        struct.pack_into("<I", fixture, section + 16, 0x10000)
        with self.assertRaisesRegex(PEFormatError, "exceeds file bounds"):
            parse_pe(fixture)

    def test_rejects_bad_signatures_and_section_rvas(self):
        fixture = synthetic_pe()
        fixture[0] = 0
        with self.assertRaisesRegex(PEFormatError, "MZ"):
            parse_pe(fixture)
        image = parse_pe(synthetic_pe())
        for rva, size in ((-1, 1), (0x5000, 1), (0x1010, -1)):
            with self.subTest(rva=rva, size=size), self.assertRaises(PEFormatError):
                image.rva_to_offset(rva, size)

    def test_random_inputs_fail_cleanly(self):
        generator = random.Random(0x0A11CE)
        for length in range(128):
            candidate = bytearray(generator.randbytes(length))
            if length >= 2:
                candidate[:2] = b"MZ"
            with self.subTest(length=length), self.assertRaises(PEFormatError):
                parse_pe(candidate)

    def test_rejects_sections_outside_declared_image(self):
        fixture = synthetic_pe()
        optional = 0x80 + 4 + 20
        struct.pack_into("<I", fixture, optional + 56, 0x1100)
        with self.assertRaisesRegex(PEFormatError, "exceeds image size"):
            parse_pe(fixture)

    def test_generated_section_sizes_map_consistently(self):
        for index in range(1, 33):
            virtual_size = 0x100 + index * 4
            raw_size = 0x100 + index * 8
            image = parse_pe(synthetic_pe(virtual_size=virtual_size, raw_size=raw_size))
            delta = index
            self.assertEqual(image.rva_to_offset(0x1000 + delta, 1), 0x200 + delta)

    def test_cli_reports_metadata_and_rejects_invalid_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            valid = Path(temp_dir) / "synthetic.exe"
            invalid = Path(temp_dir) / "not-pe.bin"
            valid.write_bytes(synthetic_pe())
            invalid.write_bytes(b"not a PE")
            good = subprocess.run([sys.executable, "-m", "overhall", "inspect", str(valid)],
                                  capture_output=True, text=True, check=False)
            bad = subprocess.run([sys.executable, "-m", "overhall", "inspect", str(invalid)],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn("AMD64", good.stdout)
            self.assertIn(".text", good.stdout)
            self.assertEqual(bad.returncode, 2)
            self.assertIn("MZ", bad.stderr)

    def test_rejects_overlapping_sections(self):
        fixture = synthetic_pe()
        pe_offset = 0x80
        coff = pe_offset + 4
        struct.pack_into("<H", fixture, coff + 2, 2)
        struct.pack_into("<I", fixture, 0x80 + 4 + 20 + 56, 0x3000)
        first = 0x80 + 4 + 20 + 0xF0
        second = first + 40
        fixture[second:second + 8] = b".data\0\0\0"
        struct.pack_into("<IIII", fixture, second + 8, 0x100, 0x1100, 0x100, 0x300)
        with self.assertRaisesRegex(PEFormatError, "overlapping virtual"):
            parse_pe(fixture)
        struct.pack_into("<IIII", fixture, second + 8, 0x100, 0x2000, 0x100, 0x300)
        with self.assertRaisesRegex(PEFormatError, "overlapping raw"):
            parse_pe(fixture)


if __name__ == "__main__":
    unittest.main()
