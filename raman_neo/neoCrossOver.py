"""Crossover operators. Raman analogue of ``exafs_neo.neoCrossOver``.

Each child band takes parameters from one of the two parents, slot by slot,
using the EXAFS 4-slot ordering ``[amp, shift, width, center_shift]``.
"""

import numpy as np


class Raman_CrossoverBase:
    def __init__(self, raman_pars, logger=None):
        self.logger = logger
        self.raman_pars = raman_pars
        self.croOpt = self.raman_pars.crossPars.croOpt
        self.croType = None

    def crossover(self, pops, individual1, individual2):
        pass

    def __str__(self):
        return f"Crossover Option: {self.croType}"

    def _nband(self):
        return self.raman_pars.ramanBandPars.nband

    def _child_with_shift(self, pops, individual1, individual2):
        child = pops.generate_individual()
        if np.random.randint(0, 1):
            child.set_e0(individual1.get_e0())
        else:
            child.set_e0(individual2.get_e0())
        return child


class Raman_UniformCrossover(Raman_CrossoverBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.croOpt = 0
        self.croType = "Uniform Crossover"

    def crossover(self, pops, individual1, individual2):
        child = self._child_with_shift(pops, individual1, individual2)
        for i in range(self._nband()):
            b1 = individual1.get_band(i)
            b2 = individual2.get_band(i)
            temp = []
            for j in range(4):
                temp.append(b1[j] if np.random.randint(0, 2) else b2[j])
            child.set_band(i, temp[0], temp[2], temp[3])
        return child


class Raman_SinglePointCrossover(Raman_CrossoverBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.croOpt = 1
        self.croType = "Single Point Crossover"

    def crossover(self, pops, individual1, individual2, co_point=1):
        co_point = np.clip(co_point, 0, 3)
        child = self._child_with_shift(pops, individual1, individual2)
        for i in range(self._nband()):
            b1 = individual1.get_band(i)
            b2 = individual2.get_band(i)
            temp = []
            for j in range(4):
                temp.append(b1[j] if j < co_point else b2[j])
            child.set_band(i, temp[0], temp[2], temp[3])
        return child


class Raman_DualPointCrossover(Raman_CrossoverBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.croOpt = 2
        self.croType = "Dual Point Crossover"

    def crossover(self, pops, individual1, individual2):
        pass


class Raman_ArithmeticCrossover(Raman_CrossoverBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.croOpt = 3
        self.croType = "Arithmetic Crossover"

    def crossover(self, pops, individual1, individual2):
        child = self._child_with_shift(pops, individual1, individual2)
        for i in range(self._nband()):
            b1 = individual1.get_band(i)
            b2 = individual2.get_band(i)
            temp = []
            for j in range(4):
                ind_1 = np.random.randint(0, 2)
                ind_2 = np.random.randint(0, 2)
                temp.append(b1[j] if np.logical_and(ind_1, ind_2) else b2[j])
            child.set_band(i, temp[0], temp[2], temp[3])
        return child


class Raman_OrCrossover(Raman_CrossoverBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.croOpt = 4
        self.croType = "Or Crossover"

    def crossover(self, pops, individual1, individual2):
        child = self._child_with_shift(pops, individual1, individual2)
        for i in range(self._nband()):
            b1 = individual1.get_band(i)
            b2 = individual2.get_band(i)
            temp = []
            for j in range(4):
                ind_1 = np.random.randint(0, 2)
                ind_2 = np.random.randint(0, 2)
                temp.append(b1[j] if np.logical_or(ind_1, ind_2) else b2[j])
            child.set_band(i, temp[0], temp[2], temp[3])
        return child


class Raman_AverageCrossOver(Raman_CrossoverBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.croOpt = 5
        self.croType = "Average Crossover"

    def crossover(self, pops, individual1, individual2):
        child = self._child_with_shift(pops, individual1, individual2)
        for i in range(self._nband()):
            b1 = individual1.get_band(i)
            b2 = individual2.get_band(i)
            temp = [(b1[j] + b2[j]) / 2 for j in range(4)]
            child.set_band(i, temp[0], temp[2], temp[3])
        return child


class NeoCrossover:
    def __init__(self, logger=None):
        self.logger = logger
        self.raman_pars = None
        self.crossover_type = None
        self.crossover_operator = None
        self.crossover_score = 0

    def initialize(self, raman_pars):
        self.raman_pars = raman_pars
        self.crossover_type = raman_pars.crossPars.croOpt
        mapping = {
            0: Raman_UniformCrossover,
            1: Raman_SinglePointCrossover,
            2: Raman_DualPointCrossover,
            3: Raman_ArithmeticCrossover,
            4: Raman_OrCrossover,
            5: Raman_AverageCrossOver,
        }
        cls = mapping.get(self.crossover_type)
        if cls is None:
            self.crossover_operator = Raman_CrossoverBase(raman_pars, logger=self.logger)
            raise ValueError("Invalid crossover type, returning standard crossover type.")
        self.crossover_operator = cls(raman_pars, logger=self.logger)

    def __str__(self):
        if self.crossover_operator is None:
            return "Crossover is not selected"
        return f"Crossover Type: {self.crossover_type}, {self.crossover_operator}"

    def crossover(self, pops):
        if self.crossover_operator is None:
            raise ValueError("Crossover is not initialized")
        temp_population = []
        if len(pops.next_population) > 2:
            for _ in range(self.raman_pars.selPars.nCross):
                par_ind = np.random.choice(len(pops.next_population), size=2, replace=False)
                ind1 = pops.next_population[par_ind[0]]
                ind2 = pops.next_population[par_ind[1]]
                child = self.crossover_operator.crossover(pops, ind1, ind2)
                temp_population.append(child)
            pops.next_population.extend(temp_population)
            pops.population = pops.next_population

    def crossover_single(self, pops, ind1, ind2):
        if self.crossover_operator is None:
            raise ValueError("Crossover is not initialized")
        return self.crossover_operator.crossover(pops, ind1, ind2)
