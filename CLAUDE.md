# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

`python-fhir-converter` is a Python port of Microsoft's C# [FHIR-Converter](https://github.com/microsoft/FHIR-Converter). It renders Liquid templates (via `python-liquid`) to transform source healthcare data into FHIR R4 JSON.

Supported conversions: **C-CDA -> FHIR R4** and **FHIR STU3 -> FHIR R4**. JSON->FHIR and HL7v2<->FHIR are not implemented.

## Layout

- `fhir_converter/renderers.py`: public rendering API. `BaseFhirRenderer` (abstract), `CcdaRenderer`, `Stu3FhirRenderer`, plus `make_environment`, `render_to_dir`, `render_files_to_dir`.
- `fhir_converter/__main__.py`: CLI (`fhir_converter_cli` / `python -m fhir_converter`).
- `fhir_converter/filters.py`: custom Liquid filters, including C# date format string support.
- `fhir_converter/tags.py`: custom Liquid tags.
- `fhir_converter/loaders.py`, `parsers.py`, `hl7.py`, `utils.py`, `exceptions.py`: template loading, XML/JSON parsing, HL7 helpers, utilities, errors.
- `fhir_converter/templates/ccda/` and `templates/stu3/`: bundled Liquid templates (subfolders `DataType`, `Entry`, `Extension`, `Reference`, `Resource`, `Section`, `Utils`, `ValueSet`).
- `tests/`: pytest suite; fixtures in `tests/data/`.
- `scripts/`: `examples.py` (usage examples), `benchmark.py`.
- `data/`: sample inputs.

## Commands

Uses Poetry. The Makefile targets Python 3.12.

```bash
make init            # poetry env use 3.12 + poetry install
make test            # poetry run pytest
make cov             # pytest with HTML coverage
make type-check      # mypy fhir_converter
make linting-check   # flake8 (max line length 120)
make build           # init + lint + type-check + cov
```

Run a single test: `poetry run pytest tests/test_filters.py::test_name`

## Conventions

- Code style is Black; flake8 max line length 120; mypy must pass on `fhir_converter/`.
- The package ships `py.typed`, so keep public APIs fully type-annotated.
- Liquid templates must use python-liquid syntax: commas between tag parameters, and explicit variable names when passing variables to snippets (see `templates/stu3/Resource.liquid`). Templates copied from the C# project usually need these fixes.
- When changing templates, add or update fixtures under `tests/data/` and the matching test.

## Gotchas

- `pyproject.toml` declares `python = "^3.8.1"` and CI tests 3.8 through 3.12. Do not use 3.9+ stdlib or syntax (for example `enum.StrEnum`, `str.removeprefix`, `list[str]` annotations, `match`). The CLI once broke on 3.8 to 3.10 this way; `tests/test_main.py` now guards it.
- `argparse` prints `options:` on 3.10+ and `optional arguments:` on older Pythons. That help-text difference is expected.
- Input data may contain PHI. Do not commit real patient data; use synthetic samples only.

## Spec-driven development

This repo uses [GitHub Spec Kit](https://github.com/github/spec-kit) v1.3.1 (Claude integration, PowerShell scripts).

- `.specify/memory/constitution.md`: project principles. All specs and plans must comply.
- `.specify/templates/`: spec, plan, tasks, checklist templates. `.specify/scripts/powershell/`: helper scripts.
- `.claude/skills/speckit-*`: the Spec Kit slash commands.
- `specs/NNN-short-name/`: one folder per feature (`spec.md`, `plan.md`, `tasks.md`, `checklists/`). Numbering is sequential.
- `specs/001-baseline-fhir-converter/`: baseline spec of current behavior. New feature specs should reference it instead of restating it.
- `.specify/feature.json`: local pointer to the active feature (gitignored).

Run these one at a time in Claude Code chat, reviewing each result before continuing:

1. `/speckit-constitution`: set project principles (once per project)
2. `/speckit-specify`: describe what to build and why
3. `/speckit-plan`: produce the technical plan
4. `/speckit-tasks`: break the plan into tasks
5. `/speckit-implement`: execute the tasks
6. `/speckit-converge`: repeat implement and converge until it reports `Converged`

Optional: `/speckit-clarify` (before plan), `/speckit-checklist` (after plan), `/speckit-analyze` (after tasks, before implement).
