from raman_neo.analysis.raman_analysis import RamanAnalysis
from raman_neo.raman import RamanNeo


def test_end_to_end_recovers_bands(base_inputs):
    base_inputs["nGen"] = 40
    base_inputs["nPops"] = 120
    base_inputs["solOpt"] = 1
    r = RamanNeo(verbose_lvl=0)
    r.raman_read(input_parameters=base_inputs)
    r.raman_setup()
    result = r.run()

    an = RamanAnalysis(result)
    table = an.peak_table()
    assert len(table) == 4
    # centres of the four real bands should be recovered within a few cm^-1
    fitted = sorted(row["fitted_center"] for row in table)
    truth = [480.0, 720.0, 1350.0, 1580.0]
    for f, t in zip(fitted, truth, strict=True):
        assert abs(f - t) < 15.0
    assert an.r_factor() < 0.15
    assert isinstance(an.report(), str)
