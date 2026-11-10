# Feature Specification: CLI Python Version Compatibility

**Feature Branch**: `002-cli-python-compat`

**Created**: 2026-11-06

**Status**: Draft

**Input**: User description: "Make the fhir_converter command-line tool work on every Python version the package declares support for (3.8 through 3.12). Today the CLI module imports a language feature that only exists in Python 3.11+, so on 3.8, 3.9 and 3.10 the CLI fails at import time before doing anything. Operators on those versions must be able to run conversions from the command line exactly as on 3.11+, with the same arguments, accepted source format values (STU3, CCDA), outputs and error behavior. Add automated tests covering the CLI's source format handling and a basic end-to-end CLI conversion. This resolves open item FR-015 in specs/001-baseline-fhir-converter in favor of keeping the declared 3.8+ support."

**Relates to**: [001-baseline-fhir-converter](../001-baseline-fhir-converter/spec.md), resolves FR-015 (keep declared 3.8+ support).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run the CLI on an older supported runtime (Priority: P1)

An operator whose environment is pinned to Python 3.8, 3.9 or 3.10 installs the package (which says it supports those versions) and runs the command-line converter. Today it crashes immediately with an import error. After this change it converts files exactly as it does on 3.11 and later.

**Why this priority**: The package promises support for these runtimes. Breaking that promise on the main non-programmer entry point is a defect that blocks real users.

**Independent Test**: On each supported runtime, start the CLI with `--help` and with a single-file conversion of a bundled sample. Confirm it starts, converts, and exits successfully.

**Acceptance Scenarios**:

1. **Given** the package installed on Python 3.8, 3.9 or 3.10, **When** the operator runs the CLI with `--help`, **Then** usage text is shown and the process exits successfully (no import error).
2. **Given** the package installed on any supported runtime (3.8 to 3.12), **When** the operator converts a sample C-CDA file with source format `CCDA` and template `CCD`, **Then** one `.json` output file is written and the run summary reports success.

---

### User Story 2 - Source format values behave the same everywhere (Priority: P1)

An operator passes the source format on the command line. The accepted values and the error for a bad value must be identical on every supported runtime, so scripts written on one runtime work on another.

**Why this priority**: The source format is the only CLI argument whose handling the fix touches. A silent behavior change would break existing scripts.

**Independent Test**: Run the CLI with each valid value and with an invalid one, and compare results to the current behavior on 3.11+.

**Acceptance Scenarios**:

1. **Given** `--source-format CCDA`, **When** the CLI runs, **Then** the C-CDA converter is selected.
2. **Given** `--source-format STU3`, **When** the CLI runs, **Then** the STU3 converter is selected.
3. **Given** an unsupported value (for example `HL7V2`), **When** the CLI runs, **Then** it exits with a usage error that names the invalid value, before any conversion starts and without creating the output folder.

---

### User Story 3 - Regressions are caught automatically (Priority: P2)

A maintainer needs confidence that this cannot silently break again. Automated tests exercise the CLI's source format handling and one complete CLI conversion, and the existing multi-version test run executes them on every supported runtime.

**Why this priority**: There are currently no CLI tests at all, which is how the defect shipped. It does not change user-visible behavior, so it ranks below the fix itself.

**Independent Test**: Run the test suite. The new CLI tests run and pass, and reverting the fix makes them fail on 3.8 to 3.10.

**Acceptance Scenarios**:

1. **Given** the test suite, **When** it runs on any supported runtime, **Then** the CLI tests for valid formats, an invalid format, and an end-to-end single-file conversion all pass.

### Edge Cases

- **Lowercase format value** (`ccda`): rejected today on 3.11+. It must stay rejected, so behavior is unchanged (no new case-insensitivity).
- **Missing `--source-format`**: still a usage error, since the argument stays required.
- **Help text**: the placeholder shown for the format argument in `--help` output stays the same.
- **Library users**: anyone importing the source format list from the CLI module still gets the same two named values, and each value still equals its text (`"CCDA"`, `"STU3"`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The command-line tool MUST start and run on every runtime version the package declares support for (3.8, 3.9, 3.10, 3.11, 3.12).
- **FR-002**: The CLI MUST accept exactly the source format values `CCDA` and `STU3` (case-sensitive), as today.
- **FR-003**: An unsupported source format value MUST produce a usage error naming the value and a non-zero exit, before any output is written.
- **FR-004**: Arguments, outputs, run summary and exit codes MUST be unchanged on 3.11 and later.
- **FR-005**: Each source format value MUST continue to compare equal to its text form (`"CCDA"`, `"STU3"`) for code that imports it.
- **FR-006**: Automated tests MUST cover: each valid source format choosing the right converter, rejection of an invalid value, and one end-to-end single-file CLI conversion producing an output file.
- **FR-007**: The baseline spec's open item FR-015 MUST be updated to record the decision: keep declared support for 3.8 and later.

### Key Entities

- **Source format**: the CLI's choice of input kind (`CCDA` or `STU3`). Determines which converter runs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The CLI starts successfully on 5 of 5 declared runtime versions (today: 2 of 5).
- **SC-002**: 100% of new CLI tests pass on every runtime in the existing multi-version test run.
- **SC-003**: 0 changes in CLI output, exit codes, or accepted values on 3.11 and later, verified by the same tests passing before and after the change there.
- **SC-004**: All existing tests still pass, with no change to their count of failures (zero).

## Assumptions

- "Declared support" means the runtime range in the package metadata (3.8.1 and later) and the versions already in the project's multi-version CI run. No new runtime is added or dropped.
- Accepted values stay case-sensitive, matching current behavior. Making them case-insensitive would be a separate feature.
- The end-to-end test uses existing synthetic sample data in the repository. No real patient data is added.
- The local machine may not have every runtime installed. Runtimes that cannot be tested locally are covered by the project's existing CI matrix once the change is pushed.
- Out of scope: other places that might also need newer runtimes outside the CLI (none were found in a scan of the package), README changes, and dependency upgrades.
