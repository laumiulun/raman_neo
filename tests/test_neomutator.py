import pytest

from raman_neo.neoMutator import NeoMutator
from raman_neo.neoPars import NeoPars
from raman_neo.raman_pop import NeoPopulations


@pytest.mark.parametrize("mutOpt", [0, 1, 2, 3, 4])
def test_mutators_run(base_inputs, mutOpt):
    base_inputs["mut_options"] = mutOpt
    base_inputs["mutChance"] = 0.5
    pars = NeoPars()
    pars.read_inputs(base_inputs)
    pop = NeoPopulations(pars)
    pop.initialize_populations()

    mut = NeoMutator()
    mut.initialize(pars)
    mut.mutate(pop)
    assert len(pop.population) == pars.fixedPars.nPops
    for ind in pop.population:
        assert len(ind.get()) == 4


def test_invalid_mutator_raises(base_inputs):
    base_inputs["mut_options"] = 99
    pars = NeoPars()
    pars.read_inputs(base_inputs)
    mut = NeoMutator()
    with pytest.raises(ValueError):
        mut.initialize(pars)
