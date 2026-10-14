from xml.etree.ElementTree import fromstring

import pytest

from integration_evals.models import (
    CaseId,
    CaseResult,
    Mode,
    Origin,
    Outcome,
    RequirementId,
    Status,
)
from integration_evals.reporting import junit

INVALID_TEXT = (
    "nul\x00diagnostic",
    "\x1b[31mfixture failure\x1b[0m",
    "".join(chr(code) for code in range(32) if code not in {9, 10, 13}),
    "noncharacters\ufffe\uffff",
    "surrogates\ud800\udfff",
)
INVALID_IDS = ("nul", "ansi", "forbidden-c0", "bmp-noncharacters", "surrogates")
VALID_TEXT = (
    'ordinary <value> & "quotes"',
    "tab\tline\nreturn\rspace ",
    "\x7f\x85\x9f\ud7ff\ue000\ufdd0\ufffd\U00010000\U0010ffff",
    "caf\u00e9 \u4e2d\u6587 \U0001f9ea",
    "literal \\u0000 stays literal",
)


def case_result(
    outcome: Outcome, *, name: str = "fixture-case", reason: str | None = None
) -> CaseResult:
    return CaseResult(
        case_id=CaseId(name),
        requirements=(RequirementId("IE-09A.AC1"),),
        outcome=outcome,
        criterion_status=Status.BLOCKED if outcome is Outcome.SKIPPED else Status.IN_PROGRESS,
        mode=Mode.MOCK,
        origin=Origin.SYNTHETIC,
        duration_seconds=0.25,
        reason=reason,
    )


@pytest.mark.parametrize("text", INVALID_TEXT, ids=INVALID_IDS)
@pytest.mark.parametrize("outcome", [Outcome.FAILED, Outcome.ERROR, Outcome.SKIPPED])
def test_junit_renders_invalid_diagnostics_without_changing_records(
    text: str, outcome: Outcome
) -> None:
    result = case_result(outcome, reason=text)
    before = result.model_dump()
    root = fromstring(junit((result,)))  # noqa: S314 - XML generated from synthetic records.
    diagnostic = root[0][0]
    assert (
        diagnostic.tag
        == {
            Outcome.FAILED: "failure",
            Outcome.ERROR: "error",
            Outcome.SKIPPED: "skipped",
        }[outcome]
    )
    assert "\ufffd" in diagnostic.attrib["message"]
    assert result.model_dump() == before


@pytest.mark.parametrize("text", INVALID_TEXT, ids=INVALID_IDS)
@pytest.mark.parametrize("outcome", list(Outcome))
def test_junit_renders_invalid_names_without_hiding_cases(text: str, outcome: Outcome) -> None:
    result = case_result(outcome, name=text, reason="fixture outcome")
    root = fromstring(junit((result,)))  # noqa: S314 - XML generated from synthetic records.
    assert len(root) == 1
    assert "\ufffd" in root[0].attrib["name"]
    assert result.case_id == text
    assert len(root[0]) == (0 if outcome is Outcome.PASSED else 1)


@pytest.mark.parametrize("text", VALID_TEXT)
def test_junit_preserves_legal_unicode_and_attribute_metacharacters(text: str) -> None:
    result = case_result(Outcome.FAILED, name=text, reason=text)
    root = fromstring(junit((result,)))  # noqa: S314 - XML generated from synthetic records.
    assert root[0].attrib["name"] == text
    assert root[0][0].attrib["message"] == text


@pytest.mark.parametrize("reason", [None, ""])
@pytest.mark.parametrize("outcome", [Outcome.FAILED, Outcome.ERROR, Outcome.SKIPPED])
def test_junit_preserves_missing_reason_fallback(reason: str | None, outcome: Outcome) -> None:
    root = fromstring(junit((case_result(outcome, reason=reason),)))  # noqa: S314 - Synthetic XML.
    assert root[0][0].attrib["message"] == outcome.value


def test_junit_retains_mixed_outcomes_and_unknown_costs() -> None:
    results = tuple(
        case_result(outcome, name=f"fixture-{outcome}", reason="fixture\x00outcome")
        for outcome in Outcome
    )
    original_json = tuple(result.model_dump_json() for result in results)
    output = junit(results)
    root = fromstring(output)  # noqa: S314 - XML generated from synthetic records.
    assert root.attrib == {"tests": "4", "failures": "1", "errors": "1", "skipped": "1"}
    assert [len(case) for case in root] == [0, 1, 1, 1]
    assert [case[0].tag for case in root if len(case)] == ["failure", "skipped", "error"]
    assert all(case.attrib["time"] == "0.25" for case in root)
    assert root[1][0].attrib["message"] == "fixture\ufffdoutcome"
    assert tuple(result.model_dump_json() for result in results) == original_json
    assert all(result.cost is None and result.cost_status == "unknown" for result in results)
    assert junit(results) == output


def test_junit_retains_empty_suite_counts() -> None:
    root = fromstring(junit(()))  # noqa: S314 - XML generated from an empty synthetic suite.
    assert root.attrib == {"tests": "0", "failures": "0", "errors": "0", "skipped": "0"}
    assert len(root) == 0
