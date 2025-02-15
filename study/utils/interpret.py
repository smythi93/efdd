import json
from pathlib import Path

from matplotlib import pyplot as plt
from sflkit.analysis.analysis_type import AnalysisType
from sflkit.analysis.spectra import Spectrum
from sflkit.evaluation import Scenario

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
    "unified_max": "$\\text{Unified}_\\text{max}$",
    "unified_avg": "$\\text{Unified}_\\text{mean}$",
}

feature_order = [
    AnalysisType.LINE.name,
    AnalysisType.BRANCH.name,
    AnalysisType.FUNCTION.name,
    AnalysisType.FUNCTION_ERROR.name,
    AnalysisType.DEF_USE.name,
    AnalysisType.LOOP.name,
    AnalysisType.CONDITION.name,
    AnalysisType.SCALAR_PAIR.name,
    AnalysisType.VARIABLE.name,
    AnalysisType.RETURN.name,
    AnalysisType.NONE.name,
    AnalysisType.LENGTH.name,
    AnalysisType.EMPTY_STRING.name,
    AnalysisType.ASCII_STRING.name,
    AnalysisType.DIGIT_STRING.name,
    AnalysisType.SPECIAL_STRING.name,
    AnalysisType.EMPTY_BYTES.name,
]

unified_order = [
    "unified_max",
    "unified_avg",
]

scenario_order = [
    Scenario.BEST_CASE.value,
    Scenario.AVG_CASE.value,
    Scenario.WORST_CASE.value,
]

metric_order = [
    Spectrum.Tarantula.__name__,
    Spectrum.Ochiai.__name__,
    Spectrum.DStar.__name__,
    Spectrum.Naish2.__name__,
    Spectrum.GP13.__name__,
]

localization_order = [
    "top-1",
    "top-5",
    "top-10",
    "top-200",
    "exam",
    "wasted-effort",
]

localization_comp = [
    True,
    True,
    True,
    True,
    False,
    False,
]

correlation_order = ["best", "mean", "median", "worst"]


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
    for feature in feature_order + unified_order:
        t = table if feature in feature_order else unified_table
        for metric in metric_order:
            if metric == metric_order[0]:
                t += f"    \\multirow{3}*{{{tex_translation[feature]}}}"
            else:
                t += "    "
            t += f" & {tex_translation[metric]}"
            for scenario in scenario_order:
                for localization in localization_order:
                    if feature in feature_order:
                        text_bf = (
                            feature
                            in best_for_each_metric["localization"][metric][scenario][
                                localization
                            ][0][1]
                        )
                    else:
                        text_bf = (
                            feature
                            in best_for_each_metric["localization"][metric][scenario][
                                f"unified_{localization}"
                            ][0][1]
                            and best_for_each_metric["localization"][metric][scenario][
                                f"unified_{localization}_wins"
                            ]
                        )
                    t += " & "
                    if text_bf:
                        t += "\\textbf{\\color{deepblue}"
                    if localization.startswith("top"):
                        t += (
                            f"{results['localization'][feature][metric][scenario][localization]['avg'] * 100:.1f}"
                            "\\%"
                        )
                    elif localization == "exam":
                        t += f"{results['localization'][feature][metric][scenario][localization]['avg']:.3f}"
                    else:
                        t += (
                            f"{results['localization'][feature][metric][scenario][localization]['avg'] / 1000:.1f}"
                            f"k"
                        )
                    if text_bf:
                        t += "}"
            t += " \\\\\n"
        if feature != unified_order[-1] and feature != feature_order[-1]:
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
    for feature in feature_order:
        for metric in metric_order:
            if metric == metric_order[0]:
                table += f"    \\multirow{3}*{{{tex_translation[feature]}}}"
            else:
                table += "    "
            table += f" & {tex_translation[metric]}"
            for correlation in correlation_order:
                text_bf = (
                    feature
                    in best_for_each_metric["correlation"][metric][correlation][0][1]
                )
                table += " & "
                if text_bf:
                    table += "\\textbf{\\color{deepblue}"
                table += (
                    f"{results['correlation'][feature][metric][correlation]['avg']:.3f}"
                )
                if text_bf:
                    table += "}"
            if metric == metric_order[0]:
                subject_part = ""
                # TODO CORRELATION
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
        "correlation": dict(),
        "localization": dict(),
        "relevance": dict(),
    }
    for metric in metric_order:
        best_for_each_metric["correlation"][metric] = dict()
        best_for_each_metric["localization"][metric] = dict()
        for correlation in correlation_order:
            bests = dict()
            for feature in feature_order:
                avg = results["correlation"][feature][metric][correlation]["avg"]
                if avg in bests:
                    bests[avg].append(feature)
                else:
                    bests[avg] = [feature]
                for feature_2 in feature_order:
                    if feature == feature_2:
                        continue
            bests = sorted([(score, bests[score]) for score in bests], reverse=True)
            best_for_each_metric["correlation"][metric][correlation] = bests
        for scenario in scenario_order:
            best_for_each_metric["localization"][metric][scenario] = dict()
            for localization, comp in zip(localization_order, localization_comp):
                bests = dict()
                bests_unified = dict()
                for feature in feature_order + unified_order:
                    avg = results["localization"][feature][metric][scenario][
                        localization
                    ]["avg"]
                    if feature in ["unified_max", "unified_avg"]:
                        if avg in bests_unified:
                            bests_unified[avg].append(feature)
                        else:
                            bests_unified[avg] = [feature]
                    else:
                        if avg in bests:
                            bests[avg].append(feature)
                        else:
                            bests[avg] = [feature]
                    for feature_2 in unified_order:
                        if feature == feature_2:
                            continue
                bests = sorted([(score, bests[score]) for score in bests], reverse=comp)
                bests_unified = sorted(
                    [(score, bests_unified[score]) for score in bests_unified],
                    reverse=comp,
                )
                best_for_each_metric["localization"][metric][scenario][
                    localization
                ] = bests
                best_for_each_metric["localization"][metric][scenario][
                    f"unified_{localization}"
                ] = bests_unified
                best_for_each_metric["localization"][metric][scenario][
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
    if plot_parts[0] == "correlation":
        _, metric, correlation = plot_parts
        features = list()
        for score, fs in best_for_each_metric["correlation"][metric][correlation]:
            for f in fs:
                features.append(f)
                if len(features) >= n:
                    break
            if len(features) >= n:
                break
        data = [
            results["correlation"][feature][metric][correlation]["all"]
            for feature in features
        ]
        plt.boxplot(data, tick_labels=[tex_translation[f] for f in features])
        if any([any([d > 5 for d in ds]) for ds in data]):
            plt.ylim(0, 5)
    elif plot_parts[0] == "localization":
        _, metric, scenario, localization = plot_parts
        features = list()
        for score, fs in best_for_each_metric["localization"][metric][scenario][
            localization
        ]:
            for f in fs:
                features.append(f)
                if len(features) >= n:
                    break
        data = [
            results["localization"][feature][metric][scenario][localization]["all"]
            for feature in features
        ]
        plt.boxplot(data, tick_labels=[tex_translation[f] for f in features])
    plt.savefig(plots_dir / ("-".join(plot_parts) + ".pdf"))
    plt.clf()


def interpret(tex=False, plots=None, n=5):
    summary = Path("summary.json")
    summary_behavior = Path("summary_behavior.json")
    if not summary.exists() or not summary_behavior.exists():
        return
    with summary.open() as f:
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
