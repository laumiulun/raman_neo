from raman_neo.bandObj import BandObject
from raman_neo.bandrange import Bandrange_limits


def test_bandobject_slots_and_get():
    b = BandObject(Bandrange_limits(0), 1.5)
    vals = b.get()
    assert len(vals) == 4
    # slot ordering: [amp, shift, width, center_shift]
    assert vals[1] == 1.5
    assert b.get_e0() == 1.5
    assert len(b.get_var()) == 3


def test_set_and_mutate():
    b = BandObject(Bandrange_limits(0), 0.0)
    b.set(0.7, 15.0, -4.0)
    assert b.get() == [0.7, 0.0, 15.0, -4.0]
    b.set_e0(2.0)
    assert b.get_e0() == 2.0
    # 100% chance forces a mutation of every trait
    before = b.get_var()
    b.mutate(100.0)
    assert isinstance(b.get_var(), list)
