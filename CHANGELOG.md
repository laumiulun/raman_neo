# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-09

### Added
- Initial release: genetic-algorithm fitting of Raman spectra, mirroring the
  structure of [EXAFS_Neo](https://github.com/laumiulun/EXAFS-Neo-Public).
- Band synthesis engine (`bandshape.py`) with Lorentzian, Gaussian and
  pseudo-Voigt line shapes and a polynomial baseline estimator.
- GA engine ported from EXAFS_Neo: populations, roulette-wheel selection,
  six crossover operators, five mutation operators (per-individual, per-band,
  per-trait, Metropolis, bounded), and GA / GA+Rechenberg solvers.
- Global-shift optimisation (E0 analogue) and band-area "band optimize"
  pruning (path-optimize analogue).
- `.ini` configuration parser, CLI entry point (`raman_neo -i input.ini`),
  and a Python API (`RamanNeo`).
- Standalone scoring (`analysis/raman_score.py`) and post-fit reporting
  (`analysis/raman_analysis.py`: peak table, R-factor, fit/residual plot).
- Bundled synthetic sample spectrum + band-definition file and a sample `.ini`.
- Test suite (50 tests) and CI/CD workflows.

[Unreleased]: https://github.com/laumiulun/raman_neo/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/laumiulun/raman_neo/releases/tag/v0.1.0
