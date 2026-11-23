# OverHall

OverHall is an independent, clean-room research project exploring how a locally owned Xbox game executable could be
made compatible with Windows PCs. It is not affiliated with Rockstar Games, Take-Two Interactive, Microsoft, or the
Leonida project.

## Status

**Planning prototype. Nothing is playable yet.** This repository currently contains only an original build skeleton
and architecture notes. It does not contain a game executable, game assets, shaders, keys, or generated game data.

## Project boundaries

- Work only with files the user already owns and can read locally.
- Do not include game files or generated outputs in this repository.
- Do not implement key extraction, decryption, DRM circumvention, or network access to game services.
- Confirm behavior with public documentation and hand-written synthetic fixtures before supporting a format or API.
- Keep game-specific inputs and test results on the user's PC; publish only source code and aggregate outcomes.

## Initial milestones

1. Establish a reproducible native build and synthetic test harness.
2. Implement and test a small PE image loader using generated test images.
3. Add only well-understood offline platform APIs, each with focused tests.
4. Build a graphics compatibility layer and validate it with synthetic workloads.
5. Investigate shader translation using hand-written inputs and documented hardware behavior.
6. Attempt any local title-specific validation only when the required tools and an authorized local copy are available.

## Build

The initial prototype needs a C++20 compiler and CMake:

```powershell
cmake -S . -B build
cmake --build build --config Release
```

The current executable is only a build smoke target; it does not load or run a game.

## License

The project license has not been selected yet. No third-party code has been copied into this repository.
