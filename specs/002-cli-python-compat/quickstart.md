# Quickstart: validate CLI Python version compatibility

## Prerequisites

- `uv` on PATH (local check) or Poetry (project standard)
- Repository root as the working directory

## 1. Reproduce the defect (before the fix)

```bash
uv run --isolated --python 3.10 --with-editable . python -m fhir_converter --help
```

Expected before the fix: `ImportError: cannot import name 'StrEnum' from 'enum'`.
Expected after the fix: usage text and exit code 0.

## 2. Run the CLI tests on the oldest and newest runtimes

```bash
uv venv .venv-py38 --python 3.8
uv pip install --python .venv-py38 -e . pytest==7.4.4 pytest-mock==3.12.0
.venv-py38/Scripts/python -m pytest tests/test_main.py -q   # Windows path; use bin/ on Linux/macOS
```

Repeat with 3.12. Expected: all tests in `tests/test_main.py` pass on both.

## 3. Full suite and static checks (3.12)

```bash
python -m pytest -q
python -m mypy fhir_converter
python -m flake8 fhir_converter --count --select=E9,F63,F7,F82 --show-source --statistics
```

Expected: no failures, mypy `Success`, flake8 count `0`.

## 4. Manual end-to-end

```bash
python -m fhir_converter --from-file tests/data/ccda/sample.ccda --to-dir ./out --template-name CCD --source-format CCDA
```

Expected: `out/sample.json` exists and the summary says `RENDER SUCCESS`. Then try `--source-format ccda` and expect exit 2 with `invalid RenderSourceFormat value: 'ccda'`.

Contract details: [contracts/cli.md](contracts/cli.md). Invariants: [data-model.md](data-model.md).
