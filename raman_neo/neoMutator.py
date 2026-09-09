"""Mutation operators. Raman analogue of ``exafs_neo.neoMutator``."""

import copy

import numpy as np

from raman_neo.raman_pop import fitness


class RamanMutatorBase:
    def __init__(self, raman_pars, logger):
        self.logger = logger
        self.raman_pars = raman_pars
        self.mutOpt = self.raman_pars.mutPars.mutOpt
        self.mutChance = self.raman_pars.mutPars.mutChance
        self.mutChanceE0 = self.raman_pars.mutPars.mutChanceE0
        self.mutType = None

    def mutate(self, pops):
        pass

    def __str__(self):
        return f"mutation chance: {self.mutChance}%, shift mutation chance: {self.mutChanceE0}%"


class RamanMutator_PerIndividual(RamanMutatorBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.mutOpt = 0
        self.mutType = "Mutate Per Individual"

    def mutate(self, pops):
        for i, _ in enumerate(pops.population):
            if np.random.random() < self.mutChance:
                pops.population[i] = pops.generate_individual()
                self.raman_pars.mutPars.nmut += 1


class RamanMutator_PerBand(RamanMutatorBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.mutOpt = 1
        self.mutType = "Mutate Per Band"

    def mutate(self, pops):
        for i in range(len(pops.population)):
            if np.random.random() < self.mutChance:
                pops.population[i].mutate_bands(self.mutChance)
                self.raman_pars.mutPars.nmut += 1


class RamanMutator_PerTrait(RamanMutatorBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.mutOpt = 2
        self.mutType = "Mutate Per Trait"

    def mutate(self, pops):
        for pop in pops.population:
            for j in range(pop.nbands):
                if np.random.random() < self.mutChance:
                    pop.Population[j].mutate(self.mutChance * 100)


class RamanMutator_Metropolis(RamanMutatorBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.mutOpt = 3
        self.mutType = "Mutate Metropolis"

    def mutate(self, pops):
        for i, indi in enumerate(pops.population):
            if np.random.random() < self.mutChance:
                og_indi = copy.deepcopy(indi)
                og_score = fitness(self.raman_pars, og_indi)
                mut_indi = copy.deepcopy(indi)
                mut_indi.mutate_bands(self.mutChance)
                mut_score = fitness(self.raman_pars, mut_indi)
                ratio = 1 - (self.raman_pars.runPars.currGen / self.raman_pars.fixedPars.nGen)
                ratio = ratio if ratio > 1e-9 else 1e-9
                bestDiff = self.raman_pars.bestFitPars.bestDiff
                bestDiff = bestDiff if np.isfinite(bestDiff) and bestDiff != 0 else 1.0
                T = -bestDiff / np.log(ratio)
                T = T if T != 0 else 1e-9
                if mut_score < og_score:
                    newIndi = mut_indi
                elif np.exp(-(mut_score - og_score) / T) > np.random.uniform():
                    newIndi = mut_indi
                else:
                    newIndi = og_indi
                pops.population[i] = newIndi


class RamanMutator_Bounded(RamanMutatorBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.mutOpt = 4
        self.mutType = "Mutate Bounded Per Range"

    def mutate(self, pops):
        def delta_fun(t, delta_val):
            rnd = np.random.random()
            return delta_val * (1 - rnd ** (1 - (t / self.raman_pars.fixedPars.nGen)) ** 5)

        for indi in pops.population:
            if np.random.random() < self.mutChance:
                og_data = indi.get_var()
                for j, band in enumerate(og_data):
                    arr = np.random.randint(2, size=3)
                    new_band = []
                    for k in range(len(arr)):
                        val = band[k]
                        lim = self.raman_pars.ramanRangePars.bandrange_pars[j].get_lim()[k + 1]
                        if arr[k] == 0:
                            del_val = delta_fun(self.raman_pars.runPars.currGen, lim[1] - val)
                            val = val + del_val
                        else:
                            del_val = delta_fun(self.raman_pars.runPars.currGen, val - lim[0])
                            val = val - del_val
                        new_band.append(val)
                    indi.set_band(j, new_band[0], new_band[1], new_band[2])


class RamanMutator_DE(RamanMutatorBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.mutOpt = 5
        self.mutType = "Mutate Differential Evolution"

    def mutate(self, pops):
        pass


class NeoMutator:
    def __init__(self, logger=None):
        self.mutator = None
        self.logger = logger
        self.mutator_type = None
        self.raman_pars = None
        self.mutator_score = 0

    def initialize(self, raman_pars):
        self.raman_pars = raman_pars
        self.mutator_type = raman_pars.mutPars.mutOpt
        mapping = {
            0: RamanMutator_PerIndividual,
            1: RamanMutator_PerBand,
            2: RamanMutator_PerTrait,
            3: RamanMutator_Metropolis,
            4: RamanMutator_Bounded,
            5: RamanMutator_DE,
        }
        cls = mapping.get(self.mutator_type)
        if cls is None:
            self.mutator = RamanMutatorBase(self.raman_pars, logger=self.logger)
            raise ValueError("Invalid mutator type")
        self.mutator = cls(self.raman_pars, logger=self.logger)
        return self.mutator

    def __str__(self):
        if self.mutator is None:
            return "None Mutator selected"
        return f"Mutator Type: {self.mutator.mutType}, {self.mutator}"

    def mutate(self, pops):
        if self.mutator is None:
            raise ValueError("Mutator is not initialized")
        if self.raman_pars.runPars.secondHalf:
            self.mutate_e0(pops)
        self.mutator.mutate(pops)

    def mutate_e0(self, pops):
        """Mutate the shared global shift in the second half of the run."""
        if np.random.random() * 100 < self.mutator.mutChanceE0:
            shift = float(np.random.choice(self.raman_pars.ramanRangePars.rangeE0))
            if self.raman_pars.verbose_lvl >= 5 and self.logger is not None:
                self.logger.print(f"Mutate shift to: {shift:.3f}")
            for individual in pops.population:
                individual.set_e0(shift)
