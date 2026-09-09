import datetime
import logging
import sys
from pathlib import Path

import numpy as np

from raman_neo.helper import time_call
from raman_neo.utils_mapping import (
    neocrossover_int2str,
    neomutator_int2str,
    neoselector_int2str,
    neosolver_int2str,
)


def raise_error(msg="Error"):
    """Raise an exception with a message."""
    raise Exception(msg)


def checkKey(key, dictionary, alt_value=None, logger=None, verbose=False):
    """Return ``dictionary[key]`` if present, else ``alt_value``."""
    if key not in dictionary:
        if verbose:
            warn_str = f"{key} not found! Using default value of {key}: {alt_value}"
            if logger is None:
                print(warn_str)
            else:
                logger.warn(warn_str)
        return alt_value
    else:
        return dictionary[key]


class NeoLogger:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("")
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.log_path = None
        self.logging_level = logging.DEBUG

    def initialize_logging(self, log_path=None, log_format="%(message)s"):
        self.log_path = log_path
        formatter = logging.Formatter(log_format)

        if log_path is not None:
            file_handler = logging.FileHandler(self.log_path, mode="a+", encoding="utf-8")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(self.logging_level)
            self.logger.addHandler(file_handler)

        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.setLevel(self.logging_level)
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)
        self.logger.setLevel(self.logging_level)

    def set_loglevel(self, loglevel):
        self.logging_level = loglevel
        self.logger.setLevel(loglevel)

    def print(self, message: str):
        self.logger.debug(message)

    def warn(self, message: str):
        self.logger.warning(message)

    def __call__(self, message):
        self.logger.debug(message)


def check_if_exists(path_file: str | Path) -> None:
    """Remove ``path_file`` if it exists and ensure its parent directory exists."""
    path_file = Path(path_file)
    if path_file.is_file():
        path_file.unlink()
    path_file.parent.mkdir(parents=True, exist_ok=True)


class STRColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def logger_print_based_on_verbose_lvl(
        logger: NeoLogger, string: str, verbose_lvl: int, des_verbose_lvl: int
    ) -> None:
        if verbose_lvl >= des_verbose_lvl:
            logger.print(string)

    @staticmethod
    def _p(logger, string, verbose_lvl, des=5):
        STRColors.logger_print_based_on_verbose_lvl(logger, string, verbose_lvl, des)

    @staticmethod
    def run_verbose_start(logger, raman_NeoPars, verbose_lvl: int = 5) -> None:
        """Print the input configuration at the start of a run."""
        p = STRColors._p
        B, E = STRColors.BOLD, STRColors.ENDC

        if raman_NeoPars.fixedPars.debug_mode:
            p(logger, f"{B}DEBUG-MODE{E}", verbose_lvl, 5)
        p(logger, "------------Inputs File Stats--------------", verbose_lvl, 5)
        p(logger, f"{B}Data File{E}: {raman_NeoPars.neoFilePars.data_path}", verbose_lvl, 5)
        p(logger, f"{B}Band File{E}: {raman_NeoPars.neoFilePars.front}", verbose_lvl, 5)
        p(logger, f"{B}Output File{E}: {raman_NeoPars.neoFilePars.output_path}", verbose_lvl, 5)
        p(logger, f"{B}Log File{E}: {raman_NeoPars.neoFilePars.log_path}", verbose_lvl, 5)
        p(logger, f"{B}Series{E}: {raman_NeoPars.neoFilePars.multi_data_toggle}", verbose_lvl, 5)
        p(logger, "--------------Populations------------------", verbose_lvl, 5)
        p(logger, f"{B}Population{E}: {raman_NeoPars.fixedPars.nPops}", verbose_lvl, 5)
        p(logger, f"{B}Num Gen{E}: {raman_NeoPars.fixedPars.nGen}", verbose_lvl, 5)
        p(logger, f"{B}Best Individuals{E}: {raman_NeoPars.selPars.nBestSample}", verbose_lvl, 5)
        p(logger, f"{B}Lucky Survivor{E}: {raman_NeoPars.selPars.nLuckSample}", verbose_lvl, 5)
        p(logger, "-----------------Bands---------------------", verbose_lvl, 5)
        p(
            logger,
            f"{B}Individual Band{E}: {raman_NeoPars.ramanBandPars.individual_bands}",
            verbose_lvl,
            5,
        )
        p(logger, f"{B}Num Band{E}: {raman_NeoPars.ramanBandPars.nband}", verbose_lvl, 5)
        p(logger, f"{B}Bands{E}: {raman_NeoPars.ramanBandPars.band_lists}", verbose_lvl, 5)
        p(logger, f"{B}Band Optimize{E}: {raman_NeoPars.fixedPars.bandOptimize}", verbose_lvl, 5)
        p(
            logger,
            f"{B}Band Optimize Percent{E}: {raman_NeoPars.fixedPars.bandOptimizePercent}",
            verbose_lvl,
            5,
        )
        p(logger, "-----------------Solvers-------------------", verbose_lvl, 5)
        p(
            logger,
            f"{B}Solver Options{E}: {neosolver_int2str(raman_NeoPars.solPars.solOpt)}",
            verbose_lvl,
            5,
        )
        p(logger, "----------------Mutations------------------", verbose_lvl, 5)
        p(logger, f"{B}Mutations{E}: {raman_NeoPars.mutPars.mutChance}", verbose_lvl, 5)
        p(logger, f"{B}Shift Mutations{E}: {raman_NeoPars.mutPars.mutChanceE0}", verbose_lvl, 5)
        p(
            logger,
            f"{B}Mutation Options{E}: {neomutator_int2str(raman_NeoPars.mutPars.mutOpt)}",
            verbose_lvl,
            5,
        )
        p(
            logger,
            f"{B}Selection Options{E}: {neoselector_int2str(raman_NeoPars.selPars.selOpt)}",
            verbose_lvl,
            5,
        )
        p(
            logger,
            f"{B}Crossover Options{E}: {neocrossover_int2str(raman_NeoPars.crossPars.croOpt)}",
            verbose_lvl,
            5,
        )
        p(logger, "---------------Spectrum Range--------------", verbose_lvl, 5)
        p(logger, f"{B}Xmin (cm-1){E}: {raman_NeoPars.ramanPars.xmin}", verbose_lvl, 5)
        p(logger, f"{B}Xmax (cm-1){E}: {raman_NeoPars.ramanPars.xmax}", verbose_lvl, 5)
        p(logger, f"{B}Weight{E}: {raman_NeoPars.ramanPars.weight}", verbose_lvl, 5)
        p(logger, f"{B}Delta x{E}: {raman_NeoPars.ramanPars.dx}", verbose_lvl, 5)
        p(logger, f"{B}Baseline Order{E}: {raman_NeoPars.ramanPars.baseline_order}", verbose_lvl, 5)
        p(logger, "-------------------------------------------", verbose_lvl, 5)
        p(logger, f"{B}Steady State{E}: {raman_NeoPars.fixedPars.steadyState}", verbose_lvl, 5)
        p(logger, f"{B}Print Graph{E}: {raman_NeoPars.fixedPars.printGraph}", verbose_lvl, 5)
        p(logger, "-------------------------------------------", verbose_lvl, 5)

    @staticmethod
    def run_verbose_gen(logger, raman_NeoPars, neo_population, verbose_lvl=5):
        """Print per-generation progress."""
        p = STRColors._p
        B, E, BL = STRColors.BOLD, STRColors.ENDC, STRColors.OKBLUE
        st = time_call()
        currGen = raman_NeoPars.runPars.currGen
        nGen = raman_NeoPars.runPars.nGen

        if currGen == nGen // 2 or currGen == nGen:
            p(logger, "---------------------------------------------------------", verbose_lvl, 1)
            p(
                logger,
                "Continue With Shift= " + str(round(raman_NeoPars.bestFitPars.bestE0, 3)),
                verbose_lvl,
                5,
            )

        population_sorted = neo_population.population_sorted
        p(logger, "---------------------------------------------------------", verbose_lvl, 1)
        p(
            logger,
            datetime.datetime.fromtimestamp(st).strftime("%H:%M:%S")
            + f"{B} Gen: {E}{raman_NeoPars.runPars.currGen}",
            verbose_lvl,
            1,
        )
        p(logger, f"Best Fit: {B}{np.round(population_sorted[0][1], 3)}{E}", verbose_lvl, 5)
        if len(population_sorted) > 2:
            p(logger, f"2nd Fit: {B}{np.round(population_sorted[1][1], 3)}{E}", verbose_lvl, 5)
            p(logger, f"3rd Fit: {B}{np.round(population_sorted[2][1], 3)}{E}", verbose_lvl, 5)
        p(logger, f"Last Fit: {B}{np.round(population_sorted[-1][1], 3)}{E}", verbose_lvl, 5)
        p(
            logger,
            f"Difference from last best fit: {raman_NeoPars.bestFitPars.bestDiff:.4f}",
            verbose_lvl,
            5,
        )
        p(
            logger,
            f"Glob Best Ind:\n{np.array_str(np.array(raman_NeoPars.bestFitPars.globBestInd.get()), precision=3)}",
            verbose_lvl,
            5,
        )
        p(
            logger,
            f"Curr Best Ind:\n{np.array_str(np.array(raman_NeoPars.bestFitPars.currBestInd.get()), precision=3)}",
            verbose_lvl,
            5,
        )
        p(
            logger,
            B + "Best fit: " + BL + str(np.round(raman_NeoPars.bestFitPars.currBestVal, 3)) + E,
            verbose_lvl,
            5,
        )

        denom = len(raman_NeoPars.ramanPars.intervalK) - 3 * raman_NeoPars.ramanPars.nband + 1
        denom = denom if denom != 0 else 1
        CurrchiR = np.round(raman_NeoPars.bestFitPars.currBestVal / denom, 3)
        p(logger, B + "Best fit ChiR: " + BL + str(CurrchiR) + E, verbose_lvl, 5)
        p(
            logger,
            B + "History Best: " + BL + str(np.round(raman_NeoPars.bestFitPars.globBestVal, 4)) + E,
            verbose_lvl,
            1,
        )
        GlobchiR = raman_NeoPars.bestFitPars.globBestVal / denom
        p(logger, B + "History Best ChiR: " + BL + str(np.round(GlobchiR, 4)) + E, verbose_lvl, 1)
        p(logger, "DiffCounter: " + str(raman_NeoPars.runPars.diffCounter), verbose_lvl, 5)
        p(logger, f"Mutation Chance: {100 * raman_NeoPars.mutPars.mutChance:.2f}%", verbose_lvl, 5)
        p(logger, "Time: " + str(round(raman_NeoPars.runPars.currGen_tt, 3)) + "s", verbose_lvl, 5)

    @staticmethod
    def run_verbose_end(logger, raman_NeoPars, verbose_lvl=5):
        """Print end-of-run statistics."""
        p = STRColors._p
        B, E = STRColors.BOLD, STRColors.ENDC
        p(logger, "---------------Output Stats---------------", verbose_lvl, 1)
        p(logger, f"{B}Total Time(s){E}: {round(raman_NeoPars.runPars.tt, 4)}", verbose_lvl, 1)
        p(logger, f"{B}File{E}: {raman_NeoPars.neoFilePars.data_path}", verbose_lvl, 1)
        p(logger, f"{B}Bands{E}: {raman_NeoPars.ramanBandPars.band_lists}", verbose_lvl, 1)
        p(
            logger,
            f"{B}Final Fitness Score{E}: {raman_NeoPars.bestFitPars.globBestVal:.2f}",
            verbose_lvl,
            1,
        )
        p(logger, "-------------------------------------------", verbose_lvl, 1)

    @staticmethod
    def run_verbose_band_optimize(logger, new_optimize_band: dict, verbose_lvl=5) -> None:
        p = STRColors._p
        p(logger, "---------------Band Optimizations---------------", verbose_lvl, 5)
        if not new_optimize_band:
            p(
                logger,
                "No band optimizes, consider lowering the cut off percentage.",
                verbose_lvl,
                5,
            )
            return
        p(
            logger,
            f"Filter Percentage: {str(round(new_optimize_band['band_optimize_percent'] * 100, 2)).zfill(4)} %",
            verbose_lvl,
            5,
        )
        p(logger, f"""Original Bands: {new_optimize_band["original_bands"]}""", verbose_lvl, 5)
        p(logger, f"""Filter Bands: {new_optimize_band["optimize_bands"]}""", verbose_lvl, 5)
        p(logger, "Optimized Band:", verbose_lvl, 5)
        for key, vals in new_optimize_band["optimize_band_lists"].items():
            p(
                logger,
                f"\tBand {key}, Contributed {str(round(vals * 100, 2)).zfill(4)} %",
                verbose_lvl,
                5,
            )
        p(logger, "-------------------------------------------", verbose_lvl, 5)


class Utils:
    @staticmethod
    def get_sum_band(band_lists, ncomp):
        """Return the number of bands in each component."""
        sum_band = []
        if ncomp > 1:
            for i in range(ncomp):
                sum_band.append(len(band_lists[i]))
        return sum_band


if __name__ == "__main__":
    pass
