import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "raman_neo", "data")


@pytest.fixture
def data_file():
    return os.path.join(DATA, "sample_raman.dat")


@pytest.fixture
def band_file():
    return os.path.join(DATA, "sample_bands.txt")


@pytest.fixture
def base_inputs(tmp_path, data_file, band_file):
    """A minimal input dict for building NeoPars in tests."""
    return {
        "data_file": data_file,
        "band_file": band_file,
        "output_file": str(tmp_path / "out.csv"),
        "nGen": 6,
        "nPops": 20,
        "xmin": 150,
        "xmax": 1750,
        "deltax": 1.0,
        "weight": 0.0,
        "baseline_order": 1,
        "printGraph": False,
        "nBestSample": 0.3,
        "nLuckSample": 0.2,
        "bandrange": [1, 2, 3, 4],
        "solOpt": 0,
        "mut_options": 1,
        "croOpt": 0,
    }
