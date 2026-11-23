# Contributing

OverHall is a clean-room compatibility research prototype. Before opening a change:

1. Read [the project boundaries](README.md#project-boundaries), [format scope](docs/PE_FORMAT.md), and
   [roadmap](docs/ROADMAP.md).
2. Keep fixtures synthetic and generated in tests. Do not add proprietary code, executable samples, extracted assets,
   keys, title logs, or output derived from private game data.
3. Make unsupported inputs fail clearly. Do not silently accept behavior that has not been verified against public
   documentation.
4. Run `python -m unittest discover -s tests -v`, `python -m compileall -q overhall tests`, and `git diff --check`.
5. Describe the supported behavior, tests run, and known limits. Do not claim a title is supported unless that is
   independently demonstrated through an authorized and reproducible test.

The repository does not yet have a selected software license. Please discuss license selection before contributing
third-party code or suggesting redistribution terms.
