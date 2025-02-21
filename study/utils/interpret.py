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
    CORRELATION,
    MEDIAN,
    BEST,
    MEAN,
    WORST,
    TRUE,
    P_VALUE,
)

tex_translation = {
    Spectrum.Tarantula.__name__: "\\TARANTULA{}",
    Spectrum.Ochiai.__name__: "\\OCHIAI{}",
    Spectrum.DStar.__name__: "\\DSTAR{}",
    Spectrum.Naish2.__name__: "\\NAISHT{}",
    Spectrum.GP13.__name__: "\\GPOT{}",
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
    "unified-max": "$\\text{Multi}_\\text{max}$",
    "unified-avg": "$\\text{Multi}_\\text{mean}$",
}


def get_localization_table(results, best_for_each_metric, features):
    table = (
        "\\begin{tabular}{llrrrrrrrrrrrrrrrrrr}\n"
        "    \\toprule\n"
        "    \\multicolumn{1}{c}{\\multirow{4}*{Feature}} & \\multicolumn{1}{c}{\\multirow{4}*{Metric}} & "
        "\\multicolumn{6}{c}{Best-Case Debugging} & \\multicolumn{6}{c}{Average-Case Debugging} & "
        "\\multicolumn{6}{c}{Worst-Case Debugging} \\\\\\cmidrule(lr){3-8}\\cmidrule(lr){9-14}\\cmidrule(lr){15-20}\n"
        "    &"
        + (
            (
                " & \\multicolumn{4}{c}{Top-k} & \\multicolumn{1}{c}{\\multirow{2}*{\\EXAM{}}} & "
                "\\multicolumn{1}{c}{\\multirow{2}*{Effort}}\n"
            )
            * 3
        )
        + "\\\\\\cmidrule{3-6}\\cmidrule{9-11}\\cmidrule{15-17}\n    &"
        + (
            (
                " & \\multicolumn{1}{c}{1} & \\multicolumn{1}{c}{5}"
                " & \\multicolumn{1}{c}{10} & \\multicolumn{1}{c}{200} & &\n"
            )
            * 3
        )
        + "\\\\\\midrule\n"
    )
    for feature in features:
        for metric in METRICS:
            metric = metric.__name__
            if features.index(feature) % 2 == 1:
                table += "\\rowcolor{row}\n"
            if metric == METRICS[len(METRICS) // 2].__name__:
                table += f"    {tex_translation[feature]}"
            else:
                table += "    "
            table += f" & {tex_translation[metric]}"
            if metric == METRICS[0].__name__:
                table += "\\rowstrut{}"
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
                    table += " & "
                    if text_bf:
                        table += "\\textbf{\\color{deepblue}"
                    if localization.startswith("top"):
                        table += (
                            f"{results[LOCALIZATION][feature][metric][scenario][localization][AVG] * 100:.1f}"
                            "\\%"
                        )
                    elif localization == "exam":
                        table += f"{results[LOCALIZATION][feature][metric][scenario][localization][AVG]:.3f}"
                    else:
                        table += (
                            f"{results[LOCALIZATION][feature][metric][scenario][localization][AVG] / 1000:.1f}"
                            f"k"
                        )
                    if text_bf:
                        table += "}"
            table += " \\\\"
            if metric != METRICS[-1].__name__:
                table += "\n"
        table += "[.2em]\n"
    table += "\\bottomrule\n\\end{tabular}\n"
    return table


def get_localization_tex_table(results, best_for_each_metric):
    return (
        get_localization_table(
            results, best_for_each_metric, FEATURES[: len(FEATURES) // 2]
        ),
        get_localization_table(
            results, best_for_each_metric, FEATURES[len(FEATURES) // 2 :]
        ),
        get_localization_table(results, best_for_each_metric, UNIFIED),
    )


def get_correlation_table(results, best_for_each_metric, features):
    table = (
        "\\begin{tabular}{llrrrrrrrrr}\n"
        "    \\toprule\n"
        "    \\multicolumn{1}{c}{\\multirow{2}*{Feature}} & \\multicolumn{1}{c}{\\multirow{2}*{Metric}} & "
        "\\multicolumn{4}{c}{Suspiciousness} & \\multicolumn{5}{c}{Correlation} "
        "\\\\\\cmidrule(lr){3-6}\\cmidrule(lr){7-11}\n"
        "    & & \\multicolumn{1}{c}{Best} & \\multicolumn{1}{c}{Mean} & \\multicolumn{1}{c}{Median} & "
        "\\multicolumn{1}{c}{Worst}"
        "& \\multicolumn{1}{c}{Overall} & \\multicolumn{1}{c}{Best} &  \\multicolumn{1}{c}{Mean} "
        "& \\multicolumn{1}{c}{Median} & \\multicolumn{1}{c}{Worst} \\\\\\midrule\n"
    )
    for feature in features:
        for metric in METRICS:
            if features.index(feature) % 2 == 1:
                table += "\\rowcolor{row}\n"
            metric = metric.__name__
            if metric == METRICS[len(METRICS) // 2].__name__:
                table += f"    {tex_translation[feature]}"
            else:
                table += "    "
            table += f" & {tex_translation[metric]}"
            if metric == METRICS[0].__name__:
                table += "\\rowstrut{}"
            for a in AGGREGATES:
                text_bf = (
                    feature in best_for_each_metric[SUSPICIOUSNESS][metric][a][0][1]
                )
                table += " & "
                if text_bf:
                    table += "\\textbf{\\color{deepblue}"
                table += f"{results[SUSPICIOUSNESS][feature][metric][a][AVG]:.3f}"
                if text_bf:
                    table += "}"
            if metric == METRICS[len(METRICS) // 2].__name__:
                subject_part = " & "
                text_bf = feature in best_for_each_metric[CORRELATION][ALL][0][1]
                if text_bf:
                    subject_part += "\\textbf{\\color{deepblue}"
                underline = results[CORRELATION][feature][ALL][TRUE][1] < P_VALUE
                if underline:
                    subject_part += "\\underline{"
                subject_part += f"{results[CORRELATION][feature][ALL][TRUE][0]:.3f}"
                if underline:
                    subject_part += "}"
                if text_bf:
                    subject_part += "}"
                for a in AGGREGATES:
                    subject_part += " & "
                    text_bf = feature in best_for_each_metric[CORRELATION][a][0][1]
                    if text_bf:
                        subject_part += "\\textbf{\\color{deepblue}"
                    underline = results[CORRELATION][feature][TRUE][a][1] < P_VALUE
                    if underline:
                        subject_part += "\\underline{"
                    subject_part += f"{results[CORRELATION][feature][TRUE][a][0]:.3f}"
                    if underline:
                        subject_part += "}"
                    if text_bf:
                        subject_part += "}"
                table += subject_part
            else:
                table += " & " * 5
            table += "\\\\"
            if metric != METRICS[-1].__name__:
                table += "\n"
        table += "[.2em]\n"
    table += "\\bottomrule\n\\end{tabular}\n"
    return table


def get_correlation_tex_table(results, best_for_each_metric):
    return (
        get_correlation_table(
            results, best_for_each_metric, FEATURES[: len(FEATURES) // 2]
        ),
        get_correlation_table(
            results, best_for_each_metric, FEATURES[len(FEATURES) // 2 :]
        ),
    )


def write_tex(results, best_for_each_metric):
    tex_output = Path("tex")
    if not tex_output.exists():
        tex_output.mkdir()
    correlation_table_1, correlation_table_2 = get_correlation_tex_table(
        results, best_for_each_metric
    )
    with Path(tex_output, "correlation_1.tex").open("w") as f:
        f.write(correlation_table_1)
    with Path(tex_output, "correlation_2.tex").open("w") as f:
        f.write(correlation_table_2)
    (
        localization_table_1,
        localization_table_2,
        unified_table,
    ) = get_localization_tex_table(results, best_for_each_metric)
    with Path(tex_output, "localization_1.tex").open("w") as f:
        f.write(localization_table_1)
    with Path(tex_output, "localization_2.tex").open("w") as f:
        f.write(localization_table_2)
    with Path(tex_output, "unified_localization.tex").open("w") as f:
        f.write(unified_table)


def analyze(results):
    """analyze bests for the various metrics and report highest p-value"""
    best_for_each_metric = {
        SUSPICIOUSNESS: dict(),
        LOCALIZATION: dict(),
        CORRELATION: {
            ALL: [],
            BEST: [],
            MEAN: [],
            MEDIAN: [],
            WORST: [],
        },
    }
    bests = dict()
    for feature in FEATURES:
        value, _ = results[CORRELATION][feature][ALL][TRUE]
        if value in bests:
            bests[value].append(feature)
        else:
            bests[value] = [feature]
    bests = sorted([(score, bests[score]) for score in bests], reverse=True)
    best_for_each_metric[CORRELATION][ALL] = bests
    for a in AGGREGATES:
        bests = dict()
        for feature in FEATURES:
            value, _ = results[CORRELATION][feature][TRUE][a]
            if value in bests:
                bests[value].append(feature)
            else:
                bests[value] = [feature]
        bests = sorted([(score, bests[score]) for score in bests], reverse=True)
        best_for_each_metric[CORRELATION][a] = bests
    for metric in METRICS:
        metric = metric.__name__
        best_for_each_metric[SUSPICIOUSNESS][metric] = dict()
        best_for_each_metric[LOCALIZATION][metric] = dict()
        for a in AGGREGATES:
            bests = dict()
            for feature in FEATURES:
                avg = results[SUSPICIOUSNESS][feature][metric][a][AVG]
                if avg in bests:
                    bests[avg].append(feature)
                else:
                    bests[avg] = [feature]
            bests = sorted([(score, bests[score]) for score in bests], reverse=True)
            best_for_each_metric[SUSPICIOUSNESS][metric][a] = bests
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
