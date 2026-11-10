# Implementation Plan: CLI Python Version Compatibility

**Branch**: `002-cli-python-compat` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-cli-python-compat/spec.md`

## Summary

The CLI module imports `enum.StrEnum`, which only exists on Python 3.11+, so `fhir_converter_cli` and `python -m fhir_converter` fail at import time on 3.8, 3.9 and 3.10 even though the package declares `python = "^3.8.1"`. CI did not catch it because no test imports `fhir_converter.__main__`.

Approach: change `RenderSourceFormat` from `StrEnum` to a `str`-mixin `Enum` with `__str__` returning the value, so argparse conversion, dict lookup, string equality, `str()` and f-string formatting all behave exactly as `StrEnum` does today. Add `tests/test_main.py` so the existing 3.8 to 3.12 CI matrix exercises the CLI. Record the FR-015 decision in the baseline spec.

## Technical Context

**Language/Version**: Python, declared `^3.8.1`; CI matrix 3.8, 3.9, 3.10, 3.11, 3.12; Makefile default 3.12

**Primary Dependencies**: stdlib `enum`, `argparse` only for this change. No new dependencies.

**Storage**: N/A (CLI writes output files to a caller-chosen folder)

**Testing**: pytest 7.4.4 (+ pytest-mock), mypy 1.8.0, flake8 7.0.0 via Poetry / Makefile targets

**Target Platform**: Any OS with a supported CPython (package classifiers list Linux and macOS; Windows used for local verification here)

**Project Type**: Library with a CLI entry point

**Performance Goals**: N/A (no runtime path change beyond enum construction)

**Constraints**: Zero behavior change on 3.11+ (spec FR-004, SC-003). No changes to arguments, help text, exit codes or output.

**Scale/Scope**: 1 production file (`fhir_converter/__main__.py`, about 10 lines), 1 new test file, 1 spec doc update.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unratified template, so there are no formal gates. Interim gates are taken from the conventions in `CLAUDE.md`:

| Gate | Pre-design | Post-design |
|------|------------|-------------|
| Public API stays fully type-annotated, mypy passes on `fhir_converter/` | PASS (enum keeps its annotations) | PASS |
| flake8 (max line 120) passes | PASS | PASS |
| Behavior change covered by tests | PASS (tests are part of scope) | PASS |
| No real patient data added; synthetic samples only | PASS (uses `tests/data/ccda/sample.ccda`) | PASS |
| No new dependencies | PASS | PASS |

Recommendation: ratify a constitution with `/speckit-constitution` before the next feature.

## Project Structure

### Documentation (this feature)

```text
specs/002-cli-python-compat/
├── spec.md
├── plan.md              # this file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── cli.md           # Phase 1: CLI contract that must not change
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
fhir_converter/
└── __main__.py          # MODIFY: RenderSourceFormat base class, import line

tests/
├── data/ccda/sample.ccda  # EXISTING synthetic fixture, read-only
└── test_main.py           # NEW: CLI tests

specs/001-baseline-fhir-converter/
├── spec.md                       # MODIFY: resolve FR-015
└── checklists/requirements.md    # MODIFY: tick the clarification item
```

**Structure Decision**: Existing single-package layout. Tests sit next to the existing `tests/test_*.py` modules and follow their style (pytest, `unittest.TestCase` allowed).

## Risks

- **Other 3.9+ syntax elsewhere in the package.** CI already runs the suite on 3.8 and passes, which suggests the library modules are fine, but `__main__` was never imported there. Mitigation: run the full suite locally on 3.8 and 3.12. If a different incompatibility appears, stop and report it rather than widening scope.
- **Pinned wheels on old runtimes locally** (for example `lxml 5.3.0` on 3.8 Windows). Mitigation: if a local install fails, rely on the CI matrix and say so in the PR.
- **`str()` of a `(str, Enum)` member differs from `StrEnum`** (`"RenderSourceFormat.CCDA"` vs `"CCDA"`). Mitigation: explicit `__str__` override, covered by a test.

## Complexity Tracking

No violations. Section intentionally empty.
