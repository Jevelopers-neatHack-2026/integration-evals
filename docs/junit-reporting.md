# JUnit report rendering

`integration_evals.reporting.junit` renders `CaseResult` records as UTF-8 XML.
The report keeps separate passed, failed, error, and skipped outcomes. A skipped
required boundary is not a passing execution or accepted product criterion.

## Text compatibility

XML 1.0 cannot represent every character accepted in Python strings and JSON.
The serializer replaces forbidden characters in the rendered testcase name and
diagnostic message with U+FFFD. This includes NUL, terminal escape characters,
lone surrogates, and U+FFFE/U+FFFF. Permitted tab, newline, carriage return,
Unicode, and XML metacharacters retain their values after XML parsing.

The character ranges follow [XML 1.0, section 2.2](https://www.w3.org/TR/xml/#charsets).
Only the JUnit derivative is normalized. Input records and their JSON evidence,
case outcomes, counts, durations, unknown costs, and canonical acceptance states
are not changed. Use the original records for exact identifiers and diagnostic
bytes; rendered names are not a substitute for canonical evidence joins. This
formatting rule is not a privacy filter or a replacement for export validation.

## Verification

From a complete checkout with the repository toolchain:

```sh
uv sync --frozen
uv run pytest tests/test_junit_xml.py tests/test_reporting.py
uv run basedpyright
uv run ruff check
uv run ruff format --check
```

The focused XML regressions exercise invalid text in names and diagnostics,
legal Unicode boundaries, attribute escaping, reason fallbacks, mixed outcomes,
empty suites, immutable input records, and deterministic output. The existing
reporting tests additionally exercise the normal runner, blocked assembly,
immutable archive, and CLI boundaries. These commands describe validation to
perform, not a claim that any particular revision has passed them.

Related scope: [IE-09A issue #8](https://github.com/Jevelopers-neatHack-2026/integration-evals/issues/8),
particularly CI-compatible reports and outcome preservation. This repair alone
does not complete that issue, a provider integration, or the release gate.
