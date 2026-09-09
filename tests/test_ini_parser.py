import os

from raman_neo.ini_parser import split_band_arr, validate_input_file
from raman_neo.parser import InputParamsParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INI = os.path.join(ROOT, "test_inputs", "test_raman.ini")


def test_split_band_arr_single():
    assert split_band_arr("1,2,3", 1) == ["1", "2", "3"]


def test_split_band_arr_multi():
    out = split_band_arr("[1,2][3,4]", 2)
    assert out == [["1", "2"], ["3", "4"]]


def test_full_ini_parse_and_export():
    p = InputParamsParser()
    p.read_input_file(INI)
    p.input_dict = validate_input_file(p.input_dict)
    d = p.export_input_dict()
    assert d["nPops"] == 100
    assert d["nGen"] == 40
    assert d["bandrange"] == ["1", "2", "3", "4", "5", "6"]
    # best_sample given as count 30 -> fraction 0.30
    assert abs(float(d["nBestSample"]) - 0.30) < 1e-9
    # chance_of_mutation given as 20 (%) -> 0.20
    assert abs(float(d["mutChance"]) - 0.20) < 1e-9
    assert d["solOpt"] == 1
    assert d["bandOptimize"] is True
    assert d["xmin"] == 150.0
