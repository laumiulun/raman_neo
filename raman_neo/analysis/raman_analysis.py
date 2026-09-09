"""Post-fit analysis and reporting.

Raman analogue of ``exafs_neo.analysis.EXAFS_Analysis``. Turns a finished GA
result into a human-readable peak table, a fit/residual curve, and summary
statistics.
"""

import numpy as np

from raman_neo.analysis.raman_score import r_factor


class RamanAnalysis:
    """Summarise a completed :class:`raman_neo.neoResult.NeoResult`."""

    def __init__(self, result):
        self.result = result
        self.raman_pars = result.raman_pars
        self.best_individual = result.best_individual

        band_pars = self.raman_pars.ramanBandPars
        self.xgrid = band_pars.xgrid
        self.exp = band_pars.exp
        self.bandnames = band_pars.bandname
        self.bandDictionary = band_pars.bandDictionary
        self.interval = self.raman_pars.ramanPars.intervalK

        self.params = np.asarray(self.best_individual.get())  # (nband, 4)
        self.shift = float(self.best_individual.get_e0())
        self.model = self._synthesize()

    def _synthesize(self):
        y_total = np.zeros_like(self.xgrid, dtype=float)
        for i, name in enumerate(self.bandnames):
            band = self.bandDictionary[name]
            band.amp = self.params[i, 0]
            band.shift = self.shift
            band.width = self.params[i, 2]
            band.center_shift = self.params[i, 3]
            y_total += band.band2chi(self.xgrid)
        return y_total

    def peak_table(self):
        """Return a list of per-band dicts with fitted peak descriptors."""
        rows = []
        for i, name in enumerate(self.bandnames):
            band = self.bandDictionary[name]
            amp, shift, width, cshift = self.params[i]
            rows.append(
                {
                    "band": name,
                    "nominal_center": band.center,
                    "fitted_center": band.center + cshift + shift,
                    "amplitude": float(amp),
                    "width": float(width),
                    "center_shift": float(cshift),
                    "shape": band.shape,
                    "area": band.area(self.xgrid),
                }
            )
        return rows

    def r_factor(self):
        return r_factor(self.model, self.exp, self.interval)

    def residual(self):
        return self.exp - self.model

    def report(self):
        """Return a formatted multi-line text report."""
        lines = []
        lines.append("=" * 60)
        lines.append("raman_neo fit report")
        lines.append("=" * 60)
        lines.append(f"Global shift (cm^-1) : {self.shift:.3f}")
        lines.append(f"Final fitness        : {self.raman_pars.bestFitPars.globBestVal:.4f}")
        lines.append(f"R-factor             : {self.r_factor():.5f}")
        lines.append("-" * 60)
        lines.append(f"{'band':>8} {'center':>9} {'amp':>8} {'width':>8} {'area':>10}")
        for row in self.peak_table():
            lines.append(
                f"{row['band']:>8} {row['fitted_center']:>9.2f} "
                f"{row['amplitude']:>8.3f} {row['width']:>8.2f} {row['area']:>10.2f}"
            )
        lines.append("=" * 60)
        return "\n".join(lines)

    def plot(self, ax=None):
        import matplotlib.pyplot as plt

        if ax is None:
            _, ax = plt.subplots(figsize=(8, 5))
        idx = self.interval
        ax.plot(self.xgrid[idx], self.exp[idx], "k-", lw=1.2, label="experiment")
        ax.plot(self.xgrid[idx], self.model[idx], "r--", lw=1.2, label="fit")
        ax.plot(self.xgrid[idx], self.residual()[idx] - 0.2, "b-", lw=0.8, label="residual")
        ax.set_xlabel("Raman shift (cm$^{-1}$)")
        ax.set_ylabel("Intensity (norm.)")
        ax.legend()
        return ax
