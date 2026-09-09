"""Command-line entry point: ``raman_neo -i input.ini``.

Raman analogue of ``exafs_neo.input_arg``.
"""

import argparse
import os
import sys

from raman_neo.ini_parser import validate_input_file
from raman_neo.parser import InputParamsParser
from raman_neo.raman import RamanNeo


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(prog="raman_neo")
    parser.add_argument("-i", "--input", help="Submit input .ini file to raman_neo")
    parser.add_argument("-v", "--verbose", help="output verbosity", action="store_true")
    parser.add_argument("-s", "--show_input", help="show input file", action="store_true")
    parser.add_argument("-t", help="Timing mode", action="store_true")
    parser.add_argument("-d", help="Debug mode", action="store_true")
    return parser, parser.parse_args(argv)


def main(argv=None):
    parser, args = _parse_args(argv)
    if args.input is None:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args.input = args.input.strip(" ")
    file_path = os.path.join(os.getcwd(), args.input)
    input_params = InputParamsParser()
    input_params.read_input_file(file_path, verbose=args.show_input)
    input_params.input_dict = validate_input_file(input_params.input_dict)
    input_pars = input_params.export_input_dict()

    verbose_lvl = 5 if args.verbose else 5
    raman_neo = RamanNeo(verbose_lvl=verbose_lvl)
    raman_neo.raman_neo_pars.fixedPars.debug_mode = args.d
    raman_neo.raman_read(input_parameters=input_pars)
    raman_neo.raman_setup()
    return raman_neo.run()


if __name__ == "__main__":
    main()
