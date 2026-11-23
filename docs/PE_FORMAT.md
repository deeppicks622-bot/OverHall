# PE32+ metadata inspection

The first implementation reads a narrow part of Microsoft's PE/COFF image format: the DOS pointer to the PE header,
COFF machine and section count, PE32+ optional-header fields, and section table. It recognizes AMD64 images only.
`PEImage.rva_to_offset()` maps file-backed header or section bytes and rejects gaps, virtual-only bytes, and ranges
outside the input buffer.

The command `python -m overhall inspect path-to-file.exe` prints this metadata. The input is read as data only. The
tool does not execute, map, patch, unpack, decrypt, resolve imports, or bypass any platform checks.

This is **not an Xbox executable reader**. Xbox packages and executable containers have platform-specific formats and
requirements; this parser only accepts the documented Windows PE32+ image form. It cannot make a console title run on
Windows, and a PE header is not a substitute for source code, platform SDKs, or a supported Windows build.

Tests construct small byte arrays in memory and exercise valid headers, RVA mapping, truncation, wrong architectures,
virtual-only ranges, malformed signatures, and out-of-bounds sections. They use no commercial executable or game data.

Format reference: [Microsoft PE/COFF specification](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format).
