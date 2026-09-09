import time
from typing import AnyStr

import numpy as np

from raman_neo._version import __version__


class Bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def time_call():
    return time.time()


def str_to_bool(s: AnyStr):
    s = str(s).lower()
    if s == "true":
        return True
    elif s == "false":
        return False
    else:
        raise ValueError(f"Cannot convert {s!r} to bool")


def norm(val: float):
    return np.linalg.norm(val)


def banner():
    banner_str = rf"""
            RAMAN_GA ver {__version__}
 _________________________________________
|   ____      _    __  __    _    _   _    |
|  |  _ \    / \  |  \/  |  / \  | \ | |   |
|  | |_) |  / _ \ | |\/| | / _ \ |  \| |   |
|  |  _ <  / ___ \| |  | |/ ___ \| |\  |   |
|  |_| \_\/_/   \_\_|  |_/_/   \_\_| \_|   |
|__________________________________________|

  Genetic-algorithm fitting of Raman spectra
    """

    return banner_str
