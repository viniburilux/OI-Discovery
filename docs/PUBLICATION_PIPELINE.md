# Publication Pipeline

## Mandate

The private research corpus is a source of candidates for public distribution. It is not a publishing queue that should be mirrored automatically. The purpose of this pipeline is to extract the smallest shareable unit from mature work and publish it as evidence, infrastructure, demonstration or reusable knowledge.

> **Private = laboratory + memory. Public = evidence + infrastructure + demonstration + shareable knowledge.**

## Lifecycle

```text
candidate → triaged → sanitized → tested → publishable → published
                         ↘ blocked / rejected / private-only
```

Every transition is recorded with source files, evidence, license state, security result, reproducibility checks and the reason for the destination decision. A rejected or private-only item is still valuable: it prevents accidental disclosure and gives the next review a clear reason not to repeat the same work.

## Publication classes

| Class | Public artifact | Typical destination | Minimum requirement |
|---|---|---|---|
| Infrastructure | Code, schema, adapter, test, CLI | TraceFoundry GitHub | License, tests, no secrets, stable contract |
| Evidence | Metadata manifest, source-linked claim, negative result | TraceFoundry docs/examples | Public source, provenance, bounded language |
| Demonstration | Fixture, case study, walkthrough | TraceFoundry README/docs | Reproducible path and explicit limitations |
| Knowledge | Playbook, technical note, tutorial | TraceFoundry/docs or paper draft | Clear scope, references, reviewable claims |
| Dataset | Publicly redistributable data or derived artifact | Original repository, Zenodo or domain archive | Rights, documentation, checksums, schema and provenance |
| Paper | Manuscript, preprint or technical report | Private draft → appropriate public venue | Authorship, sources, methods and review readiness |
| Product surface | Landing page, demo, API contract | TraceFoundry or future hosted service | Honest capability statement and maintenance owner |

## Gate checklist

An item is `publishable` only when all applicable checks pass:

- **Provenance:** source repository, file path, commit or version and public source URI are recorded.
- **Rights:** the license permits the intended redistribution or the artifact stays as a link/reference rather than a copy.
- **Security:** no API keys, tokens, local paths, private names, memory entries or hidden configuration are included.
- **Scientific boundary:** raw NWB/HDF5/pickle, downloaded datasets and derived tables are not moved by default.
- **Reproducibility:** tests, validators or a bounded manual procedure exist.
- **Epistemic language:** observed facts, inferences, hypotheses, insufficiency and blocked states are not merged.
- **Reversibility:** the item can be removed or corrected in an isolated commit without damaging the private laboratory.

## What the pipeline may prepare autonomously

The pipeline may create a candidate report, copy only explicitly safe public metadata, generate a schema or template, write documentation, prepare a case-study skeleton, run offline checks and stage a commit. It may not publish private memory, raw scientific files, derived data, credentials, third-party code with incompatible license or an unreviewed manuscript under a claim of completion.

## Continuous loop

After a package is published, the next cycle returns to the private inventory and asks:

1. What else is mature enough to share?
2. Which published artifact now needs a correction or clearer boundary?
3. Which private item needs only one reversible step before publication?
4. Which item should remain private because its value depends on context, memory or strategy?

The loop is intentionally append-only and evidence-first. It increases the public surface without destroying the private advantage.

## Current wave

The first public wave consists of:

- TraceFoundry core and source adapters;
- Investigation State and Research Move contracts;
- Scientific Staging Playbook;
- Claim Audit Starter Kit;
- metadata-only V001 and cross-domain fixtures.

Candidate future waves include a curated negative-result case study from the private laboratory, safe adapter integration recipes and a manuscript scaffold. These remain `candidate` until rights, provenance and reproducibility checks are complete.
