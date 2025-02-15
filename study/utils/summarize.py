import json
import warnings
from math import isnan

from scipy.stats import spearmanr

from utils.constants import (
    RESULTS_DIR,
    AGGREGATES,
    METRICS,
    AVG,
    ALL,
    FEATURES,
    UNIFIED,
    SUSPICIOUSNESS,
    LOCALIZATION,
    LOCALIZATIONS,
    SCENARIOS,
    SUBJECTS,
    SUMMARY,
    CORRELATION,
    TRUE,
    FALSE,
    TOTAL,
    BEST,
    MEAN,
    MEDIAN,
)

warnings.filterwarnings("ignore")


def spearman(x, y):
    rho, p = spearmanr(x, y)
    if isnan(rho):
        rho = 0
    if isnan(p):
        p = 0
    return rho, p


def summarize():
    if not RESULTS_DIR.exists():
        return
    results = {
        CORRELATION: {
            type_: {
                TRUE: {ALL: list(), **{a: (0, 0) for a in AGGREGATES}},
                FALSE: {ALL: list(), **{a: (0, 0) for a in AGGREGATES}},
                TOTAL: {ALL: list(), **{a: (0, 0) for a in AGGREGATES}},
                ALL: {
                    TRUE: (0, 0),
                    FALSE: (0, 0),
                    TOTAL: (0, 0),
                },
            }
            for type_ in FEATURES + UNIFIED
        },
        SUSPICIOUSNESS: {
            type_: {
                metric.__name__: {m: {AVG: 0.0, ALL: list()} for m in AGGREGATES}
                for metric in METRICS
            }
            for type_ in FEATURES + UNIFIED
        },
        LOCALIZATION: {
            type_: {
                metric.__name__: {
                    scenario: {m: {AVG: 0.0, ALL: list()} for m in LOCALIZATIONS}
                    for scenario in SCENARIOS
                }
                for metric in METRICS
            }
            for type_ in FEATURES + UNIFIED
        },
    }
    number_of_subjects = 0

    all_corr = {
        type_: {
            TRUE: [],
            FALSE: [],
            TOTAL: [],
        }
        for type_ in FEATURES + UNIFIED
    }
    for subject in SUBJECTS:
        for i in range(100):
            subject_results = RESULTS_DIR / f"{subject}_{i}.json"
            if not subject_results.exists():
                continue
            with subject_results.open() as f:
                subject_data = json.load(f)
            for s in subject_data:
                number_of_subjects += 1
                for t in FEATURES + UNIFIED:
                    all_corr[t][TRUE].extend(subject_data[s][t][CORRELATION][TRUE])
                    all_corr[t][FALSE].extend(subject_data[s][t][CORRELATION][FALSE])
                    all_corr[t][TOTAL].extend(subject_data[s][t][CORRELATION][TOTAL])
                    results[CORRELATION][t][TRUE][ALL].append(
                        spearman(
                            subject_data[s][t][CORRELATION][TRUE],
                            subject_data[s][t][CORRELATION][TOTAL],
                        )
                    )
                    results[CORRELATION][t][FALSE][ALL].append(
                        spearman(
                            subject_data[s][t][CORRELATION][FALSE],
                            subject_data[s][t][CORRELATION][TOTAL],
                        )
                    )
                    results[CORRELATION][t][TOTAL][ALL].append(
                        spearman(
                            subject_data[s][t][CORRELATION][TRUE]
                            + subject_data[s][t][CORRELATION][FALSE],
                            subject_data[s][t][CORRELATION][TOTAL]
                            + subject_data[s][t][CORRELATION][TOTAL],
                        )
                    )
                    for m in METRICS:
                        m = m.__name__
                        for c in AGGREGATES:
                            results[SUSPICIOUSNESS][t][m][c][ALL].append(
                                subject_data[s][t][SUSPICIOUSNESS][m][c]
                            )
                        for sce in SCENARIOS:
                            for loc in LOCALIZATIONS:
                                results[LOCALIZATION][t][m][sce][loc][ALL].append(
                                    subject_data[s][t][LOCALIZATION][m][sce][loc]
                                )

    for t in FEATURES + UNIFIED:
        results[CORRELATION][t][ALL][TRUE] = spearman(
            all_corr[t][TRUE], all_corr[t][TOTAL]
        )
        results[CORRELATION][t][ALL][FALSE] = spearman(
            all_corr[t][FALSE], all_corr[t][TOTAL]
        )
        results[CORRELATION][t][ALL][TOTAL] = spearman(
            all_corr[t][TRUE] + all_corr[t][FALSE],
            all_corr[t][TOTAL] + all_corr[t][TOTAL],
        )
        for a in AGGREGATES:
            if a == BEST:
                func = max
            elif a == MEAN:
                func = lambda x: sum(x) / len(x)
            elif a == MEDIAN:
                func = lambda x: sorted(x)[len(x) // 2]
            else:
                func = min
            f = lambda rhos, ps: (func(rhos), func(ps))
            for r in [TRUE, FALSE, TOTAL]:
                results[CORRELATION][t][r][a] = f(
                    *zip(*results[CORRELATION][t][r][ALL])
                )
        for m in METRICS:
            m = m.__name__
            for c in AGGREGATES:
                results[SUSPICIOUSNESS][t][m][c][AVG] = (
                    sum(results[SUSPICIOUSNESS][t][m][c][ALL]) / number_of_subjects
                )
            for sce in SCENARIOS:
                for loc in LOCALIZATIONS:
                    results[LOCALIZATION][t][m][sce][loc][AVG] = (
                        sum(results[LOCALIZATION][t][m][sce][loc][ALL])
                        / number_of_subjects
                    )
    with open(SUMMARY, "w") as f:
        json.dump(results, f, indent=1)
