import pytest

from raman_neo.neoCrossOver import NeoCrossover
from raman_neo.neoPars import NeoPars
from raman_neo.neoSelector import NeoSelector
from raman_neo.raman_pop import NeoPopulations


@pytest.mark.parametrize("croOpt", [0, 1, 3, 4, 5])
def test_crossover_children_valid(base_inputs, croOpt):
    base_inputs["croOpt"] = croOpt
    pars = NeoPars()
    pars.read_inputs(base_inputs)
    pop = NeoPopulations(pars)
    pop.initialize_populations()

    sel = NeoSelector()
    sel.initialize(pars)
    sel.select(pop)

    cross = NeoCrossover()
    cross.initialize(pars)
    n_before = len(pop.next_population)
    cross.crossover(pop)
    # population is rebuilt to full size
    assert len(pop.population) == pars.fixedPars.nPops
    child = pop.population[-1]
    assert len(child.get()) == 4


def test_crossover_single(base_inputs):
    base_inputs["croOpt"] = 1
    pars = NeoPars()
    pars.read_inputs(base_inputs)
    pop = NeoPopulations(pars)
    pop.initialize_populations()
    cross = NeoCrossover()
    cross.initialize(pars)
    child = cross.crossover_single(pop, pop.population[0], pop.population[1])
    assert child.nbands == 4
