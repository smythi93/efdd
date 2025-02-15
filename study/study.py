import argparse
import os
import sys

import sflkit.logger


def parse_args(*args: str):
    arg_parser = argparse.ArgumentParser()
    commands = arg_parser.add_subparsers(
        title="command",
        description="The framework allows for the execution of various commands.",
        help="the command to execute",
        dest="command",
        required=True,
    )

    interpret_parser = commands.add_parser(
        "interpret",
        description="The interpretation command interprets the results of the study.",
        help="execute the interpretation of the study results",
    )
    interpret_parser.add_argument(
        "-t", default=False, action="store_true", dest="tex", help="generate tex tables"
    )
    interpret_parser.add_argument(
        "-n", default=5, type=int, dest="n", help="top n for plots"
    )
    interpret_parser.add_argument(
        "-p",
        default=None,
        dest="plots",
        help="generate plots for the provided metrics",
        nargs="+",
    )

    return arg_parser.parse_args(args or sys.argv[1:])


def main(*args: str, stdout=sys.stdout, stderr=sys.stderr):
    if stdout is not None:
        sys.stdout = stdout
    if stderr is not None:
        sys.stderr = stderr
    sflkit.logger.LOGGER.disabled = True
    args = parse_args(*args)


if __name__ == "__main__":
    if "-O" in sys.argv:
        sys.argv.remove("-O")
        os.execl(sys.executable, sys.executable, "-O", *sys.argv)
    else:
        main()
