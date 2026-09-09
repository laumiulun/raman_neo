"""Run result container. Raman analogue of ``exafs_neo.neoResult``."""

import pickle

import numpy as np
from attrs import define, field

from raman_neo.raman_pop import fitness
from raman_neo.utils import NeoLogger


@define
class NeoResult:
    raman_pars: object = None
    best_individual: object = None
    historyBest: list = field(factory=list)
    historyBestChiR: list = field(factory=list)
    genBest: list = field(factory=list)
    crossover_scorelist: list = field(factory=list)
    mutation_scorelist: list = field(factory=list)
    logger: NeoLogger = None

    def __str__(self) -> str:
        if self.best_individual is None:
            return "Best Individual: None"
        return f"Best Individual: {self.best_individual}"

    def save(self, filename: str) -> None:
        try:
            with open(filename, "wb") as file:
                pickle.dump(self, file)
        except Exception as e:
            if self.logger is not None:
                self.logger.print(f"Error saving file: {e}")

    @classmethod
    def load(cls, filename: str):
        try:
            with open(filename, "rb") as file:
                obj = pickle.load(file)
            print(f"Object loaded from {filename}")
            return obj
        except Exception as e:
            print(f"Error loading object: {e}")
            return None

    def initialize(self, raman_pars) -> None:
        self.raman_pars = raman_pars

    def collect(self, neo_population, raman_pars) -> None:
        self.raman_pars = raman_pars
        self.best_individual = neo_population.population_sorted[0][0]
        self.historyBest.append(raman_pars.bestFitPars.globBestVal)
        self.genBest.append(raman_pars.bestFitPars.currBestVal)
        denom = len(raman_pars.ramanPars.intervalK) - 3 * raman_pars.ramanPars.nband + 1
        denom = denom if denom != 0 else 1
        self.historyBestChiR.append(raman_pars.bestFitPars.globBestVal / denom)

    def best_curve(self):
        """Return (xgrid, model, experimental) for the best individual."""
        band_pars = self.raman_pars.ramanBandPars
        _, y_total = fitness(self.raman_pars, self.best_individual, return_tot=True)
        return band_pars.xgrid, y_total, band_pars.exp

    def plot_fitness(self, ax=None):
        import matplotlib.pyplot as plt

        if ax is None:
            _, ax = plt.subplots()
        x = np.arange(0, len(self.historyBest), 1)
        ax.plot(x, self.historyBest, label="Fitness")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Fitness")
        ax.legend()
        return ax
