import json
import os.path
import shutil
import time
import traceback

from sflkit.runners import Runner

import tests4py.api as t4p
from tests4py import sfl
from tests4py.projects import TestStatus

from utils.constants import EVENT_REPORT_DIR, MAPPINGS_DIR, TMP, EVENTS_DIR


def events(project_name, bug_id, start: int = None, end: int = None):
    report_file = EVENT_REPORT_DIR / f"report_{project_name}.json"
    if os.path.exists(report_file):
        with open(report_file, "r") as f:
            report = json.load(f)
    else:
        report = dict()
    os.makedirs(MAPPINGS_DIR, exist_ok=True)
    for project in t4p.get_projects(project_name, bug_id):
        if start is not None and project.bug_id < start:
            continue
        if end is not None and project.bug_id > end:
            continue
        identifier = project.get_identifier()
        print(identifier)
        if (
            identifier in report
            and "check" in report[identifier]
            and report[identifier]["check"] == "successful"
        ):
            continue
        report[identifier] = dict()

        if (
            project.test_status_buggy != TestStatus.FAILING
            or project.test_status_fixed != TestStatus.PASSING
        ):
            report[identifier]["status"] = "skipped"
            continue
        else:
            report[identifier]["status"] = "running"

        report[identifier]["time"] = dict()

        start = time.time()
        r = t4p.checkout(project)
        report[identifier]["time"]["checkout"] = time.time() - start
        if r.successful:
            report[identifier]["checkout"] = "successful"
        else:
            report[identifier]["checkout"] = "failed"
            report[identifier]["error"] = traceback.format_exception(r.raised)
            continue
        original_checkout = r.location

        mapping = MAPPINGS_DIR / f"{project}.json"
        sfl_path = TMP / f"sfl_{identifier}"
        start = time.time()
        r = sfl.sflkit_instrument(sfl_path, project, mapping=mapping)
        report[identifier]["time"]["instrument"] = time.time() - start
        if r.successful:
            report[identifier]["build"] = "successful"
        else:
            report[identifier]["build"] = "failed"
            report[identifier]["error"] = traceback.format_exception(r.raised)
            continue

        with open(mapping, "r") as f:
            mapping_content = json.load(f)
        with open(mapping, "w") as f:
            json.dump(mapping_content, f, indent=2)

        events_base = EVENTS_DIR / project.project_name / str(project.bug_id)
        shutil.rmtree(events_base, ignore_errors=True)
        if project.project_name == "ansible":
            """
            When ansible is executed it sometimes loads the original version.
            Even though it is never installed and the virtual environment clearly
            contains the instrumented version.
            This prevents an event collection.
            Removing the original version fixes this problem.
            """
            shutil.rmtree(original_checkout, ignore_errors=True)
        start = time.time()
        r = sfl.sflkit_unittest(
            sfl_path, relevant_tests=True, all_tests=False, include_suffix=True
        )
        report[identifier]["time"]["test"] = time.time() - start
        if r.successful:
            report[identifier]["test"] = "successful"
        else:
            report[identifier]["test"] = "failed"
            report[identifier]["error"] = traceback.format_exception(r.raised)
            continue

        checks = True
        bug_events = os.path.join(events_base, "bug")
        for failing_test in project.test_cases:
            safe_test = Runner.safe(failing_test)
            if not os.path.exists(os.path.join(bug_events, "failing", safe_test)):
                report[identifier][f"bug:{failing_test}"] = "not_found"
                checks = False
        if not os.listdir(os.path.join(bug_events, "passing")):
            report[identifier]["bug_passing"] = "empty"
            checks = False

        if checks:
            report[identifier]["check"] = "successful"
        else:
            report[identifier]["check"] = "failed"

    with open(f"report_{project_name}.json", "w") as f:
        json.dump(report, f, indent=2)
