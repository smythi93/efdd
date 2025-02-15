import json
from pathlib import Path

from matplotlib import pyplot as plt
from sflkit.analysis.analysis_type import AnalysisType
from sflkit.analysis.spectra import Spectrum
from sflkit.evaluation import Scenario

from utils.constants import (
    FEATURES,
    UNIFIED,
    SUSPICIOUSNESS,
    LOCALIZATION,
    AGGREGATES,
    LOCALIZATIONS,
    LOCALIZATION_COMP,
    METRICS,
    SCENARIOS,
    AVG,
    ALL,
    SUMMARY,
)

tex_translation = {
    Spectrum.Tarantula.__name__: "\\TARANTULA{}",
    Spectrum.Ochiai.__name__: "\\OCHIAI{}",
    Spectrum.DStar.__name__: "\\DSTAR{}",
    AnalysisType.LINE.name: "Lines",
    AnalysisType.BRANCH.name: "Branches",
    AnalysisType.FUNCTION.name: "Functions",
    AnalysisType.DEF_USE.name: "Def-Use Pairs",
    AnalysisType.LOOP.name: "Loops",
    AnalysisType.CONDITION.name: "Conditions",
    AnalysisType.SCALAR_PAIR.name: "Scalar Pairs",
    AnalysisType.VARIABLE.name: "Variable Values",
    AnalysisType.RETURN.name: "Return Values",
    AnalysisType.NONE.name: "Null Values",
    AnalysisType.LENGTH.name: "Lengths",
    AnalysisType.EMPTY_STRING.name: "Empty Strings",
    AnalysisType.ASCII_STRING.name: "ASCII Strings",
    AnalysisType.DIGIT_STRING.name: "Digit Strings",
    AnalysisType.SPECIAL_STRING.name: "Special Strings",
    AnalysisType.EMPTY_BYTES.name: "Empty Bytes",
    AnalysisType.FUNCTION_ERROR.name: "Function Errors",
    Scenario.BEST_CASE.value: "Best Case Debugging",
    Scenario.WORST_CASE.value: "Worst Case Debugging",
    Scenario.AVG_CASE.value: "Average Case Debugging",
    "exam": "\\EXAM{}",
    "wasted-effort": "W Effort",
    "unified_max": "$\\text{Multi}_\\text{max}$",
    "unified_avg": "$\\text{Multi}_\\text{mean}$",
}


def get_localization_tex_table(results, best_for_each_metric):
    table = (
        "\\begin{tabular}{llrrrrrrrrrrrrrrr}\n"
        "    \\toprule\n"
        "    \\multicolumn{1}{c}{\\multirow{4}*{Feature}} & \\multicolumn{1}{c}{\\multirow{4}*{Metric}} & "
        "\\multicolumn{5}{c}{Best-Case Debugging} & \\multicolumn{5}{c}{Average-Case Debugging} & "
        "\\multicolumn{5}{c}{Worst-Case Debugging} \\\\\\cmidrule(lr){3-7}\\cmidrule(lr){8-12}\\cmidrule(lr){13-17}\n"
        "    &"
        + (
            (
                " & \\multicolumn{3}{c}{Top-k} & \\multicolumn{1}{c}{\\multirow{2}*{\\EXAM{}}} & "
                "\\multicolumn{1}{c}{\\multirow{2}*{Effort}}\n"
            )
            * 3
        )
        + "\\\\\\cmidrule{3-5}\\cmidrule{8-10}\\cmidrule{13-15}\n    &"
        + (
            (
                " & \\multicolumn{1}{c}{5} & \\multicolumn{1}{c}{10} & \\multicolumn{1}{c}{200} & &\n"
            )
            * 3
        )
        + "\\\\\\midrule\n"
    )
    unified_table = table[:]
    for feature in FEATURES + UNIFIED:
        if feature in FEATURES:
            t = table
            if FEATURES.index(feature) % 2 == 1:
                t += "\\rowcolor{row}\n"
        else:
            t = unified_table
            if UNIFIED.index(feature) % 2 == 1:
                t += "\\rowcolor{row}\n"
        for metric in METRICS:
            if metric == METRICS[0]:
                t += f"    \\multirow{{{len(METRICS)}}}*{{{tex_translation[feature]}}}"
            else:
                t += "    "
            t += f" & {tex_translation[metric]}"
            for scenario in SCENARIOS:
                for localization in LOCALIZATIONS:
                    if feature in FEATURES:
                        text_bf = (
                            feature
                            in best_for_each_metric[LOCALIZATION][metric][scenario][
                                localization
                            ][0][1]
                        )
                    else:
                        text_bf = (
                            feature
                            in best_for_each_metric[LOCALIZATION][metric][scenario][
                                f"unified_{localization}"
                            ][0][1]
                            and best_for_each_metric[LOCALIZATION][metric][scenario][
                                f"unified_{localization}_wins"
                            ]
                        )
                    t += " & "
                    if text_bf:
                        t += "\\textbf{\\color{deepblue}"
                    if localization.startswith("top"):
                        t += (
                            f"{results[LOCALIZATION][feature][metric][scenario][localization][AVG] * 100:.1f}"
                            "\\%"
                        )
                    elif localization == "exam":
                        t += f"{results[LOCALIZATION][feature][metric][scenario][localization][AVG]:.3f}"
                    else:
                        t += (
                            f"{results[LOCALIZATION][feature][metric][scenario][localization][AVG] / 1000:.1f}"
                            f"k"
                        )
                    if text_bf:
                        t += "}"
            t += " \\\\\n"
        if feature != UNIFIED[-1] and feature != FEATURES[-1]:
            t += "\\addlinespace[0.5em]\n"

    table += "\\bottomrule\n\\end{tabular}\n"
    unified_table += "\\bottomrule\n\\end{tabular}\n"
    return table, unified_table


def get_correlation_tex_table(results, best_for_each_metric):
    table = (
        "\\begin{tabular}{llrrrrrrrrrrrr}\n"
        "    \\toprule\n"
        "    \\multicolumn{1}{c}{\\multirow{4}*{Feature}} & \\multicolumn{1}{c}{\\multirow{4}*{Metric}} & "
        "\\multicolumn{4}{c}{\\multirow{2}*{Correlation}} & \\multicolumn{8}{c}{Impact of Repairs} "
        "\\\\\\cmidrule(lr){7-14}\n"
        "    & & & & & & \\multicolumn{4}{c}{Relative} & \\multicolumn{4}{c}{Subjects} "
        "\\\\\\cmidrule(lr){3-6}\\cmidrule(lr){7-10}\\cmidrule(lr){11-14}\n"
        "    & & \\multicolumn{1}{c}{Best} & \\multicolumn{1}{c}{Mean} & \\multicolumn{1}{c}{Median} & "
        "\\multicolumn{1}{c}{Worst}"
        + (
            "& \\multicolumn{1}{c}{Add} & \\multicolumn{1}{c}{Remove} & "
            "\\multicolumn{1}{c}{Change} & \\multicolumn{1}{c}{All}"
        )
        * 2
        + "\\\\\\midrule\n"
    )
    for feature in FEATURES:
        for metric in METRICS:
            if metric == METRICS[0]:
                table += (
                    f"    \\multirow{{{len(METRICS)}}}*{{{tex_translation[feature]}}}"
                )
            else:
                table += "    "
            table += f" & {tex_translation[metric]}"
            for correlation in AGGREGATES:
                text_bf = (
                    feature
                    in best_for_each_metric[SUSPICIOUSNESS][metric][correlation][0][1]
                )
                table += " & "
                if text_bf:
                    table += "\\textbf{\\color{deepblue}"
                table += (
                    f"{results[SUSPICIOUSNESS][feature][metric][correlation][AVG]:.3f}"
                )
                if text_bf:
                    table += "}"
            if metric == METRICS[0]:
                subject_part = ""
                # TODO SUSPICIOUSNESS
                table += subject_part
            else:
                table += " & " * 8
            table += "\\\\\n"
        table += "\\addlinespace[0.5em]"
    table += "\\bottomrule\n\\end{tabular}\n"
    return table


def write_tex(results, best_for_each_metric):
    tex_output = Path("tex")
    if not tex_output.exists():
        tex_output.mkdir()
    correlation_table = get_correlation_tex_table(results, best_for_each_metric)
    with Path(tex_output, "correlation.tex").open("w") as f:
        f.write(correlation_table)
    localization_table, unified_table = get_localization_tex_table(
        results, best_for_each_metric
    )
    with Path(tex_output, "localization.tex").open("w") as f:
        f.write(localization_table)
    with Path(tex_output, "unified_localization.tex").open("w") as f:
        f.write(unified_table)


def analyze(results):
    """analyze bests for the various metrics and report highest p-value"""
    best_for_each_metric = {
        SUSPICIOUSNESS: dict(),
        LOCALIZATION: dict(),
    }
    for metric in METRICS:
        best_for_each_metric[SUSPICIOUSNESS][metric] = dict()
        best_for_each_metric[LOCALIZATION][metric] = dict()
        for correlation in AGGREGATES:
            bests = dict()
            for feature in FEATURES:
                avg = results[SUSPICIOUSNESS][feature][metric][correlation][AVG]
                if avg in bests:
                    bests[avg].append(feature)
                else:
                    bests[avg] = [feature]
            bests = sorted([(score, bests[score]) for score in bests], reverse=True)
            best_for_each_metric[SUSPICIOUSNESS][metric][correlation] = bests
        for scenario in SCENARIOS:
            best_for_each_metric[LOCALIZATION][metric][scenario] = dict()
            for localization, comp in zip(LOCALIZATIONS, LOCALIZATION_COMP):
                bests = dict()
                bests_unified = dict()
                for feature in FEATURES + UNIFIED:
                    avg = results[LOCALIZATION][feature][metric][scenario][
                        localization
                    ][AVG]
                    if feature in UNIFIED:
                        if avg in bests_unified:
                            bests_unified[avg].append(feature)
                        else:
                            bests_unified[avg] = [feature]
                    else:
                        if avg in bests:
                            bests[avg].append(feature)
                        else:
                            bests[avg] = [feature]
                bests = sorted([(score, bests[score]) for score in bests], reverse=comp)
                bests_unified = sorted(
                    [(score, bests_unified[score]) for score in bests_unified],
                    reverse=comp,
                )
                best_for_each_metric[LOCALIZATION][metric][scenario][
                    localization
                ] = bests
                best_for_each_metric[LOCALIZATION][metric][scenario][
                    f"unified_{localization}"
                ] = bests_unified
                best_for_each_metric[LOCALIZATION][metric][scenario][
                    f"unified_{localization}_wins"
                ] = (
                    bests_unified[0][0] >= bests[0][0]
                    if comp
                    else bests_unified[0][0] <= bests[0][0]
                )
    return best_for_each_metric


def write_plot(plot, results, best_for_each_metric, n=5):
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)
    plot_parts = plot.split(",")
    if plot_parts[0] == SUSPICIOUSNESS:
        _, metric, correlation = plot_parts
        features = list()
        for score, fs in best_for_each_metric[SUSPICIOUSNESS][metric][correlation]:
            for f in fs:
                features.append(f)
                if len(features) >= n:
                    break
            if len(features) >= n:
                break
        data = [
            results[SUSPICIOUSNESS][feature][metric][correlation][ALL]
            for feature in features
        ]
        plt.boxplot(data, tick_labels=[tex_translation[f] for f in features])
        if any([any([d > 5 for d in ds]) for ds in data]):
            plt.ylim(0, 5)
    elif plot_parts[0] == LOCALIZATION:
        _, metric, scenario, localization = plot_parts
        features = list()
        for score, fs in best_for_each_metric[LOCALIZATION][metric][scenario][
            localization
        ]:
            for f in fs:
                features.append(f)
                if len(features) >= n:
                    break
        data = [
            results[LOCALIZATION][feature][metric][scenario][localization][ALL]
            for feature in features
        ]
        plt.boxplot(data, tick_labels=[tex_translation[f] for f in features])
    plt.savefig(plots_dir / ("-".join(plot_parts) + ".pdf"))
    plt.clf()


def interpret(tex=False, plots=None, n=5):
    if not SUMMARY.exists():
        return
    with SUMMARY.open() as f:
        results = json.load(f)
    best_for_each_metric = analyze(results)
    if tex:
        write_tex(
            results,
            best_for_each_metric,
        )
    if plots:
        for plot in plots:
            write_plot(plot, results, best_for_each_metric, n)
