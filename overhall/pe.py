"""Bounds-checked PE32+ metadata inspection. This module never loads or runs images."""

from __future__ import annotations

from dataclasses import dataclass
import struct


class PEFormatError(ValueError):
    """Raised when bytes do not describe a supported, well-bounded PE32+ image."""


@dataclass(frozen=True, slots=True)
class PESection:
    name: str
    virtual_size: int
    virtual_address: int
    raw_size: int
    raw_offset: int
    characteristics: int


@dataclass(frozen=True, slots=True)
class PEImage:
    machine: int
    section_count: int
    timestamp: int
    image_base: int
    section_alignment: int
    file_alignment: int
    size_of_image: int
    size_of_headers: int
    sections: tuple[PESection, ...]
    _data: bytes

    def rva_to_offset(self, rva: int, size: int = 1) -> int:
        """Map file-backed RVA bytes to a file offset; reject virtual-only or invalid ranges."""
        if rva < 0 or size < 0:
            raise PEFormatError("RVA and size must be non-negative")
        end = rva + size
        if end > 0x1_0000_0000:
            raise PEFormatError("RVA range overflows the 32-bit address space")
        if rva < self.size_of_headers:
            if end > self.size_of_headers or end > len(self._data):
                raise PEFormatError("RVA range exceeds file-backed headers")
            return rva
        for section in self.sections:
            span = max(section.virtual_size, section.raw_size)
            if section.virtual_address <= rva < section.virtual_address + span:
                delta = rva - section.virtual_address
                if delta + size > section.raw_size:
                    raise PEFormatError("RVA points to virtual-only or out-of-section data")
                offset = section.raw_offset + delta
                if offset + size > len(self._data):
                    raise PEFormatError("RVA range exceeds file data")
                return offset
        raise PEFormatError(f"RVA 0x{rva:x} is not inside a mapped section or headers")


def _unpack(data: bytes, fmt: str, offset: int, label: str) -> tuple[int, ...]:
    size = struct.calcsize(fmt)
    if offset < 0 or offset + size > len(data):
        raise PEFormatError(f"truncated {label}")
    return struct.unpack_from(fmt, data, offset)


def parse_pe(data: bytes | bytearray | memoryview) -> PEImage:
    """Parse PE32+ x86-64 headers and sections without executing or mapping the image."""
    raw = bytes(data)
    if len(raw) < 64 or raw[:2] != b"MZ":
        raise PEFormatError("missing DOS MZ header")
    (pe_offset,) = _unpack(raw, "<I", 0x3C, "DOS e_lfanew")
    if pe_offset < 64 or raw[pe_offset:pe_offset + 4] != b"PE\0\0":
        raise PEFormatError("missing or invalid PE signature")
    coff = pe_offset + 4
    machine, section_count, timestamp, _, _, optional_size, _ = _unpack(raw, "<HHIIIHH", coff, "COFF header")
    if machine != 0x8664:
        raise PEFormatError(f"unsupported machine 0x{machine:04x}; expected AMD64")
    if not 1 <= section_count <= 96:
        raise PEFormatError("section count must be between 1 and 96")
    optional = coff + 20
    if optional_size < 112 or optional + optional_size > len(raw):
        raise PEFormatError("truncated PE32+ optional header")
    (magic,) = _unpack(raw, "<H", optional, "optional header magic")
    if magic != 0x20B:
        raise PEFormatError(f"unsupported optional header magic 0x{magic:04x}; expected PE32+")
    image_base, = _unpack(raw, "<Q", optional + 24, "image base")
    section_alignment, file_alignment = _unpack(raw, "<II", optional + 32, "alignments")
    size_of_image, size_of_headers = _unpack(raw, "<II", optional + 56, "image sizes")
    if not section_alignment or not file_alignment or not size_of_image or not size_of_headers:
        raise PEFormatError("alignment and image size fields must be non-zero")
    if size_of_headers > len(raw):
        raise PEFormatError("declared headers exceed file bounds")
    if size_of_image < size_of_headers:
        raise PEFormatError("image size is smaller than its headers")
    table = optional + optional_size
    if table + section_count * 40 > len(raw):
        raise PEFormatError("truncated section table")
    if table + section_count * 40 > size_of_headers:
        raise PEFormatError("section table exceeds declared header size")
    sections: list[PESection] = []
    for index in range(section_count):
        off = table + index * 40
        name = raw[off:off + 8].split(b"\0", 1)[0].decode("ascii", errors="replace")
        virtual_size, virtual_address, raw_size, raw_offset = _unpack(raw, "<IIII", off + 8, "section dimensions")
        (characteristics,) = _unpack(raw, "<I", off + 36, "section characteristics")
        if raw_size and (raw_offset > len(raw) or raw_size > len(raw) - raw_offset):
            raise PEFormatError(f"section {name!r} raw data exceeds file bounds")
        if raw_size and raw_offset < size_of_headers:
            raise PEFormatError(f"section {name!r} raw data overlaps headers")
        if virtual_address + max(virtual_size, raw_size) > 0x1_0000_0000:
            raise PEFormatError(f"section {name!r} virtual range overflows")
        if virtual_address + max(virtual_size, raw_size) > size_of_image:
            raise PEFormatError(f"section {name!r} virtual range exceeds image size")
        sections.append(PESection(name, virtual_size, virtual_address, raw_size, raw_offset, characteristics))
    virtual_ranges = sorted((s.virtual_address, s.virtual_address + max(s.virtual_size, s.raw_size), s.name)
                            for s in sections if max(s.virtual_size, s.raw_size))
    for previous, current in zip(virtual_ranges, virtual_ranges[1:]):
        if current[0] < previous[1]:
            raise PEFormatError(f"sections {previous[2]!r} and {current[2]!r} have overlapping virtual ranges")
    raw_ranges = sorted((s.raw_offset, s.raw_offset + s.raw_size, s.name) for s in sections if s.raw_size)
    for previous, current in zip(raw_ranges, raw_ranges[1:]):
        if current[0] < previous[1]:
            raise PEFormatError(f"sections {previous[2]!r} and {current[2]!r} have overlapping raw data")
    return PEImage(machine, section_count, timestamp, image_base, section_alignment,
                   file_alignment, size_of_image, size_of_headers, tuple(sections), raw)
