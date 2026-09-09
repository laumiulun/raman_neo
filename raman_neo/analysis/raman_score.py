"""Standalone scoring helpers, independent of the GA machinery.

Raman analogue of ``exafs_neo.analysis.larch_score``. Given a set of band
definitions and parameters, synthesise a model spectrum and score it against an
experimental spectrum. Useful for unit tests and for scoring a fixed candidate
model without running the full GA.
"""

import numpy as np

from raman_neo.bandshape import Band, polynomial_baseline, read_band_file


def build_grid(xmin, xmax, dx):
    """Model grid indexed 0..big with spacing dx (matches the GA convention)."""
    big = int(xmax / dx)
    xgrid = np.arange(big + 1) * dx
    small = int(xmin / dx)
    interval = np.arange(small, big + 1)
    return xgrid, interval


def load_experimental(path, xgrid, baseline_order=0, normalize=True, interval=None):
    """Load, resample, baseline-correct and (optionally) normalise a spectrum."""
    data = np.atleast_2d(np.genfromtxt(str(path), comments="#"))
    x = data[:, 0].astype(float)
    y = data[:, 1].astype(float)
    order = np.argsort(x)
    exp = np.interp(xgrid, x[order], y[order], left=0.0, right=0.0)
    if baseline_order and baseline_order > 0:
        exp = exp - polynomial_baseline(xgrid, exp, order=baseline_order)
    if normalize:
        idx = interval if interval is not None else slice(None)
        peak = np.max(exp[idx]) if np.max(exp[idx]) > 0 else 1.0
        exp = exp / peak
    return exp


def synthesize(bands, params, xgrid):
    """Synthesise the total spectrum from band objects and a (nband, 4) param array.

    ``params`` rows are ``[amp, shift, width, center_shift]``.
    """
    params = np.asarray(params, dtype=float)
    y_total = np.zeros_like(xgrid, dtype=float)
    for i, band in enumerate(bands):
        band.amp = params[i, 0]
        band.shift = params[i, 1]
        band.width = params[i, 2]
        band.center_shift = params[i, 3]
        y_total += band.band2chi(xgrid)
    return y_total


def score(y_model, y_exp, xgrid=None, interval=None, weight=0.0):
    """Weighted sum-of-squares misfit (the GA fitness, computed standalone)."""
    if interval is None:
        interval = np.arange(len(y_model))
    diff = y_model[interval] - y_exp[interval]
    if weight and weight != 0.0 and xgrid is not None:
        diff = diff * (xgrid[interval] ** weight)
    return float(np.sum(diff**2))


def r_factor(y_model, y_exp, interval=None):
    """EXAFS-style R-factor: sum |model-exp|^2 / sum |exp|^2."""
    if interval is None:
        interval = np.arange(len(y_model))
    num = np.sum((y_model[interval] - y_exp[interval]) ** 2)
    den = np.sum(y_exp[interval] ** 2)
    return float(num / den) if den > 0 else float("inf")


def bands_from_file(band_file, band_list=None):
    """Instantiate :class:`Band` objects from a band-definition file."""
    defs = read_band_file(band_file)
    if band_list is None:
        band_list = list(range(1, len(defs) + 1))
    bands = []
    for band_id in band_list:
        d = defs[int(band_id) - 1]
        bands.append(Band(f"Band{band_id}", d["center"], d["shape"], d["eta"], d["base_width"]))
    return bands
