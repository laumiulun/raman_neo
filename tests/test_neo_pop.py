import numpy as np

from raman_neo.neoPars import NeoPars
from raman_neo.raman_pop import NeoPopulations, fitness


def _pop(base_inputs):
    pars = NeoPars()
    pars.read_inputs(base_inputs)
    pop = NeoPopulations(pars)
    pop.initialize_populations()
    return pars, pop


def test_population_size_and_sorted(base_inputs):
    pars, pop = _pop(base_inputs)
    assert len(pop.population) == pars.fixedPars.nPops
    scores = [s for _, s in pop.population_sorted]
    assert scores == sorted(scores)


def test_fitness_nonnegative_and_finite(base_inputs):
    pars, pop = _pop(base_inputs)
    val = fitness(pars, pop.population[0])
    assert np.isfinite(val)
    assert val >= 0


def test_fitness_return_tot(base_inputs):
    pars, pop = _pop(base_inputs)
    loss, ytot = fitness(pars, pop.population[0], return_tot=True)
    assert ytot.shape[0] == pars.ramanPars.npts
    assert np.isfinite(loss)


def test_bestfit_tracked(base_inputs):
    pars, pop = _pop(base_inputs)
    assert pars.bestFitPars.globBestInd is not None
    assert pars.bestFitPars.globBestVal == pop.population_sorted[0][1]


def test_optimize_e0_improves_or_equal(base_inputs):
    pars, pop = _pop(base_inputs)
    before = pars.bestFitPars.globBestVal
    pop.optimize_e0()
    assert pars.bestFitPars.globBestVal <= before + 1e-9
