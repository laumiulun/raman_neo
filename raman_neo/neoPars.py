"""Parameter containers for a raman_neo run.

Mirrors ``exafs_neo.neoPars`` one-to-one. The EXAFS-specific classes map to
Raman equivalents:

    EXAFSStaticPars  -> RamanStaticPars   (spectrum window & weighting)
    EXAFSPathRange   -> RamanBandRange     (per-band + global-shift ranges)
    EXAFSPath        -> RamanBand          (data loading + band synthesis)
"""

import numpy as np
from attrs import define, field

from raman_neo.bandrange import Bandrange_limits, read_bandrange_file
from raman_neo.bandshape import Band, polynomial_baseline, read_band_file
from raman_neo.helper import time_call
from raman_neo.neoFilePars import NeoFilePars
from raman_neo.utils import checkKey


@define
class NeoBestFit:
    currBestInd: object = None
    currBestVal: float = np.inf
    globBestInd: object = None
    globBestVal: float = np.inf

    bestDiff: float = np.inf
    bestE0: float = 0  # best global shift

    bestChir_magTotal: np.ndarray = field(default=np.zeros(1))
    bestYTotal: np.ndarray = field(default=np.zeros(1))


@define(kw_only=True, slots=True)
class NeoFixedPars:
    nPops: int = 100
    nGen: int = 100
    steadyState: bool = False

    selOpt: int = 0
    croOpt: int = 0

    DE: bool = False

    bandOptimize: bool = False
    bandOptimizePercent: float = 0.01
    bandOptimizeOnly: bool = False
    filter_percentage: float = 0.2

    solver: str = "GA"

    printGraph: bool = True
    debug_mode: bool = False

    def read_inputs(self, input_dicts):
        self.nPops = int(checkKey("nPops", input_dicts, 100))
        self.nGen = int(checkKey("nGen", input_dicts, 100))
        self.steadyState = checkKey("steadyState", input_dicts, False)

        self.selOpt = checkKey("selOpt", input_dicts, 0)
        self.croOpt = checkKey("croOpt", input_dicts, 0)

        self.DE = checkKey("DE", input_dicts, False)

        self.bandOptimize = checkKey("bandOptimize", input_dicts, False)
        self.bandOptimizePercent = checkKey("bandOptimize_percent", input_dicts, 0.01)
        self.bandOptimizeOnly = checkKey("bandOptimizeOnly", input_dicts, False)
        self.filter_percentage = checkKey("filter_percentage", input_dicts, 0.2)

        self.solver = checkKey("solver", input_dicts, "GA")

        self.printGraph = checkKey("printGraph", input_dicts, True)
        self.debug_mode = checkKey("debug_mode", input_dicts, False)


@define
class NeoRunPars:
    currGen: int = 1
    time: bool = False
    tt: float = 0
    secondHalf: bool = False
    diffCounter: int = 0
    cycles: int = 0
    currGen_st: float = 0
    currGen_tt: float = 0
    nGen: int = 100

    def start_gen(self):
        self.currGen_st = time_call()

    def end_gen(self, neo_population):
        self.currGen += 1
        self.currGen_tt = time_call() - self.currGen_st
        self.tt += self.currGen_tt
        if self.currGen == self.nGen // 2:
            neo_population.optimize_e0()
            self.secondHalf = True
        if self.currGen == self.nGen:
            neo_population.optimize_e0()

    def read_inputs(self, input_dicts):
        self.nGen = int(checkKey("nGen", input_dicts, 100))


@define
class NeoMutPars:
    mutOpt: int = 1
    mutChance: float = field(default=0.3)
    mutChanceE0: float = field(default=0.3)
    nmut: int = 0

    def read_inputs(self, input_dicts):
        self.mutOpt = checkKey("mut_options", input_dicts, 1)
        self.mutChance = checkKey("mutChance", input_dicts, 0.3)
        self.mutChanceE0 = checkKey("mutChanceE0", input_dicts, 0.3)

    @mutChance.validator
    def check_mutchance(self, attribute, value):
        if value > 1.0 or value < 0.0:
            raise ValueError("mutChance should be between 0 and 1")


@define
class NeoCrossPars:
    croOpt: int = 0

    def read_inputs(self, input_dicts):
        self.croOpt = checkKey("croOpt", input_dicts, 0)


@define
class NeoSelPars:
    selOpt: int = 0
    nBestSample: float = 0.3
    nLuckSample: float = 0.2

    parents: list = field(factory=list)
    __nPop: int = 0
    nBest: int = 0
    nLuck: int = 0
    nCross: int = 0

    def read_inputs(self, input_dicts):
        self.selOpt = checkKey("selOpt", input_dicts, 0)
        self.nBestSample = float(checkKey("nBestSample", input_dicts, 0.3))
        self.nLuckSample = float(checkKey("nLuckSample", input_dicts, 0.2))
        self.__nPop = int(checkKey("nPops", input_dicts, 100))
        self.nBest = int(self.__nPop * self.nBestSample)
        self.nLuck = int(self.__nPop * self.nLuckSample)
        self.nCross = self.__nPop - self.nBest - self.nLuck


@define
class NeoSol:
    solOpt: int = 0

    def read_inputs(self, input_dicts):
        self.solOpt = checkKey("solOpt", input_dicts, 0)


class NeoPars:
    def __init__(self, verbose_lvl=5):
        self.verbose_lvl = verbose_lvl
        self.fixedPars = NeoFixedPars()
        self.runPars = NeoRunPars()
        self.mutPars = NeoMutPars()
        self.crossPars = NeoCrossPars()
        self.selPars = NeoSelPars()
        self.ramanPars = RamanStaticPars()
        self.bestFitPars = NeoBestFit()
        self.neoFilePars = NeoFilePars()
        self.ramanRangePars = RamanBandRange()
        self.ramanBandPars = RamanBand()
        self.solPars = NeoSol()

    def read_inputs(self, input_dicts):
        self.fixedPars.read_inputs(input_dicts)
        self.runPars.read_inputs(input_dicts)
        self.ramanPars.read_inputs(input_dicts)
        self.neoFilePars.read_inputs(input_dicts)
        self.mutPars.read_inputs(input_dicts)
        self.selPars.read_inputs(input_dicts)
        self.solPars.read_inputs(input_dicts)
        self.crossPars.read_inputs(input_dicts)
        self.neoFilePars.initialize_filepath(cycles=0)

        self.ramanRangePars.read_inputs(input_dicts, self.ramanPars)
        self.ramanBandPars.read_inputs(self.neoFilePars, self.ramanPars)
        self.ramanBandPars.initialize()

    def output(self):
        self.neoFilePars.write_outputs(self.runPars, self.bestFitPars)
        self.neoFilePars.write_data_outputs(self.bestFitPars)

    def end_gen(self, neo_population):
        self.output()
        self.runPars.end_gen(neo_population)


@define
class RamanBandRange:
    """Per-band ranges plus the global-shift scan ranges.

    ``rangeE0`` / ``rangeE0_large`` keep their EXAFS names but hold the global
    wavenumber-shift scan grids (cm^-1).
    """

    bandrange_file: str = ""
    bandrange_pars: list = field(default=None)
    nband: int = 0

    rangeE0: np.ndarray = field(default=np.linspace(-10, 10, 201))
    rangeE0_large: np.ndarray = field(default=np.linspace(-30, 30, 601))

    def read_inputs(self, input_dicts, raman_pars):
        self.bandrange_pars = []
        self.nband = raman_pars.nband
        self.bandrange_file = checkKey("bandrange_file", input_dicts, None)
        if self.bandrange_file is None:
            for i in range(self.nband):
                self.bandrange_pars.append(Bandrange_limits(i))
        else:
            bandrange_file = read_bandrange_file(self.bandrange_file, self.nband)
            for i in range(self.nband):
                self.bandrange_pars.append(Bandrange_limits(i, bandrange_file[i, :]))

    def modify_bandrange(self, best_individual):
        for i in range(self.nband):
            band_bestfit = best_individual.get_band(i)
            self.bandrange_pars[i].mod_amp(band_bestfit[0])
            self.bandrange_pars[i].mod_width(band_bestfit[2])
            self.bandrange_pars[i].mod_cshift(band_bestfit[3])


@define(slots=True)
class RamanStaticPars:
    """Spectrum window and weighting. Raman analogue of ``EXAFSStaticPars``."""

    xmin: float = 100.0
    xmax: float = 1800.0
    dx: float = 1.0
    weight: float = 0.0

    baseline_order: int = 0
    normalize: bool = True

    small: int = 0
    big: int = 0
    mid: int = 0
    intervalK: np.ndarray = field(factory=lambda: np.array([]))
    npts: int = 0

    bandOptimize: bool = False
    bandOptimizePercent: float = 0.01
    bandOptimizeOnly: bool = False

    individual_bands: bool = False

    ncomp: int = 1
    bandrange: list = field(factory=list)
    nband: int = 0

    def calculate_pars(self):
        self.small = int(self.xmin / self.dx)
        self.big = int(self.xmax / self.dx)
        self.mid = int(self.big - self.small + 1)
        self.intervalK = np.linspace(self.small, self.big, self.mid).astype(int)
        self.npts = self.big + 1

    def read_inputs(self, input_dicts):
        self.xmin = float(checkKey("xmin", input_dicts, 100.0))
        self.xmax = float(checkKey("xmax", input_dicts, 1800.0))
        self.dx = float(checkKey("deltax", input_dicts, 1.0))
        self.weight = float(checkKey("weight", input_dicts, 0.0))
        self.baseline_order = int(checkKey("baseline_order", input_dicts, 0))
        self.normalize = checkKey("normalize", input_dicts, True)

        self.bandrange = checkKey("bandrange", input_dicts, None)
        self.ncomp = checkKey("num_compounds", input_dicts, 1)

        if self.ncomp > 1:
            self.individual_bands = True
            self.nband = sum(len(comp) for comp in self.bandrange)
        else:
            self.nband = len(self.bandrange)

        self.calculate_pars()

        self.bandOptimize = checkKey("bandOptimize", input_dicts, False)
        self.bandOptimizePercent = checkKey("bandOptimize_percent", input_dicts, 0.01)
        self.bandOptimizeOnly = checkKey("bandOptimizeOnly", input_dicts, False)


@define
class RamanBand:
    """Loads the spectrum and synthesises bands. Analogue of ``EXAFSPath``.

    The equivalent of larch's ``pathDictionary`` of ``feffpath`` objects is
    ``bandDictionary`` of :class:`raman_neo.bandshape.Band` objects, and the
    equivalent of the experimental ``g.chi`` array is ``self.exp`` evaluated on
    ``self.xgrid``.
    """

    g_x: np.ndarray = None
    g_y: np.ndarray = None
    xgrid: np.ndarray = None
    exp: np.ndarray = None
    baseline: np.ndarray = None

    ncomp: int = 1
    individual_bands: bool = False
    bandname: list = field(factory=list)
    band_lists: list = field(factory=list)
    bandDictionary: dict = field(factory=dict)
    front: object = None
    nband: int = None
    raman_static_pars: RamanStaticPars = None
    raman_file_pars: NeoFilePars = None
    mylarch: object = None  # kept for API parity with EXAFS (unused)

    def read_inputs(self, raman_filepars, raman_static_pars: RamanStaticPars):
        self.raman_file_pars = raman_filepars
        self.raman_static_pars = raman_static_pars
        self.ncomp = raman_filepars.nComp
        self.individual_bands = raman_static_pars.individual_bands
        self.nband = raman_static_pars.nband
        self.front = raman_filepars.front
        self.band_lists = raman_static_pars.bandrange

    @staticmethod
    def _read_spectrum(path):
        """Load a two-column (wavenumber, intensity) ascii spectrum."""
        data = np.genfromtxt(str(path), comments="#")
        data = np.atleast_2d(data)
        if data.shape[1] < 2:
            raise ValueError(
                f"Data file {path} must have at least two columns (wavenumber, intensity)"
            )
        x = data[:, 0].astype(float)
        y = data[:, 1].astype(float)
        order = np.argsort(x)
        return x[order], y[order]

    def __initialize_group(self):
        sp = self.raman_static_pars
        self.g_x, self.g_y = RamanBand._read_spectrum(self.raman_file_pars.data_path)

        # Uniform model grid indexed 0..big with spacing dx.
        self.xgrid = np.arange(sp.npts) * sp.dx

        # Resample experimental intensity onto the model grid.
        exp = np.interp(self.xgrid, self.g_x, self.g_y, left=0.0, right=0.0)

        # Baseline removal (analogue of autobk background subtraction).
        if sp.baseline_order and sp.baseline_order > 0:
            self.baseline = polynomial_baseline(self.xgrid, exp, order=sp.baseline_order)
            exp = exp - self.baseline
        else:
            self.baseline = np.zeros_like(exp)

        # Normalise to unit peak within the fit window so amp is relative.
        if sp.normalize:
            idx = sp.intervalK
            peak = np.max(exp[idx]) if len(idx) and np.max(exp[idx]) > 0 else 1.0
            exp = exp / peak

        self.exp = exp

    def __initialize_bands(self):
        self.bandname = []
        self.bandDictionary = {}

        if self.ncomp > 1:
            for i in range(self.ncomp):
                all_defs = read_band_file(self.front[i])
                for band_id in self.band_lists[i]:
                    d = all_defs[int(band_id) - 1]
                    name = f"Comp{i}Band{band_id}"
                    self.bandname.append(name)
                    self.bandDictionary[name] = Band(
                        name, d["center"], d["shape"], d["eta"], d["base_width"]
                    )
        else:
            all_defs = read_band_file(self.front)
            for band_id in self.band_lists[: self.nband]:
                d = all_defs[int(band_id) - 1]
                name = f"Band{band_id}"
                self.bandname.append(name)
                self.bandDictionary[name] = Band(
                    name, d["center"], d["shape"], d["eta"], d["base_width"]
                )

    def band_optimize(self, best_individual, raman_static_pars, band_optimize_percent):
        """Rank bands by integrated area and keep those above a threshold."""
        arr = np.asarray(best_individual.get())
        contrib = []
        total = 0.0
        for i, band in enumerate(self.bandDictionary.values()):
            band.amp = arr[i, 0]
            band.shift = arr[i, 1]
            band.width = arr[i, 2]
            band.center_shift = arr[i, 3]
            area = band.area(self.xgrid)
            total += area
            contrib.append(area)
        total = total if total != 0 else 1.0
        contrib_p = [c / total for c in contrib]
        new_band_ind = np.argwhere(np.array(contrib_p) >= band_optimize_percent).flatten()

        new_band_dict = {
            "band_optimize_percent": band_optimize_percent,
            "original_bands": self.band_lists,
        }
        optimized_band = {}
        new_band = [self.band_lists[i] for i in new_band_ind]
        for i, band in enumerate(self.band_lists):
            if i in new_band_ind:
                optimized_band[str(band)] = float(contrib_p[i])
        new_band_dict["optimize_bands"] = new_band
        new_band_dict["optimize_band_lists"] = optimized_band
        return new_band_dict

    def initialize(self):
        self.__initialize_group()
        self.__initialize_bands()


if __name__ == "__main__":
    inputs_pars = {
        "data_file": "raman_neo/data/sample_raman.dat",
        "output_file": "sample_out.csv",
        "band_file": "raman_neo/data/sample_bands.txt",
        "xmin": 100,
        "xmax": 1800,
        "deltax": 1.0,
        "weight": 0.0,
        "bandrange": [1, 2, 3, 4],
    }
    raman_NeoPars = NeoPars()
    raman_NeoPars.read_inputs(inputs_pars)
    print(raman_NeoPars.ramanRangePars)
    print("nband:", raman_NeoPars.ramanBandPars.nband)
