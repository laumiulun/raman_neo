from raman_neo.neoPars import NeoPars
from raman_neo.raman_pop import NeoPopulations


def _pop(base_inputs):
    pars = NeoPars()
    pars.read_inputs(base_inputs)
    pop = NeoPopulations(pars)
    pop.initialize_populations()
    return pars, pop


def test_individual_shape(base_inputs):
    _, pop = _pop(base_inputs)
    ind = pop.population[0]
    assert ind.nbands == 4
    assert len(ind.get()) == 4
    assert all(len(b) == 4 for b in ind.get())
    assert len(ind) == 3 * 4 + 1


def test_shared_shift(base_inputs):
    _, pop = _pop(base_inputs)
    ind = pop.population[0]
    ind.set_e0(7.0)
    assert ind.get_e0() == 7.0
    assert all(b[1] == 7.0 for b in ind.get())


def test_set_band(base_inputs):
    _, pop = _pop(base_inputs)
    ind = pop.population[0]
    ind.set_band(0, 0.5, 20.0, -3.0)
    assert ind.get_band(0)[0] == 0.5
    assert ind.get_band(0)[2] == 20.0
    assert ind.get_band(0)[3] == -3.0
