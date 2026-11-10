# Research: CLI Python Version Compatibility

## R1. How to replace `StrEnum` on 3.8+

- **Decision**: `class RenderSourceFormat(str, Enum)` with `def __str__(self) -> str: return str(self.value)`.
- **Rationale**: A `str` mixin makes members real strings, so `RenderSourceFormat("CCDA")` (argparse `type=`), dict hashing/lookup in `render_map`, and `== "CCDA"` all work on every version. The `__str__` override restores the one visible `StrEnum` difference: `str(member)` returns `"CCDA"` instead of `"RenderSourceFormat.CCDA"`. With that override, f-string/`format()` output is the value whether a given runtime formats mixin enums via the `str` value or via `__str__`; a test asserts this on every CI runtime rather than relying on version-specific behavior.
- **Alternatives considered**:
  - `sys.version_info` conditional import of `StrEnum`: two code paths, worse for mypy, no benefit.
  - `backports.strenum` / `StrEnum` package: adds a dependency for a 3-line class. Rejected (plan constraint: no new dependencies).
  - Plain `Enum` + `type=lambda s: RenderSourceFormat[s]`: changes the argparse error message (`invalid <lambda> value`). Rejected (FR-003, FR-004).
  - Raising the minimum Python to 3.11: rejected by the FR-015 decision (keep declared 3.8+ support).

## R2. Argparse error message must stay the same

- **Decision**: Keep `type=RenderSourceFormat`.
- **Rationale**: argparse builds the message from the type's `__name__`: `invalid RenderSourceFormat value: 'HL7V2'`, exit code 2. The class name does not change, so the message does not change.

## R3. Testing the CLI in-process

- **Decision**: Call `fhir_converter.__main__.main([...])` inside `pytest.raises(SystemExit)` and assert the exit code. Use pytest `tmp_path` for `--to-dir` and `tests/data/ccda/sample.ccda` as input.
- **Rationale**: `main()` always ends in `sys.exit` (0 success, 1 render failure). Argument errors raise `SystemExit(2)` from argparse, which bypasses `main()`'s `except Exception`. In-process tests are fast and give coverage numbers, unlike a subprocess.
- **Notes**: `--to-dir` must be a child of an existing folder (`mkdir` is called without `parents=True`). The CLI removes the output folder only if it created it and it is still empty (`rmdir`), so a successful run leaves the output file in place.
- **Alternatives considered**: subprocess invocation of `python -m fhir_converter`. More realistic, but slower and invisible to coverage; the import-time failure is already caught by importing the module in-process on each CI runtime.

## R4. Local multi-version verification

- **Decision**: Use `uv` (already installed) to create throwaway virtualenvs for Python 3.8 and 3.12 and run pytest, mypy and flake8 there. The 3.9 to 3.11 runtimes are covered by the existing CI matrix.
- **Rationale**: Poetry is not installed on this machine. CI uses Poetry, so this only affects local verification, not the project's tooling.
