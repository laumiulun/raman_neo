"""Selection operators. Raman analogue of ``exafs_neo.neoSelector``."""

from raman_neo.neoPars import NeoPars
from raman_neo.utils import NeoLogger


class NeoSelectorBase:
    def __init__(self, raman_pars: NeoPars, logger: NeoLogger):
        self.logger = logger
        self.raman_pars = raman_pars
        self.npops = raman_pars.fixedPars.nPops
        self.nBest_Percent = raman_pars.selPars.nBestSample
        self.nLucky_Percent = raman_pars.selPars.nLuckSample

        self.nBest = int(self.nBest_Percent * self.npops)
        self.nLucky = int(self.nLucky_Percent * self.npops)
        self.nStatic = int(self.npops - self.nBest - self.nLucky)

        self.sel_list = []

    def select(self, pops):
        pass

    def __str__(self):
        return f"Top Percentage: {100 * self.nBest_Percent}%, Lucky: {100 * self.nLucky_Percent}%"


class NeoSelector_RouletteWheel(NeoSelectorBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.selector_type = 0
        self.selector_operator = "Roulette Wheel"

    def select(self, pops):
        next_population = []
        for i in range(self.nBest):
            next_population.append(pops.population_sorted[i][0])
        for _ in range(self.nLucky):
            next_population.append(pops.generate_individual())
        pops.next_population = next_population


class NeoSelector_Tournament(NeoSelectorBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.selector_type = 1
        self.selector_operator = "Tournament"

    def select(self, pops):
        pass


class NeoSelector:
    def __init__(self, logger=None):
        self.selector_operator = None
        self.logger = logger
        self.selector_type = None
        self.raman_pars = None

    def initialize(self, raman_pars):
        self.raman_pars = raman_pars
        self.selector_type = raman_pars.selPars.selOpt
        if self.selector_type == 0:
            self.selector_operator = NeoSelector_RouletteWheel(raman_pars, logger=self.logger)
        elif self.selector_type == 1:
            self.selector_operator = NeoSelector_Tournament(raman_pars, logger=self.logger)
        else:
            self.selector_operator = NeoSelectorBase(raman_pars, logger=self.logger)
            raise ValueError("Invalid selector type, returning standard selector type.")

    def select(self, pops):
        if self.selector_operator is None:
            raise ValueError("Selector is not initialized")
        return self.selector_operator.select(pops)

    def __str__(self):
        if self.selector_operator is None:
            return "None Selector selected"
        return f"Selector Type: {self.selector_type}, {self.selector_operator}"
