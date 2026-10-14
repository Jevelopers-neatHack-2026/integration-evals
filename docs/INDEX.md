# Integration-evals documentation

This repository supplies evaluation tooling and retained evidence, not the
application services or authority it checks. Start with the [README](../README.md)
for the supported Python environment and actual CI commands, then use the
[CLI reference](cli-reference.md) for arguments, exit codes and file-writing
boundaries. A successful command or component test does not approve the product.

## Authority and system boundaries

| Guide | Purpose |
| --- | --- |
| [Ownership](architecture/OWNERSHIP.md) | Evaluator responsibilities, producer boundaries and current-state architecture references. |
| [Local acceptance view](architecture/ACCEPTANCE.md) | Relevant master identifiers and retained source pins; not a competing acceptance tracker. |
| [Master checklist](../planning/acceptance-checklist.md) | Canonical acceptance states and evidence rules; its [JSON tracker](../planning/acceptance-checklist.json) is the machine-readable counterpart. |
| [Owner decisions](../planning/decisions/) | Direction recorded separately from provisioning, provider authority and verified operations. |
| [Evidence index](../evidence/README.md) | Dated sponsor and submission records with their original qualifications. |

## Execution, integrity and retained results

| Guide | Use it for |
| --- | --- |
| [Execution protocol](execution-protocol.md) | App-owned assembly, pinned components, isolation, owner observations, contract conformance and benchmark requirements. |
| [Command reference](cli-reference.md) | All twelve implemented CLI commands, their options, output behavior and limits. |
| [Evidence audit](evidence-audit.md) | Standard-library integrity checks and the distinction between byte custody and acceptance. |
| [JUnit rendering](junit-reporting.md) | XML-compatible derivative reports without changing source evidence, outcomes or acceptance. |
| [Evidence indexing and local reviews](evidence-index.md) | Requirement joins, review derivatives, image qualifications and persistent blockers. |
| [Safe reruns](safe-reruns.md) | Rerun diagnostics, changed inputs and limits on release claims. |
| [Retained runner](safe-reruns-runner.md) | Preserved history and replay procedures without executing commands from archive metadata. |
| [Offline read containment](offline-read-containment.md) | Host read/isolation boundaries and the exact limits of offline evidence. |

## Pinned component and development checks

These guides have separate producer/runtime pins, fixtures, authority requirements
and limitations. A guide's existence or a successful isolated check does not mean
that all components were assembled or executed together.

| Guide | Component boundary |
| --- | --- |
| [Retrieval component](retrieval-component.md) | Controlled retrieval and its owner/runtime evidence. |
| [Print component](print-component.md) | Guarded synthetic print profile; production containment and ART-04 remain distinct. |
| [Finance component](finance-component-development.md) | Bounded Finance development-consumer execution. |
| [Captured Finance exports](finance-export-captured-consumer.md) | Captured export fixtures and their original provenance. |
| [Fulfillment component](fulfillment-component-development.md) | Bounded Fulfillment consumer checks, not supplier authority or ordering approval. |
| [App recovery component](app-recovery-component-development.md) | Pinned application recovery checks. |
| [Decision-failure component](decision-failure-component-development.md) | The specifically scoped decision/failure development lane. |
| [Canonical 0.10.1 development](canonical-v0101-development.md) | The named candidate lane, not a declaration of the latest accepted shared package. |

## Maintaining this index

Update a guide with its source, configuration, test and owner evidence. Keep
fixture copies, dated captures and checksum manifests intact. Link canonical
product schemas to their owner rather than copying them into evaluator authority.
Keep required-but-unexecuted tests and unavailable owner inputs visibly blocked.
Do not convert a guide update, CI result or this index into an acceptance-state
change. The [organization contribution guidance](https://github.com/Jevelopers-neatHack-2026/.github/blob/main/CONTRIBUTING.md)
applies alongside this repository's own instructions.
