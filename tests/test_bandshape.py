import numpy as np
import pytest

from raman_neo.bandshape import (
    Band,
    evaluate_shape,
    gaussian,
    lorentzian,
    polynomial_baseline,
    pseudo_voigt,
    read_band_file,
)


def test_lineshapes_unit_peak():
    x = np.linspace(0, 100, 1001)
    for f in (lorentzian, gaussian):
        y = f(x, 50.0, 5.0)
        assert y.max() == pytest.approx(1.0, abs=1e-6)
        assert np.argmax(y) == pytest.approx(500, abs=1)


def test_pseudo_voigt_bounds():
    x = np.linspace(0, 100, 1001)
    lo = pseudo_voigt(x, 50, 5, eta=1.0)
    ga = pseudo_voigt(x, 50, 5, eta=0.0)
    assert np.allclose(lo, lorentzian(x, 50, 5))
    assert np.allclose(ga, gaussian(x, 50, 5))


def test_evaluate_shape_unknown():
    with pytest.raises(ValueError):
        evaluate_shape("triangle", np.array([1.0]), 1.0, 1.0)


def test_band_synthesis_and_center():
    x = np.linspace(100, 1600, 1501)
    b = Band("B1", 500.0, "lorentzian", base_width=10.0)
    b.amp = 2.0
    b.width = 10.0
    b.center_shift = 5.0
    b.shift = 3.0
    y = b.band2chi(x)
    assert b.absolute_center() == pytest.approx(508.0)
    assert y.max() == pytest.approx(2.0, abs=1e-3)
    assert b.area(x) > 0


def test_read_band_file(band_file):
    bands = read_band_file(band_file)
    assert len(bands) == 6
    assert bands[0]["center"] == pytest.approx(480.0)
    assert bands[2]["shape"] == "voigt"


def test_polynomial_baseline_slope():
    x = np.linspace(0, 100, 200)
    y = 2.0 + 0.5 * x  # pure line
    bl = polynomial_baseline(x, y, order=1)
    assert np.allclose(bl, y, atol=1e-6)
