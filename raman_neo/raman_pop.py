"""Population container and fitness function.

Raman analogue of ``exafs_neo.exafs_pop``. The fitness synthesises the total
model spectrum by summing the band line shapes and compares it to the
experimental spectrum with an optional wavenumber weighting.
"""

import copy
import operator
from typing import Any

import numpy as np
from attrs import define, field

from raman_neo.individual import Individual
from raman_neo.neoPars import NeoPars


def fitness(raman_neo_pars, ind_obj, return_tot=False):
    """Sum-of-squares misfit between the synthesised and experimental spectra."""
    band_pars = raman_neo_pars.ramanBandPars
    static = raman_neo_pars.ramanPars

    y_total = np.zeros(static.npts)
    idx = static.intervalK
    weight = static.weight

    shift_val = ind_obj.get_e0()

    for i in range(static.nband):
        name = band_pars.bandname[i]
        band = band_pars.bandDictionary.get(name)

        band_params = ind_obj.get_band(i)
        band.amp = band_params[0]
        band.shift = shift_val
        band.width = band_params[2]
        band.center_shift = band_params[3]

        y = band.band2chi(band_pars.xgrid)
        y_total[idx] += y[idx]

    exp_idx = band_pars.exp[idx]
    if weight and weight != 0.0:
        w = band_pars.xgrid[idx] ** weight
    else:
        w = 1.0

    weighted_diff = (y_total[idx] - exp_idx) * w
    loss = float(np.sum(weighted_diff**2))

    if return_tot:
        return loss, y_total
    return loss


@define
class NeoPopulations:
    raman_NeoPars: NeoPars = None
    population: list = field(factory=list)
    population_sorted: list = field(factory=list)
    population_score: list = field(factory=list)
    population_perf: dict = field(factory=dict)
    next_population: list = field(factory=list)

    def generate_individual(self) -> Individual:
        if not self.raman_NeoPars.runPars.secondHalf:
            shift = float(np.random.choice(self.raman_NeoPars.ramanRangePars.rangeE0))
        else:
            shift = self.raman_NeoPars.bestFitPars.bestE0
        return Individual(
            self.raman_NeoPars.ramanPars.nband,
            self.raman_NeoPars.ramanBandPars.bandDictionary,
            self.raman_NeoPars.ramanRangePars.bandrange_pars,
            self.raman_NeoPars.ramanBandPars.band_lists,
            shift,
            self.raman_NeoPars.ramanBandPars.bandname,
        )

    def eval_population(self, replace=True, sorting=True) -> list:
        score = []
        population_perf = {}
        for individual in self.population:
            temp_score = fitness(self.raman_NeoPars, individual)
            score.append(temp_score)
            population_perf[individual] = temp_score
        if sorting:
            self.population_sorted = sorted(
                population_perf.items(), key=operator.itemgetter(1), reverse=False
            )
        if replace:
            self.__replace_bestfit()
        return score

    def initialize_populations(self) -> None:
        for _ in range(self.raman_NeoPars.fixedPars.nPops):
            self.population.append(self.generate_individual())
        self.eval_population()

    def __getitem__(self, item) -> "list[Any] | Any":
        return self.population_sorted[item]

    def __replace_bestfit(self) -> None:
        best = self.raman_NeoPars.bestFitPars
        best.currBestInd = self.population_sorted[0][0]
        best.currBestVal = self.population_sorted[0][1]

        delta = best.globBestVal - best.currBestVal
        if np.abs(delta) > 0.01:
            best.bestDiff = delta
        else:
            best.bestDiff = 0

        if best.currBestVal < best.globBestVal:
            best.globBestInd = best.currBestInd
            best.globBestVal = best.currBestVal

    def optimize_e0(self) -> None:
        """Scan the global wavenumber shift for the best value (E0 analogue)."""
        best = self.raman_NeoPars.bestFitPars
        if best.globBestInd is None:
            return
        curr_ind = copy.deepcopy(best.globBestInd)
        curr_score = copy.deepcopy(best.globBestVal)
        curr_shift = curr_ind.get_e0()
        for i in self.raman_NeoPars.ramanRangePars.rangeE0_large:
            curr_ind.set_e0(i)
            fit_score = fitness(self.raman_NeoPars, curr_ind)
            if fit_score < curr_score:
                curr_shift = i
                curr_score = fit_score
        new_shift = curr_shift
        best.bestE0 = new_shift
        best.globBestInd.set_e0(new_shift)
        best.globBestVal = curr_score
        for ind in self.population:
            ind.set_e0(new_shift)
        best.bestE0 = new_shift


if __name__ == "__main__":
    inputs_pars = {
        "data_file": "raman_neo/data/sample_raman.dat",
        "output_file": "sample_out.csv",
        "band_file": "raman_neo/data/sample_bands.txt",
        "xmin": 100,
        "xmax": 1800,
        "deltax": 1.0,
        "bandrange": [1, 2, 3, 4],
    }
    raman_NeoPars = NeoPars()
    raman_NeoPars.read_inputs(inputs_pars)
    neo_population = NeoPopulations(raman_NeoPars)
    neo_population.initialize_populations()
    print("best score:", neo_population.population_sorted[0][1])
