"""Top-level orchestration for a raman_neo run.

Raman analogue of ``exafs_neo.exafs.ExafsNeo``.
"""

import os
from pathlib import Path

from raman_neo.helper import banner
from raman_neo.ini_parser import validate_input_file
from raman_neo.neoCrossOver import NeoCrossover
from raman_neo.neoMutator import NeoMutator
from raman_neo.neoPars import NeoPars
from raman_neo.neoResult import NeoResult
from raman_neo.neoSelector import NeoSelector
from raman_neo.neoSolver import NeoSolver
from raman_neo.parser import InputParamsParser
from raman_neo.raman_pop import NeoPopulations
from raman_neo.utils import NeoLogger, STRColors


class RamanNeo:
    def __init__(self, verbose_lvl: int = 5) -> None:
        print(banner())
        self.logger = NeoLogger()
        self.raman_neo_pars = NeoPars()
        self.mutator = NeoMutator(logger=self.logger)
        self.selector = NeoSelector(logger=self.logger)
        self.crossOver = NeoCrossover(logger=self.logger)
        self.solver = NeoSolver(logger=self.logger)
        self.neo_population = None
        self.verbose_lvl = verbose_lvl
        self.result = NeoResult(logger=self.logger)
        self.input_parameters = None

    def raman_read(self, filepath: str | Path = None, input_parameters: dict = None) -> None:
        """Read an input .ini file (or a params dict) into the run parameters."""
        if filepath is not None:
            file_path = os.path.join(os.getcwd(), filepath)
            input_params = InputParamsParser()
            input_params.read_input_file(file_path, verbose=False)
            input_params.input_dict = validate_input_file(input_params.input_dict)
            self.input_parameters = input_params.export_input_dict()

        if input_parameters is not None:
            self.input_parameters = input_parameters

        if self.input_parameters is None:
            raise ValueError("No input parameters are given")

    def raman_setup(self) -> None:
        """Build the population and initialise all GA operators."""
        self.raman_neo_pars.read_inputs(self.input_parameters)
        self.logger.initialize_logging(self.raman_neo_pars.neoFilePars.log_path)
        self.neo_population = NeoPopulations(self.raman_neo_pars)
        self.neo_population.initialize_populations()
        self.result.initialize(self.raman_neo_pars)
        self.selector.initialize(self.raman_neo_pars)
        self.crossOver.initialize(self.raman_neo_pars)
        self.mutator.initialize(self.raman_neo_pars)
        self.solver.initialize(self.raman_neo_pars)

    def run(self) -> NeoResult:
        """Run the genetic algorithm to convergence."""
        STRColors.run_verbose_start(self.logger, self.raman_neo_pars, verbose_lvl=self.verbose_lvl)

        for _ in range(self.raman_neo_pars.fixedPars.nGen):
            self.raman_neo_pars.runPars.start_gen()

            self.solver.solve(
                self.neo_population,
                self.selector,
                self.crossOver,
                self.mutator,
                self.raman_neo_pars,
            )

            STRColors.run_verbose_gen(
                self.logger, self.raman_neo_pars, self.neo_population, verbose_lvl=self.verbose_lvl
            )
            self.result.collect(self.neo_population, self.raman_neo_pars)
            self.raman_neo_pars.end_gen(self.neo_population)

        if self.raman_neo_pars.ramanPars.bandOptimize:
            optimize_band = self.raman_neo_pars.ramanBandPars.band_optimize(
                self.raman_neo_pars.bestFitPars.globBestInd,
                self.raman_neo_pars.ramanPars,
                self.raman_neo_pars.fixedPars.bandOptimizePercent,
            )
            STRColors.run_verbose_band_optimize(
                self.logger, optimize_band, verbose_lvl=self.verbose_lvl
            )

        STRColors.run_verbose_end(self.logger, self.raman_neo_pars, verbose_lvl=self.verbose_lvl)
        return self.result


if __name__ == "__main__":
    import os as _os

    here = _os.path.dirname(__file__)
    input_dict = {
        "data_file": _os.path.join(here, "data", "sample_raman.dat"),
        "output_file": "sample_out.csv",
        "band_file": _os.path.join(here, "data", "sample_bands.txt"),
        "nGen": 20,
        "nPops": 100,
        "xmin": 100,
        "xmax": 1800,
        "deltax": 1.0,
        "weight": 0.0,
        "printGraph": False,
        "nBestSample": 0.3,
        "nLuckSample": 0.2,
        "bandrange": [1, 2, 3, 4],
        "solOpt": 1,
        "mut_options": 1,
        "croOpt": 0,
    }
    raman_temp = RamanNeo(verbose_lvl=1)
    raman_temp.raman_read(input_parameters=input_dict)
    raman_temp.raman_setup()
    result = raman_temp.run()
    print(result)
