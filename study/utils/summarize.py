import json

from utils.constants import (
    RESULTS_DIR,
    CORRELATIONS,
    METRICS,
    AVG,
    ALL,
    FEATURES,
    UNIFIED,
    CORRELATION,
    LOCALIZATION,
    LOCALIZATIONS,
    SCENARIOS,
    SUBJECTS,
    SUMMARY,
)


def summarize():
    if not RESULTS_DIR.exists():
        return
    results = {
        CORRELATION: {
            type_: {
                metric: {m: {AVG: 0.0, ALL: list()} for m in CORRELATIONS}
                for metric in METRICS
            }
            for type_ in FEATURES + UNIFIED
        },
        LOCALIZATION: {
            type_: {
                metric: {
                    scenario: {m: {AVG: 0.0, ALL: list()} for m in LOCALIZATIONS}
                    for scenario in SCENARIOS
                }
                for metric in METRICS
            }
            for type_ in FEATURES + UNIFIED
        },
    }
    number_of_subjects = 0
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
                    for m in METRICS:
                        for c in CORRELATIONS:
                            results[CORRELATION][t][m][c][ALL].append(
                                subject_data[s][t][CORRELATION][m][c]
                            )
                        for sce in SCENARIOS:
                            for loc in LOCALIZATIONS:
                                results[LOCALIZATION][t][m][sce][loc][ALL].append(
                                    subject_data[s][t][LOCALIZATION][m][sce][loc]
                                )

    for t in FEATURES + UNIFIED:
        for m in METRICS:
            for c in CORRELATIONS:
                results[CORRELATION][t][m][c][AVG] = (
                    sum(results[CORRELATION][t][m][c][ALL]) / number_of_subjects
                )
            for sce in SCENARIOS:
                for loc in LOCALIZATIONS:
                    results[LOCALIZATION][t][m][sce][loc][AVG] = (
                        sum(results[LOCALIZATION][t][m][sce][loc][ALL])
                        / number_of_subjects
                    )
    with open(SUMMARY, "w") as f:
        json.dump(results, f, indent=1)
