"""Generate a synthetic Raman spectrum + band-definition file for demos/tests."""

import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "raman_neo", "data")
os.makedirs(DATA, exist_ok=True)


def lorentzian(x, c, w):
    return w**2 / ((x - c) ** 2 + w**2)


# Ground-truth bands: (center, amplitude, width_cm-1)
TRUE = [
    (480.0, 0.45, 9.0),
    (720.0, 0.30, 12.0),
    (1350.0, 0.80, 28.0),  # D-band-like
    (1580.0, 1.00, 18.0),  # G-band-like
]

rng = np.random.default_rng(1234)
x = np.arange(100.0, 1800.0 + 1.0, 1.0)
y = np.zeros_like(x)
for c, a, w in TRUE:
    y += a * lorentzian(x, c, w)

# Gentle sloping baseline + noise to make it realistic.
y += 0.05 + 0.00005 * (x - 100.0)
y += rng.normal(0.0, 0.006, size=x.shape)

spectrum = np.column_stack([x, y])
np.savetxt(
    os.path.join(DATA, "sample_raman.dat"),
    spectrum,
    fmt="%.4f",
    header="wavenumber_cm-1 intensity  (synthetic: bands at 480/720/1350/1580)",
)

# Band-definition file: 6 candidates (4 real + 2 decoys) so band_optimize matters.
band_lines = [
    "# center, shape, eta, base_width",
    "480.0, lorentzian, 1.0, 9.0",
    "720.0, lorentzian, 1.0, 12.0",
    "1350.0, voigt, 0.7, 28.0",
    "1580.0, lorentzian, 1.0, 18.0",
    "1000.0, lorentzian, 1.0, 15.0",  # decoy (no real band here)
    "1700.0, gaussian, 0.0, 20.0",  # decoy
]
with open(os.path.join(DATA, "sample_bands.txt"), "w") as fh:
    fh.write("\n".join(band_lines) + "\n")

print("wrote", os.path.join(DATA, "sample_raman.dat"), spectrum.shape)
print("wrote", os.path.join(DATA, "sample_bands.txt"))
