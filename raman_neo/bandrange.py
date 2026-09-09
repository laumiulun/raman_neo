"""Per-band parameter ranges for the GA search.

Raman analogue of ``exafs_neo.pathrange``. Each band has three searchable
per-band parameters (amplitude, width, centre shift) plus the shared global
shift. The discrete ranges below are what the GA samples and mutates over.

Custom range file format (one band per row, 10 comma-separated columns)::

    band, amp_low, amp_high, amp_dt, width_low, width_high, width_dt,
          cshift_low, cshift_high, cshift_dt
"""

import copy

import numpy as np

from raman_neo.utils import raise_error


class Bandrange_limits:
    _tol = 1e-13

    def __init__(self, _band_, custom_range=None):
        self._band_ = _band_
        self.offset_val = 3

        if custom_range is None:
            self.rangeAmp = np.arange(0.02, 2.0, 0.02)
            self.rangeAmp = np.insert(self.rangeAmp, 0, 0)
            self.rangeShift = np.arange(-10, 10.1, 0.1)
            self.rangeWidth = np.arange(2.0, 40.0, 1.0)
            self.rangeCshift = np.arange(-15, 15.1, 1.0)

            self.Amp_min = np.min(self.rangeAmp)
            self.Amp_max = np.max(self.rangeAmp)
            self.Amp_dt = 0.02

            self.Width_min = np.min(self.rangeWidth)
            self.Width_max = np.max(self.rangeWidth)
            self.Width_dt = 1.0

            self.Cshift_min = np.min(self.rangeCshift)
            self.Cshift_max = np.max(self.rangeCshift)
            self.Cshift_dt = 1.0
        else:
            self.Amp_min = custom_range[1]
            self.Amp_max = custom_range[2]
            self.Amp_dt = custom_range[3]

            self.Width_min = custom_range[4]
            self.Width_max = custom_range[5]
            self.Width_dt = custom_range[6]

            self.Cshift_min = custom_range[7]
            self.Cshift_max = custom_range[8]
            self.Cshift_dt = custom_range[9]
            # -----
            self.rangeAmp = np.arange(self.Amp_min, self.Amp_max, self.Amp_dt)
            self.rangeShift = np.arange(-10, 10.1, 0.1)
            self.rangeWidth = np.arange(self.Width_min, self.Width_max, self.Width_dt)
            self.rangeCshift = np.arange(self.Cshift_min, self.Cshift_max, self.Cshift_dt)

        self.glob_rangeAmp = copy.deepcopy(self.rangeAmp)
        self.glob_rangeShift = copy.deepcopy(self.rangeShift)
        self.glob_rangeWidth = copy.deepcopy(self.rangeWidth)
        self.glob_rangeCshift = copy.deepcopy(self.rangeCshift)

    def get_lim(self):
        return (
            self._band_,
            self.get_lim_Amp(),
            self.get_lim_Width(),
            self.get_lim_Cshift(),
        )

    def get_lim_Amp(self):
        return self.Amp_min, self.Amp_max, self.Amp_dt

    def get_lim_Width(self):
        return self.Width_min, self.Width_max, self.Width_dt

    def get_lim_Cshift(self):
        return self.Cshift_min, self.Cshift_max, self.Cshift_dt

    def get_lim_Shift(self):
        return -10, 10, 0.1

    def get_band(self):
        return self._band_

    def getrange_Amp(self):
        return self.rangeAmp

    def getrange_Shift(self):
        return self.rangeShift

    def getrange_Width(self):
        return self.rangeWidth

    def getrange_Cshift(self):
        return self.rangeCshift

    def getrange(self):
        return (
            self.getrange_Amp(),
            self.getrange_Shift(),
            self.getrange_Width(),
            self.getrange_Cshift(),
        )

    # Narrow a range to a window around a value (used by band_optimize).
    def mod_range(self, glob_arr, val):
        index = next(i for i, _ in enumerate(glob_arr) if np.isclose(_, val, self._tol))
        lower = index - self.offset_val
        upper = index + self.offset_val
        if lower < 0:
            lower = 0
        if upper >= len(glob_arr):
            upper = len(glob_arr) - 1
        return glob_arr[lower : upper + 1]

    def mod_amp(self, val):
        self.rangeAmp = self.mod_range(self.glob_rangeAmp, val)

    def mod_shift(self, val):
        self.rangeShift = self.mod_range(self.glob_rangeShift, val)

    def mod_width(self, val):
        self.rangeWidth = self.mod_range(self.glob_rangeWidth, val)

    def mod_cshift(self, val):
        self.rangeCshift = self.mod_range(self.glob_rangeCshift, val)


def check_range(val_low, val_high, delta_val):
    if np.abs(val_high - val_low) / delta_val < 1:
        raise_error("Delta Spacing too high")
    return np.arange(val_low, val_high, delta_val)


def read_bandrange_file(file, num_band):
    """Read a custom per-band range file (10 columns per band)."""
    raw_data = np.genfromtxt(file, delimiter=",")
    if raw_data.ndim == 1:
        raw_data = raw_data.reshape(1, -1)
    raw_nband = raw_data.shape[0]
    if num_band != raw_nband:
        raise_error("Mismatch in number of bands")
    if raw_data.shape[1] != 10:
        raise_error("Number of Columns not right")
    for i in range(num_band):
        check_range(raw_data[i][1], raw_data[i][2], raw_data[i][3])
        check_range(raw_data[i][4], raw_data[i][5], raw_data[i][6])
        check_range(raw_data[i][7], raw_data[i][8], raw_data[i][9])
    return raw_data


if __name__ == "__main__":
    br = Bandrange_limits(0)
    print(br.get_lim())
