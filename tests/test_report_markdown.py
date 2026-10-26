"""Human reports retain untrusted text without inventing verification structure."""

from pathlib import Path

import pytest

from integration_evals.artifacts import digest, load_record
from integration_evals.models import CaseId, Run, Suite
from integration_evals.reporting import Tracker, save_run
from tests.test_reporting import absent_assembly

REPOSITORY = Path(__file__).resolve().parents[1]


def render_report(tmp_path: Path, run: Run, suite: Suite | None = None) -> str:
    tracker = load_record(REPOSITORY / "planning/acceptance-checklist.json", Tracker)
    if suite is None:
        suite = load_record(REPOSITORY / "scenarios/suite.json", Suite)
    original = run.model_dump_json(indent=2)
    # These adversarial values are valid input records, not validation bypasses.
    assert Run.model_validate_json(original) == run
    directory = save_run(run, tmp_path, tracker, suite)
    assert (directory / "run.json").read_text(encoding="utf-8") == original
    assert run.model_dump_json(indent=2) == original
    return (directory / "report.md").read_text(encoding="utf-8")


def with_reason(run: Run, reason: str | None) -> Run:
    result = run.results[0].model_copy(update={"reason": reason})
    return run.model_copy(update={"results": (result, *run.results[1:])})


def table_lines(report: str) -> list[str]:
    return [line for line in report.splitlines() if line.lstrip().startswith("|")]


def separator_count(line: str) -> int:
    # Markdown treats a pipe as syntax only after an even number of backslashes.
    count = 0
    backslashes = 0
    for character in line:
        if character == "|" and backslashes % 2 == 0:
            count += 1
        backslashes = backslashes + 1 if character == "\\" else 0
    return count


@pytest.mark.parametrize("separator", ["\n", "\r", "\r\n", "\u2028", "\u2029"])
def test_diagnostic_cannot_create_a_successful_report_row(tmp_path: Path, separator: str) -> None:
    original = absent_assembly()
    injected = "| injected-pass | passed | verified | live | confirmed | - |"
    run = with_reason(original, f"missing assembly{separator}{injected}{separator}still blocked")

    report = render_report(tmp_path, run)

    assert injected not in report
    assert len(table_lines(report)) == len(original.results) + 2
    assert len(report.splitlines()) == len(render_report(tmp_path / "plain", original).splitlines())
    assert (tmp_path / run.id / "coverage.json").read_bytes() == (
        tmp_path / "plain" / original.id / "coverage.json"
    ).read_bytes()


@pytest.mark.parametrize(
    "markup",
    [
        "<img src=x onerror=alert(1)>",
        "![fake evidence](https://example.invalid/image.png)",
        "[verified evidence](https://example.invalid)",
        "**verified**",
        "`verified`",
        "&lt;script&gt;",
        "<https://example.invalid/verified>",
    ],
)
def test_diagnostic_markup_stays_literal_in_human_report(tmp_path: Path, markup: str) -> None:
    report = render_report(tmp_path, with_reason(absent_assembly(), markup))

    assert markup not in report


@pytest.mark.parametrize(
    "diagnostic", ["blocked|forged", r"blocked\|forged|extra", r"blocked\\|forged"]
)
def test_diagnostic_pipes_do_not_create_columns(tmp_path: Path, diagnostic: str) -> None:
    original = absent_assembly()

    report = render_report(tmp_path, with_reason(original, diagnostic))

    rows = table_lines(report)
    assert len(rows) == len(original.results) + 2
    assert all(separator_count(row) == 7 for row in rows)


def test_case_name_cannot_inject_report_structure(tmp_path: Path) -> None:
    original = absent_assembly()
    suite = load_record(REPOSITORY / "scenarios/suite.json", Suite)
    previous_id = suite.cases[0].id
    case_id = CaseId("case|forged\n# VERIFIED\n[receipt](https://example.invalid)")
    altered_suite = suite.model_copy(
        update={"cases": (suite.cases[0].model_copy(update={"id": case_id}), *suite.cases[1:])}
    )
    run = original.model_copy(
        update={
            "results": (
                original.results[0].model_copy(update={"case_id": case_id}),
                *original.results[1:],
            ),
            "selected_case_ids": tuple(
                case_id if selected == previous_id else selected
                for selected in original.selected_case_ids
            ),
            "suite_digest": digest(altered_suite.model_dump_json().encode()),
        }
    )

    report = render_report(tmp_path, run, altered_suite)

    assert "\n# VERIFIED" not in report
    assert "[receipt](https://example.invalid)" not in report
    rows = table_lines(report)
    assert len(rows) == len(original.results) + 2
    assert all(separator_count(row) == 7 for row in rows)


def test_valid_run_identifier_stays_literal_in_heading(tmp_path: Path) -> None:
    run = absent_assembly().model_copy(update={"id": "__untrusted__"})

    report = render_report(tmp_path, run)

    assert "__untrusted__" not in report.splitlines()[0]
    assert report.splitlines()[0].startswith("# Evaluation run ")


def test_report_preserves_readable_unicode_and_exact_json(tmp_path: Path) -> None:
    diagnostic = "Préflight absent — 日本語 🧪"

    report = render_report(tmp_path, with_reason(absent_assembly(), diagnostic))

    assert diagnostic in report


@pytest.mark.parametrize("reason", [None, ""])
def test_missing_reason_preserves_table_fallback(tmp_path: Path, reason: str | None) -> None:
    report = render_report(tmp_path, with_reason(absent_assembly(), reason))

    blocker = table_lines(report)[2].rsplit("|", maxsplit=2)[1].strip()
    assert blocker in {"-", r"\-"}


@pytest.mark.parametrize(
    "limitation",
    [
        "# VERIFIED\n| fake | passed |\n<script>alert(1)</script>",
        "![accepted](https://example.invalid/accepted.png)",
        "<details open><summary>verified</summary></details>",
    ],
)
def test_limitations_cannot_forge_report_headings_or_tables(
    tmp_path: Path, limitation: str
) -> None:
    original = absent_assembly()
    run = original.model_copy(update={"limitations": (limitation,)})

    report = render_report(tmp_path, run)

    assert "\n# VERIFIED" not in report
    assert limitation not in report
    assert "<script>" not in report
    assert "<details" not in report
    assert len(table_lines(report)) == len(original.results) + 2
