from raman_neo.neoPars import NeoPars


def test_neopars_reads_inputs(base_inputs):
    pars = NeoPars()
    pars.read_inputs(base_inputs)
    assert pars.ramanPars.nband == 4
    assert pars.ramanBandPars.nband == 4
    assert len(pars.ramanBandPars.bandDictionary) == 4
    assert pars.ramanBandPars.exp is not None
    assert pars.ramanBandPars.xgrid.shape[0] == pars.ramanPars.npts
    # experimental spectrum normalised to unit peak inside the window
    idx = pars.ramanPars.intervalK
    assert abs(pars.ramanBandPars.exp[idx].max() - 1.0) < 1e-6


def test_bandrange_pars_count(base_inputs):
    pars = NeoPars()
    pars.read_inputs(base_inputs)
    assert len(pars.ramanRangePars.bandrange_pars) == 4
