# Evaluator command reference

This reference describes the implemented `integration-evals` command surface, not a
product API or a release approval. The entry point is declared in
[`pyproject.toml`](../pyproject.toml); handlers are registered in
[`cli.py`](../src/integration_evals/cli.py), with retained-history operations in
[`history_cli.py`](../src/integration_evals/history_cli.py), evidence packaging in
[`evidence_cli.py`](../src/integration_evals/evidence_cli.py), and evaluator schema
export in [`schema_exports.py`](../src/integration_evals/schema_exports.py).

Use Python 3.13 or later and the committed lockfile. Development is pinned by
[`.python-version`](../.python-version). From a clean repository checkout:

```sh
uv sync --frozen
uv run integration-evals --help
uv run integration-evals validate --help
```

Every command supports `--help`. The generated top-level options also include
`--show-completion` and `--install-completion`; installing completion changes the
local shell configuration and is not necessary to run evaluations. With no
command, the CLI displays help. The examples below use explicit placeholder paths,
not approved manifests, credentials, grants, or existing evidence.

## Exit status is scoped to the command

| Result | Interpretation |
| --- | --- |
| `0` | The requested command completed without a handled failure. It does not by itself approve a producer, accept a master criterion, ratify benchmark policy, or establish release readiness. Some commands print blockers and still exit zero. |
| `1` | A handled artifact, validation, I/O, or runtime rejection, or a failed canonical contract execution. Inspect the command's diagnostics and retained report. This is not a successful evaluation. |
| `2` | Depending on the command, retained evaluation or evidence blockers, intentionally non-promoting replay, or a CLI argument/usage error. Distinguish a written report from parser diagnostics; a usage error may produce no report. |

The `safe_command` wrapper reports an `InvalidArtifactError` code or the class of
handled validation/I/O/subprocess errors rather than echoing their full private
inputs. That behavior is not permission to publish arbitrary logs or artifacts;
manual evidence, metadata, and privacy review remain required.

## Validation and run inspection

| Command | Inputs and options | Behavior and limits |
| --- | --- | --- |
| `validate` | Optional `--repository PATH`; defaults to the current directory. | Reads the master and local requirement inventories, fixture catalog, scenario suite/selection, benchmark corpus and policy. Validates fixture provenance and selection consistency. Prints benchmark-promotion blockers without making those blockers a nonzero exit by themselves. Does not execute product components or write acceptance state. |
| `inspect RECEIPT` | Required run-receipt path; optional `--suite PATH`, default `scenarios/suite.json`. | Loads the evaluator Run, checks it against the trusted suite and validates its evidence relative to the receipt's parent directory. Prints the validated receipt identity. It neither runs components nor authenticates a producer solely from the receipt's hashes. |

```sh
uv run integration-evals validate
uv run integration-evals inspect reports/runs/REPLACE_WITH_RUN_ID/run.json
```

Use the actual run directory returned by execution. For a non-default suite,
provide its exact trusted file rather than editing the retained receipt to fit.

## Execute selected boundaries

`run` uses the current directory as the evaluator repository. It calls fixture
validation before executing selected boundaries and writes retained run/history
reports plus a release-audit export. See the
[execution protocol](execution-protocol.md) for assembly, containment, fingerprints,
owner responses and the complete evidence contract.

| Option | Default or requirement |
| --- | --- |
| `--workspace PATH` | Defaults to the evaluator repository's parent directory. Component checkouts still need the exact required revisions. |
| `--manifest PATH` | Optional app-owned assembly path; omission does not manufacture an accepted product assembly. |
| `--mode MODE` | `mock-only` by default. Other implemented values are `recorded`, `sandbox`, and `live`. Transport mode and evidence origin are distinct. |
| `--output TEXT` | `reports/runs`; the command prints the resulting retained-report directory. |
| `--authorize-paid` / `--no-authorize-paid` | False by default. Confirmation is subordinate to existing owner authority and budget; this flag grants neither. |
| `--evaluation-diagnostics INTEGER` | Default `0`; allowed range `0` through `2`. Requests eligible comparison replays, not independent producer reruns. See the prerequisites below; a positive value can reject an otherwise retained run. |

```sh
uv run integration-evals run --mode mock-only --output reports/runs
uv run integration-evals run --manifest /approved/release.json --workspace /approved/workspace
```

After execution, report writing and any requested diagnostics complete, `run`
exits `2` if any selected result is not `passed`. An empty suite or explicitly empty
manifest selection is rejected with exit `1` before a run report is produced; omitting
the manifest selection selects all suite cases. See the nonempty constraints in
[`models.py`](../src/integration_evals/models.py) and selection in
[`runner.py`](../src/integration_evals/runner.py).

`--evaluation-diagnostics` is not a general repeat count. Every selected result must
be an eligible `mock-only` or `recorded` functional `oracle-mismatch` failure with
`recorded-comparison` evidence, successful original cleanup and a matching captured
comparison. Safety/authorization, ambiguous, quarantined, provider-operation and
other forbidden cases are excluded. The runtime, capture identities and hashes must
still match, and the diagnostic limit must not be exceeded. The complete checks are
in [`diagnostics.py`](../src/integration_evals/diagnostics.py) and
[`replay.py`](../src/integration_evals/replay.py).

A passed, skipped, errored, uncaptured or otherwise ineligible selection is rejected
rather than silently skipped. `run` saves the original history and release audit
before trying diagnostics. A diagnostic rejection exits `1` before printing the
final report directory and can leave only those original reports; it does not roll
them back or establish a completed replay.

A written report, a replay, or a zero exit is not a blanket acceptance statement:
inspect release-audit and evidence blockers and retain owner boundaries.
Sandbox/live execution requires the current authority, eligibility, credentials,
caps, permitted operations and cleanup described in the protocol. No credentials
are inferred from a fixture, hash, manifest, or successful local check.

## Canonical package checks

| Command | Required options | Optional scope and output |
| --- | --- | --- |
| `contract-runtime` | `--node PATH --output PATH` | Hashes a bounded runtime file and records its resolved path and SHA-256. Creates the output exclusively; the parent directory must already exist and the file must be new. This is binary identity staging, not a runtime or spending grant. |
| `contracts` | `--pin PATH --producer PATH --runtime PATH --output PATH` | `--candidate-scope` defaults to false. Loads the exact ContractPin and ContractRuntime, including an installed-package record when present; executes the contract check and prints its receipt directory. Execution other than `passed` exits `1`. Missing canonical contracts exit `2` when candidate scope is not selected. |

```sh
uv run integration-evals contract-runtime --help
uv run integration-evals contracts --help
```

Review the runtime record before sharing it because it contains a resolved local
path. Candidate scope limits the claim; it does not adopt a candidate or erase
missing full-scope obligations. The
[canonical development guide](canonical-v0101-development.md) and
[execution protocol](execution-protocol.md#canonical-candidate-conformance) describe
separately pinned source and installed consumers. Do not transfer their receipts
to changed package bytes or runtime binaries.

## Retained history and evidence

| Command | Inputs and options | Writes and exit behavior |
| --- | --- | --- |
| `replay-evaluation ARCHIVE` | Retained archive; optional `--suite PATH`, default `scenarios/suite.json`. | Loads hash-bound captured comparisons, reruns evaluator comparisons, and writes a successor history and release audit beside the retained archive. A completed replay deliberately exits `2`; handled invalid/missing input, drift, ineligible captures or I/O failures exit `1` instead. Exit `1` is not a completed replay and may leave partial output if a later write fails. Replay does not become fresh producer execution or source-authenticity proof. |
| `history-report ARCHIVE` | Retained archive; optional `--suite PATH`, default `scenarios/suite.json`. | Reads complete retained history and prints JSON summaries. Executes no command taken from archive metadata. Exits `2` when any summary remains release-blocked. |
| `evidence-index ARCHIVE` | Required `--output PATH`; optional `--suite PATH` and `--reviews PATH`. | Joins history to the current repository's master/local requirements and optional review sidecars. Writes a new, exclusive output file and prints its SHA-256. Exits `2` for in-scope blockers; missing reviews are not silently treated as approval. |

The `--output` parent for `evidence-index` must exist. Use a new filename for each
review rather than overwriting an earlier index. The
[evidence-index guide](evidence-index.md) defines local attestations, original-byte
bindings, image qualification and external authenticity limits. The
[safe-rerun guide](safe-reruns.md) and [retained-runner guide](safe-reruns-runner.md)
separate diagnostic attempts, genuine reruns and publication decisions.

## Benchmark analysis

| Command | Inputs and options | Output and interpretation |
| --- | --- | --- |
| `benchmark CORPUS SAMPLES` | Optional `--policy PATH` and `--receipt-root PATH`. | Reads corpus and raw sample JSON; prints per-question/stratum metrics for `rules`, `generative` and `jev`, a paired family accuracy-difference interval, and corpus blockers. With policy, also prints its promotion assessment. The command can finish at zero while promotion remains blocked. It does not execute models or generate missing samples. |
| `benchmark-history CORPUS SAMPLES REPEATS OUTPUT` | All four positional arguments required; `REPEATS` is an integer at least `1`. | Saves independently declared statistical repeats and computed metrics to a new exclusive output file. Its parent must exist. Declaring a repeat count does not create genuine model execution or authorize benchmark promotion. |

The corpus, raw samples, policy and receipt roots must describe the same reviewed
measurement context. Synthetic smoke data is not a held-out promotion corpus.
The existing benchmark deferral and acceptance requirements remain unchanged.

## Maintenance commands that regenerate files

Do not put these commands in a normal verification loop against retained evidence.
Use an isolated working copy, inspect the diff, and preserve historical inputs.

| Command | Required positional arguments | Mutation boundary |
| --- | --- | --- |
| `initialize REPOSITORY BACKLOG` | Prepared checkout and externally captured backlog file. | Requires the repository and `planning/` directory plus all expected reviewed `fixtures/data/*.txt` inputs. Rebuilds the catalog and hashes from those existing bytes; does not create the fixture text. Replaces `planning/requirements.json`, `fixtures/catalog.json` and `benchmarks/corpus.json` as their steps succeed. Not atomic: a later failure can leave earlier writes in place. |
| `schemas DESTINATION` | Destination directory. | Creates the directory and rewrites the evaluator-owned JSON Schema files generated from Python models. Existing files at those generated paths are overwritten. It does not generate or replace the shared product contracts. |

For `initialize`, [`specifications.py`](../src/integration_evals/specifications.py)
defines the ten expected fixture families, each with positive and negative input
files. Use only the prepared, reviewed synthetic inputs in an isolated checkout;
do not substitute customer data or create arbitrary empty files to satisfy missing
paths. The command imports requirements before reading every fixture: missing
fixture bytes can therefore cause exit `1` after `planning/requirements.json` was
already replaced. Inspect and restore the disposable working copy after a failure.
This command is not GitHub discovery, acceptance synchronization or read-only
validation, and must not be run as routine onboarding against retained evidence.

The schema exporter currently covers 27 evaluator model types. The exporter source
is authoritative for that list; a matching schema file is not proof that an input
record, producer, or complete journey has been accepted.

Return to the [documentation index](INDEX.md) for component-specific prerequisites
and to the [README](../README.md) for the supported development and CI commands.
