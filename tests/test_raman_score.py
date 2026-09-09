import numpy as np

from raman_neo.analysis import raman_score as rs


def test_build_grid():
    xg, iv = rs.build_grid(150, 1750, 1.0)
    assert xg[0] == 0.0
    assert xg[-1] == 1750.0
    assert iv[0] == 150
    assert iv[-1] == 1750


def test_load_and_synthesize_recovers_truth(data_file, band_file):
    xg, iv = rs.build_grid(150, 1750, 1.0)
    exp = rs.load_experimental(data_file, xg, baseline_order=1, normalize=True, interval=iv)
    bands = rs.bands_from_file(band_file, [1, 2, 3, 4])
    # ground-truth (pre-normalisation) parameters
    truth = np.array([[0.45, 0, 9, 0], [0.30, 0, 12, 0], [0.80, 0, 28, 0], [1.00, 0, 18, 0]])
    model = rs.synthesize(bands, truth, xg)
    r = rs.r_factor(model, exp, iv)
    assert r < 0.1  # truth params fit the (normalised) data well


def test_score_zero_for_identical():
    y = np.array([0.0, 1.0, 2.0, 3.0])
    assert rs.score(y, y) == 0.0
