from raman_neo.utils_mapping import (
    neocrossover_int2str,
    neocrossover_str2int,
    neomutator_int2str,
    neomutator_str2int,
    neoselector_int2str,
    neoselector_str2int,
    neosolver_int2str,
    neosolver_str2int,
)


def test_crossover_roundtrip():
    for i in range(6):
        assert neocrossover_str2int(neocrossover_int2str(i)) == i


def test_mutator_roundtrip():
    for i in range(6):
        assert neomutator_str2int(neomutator_int2str(i)) == i


def test_selector_roundtrip():
    for i in range(2):
        assert neoselector_str2int(neoselector_int2str(i)) == i


def test_solver_roundtrip():
    for i in range(3):
        assert neosolver_str2int(neosolver_int2str(i)) == i


def test_unknown():
    assert neosolver_int2str(99) == "Unknown Solver"
    assert neomutator_str2int("nope") == -1
