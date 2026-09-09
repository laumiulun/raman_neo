"""Read an .ini input file into a nested dict, then flatten it for the run.

Raman analogue of ``exafs_neo.parser``.
"""

import configparser
from dataclasses import dataclass, field

from raman_neo.helper import Bcolors


def CheckKey(dict_val, key_list):
    for key in key_list:
        if key not in dict_val:
            raise KeyError(str(key) + " is missing")


def print_input_file(file_dict):
    for key, value in file_dict.items():
        print("[" + Bcolors.BOLD + str(key) + Bcolors.ENDC + "]")
        for inner_key, inner_value in value.items():
            print("---" + inner_key + ": " + str(inner_value))


def check_optional_key(og_dict, optional_key_list):
    return [k for k in optional_key_list if k not in og_dict]


@dataclass
class InputParamsParser:
    input_dict: dict = field(default_factory=dict)

    def read_input_file(self, input_file, verbose=False):
        config_parser = configparser.ConfigParser()
        config_parser.read(input_file)
        config = config_parser._sections

        file_min = [
            "Inputs",
            "Populations",
            "Solver",
            "Mutations",
            "Bands",
            "Spectrum",
            "Outputs",
        ]
        CheckKey(config, file_min)

        Inputs_dict = config["Inputs"]
        Populations_dict = config["Populations"]
        Solver_dict = config["Solver"]
        Mutations_dict = config["Mutations"]
        Bands_dict = config["Bands"]
        Spectrum_dict = config["Spectrum"]
        Outputs_dict = config["Outputs"]

        CheckKey(Inputs_dict, ["data_file", "output_file", "band_file"])
        CheckKey(Populations_dict, ["population", "num_gen", "best_sample", "lucky_few"])
        CheckKey(
            Mutations_dict,
            ["chance_of_mutation", "original_chance_of_mutation", "chance_of_mutation_e0"],
        )
        CheckKey(Bands_dict, ["band_list"])
        CheckKey(Spectrum_dict, ["xmin", "xmax", "weight", "deltax"])
        CheckKey(Outputs_dict, ["print_graph"])

        self.input_dict["Inputs"] = Inputs_dict
        self.input_dict["Populations"] = Populations_dict
        self.input_dict["Solver"] = Solver_dict
        self.input_dict["Mutations"] = Mutations_dict
        self.input_dict["Bands"] = Bands_dict
        self.input_dict["Spectrum"] = Spectrum_dict
        self.input_dict["Outputs"] = Outputs_dict

        if verbose:
            print_input_file(self.input_dict)

    def verbose(self):
        print_input_file(self.input_dict)

    def export_input_dict(self):
        """Flatten the nested section dict into the single dict used by NeoPars."""
        d = self.input_dict
        return {
            # Inputs
            "num_compounds": int(d["Inputs"].get("num_compounds", 1)),
            "data_file": d["Inputs"]["data_file"],
            "output_file": d["Inputs"]["output_file"],
            "bandrange_file": d["Inputs"].get("bandrange_file", None),
            "band_file": d["Inputs"]["band_file"],
            # Populations
            "nPops": int(d["Populations"]["population"]),
            "nGen": int(d["Populations"]["num_gen"]),
            "nBestSample": d["Populations"]["best_sample"],
            "nLuckSample": d["Populations"]["lucky_few"],
            # Solver
            "solOpt": int(d["Solver"].get("solver_options", 0)),
            # Mutations / selection / crossover
            "selOpt": int(d["Mutations"].get("selection_options", 0)),
            "mut_options": int(d["Mutations"].get("mutated_options", 1)),
            "mutChance": d["Mutations"]["chance_of_mutation"],
            "mutChanceE0": d["Mutations"]["chance_of_mutation_e0"],
            "croOpt": int(d["Mutations"].get("crossover_options", 0)),
            # Outputs
            "steadyState": d["Outputs"].get("steady_state_exit", False),
            "printGraph": d["Outputs"]["print_graph"],
            # Spectrum
            "xmin": float(d["Spectrum"]["xmin"]),
            "xmax": float(d["Spectrum"]["xmax"]),
            "weight": float(d["Spectrum"]["weight"]),
            "deltax": float(d["Spectrum"]["deltax"]),
            "baseline_order": int(d["Spectrum"].get("baseline_order", 0)),
            # Bands
            "bandrange": d["Bands"]["band_list"],
            "individualOptions": d["Bands"].get("individual_band", False),
            "bandOptimize": d["Bands"].get("band_optimize", False),
            "bandOptimize_percent": d["Bands"].get("band_optimize_percent", 0.01),
        }
