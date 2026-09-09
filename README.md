# raman_neo

[![CI](https://github.com/laumiulun/raman_neo/actions/workflows/ci.yml/badge.svg)](https://github.com/laumiulun/raman_neo/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

#### Version: 0.1.0

Genetic-algorithm fitting of **Raman spectra**, mirroring the structure and
implementation of [EXAFS_Neo](https://github.com/laumiulun/EXAFS-Neo-Public).
Where EXAFS_Neo fits an EXAFS χ(k) spectrum as a sum of FEFF scattering paths,
`raman_neo` fits a Raman spectrum as a sum of analytic spectral bands
(Lorentzian / Gaussian / pseudo-Voigt), optimising band amplitudes, widths, and
positions with the same genetic-algorithm engine.

## Relationship to EXAFS_Neo

The two projects share the same GA architecture (populations, selection,
crossover, mutation, solvers, result collection). Only the *physics* layer
changes. The parameter mapping is one-to-one:

| EXAFS_Neo                     | raman_neo                          |
| ----------------------------- | ---------------------------------- |
| χ(k) vs wavenumber k          | Intensity vs Raman shift (cm⁻¹)    |
| FEFF scattering path          | Spectral band (line shape)         |
| S0² (amplitude)               | `amp` — band amplitude             |
| E0 (global energy shift)      | `shift` — global wavenumber offset |
| σ² (Debye–Waller)             | `width` — band width (cm⁻¹)        |
| ΔR (radial shift)             | `center_shift` — per-band offset   |
| Larch/FEFF `path2chi`         | analytic line-shape synthesis      |
| k-weighting                   | optional wavenumber weighting      |
| `autobk` background           | polynomial baseline subtraction    |
| R-space path area (optimize)  | integrated band area (optimize)    |

Each band's absolute centre is `nominal_center + center_shift + shift`.
Because the model is synthesised directly with NumPy, `raman_neo` has **no
Larch/FEFF dependency** — the core needs only NumPy and attrs (Matplotlib is
used only by the optional plotting helpers).

### Module map

| EXAFS_Neo module      | raman_neo module        | role                          |
| --------------------- | ----------------------- | ----------------------------- |
| `exafs.py`            | `raman.py`              | top-level orchestration       |
| `exafs_pop.py`        | `raman_pop.py`          | population + `fitness()`       |
| `pathObj.py`          | `bandObj.py`            | per-band GA parameters        |
| `pathrange.py`        | `bandrange.py`          | parameter search ranges       |
| `analysis/larch_score`| `bandshape.py` + `analysis/raman_score.py` | spectrum synthesis & scoring |
| `analysis/EXAFS_Analysis` | `analysis/raman_analysis.py` | post-fit reporting     |
| `neoPars`, `neoSelector`, `neoCrossOver`, `neoMutator`, `neoSolver`, `neoResult`, `neoFilePars`, `individual`, `ini_parser`, `parser`, `input_arg`, `utils*`, `helper` | same names | GA engine (ported directly) |

## Prerequisites

- Python ≥ 3.10
- NumPy, attrs (Matplotlib only for the optional plotting helpers)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .          # from a clone of this repo
```

## Usage

Run the bundled example:

```bash
raman_neo -i test_inputs/test_raman.ini
```

Or drive it from Python:

```python
from raman_neo.raman import RamanNeo
from raman_neo.analysis.raman_analysis import RamanAnalysis

r = RamanNeo(verbose_lvl=1)
r.raman_read(input_parameters={
    "data_file": "raman_neo/data/sample_raman.dat",
    "band_file": "raman_neo/data/sample_bands.txt",
    "output_file": "result/out.csv",
    "nGen": 40, "nPops": 120,
    "xmin": 150, "xmax": 1750, "deltax": 1.0, "weight": 0.0,
    "baseline_order": 1,
    "bandrange": [1, 2, 3, 4],
    "solOpt": 1, "mut_options": 1, "croOpt": 0,
})
r.raman_setup()
result = r.run()
print(RamanAnalysis(result).report())
```

### Data file

Two whitespace-separated columns — Raman shift (cm⁻¹) and intensity. Lines
starting with `#` are comments:

```
# wavenumber_cm-1 intensity
100.0  0.041
101.0  0.051
...
```

### Band-definition file

One candidate band per line (the analogue of a FEFF path folder). Only the
centre is required:

```
# center, shape, eta, base_width
480.0,  lorentzian, 1.0, 9.0
1350.0, voigt,      0.7, 28.0
```

`shape` ∈ {`lorentzian`, `gaussian`, `voigt`}; `eta` is the Lorentzian fraction
for a pseudo-Voigt; `base_width` is a reference width in cm⁻¹.

### Input `.ini`

Sections mirror EXAFS_Neo: `[Inputs] [Populations] [Solver] [Mutations]
[Bands] [Spectrum] [Outputs]`. See `test_inputs/test_raman.ini`. `band_list`
selects which rows of the band file to fit; option numbers for solver /
selection / crossover / mutation match EXAFS_Neo.

## Development

```bash
make install-dev     # editable install + dev tools + pre-commit hooks
make lint            # ruff check + format --check
make format          # ruff format + autofix
make test            # pytest              (or: ./run_tests)
make cov             # pytest with coverage
make build           # sdist + wheel
```

Continuous integration (`.github/workflows/ci.yml`) runs ruff and the test
suite on Linux, macOS and Windows across Python 3.10–3.13, then builds the
distributions. Publishing to PyPI happens automatically on a GitHub Release via
trusted publishing (`.github/workflows/publish.yml`).

## Regenerating the sample data

```bash
python scripts/make_sample_data.py
```

## Roadmap

- Differential-evolution solver and tournament selection (stubs present, as in EXAFS_Neo)
- Multi-component / multi-spectrum series fitting
- GUI (EXAFS_Neo ships a wxPython GUI; not yet ported)
- Asymmetric-least-squares baseline option

## License

GPL-3.0 (see `LICENSE`), matching EXAFS_Neo.
