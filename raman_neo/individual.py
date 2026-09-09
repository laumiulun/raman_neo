"""A GA individual: one candidate set of band parameters.

Raman analogue of ``exafs_neo.individual.Individual``. Parameter slots follow
EXAFS ordering ``[amp, shift, width, center_shift]`` so the operators are
unchanged in structure.
"""

from typing import AnyStr

from raman_neo.bandObj import BandObject


class Individual:
    def __init__(
        self,
        nbands: int,
        bandDictionary: dict,
        bandrange_Dict: list,
        bandlists: list,
        shift: float,
        bandName: AnyStr,
    ):
        self.nbands = nbands
        self.band_lists = bandlists
        self.bandname = bandName
        self.Population = []
        self.bandrange_Dict = bandrange_Dict
        self.bandDictionary = bandDictionary

        for this_band in self.bandrange_Dict:
            self.Population.append(BandObject(this_band, shift))

    def get(self) -> list:
        """Return an (nbands, 4) list of [amp, shift, width, center_shift]."""
        return [self.Population[i].get() for i in range(self.nbands)]

    def get_var(self) -> list:
        """Return an (nbands, 3) list of [amp, width, center_shift]."""
        return [self.Population[i].get_var() for i in range(self.nbands)]

    def get_e0(self) -> float:
        """Return the shared global shift."""
        return self.Population[0].get_e0()

    def get_band(self, i):
        return self.Population[i].get()

    # Backwards-compatible alias (EXAFS naming).
    def get_path(self, i):
        return self.get_band(i)

    def verbose(self) -> None:
        for i in range(self.nbands):
            self.Population[i].verbose()

    def set_band(self, i: int, amp: float, width: float, center_shift: float) -> None:
        self.Population[i].set(amp, width, center_shift)

    def set_path(self, i: int, amp: float, width: float, center_shift: float) -> None:
        self.set_band(i, amp, width, center_shift)

    def set_e0(self, shift: float) -> None:
        for i in range(self.nbands):
            self.Population[i].set_e0(shift)

    def mutate_bands(self, chance: float) -> None:
        for band in self.Population:
            band.mutate(chance)

    def mutate_paths(self, chance: float) -> None:
        self.mutate_bands(chance)

    def __len__(self) -> int:
        return int((3 * self.nbands) + 1)

    def __str__(self) -> AnyStr:
        return f"Individual with values of {self.get()}"
