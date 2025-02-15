import argparse
import os
import sys
from pathlib import Path

import sflkit.logger

from utils.analyze import get_analysis
from utils.check import check
from utils.events import get_events
from utils.interpret import interpret
from utils.metrics import get_metrics
from utils.summarize import summarize


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

    check_parser = commands.add_parser(
        "check",
        description="The check command checks if all subjects work.",
        help="execute a check of the subjects",
    )
    check_parser.add_argument(
        "-d", default=None, dest="directory", help="the directory to check"
    )

    commands.add_parser(
        "summarize",
        description="The summarize command summarizes the results of the study.",
        help="execute the summarization of the study results",
    )

    analyze_parser = commands.add_parser(
        "analyze",
        description="The analyze command analyzes the projects by deriving the analysis objects for the projects.",
        help="execute the analysis of the projects",
    )

    events_parser = commands.add_parser(
        "events",
        description="The events command generates the events for the projects.",
        help="execute the generation of the events for the projects",
    )

    metrics_parser = commands.add_parser(
        "metrics",
        description="The metrics command calculates the metrics for the projects.",
        help="execute the calculation of the metrics for the projects",
    )

    for parser in (analyze_parser, events_parser, metrics_parser):
        parser.add_argument(
            "-p", required=True, dest="project_name", help="project name"
        )
        parser.add_argument("-i", default=None, type=int, dest="bug_id", help="bug id")
        parser.add_argument(
            "-s", default=None, type=int, dest="start", help="start bug id (inclusive)"
        )
        parser.add_argument(
            "-e", default=None, type=int, dest="end", help="end bug id (inclusive)"
        )

    return arg_parser.parse_args(args or sys.argv[1:])


def main(*args: str, stdout=sys.stdout, stderr=sys.stderr):
    if stdout is not None:
        sys.stdout = stdout
    if stderr is not None:
        sys.stderr = stderr
    sflkit.logger.LOGGER.disabled = True
    args = parse_args(*args)
    if args.command == "interpret":
        interpret(args.tex, args.plots, args.n)
    elif args.command == "check":
        check(args.directory)
    elif args.command == "summarize":
        summarize()
    elif args.command == "analyze":
        get_analysis(args.project_name, args.bug_id, args.start, args.end)
    elif args.command == "events":
        get_events(args.project_name, args.bug_id, args.start, args.end)
    elif args.command == "metrics":
        get_metrics(args.project_name, args.bug_id, args.start, args.end)
    else:
        raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    assert Path.cwd() == Path(__file__).parent
    if "-O" in sys.argv:
        sys.argv.remove("-O")
        os.execl(sys.executable, sys.executable, "-O", *sys.argv)
    else:
        main()
