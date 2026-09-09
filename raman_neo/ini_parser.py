"""Validate and type-convert a parsed .ini file.

Raman analogue of ``exafs_neo.ini_parser``.
"""

from raman_neo.helper import str_to_bool


def split_band_arr(arr_str: str, num_comps: int) -> list:
    """Parse the ``band_list`` string into a list (or list-of-lists for multi-component).

    ``"1,2,3"`` -> ``["1", "2", "3"]``;
    ``"[1,2][3,4]"`` -> ``[["1", "2"], ["3", "4"]]``.
    """
    assert num_comps > 0
    starter = []
    end = []
    split_str = []
    for k, ch in enumerate(arr_str):
        if ch == "[":
            starter.append(k)
        elif ch == "]":
            end.append(k)

    assert len(starter) == len(end), "Bracket setup not matching."
    if num_comps > 1:
        assert num_comps == len(starter), "Number of compounds not matched."
        assert num_comps == len(end), "Number of compounds not matched."

    if len(starter) == 0 and len(end) == 0:
        split_str = list(arr_str.split(","))
    else:
        for i in range(len(starter)):
            split_str.append(arr_str[starter[i] + 1 : end[i]].split(","))
    return split_str


def optional_var(
    input_dict: dict, name_var: str, alt_var=None, type_var=int, output_var: bool = True
):
    """Detect an optional key and coerce it (or install the default)."""
    if type_var is bool:
        return_var = str_to_bool(input_dict[name_var]) if name_var in input_dict else alt_var
    elif type_var is None:
        return_var = input_dict[name_var] if name_var in input_dict else None
    else:
        return_var = type_var(input_dict[name_var]) if name_var in input_dict else type_var(alt_var)

    input_dict[name_var] = return_var
    if output_var:
        return return_var


def validate_input_file(file_dict: dict) -> dict:
    Inputs_dict = file_dict["Inputs"]
    Populations_dict = file_dict["Populations"]
    Solver_dict = file_dict["Solver"]
    Mutations_dict = file_dict["Mutations"]
    Bands_dict = file_dict["Bands"]
    Spectrum_dict = file_dict["Spectrum"]
    Outputs_dict = file_dict["Outputs"]

    # Inputs
    num_compounds = optional_var(Inputs_dict, "num_compounds", 1, int)
    optional_var(Inputs_dict, "bandrange_file", None, None)

    # Populations (best_sample / lucky_few given as counts -> fractions)
    size_population = int(Populations_dict["population"])
    Populations_dict["best_sample"] = float(Populations_dict["best_sample"]) / size_population
    Populations_dict["lucky_few"] = float(Populations_dict["lucky_few"]) / size_population

    # Solver
    optional_var(Solver_dict, "solver_options", 0, int)

    # Mutations (percent -> fraction)
    Mutations_dict["chance_of_mutation"] = 0.01 * float(Mutations_dict["chance_of_mutation"])
    Mutations_dict["original_chance_of_mutation"] = 0.01 * float(
        Mutations_dict["original_chance_of_mutation"]
    )
    Mutations_dict["chance_of_mutation_e0"] = 0.01 * float(Mutations_dict["chance_of_mutation_e0"])
    optional_var(Mutations_dict, "selection_options", 0, int)
    optional_var(Mutations_dict, "mutated_options", 1, int)
    optional_var(Mutations_dict, "crossover_options", 0, int)

    # Bands
    if num_compounds == 1:
        optional_var(Bands_dict, "individual_band", False, bool)
    Bands_dict["band_list"] = split_band_arr(Bands_dict["band_list"], num_compounds)
    optional_var(Bands_dict, "band_optimize", False, bool)
    optional_var(Bands_dict, "band_optimize_percent", 0.01, float)
    optional_var(Bands_dict, "optimize_only", False, bool)

    # Spectrum
    Spectrum_dict["xmin"] = float(Spectrum_dict["xmin"])
    Spectrum_dict["xmax"] = float(Spectrum_dict["xmax"])
    Spectrum_dict["weight"] = float(Spectrum_dict["weight"])
    Spectrum_dict["deltax"] = float(Spectrum_dict["deltax"])
    optional_var(Spectrum_dict, "baseline_order", 0, int)

    # Outputs
    optional_var(Outputs_dict, "print_graph", False, bool)
    optional_var(Outputs_dict, "steady_state_exit", False, bool)

    return {
        "Inputs": Inputs_dict,
        "Populations": Populations_dict,
        "Solver": Solver_dict,
        "Mutations": Mutations_dict,
        "Bands": Bands_dict,
        "Spectrum": Spectrum_dict,
        "Outputs": Outputs_dict,
    }
