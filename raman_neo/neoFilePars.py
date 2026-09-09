from pathlib import Path

from attrs import define, field

from raman_neo.utils import check_if_exists, checkKey


@define
class NeoFilePars:
    """File-path bookkeeping. Raman analogue of ``exafs_neo.neoFilePars``.

    ``band_file`` (the band-definition file) replaces the EXAFS ``feff_file``.
    """

    base: str = Path.cwd()
    data_file: str = ""
    output_file: Path = ""
    output_datafile: Path = ""
    band_file: list = field(factory=list)
    log_file: str = "raman_neo.log"

    firstPass: bool = False
    multi_data_toggle: bool = False
    multi_data: list = field(factory=list)
    nComp: int = 1

    front: list = field(factory=list)

    data_path: Path = None
    output_path: Path = None
    log_path: Path = None

    bandOptimize: bool = False

    def initialize_filepath(self, cycles: float = 0) -> None:
        if self.nComp > 1:
            for i in range(self.nComp):
                self.front.append(self.base / self.band_file[i])
        else:
            self.front = self.base / self.band_file

        if self.multi_data_toggle:
            self.data_path = self.base / self.multi_data[cycles]
            self.output_path = Path(
                str((self.base / self.output_file).with_suffix("")) + f"_{cycles}.csv"
            )
            self.log_path = Path(str(self.output_path.with_suffix("")) + ".log")
        else:
            self.data_path = self.base / self.data_file
            self.output_path = self.base / self.output_file
            self.log_path = Path(str(self.output_path.with_suffix("")) + ".log")

        if self.bandOptimize:
            self.output_path = Path(
                str((self.base / self.output_file).with_suffix("")) + "_optimizes.csv"
            )

        self.initialize_outputs()

    def read_inputs(self, input_dicts: dict) -> None:
        self.nComp = checkKey("num_compounds", input_dicts, 1)
        if self.nComp > 1:
            self.band_file = list(input_dicts["band_file"].split(","))
        else:
            self.band_file = input_dicts["band_file"]

        self.data_file = checkKey("data_file", input_dicts, "")
        self.output_file = checkKey("output_file", input_dicts, "raman_neo_out.csv")
        self.log_file = checkKey("log_file", input_dicts, "raman_neo.log")
        self.bandOptimize = checkKey("bandOptimize", input_dicts, False)

    def initialize_outputs(self) -> None:
        base_file = self.output_path.stem
        self.output_datafile = self.output_path.with_name(f"{base_file}_data.csv")

        # Ensure output/log directories exist and start the run files clean
        # (mirrors ``check_output_files`` in the EXAFS file object).
        check_if_exists(self.output_path)
        check_if_exists(self.output_datafile)
        check_if_exists(self.log_path)
        with open(self.output_path, "a+") as f:
            f.write("Gen,TotalTime,Fitness\n")

    def write_outputs(self, neoRunPars, bestFitPars) -> None:
        with open(self.output_path, "a") as f1:
            data_line = f"{neoRunPars.currGen},{neoRunPars.tt},{bestFitPars.globBestVal}\n"
            f1.writelines(data_line)

    def write_data_outputs(self, bestFitPars) -> None:
        if bestFitPars.globBestInd is None:
            return
        globBestFit = bestFitPars.globBestInd.get()
        with open(self.output_datafile, "a") as f2:
            for band in globBestFit:
                line = f"{band[0]},{band[1]},{band[2]},{band[3]}\n"
                f2.writelines(line)
            f2.write("#################################\n")


if __name__ == "__main__":
    inputs_pars = {
        "data_file": "data/sample_raman.dat",
        "output_file": "tests/output.csv",
        "band_file": "data/sample_bands.txt",
    }
    raman_NeoPars = NeoFilePars()
    raman_NeoPars.read_inputs(inputs_pars)
    raman_NeoPars.initialize_filepath()
    print(raman_NeoPars)
