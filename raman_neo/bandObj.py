"""Per-band GA parameter holder.

Raman analogue of ``exafs_neo.pathObj.PathObject``. ``get()`` returns the four
parameters in the same slot order as EXAFS_Neo::

    [amp, shift, width, center_shift]   <->   [s02, e0, sigma2, deltaR]

so the crossover/mutation operators are unchanged from the EXAFS version.
"""

import random

import attr
import numpy as np

from raman_neo.bandrange import Bandrange_limits


@attr.s(slots=True)
class BandObject:
    bandrange_obj: Bandrange_limits = attr.ib()
    shift: float = attr.ib()  # <- e0 (global, shared across bands)
    Amp_range = attr.ib(default=list)
    Shift_range = attr.ib(default=list)
    Width_range = attr.ib(default=list)
    Cshift_range = attr.ib(default=list)

    amp = attr.ib(default=0)
    width = attr.ib(default=0)
    center_shift = attr.ib(default=0)

    def __attrs_post_init__(self):
        self.Amp_range = self.bandrange_obj.getrange_Amp()
        self.Shift_range = self.bandrange_obj.getrange_Shift()
        self.Width_range = self.bandrange_obj.getrange_Width()
        self.Cshift_range = self.bandrange_obj.getrange_Cshift()

        self.amp = np.random.choice(self.Amp_range)
        self.width = np.random.choice(self.Width_range)
        self.center_shift = np.random.choice(self.Cshift_range)

    def get(self):
        return [self.amp, self.shift, self.width, self.center_shift]

    def get_var(self):
        return [self.amp, self.width, self.center_shift]

    def verbose(self):
        print(self.amp, self.shift, self.width, self.center_shift)

    def get_e0(self):
        return self.shift

    # ----------------- setters -----------------
    def set_amp(self, amp):
        self.amp = amp

    def set_e0(self, shift):
        np.clip(shift, self.Shift_range[0], self.Shift_range[-1])
        self.shift = shift

    def set_width(self, width):
        self.width = width

    def set_center_shift(self, center_shift):
        self.center_shift = center_shift

    def set(self, amp, width, center_shift):
        self.set_amp(amp)
        self.set_width(width)
        self.set_center_shift(center_shift)

    # ----------------- mutation -----------------
    def __mutate_amp(self, chance):
        if random.random() * 100 < chance:
            self.amp = np.random.choice(self.bandrange_obj.getrange_Amp())

    def __mutate_width(self, chance):
        if random.random() * 100 < chance:
            self.width = np.random.choice(self.bandrange_obj.getrange_Width())

    def __mutate_center_shift(self, chance):
        if random.random() * 100 < chance:
            self.center_shift = np.random.choice(self.bandrange_obj.getrange_Cshift())

    def mutate(self, chance):
        self.__mutate_amp(chance)
        self.__mutate_width(chance)
        self.__mutate_center_shift(chance)

    def __str__(self):
        return (
            f"BandObject: amp: {np.round(self.amp, 3)}, shift: {np.round(self.shift, 2)}, "
            f"width: {np.round(self.width, 2)}, center_shift: {np.round(self.center_shift, 2)}"
        )


if __name__ == "__main__":
    bandrange_Obj = Bandrange_limits(0)
    bandObj = BandObject(bandrange_Obj, 0.0)
    print(bandObj)
