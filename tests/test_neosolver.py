import pytest

from raman_neo.neoCrossOver import NeoCrossover
from raman_neo.neoMutator import NeoMutator
from raman_neo.neoPars import NeoPars
from raman_neo.neoSelector import NeoSelector
from raman_neo.neoSolver import NeoSolver
from raman_neo.raman_pop import NeoPopulations


@pytest.mark.parametrize("solOpt", [0, 1])
def test_solver_step_reduces_or_keeps_best(base_inputs, solOpt):
    base_inputs["solOpt"] = solOpt
    pars = NeoPars()
    pars.read_inputs(base_inputs)
    pop = NeoPopulations(pars)
    pop.initialize_populations()

    sel = NeoSelector()
    sel.initialize(pars)
    cross = NeoCrossover()
    cross.initialize(pars)
    mut = NeoMutator()
    mut.initialize(pars)
    solver = NeoSolver()
    solver.initialize(pars)

    best_before = pars.bestFitPars.globBestVal
    for _ in range(3):
        pars.runPars.start_gen()
        solver.solve(pop, sel, cross, mut, pars)
    # global best is monotonically non-increasing
    assert pars.bestFitPars.globBestVal <= best_before + 1e-9


def test_invalid_solver_raises(base_inputs):
    base_inputs["solOpt"] = 99
    pars = NeoPars()
    pars.read_inputs(base_inputs)
    solver = NeoSolver()
    with pytest.raises(ValueError):
        solver.initialize(pars)
