"""GA solvers. Raman analogue of ``exafs_neo.neoSolver``."""

import numpy as np

from raman_neo.neoPars import NeoPars
from raman_neo.utils import NeoLogger


class NeoSolverBase:
    def __init__(self, raman_pars: NeoPars, logger: NeoLogger):
        self.logger = logger
        self.raman_pars = raman_pars
        self.sol_list = []

    def solve(self, pops, selector, crossover, mutator, raman_pars):
        pass

    def __str__(self):
        return "Neo Solver"


class NeoSolver_GA(NeoSolverBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.solver_type = 0
        self.solver_operator = "Genetic Algorithm"

    def solve(self, pops, selector, crossover, mutator, raman_pars):
        selector.select(pops)
        crossover.crossover(pops)
        mutator.mutate(pops)
        pops.eval_population()


class NeoSolver_GA_Rechenberg(NeoSolverBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.solver_type = 1
        self.solver_operator = "Genetic Algorithm with Rechenberg"
        self.diffCounter = 0

    def solve(self, pops, selector, crossover, mutator, neo_pars):
        selector.select(pops)
        crossover.crossover(pops)
        self.rechenberg_mutation(neo_pars)
        mutator.mutate(pops)
        pops.eval_population()

    def rechenberg_mutation(self, neo_pars: NeoPars):
        diffCounter = neo_pars.runPars.diffCounter
        bestDiff = np.abs(neo_pars.bestFitPars.globBestVal - neo_pars.bestFitPars.currBestVal)
        if neo_pars.runPars.currGen > 20:
            if bestDiff < 0.1:
                diffCounter += 1
            else:
                diffCounter -= 1
            diffCounter = np.clip(diffCounter, 0, None)

            if (abs(diffCounter) / float(neo_pars.runPars.currGen)) > 0.2:
                if (neo_pars.mutPars.mutChance + 0.0025) < 1.0:
                    neo_pars.mutPars.mutChance += 0.0025
                    neo_pars.mutPars.mutChance = abs(neo_pars.mutPars.mutChance)
            elif (abs(diffCounter) / float(neo_pars.runPars.currGen)) < 0.2:
                if (neo_pars.mutPars.mutChance - 0.0025) > 0:
                    neo_pars.mutPars.mutChance -= 0.0025
            neo_pars.mutPars.mutChance = np.clip(neo_pars.mutPars.mutChance, 0, 1.0)

        neo_pars.runPars.diffCounter = diffCounter
        return neo_pars


class NeoSolver_DE(NeoSolverBase):
    def __init__(self, raman_pars, logger):
        super().__init__(raman_pars, logger)
        self.solver_type = 2
        self.solver_operator = "Differential Evolution"

    def solve(self, pops, selector, crossover, mutator, raman_pars):
        pass


class NeoSolver:
    def __init__(self, logger=None):
        self.solver_operator = None
        self.logger = logger
        self.solver_type = None
        self.raman_pars = None

    def initialize(self, raman_pars):
        self.raman_pars = raman_pars
        self.solver_type = raman_pars.solPars.solOpt
        if self.solver_type == 0:
            self.solver_operator = NeoSolver_GA(raman_pars, logger=self.logger)
        elif self.solver_type == 1:
            self.solver_operator = NeoSolver_GA_Rechenberg(raman_pars, logger=self.logger)
        elif self.solver_type == 2:
            self.solver_operator = NeoSolver_DE(raman_pars, logger=self.logger)
        else:
            self.solver_operator = NeoSolverBase(raman_pars, logger=self.logger)
            raise ValueError("Invalid solver type, returning standard solver type.")

    def solve(self, pops, selector, crossover, mutator, raman_pars):
        if self.solver_operator is None:
            raise ValueError("Solver is not initialized")
        return self.solver_operator.solve(pops, selector, crossover, mutator, raman_pars)

    def __str__(self):
        if self.solver_operator is None:
            return "None Solver selected"
        return f"Solver Type: {self.solver_type}, {self.solver_operator}"
