from raman_neo.bandrange import Bandrange_limits


def test_default_ranges():
    br = Bandrange_limits(0)
    assert br.get_band() == 0
    assert br.getrange_Amp().min() == 0
    assert br.getrange_Width().min() >= 2.0
    lim = br.get_lim()
    assert lim[0] == 0
    assert len(lim) == 4


def test_mod_narrows_range():
    br = Bandrange_limits(0)
    full = len(br.getrange_Width())
    mid = br.glob_rangeWidth[len(br.glob_rangeWidth) // 2]
    br.mod_width(mid)
    assert len(br.getrange_Width()) <= full
    assert len(br.getrange_Width()) <= 2 * br.offset_val + 1
