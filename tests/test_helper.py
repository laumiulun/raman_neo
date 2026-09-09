import pytest

from raman_neo._version import __version__
from raman_neo.helper import banner, norm, str_to_bool


def test_str_to_bool():
    assert str_to_bool("True") is True
    assert str_to_bool("false") is True or str_to_bool("false") is False
    assert str_to_bool("false") is False
    with pytest.raises(ValueError):
        str_to_bool("maybe")


def test_banner_contains_version():
    assert __version__ in banner()
    assert "RAMAN_GA" in banner()


def test_norm():
    assert norm([3.0, 4.0]) == pytest.approx(5.0)
