"""Standalone file-object helper (Raman analogue of ``exafs_neo.exafsfileobj``).

Kept for structural parity with EXAFS_Neo; the main pipeline uses
:class:`raman_neo.neoFilePars.NeoFilePars`.
"""

import copy
import os
from typing import AnyStr

from raman_neo.utils import check_if_exists, checkKey


def check_output_files(file: AnyStr):
    """Create the output files with headers, mirroring EXAFS_Neo."""
    check_if_exists(file)
    with open(file, "a+") as file_initial:
        file_initial.write("Gen,TPS,FITNESS\n")

    file_data = os.path.splitext(file)[0] + "_data.csv"
    check_if_exists(file_data)

    file_gen = os.path.splitext(file)[0] + "_generations.csv"
    check_if_exists(file_gen)


class RamanFileobj:
    def __init__(self):
        self.end = None
        self.base = None
        self._front = None
        self.nComp = 0
        self.data_file = None
        self.data_series = False
        self.band_file = None
        self.output_file = None

        self.data_path = None
        self.output_path = None
        self.log_path = None

    def initialize(
        self,
        data_dict: dict,
        i=0,
        firstPass: bool = False,
        band_optimize: bool = False,
        logger=None,
    ):
        self.base = os.getcwd()

        self.nComp = checkKey("nComp", data_dict, 1, logger=logger)
        self.data_file = checkKey("data_file", data_dict, logger=logger)
        self.band_file = checkKey("band_file", data_dict, logger=logger)
        self.output_file = checkKey("output_file", data_dict, logger=logger)

        if self.nComp > 1:
            self._front = []
            for i in range(self.nComp):
                self._front.append(os.path.join(self.base, self.band_file[i]))
        else:
            self._front = os.path.join(self.base, self.band_file)

        if self.data_series:
            self.data_path = os.path.join(self.base, self.data_file[i])
            self.output_path = (
                os.path.splitext(os.path.join(self.base, self.output_file))[0]
                + "_"
                + str(i)
                + ".csv"
            )
            self.log_path = os.path.splitext(copy.deepcopy(self.output_path))[0] + ".log"
        else:
            self.data_path = os.path.join(self.base, self.data_file)
            self.output_path = os.path.join(self.base, self.output_file)
            self.log_path = os.path.splitext(copy.deepcopy(self.output_path))[0] + ".log"

        if band_optimize:
            self.output_path = (
                os.path.splitext(os.path.join(self.base, self.output_file))[0] + "_optimized.csv"
            )

        check_output_files(self.output_path)
        if not firstPass:
            check_if_exists(self.log_path)


if __name__ == "__main__":
    raman_File = RamanFileobj()
    data_dict = {
        "data_file": "data/sample_raman.dat",
        "band_file": "data/sample_bands.txt",
        "output_file": "result/test/raman.csv",
        "nComp": 1,
    }
    raman_File.initialize(data_dict)
    print(raman_File.output_file)
