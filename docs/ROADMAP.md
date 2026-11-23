# Development roadmap

This roadmap records engineering gates, not promises that a commercial title will run.

## Complete in this milestone

- [x] Parse bounded AMD64 PE32+ header and section metadata.
- [x] Convert file-backed header and section RVAs, rejecting virtual-only and out-of-range data.
- [x] Provide an offline command-line inspector.
- [x] Exercise the parser with in-memory synthetic fixtures and a CI workflow.

## Next engineering gates

1. **Format inventory:** document the exact public specifications and supported input forms before adding another
   container reader. Do not infer Xbox format support from Windows PE support.
2. **Parser robustness:** collect more synthetic malformed-input cases, check overlap and arithmetic edges, and keep
   diagnostics stable and useful.
3. **Build reproducibility:** run the existing C++ smoke target on a machine with CMake and a C++20 compiler; record
   tool versions. The current Windows workstation does not have those tools installed.
4. **Documented interfaces:** choose one small offline API behavior with a public specification and build an isolated
   synthetic test before implementing it.
5. **Graphics experiments:** only consider a narrow documented host API experiment after interface and resource
   behavior can be tested with generated data.

## Hard constraints and current blockers

- This repository has no Rockstar source code, supported Windows build, Xbox SDK, title assets, or licensed porting
  materials. There is no basis here to recompile the game for PC.
- The present parser understands neither Xbox executable containers nor console ABIs, system services, graphics
  commands, or shaders.
- No executable loader, emulator, DRM bypass, key handling, decryptor, or network service integration is implemented or
  planned in this prototype.
- A practical PC release requires a supported PC build from the rights holder or a documented, authorized porting
  route and substantial platform-specific engineering. The current milestone does not approach playability.
