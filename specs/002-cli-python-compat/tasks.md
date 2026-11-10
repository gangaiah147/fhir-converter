---

description: "Tasks for 002-cli-python-compat"
---

# Tasks: CLI Python Version Compatibility

**Input**: Design documents from `specs/002-cli-python-compat/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: Requested by the spec (FR-006, User Story 3). Tests are written first and must fail on Python 3.8 before the fix.

**Organization**: Grouped by user story. US1 and US2 share one production change (the enum), so US2 depends on the Foundational phase like US1 does.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3 from spec.md

---

## Phase 1: Setup

**Purpose**: Local environments to prove the defect and the fix on oldest and newest runtimes

**Executed note**: the 3.8 and 3.12 virtualenvs were created outside the repository (session scratchpad) instead of `.venv-py38/` and `.venv-py312/`, so T004 needed no `.gitignore` change.

- [x] T001 Create a feature branch `002-cli-python-compat` from `main` in the repository root
- [x] T002 [P] Create a Python 3.8 virtualenv at `.venv-py38` with `uv venv .venv-py38 --python 3.8` and install `-e .` plus `pytest==7.4.4 pytest-mock==3.12.0` (see `specs/002-cli-python-compat/quickstart.md` step 2)
- [x] T003 [P] Create a Python 3.12 virtualenv at `.venv-py312` the same way, adding `mypy==1.8.0 flake8==7.0.0 types-xmltodict==0.13.0.3 types-psutil==5.9.5.17 types-lxml==2024.8.7 lxml-stubs==0.5.1`
- [x] T004 Confirm both `.venv-py38/` and `.venv-py312/` are ignored by git (add `.venv-*/` to `.gitignore` if not), so they are never committed
- [x] T005 Reproduce the defect: run `python -m fhir_converter --help` in `.venv-py38` and record the `ImportError: cannot import name 'StrEnum'` output for the PR description

---

## Phase 2: Foundational (Tests First)

**Purpose**: Failing tests that pin the contract in `contracts/cli.md` and the invariants in `data-model.md`

**⚠️ CRITICAL**: Write and run these before touching `fhir_converter/__main__.py`

- [x] T006 Create `tests/test_main.py` with a `RenderSourceFormatTest` class asserting, verbatim from data-model.md: `RenderSourceFormat("CCDA") is RenderSourceFormat.CCDA`; `RenderSourceFormat("ccda")` raises `ValueError`; `RenderSourceFormat.CCDA == "CCDA"` and `isinstance(RenderSourceFormat.CCDA, str)`; `str(RenderSourceFormat.CCDA) == "CCDA"` and `f"{RenderSourceFormat.CCDA}" == "CCDA"`; `render_map` has exactly the keys `STU3` and `CCDA`
- [x] T007 Run `tests/test_main.py` in `.venv-py38` and confirm it fails at import (proves the tests catch the defect); run it in `.venv-py312` and confirm it passes (proves current behavior is pinned)

---

## Phase 3: User Story 1 - Run the CLI on an older supported runtime (Priority: P1) 🎯 MVP

**Goal**: CLI imports and converts on Python 3.8 to 3.10

**Independent Test**: `python -m fhir_converter --help` exits 0 on 3.8, and a single-file CCDA conversion writes `sample.json`

### Tests for User Story 1

- [x] T008 [US1] In `tests/test_main.py` add `test_help_exits_zero`: `main(["--help"])` inside `pytest.raises(SystemExit)` with exit code `0`
- [x] T009 [US1] In `tests/test_main.py` add `test_render_ccda_file`: `main(["--from-file", "tests/data/ccda/sample.ccda", "--to-dir", str(tmp_path / "out"), "--template-name", "CCD", "--source-format", "CCDA"])` raises `SystemExit` with code `0`, `tmp_path / "out" / "sample.json"` exists, and its JSON has `"resourceType": "Bundle"`

### Implementation for User Story 1

- [x] T010 [US1] In `fhir_converter/__main__.py` replace `from enum import StrEnum` with `from enum import Enum`, change `class RenderSourceFormat(StrEnum)` to `class RenderSourceFormat(str, Enum)`, and add `def __str__(self) -> str: return str(self.value)` with a one-line docstring noting it preserves StrEnum behavior on Python < 3.11
- [x] T011 [US1] Run `tests/test_main.py` in `.venv-py38` and `.venv-py312`; all tests from T006, T008, T009 pass on both

**Checkpoint**: MVP done. CLI works on 3.8 and behavior is pinned on 3.12.

---

## Phase 4: User Story 2 - Source format values behave the same everywhere (Priority: P1)

**Goal**: Valid values select the right renderer; invalid values fail the same way on every runtime

**Independent Test**: The tests below pass on 3.8 and 3.12

- [x] T012 [US2] In `tests/test_main.py` add a parametrized test that parses `--source-format CCDA` / `STU3` with `parse_args(get_argparser(), [...])` and asserts `render_map[args.source_format]` is `CcdaRenderer` / `Stu3FhirRenderer` respectively
- [x] T013 [US2] In `tests/test_main.py` add `test_invalid_source_format`: for `HL7V2` and `ccda`, `main([...])` raises `SystemExit` with code `2`, stderr (via `capsys`) contains `invalid RenderSourceFormat value: '<value>'`, and `tmp_path / "out"` does not exist
- [x] T014 [US2] In `tests/test_main.py` add `test_missing_source_format`: omitting `--source-format` raises `SystemExit` with code `2`
- [x] T015 [US2] Run `tests/test_main.py` in `.venv-py38` and `.venv-py312`; all pass

---

## Phase 5: User Story 3 - Regressions are caught automatically (Priority: P2)

**Goal**: Full suite and static checks green; CI matrix runs the new tests

**Independent Test**: Full suite passes on 3.8 and 3.12; mypy and flake8 clean on 3.12

- [x] T016 [US3] Run the full `tests/` suite in `.venv-py38` and `.venv-py312`; zero failures. If an unrelated 3.8 incompatibility appears, stop and report it instead of fixing it (out of scope per plan.md Risks)
- [x] T017 [P] [US3] Run `mypy fhir_converter` in `.venv-py312` (uses `mypy.ini`); result `Success`
- [x] T018 [P] [US3] Run both flake8 commands from `Makefile` target `linting-check` in `.venv-py312`; first command count `0`
- [x] T019 [US3] Confirm `.github/workflows/python-package.yml` already runs `pytest` on 3.8 to 3.12 (no workflow change needed); note this in the PR description

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T020 [P] In `specs/001-baseline-fhir-converter/spec.md` replace the FR-015 `[NEEDS CLARIFICATION ...]` text with the decision "keep declared support for 3.8 and later; see specs/002-cli-python-compat"
- [x] T021 [P] In `specs/001-baseline-fhir-converter/checklists/requirements.md` tick "No [NEEDS CLARIFICATION] markers remain" and update the FR-015 note
- [x] T022 [P] In `CLAUDE.md` update the "Gotchas" StrEnum bullet to say it is fixed and that the CLI must stay importable on 3.8
- [ ] T023 Walk every acceptance criterion on Jira [SCRUM-5](https://gangaiah147.atlassian.net/browse/SCRUM-5) and record pass/fail with evidence in the PR description
- [ ] T024 Commit on branch `002-cli-python-compat` (code, tests, spec docs; not the `.venv-*` folders) and open a PR against `main`, linking the Jira issue. Do not approve or merge.

---

## Dependencies & Execution Order

- Phase 1 (T001 to T005) → Phase 2 (T006, T007) → Phase 3 (US1) → Phase 4 (US2) and Phase 5 (US3) → Phase 6
- US2 and US3 both depend on T010 (the single production change). US2 test-writing tasks can be drafted in parallel with US1 but must be run after T010.
- T024 depends on everything else.

## Parallel Opportunities

- T002 and T003 (separate virtualenvs)
- T017 and T018 (independent static checks)
- T020, T021, T022 (separate docs)

## Implementation Strategy

1. MVP = Phases 1 to 3: the CLI works on 3.8 and core behavior is pinned.
2. Add US2 for full contract coverage of source format handling.
3. Add US3 checks, docs, then the PR.

Total: 24 tasks (Setup 5, Foundational 2, US1 4, US2 4, US3 4, Polish 5).
