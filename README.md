# OverHall

OverHall is an independent, clean-room research project exploring how a locally owned Xbox game executable could be
made compatible with Windows PCs. It is not affiliated with Rockstar Games, Take-Two Interactive, Microsoft, or the
Leonida project.

## Status

**Early research prototype. Nothing is playable.** OverHall currently contains a bounds-checked, offline inspector for
AMD64 PE32+ headers and section metadata, plus tests built from synthetic byte arrays. It is not an Xbox/XEX parser,
game loader, emulator, or PC port. The repository contains no game executable, game assets, shaders, keys, or generated
game data.

## Project boundaries

- Work only with files the user already owns and can read locally.
- Do not include game files or generated outputs in this repository.
- Do not implement key extraction, decryption, DRM circumvention, or network access to game services.
- Confirm behavior with public documentation and hand-written synthetic fixtures before supporting a format or API.
- Keep game-specific inputs and test results on the user's PC; publish only source code and aggregate outcomes.

## Initial milestones

1. Keep the synthetic test harness and parser bounds checks reproducible.
2. Document platform container formats before considering any additional offline metadata reader.
3. Add only well-understood APIs, each with focused tests and explicit unsupported cases.
4. Explore graphics and shader behavior only through documented interfaces and synthetic workloads.
5. Keep compatibility research separate from claims of title support or playability.

## Build

The original C++ smoke target needs a C++20 compiler and CMake:

```powershell
cmake -S . -B build
cmake --build build --config Release
```

The current C++ executable is only a build smoke target. The PE inspector uses Python 3.10+ and no runtime dependencies:

```powershell
python -m unittest discover -s tests -v
python -m overhall inspect path-to-pe32plus.exe
```

See [PE32+ inspection scope](docs/PE_FORMAT.md) and the [engineering roadmap](docs/ROADMAP.md) for current limits and
next gates.

## License

The project license has not been selected yet. No third-party code has been copied into this repository.
