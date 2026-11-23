# Initial architecture

OverHall starts as a clean-room implementation. The modules below are planned boundaries, not claims that the work is
already implemented.

## Components

- **Image loader** — parse and map PE images in synthetic tests, then resolve imports through an explicit offline
  registry. Unknown imports must fail with a useful diagnostic instead of silently returning success.
- **Platform layer** — implement only documented local APIs. Each shim records its supported behavior and has a
  synthetic unit test.
- **Shader translator** — translate documented instruction behavior from hand-written fixtures. Unsupported forms
  remain explicit errors until their behavior is verified.
- **Graphics backend** — expose a narrow host graphics interface and validate resource, synchronization, and draw
  behavior with synthetic workloads before considering title-specific inputs.
- **Build and diagnostics** — keep tool versions, test results, and error summaries reproducible without recording
  game data.

## Development sequence

1. Keep the build dependency-light and make the smoke target compile on Windows.
2. Add one module at a time with tests that use generated inputs.
3. Record assumptions separately from verified behavior.
4. Require a local validation plan before adding title-specific support.

## Repository hygiene

Do not commit executables, archives, shaders, textures, audio, extracted assets, keys, or logs containing game data.
The repository should contain source, documentation, and synthetic fixtures only.
